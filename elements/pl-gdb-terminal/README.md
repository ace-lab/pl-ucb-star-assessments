# pl-gdb-terminal

docker run -it --rm -p 3000:3000 \
  -v "$HOME/pl-ucb-star-assessments:/course" \
  -v "$HOME/pl_ag_jobs:/jobs" \
  -e HOST_JOBS_DIR="$HOME/pl_ag_jobs" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --add-host=host.docker.internal:172.17.0.1 \
  prairielearn/prairielearn

A PrairieLearn element that puts a **gdb terminal inside a question page**, so students can debug and
exploit a small C program without installing anything. Each student gets their own isolated
environment, and you choose which memory-safety protections the program is built with.

It is designed for memory-safety and binary-exploitation exercises (stack smashing, shellcode,
canaries, ASLR), but it works for any question where students should step through a C program in gdb.

## What students see

- A terminal running gdb, already attached to your program, on the question page.
- An editor (`pl-file-editor`) for their exploit or input script, `egg.py`, with a **Sync** button
  that copies it into their environment. It is also synced automatically when the terminal connects.
- Typical use inside gdb: `run $(python3 egg.py)`.

To keep students on task, gdb's `shell`, `pipe`, `edit`, `make`, `source`, `file` and `exec-file`
commands are disabled, and gdb ignores all user and system init files.

## How it works

```
question page (this element)  --same origin-->  /pl/workspace/<id>/container/  -->  workspace container
   xterm.js + egg.py editor                      (proxied by PrairieLearn)             small server + gdb
```

The element uses PrairieLearn's **workspace** feature as its backend. PrairieLearn starts one container
per student and question from a Docker image that you publish (source included in this directory),
proxies it on the PrairieLearn site, and handles login and cleanup. The question page talks to that
container directly, so there is no separate server for you to host.

## Requirements

- A PrairieLearn instance with workspaces enabled (hosted PrairieLearn deployments normally have this).
- A Docker Hub account (the workspace image is pulled from Docker Hub) and Docker on your computer to
  build the image.
