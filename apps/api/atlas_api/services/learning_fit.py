from __future__ import annotations

from atlas_api.db.repositories import Repository
from atlas_api.models.learning_fit import LearningFitReport
from atlas_api.util.json import loads


class LearningFitService:
    def __init__(self, repo: Repository):
        self.repo = repo

    async def report(self, workspace_id: str) -> LearningFitReport:
        events = await self.repo.learning_events(workspace_id)
        if not events:
            return LearningFitReport(notes=["No learning-fit events yet."])
        payloads = [loads(event["payload_json"], {}) for event in events]
        feedback = [payload.get("feedback") for payload in payloads if payload.get("feedback")]
        assistant_lengths = [payload.get("length", 0) for payload in payloads if event_type(event := payload) == "assistant_response_length"]
        too_much = sum(1 for item in feedback if item == "too_much")
        deepen = sum(1 for item in feedback if item in {"show_deeper", "deepen"})
        sessions = sum(1 for event in events if event["event_type"] == "session_created")
        turns = sum(1 for event in events if event["event_type"] == "turn_created")
        rejected = sum(1 for event in events if event["event_type"] == "patch_rejected")
        patches = sum(1 for event in events if event["event_type"] == "map_patch_created")
        return LearningFitReport(
            average_response_length=sum(assistant_lengths) / len(assistant_lengths) if assistant_lengths else 0,
            too_much_rate=too_much / max(1, len(feedback)),
            deepen_rate=deepen / max(1, len(feedback)),
            return_rate=0,
            session_fragmentation=sessions / max(1, turns),
            patch_rejection_rate=rejected / max(1, patches),
            source_usage_rate=0,
            map_open_rate=0,
            notes=["Metrics are intentionally lightweight and non-gamified."],
        )


def event_type(payload: dict) -> str:
    return payload.get("metric", "")

