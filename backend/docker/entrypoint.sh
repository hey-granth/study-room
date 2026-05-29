#!/bin/bash
set -euo pipefail

echo "[entrypoint] Running Alembic migrations..."
alembic upgrade head

echo "[entrypoint] Starting uvicorn..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1 \
  --proxy-headers \
  --forwarded-allow-ips="*" \
  --log-level info
