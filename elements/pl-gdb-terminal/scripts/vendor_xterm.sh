#!/bin/bash
# Downloads xterm.js into the element so PrairieLearn serves it itself instead of
# the page loading it from a CDN. Run once (needs internet), then commit the files.
set -euo pipefail
VERSION="5.3.0"   # keep in sync with XTERM_VERSION in pl-gdb-terminal.py
DEST="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/clientFilesElement"
BASE="https://cdn.jsdelivr.net/npm/xterm@${VERSION}"

mkdir -p "$DEST"
curl -fsSL -o "$DEST/xterm.js"  "$BASE/lib/xterm.js"
curl -fsSL -o "$DEST/xterm.css" "$BASE/css/xterm.css"

echo "Downloaded xterm ${VERSION} into $DEST"
( cd "$DEST" && (sha256sum xterm.js xterm.css 2>/dev/null || shasum -a 256 xterm.js xterm.css) )
echo "Commit these files with the element. The element uses them automatically."
