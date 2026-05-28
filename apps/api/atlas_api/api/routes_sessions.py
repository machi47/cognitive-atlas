from __future__ import annotations

from fastapi import APIRouter, Request

from atlas_api.db.repositories import Repository
from atlas_api.errors import NotFoundError
from atlas_api.models.sessions import SessionCreate, SessionOut, SessionPatch

router = APIRouter()


@router.get("/sessions", response_model=list[SessionOut])
async def list_sessions(request: Request, include_archived: bool = False) -> list[SessionOut]:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await repo.list_sessions(workspace_id, include_archived=include_archived)


@router.post("/sessions", response_model=SessionOut)
async def create_session(request: Request, payload: SessionCreate) -> SessionOut:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await repo.create_session(workspace_id, payload.title or "New Thought", payload.mode, payload.metadata)


@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(request: Request, session_id: str) -> SessionOut:
    session = await Repository(request.app.state.db).get_session(session_id)
    if not session:
        raise NotFoundError("Session not found")
    return session


@router.patch("/sessions/{session_id}", response_model=SessionOut)
async def patch_session(request: Request, session_id: str, payload: SessionPatch) -> SessionOut:
    updates = payload.model_dump(exclude_unset=True)
    session = await Repository(request.app.state.db).update_session(session_id, updates)
    if not session:
        raise NotFoundError("Session not found")
    return session


@router.post("/sessions/{session_id}/archive", response_model=SessionOut)
async def archive_session(request: Request, session_id: str) -> SessionOut:
    session = await Repository(request.app.state.db).update_session(session_id, {"status": "archived"})
    if not session:
        raise NotFoundError("Session not found")
    return session


@router.post("/sessions/{session_id}/fork", response_model=SessionOut)
async def fork_session(request: Request, session_id: str) -> SessionOut:
    session = await Repository(request.app.state.db).fork_session(session_id)
    if not session:
        raise NotFoundError("Session not found")
    return session

