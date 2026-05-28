from __future__ import annotations

from atlas_api.db.repositories import Repository
from atlas_api.models.patches import MapPatch, PostTurnExtraction, Provenance


class MapPatchBuilder:
    def __init__(self, repo: Repository):
        self.repo = repo

    async def build(self, workspace_id: str, session_id: str, turn_id: str, extraction: PostTurnExtraction) -> MapPatch:
        if not extraction.topics and not extraction.node_candidates and not extraction.open_questions:
            return MapPatch(action="no_op", provenance=[Provenance(turn_id=turn_id, session_id=session_id, speaker="system", note="No extraction candidates.")])
        title = self._map_title(extraction)
        existing = await self.repo.find_map_by_title(workspace_id, title)
        target_map_ids = [existing.id] if existing else []
        create_maps = [] if existing else [{"title": title, "summary": f"Map grown from conversation around {title}.", "salience": 0.5}]
        action = "update_existing" if existing else "create_new"
        return MapPatch(
            action=action,
            target_map_ids=target_map_ids,
            create_maps=create_maps,
            add_nodes=extraction.node_candidates,
            add_edges=extraction.edge_candidates,
            add_claims=extraction.claims,
            add_questions=extraction.open_questions,
            add_tensions=extraction.tensions,
            add_analogies=extraction.analogies,
            add_latent_bridges=extraction.latent_bridges,
            provenance=[Provenance(turn_id=turn_id, session_id=session_id, speaker="user", note="Post-turn extraction from current exchange.")],
            confidence=0.65 if extraction.node_candidates else 0.4,
            risk_level="low" if len(extraction.edge_candidates) <= 8 else "medium",
        )

    def _map_title(self, extraction: PostTurnExtraction) -> str:
        topics = [topic.lower() for topic in extraction.topics]
        if any("analog" in topic or "compute-in-memory" in topic or "compute in memory" in topic for topic in topics):
            return "Analog Compute"
        if any("agent" in topic or "conversation" in topic or "map forest" in topic for topic in topics):
            return "Learning Agent Architecture"
        if extraction.topics:
            return extraction.topics[0].title()
        if extraction.node_candidates:
            return extraction.node_candidates[0].label.title()
        return "Unsorted Thoughts"

