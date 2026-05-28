from __future__ import annotations

from typing import Any

from pydantic import Field

from atlas_api.models.common import ApiModel


class DomainOut(ApiModel):
    id: str
    name: str
    description: str | None = None
    parent_domain_id: str | None = None
    status: str


class TopicMapCreate(ApiModel):
    title: str
    summary: str | None = None
    domain_id: str | None = None
    parent_map_id: str | None = None


class TopicMapOut(ApiModel):
    id: str
    workspace_id: str
    domain_id: str | None = None
    parent_map_id: str | None = None
    title: str
    summary: str | None = None
    status: str
    created_at: str
    updated_at: str
    salience: float = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConceptNodeOut(ApiModel):
    id: str
    map_id: str
    label: str
    description: str | None = None
    node_type: str
    epistemic_status: str
    confidence: float
    local_salience: float = 0
    global_salience: float = 0
    novelty_score: float = 0
    bridge_potential: float = 0
    recurrence_count: int = 0


class RelationEdgeOut(ApiModel):
    id: str
    map_id: str | None = None
    from_node_id: str
    to_node_id: str
    relation_type: str
    label: str | None = None
    description: str | None = None
    epistemic_status: str
    confidence: float
    salience: float = 0


class OpenQuestionOut(ApiModel):
    id: str
    session_id: str | None = None
    map_id: str | None = None
    question: str
    status: str
    priority: float = 0


class AtlasTreeMap(ApiModel):
    id: str
    title: str
    summary: str | None = None
    status: str
    node_count: int = 0
    question_count: int = 0
    salience: float = 0
    children: list["AtlasTreeMap"] = Field(default_factory=list)


class AtlasTreeDomain(ApiModel):
    id: str
    name: str
    status: str
    maps: list[AtlasTreeMap] = Field(default_factory=list)


class AtlasTree(ApiModel):
    workspace_id: str
    domains: list[AtlasTreeDomain] = Field(default_factory=list)
    uncategorized_maps: list[AtlasTreeMap] = Field(default_factory=list)


class MapGraph(ApiModel):
    map: TopicMapOut
    nodes: list[ConceptNodeOut]
    edges: list[RelationEdgeOut]
    questions: list[OpenQuestionOut]
    latent_bridges: list[dict[str, Any]] = Field(default_factory=list)

