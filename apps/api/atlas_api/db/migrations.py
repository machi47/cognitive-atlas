from __future__ import annotations

from pathlib import Path

from atlas_api.db.connection import Database
from atlas_api.util.time import utc_now


SCHEMA_VERSION = 1


async def run_migrations(db: Database) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    schema_sql = schema_path.read_text(encoding="utf-8")
    conn = await db.connect()
    try:
        await conn.executescript(schema_sql)
        row = await (await conn.execute("select max(version) as version from schema_versions")).fetchone()
        current = row["version"] if row and row["version"] is not None else 0
        if current < SCHEMA_VERSION:
            await conn.execute(
                "insert or replace into schema_versions(version, applied_at) values(?, ?)",
                (SCHEMA_VERSION, utc_now()),
            )
        await conn.commit()
    finally:
        await conn.close()
