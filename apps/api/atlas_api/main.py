from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from atlas_api.api import (
    routes_atlas,
    routes_commands,
    routes_dev,
    routes_events,
    routes_exports,
    routes_health,
    routes_learn,
    routes_patches,
    routes_search,
    routes_sessions,
    routes_sources,
    routes_turns,
)
from atlas_api.config import get_settings
from atlas_api.db.connection import Database
from atlas_api.db.migrations import run_migrations
from atlas_api.db.repositories import Repository
from atlas_api.errors import AppError, AuthRequiredError, install_error_handlers
from atlas_api.llm.codex_cli_adapter import CodexCliAdapter
from atlas_api.llm.fake_adapter import FakeLlmAdapter
from atlas_api.llm.openai_responses_adapter import OpenAIResponsesAdapter
from atlas_api.logging_config import configure_logging

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.debug)
    db = Database(settings.database_path)
    await run_migrations(db)
    repo = Repository(db)
    await repo.ensure_default_workspace()
    adapter = await _select_adapter(settings)
    app.state.settings = settings
    app.state.db = db
    app.state.llm_adapter = adapter
    log.info("app_started", provider=adapter.provider_name, db=str(settings.database_path))
    yield


app = FastAPI(title="Research Partner", version="0.1.0", lifespan=lifespan)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_error_handlers(app)


@app.middleware("http")
async def request_context_and_auth(request: Request, call_next):
    request.state.request_id = request.headers.get("x-request-id", uuid4().hex)
    runtime_settings = get_settings()
    if runtime_settings.require_token and request.url.path.startswith("/api"):
        auth = request.headers.get("authorization")
        if auth != f"Bearer {runtime_settings.app_access_token}":
            exc = AuthRequiredError()
            return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": exc.message, "request_id": request.state.request_id}})
    try:
        return await call_next(request)
    except AppError:
        raise


api_router_prefix = "/api"
for router in [
    routes_health.router,
    routes_sessions.router,
    routes_turns.router,
    routes_learn.router,
    routes_atlas.router,
    routes_patches.router,
    routes_sources.router,
    routes_search.router,
    routes_exports.router,
    routes_events.router,
    routes_dev.router,
    routes_commands.router,
]:
    app.include_router(router, prefix=api_router_prefix)


repo_root = Path(__file__).resolve().parents[3]
web_dist = repo_root / "apps" / "web" / "dist"
assets_dir = web_dist / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"error": {"code": "not_found", "message": "API route not found"}})
    requested = web_dist / full_path
    if requested.exists() and requested.is_file():
        return FileResponse(requested)
    index = web_dist / "index.html"
    if index.exists():
        return FileResponse(index)
    return JSONResponse(
        status_code=200,
        content={
            "app": "Research Partner API",
            "message": "Frontend build not found. Run scripts/build.sh for production or scripts/dev.sh for Vite dev.",
        },
    )


async def _select_adapter(settings):
    provider = settings.llm_provider.lower()
    if provider == "codex":
        return CodexCliAdapter(settings)
    if provider == "openai":
        return OpenAIResponsesAdapter(settings)
    if provider == "fake" and settings.allow_fake_for_tests:
        return FakeLlmAdapter()
    return CodexCliAdapter(settings)
