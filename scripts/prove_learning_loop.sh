#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export ATLAS_LLM_PROVIDER="${ATLAS_LLM_PROVIDER:-codex}"
export ATLAS_ALLOW_FAKE_FOR_TESTS="${ATLAS_ALLOW_FAKE_FOR_TESTS:-false}"

if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

pytest apps/api/tests/test_cross_session_learning_loop.py -q
