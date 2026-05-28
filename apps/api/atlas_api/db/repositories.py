from __future__ import annotations

from typing import Any

import aiosqlite

from atlas_api.db import fts
from atlas_api.db.connection import Database
from atlas_api.models.atlas import (
    AtlasTree,
    AtlasTreeDomain,
    AtlasTreeMap,
    ConceptNodeOut,
    MapGraph,
    OpenQuestionOut,
    RelationEdgeOut,
    TopicMapOut,
)
from atlas_api.models.events import EventOut
from atlas_api.models.patches import MapPatchOut
from atlas_api.models.sessions import SessionOut
from atlas_api.models.sources import SourceCardIn, SourceCardOut
from atlas_api.models.turns import TurnOut
from atlas_api.util.ids import new_id
from atlas_api.util.json import dumps, loads
from atlas_api.util.time import utc_now

DEFAULT_WORKSPACE_ID = "ws_default"


class Repository:
    def __init__(self, db: Database):
        self.db = db

    async def ensure_default_workspace(self) -> str:
        now = utc_now()

        async def tx(conn: aiosqlite.Connection) -> str:
            row = await (await conn.execute("select id from workspaces where id = ?", (DEFAULT_WORKSPACE_ID,))).fetchone()
            if row:
                return DEFAULT_WORKSPACE_ID
            await conn.execute(
                "insert into workspaces(id, name, created_at, updated_at, settings_json) values(?, ?, ?, ?, ?)",
                (DEFAULT_WORKSPACE_ID, "Personal Memory", now, now, "{}"),
            )
            await conn.execute(
                "insert into events(id, workspace_id, event_type, aggregate_type, aggregate_id, payload_json, created_at) values(?, ?, ?, ?, ?, ?, ?)",
                (new_id("evt"), DEFAULT_WORKSPACE_ID, "workspace_created", "workspace", DEFAULT_WORKSPACE_ID, dumps({"name": "Personal Memory"}), now),
            )
            return DEFAULT_WORKSPACE_ID

        return await self.db.transaction(tx)

    async def create_session(self, workspace_id: str, title: str = "New Thought", mode: str = "discuss", metadata: dict[str, Any] | None = None) -> SessionOut:
        now = utc_now()
        session_id = new_id("ses")
        metadata = metadata or {}
        response_budget = {"min_words": 120, "max_words": 250}

        async def tx(conn: aiosqlite.Connection) -> SessionOut:
            await conn.execute(
                """
                insert into sessions(id, workspace_id, title, status, mode, response_budget_json, created_at, updated_at, metadata_json)
                values(?, ?, ?, 'active', ?, ?, ?, ?, ?)
                """,
                (session_id, workspace_id, title, mode, dumps(response_budget), now, now, dumps(metadata)),
            )
            await fts.index_session(conn, session_id, title, None)
            await self._insert_event_conn(conn, workspace_id, session_id, "session_created", "session", session_id, {"title": title})
            row = await self._get_session_row_conn(conn, session_id)
            return self._session_from_row(row)

        return await self.db.transaction(tx)

    async def list_sessions(self, workspace_id: str, include_archived: bool = False, limit: int = 50) -> list[SessionOut]:
        where = "workspace_id = ?"
        params: list[Any] = [workspace_id]
        if not include_archived:
            where += " and status != 'archived'"
        rows = await self.db.fetchall(
            f"select * from sessions where {where} order by coalesce(last_turn_at, updated_at) desc limit ?",
            (*params, limit),
        )
        return [self._session_from_row(row) for row in rows]

    async def get_session(self, session_id: str) -> SessionOut | None:
        row = await self.db.fetchone("select * from sessions where id = ?", (session_id,))
        return self._session_from_row(row) if row else None

    async def update_session(self, session_id: str, updates: dict[str, Any]) -> SessionOut | None:
        existing = await self.get_session(session_id)
        if not existing:
            return None
        allowed = {"title", "status", "mode", "user_summary", "system_summary", "metadata_json", "active_map_ids_json", "touched_map_ids_json"}
        values: dict[str, Any] = {}
        for key, value in updates.items():
            if key == "metadata":
                values["metadata_json"] = dumps(value)
            elif key == "active_map_ids":
                values["active_map_ids_json"] = dumps(value)
            elif key == "touched_map_ids":
                values["touched_map_ids_json"] = dumps(value)
            elif key in allowed and value is not None:
                values[key] = value
        values["updated_at"] = utc_now()
        set_clause = ", ".join(f"{key} = ?" for key in values)
        params = [*values.values(), session_id]

        async def tx(conn: aiosqlite.Connection) -> SessionOut:
            await conn.execute(f"update sessions set {set_clause} where id = ?", tuple(params))
            row = await self._get_session_row_conn(conn, session_id)
            await fts.index_session(conn, session_id, row["title"], row["system_summary"] or row["user_summary"])
            return self._session_from_row(row)

        return await self.db.transaction(tx)

    async def fork_session(self, session_id: str) -> SessionOut | None:
        existing = await self.get_session(session_id)
        if not existing:
            return None
        return await self.create_session(
            existing.workspace_id,
            f"{existing.title} fork",
            existing.mode,
            {"forked_from_session_id": existing.id},
        )

    async def create_turn(
        self,
        session_id: str,
        role: str,
        content: str,
        original_content: str | None,
        token_estimate: int,
        metadata: dict[str, Any] | None = None,
    ) -> TurnOut:
        now = utc_now()
        turn_id = new_id("turn")
        metadata = metadata or {}

        async def tx(conn: aiosqlite.Connection) -> TurnOut:
            await conn.execute(
                """
                insert into turns(id, session_id, role, content, original_content, created_at, token_estimate, metadata_json)
                values(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (turn_id, session_id, role, content, original_content, now, token_estimate, dumps(metadata)),
            )
            await fts.index_turn(conn, turn_id, session_id, content)
            await conn.execute("update sessions set updated_at = ?, last_turn_at = ? where id = ?", (now, now, session_id))
            row = await (await conn.execute("select workspace_id from sessions where id = ?", (session_id,))).fetchone()
            if row:
                await self._insert_event_conn(conn, row["workspace_id"], session_id, "turn_created", "turn", turn_id, {"role": role})
            return TurnOut(id=turn_id, session_id=session_id, role=role, content=content, original_content=original_content, created_at=now, token_estimate=token_estimate, metadata=metadata)

        return await self.db.transaction(tx)

    async def list_turns(self, session_id: str, limit: int = 200) -> list[TurnOut]:
        rows = await self.db.fetchall(
            "select * from turns where session_id = ? order by created_at asc limit ?",
            (session_id, limit),
        )
        return [self._turn_from_row(row) for row in rows]

    async def get_turn(self, turn_id: str) -> TurnOut | None:
        row = await self.db.fetchone("select * from turns where id = ?", (turn_id,))
        return self._turn_from_row(row) if row else None

    async def create_artifact(
        self,
        workspace_id: str,
        session_id: str | None,
        turn_id: str | None,
        artifact_type: str,
        title: str,
        content: dict[str, Any],
        status: str = "succeeded",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = utc_now()
        artifact_id = new_id("art")
        metadata = metadata or {}

        async def tx(conn: aiosqlite.Connection) -> dict[str, Any]:
            await conn.execute(
                """
                insert into artifacts(id, workspace_id, session_id, turn_id, artifact_type, title, content_json, status, created_at, metadata_json)
                values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (artifact_id, workspace_id, session_id, turn_id, artifact_type, title, dumps(content), status, now, dumps(metadata)),
            )
            await self._insert_event_conn(conn, workspace_id, session_id, "artifact_created", "artifact", artifact_id, {"artifact_type": artifact_type})
            return {"id": artifact_id, "workspace_id": workspace_id, "session_id": session_id, "turn_id": turn_id, "artifact_type": artifact_type, "title": title, "content": content, "status": status, "created_at": now, "metadata": metadata}

        return await self.db.transaction(tx)

    async def list_artifacts_for_turn(self, turn_id: str) -> list[dict[str, Any]]:
        rows = await self.db.fetchall("select * from artifacts where turn_id = ? order by created_at desc", (turn_id,))
        return [self._artifact_from_row(row) for row in rows]

    async def get_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        row = await self.db.fetchone("select * from artifacts where id = ?", (artifact_id,))
        return self._artifact_from_row(row) if row else None

    async def find_map_by_title(self, workspace_id: str, title: str) -> TopicMapOut | None:
        row = await self.db.fetchone("select * from topic_maps where workspace_id = ? and lower(title) = lower(?)", (workspace_id, title))
        return self._map_from_row(row) if row else None

    async def create_map(self, workspace_id: str, title: str, summary: str | None = None, domain_id: str | None = None, parent_map_id: str | None = None) -> TopicMapOut:
        existing = await self.find_map_by_title(workspace_id, title)
        if existing:
            return existing
        now = utc_now()
        map_id = new_id("map")

        async def tx(conn: aiosqlite.Connection) -> TopicMapOut:
            await conn.execute(
                """
                insert into topic_maps(id, workspace_id, domain_id, parent_map_id, title, summary, status, created_at, updated_at, salience, metadata_json)
                values(?, ?, ?, ?, ?, ?, 'active', ?, ?, 0.5, '{}')
                """,
                (map_id, workspace_id, domain_id, parent_map_id, title, summary, now, now),
            )
            await self._insert_event_conn(conn, workspace_id, None, "map_created", "topic_map", map_id, {"title": title})
            row = await (await conn.execute("select * from topic_maps where id = ?", (map_id,))).fetchone()
            return self._map_from_row(dict(row))

        return await self.db.transaction(tx)

    async def list_maps(self, workspace_id: str) -> list[TopicMapOut]:
        rows = await self.db.fetchall("select * from topic_maps where workspace_id = ? order by updated_at desc", (workspace_id,))
        return [self._map_from_row(row) for row in rows]

    async def get_map(self, map_id: str) -> TopicMapOut | None:
        row = await self.db.fetchone("select * from topic_maps where id = ?", (map_id,))
        return self._map_from_row(row) if row else None

    async def upsert_node(self, conn: aiosqlite.Connection, workspace_id: str, map_id: str, node: dict[str, Any], provenance: list[dict[str, Any]]) -> str:
        now = utc_now()
        row = await (await conn.execute("select * from concept_nodes where map_id = ? and lower(label) = lower(?)", (map_id, node["label"]))).fetchone()
        if row:
            node_id = row["id"]
            await conn.execute(
                """
                update concept_nodes
                set recurrence_count = recurrence_count + 1,
                    local_salience = max(local_salience, ?),
                    global_salience = max(global_salience, ?),
                    novelty_score = max(novelty_score, ?),
                    bridge_potential = max(bridge_potential, ?),
                    updated_at = ?
                where id = ?
                """,
                (
                    node.get("local_salience", 0.4),
                    node.get("global_salience", 0.2),
                    node.get("novelty_score", 0.2),
                    node.get("bridge_potential", 0.2),
                    now,
                    node_id,
                ),
            )
            return node_id
        node_id = new_id("node")
        await conn.execute(
            """
            insert into concept_nodes(
              id, workspace_id, map_id, label, description, node_type, epistemic_status, confidence,
              local_salience, global_salience, novelty_score, bridge_potential, recurrence_count,
              created_at, updated_at, provenance_json, metadata_json
            ) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
            """,
            (
                node_id,
                workspace_id,
                map_id,
                node["label"],
                node.get("description"),
                node.get("node_type", "concept"),
                node.get("epistemic_status", "user_asserted"),
                node.get("confidence", 0.5),
                node.get("local_salience", 0.4),
                node.get("global_salience", 0.2),
                node.get("novelty_score", 0.2),
                node.get("bridge_potential", 0.2),
                now,
                now,
                dumps(provenance),
                dumps(node.get("metadata", {})),
            ),
        )
        await fts.index_node(conn, node_id, map_id, node["label"], node.get("description"))
        return node_id

    async def insert_map_patch(self, workspace_id: str, session_id: str | None, turn_id: str | None, patch: dict[str, Any], status: str, risk_level: str) -> MapPatchOut:
        now = utc_now()
        patch_id = new_id("patch")
        target_ids = patch.get("target_map_ids", [])

        async def tx(conn: aiosqlite.Connection) -> MapPatchOut:
            await conn.execute(
                """
                insert into map_patches(id, workspace_id, session_id, turn_id, target_map_ids_json, patch_json, status, risk_level, created_at, applied_at, metadata_json)
                values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}')
                """,
                (patch_id, workspace_id, session_id, turn_id, dumps(target_ids), dumps(patch), status, risk_level, now, now if status == "applied" else None),
            )
            await self._insert_event_conn(conn, workspace_id, session_id, "map_patch_created", "map_patch", patch_id, {"status": status, "risk_level": risk_level})
            row = await (await conn.execute("select * from map_patches where id = ?", (patch_id,))).fetchone()
            return self._patch_from_row(dict(row))

        return await self.db.transaction(tx)

    async def update_patch_status(self, patch_id: str, status: str) -> MapPatchOut | None:
        now = utc_now()
        field = "applied_at" if status == "applied" else "rejected_at" if status == "rejected" else None
        set_clause = "status = ?"
        params: list[Any] = [status]
        if field:
            set_clause += f", {field} = ?"
            params.append(now)
        params.append(patch_id)
        await self.db.execute(f"update map_patches set {set_clause} where id = ?", tuple(params))
        row = await self.db.fetchone("select * from map_patches where id = ?", (patch_id,))
        return self._patch_from_row(row) if row else None

    async def list_patches(self, workspace_id: str, status: str | None = None, limit: int = 25) -> list[MapPatchOut]:
        if status:
            rows = await self.db.fetchall(
                "select * from map_patches where workspace_id = ? and status = ? order by created_at desc limit ?",
                (workspace_id, status, limit),
            )
        else:
            rows = await self.db.fetchall(
                "select * from map_patches where workspace_id = ? order by created_at desc limit ?",
                (workspace_id, limit),
            )
        return [self._patch_from_row(row) for row in rows]

    async def apply_patch_to_map(self, workspace_id: str, session_id: str | None, turn_id: str | None, patch: dict[str, Any]) -> tuple[list[str], dict[str, int]]:
        provenance = patch.get("provenance", [])
        counters = {"maps": 0, "nodes": 0, "edges": 0, "claims": 0, "questions": 0, "analogies": 0, "latent_bridges": 0}

        async def tx(conn: aiosqlite.Connection) -> tuple[list[str], dict[str, int]]:
            target_map_ids = list(patch.get("target_map_ids", []))
            for map_payload in patch.get("create_maps", []):
                existing = await (await conn.execute("select id from topic_maps where workspace_id = ? and lower(title) = lower(?)", (workspace_id, map_payload["title"]))).fetchone()
                if existing:
                    map_id = existing["id"]
                else:
                    map_id = new_id("map")
                    now = utc_now()
                    await conn.execute(
                        """
                        insert into topic_maps(id, workspace_id, domain_id, parent_map_id, title, summary, status, created_at, updated_at, salience, metadata_json)
                        values(?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?)
                        """,
                        (
                            map_id,
                            workspace_id,
                            map_payload.get("domain_id"),
                            map_payload.get("parent_map_id"),
                            map_payload["title"],
                            map_payload.get("summary"),
                            now,
                            now,
                            map_payload.get("salience", 0.5),
                            dumps(map_payload.get("metadata", {})),
                        ),
                    )
                    counters["maps"] += 1
                if map_id not in target_map_ids:
                    target_map_ids.append(map_id)

            if not target_map_ids:
                uncategorized = await (await conn.execute("select id from topic_maps where workspace_id = ? and title = 'Unsorted Thoughts'", (workspace_id,))).fetchone()
                if uncategorized:
                    target_map_ids.append(uncategorized["id"])
                else:
                    map_id = new_id("map")
                    now = utc_now()
                    await conn.execute(
                        """
                        insert into topic_maps(id, workspace_id, title, summary, status, created_at, updated_at, salience, metadata_json)
                        values(?, ?, 'Unsorted Thoughts', 'Captured ideas waiting for a better map.', 'active', ?, ?, 0.2, '{}')
                        """,
                        (map_id, workspace_id, now, now),
                    )
                    target_map_ids.append(map_id)
                    counters["maps"] += 1

            primary_map_id = target_map_ids[0]
            label_to_id: dict[str, str] = {}
            for node in patch.get("add_nodes", []):
                node_id = await self.upsert_node(conn, workspace_id, primary_map_id, node, provenance)
                label_to_id[node["label"].lower()] = node_id
                counters["nodes"] += 1

            for edge in patch.get("add_edges", []):
                from_id = label_to_id.get(edge["from_label"].lower())
                to_id = label_to_id.get(edge["to_label"].lower())
                if not from_id:
                    from_id = await self.upsert_node(conn, workspace_id, primary_map_id, {"label": edge["from_label"], "node_type": "concept", "epistemic_status": "unverified", "confidence": 0.4}, provenance)
                if not to_id:
                    to_id = await self.upsert_node(conn, workspace_id, primary_map_id, {"label": edge["to_label"], "node_type": "concept", "epistemic_status": "unverified", "confidence": 0.4}, provenance)
                existing = await (
                    await conn.execute(
                        "select id from relation_edges where map_id = ? and from_node_id = ? and to_node_id = ? and relation_type = ?",
                        (primary_map_id, from_id, to_id, edge["relation_type"]),
                    )
                ).fetchone()
                if existing:
                    continue
                now = utc_now()
                await conn.execute(
                    """
                    insert into relation_edges(id, workspace_id, map_id, from_node_id, to_node_id, relation_type, label, description, epistemic_status, confidence, salience, created_at, updated_at, provenance_json, metadata_json)
                    values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}')
                    """,
                    (
                        new_id("edge"),
                        workspace_id,
                        primary_map_id,
                        from_id,
                        to_id,
                        edge["relation_type"],
                        edge.get("label"),
                        edge.get("description"),
                        edge.get("epistemic_status", "speculative"),
                        edge.get("confidence", 0.5),
                        edge.get("salience", 0.4),
                        now,
                        now,
                        dumps(provenance),
                    ),
                )
                counters["edges"] += 1

            for claim in patch.get("add_claims", []):
                now = utc_now()
                claim_id = new_id("claim")
                await conn.execute(
                    """
                    insert into claims(id, workspace_id, session_id, map_id, text, claim_type, epistemic_status, confidence, created_at, updated_at, provenance_json, source_ids_json, metadata_json)
                    values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}')
                    """,
                    (
                        claim_id,
                        workspace_id,
                        session_id,
                        primary_map_id,
                        claim["text"],
                        claim.get("claim_type", "observation"),
                        claim.get("epistemic_status", "user_asserted"),
                        claim.get("confidence", 0.5),
                        now,
                        now,
                        dumps(provenance),
                        dumps(claim.get("source_ids", [])),
                    ),
                )
                await fts.index_claim(conn, claim_id, session_id, claim["text"])
                counters["claims"] += 1

            for question in patch.get("add_questions", []):
                now = utc_now()
                await conn.execute(
                    """
                    insert into open_questions(id, workspace_id, session_id, map_id, question, status, priority, created_at, updated_at, provenance_json, metadata_json)
                    values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}')
                    """,
                    (
                        new_id("q"),
                        workspace_id,
                        session_id,
                        primary_map_id,
                        question["question"],
                        question.get("status", "open"),
                        question.get("priority", 0.3),
                        now,
                        now,
                        dumps(provenance),
                    ),
                )
                counters["questions"] += 1

            for analogy in patch.get("add_analogies", []):
                await conn.execute(
                    """
                    insert into analogies(id, workspace_id, map_id, source_concept, target_concept, useful_because, breaks_at, status, confidence, created_at, provenance_json)
                    values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        new_id("ana"),
                        workspace_id,
                        primary_map_id,
                        analogy["source_concept"],
                        analogy["target_concept"],
                        analogy.get("useful_because"),
                        analogy.get("breaks_at"),
                        analogy.get("status", "suggested"),
                        analogy.get("confidence", 0.5),
                        utc_now(),
                        dumps(provenance),
                    ),
                )
                counters["analogies"] += 1

            for bridge in patch.get("add_latent_bridges", []):
                from_id = label_to_id.get(bridge["from_label"].lower())
                to_id = label_to_id.get(bridge["to_label"].lower())
                if from_id and to_id and from_id != to_id:
                    now = utc_now()
                    await conn.execute(
                        """
                        insert into latent_bridges(id, workspace_id, from_node_id, to_node_id, bridge_type, reason, confidence, status, discovered_by, created_at, updated_at, evidence_artifact_ids_json, metadata_json)
                        values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}')
                        """,
                        (
                            new_id("bridge"),
                            workspace_id,
                            from_id,
                            to_id,
                            bridge.get("bridge_type", "bridges_to"),
                            bridge["reason"],
                            bridge.get("confidence", 0.45),
                            bridge.get("status", "suggested"),
                            bridge.get("discovered_by", "deterministic"),
                            now,
                            now,
                            dumps(bridge.get("evidence_artifact_ids", [])),
                        ),
                    )
                    counters["latent_bridges"] += 1

            now = utc_now()
            await conn.execute(
                "update topic_maps set updated_at = ?, salience = salience + 0.05 where id in (%s)" % ",".join("?" for _ in target_map_ids),
                (now, *target_map_ids),
            )
            if session_id:
                row = await (await conn.execute("select active_map_ids_json, touched_map_ids_json from sessions where id = ?", (session_id,))).fetchone()
                if row:
                    active = list(dict.fromkeys([*loads(row["active_map_ids_json"], []), *target_map_ids]))
                    touched = list(dict.fromkeys([*loads(row["touched_map_ids_json"], []), *target_map_ids]))
                    await conn.execute(
                        "update sessions set active_map_ids_json = ?, touched_map_ids_json = ?, updated_at = ? where id = ?",
                        (dumps(active), dumps(touched), now, session_id),
                    )
            await self._insert_event_conn(conn, workspace_id, session_id, "map_patch_applied", "topic_map", primary_map_id, {"counters": counters, "target_map_ids": target_map_ids}, causation_id=turn_id)
            return target_map_ids, counters

        return await self.db.transaction(tx)

    async def atlas_tree(self, workspace_id: str) -> AtlasTree:
        domains = await self.db.fetchall("select * from domains where workspace_id = ? and status != 'archived' order by name", (workspace_id,))
        maps = await self.db.fetchall(
            """
            select m.*,
              (select count(*) from concept_nodes n where n.map_id = m.id) as node_count,
              (select count(*) from open_questions q where q.map_id = m.id and q.status != 'closed') as question_count
            from topic_maps m
            where m.workspace_id = ? and m.status != 'archived'
            order by m.salience desc, m.updated_at desc
            """,
            (workspace_id,),
        )
        by_parent: dict[str | None, list[dict[str, Any]]] = {}
        by_domain: dict[str | None, list[dict[str, Any]]] = {}
        for row in maps:
            by_parent.setdefault(row.get("parent_map_id"), []).append(row)
            by_domain.setdefault(row.get("domain_id"), []).append(row)

        def build_map(row: dict[str, Any]) -> AtlasTreeMap:
            return AtlasTreeMap(
                id=row["id"],
                title=row["title"],
                summary=row["summary"],
                status=row["status"],
                node_count=row["node_count"],
                question_count=row["question_count"],
                salience=row["salience"],
                children=[build_map(child) for child in by_parent.get(row["id"], [])],
            )

        domain_models = [
            AtlasTreeDomain(
                id=domain["id"],
                name=domain["name"],
                status=domain["status"],
                maps=[build_map(row) for row in by_domain.get(domain["id"], []) if row.get("parent_map_id") is None],
            )
            for domain in domains
        ]
        uncategorized = [build_map(row) for row in by_domain.get(None, []) if row.get("parent_map_id") is None]
        return AtlasTree(workspace_id=workspace_id, domains=domain_models, uncategorized_maps=uncategorized)

    async def map_graph(self, map_id: str) -> MapGraph | None:
        map_out = await self.get_map(map_id)
        if not map_out:
            return None
        node_rows = await self.db.fetchall("select * from concept_nodes where map_id = ? order by local_salience desc, updated_at desc limit 100", (map_id,))
        edge_rows = await self.db.fetchall("select * from relation_edges where map_id = ? order by salience desc, updated_at desc limit 100", (map_id,))
        question_rows = await self.db.fetchall("select * from open_questions where map_id = ? order by priority desc, updated_at desc limit 50", (map_id,))
        bridge_rows = await self.db.fetchall(
            """
            select b.*, nf.label as from_label, nt.label as to_label
            from latent_bridges b
            join concept_nodes nf on nf.id = b.from_node_id
            join concept_nodes nt on nt.id = b.to_node_id
            where nf.map_id = ? or nt.map_id = ?
            order by b.confidence desc, b.updated_at desc
            limit 3
            """,
            (map_id, map_id),
        )
        return MapGraph(
            map=map_out,
            nodes=[self._node_from_row(row) for row in node_rows],
            edges=[self._edge_from_row(row) for row in edge_rows],
            questions=[self._question_from_row(row) for row in question_rows],
            latent_bridges=[{**row, "evidence_artifact_ids": loads(row["evidence_artifact_ids_json"], [])} for row in bridge_rows],
        )

    async def create_source(self, workspace_id: str, source: SourceCardIn) -> SourceCardOut:
        now = utc_now()
        source_id = new_id("src")

        async def tx(conn: aiosqlite.Connection) -> SourceCardOut:
            await conn.execute(
                """
                insert into source_cards(id, workspace_id, title, url, doi, arxiv_id, source_type, year, authors_json, venue, abstract, key_claims_json, limitations_json, relevance_score, credibility_score, freshness_score, created_at, updated_at, metadata_json)
                values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_id,
                    workspace_id,
                    source.title,
                    source.url,
                    source.doi,
                    source.arxiv_id,
                    source.source_type,
                    source.year,
                    dumps(source.authors),
                    source.venue,
                    source.abstract,
                    dumps(source.key_claims),
                    dumps(source.limitations),
                    source.relevance_score,
                    source.credibility_score,
                    source.freshness_score,
                    now,
                    now,
                    dumps(source.metadata),
                ),
            )
            await fts.index_source(conn, source_id, source.title, source.abstract, source.key_claims)
            row = await (await conn.execute("select * from source_cards where id = ?", (source_id,))).fetchone()
            return self._source_from_row(dict(row))

        return await self.db.transaction(tx)

    async def list_sources(self, workspace_id: str, limit: int = 50) -> list[SourceCardOut]:
        rows = await self.db.fetchall("select * from source_cards where workspace_id = ? order by updated_at desc limit ?", (workspace_id, limit))
        return [self._source_from_row(row) for row in rows]

    async def get_source(self, source_id: str) -> SourceCardOut | None:
        row = await self.db.fetchone("select * from source_cards where id = ?", (source_id,))
        return self._source_from_row(row) if row else None

    async def recent_events(self, workspace_id: str, limit: int = 50) -> list[EventOut]:
        rows = await self.db.fetchall("select * from events where workspace_id = ? order by created_at desc limit ?", (workspace_id, limit))
        return [self._event_from_row(row) for row in rows]

    async def search(self, workspace_id: str, query: str, limit: int = 25) -> dict[str, list[dict[str, Any]]]:
        safe_query = query.strip()
        if not safe_query:
            return {"sessions": [], "turns": [], "maps": [], "claims": [], "sources": []}
        like = f"%{safe_query}%"
        sessions = await self.db.fetchall(
            """
            select s.id, s.title, s.updated_at, 'session' as result_type
            from sessions s where s.workspace_id = ? and s.title like ?
            order by s.updated_at desc limit ?
            """,
            (workspace_id, like, limit),
        )
        turns = await self.db.fetchall(
            """
            select t.id, t.session_id, substr(t.content, 1, 240) as snippet, t.created_at, 'turn' as result_type
            from turns t join sessions s on s.id = t.session_id
            where s.workspace_id = ? and t.content like ?
            order by t.created_at desc limit ?
            """,
            (workspace_id, like, limit),
        )
        maps = await self.db.fetchall(
            "select id, title, summary, updated_at, 'map' as result_type from topic_maps where workspace_id = ? and (title like ? or coalesce(summary, '') like ?) order by updated_at desc limit ?",
            (workspace_id, like, like, limit),
        )
        claims = await self.db.fetchall(
            "select id, text, updated_at, 'claim' as result_type from claims where workspace_id = ? and text like ? order by updated_at desc limit ?",
            (workspace_id, like, limit),
        )
        sources = await self.db.fetchall(
            "select id, title, year, source_type, updated_at, 'source' as result_type from source_cards where workspace_id = ? and (title like ? or coalesce(abstract, '') like ?) order by updated_at desc limit ?",
            (workspace_id, like, like, limit),
        )
        return {"sessions": sessions, "turns": turns, "maps": maps, "claims": claims, "sources": sources}

    async def learning_events(self, workspace_id: str) -> list[dict[str, Any]]:
        return await self.db.fetchall("select * from events where workspace_id = ? order by created_at asc", (workspace_id,))

    async def _get_session_row_conn(self, conn: aiosqlite.Connection, session_id: str) -> dict[str, Any]:
        row = await (await conn.execute("select * from sessions where id = ?", (session_id,))).fetchone()
        return dict(row)

    async def _insert_event_conn(
        self,
        conn: aiosqlite.Connection,
        workspace_id: str,
        session_id: str | None,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, Any],
        causation_id: str | None = None,
        correlation_id: str | None = None,
    ) -> None:
        await conn.execute(
            """
            insert into events(id, workspace_id, session_id, event_type, aggregate_type, aggregate_id, payload_json, created_at, causation_id, correlation_id)
            values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (new_id("evt"), workspace_id, session_id, event_type, aggregate_type, aggregate_id, dumps(payload), utc_now(), causation_id, correlation_id),
        )

    def _session_from_row(self, row: dict[str, Any]) -> SessionOut:
        return SessionOut(
            id=row["id"],
            workspace_id=row["workspace_id"],
            title=row["title"],
            status=row["status"],
            mode=row["mode"],
            response_budget=loads(row["response_budget_json"], {}),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_turn_at=row["last_turn_at"],
            user_summary=row["user_summary"],
            system_summary=row["system_summary"],
            active_map_ids=loads(row["active_map_ids_json"], []),
            touched_map_ids=loads(row["touched_map_ids_json"], []),
            metadata=loads(row["metadata_json"], {}),
        )

    def _turn_from_row(self, row: dict[str, Any]) -> TurnOut:
        return TurnOut(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            content=row["content"],
            original_content=row["original_content"],
            created_at=row["created_at"],
            token_estimate=row["token_estimate"],
            metadata=loads(row["metadata_json"], {}),
        )

    def _artifact_from_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "workspace_id": row["workspace_id"],
            "session_id": row["session_id"],
            "turn_id": row["turn_id"],
            "artifact_type": row["artifact_type"],
            "title": row["title"],
            "content": loads(row["content_json"], {}),
            "status": row["status"],
            "created_at": row["created_at"],
            "metadata": loads(row["metadata_json"], {}),
        }

    def _map_from_row(self, row: dict[str, Any]) -> TopicMapOut:
        return TopicMapOut(
            id=row["id"],
            workspace_id=row["workspace_id"],
            domain_id=row["domain_id"],
            parent_map_id=row["parent_map_id"],
            title=row["title"],
            summary=row["summary"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            salience=row["salience"],
            metadata=loads(row["metadata_json"], {}),
        )

    def _node_from_row(self, row: dict[str, Any]) -> ConceptNodeOut:
        return ConceptNodeOut(
            id=row["id"],
            map_id=row["map_id"],
            label=row["label"],
            description=row["description"],
            node_type=row["node_type"],
            epistemic_status=row["epistemic_status"],
            confidence=row["confidence"],
            local_salience=row["local_salience"],
            global_salience=row["global_salience"],
            novelty_score=row["novelty_score"],
            bridge_potential=row["bridge_potential"],
            recurrence_count=row["recurrence_count"],
        )

    def _edge_from_row(self, row: dict[str, Any]) -> RelationEdgeOut:
        return RelationEdgeOut(
            id=row["id"],
            map_id=row["map_id"],
            from_node_id=row["from_node_id"],
            to_node_id=row["to_node_id"],
            relation_type=row["relation_type"],
            label=row["label"],
            description=row["description"],
            epistemic_status=row["epistemic_status"],
            confidence=row["confidence"],
            salience=row["salience"],
        )

    def _question_from_row(self, row: dict[str, Any]) -> OpenQuestionOut:
        return OpenQuestionOut(
            id=row["id"],
            session_id=row["session_id"],
            map_id=row["map_id"],
            question=row["question"],
            status=row["status"],
            priority=row["priority"],
        )

    def _patch_from_row(self, row: dict[str, Any]) -> MapPatchOut:
        return MapPatchOut(
            id=row["id"],
            workspace_id=row["workspace_id"],
            session_id=row["session_id"],
            turn_id=row["turn_id"],
            target_map_ids=loads(row["target_map_ids_json"], []),
            patch=loads(row["patch_json"], {}),
            status=row["status"],
            risk_level=row["risk_level"],
            created_at=row["created_at"],
            applied_at=row["applied_at"],
            rejected_at=row["rejected_at"],
            metadata=loads(row["metadata_json"], {}),
        )

    def _source_from_row(self, row: dict[str, Any]) -> SourceCardOut:
        return SourceCardOut(
            id=row["id"],
            workspace_id=row["workspace_id"],
            title=row["title"],
            url=row["url"],
            doi=row["doi"],
            arxiv_id=row["arxiv_id"],
            source_type=row["source_type"],
            year=row["year"],
            authors=loads(row["authors_json"], []),
            venue=row["venue"],
            abstract=row["abstract"],
            key_claims=loads(row["key_claims_json"], []),
            limitations=loads(row["limitations_json"], []),
            relevance_score=row["relevance_score"],
            credibility_score=row["credibility_score"],
            freshness_score=row["freshness_score"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            metadata=loads(row["metadata_json"], {}),
        )

    def _event_from_row(self, row: dict[str, Any]) -> EventOut:
        return EventOut(
            id=row["id"],
            workspace_id=row["workspace_id"],
            session_id=row["session_id"],
            event_type=row["event_type"],
            aggregate_type=row["aggregate_type"],
            aggregate_id=row["aggregate_id"],
            payload=loads(row["payload_json"], {}),
            created_at=row["created_at"],
            causation_id=row["causation_id"],
            correlation_id=row["correlation_id"],
        )
