#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

python - <<'PY'
from __future__ import annotations

import asyncio
import json
import shutil

from atlas_api.config import get_settings
from atlas_api.db.connection import Database
from atlas_api.db.migrations import run_migrations
from atlas_api.db.repositories import Repository


async def main() -> None:
    get_settings.cache_clear()
    settings = get_settings()
    db = Database(settings.database_path)
    await run_migrations(db)
    repo = Repository(db)
    workspace_id = await repo.ensure_default_workspace()
    counts = await repo.reset_workspace_data(workspace_id)
    for path in [settings.artifacts_dir, settings.exports_dir, settings.codex_runs_dir]:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
        (path / ".gitkeep").touch()
    print(json.dumps({
        "status": "reset",
        "data_dir": str(settings.data_dir),
        "database": str(settings.database_path),
        "workspace_id": workspace_id,
        "deleted": counts,
    }, indent=2))


asyncio.run(main())
PY
