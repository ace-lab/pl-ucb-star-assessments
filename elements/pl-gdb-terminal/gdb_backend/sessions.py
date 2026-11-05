"""Per-student sessions for the gdb backend.

No third-party imports, so it can be unit-tested without Flask.

A session is one student's private environment:
  * a token (random, unguessable) that the browser presents on every call
  * a slot: a private home directory <root>/s<N> (mode 700)
  * a dedicated unix uid/gid (uid_base + N) that gdb and the student's egg.py
    run as

Slots are recycled, so the number of uids is bounded by max_sessions. The uid
is what stops one student's code from reading, modifying or signalling another
student's files and processes. Directory permissions alone would not: egg.py is
arbitrary Python, and without separate uids it runs as the same user for
everyone.
"""
from __future__ import annotations

import os
import secrets
import shutil
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass


class CapacityError(Exception):
    """Every slot is held by a recently active session."""


@dataclass
class Session:
    token: str
    slot: int
    uid: int
    gid: int
    home: str
    last_seen: float
    binary: str | None = None    # compiled challenge for this session
    term_pid: int | None = None  # live gdb process, if a terminal is attached


def write_file(home, name, data, *, mode=0o644, uid=None, gid=None):
    """Write home/name, safely, even though the student owns `home`.

    The server runs as root; the student can replace anything inside their own
    directory with a symlink or hardlink. Opening the final path directly
    would let them aim a root-owned write at any file on the system. Instead:
    create a fresh temp file (O_EXCL | O_NOFOLLOW, so it can never be a link),
    fill it, then rename it over the target. rename replaces a symlink itself
    rather than following it.
    """
    final = os.path.join(home, name)
    tmp = os.path.join(home, f".{name}.{secrets.token_hex(8)}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fchmod(f.fileno(), mode)
            if uid is not None:
                os.fchown(f.fileno(), uid, gid)
        os.replace(tmp, final)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _kill_group(pid: int | None) -> None:
    if not pid:
        return
    try:
        os.killpg(pid, signal.SIGKILL)  # pty.fork makes the child a group leader
    except OSError:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass


class SessionManager:
    def __init__(
        self,
        *,
        root: str,
        uid_base: int,
        max_sessions: int,
        privileged: bool,
        idle_ttl: float = 1800.0,
        min_evict_idle: float = 120.0,
    ):
        self.root = root
        self.uid_base = uid_base
        self.max_sessions = max_sessions
        self.privileged = privileged  # True when running as root (chown/uid drop)
        self.idle_ttl = idle_ttl
        self.min_evict_idle = min_evict_idle
        self._lock = threading.Lock()
        self._by_token: dict[str, Session] = {}
        self._by_slot: dict[int, Session] = {}
        os.makedirs(root, exist_ok=True)
        os.chmod(root, 0o711)  # students can enter their own s<N>, not list others

    # ---- lookup -----------------------------------------------------------

    def get(self, token) -> Session | None:
        """Return the live session for `token` (and mark it active), or None."""
        if not isinstance(token, str):
            return None
        with self._lock:
            s = self._by_token.get(token)
            if s is not None:
                s.last_seen = time.time()
            return s

    def count(self) -> int:
        with self._lock:
            return len(self._by_token)

    # ---- lifecycle --------------------------------------------------------

    def create(self) -> Session:
        with self._lock:
            slot = next((i for i in range(self.max_sessions) if i not in self._by_slot), None)
            if slot is None:
                victim = self._lru_idle_locked()
                if victim is None:
                    raise CapacityError()
                slot = victim.slot
                self._destroy_locked(victim)
            uid = self.uid_base + slot
            s = Session(
                token=secrets.token_urlsafe(32),
                slot=slot,
                uid=uid,
                gid=uid,
                home=os.path.join(self.root, f"s{slot}"),
                last_seen=time.time(),
            )
            shutil.rmtree(s.home, ignore_errors=True)
            os.makedirs(s.home, mode=0o700)
            os.chmod(s.home, 0o700)
            if self.privileged:
                os.chown(s.home, s.uid, s.gid)
            self._by_token[s.token] = s
            self._by_slot[slot] = s
            return s

    def release(self, session: Session) -> None:
        with self._lock:
            if self._by_token.get(session.token) is session:
                self._destroy_locked(session)

    def reap_idle(self) -> int:
        """Destroy sessions with no terminal attached that have been idle too long."""
        now = time.time()
        n = 0
        with self._lock:
            for s in list(self._by_token.values()):
                if s.term_pid is None and now - s.last_seen > self.idle_ttl:
                    self._destroy_locked(s)
                    n += 1
        return n

    # ---- terminal bookkeeping --------------------------------------------

    def set_terminal(self, s: Session, pid: int) -> None:
        """Register the live gdb. A second terminal for the same session replaces the first."""
        with self._lock:
            old, s.term_pid = s.term_pid, pid
        _kill_group(old)

    def clear_terminal(self, s: Session, pid: int) -> None:
        with self._lock:
            if s.term_pid == pid:  # a replaced terminal must not clear its successor
                s.term_pid = None
                s.last_seen = time.time()

    # ---- internals (caller holds the lock) --------------------------------

    def _lru_idle_locked(self) -> Session | None:
        now = time.time()
        idle = [
            s for s in self._by_token.values()
            if s.term_pid is None and now - s.last_seen >= self.min_evict_idle
        ]
        return min(idle, key=lambda s: s.last_seen, default=None)

    def _destroy_locked(self, s: Session) -> None:
        self._by_token.pop(s.token, None)
        self._by_slot.pop(s.slot, None)
        _kill_group(s.term_pid)
        s.term_pid = None
        self._kill_uid(s)
        # Only after every process is dead, so nothing can race the delete.
        shutil.rmtree(s.home, ignore_errors=True)

    def _kill_uid(self, s: Session) -> None:
        """Kill everything the student left running (background jobs, forks)."""
        if not self.privileged:
            return
        try:
            # kill(-1, SIGKILL) signals every process the caller may signal.
            # As the session's own uid, that is exactly that student's processes.
            subprocess.run(
                [sys.executable, "-c", "import os, signal; os.kill(-1, signal.SIGKILL)"],
                user=s.uid, group=s.gid, extra_groups=[],
                timeout=5, capture_output=True,
            )
        except Exception:
            pass
