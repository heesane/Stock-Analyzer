#!/usr/bin/env bash
set -euo pipefail

HOST=${BACKEND_HOST:-0.0.0.0}
PORT=${BACKEND_PORT:-8000}
MAX_PORT=${BACKEND_MAX_PORT:-9000}

is_port_free() {
  python - "$1" <<'PY'
import socket, sys
port = int(sys.argv[1])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("", port))
    except OSError:
        sys.exit(1)
sys.exit(0)
PY
}

while ! is_port_free "$PORT"; do
  if [ "$PORT" -ge "$MAX_PORT" ]; then
    echo "[backend] No free port between ${BACKEND_PORT:-8000} and $MAX_PORT" >&2
    exit 1
  fi
  PORT=$((PORT + 1))
done

export BACKEND_PORT="$PORT"
echo "[backend] Starting API on port $PORT"
exec uvicorn backend.app.server:app --host "$HOST" --port "$PORT"
