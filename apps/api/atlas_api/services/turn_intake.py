from __future__ import annotations

from atlas_api.db.repositories import Repository
from atlas_api.models.turns import TurnCreate, TurnOut
from atlas_api.util.text import estimate_tokens, normalize_whitespace, parse_command


class TurnIntakeService:
    def __init__(self, repo: Repository):
        self.repo = repo

    async def intake(self, session_id: str, payload: TurnCreate) -> tuple[TurnOut, str | None, str]:
        command, command_text = parse_command(payload.content)
        content_for_turn = command_text if command and command_text else payload.content
        normalized = normalize_whitespace(content_for_turn)
        turn = await self.repo.create_turn(
            session_id=session_id,
            role="user",
            content=normalized,
            original_content=payload.content,
            token_estimate=estimate_tokens(payload.content),
            metadata={"command": payload.command or command, "mode": payload.mode},
        )
        return turn, payload.command or command, normalized

