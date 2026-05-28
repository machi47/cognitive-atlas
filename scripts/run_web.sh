#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
if command -v pnpm >/dev/null 2>&1; then
  pnpm --dir apps/web dev
else
  npm --prefix apps/web run dev
fi

