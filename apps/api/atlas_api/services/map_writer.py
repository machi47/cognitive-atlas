from __future__ import annotations

from atlas_api.db.repositories import Repository
from atlas_api.models.patches import MapPatch, MapPatchOut, MapPatchValidationResult


class MapWriter:
    def __init__(self, repo: Repository):
        self.repo = repo

    async def persist(self, workspace_id: str, session_id: str, turn_id: str, patch: MapPatch, validation: MapPatchValidationResult) -> tuple[MapPatchOut, dict[str, int]]:
        patch_to_store = validation.cleaned_patch or patch
        counters = {"maps": 0, "nodes": 0, "edges": 0, "claims": 0, "questions": 0, "tensions": 0, "analogies": 0, "latent_bridges": 0}
        status = "pending"
        if validation.valid and validation.auto_apply and patch_to_store.action != "no_op":
            target_map_ids, counters = await self.repo.apply_patch_to_map(workspace_id, session_id, turn_id, patch_to_store.model_dump())
            patch_to_store.target_map_ids = target_map_ids
            status = "applied"
        elif patch_to_store.action == "no_op":
            status = "skipped"
        patch_out = await self.repo.insert_map_patch(workspace_id, session_id, turn_id, patch_to_store.model_dump(), status, validation.risk_level)
        return patch_out, counters
