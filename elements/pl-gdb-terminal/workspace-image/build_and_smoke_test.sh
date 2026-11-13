#!/bin/bash
# Builds the workspace image and checks it the way PrairieLearn will run it:
# as user 1001:1001, serving on port 5000. Does not need PrairieLearn.
#   usage: [PLATFORM=linux/amd64] ./build_and_smoke_test.sh [image:tag]
#   PLATFORM: set on Apple Silicon so the image matches PrairieLearn's servers.
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="${1:-pl-gdb-workspace:latest}"

echo "Building $IMAGE ..."
docker build ${PLATFORM:+--platform "$PLATFORM"} -t "$IMAGE" "$HERE"

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

# Compile the sample program for each architecture through the same API the page
# uses, then run the result inside the container. 64-bit must work. 32-bit is
# reported separately because it also depends on the Docker host's kernel.
check_arch() {
  local arch="$1" resp out
  resp=$(python3 - "$HERE/smoke-test/vuln.c" "$arch" <<'PY' | curl -sS -X POST -H 'Content-Type: application/json' --data @- http://localhost:5001/sync-challenge
import json, sys
print(json.dumps({"code": open(sys.argv[1]).read(), "architecture": sys.argv[2]}))
PY
  )
  if ! echo "$resp" | grep -q '"ok": *true'; then
    echo "  ${arch}-bit: NOT AVAILABLE -> $resp"
    return 1
  fi
  if out=$(docker exec gdb-workspace-test /home/student/.challenge/vuln x 2>&1); then
    echo "  ${arch}-bit: compiled and ran -> $out"
  else
    echo "  ${arch}-bit: compiled but could not run -> $out"
    return 1
  fi
}

# Can gdb actually trace the compiled program? Compiling and running it is not enough:
# gdb needs ptrace, which does not work when an x86-64 image runs under emulation on
# Apple Silicon (gdb then reports "Couldn't get registers: Input/output error").
check_gdb() {
  local label="$1" out
  out=$(docker exec gdb-workspace-test gdb -batch -nx -q -ex run \
        --args /home/student/.challenge/vuln x 2>&1) || true
  if echo "$out" | grep -q "exited normally"; then
    echo "  gdb (${label}): can run and trace the program"
    if echo "$out" | grep -qi "disabling address space randomization"; then
      echo "    note: gdb could not turn ASLR off here, so addresses may change between runs."
    fi
  else
    echo "  gdb (${label}): CANNOT TRACE the program ->"
    echo "$out" | tail -3 | sed 's/^/      /'
    return 1
  fi
}

echo "Compiling, running and tracing the smoke-test program ..."
check_arch 64 || { docker logs gdb-workspace-test; exit 1; }
if ! check_gdb 64-bit; then
  echo
  echo "  gdb cannot debug programs in this Docker setup, so the terminal will not work here."
  echo "  On Apple Silicon this is expected for an amd64 image: the emulation does not support"
  echo "  ptrace. For local testing build WITHOUT PLATFORM (a native arm64 image, ARM programs),"
  echo "  or test on an x86-64 Linux machine or on your PrairieLearn site."
  exit 1
fi
if check_arch 32; then
  check_gdb 32-bit || echo "  WARNING: 32-bit programs run but gdb cannot trace them here."
else
  echo
  echo "  WARNING: 32-bit questions (architecture=\"32\") will not work with this image on this"
  echo "  Docker host. 64-bit is fine. See the message above, and the README's 32-bit section."
fi
echo
echo "OK. (The test container is removed on exit.)"
echo
echo "To publish: docker tag $IMAGE <dockerhub-user>/pl-gdb-workspace:<version>"
echo "            docker push <dockerhub-user>/pl-gdb-workspace:<version>"
echo "Use a pinned version tag (not 'latest') in the question's workspaceOptions.image."
