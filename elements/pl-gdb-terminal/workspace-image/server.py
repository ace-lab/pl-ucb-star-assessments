"""Workspace backend: gdb over a websocket for ONE student.

This runs inside a PrairieLearn workspace container. PrairieLearn starts one
container per student and question, and proxies it on the PrairieLearn origin
at /pl/workspace/<id>/container/ (the image is built with rewrite-url=true,
so this server simply sees / and no path prefix).

  GET  /health                -> {"ok": true}
  POST /sync {"code": s}      -> writes $HOME/egg.py
  POST /sync-challenge {...}  -> writes + compiles $HOME/.challenge/vuln.c
  WS   /term                  -> raw text in/out of a pty running gdb

There is no session or token logic on purpose: the container already belongs
to a single student, and PrairieLearn authenticates every request to it.
Do NOT publish this port yourself. Never put secrets (reference solutions,
flags) in the image or the home directory; the student can read all of it.
"""
import fcntl
import os
import pty
import select
import signal
import struct
import subprocess
import termios
import threading

from flask import Flask, jsonify, request
from flask_sock import Sock
from launcher import build_command

HOME = os.environ.get("GDB_HOME", "/home/student")
EGG_PATH = os.path.join(HOME, "egg.py")
UID = int(os.environ.get("GDB_UID", "1001"))
GID = int(os.environ.get("GDB_GID", "1001"))
ROWS, COLS = 20, 80  # matches the xterm.js size in pl-gdb-terminal.html

# Compiled at runtime from the question's vuln.c. It lives in the student's
# home (the only place a non-root user can write), in a hidden directory so
# it stays out of the way. List ".challenge/" under workspaceOptions.syncIgnore
# if you don't want PrairieLearn to back it up.
CHALLENGE_DIR = os.environ.get("GDB_CHALLENGE_DIR", os.path.join(HOME, ".challenge"))
CHALLENGE_SRC = os.path.join(CHALLENGE_DIR, "vuln.c")
CHALLENGE_BIN = os.path.join(CHALLENGE_DIR, "vuln")

# -fno-stack-protector/-no-pie keep classic stack-smashing exploits working
# by default; adjust per challenge if you need canaries/PIE on.
CFLAGS = ["-g", "-O0", "-fno-stack-protector", "-no-pie"]

IS_ROOT = os.getuid() == 0

app = Flask(__name__)
sock = Sock(app)
_compile_lock = threading.Lock()


class CompileError(Exception):
    pass


def _read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def compile_challenge(code: str) -> None:
    """Write and compile vuln.c; do nothing if this exact source is already built."""
    with _compile_lock:
        os.makedirs(CHALLENGE_DIR, exist_ok=True)
        if os.path.exists(CHALLENGE_BIN) and _read(CHALLENGE_SRC) == code:
            return
        try:
            os.remove(CHALLENGE_BIN)  # never leave a stale binary next to new source
        except FileNotFoundError:
            pass
        with open(CHALLENGE_SRC, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            # Absolute paths, so gdb's `list` finds vuln.c from the debug info.
            result = subprocess.run(
                ["gcc", *CFLAGS, "-o", CHALLENGE_BIN, CHALLENGE_SRC],
                capture_output=True, text=True, timeout=30,
            )
        except subprocess.TimeoutExpired:
            raise CompileError("compilation timed out")
        if result.returncode != 0:
            raise CompileError(result.stderr)
        os.chmod(CHALLENGE_BIN, 0o755)
        if IS_ROOT:  # only when run by hand as root; PrairieLearn runs us as 1001
            for p in (CHALLENGE_DIR, CHALLENGE_SRC, CHALLENGE_BIN):
                os.chown(p, UID, GID)


def gdb_command() -> list[str]:
    return build_command(
        uid=UID,
        gid=GID,
        home=HOME,
        program_args=[CHALLENGE_BIN],
        script_dir=os.environ.get("GDB_SCRIPT_DIR", "/opt/gdb"),
        # egg.py is normally run as `run $(python3 egg.py)`, which needs a shell.
        run_uses_shell=os.environ.get("GDB_RUN_USES_SHELL", "1") == "1",
        running_as_root=IS_ROOT,
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


@app.get("/")
def index():
    # PrairieLearn's workspace host checks that the container answers HTTP on its
    # port. Answer 200 at / like other workspace images do (the terminal itself
    # lives in the question page, not here).
    return "pl-gdb-terminal workspace backend is running\n"


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
    if IS_ROOT:
        os.chown(EGG_PATH, UID, GID)

    # NOTE: do not write anything to the terminal here. In gdb an empty line
    # REPEATS THE LAST COMMAND (e.g. `run` or `step`). The page shows its own message.
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
    try:
        compile_challenge(code)
    except CompileError as e:
        return jsonify(ok=False, error=str(e)), 400
    return jsonify(ok=True, path=CHALLENGE_BIN)


@sock.route("/term")
def term(ws):
    if not os.path.exists(CHALLENGE_BIN):
        ws.send("[challenge is not compiled yet; reload the page]\r\n")
        return
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), threaded=True)
