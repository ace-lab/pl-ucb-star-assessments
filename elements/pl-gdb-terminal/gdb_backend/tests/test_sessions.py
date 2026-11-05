"""Run from gdb_backend/:  python3 -m unittest discover -s tests -v

The root-only tests are skipped when not run as root (e.g. on a laptop); run
them inside the container to check the real uid isolation:
  docker run --rm --entrypoint /opt/venv/bin/python ucb-star-gdb:latest \
      -m unittest discover -s /app/tests -v
"""
import os
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from launcher import build_command
from sessions import CapacityError, SessionManager, write_file

IS_ROOT = os.getuid() == 0


def read(path):
    with open(path) as f:
        return f.read()


def make(tmp, **kw):
    kw.setdefault("uid_base", 30000)
    kw.setdefault("max_sessions", 3)
    kw.setdefault("privileged", False)
    return SessionManager(root=os.path.join(tmp, "sessions"), **kw)


class SessionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_each_session_gets_own_token_dir_and_uid(self):
        m = make(self.tmp)
        a, b = m.create(), m.create()
        self.assertNotEqual(a.token, b.token)
        self.assertNotEqual(a.home, b.home)
        self.assertNotEqual(a.uid, b.uid)
        self.assertEqual(os.stat(a.home).st_mode & 0o777, 0o700)

    def test_unknown_token_is_rejected(self):
        m = make(self.tmp)
        m.create()
        self.assertIsNone(m.get("nope"))
        self.assertIsNone(m.get(None))
        self.assertIsNone(m.get(12345))

    def test_files_are_not_shared_between_sessions(self):
        m = make(self.tmp)
        a, b = m.create(), m.create()
        write_file(a.home, "egg.py", b"print('A')\n", mode=0o755)
        write_file(b.home, "egg.py", b"print('B')\n", mode=0o755)
        self.assertEqual(read(os.path.join(a.home, "egg.py")), "print('A')\n")
        self.assertEqual(read(os.path.join(b.home, "egg.py")), "print('B')\n")

    def test_capacity_and_eviction_of_idle_sessions(self):
        m = make(self.tmp, max_sessions=2, min_evict_idle=100)
        a, b = m.create(), m.create()
        with self.assertRaises(CapacityError):  # both recently active
            m.create()
        a.last_seen -= 500  # a goes idle
        c = m.create()
        self.assertEqual(c.slot, a.slot)  # slot recycled...
        self.assertIsNone(m.get(a.token))  # ...and the old token is dead
        self.assertIsNotNone(m.get(b.token))

    def test_session_with_live_terminal_is_never_evicted_or_reaped(self):
        m = make(self.tmp, max_sessions=1, min_evict_idle=0, idle_ttl=0)
        a = m.create()
        a.term_pid = 0x7FFFFFF0  # pretend a terminal is attached
        a.last_seen -= 10_000
        self.assertEqual(m.reap_idle(), 0)
        with self.assertRaises(CapacityError):
            m.create()

    def test_reap_idle_wipes_the_directory(self):
        m = make(self.tmp, idle_ttl=10)
        a = m.create()
        write_file(a.home, "egg.py", b"x\n")
        a.last_seen -= 60
        self.assertEqual(m.reap_idle(), 1)
        self.assertFalse(os.path.exists(a.home))
        self.assertIsNone(m.get(a.token))

    def test_recycled_slot_starts_empty(self):
        m = make(self.tmp, max_sessions=1, min_evict_idle=0)
        a = m.create()
        write_file(a.home, "secret.txt", b"previous student\n")
        b = m.create()  # evicts a (idle >= 0)
        self.assertEqual(os.listdir(b.home), [])

    def test_symlinked_egg_py_cannot_redirect_the_write(self):
        m = make(self.tmp)
        a = m.create()
        victim = os.path.join(self.tmp, "victim.txt")
        with open(victim, "w") as f:
            f.write("untouched\n")
        os.symlink(victim, os.path.join(a.home, "egg.py"))  # what a hostile student does
        write_file(a.home, "egg.py", b"print('hi')\n", mode=0o755)
        self.assertEqual(read(victim), "untouched\n")
        self.assertFalse(os.path.islink(os.path.join(a.home, "egg.py")))
        self.assertEqual(read(os.path.join(a.home, "egg.py")), "print('hi')\n")

    def test_dangling_symlink_at_temp_name_is_not_followed(self):
        # Even a pre-planted link where a temp file might go must not be followed.
        m = make(self.tmp)
        a = m.create()
        victim = os.path.join(self.tmp, "victim2.txt")
        os.symlink(victim, os.path.join(a.home, ".egg.py.deadbeef.tmp"))
        write_file(a.home, "egg.py", b"ok\n")
        self.assertFalse(os.path.exists(victim))


