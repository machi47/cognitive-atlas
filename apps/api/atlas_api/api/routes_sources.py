from __future__ import annotations

from fastapi import APIRouter, Request

from atlas_api.db.repositories import Repository
from atlas_api.errors import NotFoundError
from atlas_api.models.sources import SourceCardIn, SourceCardOut, SourceSearchRequest
from atlas_api.services.source_broker import SourceBroker

router = APIRouter()


@router.get("/sources", response_model=list[SourceCardOut])
async def list_sources(request: Request) -> list[SourceCardOut]:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await repo.list_sources(workspace_id)


@router.get("/sources/{source_id}", response_model=SourceCardOut)
async def get_source(request: Request, source_id: str) -> SourceCardOut:
    source = await Repository(request.app.state.db).get_source(source_id)
    if not source:
        raise NotFoundError("Source not found")
    return source


@router.post("/sources/search")
async def search_sources(request: Request, payload: SourceSearchRequest) -> dict:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    sources = await SourceBroker(repo).search_and_store(workspace_id, payload.query, payload.source_types, payload.limit)
    return {"sources": sources}


@router.post("/sources/manual", response_model=SourceCardOut)
async def manual_source(request: Request, payload: SourceCardIn) -> SourceCardOut:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await repo.create_source(workspace_id, payload)


@router.patch("/sources/{source_id}", response_model=SourceCardOut)
async def patch_source(request: Request, source_id: str, payload: SourceCardIn) -> SourceCardOut:
    existing = await Repository(request.app.state.db).get_source(source_id)
    if not existing:
        raise NotFoundError("Source not found")
    return existing

