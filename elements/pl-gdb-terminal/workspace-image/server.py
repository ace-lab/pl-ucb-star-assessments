"""Workspace backend: gdb over a websocket for ONE student.

This runs inside a PrairieLearn workspace container. PrairieLearn starts one
container per student and question, and proxies it on the PrairieLearn origin
at /pl/workspace/<id>/container/ (the image is built with rewrite-url=true,
so this server simply sees / and no path prefix).

  GET  /health                -> {"ok": true}
  POST /sync {"code": s}      -> writes $HOME/egg.py
  POST /sync-challenge {code, aslr, canary, nx}
                              -> writes + compiles $HOME/.challenge/vuln.c with the
                                 requested protections; gdb is configured for ASLR
  WS   /term                  -> raw text in/out of a pty running gdb

There is no session or token logic on purpose: the container already belongs
to a single student, and PrairieLearn authenticates every request to it.
Do NOT publish this port yourself. Never put secrets (reference solutions,
flags) in the image or the home directory; the student can read all of it.
"""
import fcntl
import hashlib
import json
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

BUILD_INFO = os.path.join(CHALLENGE_DIR, "build.json")

# The three protections the instructor chooses per question (element attributes
# enable-aslr, enable-canary, enable-non-exec-pages). All default to off.
SETTING_NAMES = ("aslr", "canary", "nx")


def cflags(canary: bool, nx: bool) -> list[str]:
    """Compiler flags for the requested protections.

    canary: -fstack-protector-all puts a canary in every function; otherwise it is
            switched off explicitly (Ubuntu's gcc would enable one by default).
    nx:     -z noexecstack marks the stack non-executable; otherwise -z execstack
            makes it executable, which is what stack-shellcode exercises need.
    -no-pie keeps the program's own addresses fixed whatever ASLR does.
    ASLR is a runtime setting: see gdb_command().
    """
    return [
        "-g", "-O0", "-no-pie",
        "-fstack-protector-all" if canary else "-fno-stack-protector",
        "-Wl,-z,noexecstack" if nx else "-Wl,-z,execstack",
    ]


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


def _read_build_info() -> dict:
    try:
        with open(BUILD_INFO, "r", encoding="utf-8") as f:
            info = json.load(f)
        return info if isinstance(info, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_build_info(info: dict) -> None:
    tmp = BUILD_INFO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(info, f)
    os.replace(tmp, BUILD_INFO)
    if IS_ROOT:  # only when run by hand as root; PrairieLearn runs us as 1001
        os.chown(BUILD_INFO, UID, GID)


def _fingerprint(code: str, canary: bool, nx: bool) -> str:
    # ASLR is not part of the build, so changing only it never forces a recompile.
    payload = json.dumps({"code": code, "flags": cflags(canary, nx)}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compile_challenge(code: str, settings: dict) -> None:
    """Write and compile vuln.c with the requested protections.

    Does nothing if this exact source and flags are already built. Always records
    the settings (including aslr) so the next terminal connection uses them.
    """
    canary, nx = settings["canary"], settings["nx"]
    with _compile_lock:
        os.makedirs(CHALLENGE_DIR, exist_ok=True)
        fingerprint = _fingerprint(code, canary, nx)
        info = {"fingerprint": fingerprint, **{k: settings[k] for k in SETTING_NAMES}}

        if os.path.exists(CHALLENGE_BIN) and _read_build_info().get("fingerprint") == fingerprint:
            _write_build_info(info)  # only aslr may have changed
            return

        for stale in (CHALLENGE_BIN, BUILD_INFO):  # never keep a binary that doesn't match
            try:
                os.remove(stale)
            except FileNotFoundError:
                pass
        with open(CHALLENGE_SRC, "w", encoding="utf-8") as f:
            f.write(code)
        try:
            # Absolute paths, so gdb's `list` finds vuln.c from the debug info.
            result = subprocess.run(
                ["gcc", *cflags(canary, nx), "-o", CHALLENGE_BIN, CHALLENGE_SRC],
                capture_output=True, text=True, timeout=30,
            )
        except subprocess.TimeoutExpired:
            raise CompileError("compilation timed out")
        if result.returncode != 0:
            raise CompileError(result.stderr)
        os.chmod(CHALLENGE_BIN, 0o755)
        _write_build_info(info)
        if IS_ROOT:
            for p in (CHALLENGE_DIR, CHALLENGE_SRC, CHALLENGE_BIN):
                os.chown(p, UID, GID)


def gdb_command() -> list[str]:
    # ASLR is applied here, not at compile time. gdb turns it off by default, so
    # both cases are set explicitly.
    aslr = bool(_read_build_info().get("aslr", False))
    return build_command(
        uid=UID,
        gid=GID,
        home=HOME,
        program_args=[CHALLENGE_BIN],
        script_dir=os.environ.get("GDB_SCRIPT_DIR", "/opt/gdb"),
        # egg.py is normally run as `run $(python3 egg.py)`, which needs a shell.
        run_uses_shell=os.environ.get("GDB_RUN_USES_SHELL", "1") == "1",
        running_as_root=IS_ROOT,
        extra_gdb_commands=[f"set disable-randomization {'off' if aslr else 'on'}"],
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
    payload = request.get_json(silent=True) or {}
    code = payload.get("code")
    if not isinstance(code, str) or len(code) > 200_000:
        return jsonify(ok=False, error="missing or oversized 'code'"), 400
    settings = {}
    for name in SETTING_NAMES:
        value = payload.get(name, False)
        if not isinstance(value, bool):
            return jsonify(ok=False, error=f"'{name}' must be true or false"), 400
        settings[name] = value
    try:
        compile_challenge(code, settings)
    except CompileError as e:
        return jsonify(ok=False, error=str(e)), 400
    return jsonify(ok=True, path=CHALLENGE_BIN, **settings)


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
