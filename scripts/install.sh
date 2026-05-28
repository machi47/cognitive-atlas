#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-python3.12}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "python3.12 is required. Set PYTHON_BIN to a Python 3.12+ interpreter." >&2
  exit 1
fi

"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e "apps/api[dev]"

if command -v pnpm >/dev/null 2>&1; then
  pnpm --dir apps/web install
else
  npm --prefix apps/web install
fi

python -m atlas_api.db.migrate

