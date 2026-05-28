from __future__ import annotations

import asyncio

from atlas_api.config import get_settings
from atlas_api.db.connection import Database
from atlas_api.db.migrations import run_migrations


async def main() -> None:
    settings = get_settings()
    await run_migrations(Database(settings.database_path))
    print(f"Migrated {settings.database_path}")


if __name__ == "__main__":
    asyncio.run(main())

