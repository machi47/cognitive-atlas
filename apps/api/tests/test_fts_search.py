import pytest

from atlas_api.db.connection import Database
from atlas_api.db.migrations import run_migrations
from atlas_api.db.repositories import Repository


@pytest.mark.asyncio
async def test_search_finds_turns(tmp_path):
    db = Database(tmp_path / "atlas.db")
    await run_migrations(db)
    repo = Repository(db)
    workspace_id = await repo.ensure_default_workspace()
    session = await repo.create_session(workspace_id, "Search")
    await repo.create_turn(session.id, "user", "analog compute data movement", "analog compute data movement", 5)
    results = await repo.search(workspace_id, "analog")
    assert results["turns"]

