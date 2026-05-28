#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then
  ./scripts/install.sh
fi
source .venv/bin/activate
export ATLAS_DATA_DIR="${ATLAS_DATA_DIR:-./data}"
python -m atlas_api.db.migrate
exec uvicorn atlas_api.main:app --app-dir apps/api --host "${ATLAS_HOST:-127.0.0.1}" --port "${ATLAS_PORT:-8787}"

