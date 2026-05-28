from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ApiModel(BaseModel):
    model_config = {"extra": "forbid"}


JsonDict = dict[str, Any]


class ProcessingState(ApiModel):
    status: str = "succeeded"
    steps: list[str] = Field(default_factory=list)
    message: str | None = None

