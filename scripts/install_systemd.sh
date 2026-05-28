#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
INSTALL_DIR="${INSTALL_DIR:-$(pwd)}"
SERVICE_DIR="${SERVICE_DIR:-$HOME/.config/systemd/user}"
mkdir -p "$SERVICE_DIR"
sed "s#__INSTALL_DIR__#${INSTALL_DIR}#g" deploy/cognitive-atlas.service > "$SERVICE_DIR/cognitive-atlas.service"
systemctl --user daemon-reload
systemctl --user enable cognitive-atlas.service
echo "Installed user service. Start with: systemctl --user start cognitive-atlas.service"

