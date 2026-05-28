from __future__ import annotations

from typing import Any

from atlas_api.config import Settings
from atlas_api.llm.base import LlmAdapter
from atlas_api.models.llm import LlmHealth, LlmJsonRequest, LlmJsonResult, LlmTextRequest, LlmTextResult


class OpenAIResponsesAdapter(LlmAdapter):
    provider_name = "openai"
    supports_web_search = False
    supports_schema_output = True

    def __init__(self, settings: Settings):
        self.settings = settings

    async def healthcheck(self) -> LlmHealth:
        if not self.settings.openai_api_key:
            return LlmHealth(provider_name=self.provider_name, available=False, message="OPENAI_API_KEY is not set; OpenAI adapter disabled")
        return LlmHealth(provider_name=self.provider_name, available=False, message="OpenAI Responses adapter placeholder is present but disabled in v0")

    async def complete_text(self, request: LlmTextRequest) -> LlmTextResult:
        return LlmTextResult(text="OpenAI Responses adapter is disabled in v0.", provider_name=self.provider_name, raw={"disabled": True})

    async def complete_json(self, request: LlmJsonRequest, schema: dict[str, Any] | None = None) -> LlmJsonResult:
        return LlmJsonResult(data={"error": "openai_adapter_disabled"}, provider_name=self.provider_name, raw={"disabled": True})

