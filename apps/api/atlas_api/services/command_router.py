from __future__ import annotations


COMMAND_MODES = {
    "deepen": "deep",
    "shorter": "discuss",
    "map": "map",
    "sources": "source",
    "criticize": "critique",
    "compress": "compress",
    "quiz": "quiz",
    "research": "research",
    "trace": "trace",
}


class CommandRouter:
    def route(self, command: str | None, current_mode: str) -> str:
        if not command:
            return current_mode
        return COMMAND_MODES.get(command, current_mode)

