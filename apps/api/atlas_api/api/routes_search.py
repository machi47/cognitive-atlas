from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from atlas_api.db.repositories import Repository

router = APIRouter()


class SearchPayload(BaseModel):
    q: str


@router.get("/search")
async def search_get(request: Request, q: str = "") -> dict:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await repo.search(workspace_id, q)


@router.post("/search")
async def search_post(request: Request, payload: SearchPayload) -> dict:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await repo.search(workspace_id, payload.q)

