#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

HOST="${ATLAS_HOST:-0.0.0.0}"
PORT="${ATLAS_PORT:-8788}"
DATA_DIR="${ATLAS_DATA_DIR:-./data}"

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI is required for standalone mode. Install Codex and run: codex login" >&2
  exit 1
fi

if ! codex login status >/dev/null 2>&1; then
  echo "Codex CLI is not logged in. Run: codex login" >&2
  exit 1
fi

if [ ! -d .venv ]; then
  ./scripts/install.sh
fi

source .venv/bin/activate

if command -v pnpm >/dev/null 2>&1; then
  pnpm --dir apps/web install
  pnpm --dir apps/web build
else
  npm --prefix apps/web install
  npm --prefix apps/web run build
fi

export ATLAS_HOST="$HOST"
export ATLAS_PORT="$PORT"
export ATLAS_DATA_DIR="$DATA_DIR"
export ATLAS_LLM_PROVIDER="${ATLAS_LLM_PROVIDER:-codex}"
export ATLAS_ALLOW_FAKE_FOR_TESTS="${ATLAS_ALLOW_FAKE_FOR_TESTS:-false}"
export ATLAS_DEBUG="${ATLAS_DEBUG:-false}"
export ATLAS_STORE_LLM_PROMPTS="${ATLAS_STORE_LLM_PROMPTS:-false}"

python -m atlas_api.db.migrate

cat <<EOF
Research Partner standalone is starting.

Local URL:
  http://127.0.0.1:${PORT}

Network URL:
  http://<agent-machine-ip>:${PORT}

Runtime data stays local in:
  ${DATA_DIR}

EOF

exec uvicorn atlas_api.main:app --app-dir apps/api --host "$HOST" --port "$PORT"
