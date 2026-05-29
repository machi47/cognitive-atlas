from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from atlas_api.db.repositories import Repository

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/reset-data")
async def reset_data(request: Request):
    settings = request.app.state.settings
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Not found")
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    counts = await repo.reset_workspace_data(workspace_id)
    return {"status": "reset", "workspace_id": workspace_id, "deleted": counts}
