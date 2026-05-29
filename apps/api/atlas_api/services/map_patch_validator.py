from __future__ import annotations

from atlas_api.models.patches import MapPatch, MapPatchValidationResult


FORBIDDEN_USER_STATE_PHRASES = [
    "user now believes",
    "user learned",
    "user accepts",
    "user's intuition changed",
    "user understands",
]

FORBIDDEN_MAP_TITLES = {
    "extract exchange only",
    "current user message",
    "post turn extraction",
    "discussion reply",
    "recent dialogue",
}


class MapPatchValidator:
    def validate(self, patch: MapPatch, forbidden_user_state_claims: list[str] | None = None) -> MapPatchValidationResult:
        issues: list[str] = []
        blocking_issues: list[str] = []
        forbidden_user_state_claims = forbidden_user_state_claims or []
        if not patch.provenance:
            blocking_issues.append("Patch has no provenance.")
        payload = patch.model_dump()
        serialized = str(payload).lower()
        for forbidden_claim in forbidden_user_state_claims:
            if forbidden_claim and forbidden_claim.lower() in serialized:
                blocking_issues.append("Patch attempted forbidden user-state claims.")
                break
        for phrase in FORBIDDEN_USER_STATE_PHRASES:
            if phrase in serialized:
                blocking_issues.append(f"Forbidden user belief memory phrase: {phrase}")
        for map_payload in patch.create_maps:
            if str(map_payload.get("title", "")).strip().lower() in FORBIDDEN_MAP_TITLES:
                blocking_issues.append("Patch attempted to create a prompt-boilerplate map title.")
        for claim in patch.add_claims:
            if claim.epistemic_status == "source_backed" and not claim.source_ids:
                blocking_issues.append("Source-backed claim lacks source id.")
        low_conf_edges = [edge for edge in patch.add_edges if edge.confidence < 0.35]
        if len(low_conf_edges) > 3:
            blocking_issues.append("Too many low-confidence edges.")
        if len(patch.add_edges) > 30:
            issues.append("Relation overload; patch should remain pending.")
        if len(patch.add_nodes) + len(patch.add_edges) + len(patch.add_claims) > 60:
            issues.append("Patch is too large for auto-apply.")
        if blocking_issues:
            all_issues = [*blocking_issues, *issues]
            return MapPatchValidationResult(
                valid=False,
                risk_level="high",
                issues=all_issues,
                auto_apply=False,
                cleaned_patch=None,
            )
        cleaned_patch = self._trim_for_auto_apply(patch) if issues else patch
        auto_apply = True
        risk = patch.risk_level
        if issues:
            risk = "medium"
        return MapPatchValidationResult(
            valid=True,
            risk_level=risk,
            issues=issues,
            auto_apply=auto_apply and risk != "high",
            cleaned_patch=cleaned_patch,
        )

    def _trim_for_auto_apply(self, patch: MapPatch) -> MapPatch:
        def score_node(node) -> tuple[int, float, float]:
            priority = {
                "project_goal": 0,
                "foundation": 1,
                "constraint": 2,
                "cross_domain_abstraction": 3,
            }.get(node.node_type, 4)
            return (priority, -node.local_salience, -node.confidence)

        keep_nodes = sorted(patch.add_nodes, key=score_node)[:24]
        keep_labels = {node.label.lower() for node in keep_nodes}
        keep_edges = [
            edge
            for edge in sorted(patch.add_edges, key=lambda item: (-item.salience, -item.confidence))
            if edge.from_label.lower() in keep_labels and edge.to_label.lower() in keep_labels
        ][:24]
        keep_claims = sorted(patch.add_claims, key=lambda item: -item.confidence)[:8]
        keep_questions = sorted(patch.add_questions, key=lambda item: -item.priority)[:10]
        keep_tensions = patch.add_tensions[:6]
        keep_analogies = patch.add_analogies[:4]
        keep_bridges = sorted(patch.add_latent_bridges, key=lambda item: -item.confidence)[:8]
        return patch.model_copy(
            update={
                "add_nodes": keep_nodes,
                "add_edges": keep_edges,
                "add_claims": keep_claims,
                "add_questions": keep_questions,
                "add_tensions": keep_tensions,
                "add_analogies": keep_analogies,
                "add_latent_bridges": keep_bridges,
                "risk_level": "medium",
            }
        )
