#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

if [[ ! -f "$BACKEND/manage.py" ]]; then
  echo "[ERROR] Missing $BACKEND/manage.py" >&2
  exit 1
fi
if [[ ! -f "$FRONTEND/package.json" ]]; then
  echo "[ERROR] Missing $FRONTEND/package.json" >&2
  exit 1
fi

PY="python3"
command -v "$PY" >/dev/null 2>&1 || PY="python"

echo "=== Backend: venv, dependencies, migrate, seed_data ==="
cd "$BACKEND"
if [[ ! -d .venv ]]; then
  echo "Creating .venv..."
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip -q
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py seed_data

echo "=== Frontend: npm install, production build ==="
cd "$FRONTEND"
npm install
npm run build

echo ""
echo "=== Готово ==="
echo "Демо-пользователи: chef_anna, foodie_ivan, cook_maria (пароли в backend/recipes/management/commands/seed_data.py)"
echo ""
echo "Запуск API:     cd backend && source .venv/bin/activate && python manage.py runserver 127.0.0.1:8000"
echo "Preview UI:     cd frontend && npm run preview -- --host 127.0.0.1 --port 4173"
echo "Dev UI:         cd frontend && npm run dev"
echo ""

if [[ "${1:-}" == "--serve" ]]; then
  trap 'kill 0' INT TERM
  (cd "$BACKEND" && source .venv/bin/activate && exec python manage.py runserver 127.0.0.1:8000) &
  sleep 2
  (cd "$FRONTEND" && exec npm run preview -- --host 127.0.0.1 --port 4173) &
  wait
fi
