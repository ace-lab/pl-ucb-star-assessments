"""Local backend: gdb over a websocket, plus /sync for the editor's egg.py
and /sync-challenge for the question's vuln.c.

Speaks the protocol pl-gdb-terminal.html expects:
  GET  /health                -> {"ok": true}
  POST /sync {"code": s}      -> writes /home/student/egg.py
  POST /sync-challenge {...}  -> writes + compiles /opt/challenge/vuln.c
  WS   /term                  -> raw text in/out of a pty running gdb

LOCAL DEVELOPMENT ONLY: all browsers share this one container, and students
run their own egg.py, which is arbitrary Python. Never expose it publicly.
"""
import fcntl
import json
import os
import pty
import select
import signal
import struct
import subprocess
import termios

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sock import Sock
from launcher import build_command

HOME = os.environ.get("GDB_HOME", "/home/student")
EGG_PATH = os.path.join(HOME, "egg.py")
UID = int(os.environ.get("GDB_UID", "1001"))
GID = int(os.environ.get("GDB_GID", "1001"))
ROWS, COLS = 20, 80  # matches the xterm.js size in pl-gdb-terminal.html

# Per-question vulnerable source, written and compiled by /sync-challenge.
CHALLENGE_SRC = "/opt/challenge/vuln.c"
CHALLENGE_BIN = "/opt/challenge/vuln"

app = Flask(__name__)
CORS(app)
sock = Sock(app)


def gdb_command() -> list[str]:
    return build_command(
        uid=UID,
        gid=GID,
        home=HOME,
        program_args=[CHALLENGE_BIN],
        script_dir=os.environ.get("GDB_SCRIPT_DIR", "/opt/gdb"),
        # egg.py is normally run as `run $(python3 egg.py)`, which needs a shell.
        run_uses_shell=os.environ.get("GDB_RUN_USES_SHELL", "1") == "1",
        running_as_root=os.getuid() == 0,
    )


def spawn_pty(command: list[str]) -> tuple[int, int]:
    """Start `command` on a new pty. Returns (pid, master_fd)."""
    pid, fd = pty.fork()
    if pid == 0:  # child: become gdb (no shell in between)
        try:
            os.execvp(command[0], command)
        finally:
            os._exit(127)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
    return pid, fd


@app.get("/health")
def health():
    return jsonify(ok=True)


@app.post("/sync")
def sync():
    code = (request.get_json(silent=True) or {}).get("code")
    if not isinstance(code, str) or len(code) > 100_000:
        return jsonify(ok=False, error="missing or oversized 'code'"), 400
    if not code.endswith("\n"):
        code += "\n"

    os.makedirs(HOME, exist_ok=True)
    with open(EGG_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    os.chmod(EGG_PATH, 0o755)
    if os.getuid() == 0:
        os.chown(EGG_PATH, UID, GID)  # the server is root; gdb runs as UID

    # NOTE: do not write anything to the terminal here. The old bash version
    # sent "\n" to redraw the prompt, but in gdb an empty line REPEATS THE
    # LAST COMMAND (e.g. `run` or `step`). The page shows its own message.
    return jsonify(ok=True, path=EGG_PATH, bytes=len(code.encode("utf-8")))


@app.post("/sync-challenge")
def sync_challenge():
    """Write and compile the question's vulnerable source (vuln.c).

    Runs once per page load, before the terminal connects. The binary this
    produces (CHALLENGE_BIN) is what gdb_command() points gdb --args at.
    """
    code = (request.get_json(silent=True) or {}).get("code")
    if not isinstance(code, str) or len(code) > 200_000:
        return jsonify(ok=False, error="missing or oversized 'code'"), 400

    os.makedirs(os.path.dirname(CHALLENGE_SRC), exist_ok=True)
    with open(CHALLENGE_SRC, "w", encoding="utf-8") as f:
        f.write(code)

    # -fno-stack-protector/-no-pie keep classic stack-smashing exploits
    # working by default; adjust per challenge if you need canaries/PIE on.
    result = subprocess.run(
        ["gcc", "-g", "-O0", "-fno-stack-protector", "-no-pie",
         "-o", CHALLENGE_BIN, CHALLENGE_SRC],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return jsonify(ok=False, error=result.stderr), 400

    os.chmod(CHALLENGE_BIN, 0o755)
    if os.getuid() == 0:
        os.chown(CHALLENGE_BIN, UID, GID)

    return jsonify(ok=True, path=CHALLENGE_BIN)


@sock.route("/term")
def term(ws):
    command = gdb_command()
    print("Starting:", command, flush=True)
    pid, fd = spawn_pty(command)
    try:
        while True:
            readable, _, _ = select.select([fd], [], [], 0.02)
            if readable:
                data = os.read(fd, 4096)
                if not data:
                    break  # gdb exited (e.g. the student typed `quit`)
                ws.send(data.decode("utf-8", "replace"))
            msg = ws.receive(timeout=0)
            if msg is not None:
                os.write(fd, msg.encode("utf-8"))
    except Exception:
        pass  # client disconnected or gdb exited
    finally:
        try:
            os.killpg(pid, signal.SIGKILL)  # gdb and anything it started
        except Exception:
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception:
                pass
        try:
            os.waitpid(pid, 0)
        except Exception:
            pass
        try:
            os.close(fd)
        except Exception:
            pass


if __name__ == "__main__":
    os.makedirs(HOME, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, threaded=True)
