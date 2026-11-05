`pl-memory-exploit` element

Displays a interactive terminal environment with gdb functionality. 

## Customization

| Attribute | Type | Default | Description|
| ------ | --- | --- | --- |
| `input-program` | Python file | Empty Python file | File that the student edits within `pl-file-editor`. |
| `vulnerable-program` | C file | — | File that the instructor provides that takes in output(s) from `input-program`. |
| `enable-aslr` | boolean | false | Randomizes memory locations of the stack and code between executions. |
| `enable-canary` | boolean | false | Randomizes and inserts a canary value directly after the buffer, which causes a segfault if modified. |
| `enable-non-exec-pages` | boolean | false | Prevents code stored in inputs and variables from being executed. |
| `enable-interact` | boolean | false | Allows for the usage of an interact API that allows for IO support between the input and vulnerable programs. |
| `width` | integer | 500 | Max characters per line for displaying Python code. |
| `shellcode-in-environ-var` | boolean | false | Places the shellcode inside of an environment variable. If false, provides shellcode within `input-program`. |

## Per-student environments

Every browser tab gets its own session; two students on the same question never share
files, processes or a gdb.

* The page calls `POST /session`; the backend returns a random token. The page keeps it in
  `sessionStorage`, so a reload reattaches to the same environment.
* A session owns a **slot**: a private directory `/sessions/s<N>` (mode 700) and a dedicated
  unix uid (`GDB_UID_BASE + N`). gdb and the student's `egg.py` run as that uid, so they cannot
  read, modify or signal another student's files or processes.
* The challenge binary is compiled once per distinct `vuln.c` and cached read-only under
  `/opt/challenge-cache/<hash>/`; all sessions debug the same binary.
* Slots are recycled. A session with no terminal attached is deleted after `GDB_IDLE_TTL`
  seconds (default 1800), or earlier (after 2 minutes idle) when all `GDB_MAX_SESSIONS`
  (default 64) slots are taken. The page re-syncs the editor's `egg.py` on every connect, so a
  recycled student loses nothing but gdb state.
* Per-session limits (see `LIMITS` in `server.py`) cap processes, open files and file size.

| Env var | Default | Meaning |
| --- | --- | --- |
| `GDB_MAX_SESSIONS` | 64 | Concurrent environments (= number of slots/uids). |
| `GDB_IDLE_TTL` | 1800 | Seconds before an unattached session is deleted. |
| `GDB_UID_BASE` | 20000 | First session uid. The compile uid is `GDB_UID_BASE - 1`. |

Run the tests with `python3 -m unittest discover -s tests -v` from `gdb_backend/` (the
isolation tests need root, e.g. inside the container).
