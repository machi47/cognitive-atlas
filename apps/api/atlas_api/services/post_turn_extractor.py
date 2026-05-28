from __future__ import annotations

from atlas_api.llm.base import LlmAdapter
from atlas_api.models.llm import LlmJsonRequest
from atlas_api.models.patches import PostTurnExtraction


class PostTurnExtractor:
    def __init__(self, llm: LlmAdapter):
        self.llm = llm

    async def extract(self, extraction_context: str) -> PostTurnExtraction:
        result = await self.llm.complete_json(
            LlmJsonRequest(task="post_turn_extraction", prompt=extraction_context, schema_name="post_turn_extraction")
        )
        try:
            return PostTurnExtraction.model_validate(result.data)
        except Exception:
            return PostTurnExtraction(notes="Extraction provider returned malformed output.")

