from __future__ import annotations

from fastapi import APIRouter, Request

from atlas_api.config import get_settings

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict:
    provider = await request.app.state.llm_adapter.healthcheck()
    return {"ok": True, "app": "Learning Chat", "provider": provider.model_dump()}


@router.get("/config/public")
async def public_config(request: Request) -> dict:
    settings = get_settings()
    provider = await request.app.state.llm_adapter.healthcheck()
    return settings.public_config(provider.model_dump())
