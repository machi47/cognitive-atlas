from __future__ import annotations

from atlas_api.models.turns import TurnOut
from atlas_api.util.token_budget import clamp_chars


class ContextBroker:
    discussion_max_chars = 24000
    extraction_max_chars = 24000
    research_max_chars = 18000
    map_patch_max_chars = 24000

    def build_discussion_context(self, current: str, recent_turns: list[TurnOut], mode: str, memory_capsule: str | None = None) -> str:
        lines = [
            "You are Research Partner: a high-bandwidth technical/physical research conversation partner.",
            "Your job is to help the user learn through discussion, tension testing, abstraction building, mental simulation, and cross-domain linking.",
            "Answer the user's actual message directly. Do not mention internal modes, maps, patches, artifacts, extraction, or backend state.",
            "Do not give a generic short answer. For technical learning/building questions, develop the reasoning enough that the user can actually think with you.",
            "Silently do separate internal work before answering: identify the user's intent, technical objects, weak assumptions, likely constraints, open questions, source needs, and any relevant prior topology.",
            "Keep the local chat lane clean. Use selected prior learning only when it is directly relevant; never dump global memory into the conversation.",
            "When the user is trying to build or understand something, prefer concrete structure: frames, tradeoffs, dependencies, failure modes, small experiments, and what to decide next.",
            "When the user is correcting you or frustrated, engage the substance of the correction instead of giving a bland apology.",
            f"Internal route label, never mention this: {mode}",
            "Recent dialogue:",
        ]
        for turn in recent_turns[-10:]:
            lines.append(f"{turn.role}: {turn.content}")
        if memory_capsule:
            lines.extend(["Selected prior learning capsule:", memory_capsule])
        lines.append(f"Current user message: {current}")
        return clamp_chars("\n".join(lines), self.discussion_max_chars)

    def build_extraction_context(self, user_message: str, assistant_message: str, source_cards: list[dict] | None = None) -> str:
        lines = ["Extract from this exchange only.", f"User: {user_message}", f"Research Partner: {assistant_message}"]
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
