"""Builds the one command the terminal server is allowed to run: gdb.

No third-party imports, so it can be unit-tested without terminado.
"""
import glob
import os


def build_command(
    *,
    uid: int,
    gid: int,
    home: str,
    program_args: list[str],
    script_dir: str,
    run_uses_shell: bool,
    running_as_root: bool,
) -> list[str]:
    # `env -i` gives gdb a clean environment. SHELL decides what gdb's
    # `shell`, `!`, `pipe` and `make` commands execute.
    shell = "/bin/sh" if run_uses_shell else "/bin/false"
    env_cmd = [
        "env", "-i",
        f"HOME={home}",
        f"SHELL={shell}",
        "TERM=xterm-256color",
        "LANG=C.UTF-8",
        "PATH=/usr/bin:/bin",
        "DEBUGINFOD_URLS=",
    ]

    # -nx/-nh: ignore every user/system/local gdbinit file.
    gdb_cmd = ["/usr/bin/gdb", "-q", "-nx", "-nh", f"--cd={home}"]
    if not run_uses_shell:
        # Start the debuggee directly (no shell). Side effect: `run < file`,
        # `$(...)` and globbing in `run` arguments do not work.
        gdb_cmd += ["-ex", "set startup-with-shell off"]
    for script in sorted(glob.glob(os.path.join(script_dir, "*.gdb"))):
        gdb_cmd += ["-x", script]
    if program_args:
        gdb_cmd += ["--args", *program_args]  # must stay last

    cmd = env_cmd + gdb_cmd
    if running_as_root:
        # Local Docker runs containers as root; production runs them as
        # 1001:1001. Drop privileges without using su or a shell.
        cmd = ["setpriv", f"--reuid={uid}", f"--regid={gid}", "--clear-groups"] + cmd
    return cmd
