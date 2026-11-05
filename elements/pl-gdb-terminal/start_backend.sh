#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/gdb_backend"

echo "Building GDB backend..."
docker build -t ucb-star-gdb:latest "$BACKEND_DIR"

# Stop and remove existing container if it exists
docker rm -f gdb-backend-container 2>/dev/null || true

echo "Starting GDB backend container on port 5001..."
# Published on loopback only: the backend gives a shell-like session to anyone
# who can reach it. If the page says "Could not reach backend", try removing
# the "127.0.0.1:" prefix (some setups resolve localhost to ::1).
# Resource caps apply to the whole container (all students together); per-student
# caps (process count, open files, file size) are applied inside by the server.
# /sessions is a size-limited tmpfs so a student filling the disk hits a quota
# instead of the host. 'exec' keeps ./egg.py and student-built programs runnable.
docker run -d -p 127.0.0.1:5001:5000 --name gdb-backend-container \
  --memory 2g --cpus 2 --pids-limit 1024 \
  --tmpfs /sessions:rw,exec,nosuid,nodev,size=512m,mode=711 \
  ucb-star-gdb:latest

echo "Waiting for the backend..."
for i in $(seq 1 20); do
  if curl -fs http://localhost:5001/health >/dev/null; then
    echo "GDB backend is ready on port 5001!"
    exit 0
  fi
  sleep 0.5
done
echo "Backend did not answer. Check: docker logs gdb-backend-container" >&2
exit 1
