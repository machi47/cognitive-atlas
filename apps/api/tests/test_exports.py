import pytest

from atlas_api.db.connection import Database
from atlas_api.db.migrations import run_migrations
from atlas_api.db.repositories import Repository
from atlas_api.services.export_service import ExportService


@pytest.mark.asyncio
async def test_export_session_markdown(tmp_path):
    db = Database(tmp_path / "atlas.db")
    await run_migrations(db)
    repo = Repository(db)
    workspace_id = await repo.ensure_default_workspace()
    session = await repo.create_session(workspace_id, "Export Me")
    await repo.create_turn(session.id, "user", "hello", "hello", 1)
    text = await ExportService(repo).session_markdown(session.id)
    assert "# Export Me" in text
    assert "hello" in text

