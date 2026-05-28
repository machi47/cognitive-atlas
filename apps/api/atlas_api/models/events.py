from __future__ import annotations

from typing import Any

from pydantic import Field

from atlas_api.models.common import ApiModel


class EventOut(ApiModel):
    id: str
    workspace_id: str
    session_id: str | None = None
    event_type: str
    aggregate_type: str
    aggregate_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    causation_id: str | None = None
    correlation_id: str | None = None

