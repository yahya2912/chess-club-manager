#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
    echo "Missing .env file."
    echo "Create it from .env.example first."
    exit 1
fi

echo "Starting PostgreSQL and FastAPI with Docker Compose..."
docker compose up -d --build

echo "Waiting for API health check..."
until curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1
do
    sleep 1
done

echo "Backend is ready."
echo "Starting Chess Club Manager..."
PYTHONPATH="$ROOT/frontend" python3 -m chess_club_fe.main
