#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
    echo "Missing .env file."
    echo "Create it from .env.example first."
    exit 1
fi

# Load DB + API configuration
set -a
source .env
set +a

export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export CHESS_API_URL="${CHESS_API_URL:-http://127.0.0.1:8000}"
export CHESS_API_KEY="${CHESS_API_KEY:-$API_KEY}"

echo "Starting PostgreSQL..."
docker compose up -d

echo "Waiting for PostgreSQL..."
until docker compose exec -T postgres \
    pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1
do
    sleep 1
done

if [[ ! -x api/.venv/bin/uvicorn ]]; then
    echo "API virtual environment not found."
    echo "Create api/.venv and install requirements first."
    exit 1
fi

if ss -ltn | grep -q ':8000 '; then
    echo "Port 8000 is already in use."
    echo "Stop the existing API first, for example:"
    echo "  pkill -f 'uvicorn app.main:app'"
    exit 1
fi

echo "Starting API..."
api/.venv/bin/uvicorn app.main:app \
    --app-dir api \
    --host 127.0.0.1 \
    --port 8000 &

API_PID=$!

cleanup() {
    echo
    echo "Stopping API..."
    kill "$API_PID" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

# Give Uvicorn a moment to bind its port
sleep 1

echo "Starting Chess Club Manager..."
PYTHONPATH="$ROOT/frontend" python3 -m chess_club_fe.main
