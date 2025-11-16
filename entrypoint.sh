#!/usr/bin/env bash
set -euo pipefail

/app/backend/start.sh &
BACKEND_PID=$!

/app/frontend/start.sh &
FRONTEND_PID=$!

cat <<JSON > /app/runtime-ports.json
{
  "backend_port": "${BACKEND_PORT}",
  "frontend_port": "${FRONTEND_PORT}"
}
JSON

cleanup() {
  echo "[entrypoint] Shutting down..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}

trap cleanup SIGINT SIGTERM

wait -n "$BACKEND_PID" "$FRONTEND_PID"
status=$?
cleanup
exit $status
