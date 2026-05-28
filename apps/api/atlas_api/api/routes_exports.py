from __future__ import annotations

from fastapi import APIRouter, Request, Response

from atlas_api.db.repositories import Repository
from atlas_api.services.export_service import ExportService

router = APIRouter()


@router.get("/export/session/{session_id}.md")
async def export_session(request: Request, session_id: str) -> Response:
    text = await ExportService(Repository(request.app.state.db)).session_markdown(session_id)
    return Response(text, media_type="text/markdown")


@router.get("/export/map/{map_id}.md")
async def export_map(request: Request, map_id: str) -> Response:
    text = await ExportService(Repository(request.app.state.db)).map_markdown(map_id)
    return Response(text, media_type="text/markdown")


@router.get("/export/atlas.json")
async def export_atlas(request: Request) -> Response:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    text = await ExportService(repo).atlas_json(workspace_id)
    return Response(text, media_type="application/json")

