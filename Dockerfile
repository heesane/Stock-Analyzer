# ---------- Frontend build stage ----------
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend .
RUN npm run build

# ---------- Final runtime image ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Node.js runtime for Next.js (using Debian packages)
RUN apt-get update \
    && apt-get install -y curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy backend source
COPY backend /app/backend

# Copy frontend build artifacts
COPY --from=frontend-builder /frontend/.next /app/frontend/.next
COPY --from=frontend-builder /frontend/public /app/frontend/public
COPY --from=frontend-builder /frontend/package*.json /app/frontend/
COPY --from=frontend-builder /frontend/node_modules /app/frontend/node_modules

# Copy orchestrator scripts
COPY entrypoint.sh /app/entrypoint.sh
COPY backend/start.sh /app/backend/start.sh
COPY frontend/start.sh /app/frontend/start.sh
RUN chmod +x /app/entrypoint.sh /app/backend/start.sh /app/frontend/start.sh

ENV BACKEND_HOST=0.0.0.0 \
    BACKEND_PORT=8000 \
    BACKEND_MAX_PORT=9000 \
    FRONTEND_HOST=0.0.0.0 \
    FRONTEND_PORT=3000 \
    FRONTEND_MAX_PORT=3999

EXPOSE 8000 3000

CMD ["/app/entrypoint.sh"]
