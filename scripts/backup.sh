#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
DB="${ATLAS_DATA_DIR:-./data}/cognitive_atlas.db"
DEST="${ATLAS_DATA_DIR:-./data}/backups"
mkdir -p "$DEST"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
if [ -f "$DB" ]; then
  sqlite3 "$DB" ".backup '${DEST}/cognitive_atlas_${STAMP}.db'"
  echo "Backup written to ${DEST}/cognitive_atlas_${STAMP}.db"
else
  echo "No database found at $DB"
fi

