from __future__ import annotations

from atlas_api.llm.base import LlmAdapter
from atlas_api.models.llm import LlmJsonRequest


class ResearchNeedDetector:
    def __init__(self, llm: LlmAdapter):
        self.llm = llm

    async def detect(self, text: str, topics: list[str]) -> dict:
        result = await self.llm.complete_json(
            LlmJsonRequest(task="research_need", prompt=f"Topics: {topics}\nTurn: {text}", schema_name="research_need")
        )
        data = result.data or {}
        data.setdefault("needs_research", False)
        data.setdefault("freshness_required", False)
        data.setdefault("reasons", [])
        data.setdefault("query_intents", topics)
        data.setdefault("source_types", [])
        data.setdefault("priority", 0)
        return data

