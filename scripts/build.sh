#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if command -v pnpm >/dev/null 2>&1; then
  pnpm --dir apps/web install
  pnpm --dir apps/web build
else
  npm --prefix apps/web install
  npm --prefix apps/web run build
fi

mkdir -p apps/api/static
cp -R apps/web/dist/* apps/api/static/ 2>/dev/null || true

