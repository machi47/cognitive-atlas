from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from atlas_api.db.repositories import Repository

router = APIRouter()


class CommandPayload(BaseModel):
    session_id: str | None = None
    command: str
    args: dict[str, Any] = Field(default_factory=dict)


@router.post("/commands")
async def command(request: Request, payload: CommandPayload) -> dict:
    repo = Repository(request.app.state.db)
    workspace_id = await repo.ensure_default_workspace()
    if payload.command == "fit-review":
        return {"command": payload.command, "report_url": "/api/learning-fit/report"}
    if payload.command == "new":
        session = await repo.create_session(workspace_id)
        return {"command": payload.command, "session": session.model_dump()}
    return {"command": payload.command, "accepted": True, "args": payload.args}