- Permission to add an element to your course repository (`elements/`).
- For grading: an external grader of your own (see [Grading](#grading)).

## Installation

### 1. Build and publish the workspace image

The image source is in `workspace-image/`. From that folder:

```bash
./build_and_smoke_test.sh <dockerhub-user>/pl-gdb-workspace:<version>
docker login
docker push <dockerhub-user>/pl-gdb-workspace:<version>
```

- The Docker Hub repository must be **public**.
- Use a pinned version tag (`v1`, `v2`, ...), not `latest`, so you decide when students get a change.
- On an Apple Silicon Mac, build for the servers' architecture: `PLATFORM=linux/amd64 ./build_and_smoke_test.sh <image:tag>`.
- Then, in your course's **Sync** page, find the image under **Docker images** and click **Sync**
  (needed on hosted PrairieLearn so its servers pick the image up).

The smoke test builds the image, starts it the way PrairieLearn does (as user 1001 on port 5000), and
compiles a sample program. It does not need PrairieLearn.

### 2. Add the element to your course

Copy this whole directory into your course repository as `elements/pl-gdb-terminal/`, commit, push and
sync the course.

Optional: run `scripts/vendor_xterm.sh` first (needs internet) and commit the two files it creates in
`clientFilesElement/`. The page then serves the terminal library itself instead of loading it from
`cdn.jsdelivr.net`.

### 3. Create a question

A question using this element needs two things.

`info.json` (alongside your usual fields):

```json
"singleVariant": true,
"workspaceOptions": {
  "image": "<dockerhub-user>/pl-gdb-workspace:<version>",
  "port": 5000,
  "home": "/home/student",
  "syncIgnore": [".challenge/"]
}
```

`question.html`:

```html
<pl-workspace label="Start environment"></pl-workspace>
<pl-gdb-terminal vulnerable-source-file="vuln.c"></pl-gdb-terminal>
<pl-file-editor file-name="egg.py"></pl-file-editor>
```

Put the program students will debug in the question directory as `vuln.c`, next to `question.html`.

## Element attributes

All attributes are optional.

| Attribute | Default | Meaning |
| --- | --- | --- |
| `vulnerable-source-file` | `vuln.c` | C source file in the question directory that students debug. |
| `enable-aslr` | `false` | Leave address-space randomization **on** while the program runs in gdb. |
| `enable-canary` | `false` | Build the program with stack canaries. |
| `enable-non-exec-pages` | `false` | Build the program with a non-executable stack (NX). |
| `autostart-iframe` | `false` | **Experimental.** Start the workspace inside the page and avoid opening a second tab (see below). |

### Protections

The defaults are the classic "everything off" configuration, so a question that sets no attributes is
the easiest to exploit. Turn protections on to make a question harder.

| Attribute | Off (default) | On |
| --- | --- | --- |
| `enable-aslr` | gdb disables ASLR, so stack and library addresses are the same on every run. | ASLR stays on; addresses change between runs. |
| `enable-canary` | Compiled with `-fno-stack-protector`. | Compiled with `-fstack-protector-all`: every function gets a canary. |
| `enable-non-exec-pages` | Stack is executable (`-z execstack`), so shellcode on the stack runs. | Stack is not executable (`-z noexecstack`); injected shellcode will fault. |

The program is always built with `-g -O0 -no-pie`, so its own code and data addresses are fixed
whatever ASLR does. Canary and NX are properties of the compiled binary; ASLR is applied when gdb
starts the program. Changing any attribute takes effect the next time a student opens the question.

Example: a return-to-libc question with NX and ASLR on, canary off:

```html
<pl-gdb-terminal vulnerable-source-file="vuln.c"
                 enable-non-exec-pages="true" enable-aslr="true"></pl-gdb-terminal>
```

## How a student's session starts

1. The page loads and waits for the student's container to answer.
2. The student clicks **Start environment**. PrairieLearn starts their container; the first start can
   take a few minutes while the image is pulled onto a server.
3. The terminal then connects by itself: it compiles `vuln.c`, starts gdb and syncs `egg.py`.

`autostart-iframe="true"` loads the workspace page in a hidden frame so the container starts without
the click and without a second browser tab. It is experimental: test it on a development instance
first. If nothing is up after about a minute, a link to open the workspace in a new tab appears.

## Grading

The workspace is only the student's debugging environment. Grade the submission the way you would
any other file upload:

- Keep `pl-file-editor` for `egg.py` and use PrairieLearn's external grader (or any other grading
  method you already use) to run the student's `egg.py` against **your own copy** of the program.
- Do not rely on files inside the workspace container for grading. Students can edit anything in
  their container, including the compiled program.
- If you would rather grade files from the workspace, list them in `workspaceOptions.gradedFiles` and
  remove `pl-file-editor`, so there is a single source for each file.

## Customizing

| To change | Edit | Then |
| --- | --- | --- |
| Which gdb commands are blocked, or gdb settings | `workspace-image/gdb/*.gdb` (loaded in name order) | Rebuild and push the image with a new tag. |
| Compiler flags or the set of protections | `cflags()` in `workspace-image/server.py` | Rebuild and push the image. |
| Allow `run < file` and `$(...)` or disable them | `GDB_RUN_USES_SHELL` in the `Dockerfile` (`1` = shell, needed for `run $(python3 egg.py)`) | Rebuild and push the image. |
| The program students debug | `vuln.c` in the question directory | Sync the course. |

After rebuilding the image, change `workspaceOptions.image` in your questions to the new tag and sync
the **Docker images** entry again.

## Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| `No workspace host is available...` | PrairieLearn's workspace host is not running. This happens when running PrairieLearn locally without workspace support. | Hosted sites: contact your PrairieLearn administrators. Local: start PrairieLearn with the Docker socket and jobs directory options from PrairieLearn's "Running locally" documentation. |
| `Error joining workspace: Incorrect rowCount: 0` | The page points at a workspace that PrairieLearn does not have, most often a stale tab or workspace page left open after PrairieLearn's database was reset or the question was re-created. | Close old workspace tabs and open the question again from the question list (a new variant gets a new workspace). The element and image are not involved. |
| Terminal stays on "Waiting for workspace..." | Container still starting, image not found, or the workspace page errored. | Click **Start environment**, wait a few minutes, then **Reboot** in the workspace page. Check the image name and tag, that the repository is public, and that you synced it. |
| `Challenge failed to compile` | Error in `vuln.c`. | The compiler output is shown in the terminal; fix the source. |
| `Error disabling address space randomization` in gdb | The platform's container security settings block gdb's ASLR switch. | Compare an address across two runs. If it is not stable, ASLR cannot be turned off on that site; ask your administrators, or design the question around ASLR being on. |
| Terminal says `[disconnected from your workspace]` | The workspace was stopped or rebooted. | Reload the page and start the workspace again. |

## Security notes

- Every student has their own container, and PrairieLearn authenticates requests to it. A student can
  break their own environment (rebooting fixes it) but not another student's.
- Students can read everything in the image and in their home directory. Never put solutions, flags
  or grader secrets there.
- The program source is sent from the page and compiled inside the student's own container, so a
  student could compile something else in their container. That only affects their own environment.
- gdb and the student's `egg.py` run as the same user as the container's small server. Students can
  stop that server; **Reboot** restores it.

## Directory layout and development

| Path | Purpose |
| --- | --- |
| `info.json`, `pl-gdb-terminal.py`, `pl-gdb-terminal.html` | The element. |
| `clientFilesElement/` | Optional vendored terminal library (this folder is served to students; add nothing else). |
| `workspace-image/` | Source of the Docker image: `Dockerfile`, `server.py`, `launcher.py`, `gdb/`, `smoke-test/`. PrairieLearn does not read this folder. |
| `scripts/vendor_xterm.sh` | Downloads the terminal library into `clientFilesElement/`. |

The image cannot be built from the course repository by PrairieLearn; it must be built from
`workspace-image/` and pushed to Docker Hub.

Checked during development: the backend's compile and protection logic (canary and NX verified on the
resulting binaries), the element's rendering, and the page script's syntax. Not exercised: the Docker
build and the full flow inside PrairieLearn, and gdb's ASLR setting on a real workspace host.
