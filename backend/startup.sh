#!/bin/bash
# Production startup script — seeds the database on first run, then starts the API.
set -e

echo "=============================="
echo "  DropAI — Production Startup"
echo "=============================="

echo "[1/2] Running database seed..."
python seed.py || echo "  (seed already ran or failed non-fatally — continuing)"

echo "[2/2] Starting API server on port ${PORT:-8000}..."
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --workers 1 \
  --log-level info
