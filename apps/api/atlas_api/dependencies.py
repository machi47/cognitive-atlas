from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from atlas_api.config import Settings, get_settings
from atlas_api.db.connection import Database
from atlas_api.llm.base import LlmAdapter
from atlas_api.security import require_access


def get_app_settings() -> Settings:
    return get_settings()


def get_db(request: Request) -> Database:
    return request.app.state.db


def get_llm_adapter(request: Request) -> LlmAdapter:
    return request.app.state.llm_adapter


async def require_auth(settings: Annotated[Settings, Depends(get_app_settings)], authorization: str | None = None) -> None:
    await require_access(settings, authorization)

