#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  ./scripts/install.sh
fi

source .venv/bin/activate
export ATLAS_DATA_DIR="${ATLAS_DATA_DIR:-./data/test}"
export ATLAS_LLM_PROVIDER="${ATLAS_LLM_PROVIDER:-fake}"
pytest apps/api/tests

if [ -d apps/web/node_modules ]; then
  if command -v pnpm >/dev/null 2>&1; then
    pnpm --dir apps/web test
  else
    npm --prefix apps/web test
  fi
fi

