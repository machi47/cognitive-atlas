from __future__ import annotations

from atlas_api.models.patches import MapPatch, MapPatchValidationResult


FORBIDDEN_USER_STATE_PHRASES = [
    "user now believes",
    "user learned",
    "user accepts",
    "user's intuition changed",
    "user understands",
]


class MapPatchValidator:
    def validate(self, patch: MapPatch, forbidden_user_state_claims: list[str] | None = None) -> MapPatchValidationResult:
        issues: list[str] = []
        forbidden_user_state_claims = forbidden_user_state_claims or []
        if forbidden_user_state_claims:
            issues.append("Extraction attempted forbidden user-state claims.")
        if not patch.provenance:
            issues.append("Patch has no provenance.")
        payload = patch.model_dump()
        serialized = str(payload).lower()
        for phrase in FORBIDDEN_USER_STATE_PHRASES:
            if phrase in serialized:
                issues.append(f"Forbidden user belief memory phrase: {phrase}")
        for claim in patch.add_claims:
            if claim.epistemic_status == "source_backed" and not claim.source_ids:
                issues.append("Source-backed claim lacks source id.")
        low_conf_edges = [edge for edge in patch.add_edges if edge.confidence < 0.35]
        if len(low_conf_edges) > 3:
            issues.append("Too many low-confidence edges.")
        if len(patch.add_edges) > 12:
            issues.append("Relation overload; patch should remain pending.")
        if len(patch.add_nodes) + len(patch.add_edges) + len(patch.add_claims) > 60:
            issues.append("Patch is too large for auto-apply.")
        auto_apply = not issues or issues == ["Relation overload; patch should remain pending."]
        risk = patch.risk_level
        if issues:
            risk = "medium" if auto_apply else "high"
        return MapPatchValidationResult(
            valid=not any(issue != "Relation overload; patch should remain pending." for issue in issues),
            risk_level=risk,
            issues=issues,
            auto_apply=auto_apply and risk != "high" and len(patch.add_edges) <= 12,
            cleaned_patch=patch if not issues or auto_apply else None,
        )

