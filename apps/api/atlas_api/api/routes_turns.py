from __future__ import annotations

from fastapi import APIRouter, Request

from atlas_api.db.repositories import Repository
from atlas_api.errors import NotFoundError
from atlas_api.models.turns import TurnCreate, TurnOut, TurnResponse
from atlas_api.workers.pipeline import TurnPipeline

router = APIRouter()


@router.get("/sessions/{session_id}/turns", response_model=list[TurnOut])
async def list_turns(request: Request, session_id: str) -> list[TurnOut]:
    session = await Repository(request.app.state.db).get_session(session_id)
    if not session:
        raise NotFoundError("Session not found")
    return await Repository(request.app.state.db).list_turns(session_id)


@router.post("/sessions/{session_id}/turns", response_model=TurnResponse)
async def create_turn(request: Request, session_id: str, payload: TurnCreate) -> TurnResponse:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    session = await repo.get_session(session_id)
    if not session:
        raise NotFoundError("Session not found")
    return await TurnPipeline(repo, request.app.state.llm_adapter).process_turn(workspace_id, session_id, payload)


@router.get("/turns/{turn_id}", response_model=TurnOut)
async def get_turn(request: Request, turn_id: str) -> TurnOut:
    turn = await Repository(request.app.state.db).get_turn(turn_id)
    if not turn:
        raise NotFoundError("Turn not found")
    return turn


@router.get("/turns/{turn_id}/artifacts")
async def get_turn_artifacts(request: Request, turn_id: str) -> list[dict]:
    return await Repository(request.app.state.db).list_artifacts_for_turn(turn_id)

