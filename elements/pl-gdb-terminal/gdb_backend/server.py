"""Tiny local backend: a real bash shell (with gdb) over a websocket,
plus a /sync endpoint that writes the editor's egg.py into the container.

LOCAL DEVELOPMENT ONLY: it runs arbitrary commands. Never expose it publicly.
"""
import os
import pty
import select
import signal

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sock import Sock

WORKDIR = "/home/student"
EGG_PATH = os.path.join(WORKDIR, "egg.py")

app = Flask(__name__)
CORS(app)
sock = Sock(app)
sessions = set()


@app.get("/health")
def health():
    return jsonify(ok=True)


@app.post("/sync")
def sync():
    code = (request.get_json(silent=True) or {}).get("code")
    if not isinstance(code, str) or len(code) > 100_000:
        return jsonify(ok=False, error="missing or oversized 'code'"), 400

    with open(EGG_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    os.chmod(EGG_PATH, 0o755)

    # Tell any open terminals the file changed.
    for ws in list(sessions):
        try:
            ws.send("\r\n[sync] egg.py updated in container\r\n")
        except Exception:
            sessions.discard(ws)
    return jsonify(ok=True, path=EGG_PATH, bytes=len(code.encode("utf-8")))


@sock.route("/term")
def term(ws):
    pid, fd = pty.fork()
    if pid == 0:  # child: become the shell
        os.chdir(WORKDIR)
        os.environ["TERM"] = "xterm"
        os.execvp("bash", ["bash", "--login"])

    sessions.add(ws)
    try:
        while True:
            readable, _, _ = select.select([fd], [], [], 0.02)
            if readable:
                data = os.read(fd, 4096)
                if not data:
                    break
                ws.send(data.decode("utf-8", "replace"))
            msg = ws.receive(timeout=0)
            if msg is not None:
                os.write(fd, msg.encode("utf-8"))
    except Exception:
        pass  # client disconnected or shell exited
    finally:
        sessions.discard(ws)
        try:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
        except Exception:
            pass


if __name__ == "__main__":
    os.makedirs(WORKDIR, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, threaded=True)
