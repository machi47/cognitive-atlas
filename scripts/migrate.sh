#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then
  ./scripts/install.sh
fi
source .venv/bin/activate
python -m atlas_api.db.migrate

