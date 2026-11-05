"""Backend: one private gdb environment per student session.

Protocol (see pl-gdb-terminal.html):
  GET  /health                       -> {"ok": true}
  POST /session {"token"?: s}        -> {"ok": true, "token": s}   resume or create
  POST /sync            (+ token)    -> writes egg.py into THIS session's home
  POST /sync-challenge  (+ token)    -> compiles vuln.c (cached by content hash)
  WS   /term                         -> first message {"token": s}, then raw
                                        text in/out of a pty running gdb

The token travels in the X-Session-Token header for HTTP calls and in the first
websocket message for /term (never in a URL, so it stays out of access logs).

Isolation per session: its own directory (mode 700), its own unix uid, its own
process limits. Still one container, so for graded use also bound the whole
container (see start_backend.sh) and read the notes in README.md.
"""
import fcntl
import hashlib
import json
import os
import pty
import select
import shutil
import struct
import subprocess
import tempfile
import termios
import threading
import time

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sock import Sock
from launcher import build_command
from sessions import CapacityError, SessionManager, write_file

PRIVILEGED = os.getuid() == 0
SESSION_ROOT = os.environ.get("GDB_SESSION_ROOT", "/sessions")
UID_BASE = int(os.environ.get("GDB_UID_BASE", "20000"))
MAX_SESSIONS = int(os.environ.get("GDB_MAX_SESSIONS", "64"))
IDLE_TTL = float(os.environ.get("GDB_IDLE_TTL", "1800"))
COMPILE_UID = int(os.environ.get("GDB_COMPILE_UID", str(UID_BASE - 1)))
CACHE_ROOT = os.environ.get("GDB_CHALLENGE_CACHE", "/opt/challenge-cache")
LIMITS = {"nproc": 128, "nofile": 256, "fsize": 50 * 1024 * 1024, "core": 0}
ROWS, COLS = 20, 80  # matches the xterm.js size in pl-gdb-terminal.html

# -fno-stack-protector/-no-pie keep classic stack-smashing exploits working by
# default; adjust per challenge if you need canaries/PIE on.
CFLAGS = ["-g", "-O0", "-fno-stack-protector", "-no-pie"]

app = Flask(__name__)
CORS(app)
sock = Sock(app)
sessions = SessionManager(
    root=SESSION_ROOT,
    uid_base=UID_BASE,
    max_sessions=MAX_SESSIONS,
    privileged=PRIVILEGED,
    idle_ttl=IDLE_TTL,
)


# ---- helpers ---------------------------------------------------------------

def session_or_401():
    """Return (session, None) or (None, error_response)."""
    s = sessions.get(request.headers.get("X-Session-Token", ""))
    if s is None:
        return None, (jsonify(ok=False, error="unknown or expired session"), 401)
    return s, None


_compile_locks: dict[str, threading.Lock] = {}
_compile_locks_guard = threading.Lock()


def _lock_for(key: str) -> threading.Lock:
    with _compile_locks_guard:
        return _compile_locks.setdefault(key, threading.Lock())


class CompileError(Exception):
    pass


def compile_challenge(source: str) -> str:
    """Compile `source` once per distinct content and return the binary's path.

    Every student on the same question sends the same vuln.c, so the result is
    cached under CACHE_ROOT/<hash>/ and shared. The cache is root-owned and
    read-only to students, which also removes the old race where two page loads
    overwrote one global /opt/challenge/vuln.
    """
    digest = hashlib.sha256(("\0".join(CFLAGS) + "\0\0" + source).encode()).hexdigest()[:32]
    final = os.path.join(CACHE_ROOT, digest)
    binary = os.path.join(final, "vuln")
    if os.path.exists(binary):
        return binary

    with _lock_for(digest):
        if os.path.exists(binary):  # another request finished while we waited
            return binary
        os.makedirs(CACHE_ROOT, exist_ok=True)
        os.chmod(CACHE_ROOT, 0o755)
        tmp = tempfile.mkdtemp(prefix=".build-", dir=CACHE_ROOT)
        try:
            os.chmod(tmp, 0o755)
            with open(os.path.join(tmp, "vuln.c"), "w", encoding="utf-8") as f:
                f.write(source)
            os.chmod(os.path.join(tmp, "vuln.c"), 0o644)

            # The source is whatever the browser sent, so compile it as an
            # unprivileged user with a time limit.
            extra = {}
            if PRIVILEGED:
                os.chown(tmp, COMPILE_UID, COMPILE_UID)
                extra = dict(user=COMPILE_UID, group=COMPILE_UID, extra_groups=[])
            try:
                result = subprocess.run(
                    # -fdebug-prefix-map: debug info should point at the final
                    # location, so gdb's `list` finds vuln.c after the rename.
                    ["gcc", *CFLAGS, f"-fdebug-prefix-map={tmp}={final}",
                     "-o", "vuln", "vuln.c"],
                    cwd=tmp, capture_output=True, text=True, timeout=30, **extra,
                )
            except subprocess.TimeoutExpired:
                raise CompileError("compilation timed out")
            if result.returncode != 0:
                raise CompileError(result.stderr.replace(tmp + "/", ""))

            # Hand everything back to root before publishing it.
            for path, mode in ((tmp, 0o755), (os.path.join(tmp, "vuln"), 0o755),
                               (os.path.join(tmp, "vuln.c"), 0o644)):
                os.chmod(path, mode)
                if PRIVILEGED:
                    os.chown(path, 0, 0)
            try:
                os.rename(tmp, final)  # atomic; readers never see a half-built dir
            except OSError:
                if not os.path.exists(binary):
                    raise
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return binary


