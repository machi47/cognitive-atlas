from __future__ import annotations

from typing import Any

from pydantic import Field

from atlas_api.models.common import ApiModel


class DiscussionReply(ApiModel):
    message: str
    response_mode: str = "discuss"
    source_ids_used: list[str] = Field(default_factory=list)
    suggested_followups: list[str] = Field(default_factory=list, max_length=3)
    uncertainty_notes: list[str] = Field(default_factory=list)
    should_research_more: bool = False


class LlmTextRequest(ApiModel):
    task: str
    prompt: str
    model: str | None = None
    reasoning_effort: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LlmJsonRequest(LlmTextRequest):
    schema_name: str | None = None


class LlmTextResult(ApiModel):
    text: str
    provider_name: str
    raw: dict[str, Any] = Field(default_factory=dict)


class LlmJsonResult(ApiModel):
    data: dict[str, Any]
    provider_name: str
    raw: dict[str, Any] = Field(default_factory=dict)


class LlmHealth(ApiModel):
    provider_name: str
    available: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)

