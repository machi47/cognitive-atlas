#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  ./scripts/install.sh
fi

source .venv/bin/activate
export ATLAS_LLM_PROVIDER="${ATLAS_LLM_PROVIDER:-fake}"
export ATLAS_DATA_DIR="${ATLAS_DATA_DIR:-./data}"

python -m atlas_api.db.migrate

uvicorn atlas_api.main:app --app-dir apps/api --host 127.0.0.1 --port 8787 &
API_PID=$!

cleanup() {
  kill "$API_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

if command -v pnpm >/dev/null 2>&1; then
  pnpm --dir apps/web dev
else
  npm --prefix apps/web run dev
fi