def gdb_command(s) -> list[str]:
    return build_command(
        uid=s.uid,
        gid=s.gid,
        home=s.home,
        program_args=[s.binary],
        script_dir=os.environ.get("GDB_SCRIPT_DIR", "/opt/gdb"),
        # egg.py is normally run as `run $(python3 egg.py)`, which needs a shell.
        run_uses_shell=os.environ.get("GDB_RUN_USES_SHELL", "1") == "1",
        running_as_root=PRIVILEGED,
        limits=LIMITS,
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


# ---- routes ----------------------------------------------------------------

@app.get("/health")
def health():
    return jsonify(ok=True, sessions=sessions.count(), capacity=MAX_SESSIONS)


@app.post("/session")
def open_session():
    """Resume the caller's session if its token is still valid, else create one."""
    token = (request.get_json(silent=True) or {}).get("token")
    s = sessions.get(token)
    if s is None:
        try:
            s = sessions.create()
        except CapacityError:
            return jsonify(ok=False, error="all terminals are in use; try again shortly"), 503
    return jsonify(ok=True, token=s.token)


@app.post("/sync")
def sync():
    s, err = session_or_401()
    if err:
        return err
    code = (request.get_json(silent=True) or {}).get("code")
    if not isinstance(code, str) or len(code) > 100_000:
        return jsonify(ok=False, error="missing or oversized 'code'"), 400
    if not code.endswith("\n"):
        code += "\n"
    data = code.encode("utf-8")

    try:
        write_file(s.home, "egg.py", data, mode=0o755,
                   uid=s.uid if PRIVILEGED else None, gid=s.gid if PRIVILEGED else None)
    except OSError as e:
        return jsonify(ok=False, error=f"could not write egg.py: {e.strerror}"), 500

    # NOTE: do not write anything to the terminal here. In gdb an empty line
    # REPEATS THE LAST COMMAND (e.g. `run` or `step`). The page shows its own message.
    return jsonify(ok=True, bytes=len(data))


@app.post("/sync-challenge")
def sync_challenge():
    """Compile the question's vulnerable source (shared, cached) for this session."""
    s, err = session_or_401()
    if err:
        return err
    code = (request.get_json(silent=True) or {}).get("code")
    if not isinstance(code, str) or len(code) > 200_000:
        return jsonify(ok=False, error="missing or oversized 'code'"), 400
    try:
        s.binary = compile_challenge(code)
    except CompileError as e:
        return jsonify(ok=False, error=str(e)), 400
    return jsonify(ok=True)


@sock.route("/term")
def term(ws):
    # First message authenticates: {"token": "..."}
    try:
        first = json.loads(ws.receive(timeout=5) or "{}")
    except (ValueError, TypeError):
        first = {}
    s = sessions.get(first.get("token") if isinstance(first, dict) else None)
    if s is None:
        ws.send("[invalid or expired session; reload the page]\r\n")
        return
    if not s.binary or not os.path.exists(s.binary):
        ws.send("[challenge is not compiled yet; reload the page]\r\n")
        return

    command = gdb_command(s)
    pid, fd = spawn_pty(command)
    sessions.set_terminal(s, pid)  # a second tab for this session replaces the first
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
        pass  # client disconnected, gdb exited, or this terminal was replaced
    finally:
        try:
            os.killpg(pid, 9)  # gdb and anything it started
        except Exception:
            try:
                os.kill(pid, 9)
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
        sessions.clear_terminal(s, pid)


def _reaper():
    while True:
        time.sleep(60)
        try:
            sessions.reap_idle()
        except Exception as e:  # never let the reaper die
            print("reaper error:", e, flush=True)


if __name__ == "__main__":
    if not PRIVILEGED:
        print("WARNING: not running as root. Sessions get separate directories but "
              "share one unix uid, so a student's egg.py can read or kill other "
              "students' files and processes. Run as root (local) or grant "
              "CAP_SETUID/CAP_SETGID/CAP_CHOWN/CAP_KILL for real isolation.", flush=True)
    threading.Thread(target=_reaper, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, threaded=True)
