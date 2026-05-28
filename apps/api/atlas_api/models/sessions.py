from __future__ import annotations

from typing import Any

from pydantic import Field

from atlas_api.models.common import ApiModel


class SessionCreate(ApiModel):
    title: str | None = None
    mode: str = "discuss"
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionPatch(ApiModel):
    title: str | None = None
    status: str | None = None
    mode: str | None = None
    user_summary: str | None = None
    metadata: dict[str, Any] | None = None


class SessionOut(ApiModel):
    id: str
    workspace_id: str
    title: str
    status: str
    mode: str
    response_budget: dict[str, Any]
    created_at: str
    updated_at: str
    last_turn_at: str | None = None
    user_summary: str | None = None
    system_summary: str | None = None
    active_map_ids: list[str] = Field(default_factory=list)
    touched_map_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

