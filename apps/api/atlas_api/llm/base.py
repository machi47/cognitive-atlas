from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from atlas_api.models.llm import LlmHealth, LlmJsonRequest, LlmJsonResult, LlmTextRequest, LlmTextResult


class LlmAdapter(ABC):
    provider_name: str
    supports_web_search: bool = False
    supports_schema_output: bool = False

    @abstractmethod
    async def complete_text(self, request: LlmTextRequest) -> LlmTextResult:
        raise NotImplementedError

    @abstractmethod
    async def complete_json(self, request: LlmJsonRequest, schema: dict[str, Any] | None = None) -> LlmJsonResult:
        raise NotImplementedError

    @abstractmethod
    async def healthcheck(self) -> LlmHealth:
        raise NotImplementedError

