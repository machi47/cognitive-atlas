from __future__ import annotations

from atlas_api.llm.base import LlmAdapter
from atlas_api.models.llm import DiscussionReply, LlmJsonRequest


class ConversationalAgent:
    def __init__(self, llm: LlmAdapter):
        self.llm = llm

    async def reply(self, context: str, mode: str) -> DiscussionReply:
        result = await self.llm.complete_json(
            LlmJsonRequest(task="discussion_reply", prompt=context, schema_name="discussion_reply", metadata={"mode": mode})
        )
        try:
            return DiscussionReply.model_validate(result.data)
        except Exception:
            text = result.data.get("message") if isinstance(result.data, dict) else None
            return DiscussionReply(
                message=text or "I can work with that. The useful next move is to keep the thought intact, then isolate the core claim and the uncertainty without forcing a full outline yet.",
                response_mode=mode,
                uncertainty_notes=["Provider returned malformed structured output."],
            )

