#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/gdb_backend"

echo "Building GDB backend..."
docker build -t ucb-star-gdb:latest "$BACKEND_DIR"

# Stop and remove existing container if it exists
docker rm -f gdb-backend-container 2>/dev/null || true

echo "Starting GDB backend container on port 5001..."
docker run -d -p 5001:5000 --name gdb-backend-container ucb-star-gdb:latest
echo "GDB backend is ready on port 5001!"