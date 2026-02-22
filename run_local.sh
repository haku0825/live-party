#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ -z "${VIRTUAL_ENV:-}" ] && [ -f ".venv/bin/activate" ]; then
  . ".venv/bin/activate"
fi

if [ ! -f ".env.local" ]; then
  echo "Missing .env.local file."
  echo "Create it from .env.example or use the included .env.local defaults."
  exit 1
fi

set -a
. ".env.local"
set +a

HOST_PORT="${1:-127.0.0.1:8000}"
python manage.py runserver "$HOST_PORT"
