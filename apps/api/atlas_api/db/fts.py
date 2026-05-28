from __future__ import annotations

import aiosqlite


async def index_turn(conn: aiosqlite.Connection, turn_id: str, session_id: str, content: str) -> None:
    await conn.execute("delete from turns_fts where turn_id = ?", (turn_id,))
    await conn.execute(
        "insert into turns_fts(turn_id, session_id, content) values(?, ?, ?)",
        (turn_id, session_id, content),
    )


async def index_session(conn: aiosqlite.Connection, session_id: str, title: str, summary: str | None) -> None:
    await conn.execute("delete from sessions_fts where session_id = ?", (session_id,))
    await conn.execute(
        "insert into sessions_fts(session_id, title, summary) values(?, ?, ?)",
        (session_id, title, summary or ""),
    )


async def index_node(conn: aiosqlite.Connection, node_id: str, map_id: str, label: str, description: str | None) -> None:
    await conn.execute("delete from concept_nodes_fts where node_id = ?", (node_id,))
    await conn.execute(
        "insert into concept_nodes_fts(node_id, map_id, label, description) values(?, ?, ?, ?)",
        (node_id, map_id, label, description or ""),
    )


async def index_claim(conn: aiosqlite.Connection, claim_id: str, session_id: str | None, text: str) -> None:
    await conn.execute("delete from claims_fts where claim_id = ?", (claim_id,))
    await conn.execute(
        "insert into claims_fts(claim_id, session_id, text) values(?, ?, ?)",
        (claim_id, session_id or "", text),
    )


async def index_source(conn: aiosqlite.Connection, source_id: str, title: str, abstract: str | None, key_claims: list[str]) -> None:
    await conn.execute("delete from source_cards_fts where source_id = ?", (source_id,))
    await conn.execute(
        "insert into source_cards_fts(source_id, title, abstract, key_claims) values(?, ?, ?, ?)",
        (source_id, title, abstract or "", "\n".join(key_claims)),
    )

