# Backend Service

- Framework: FastAPI + Uvicorn
- Default port: 8000 (auto-increments if occupied)
- Key endpoints:
  - `GET /health`
  - `POST /analyze`
- Docker image builds with `backend/Dockerfile` and starts via `backend/start.sh`.

Environment variables:
- `BACKEND_HOST` (default `0.0.0.0`)
- `BACKEND_PORT` (default `8000`)
- `BACKEND_MAX_PORT` (fails if no free port up to this number)
