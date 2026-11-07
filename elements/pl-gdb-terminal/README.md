# pl-gdb-terminal

An inline gdb terminal for PrairieLearn questions. This directory is the whole element: copy it into
your course repo as `elements/pl-gdb-terminal/`. The terminal runs in the student's own PrairieLearn
**workspace** container, so PrairieLearn provides per-student containers, login-based access and lifecycle.

```
question page (element)  --same origin-->  /pl/workspace/<id>/container/  -->  workspace container
  xterm.js + editor Sync                    (proxied by PrairieLearn)             server.py + gdb
```

## What is in this directory

| Path | Purpose |
| --- | --- |
| `info.json`, `pl-gdb-terminal.py`, `pl-gdb-terminal.html` | The element itself. |
| `clientFilesElement/` | Optional vendored xterm.js (served to students; nothing else goes here). |
| `workspace-image/` | Source of the Docker image the workspace runs: `Dockerfile`, `server.py`, `launcher.py`, `gdb/`, `smoke-test/`. PrairieLearn does not read this folder; it is here so the image is versioned with the element. |
| `scripts/vendor_xterm.sh` | Downloads xterm.js into `clientFilesElement/`. |

The question itself lives elsewhere in your course repository.

One part cannot live inside the directory: PrairieLearn pulls the workspace image **by name from a registry**
and cannot build it from the repo, so the image must be built from `workspace-image/` and pushed.

## Deploy

1. **Image.** `cd workspace-image && ./build_and_smoke_test.sh <dockerhub-user>/pl-gdb-workspace:<version>`,
   then `docker push` the same name. The repository must be public; use a pinned version tag, not `latest`.
2. **Element.** Put this directory in the course repo at `elements/pl-gdb-terminal/`.
   Optional first: run `scripts/vendor_xterm.sh` (needs internet) and commit the two files it creates.
   Without them the page loads xterm.js from `cdn.jsdelivr.net`.
3. **Question.** In the question's `info.json`:
   ```json
   "singleVariant": true,
   "workspaceOptions": { "image": "<dockerhub-user>/pl-gdb-workspace:<version>", "syncIgnore": [".challenge/"] }
   ```
   and in `question.html`:
   ```html
   <pl-workspace label="Start environment"></pl-workspace>
   <pl-gdb-terminal vulnerable-source-file="vuln.c"></pl-gdb-terminal>
   ```
4. Sync the course and open the question as a student.

## How a student's session starts

1. The page loads; the element polls `/pl/workspace/<id>/container/health`.
2. The student clicks **Start environment** (`<pl-workspace>`). PrairieLearn starts their container
   (the first start can take minutes while the host pulls the image).
3. Once `/health` answers, the terminal compiles `vuln.c`, connects gdb and syncs `egg.py` by itself.

### Optional, experimental: no second tab (`autostart-iframe="true"`)

Loads the workspace page in a hidden iframe so the container starts inside the question page, and swallows
clicks on the `<pl-workspace>` link so no new tab opens. If nothing is up after about a minute, an "Open
workspace in a new tab" link appears as a fallback. Test it on a development instance before production.

## Grading

Unchanged: submit through `pl-file-editor` as before. The workspace is only the student's debugging
environment, so `gradedFiles` is not used. If you add `gradedFiles: ["egg.py"]`, remove `pl-file-editor`
so there is a single source for that file.

## Things to check on a real site

* The container runs as 1001 (it does) and the image must be pullable by the workspace hosts. Ask your
  PrairieLearn administrators about registry rules and Docker Hub pull limits.
* gdb turns ASLR off by default. If PrairieLearn's container security settings block that, gdb prints
  "Error disabling address space randomization". Run a program twice in a real workspace and compare an address.
* Everything in the image and the student's home is readable by the student: keep reference solutions and
  flags out of both.
* `aslr`, `canary` and `nx` are passed to the page but not yet honoured by the backend.

## Tested during development

Backend compile/sync logic as uid 1001, element rendering (with and without vendored xterm files), the
vendoring script's destination, JS syntax. The Docker build, `build_and_smoke_test.sh` and the full flow
inside PrairieLearn have not been run.
