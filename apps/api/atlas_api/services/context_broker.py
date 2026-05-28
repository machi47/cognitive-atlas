from __future__ import annotations

from atlas_api.models.turns import TurnOut
from atlas_api.util.token_budget import clamp_chars


class ContextBroker:
    discussion_max_chars = 12000
    extraction_max_chars = 24000
    research_max_chars = 18000
    map_patch_max_chars = 24000

    def build_discussion_context(self, current: str, recent_turns: list[TurnOut], mode: str, response_budget: dict) -> str:
        lines = [
            "You are the conversation plane of a private learning app.",
            "Answer the user's actual message directly. Do not mention internal modes, maps, patches, artifacts, or backend state.",
            "Stay compact unless the user asks for depth. If the user is correcting you or frustrated, acknowledge the miss and respond to the correction.",
            f"Internal route label, never mention this: {mode}",
            f"Target response budget, never mention this: {response_budget}",
            "Recent dialogue:",
        ]
        for turn in recent_turns[-10:]:
            lines.append(f"{turn.role}: {turn.content}")
        lines.append(f"Current user message: {current}")
        return clamp_chars("\n".join(lines), self.discussion_max_chars)

    def build_extraction_context(self, user_message: str, assistant_message: str, source_cards: list[dict] | None = None) -> str:
        lines = ["Extract from this exchange only.", f"User: {user_message}", f"Assistant: {assistant_message}"]
        if source_cards:
            lines.append(f"Selected source cards: {source_cards[:5]}")
        return clamp_chars("\n".join(lines), self.extraction_max_chars)

    def build_role_packet(self, role: str, content: str) -> dict[str, str | int]:
        budgets = {
            "discussion": self.discussion_max_chars,
            "extraction": self.extraction_max_chars,
            "research": self.research_max_chars,
            "map_patch": self.map_patch_max_chars,
            "critic": self.map_patch_max_chars,
        }
        max_chars = budgets.get(role, self.discussion_max_chars)
        return {"role": role, "content": clamp_chars(content, max_chars), "max_chars": max_chars}
