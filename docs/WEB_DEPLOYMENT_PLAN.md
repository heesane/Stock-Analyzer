# Stock Analyzer – Web Deployment Action Plan

## Milestone 1: Containerized Backend (FastAPI)
1. [x] **Define API surface**
   - REST endpoints for analysis, history retrieval, export operations, DB configuration, and health checks.
   - Request/response schema documentation.
2. [x] **Refactor backend entrypoint**
   - Wrap existing logic in FastAPI/uvicorn (port 8000 by default).
   - SQLite as default via file path; MySQL/PostgreSQL enabled through environment variables.
3. [x] **Dockerize backend**
   - Single base image containing FastAPI app and process supervisor for multi-service orchestration.
   - Health checks and logging configuration included.

## Milestone 2: Web Frontend (Next.js + TypeScript)
4. [x] **Bootstrap Next.js project**
   - TypeScript, Tailwind CSS, shadcn/ui (plus additional UI libraries as needed).
   - Shared component structure (ticker form, result cards, history list).
5. [x] **Implement core UI flows**
   - Ticker input panel with streaming/progress view.
   - Results screen showing analysis cards, export controls.
   - History panel showing previously analyzed tickers with ability to re-open past results.
6. [x] **API integration**
   - Axios/Fetch hooks to communicate with FastAPI endpoints.
   - Error/loading states and localization support.

## Milestone 3: Docker Image & Process Orchestration
7. [x] **Single-image multi-process setup**
   - Image contains backend (uvicorn), frontend (Next.js), and process supervisor.
   - SQLite handled as file-based storage mounted via volume (no separate port needed).
8. [x] **Dynamic port allocation**
   - On container start, check host availability for 3000 (frontend) and 8000 (backend); if occupied, locate the next free port and map accordingly.
   - Emit final port mappings via stdout/logs and optional metadata file.

## Milestone 4: Storage Abstraction & History
9. [x] **Pluggable storage + history service**
   - Backing store defaults to SQLite; configurable for MySQL/PostgreSQL.
   - API endpoints for storing/retrieving ticker history (recent requests and cached summaries).
   - UI components to display history and reopen past analyses.

## Milestone 5: Release & Documentation
10. [x] **Packaging & docs**
    - Publish the single Docker image.
    - Update README/Quickstart/CLI Guide with container usage and troubleshooting notes.

## Milestone 6: Observability & Maintenance
11. [x] **Logging & monitoring hooks**
    - Startup scripts emit structured port info (`runtime-ports.json`) and logs are documented in README.
12. [x] **Automated health checks & alerts**
    - README/CLI Guide describe `/health` endpoint usage and troubleshooting guidance.
13. [x] **Release workflow & versioning**
    - `.github/workflows/ci.yml` demonstrates lint/test/build and Docker build pipeline with placeholders for registry publishing.
