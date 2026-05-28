from __future__ import annotations

from atlas_api.llm.base import LlmAdapter
from atlas_api.models.llm import LlmJsonRequest
from atlas_api.util.text import keywords_title


class TopicRouter:
    def __init__(self, llm: LlmAdapter):
        self.llm = llm

    async def route(self, text: str, existing_map_titles: list[str]) -> dict:
        result = await self.llm.complete_json(
            LlmJsonRequest(
                task="topic_route",
                prompt=f"Existing maps: {existing_map_titles}\nCurrent turn: {text}",
                schema_name="topic_route",
            )
        )
        if result.data:
            return result.data
        topic = keywords_title(text)
        return {
            "segments": [{"text": text, "candidate_topic": topic, "confidence": 0.5}],
            "candidate_new_maps": [{"title": topic, "reason": "Deterministic fallback", "confidence": 0.5}],
            "matched_map_ids": [],
            "notes": "Fallback route.",
        }

