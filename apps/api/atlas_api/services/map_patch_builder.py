from __future__ import annotations

from atlas_api.db.repositories import Repository
from atlas_api.models.patches import MapPatch, PostTurnExtraction, Provenance


BOILERPLATE_TITLES = {
    "extract exchange only",
    "current user message",
    "post turn extraction",
    "discussion reply",
    "recent dialogue",
    "user assistant",
}

OPERATIONAL_MAP_TITLES = {
    "web browsing/search capability",
    "web browsing capability",
    "search capability",
    "internet access",
    "codex cli capability",
    "read-only environment",
    "app capabilities",
    "application capabilities",
}

OPERATIONAL_PHRASES = {
    "web browsing",
    "search capability",
    "internet access",
    "access my website",
    "access my site",
    "codex cli",
    "read-only environment",
    "port 8787",
    "port 8788",
    "phone url",
    "service worker",
    "pwa",
    "playwright",
    "screenshot",
    "latest built bundle",
}


class MapPatchBuilder:
    def __init__(self, repo: Repository):
        self.repo = repo

    async def build(self, workspace_id: str, session_id: str, turn_id: str, extraction: PostTurnExtraction) -> MapPatch:
        if not extraction.topics and not extraction.node_candidates and not extraction.open_questions:
            return MapPatch(action="no_op", provenance=[Provenance(turn_id=turn_id, session_id=session_id, speaker="system", note="No extraction candidates.")])
        title = self._map_title(extraction)
        if not title or title.lower() in BOILERPLATE_TITLES:
            return MapPatch(action="no_op", provenance=[Provenance(turn_id=turn_id, session_id=session_id, speaker="system", note="Extraction only produced boilerplate map title.")])
        if title.lower() in OPERATIONAL_MAP_TITLES or self._operational_only_extraction(extraction):
            return MapPatch(action="no_op", provenance=[Provenance(turn_id=turn_id, session_id=session_id, speaker="system", note="Operational app/support extraction excluded from learning topology.")])
        if self._weak_generic_extraction(extraction, title):
            return MapPatch(action="no_op", provenance=[Provenance(turn_id=turn_id, session_id=session_id, speaker="system", note="Extraction was too weak and generic to apply.")])
        existing = await self.repo.find_map_by_title(workspace_id, title)
        target_map_ids = [existing.id] if existing else []
        create_maps = [] if existing else [{"title": title, "summary": self._map_summary(title, extraction), "salience": 0.5}]
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
        topics = [topic.strip() for topic in extraction.topics if topic.strip() and topic.strip().lower() not in BOILERPLATE_TITLES]
        lowered_topics = [topic.lower() for topic in topics]
        labels = [node.label for node in extraction.node_candidates]
        lowered_labels = [label.lower() for label in labels]
        if "substratecad" in lowered_labels or any("substratecad" in topic or "substrate cad" in topic for topic in lowered_topics):
            return "substrateCAD"
        if any("physical signal integrity" in value for value in [*lowered_topics, *lowered_labels]):
            return "Physical Signal Integrity"
        if any(value in lowered_labels for value in ["pcb trace impedance", "package substrate interconnect", "soc interconnects"]):
            return "Physical Signal Integrity"
        if any("analog" in topic or "compute-in-memory" in topic or "compute in memory" in topic for topic in lowered_topics):
            return "Analog Compute"
        project_goals = [node.label for node in extraction.node_candidates if node.node_type == "project_goal"]
        if project_goals:
            return project_goals[0]
        if topics:
            return self._clean_title(topics[0])
        if extraction.node_candidates:
            return self._clean_title(extraction.node_candidates[0].label)
        return "Unsorted Thoughts"

    def _map_summary(self, title: str, extraction: PostTurnExtraction) -> str:
        project_nodes = [node for node in extraction.node_candidates if node.node_type == "project_goal"]
        if project_nodes:
            return project_nodes[0].description or f"Project learning path for {title}."
        if title == "Physical Signal Integrity":
            return "Cross-session topology for geometry, materials, interconnects, and physical signal behavior."
        if title == "Analog Compute":
            return "Conversation-derived topology for analog compute, compute-in-memory, data movement, and conversion overhead constraints."
        return f"Conversation-derived topology around {title}."

    def _clean_title(self, value: str) -> str:
        value = value.strip()
        if not value:
            return ""
        if value.lower() == "substratecad":
            return "substrateCAD"
        if value.isupper():
            return value
        return value[:1].upper() + value[1:]

    def _weak_generic_extraction(self, extraction: PostTurnExtraction, title: str) -> bool:
        if title.lower() in {"unsorted thoughts", "user", "assistant"}:
            return True
        if len(extraction.node_candidates) == 1 and not extraction.edge_candidates and not extraction.latent_bridges:
            node = extraction.node_candidates[0]
            return node.confidence <= 0.45 and node.node_type == "concept"
        return False

    def _operational_only_extraction(self, extraction: PostTurnExtraction) -> bool:
        values = [
            *extraction.topics,
            *[node.label for node in extraction.node_candidates],
            *[node.description or "" for node in extraction.node_candidates],
            *[claim.text for claim in extraction.claims],
            *[question.question for question in extraction.open_questions],
        ]
        text = "\n".join(values).lower()
        if not text.strip():
            return False
        return any(phrase in text for phrase in OPERATIONAL_PHRASES)
