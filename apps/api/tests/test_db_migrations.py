import aiosqlite
import pytest

from atlas_api.db.connection import Database
from atlas_api.db.migrations import run_migrations


@pytest.mark.asyncio
async def test_db_migration_creates_tables(tmp_path):
    db = Database(tmp_path / "atlas.db")
    await run_migrations(db)
    conn = await aiosqlite.connect(tmp_path / "atlas.db")
    try:
        row = await (await conn.execute("select name from sqlite_master where type='table' and name='sessions'")).fetchone()
    finally:
        await conn.close()
    assert row is not None
