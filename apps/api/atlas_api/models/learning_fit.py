from __future__ import annotations

from pydantic import Field

from atlas_api.models.common import ApiModel


class FeedbackIn(ApiModel):
    turn_id: str
    feedback: str


class LearningFitReport(ApiModel):
    average_response_length: float = 0
    too_much_rate: float = 0
    deepen_rate: float = 0
    return_rate: float = 0
    session_fragmentation: float = 0
    patch_rejection_rate: float = 0
    source_usage_rate: float = 0
    map_open_rate: float = 0
    notes: list[str] = Field(default_factory=list)

