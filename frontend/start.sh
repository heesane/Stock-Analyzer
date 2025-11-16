#!/usr/bin/env bash
set -euo pipefail

HOST=${FRONTEND_HOST:-0.0.0.0}
PORT=${FRONTEND_PORT:-3000}
MAX_PORT=${FRONTEND_MAX_PORT:-3999}
APP_DIR="/app/frontend"

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
    echo "[frontend] No free port between ${FRONTEND_PORT:-3000} and $MAX_PORT" >&2
    exit 1
  fi
  PORT=$((PORT + 1))
done

cd "$APP_DIR"
export FRONTEND_PORT="$PORT"
echo "[frontend] Starting Next.js on port $PORT"
exec node_modules/.bin/next start -H "$HOST" -p "$PORT"
