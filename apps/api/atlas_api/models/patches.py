from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from atlas_api.models.common import ApiModel


class Provenance(ApiModel):
    turn_id: str | None = None
    session_id: str | None = None
    speaker: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    note: str | None = None


class NodeCandidate(ApiModel):
    label: str
    description: str | None = None
    node_type: str = "concept"
    epistemic_status: str = "user_asserted"
    confidence: float = 0.6
    local_salience: float = 0.5
    global_salience: float = 0.2
    novelty_score: float = 0.3
    bridge_potential: float = 0.2
    metadata: dict[str, Any] = Field(default_factory=dict)


class EdgeCandidate(ApiModel):
    from_label: str
    to_label: str
    relation_type: str
    label: str | None = None
    description: str | None = None
    epistemic_status: str = "speculative"
    confidence: float = 0.5
    salience: float = 0.4


class ClaimCandidate(ApiModel):
    text: str
    claim_type: str = "observation"
    epistemic_status: str = "user_asserted"
    confidence: float = 0.5
    source_ids: list[str] = Field(default_factory=list)


class OpenQuestionCandidate(ApiModel):
    question: str
    status: str = "open"
    priority: float = 0.3


class AnalogyCandidate(ApiModel):
    source_concept: str
    target_concept: str
    useful_because: str | None = None
    breaks_at: str | None = None
    status: str = "suggested"
    confidence: float = 0.5


class LatentBridgeCandidate(ApiModel):
    from_label: str
    to_label: str
    bridge_type: str = "bridges_to"
    reason: str
    confidence: float = 0.45
    status: str = "suggested"
    discovered_by: str = "deterministic"
    evidence_artifact_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PostTurnExtraction(ApiModel):
    topics: list[str] = Field(default_factory=list)
    claims: list[ClaimCandidate] = Field(default_factory=list)
    node_candidates: list[NodeCandidate] = Field(default_factory=list)
    edge_candidates: list[EdgeCandidate] = Field(default_factory=list)
    open_questions: list[OpenQuestionCandidate] = Field(default_factory=list)
    tensions: list[dict[str, Any]] = Field(default_factory=list)
    analogies: list[AnalogyCandidate] = Field(default_factory=list)
    latent_bridges: list[LatentBridgeCandidate] = Field(default_factory=list)
    source_needs: list[str] = Field(default_factory=list)
    forbidden_user_state_claims: list[str] = Field(default_factory=list)
    notes: str = ""


class MapPatch(ApiModel):
    action: Literal["update_existing", "create_new", "bridge_maps", "split_suggest", "merge_suggest", "no_op"] = "no_op"
    target_map_ids: list[str] = Field(default_factory=list)
    create_maps: list[dict[str, Any]] = Field(default_factory=list)
    add_nodes: list[NodeCandidate] = Field(default_factory=list)
    update_nodes: list[dict[str, Any]] = Field(default_factory=list)
    add_edges: list[EdgeCandidate] = Field(default_factory=list)
    add_claims: list[ClaimCandidate] = Field(default_factory=list)
    add_questions: list[OpenQuestionCandidate] = Field(default_factory=list)
    add_tensions: list[dict[str, Any]] = Field(default_factory=list)
    add_analogies: list[AnalogyCandidate] = Field(default_factory=list)
    add_latent_bridges: list[LatentBridgeCandidate] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)
    confidence: float = 0.5
    risk_level: str = "low"


class MapPatchValidationResult(ApiModel):
    valid: bool
    risk_level: str = "low"
    issues: list[str] = Field(default_factory=list)
    auto_apply: bool = True
    cleaned_patch: MapPatch | None = None


class MapPatchOut(ApiModel):
    id: str
    workspace_id: str
    session_id: str | None = None
    turn_id: str | None = None
    target_map_ids: list[str] = Field(default_factory=list)
    patch: dict[str, Any]
    status: str
    risk_level: str
    created_at: str
    applied_at: str | None = None
    rejected_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
