from __future__ import annotations

from typing import Any

from atlas_api.db.repositories import Repository
from atlas_api.util.json import loads


class LearningProjectionService:
    def __init__(self, repo: Repository):
        self.repo = repo

    async def overview(self, workspace_id: str) -> dict[str, Any]:
        concepts = await self._concepts(workspace_id, limit=80)
        bridges = await self.bridges(workspace_id)
        questions = await self._open_questions(workspace_id)
        tensions = await self._tensions(workspace_id)
        source_needs = await self.source_needs(workspace_id)
        maps = await self._maps(workspace_id)
        recent_updates = await self.recent_updates(workspace_id)
        frame = self._current_frame(concepts)
        textbook = await TextbookProjectionService(self.repo).textbook(workspace_id)
        return {
            "current_frame": frame,
            "project_goals": [item for item in concepts if item["node_type"] == "project_goal"],
            "topology": {"maps": maps, "concepts": concepts[:40], "bridges": bridges[:8]},
            "concepts": concepts,
            "open_questions": questions,
            "tensions": tensions,
            "bridges": bridges,
            "source_needs": source_needs,
            "recent_updates": recent_updates,
            "textbook": textbook,
            "empty": not bool(concepts or questions or bridges),
        }

    async def topology(self, workspace_id: str) -> dict[str, Any]:
        return {
            "maps": await self._maps(workspace_id),
            "concepts": await self._concepts(workspace_id, limit=200),
            "bridges": await self.bridges(workspace_id, limit=40),
            "questions": await self._open_questions(workspace_id, limit=100),
            "tensions": await self._tensions(workspace_id, limit=100),
        }

    async def bridges(self, workspace_id: str, limit: int = 12) -> list[dict[str, Any]]:
        rows = await self.repo.db.fetchall(
            """
            select b.*, nf.label as from_label, nt.label as to_label,
                   mf.title as from_map_title, mt.title as to_map_title
            from latent_bridges b
            join concept_nodes nf on nf.id = b.from_node_id
            join concept_nodes nt on nt.id = b.to_node_id
            left join topic_maps mf on mf.id = nf.map_id
            left join topic_maps mt on mt.id = nt.map_id
            where b.workspace_id = ?
            order by
              case b.status when 'pinned' then 0 when 'accepted' then 1 when 'suggested' then 2 when 'hidden' then 4 else 3 end,
              b.confidence desc,
              b.updated_at desc
            limit ?
            """,
            (workspace_id, limit),
        )
        return [await self._with_contributors(self.repo._bridge_from_row(row)) for row in rows]

    async def source_needs(self, workspace_id: str, limit: int = 50) -> list[dict[str, Any]]:
        rows = await self.repo.list_research_tasks(workspace_id, limit=limit)
        out = []
        for row in rows:
            item = dict(row)
            item["contributors"] = await self._contributors_from_provenance(row.get("metadata", {}).get("provenance", []), row.get("session_id"))
            out.append(item)
        return out

    async def recent_updates(self, workspace_id: str, limit: int = 20) -> list[dict[str, Any]]:
        events = await self.repo.recent_events(workspace_id, limit=limit)
        return [event.model_dump() for event in events]

    async def retrieval_capsule(self, workspace_id: str, text: str, limit: int = 5) -> str:
        lower = text.lower()
        words = {word for word in lower.replace("/", " ").replace("-", " ").split() if len(word) >= 4}
        if not words:
            return ""
        concepts = await self._concepts(workspace_id, limit=80)
        relevant = []
        for concept in concepts:
            label = concept["label"].lower()
            haystack = f"{label} {concept.get('description') or ''}".lower()
            if label in lower or words.intersection(haystack.replace("/", " ").replace("-", " ").split()):
                relevant.append(concept)
        bridges = await self.bridges(workspace_id, limit=20)
        bridge_hits = []
        for bridge in bridges:
            haystack = f"{bridge.get('from_label')} {bridge.get('to_label')} {bridge.get('reason')}".lower()
            if words.intersection(haystack.replace("/", " ").replace("-", " ").split()):
                bridge_hits.append(bridge)
        lines = []
        for concept in relevant[:limit]:
            lines.append(f"- {concept['label']} ({concept['epistemic_status']}): {concept.get('description') or concept['node_type']}")
        for bridge in bridge_hits[:2]:
            lines.append(f"- Bridge candidate: {bridge.get('from_label')} -> {bridge.get('to_label')}: {bridge.get('reason')}")
        return "\n".join(lines)

    async def _maps(self, workspace_id: str) -> list[dict[str, Any]]:
        rows = await self.repo.db.fetchall(
            """
            select m.*,
              (select count(*) from concept_nodes n where n.map_id = m.id) as concept_count,
              (select count(*) from relation_edges e where e.map_id = m.id) as relation_count,
              (select count(*) from open_questions q where q.map_id = m.id and q.status != 'closed') as question_count
            from topic_maps m
            where m.workspace_id = ? and m.status != 'archived'
            order by m.salience desc, m.updated_at desc
            """,
            (workspace_id,),
        )
        return [
            {
                "id": row["id"],
                "title": row["title"],
                "summary": row["summary"],
                "status": row["status"],
                "salience": row["salience"],
                "concept_count": row["concept_count"],
                "relation_count": row["relation_count"],
                "question_count": row["question_count"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    async def _concepts(self, workspace_id: str, limit: int = 80) -> list[dict[str, Any]]:
        rows = await self.repo.db.fetchall(
            """
            select n.*, m.title as map_title
            from concept_nodes n
            join topic_maps m on m.id = n.map_id
            where n.workspace_id = ?
            order by
              case n.node_type when 'project_goal' then 0 when 'foundation' then 1 when 'constraint' then 2 else 3 end,
              n.global_salience desc,
              n.updated_at desc
            limit ?
            """,
            (workspace_id, limit),
        )
        out = []
        for row in rows:
            provenance = loads(row["provenance_json"], [])
            out.append(
                {
                    "id": row["id"],
                    "map_id": row["map_id"],
                    "map_title": row["map_title"],
                    "label": row["label"],
                    "description": row["description"],
                    "node_type": row["node_type"],
                    "epistemic_status": row["epistemic_status"],
                    "confidence": row["confidence"],
                    "local_salience": row["local_salience"],
                    "global_salience": row["global_salience"],
                    "recurrence_count": row["recurrence_count"],
                    "provenance": provenance,
                    "contributors": await self._contributors_from_provenance(provenance),
                    "updated_at": row["updated_at"],
                }
            )
        return out

    async def _open_questions(self, workspace_id: str, limit: int = 80) -> list[dict[str, Any]]:
        rows = await self.repo.db.fetchall(
            """
            select q.*, m.title as map_title, s.title as session_title
            from open_questions q
            left join topic_maps m on m.id = q.map_id
            left join sessions s on s.id = q.session_id
            where q.workspace_id = ? and q.status != 'closed'
            order by q.priority desc, q.updated_at desc limit ?
            """,
            (workspace_id, limit),
        )
        out = []
        for row in rows:
            provenance = loads(row["provenance_json"], [])
            out.append(
                {
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "session_title": row["session_title"],
                    "map_id": row["map_id"],
                    "map_title": row["map_title"],
                    "question": row["question"],
                    "status": row["status"],
                    "priority": row["priority"],
                    "provenance": provenance,
                    "contributors": await self._contributors_from_provenance(provenance, row["session_id"]),
                    "updated_at": row["updated_at"],
                }
            )
        return out

    async def _tensions(self, workspace_id: str, limit: int = 80) -> list[dict[str, Any]]:
        rows = await self.repo.db.fetchall(
            """
            select t.*, m.title as map_title
            from tensions t
            left join topic_maps m on m.id = t.map_id
            where t.workspace_id = ?
            order by t.updated_at desc limit ?
            """,
            (workspace_id, limit),
        )
        out = []
        for row in rows:
            node_ids = loads(row["node_ids_json"], [])
            node_labels = []
            if node_ids:
                placeholders = ",".join("?" for _ in node_ids)
                node_rows = await self.repo.db.fetchall(f"select label from concept_nodes where id in ({placeholders})", tuple(node_ids))
                node_labels = [node["label"] for node in node_rows]
            provenance = loads(row["provenance_json"], [])
            out.append(
                {
                    "id": row["id"],
                    "map_id": row["map_id"],
                    "map_title": row["map_title"],
                    "title": row["title"],
                    "description": row["description"],
                    "status": row["status"],
                    "node_labels": node_labels,
                    "provenance": provenance,
                    "contributors": await self._contributors_from_provenance(provenance),
                    "updated_at": row["updated_at"],
                }
            )
        return out

    def _current_frame(self, concepts: list[dict[str, Any]]) -> dict[str, Any]:
        labels = {concept["label"].lower(): concept for concept in concepts}
        if "substratecad" in labels:
            stack = [
                "geometry kernel",
                "substrate object model",
                "fabrication/process constraints",
                "electrical/physical constraints",
                "simulation/verification",
                "manufacturability rules",
            ]
            return {
                "project": "Build substrateCAD from first principles as a fabrication-aware CAD system.",
                "foundation_stack": [item for item in stack if item.lower() in labels],
                "status": labels["substratecad"]["epistemic_status"],
            }
        project = next((concept for concept in concepts if concept["node_type"] == "project_goal"), None)
        if project:
            return {"project": project["description"] or project["label"], "foundation_stack": [], "status": project["epistemic_status"]}
        return {"project": None, "foundation_stack": [], "status": "empty"}

    async def _with_contributors(self, item: dict[str, Any]) -> dict[str, Any]:
        item = dict(item)
        item["contributors"] = await self._contributors_from_provenance(item.get("provenance", []))
        return item

    async def _contributors_from_provenance(self, provenance: list[dict[str, Any]], fallback_session_id: str | None = None) -> list[dict[str, Any]]:
        session_ids = {entry.get("session_id") for entry in provenance if isinstance(entry, dict) and entry.get("session_id")}
        if fallback_session_id:
            session_ids.add(fallback_session_id)
        if not session_ids:
            return []
        placeholders = ",".join("?" for _ in session_ids)
        rows = await self.repo.db.fetchall(f"select id, title, status from sessions where id in ({placeholders})", tuple(session_ids))
        title_by_id = {row["id"]: row for row in rows}
        return [
            {"session_id": session_id, "session_title": title_by_id.get(session_id, {}).get("title", "Deleted chat"), "status": title_by_id.get(session_id, {}).get("status")}
            for session_id in sorted(session_ids)
        ]


class TextbookProjectionService:
    def __init__(self, repo: Repository):
        self.repo = repo
        self.learning = LearningProjectionService(repo)

    async def textbook(self, workspace_id: str, map_id: str | None = None) -> dict[str, Any]:
        concepts = await self.learning._concepts(workspace_id, limit=120)
        questions = await self.learning._open_questions(workspace_id, limit=80)
        tensions = await self.learning._tensions(workspace_id, limit=80)
        bridges = await self.learning.bridges(workspace_id, limit=12)
        if map_id:
            concepts = [concept for concept in concepts if concept["map_id"] == map_id]
            questions = [question for question in questions if question["map_id"] == map_id]
            tensions = [tension for tension in tensions if tension["map_id"] == map_id]
        labels = {concept["label"].lower(): concept for concept in concepts}
        sections: list[dict[str, Any]] = []
        if "substratecad" in labels:
            sections.append(
                {
                    "title": "substrateCAD Frame",
                    "body": "Your current frame: build substrateCAD from first principles as a fabrication-aware CAD system.",
                    "bullets": [
                        item
                        for item in [
                            "geometry kernel",
                            "substrate object model",
                            "layers/features/vias/traces/materials",
                            "fabrication/process constraints",
                            "electrical/physical constraints",
                            "simulation/verification",
                            "manufacturability rules",
                        ]
                        if item.lower() in labels
                    ],
                    "provenance": labels["substratecad"].get("contributors", []),
                }
            )
        if "adc/dac overhead" in labels or "analog compute" in labels or "compute-in-memory" in labels:
            sections.append(
                {
                    "title": "Analog/CIM Constraint Frame",
                    "body": "Your current frame: analog compute matters only if system-level conversion/control overhead does not erase local MAC efficiency.",
                    "bullets": [
                        "Current unresolved constraint: ADC/DAC placement and precision requirements may dominate the energy budget.",
                        *[
                            f"Related branch: {label}"
                            for label in ["compute-in-memory", "data movement cost", "conversion/control overhead"]
                            if label in labels
                        ],
                    ],
                    "provenance": labels.get("adc/dac overhead", labels.get("analog compute", {})).get("contributors", []),
                }
            )
        high_signal_bridges = [bridge for bridge in bridges if bridge.get("status") != "hidden"]
        if high_signal_bridges:
            sections.append(
                {
                    "title": "Bridge Candidates",
                    "body": "Cross-session bridges are suggestions, not forced merges.",
                    "bullets": [f"{bridge.get('from_label')} -> {bridge.get('to_label')}: {bridge.get('reason')}" for bridge in high_signal_bridges[:5]],
                    "provenance": high_signal_bridges[0].get("contributors", []),
                }
            )
        if tensions:
            sections.append(
                {
                    "title": "Tensions And Unknowns",
                    "body": "These are conceptual weak points from your conversations.",
                    "bullets": [f"{tension['title']}: {tension['description']}" for tension in tensions[:5]]
                    + [question["question"] for question in questions[:5]],
                    "provenance": tensions[0].get("contributors", []) if tensions else [],
                }
            )
        return {
            "map_id": map_id,
            "sections": sections,
            "empty": not bool(sections),
            "generated_from": ["topic_maps", "concept_nodes", "relation_edges", "claims", "open_questions", "tensions", "latent_bridges", "research_tasks"],
        }
