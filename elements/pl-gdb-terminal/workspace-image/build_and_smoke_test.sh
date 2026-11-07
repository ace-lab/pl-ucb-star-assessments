#!/bin/bash
# Builds the workspace image and checks it the way PrairieLearn will run it:
# as user 1001:1001, serving on port 5000. Does not need PrairieLearn.
#   usage: ./build_and_smoke_test.sh [image:tag]
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="${1:-pl-gdb-workspace:latest}"

echo "Building $IMAGE ..."
docker build -t "$IMAGE" "$HERE"

docker rm -f gdb-workspace-test 2>/dev/null || true
docker run -d --name gdb-workspace-test --user 1001:1001 -p 127.0.0.1:5001:5000 "$IMAGE" >/dev/null
trap 'docker rm -f gdb-workspace-test >/dev/null 2>&1 || true' EXIT

echo "Waiting for /health ..."
for i in $(seq 1 20); do
  if curl -fs http://localhost:5001/health >/dev/null; then break; fi
  sleep 0.5
done
curl -fsS http://localhost:5001/health || { docker logs gdb-workspace-test; exit 1; }
echo
curl -fsS http://localhost:5001/ >/dev/null && echo "GET / -> 200"

echo "Compiling the smoke-test program ..."
python3 - "$HERE/smoke-test/vuln.c" <<'PY' | curl -fsS -X POST -H 'Content-Type: application/json' --data @- http://localhost:5001/sync-challenge
import json, sys
print(json.dumps({"code": open(sys.argv[1]).read()}))
PY
echo
echo "OK. (The test container is removed on exit.)"
echo
echo "To publish: docker tag $IMAGE <dockerhub-user>/pl-gdb-workspace:<version>"
echo "            docker push <dockerhub-user>/pl-gdb-workspace:<version>"
echo "Use a pinned version tag (not 'latest') in the question's workspaceOptions.image."