@unittest.skipUnless(IS_ROOT, "needs root to switch uids")
class RootIsolationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.chmod(self._tmp.name, 0o755)  # let session uids traverse to their own dirs
        self.m = make(self._tmp.name, privileged=True, uid_base=41000)

    def tearDown(self):
        for s in list(self.m._by_token.values()):
            self.m.release(s)
        self._tmp.cleanup()

    def _as(self, s, code):
        return subprocess.run(
            [sys.executable, "-c", code],
            user=s.uid, group=s.gid, extra_groups=[], capture_output=True, text=True,
        )

    def test_student_cannot_read_another_students_files(self):
        a, b = self.m.create(), self.m.create()
        write_file(b.home, "egg.py", b"B-secret\n", uid=b.uid, gid=b.gid)
        r = self._as(a, f"print(open({os.path.join(b.home, 'egg.py')!r}).read())")
        ok = self._as(b, f"print(open({os.path.join(b.home, 'egg.py')!r}).read())")
        self.assertIn("B-secret", ok.stdout)  # owner can read: the path is reachable
        self.assertNotEqual(r.returncode, 0)  # ...so a's failure is purely permissions
        self.assertIn("Permission denied", r.stderr)

    def test_student_cannot_signal_another_students_processes(self):
        a, b = self.m.create(), self.m.create()
        victim = subprocess.Popen(["sleep", "60"], user=b.uid, group=b.gid, extra_groups=[])
        try:
            r = self._as(a, f"import os, signal; os.kill({victim.pid}, signal.SIGKILL)")
            self.assertNotEqual(r.returncode, 0)
            self.assertIsNone(victim.poll())
        finally:
            victim.kill()
            victim.wait()

    def test_release_kills_leftover_processes_of_that_uid_only(self):
        a, b = self.m.create(), self.m.create()
        pa = subprocess.Popen(["sleep", "60"], user=a.uid, group=a.gid, extra_groups=[])
        pb = subprocess.Popen(["sleep", "60"], user=b.uid, group=b.gid, extra_groups=[])
        try:
            self.m.release(a)
            time.sleep(0.2)
            self.assertIsNotNone(pa.poll())  # a's stray process is gone
            self.assertIsNone(pb.poll())  # b's is not
        finally:
            pb.kill()
            pb.wait()
            if pa.poll() is None:
                pa.kill()
            pa.wait()

    def test_launcher_chain_runs_as_session_uid_with_limits(self):
        s = self.m.create()
        cmd = build_command(
            uid=s.uid, gid=s.gid, home=s.home, program_args=[],
            script_dir="/nonexistent", run_uses_shell=True, running_as_root=True,
            limits={"nproc": 64, "nofile": 128},
        )
        # Swap gdb for a probe: keep the whole wrapper prefix, run `sh` instead.
        prefix = cmd[: cmd.index("/usr/bin/gdb")]
        out = subprocess.run(
            prefix + ["/bin/sh", "-c", "id -u; cat /proc/self/limits; echo HOME=$HOME TMPDIR=$TMPDIR"],
            capture_output=True, text=True,
        ).stdout
        self.assertEqual(out.splitlines()[0], str(s.uid))
        procs = next(l for l in out.splitlines() if l.startswith("Max processes")).split()
        files = next(l for l in out.splitlines() if l.startswith("Max open files")).split()
        self.assertEqual(procs[2:4], ["64", "64"])    # soft, hard
        self.assertEqual(files[3:5], ["128", "128"])
        self.assertIn(f"HOME={s.home} TMPDIR={s.home}", out)


class LauncherTests(unittest.TestCase):
    def test_limits_wrap_the_command_and_are_optional(self):
        base = dict(uid=1, gid=1, home="/h", program_args=["/b"], script_dir="/nonexistent",
                    run_uses_shell=True, running_as_root=True)
        plain = build_command(**base)
        limited = build_command(**base, limits={"nproc": 5, "core": 0})
        self.assertEqual(plain[0], "setpriv")
        self.assertEqual(limited[:4], ["prlimit", "--core=0", "--nproc=5", "--"])
        self.assertEqual(limited[4:], plain)
        self.assertEqual(limited[-2:], ["--args", "/b"])
        self.assertIn("--args", limited)


if __name__ == "__main__":
    unittest.main()
