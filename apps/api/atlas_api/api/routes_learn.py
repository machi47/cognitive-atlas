from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from atlas_api.db.repositories import Repository
from atlas_api.errors import NotFoundError
from atlas_api.services.learning_projection import LearningProjectionService, TextbookProjectionService

router = APIRouter()


class BridgePatch(BaseModel):
    status: str


@router.get("/learn/overview")
async def learn_overview(request: Request) -> dict:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await LearningProjectionService(repo).overview(workspace_id)


@router.get("/learn/topology")
async def learn_topology(request: Request) -> dict:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await LearningProjectionService(repo).topology(workspace_id)


@router.get("/learn/textbook")
async def learn_textbook(request: Request) -> dict:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await TextbookProjectionService(repo).textbook(workspace_id)


@router.get("/learn/textbook/{map_id}")
async def learn_textbook_for_map(request: Request, map_id: str) -> dict:
    repo = Repository(request.app.state.db)
    if not await repo.get_map(map_id):
        raise NotFoundError("Map not found")
    workspace_id = await repo.ensure_default_workspace()
    return await TextbookProjectionService(repo).textbook(workspace_id, map_id=map_id)


@router.get("/learn/bridges")
async def learn_bridges(request: Request) -> list[dict]:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await LearningProjectionService(repo).bridges(workspace_id)


@router.patch("/learn/bridges/{bridge_id}")
async def patch_bridge(request: Request, bridge_id: str, payload: BridgePatch) -> dict:
    bridge = await Repository(request.app.state.db).update_bridge_status(bridge_id, payload.status)
    if not bridge:
        raise NotFoundError("Bridge not found")
    return bridge


@router.get("/learn/source-needs")
async def learn_source_needs(request: Request) -> list[dict]:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await LearningProjectionService(repo).source_needs(workspace_id)


@router.get("/learn/updates/recent")
async def learn_recent_updates(request: Request) -> list[dict]:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await LearningProjectionService(repo).recent_updates(workspace_id)
