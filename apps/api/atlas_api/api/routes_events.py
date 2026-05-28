from __future__ import annotations

from fastapi import APIRouter, Request

from atlas_api.config import get_settings
from atlas_api.db.repositories import Repository
from atlas_api.errors import NotFoundError
from atlas_api.models.learning_fit import FeedbackIn, LearningFitReport
from atlas_api.services.learning_fit import LearningFitService

router = APIRouter()


@router.get("/events/recent")
async def recent_events(request: Request) -> list[dict]:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return [event.model_dump() for event in await repo.recent_events(workspace_id)]


@router.get("/artifacts/{artifact_id}")
async def artifact(request: Request, artifact_id: str) -> dict:
    item = await Repository(request.app.state.db).get_artifact(artifact_id)
    if not item:
        raise NotFoundError("Artifact not found")
    return item


@router.get("/debug/llm-runs")
async def llm_runs(request: Request) -> dict:
    settings = get_settings()
    if not settings.debug:
        raise NotFoundError("Debug routes are disabled")
    runs = [path.name for path in sorted(settings.codex_runs_dir.glob("*"), reverse=True)[:25] if path.is_dir()]
    return {"runs": runs}


@router.post("/feedback")
async def feedback(request: Request, payload: FeedbackIn) -> dict:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    turn = await repo.get_turn(payload.turn_id)
    await repo.create_artifact(workspace_id, turn.session_id if turn else None, payload.turn_id, "feedback", "Turn feedback", payload.model_dump(), "succeeded")
    return {"ok": True}


@router.get("/learning-fit/report", response_model=LearningFitReport)
async def learning_fit_report(request: Request) -> LearningFitReport:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    return await LearningFitService(repo).report(workspace_id)

