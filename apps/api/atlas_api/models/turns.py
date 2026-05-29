from __future__ import annotations

from typing import Any

from pydantic import Field

from atlas_api.models.common import ApiModel, ProcessingState
from atlas_api.models.sessions import SessionOut


class TurnCreate(ApiModel):
    content: str
    mode: str | None = None
    response_budget: dict[str, Any] | None = None
    command: str | None = None


class TurnOut(ApiModel):
    id: str
    session_id: str
    role: str
    content: str
    original_content: str | None = None
    created_at: str
    token_estimate: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TurnArtifactsSummary(ApiModel):
    artifact_ids: list[str] = Field(default_factory=list)
    patch_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    map_ids: list[str] = Field(default_factory=list)


class TurnResponse(ApiModel):
    session: SessionOut
    user_turn: TurnOut
    assistant_turn: TurnOut | None = None
    model_error: dict[str, Any] | None = None
    learning_delta_summary: dict[str, Any] = Field(default_factory=dict)
    processing_state: ProcessingState
    artifacts_summary: TurnArtifactsSummary
