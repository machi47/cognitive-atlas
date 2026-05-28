from __future__ import annotations

from typing import Any

from pydantic import Field

from atlas_api.models.common import ApiModel


class SourceCardIn(ApiModel):
    title: str
    url: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    source_type: str = "manual"
    year: int | None = None
    authors: list[str] = Field(default_factory=list)
    venue: str | None = None
    abstract: str | None = None
    key_claims: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    relevance_score: float = 0
    credibility_score: float = 0
    freshness_score: float = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class SourceCardOut(SourceCardIn):
    id: str
    workspace_id: str
    created_at: str
    updated_at: str


class SourceSearchRequest(ApiModel):
    query: str
    source_types: list[str] = Field(default_factory=lambda: ["openalex", "crossref", "arxiv"])
    limit: int = 5

