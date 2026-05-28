from __future__ import annotations

from atlas_api.llm.base import LlmAdapter
from atlas_api.llm.schemas import load_schema
from atlas_api.errors import LlmMalformedOutputError
from atlas_api.models.llm import DiscussionReply, LlmJsonRequest


class ConversationalAgent:
    def __init__(self, llm: LlmAdapter):
        self.llm = llm

    async def reply(self, context: str, mode: str) -> DiscussionReply:
        result = await self.llm.complete_json(
            LlmJsonRequest(task="discussion_reply", prompt=context, schema_name="discussion_reply", metadata={"mode": mode}),
            schema=load_schema("discussion_reply"),
        )
        try:
            return DiscussionReply.model_validate(result.data)
        except Exception:
            raise LlmMalformedOutputError(
                "Discussion model returned malformed output",
                {"provider": self.llm.provider_name, "task": "discussion_reply", "data": result.data},
            )
