from __future__ import annotations

from fastapi import APIRouter, Request

from atlas_api.db.repositories import Repository
from atlas_api.errors import NotFoundError
from atlas_api.models.patches import MapPatchOut

router = APIRouter()


@router.get("/patches", response_model=list[MapPatchOut])
async def patches(request: Request, status: str | None = None) -> list[MapPatchOut]:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await repo.list_patches(workspace_id, status=status)


@router.get("/patches/recent", response_model=list[MapPatchOut])
async def recent_patches(request: Request) -> list[MapPatchOut]:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await repo.list_patches(workspace_id)


@router.post("/patches/{patch_id}/apply", response_model=MapPatchOut)
async def apply_patch(request: Request, patch_id: str) -> MapPatchOut:
    patch = await Repository(request.app.state.db).update_patch_status(patch_id, "applied")
    if not patch:
        raise NotFoundError("Patch not found")
    return patch


@router.post("/patches/{patch_id}/reject", response_model=MapPatchOut)
async def reject_patch(request: Request, patch_id: str) -> MapPatchOut:
    patch = await Repository(request.app.state.db).update_patch_status(patch_id, "rejected")
    if not patch:
        raise NotFoundError("Patch not found")
    return patch


@router.post("/patches/{patch_id}/undo", response_model=MapPatchOut)
async def undo_patch(request: Request, patch_id: str) -> MapPatchOut:
    patch = await Repository(request.app.state.db).update_patch_status(patch_id, "undone")
    if not patch:
        raise NotFoundError("Patch not found")
    return patch

