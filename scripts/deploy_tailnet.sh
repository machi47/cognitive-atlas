#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
./scripts/build.sh
echo "Start the API with ./scripts/run_api.sh, then run ./scripts/tailscale_serve.sh"

