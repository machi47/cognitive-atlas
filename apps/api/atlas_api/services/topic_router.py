from __future__ import annotations

from atlas_api.llm.base import LlmAdapter
from atlas_api.util.text import keywords_title


class TopicRouter:
    def __init__(self, llm: LlmAdapter):
        self.llm = llm

    async def route(self, text: str, existing_map_titles: list[str]) -> dict:
        topic = keywords_title(text)
        matched = [title for title in existing_map_titles if title.lower() == topic.lower()]
        return {
            "segments": [{"text": text[:1000], "candidate_topic": topic, "confidence": 0.62}],
            "candidate_new_maps": [] if matched else [{"title": topic, "reason": "Deterministic route from current turn.", "confidence": 0.62}],
            "matched_map_ids": matched,
            "notes": "Deterministic v0 route; discussion model receives only bounded chat context.",
        }
