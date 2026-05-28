from __future__ import annotations

from fastapi import APIRouter, Request

from atlas_api.db.repositories import Repository
from atlas_api.errors import NotFoundError
from atlas_api.models.atlas import AtlasTree, MapGraph, TopicMapCreate, TopicMapOut
from atlas_api.services.ui_projection import UiProjectionService

router = APIRouter()


@router.get("/atlas/tree", response_model=AtlasTree)
async def atlas_tree(request: Request) -> AtlasTree:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await UiProjectionService(repo).atlas_tree(workspace_id)


@router.get("/atlas/maps", response_model=list[TopicMapOut])
async def list_maps(request: Request) -> list[TopicMapOut]:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await repo.list_maps(workspace_id)


@router.post("/atlas/maps", response_model=TopicMapOut)
async def create_map(request: Request, payload: TopicMapCreate) -> TopicMapOut:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await repo.create_map(workspace_id, payload.title, payload.summary, payload.domain_id, payload.parent_map_id)


@router.get("/atlas/maps/{map_id}", response_model=TopicMapOut)
async def get_map(request: Request, map_id: str) -> TopicMapOut:
    topic_map = await Repository(request.app.state.db).get_map(map_id)
    if not topic_map:
        raise NotFoundError("Map not found")
    return topic_map


@router.get("/atlas/maps/{map_id}/graph", response_model=MapGraph)
async def map_graph(request: Request, map_id: str) -> MapGraph:
    graph = await Repository(request.app.state.db).map_graph(map_id)
    if not graph:
        raise NotFoundError("Map not found")
    return graph


@router.get("/atlas/maps/{map_id}/timeline")
async def map_timeline(request: Request, map_id: str) -> dict:
    repo = Repository(request.app.state.db)
    graph = await repo.map_graph(map_id)
    if not graph:
        raise NotFoundError("Map not found")
    return {"map_id": map_id, "events": []}


@router.get("/atlas/maps/{map_id}/sources")
async def map_sources(request: Request, map_id: str) -> dict:
    graph = await Repository(request.app.state.db).map_graph(map_id)
    if not graph:
        raise NotFoundError("Map not found")
    return {"map_id": map_id, "sources": []}


@router.get("/atlas/maps/{map_id}/questions")
async def map_questions(request: Request, map_id: str) -> dict:
    graph = await Repository(request.app.state.db).map_graph(map_id)
    if not graph:
        raise NotFoundError("Map not found")
    return {"map_id": map_id, "questions": [q.model_dump() for q in graph.questions]}

