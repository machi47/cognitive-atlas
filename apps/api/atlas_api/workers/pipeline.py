from __future__ import annotations

from atlas_api.db.repositories import Repository
from atlas_api.errors import AppError
from atlas_api.llm.base import LlmAdapter
from atlas_api.models.common import ProcessingState
from atlas_api.models.turns import TurnCreate, TurnResponse, TurnArtifactsSummary
from atlas_api.services.command_router import CommandRouter
from atlas_api.services.context_broker import ContextBroker
from atlas_api.services.conversational_agent import ConversationalAgent
from atlas_api.services.map_patch_builder import MapPatchBuilder
from atlas_api.services.map_patch_validator import MapPatchValidator
from atlas_api.services.map_writer import MapWriter
from atlas_api.services.post_turn_extractor import PostTurnExtractor
from atlas_api.services.research_need import ResearchNeedDetector
from atlas_api.services.research_planner import ResearchPlanner
from atlas_api.services.source_broker import SourceBroker
from atlas_api.services.topic_router import TopicRouter
from atlas_api.services.turn_intake import TurnIntakeService
from atlas_api.util.text import estimate_tokens, first_sentence_title


class TurnPipeline:
    def __init__(self, repo: Repository, llm: LlmAdapter):
        self.repo = repo
        self.llm = llm
        self.context_broker = ContextBroker()
        self.command_router = CommandRouter()
        self.intake_service = TurnIntakeService(repo)
        self.topic_router = TopicRouter(llm)
        self.research_detector = ResearchNeedDetector(llm)
        self.research_planner = ResearchPlanner()
        self.source_broker = SourceBroker(repo)
        self.conversational_agent = ConversationalAgent(llm)
        self.extractor = PostTurnExtractor(llm)
        self.patch_builder = MapPatchBuilder(repo)
        self.patch_validator = MapPatchValidator()
        self.map_writer = MapWriter(repo)

    async def process_turn(self, workspace_id: str, session_id: str, payload: TurnCreate) -> TurnResponse:
        session = await self.repo.get_session(session_id)
        if not session:
            session = await self.repo.create_session(workspace_id)

        user_turn, command, normalized = await self.intake_service.intake(session.id, payload)
        mode = self.command_router.route(command, payload.mode or session.mode)
        if session.title == "New Thought":
            await self.repo.update_session(session.id, {"title": first_sentence_title(normalized)})

        maps = await self.repo.list_maps(workspace_id)
        route = await self.topic_router.route(normalized, [item.title for item in maps[:50]])
        topics = [segment.get("candidate_topic") for segment in route.get("segments", []) if segment.get("candidate_topic")]
        research_need = await self.research_detector.detect(normalized, topics)
        research_plan = self.research_planner.plan(research_need, topics)
        source_cards: list[dict] = []
        explicit_research = mode in {"research", "source"} or any(
            marker in normalized.lower()
            for marker in ["source", "sources", "research", "latest", "current", "recent paper", "cite"]
        )
        if explicit_research and research_need.get("needs_research"):
            for query in research_plan.get("queries", [])[:2]:
                source_cards.extend(
                    await self.source_broker.search_and_store(
                        workspace_id,
                        query["query"],
                        research_plan.get("source_types") or ["openalex", "crossref", "arxiv"],
                        limit=2,
                    )
                )

        recent_turns = await self.repo.list_turns(session.id)
        discussion_context = self.context_broker.build_discussion_context(normalized, recent_turns, mode, payload.response_budget or session.response_budget)
        reply = await self.conversational_agent.reply(discussion_context, mode)
        assistant_turn = await self.repo.create_turn(
            session.id,
            "assistant",
            reply.message,
            None,
            estimate_tokens(reply.message),
            {"mode": mode, "source_ids_used": reply.source_ids_used, "uncertainty_notes": reply.uncertainty_notes},
        )

        artifact_ids: list[str] = []
        patch_ids: list[str] = []
        map_ids: list[str] = []
        processing_message = "updated"
        try:
            extraction_context = self.context_broker.build_extraction_context(normalized, reply.message, source_cards)
            extraction = await self.extractor.extract(extraction_context)
            extraction_artifact = await self.repo.create_artifact(
                workspace_id,
                session.id,
                assistant_turn.id,
                "post_turn_extraction",
                "Post-turn extraction",
                extraction.model_dump(),
                "succeeded",
                {"provider": self.llm.provider_name},
            )
            artifact_ids.append(extraction_artifact["id"])
            patch = await self.patch_builder.build(workspace_id, session.id, user_turn.id, extraction)
            validation = self.patch_validator.validate(patch, extraction.forbidden_user_state_claims)
            validation_artifact = await self.repo.create_artifact(
                workspace_id,
                session.id,
                assistant_turn.id,
                "map_patch_validation",
                "Map patch validation",
                validation.model_dump(mode="json"),
                "succeeded" if validation.valid else "failed",
                {},
            )
            artifact_ids.append(validation_artifact["id"])
            patch_out, counters = await self.map_writer.persist(workspace_id, session.id, user_turn.id, patch, validation)
            patch_artifact = await self.repo.create_artifact(
                workspace_id,
                session.id,
                assistant_turn.id,
                "map_patch",
                "Map patch",
                {"patch_id": patch_out.id, "status": patch_out.status, "counters": counters, "patch": patch_out.patch},
                patch_out.status,
                {},
            )
            artifact_ids.append(patch_artifact["id"])
            patch_ids.append(patch_out.id)
            map_ids.extend(patch_out.target_map_ids)
            processing_message = patch_out.status
        except Exception as exc:
            details = {"error": getattr(exc, "message", str(exc)), "type": type(exc).__name__}
            if isinstance(exc, AppError):
                details = {"error": exc.message, "code": exc.code, "details": exc.details or {}}
            failed_artifact = await self.repo.create_artifact(
                workspace_id,
                session.id,
                assistant_turn.id,
                "structure_update_failed",
                "Structure update failed",
                details,
                "failed",
                {"provider": self.llm.provider_name},
            )
            artifact_ids.append(failed_artifact["id"])
            processing_message = "structure update failed"
        refreshed = await self.repo.get_session(session.id)
        return TurnResponse(
            session=refreshed or session,
            user_turn=user_turn,
            assistant_turn=assistant_turn,
            processing_state=ProcessingState(
                status="succeeded",
                steps=[
                    "intake",
                    "topic_route",
                    "research_detection",
                    "discussion",
                    "extraction",
                    "patch_validation",
                    "patch_persistence",
                ],
                message=processing_message,
            ),
            artifacts_summary=TurnArtifactsSummary(
                artifact_ids=artifact_ids,
                patch_ids=patch_ids,
                source_ids=[source["id"] for source in source_cards if "id" in source],
                map_ids=map_ids,
            ),
        )
