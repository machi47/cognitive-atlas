#!/usr/bin/env bash
set -euo pipefail

if ! command -v tailscale >/dev/null 2>&1; then
  echo "tailscale is not installed."
  exit 1
fi

tailscale status
echo
echo "Expose the local app to your tailnet with one of:"
echo "  tailscale serve 8787"
echo "  tailscale serve localhost:8787"
echo
echo "Do not use Funnel for this private app."

