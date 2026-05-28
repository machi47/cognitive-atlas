from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path
from typing import Any, TypeVar

import aiosqlite

T = TypeVar("T")


class Database:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def connect(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect(self.path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON")
        await conn.execute("PRAGMA journal_mode = WAL")
        await conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    async def execute(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        conn = await self.connect()
        try:
            await conn.execute(sql, params)
            await conn.commit()
        finally:
            await conn.close()

    async def fetchone(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        conn = await self.connect()
        try:
            cursor = await conn.execute(sql, params)
            row = await cursor.fetchone()
            return dict(row) if row else None
        finally:
            await conn.close()

    async def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        conn = await self.connect()
        try:
            cursor = await conn.execute(sql, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    async def transaction(self, fn: Callable[[aiosqlite.Connection], Awaitable[T]]) -> T:
        conn = await self.connect()
        try:
            await conn.execute("BEGIN")
            result = await fn(conn)
            await conn.commit()
            return result
        except Exception:
            await conn.rollback()
            raise
        finally:
            await conn.close()


async def iter_rows(cursor: aiosqlite.Cursor) -> AsyncIterator[dict[str, Any]]:
    async for row in cursor:
        yield dict(row)
