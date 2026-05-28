import pytest

from atlas_api.db.connection import Database
from atlas_api.db.migrations import run_migrations
from atlas_api.db.repositories import Repository


@pytest.mark.asyncio
async def test_create_session(tmp_path):
    db = Database(tmp_path / "atlas.db")
    await run_migrations(db)
    repo = Repository(db)
    workspace_id = await repo.ensure_default_workspace()
    session = await repo.create_session(workspace_id, "Test")
    assert session.title == "Test"
    sessions = await repo.list_sessions(workspace_id)
    assert sessions[0].id == session.id

