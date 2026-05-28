from __future__ import annotations

from atlas_api.llm.base import LlmAdapter
class ResearchNeedDetector:
    def __init__(self, llm: LlmAdapter):
        self.llm = llm

    async def detect(self, text: str, topics: list[str]) -> dict:
        lower = text.lower()
        explicit = any(term in lower for term in ["source", "sources", "research", "latest", "current", "recent", "paper", "citation", "cite"])
        frontier = any(
            term in lower
            for term in [
                "analog compute",
                "compute-in-memory",
                "chiplet",
                "hbm",
                "advanced packaging",
                "sram-cim",
                "rram",
                "photonic",
                "substratecad",
            ]
        )
        needs = explicit and frontier
        return {
            "needs_research": needs,
            "freshness_required": explicit and ("latest" in lower or "current" in lower or "recent" in lower),
            "reasons": ["Explicit source/research request on a frontier technical topic."] if needs else [],
            "query_intents": topics,
            "source_types": ["openalex", "crossref", "arxiv"] if needs else [],
            "priority": 0.75 if needs else 0,
        }
