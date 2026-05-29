from __future__ import annotations

from atlas_api.db.repositories import Repository
from atlas_api.errors import AppError
from atlas_api.llm.base import LlmAdapter
from atlas_api.models.common import ProcessingState
from atlas_api.models.patches import PostTurnExtraction
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
from atlas_api.services.learning_projection import LearningProjectionService
from atlas_api.services.source_broker import SourceBroker
from atlas_api.services.technical_signal_extractor import TechnicalSignalExtractor
from atlas_api.services.topic_router import TopicRouter
from atlas_api.services.turn_intake import TurnIntakeService
from atlas_api.util.text import estimate_tokens, first_sentence_title


OPERATIONAL_SUPPORT_PHRASES = [
    "can access my site",
    "access my website",
    "access the internet",
    "web browsing",
    "web search",
    "search capability",
    "can't resolve websites",
    "cannot resolve websites",
    "port 8787",
    "port 8788",
    "phone url",
    "hosted on",
    "running server",
    "service worker",
    "pwa",
    "latest built bundle",
    "playwright",
    "screenshot",
    "codex cli",
    "oauth",
    "fake adapter",
    "contractfixture",
    "read-only environment",
    "app capability",
    "app capabilities",
]

DOMAIN_LEARNING_PHRASES = [
    "substratecad",
    "substrate cad",
    "analog compute",
    "compute-in-memory",
    "compute in memory",
    "adc",
    "dac",
    "pcb",
    "trace impedance",
    "signal integrity",
    "soc",
    "package substrate",
    "interconnect",
    "geometry kernel",
    "fabrication",
    "materials",
    "hardware",
    "chip",
]


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
        self.technical_extractor = TechnicalSignalExtractor()
        self.learning_projection = LearningProjectionService(repo)
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
        if session.title in {"New Thought", "New chat"}:
            await self.repo.update_session(session.id, {"title": first_sentence_title(normalized)})

        maps = await self.repo.list_maps(workspace_id)
        route = await self.topic_router.route(normalized, [item.title for item in maps[:50]])
        topics = [segment.get("candidate_topic") for segment in route.get("segments", []) if segment.get("candidate_topic")]
        existing_labels = await self.repo.list_concept_labels(workspace_id)
        fast_extraction = self.technical_extractor.extract(normalized, existing_labels)
        pending_delta_artifact = await self.repo.create_artifact(
            workspace_id,
            session.id,
            user_turn.id,
            "pending_learning_delta",
            "Pending learning delta",
            fast_extraction.model_dump(),
            "pending",
            {"extractor": "deterministic"},
        )
        for source_need in fast_extraction.source_needs:
            await self.repo.create_research_task(
                workspace_id,
                session.id,
                user_turn.id,
                source_need,
                task_type="source_need",
                status="source_needed",
                priority=0.65,
                metadata={"provenance": [{"turn_id": user_turn.id, "session_id": session.id, "speaker": "user", "note": "Fast technical signal extraction."}]},
            )
        research_need = await self.research_detector.detect(normalized, topics)
        for source_need in research_need.get("source_needs", []):
            await self.repo.create_research_task(
                workspace_id,
                session.id,
                user_turn.id,
                f"Need sources for {source_need}",
                task_type="source_need",
                status="source_needed",
                priority=0.5,
                metadata={"provenance": [{"turn_id": user_turn.id, "session_id": session.id, "speaker": "user", "note": "Research need detector."}]},
            )
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
        memory_capsule = await self.learning_projection.retrieval_capsule(workspace_id, normalized)
        discussion_context = self.context_broker.build_discussion_context(normalized, recent_turns, mode, memory_capsule)
        artifact_ids: list[str] = [pending_delta_artifact["id"]]
        try:
            reply = await self.conversational_agent.reply(discussion_context, mode)
        except AppError as exc:
            model_error = {"code": exc.code, "message": exc.message, "details": exc.details or {}}
            failed_artifact = await self.repo.create_artifact(
                workspace_id,
                session.id,
                user_turn.id,
                "model_error",
                "Model error",
                model_error,
                "failed",
                {"provider": self.llm.provider_name},
            )
            artifact_ids.append(failed_artifact["id"])
            refreshed = await self.repo.get_session(session.id)
            return TurnResponse(
                session=refreshed or session,
                user_turn=user_turn,
                assistant_turn=None,
                model_error=model_error,
                learning_delta_summary=self._learning_delta_summary(fast_extraction),
                processing_state=ProcessingState(
                    status="failed",
                    steps=["intake", "fast_extraction", "research_detection", "selective_retrieval", "discussion"],
                    message="model error; user turn preserved",
                ),
                artifacts_summary=TurnArtifactsSummary(
                    artifact_ids=artifact_ids,
                    patch_ids=[],
                    source_ids=[source["id"] for source in source_cards if "id" in source],
                    map_ids=[],
                ),
            )
        assistant_turn = await self.repo.create_turn(
            session.id,
            "assistant",
            reply.message,
            None,
            estimate_tokens(reply.message),
            {"mode": mode, "source_ids_used": reply.source_ids_used, "uncertainty_notes": reply.uncertainty_notes},
        )

        patch_ids: list[str] = []
        map_ids: list[str] = []
        processing_message = "updated"
        try:
            extraction_context = self.context_broker.build_extraction_context(normalized, reply.message, source_cards)
            try:
                post_extraction = await self.extractor.extract(extraction_context)
            except Exception as exc:
                details = {"error": getattr(exc, "message", str(exc)), "type": type(exc).__name__}
                if isinstance(exc, AppError):
                    details = {"error": exc.message, "code": exc.code, "details": exc.details or {}}
                failed_extraction_artifact = await self.repo.create_artifact(
                    workspace_id,
                    session.id,
                    assistant_turn.id,
                    "post_turn_extraction_failed",
                    "Post-turn extraction failed",
                    details,
                    "failed",
                    {"provider": self.llm.provider_name, "fallback": "fast_extraction"},
                )
                artifact_ids.append(failed_extraction_artifact["id"])
                post_extraction = type(fast_extraction)(notes="Post-turn extraction failed; using deterministic fast extraction only.")
            extraction = self.technical_extractor.merge(fast_extraction, post_extraction)
            extraction = self._remove_operational_support_pollution(normalized, extraction)
            for source_need in extraction.source_needs:
                if source_need not in fast_extraction.source_needs:
                    await self.repo.create_research_task(
                        workspace_id,
                        session.id,
                        user_turn.id,
                        source_need,
                        task_type="source_need",
                        status="source_needed",
                        priority=0.55,
                        metadata={"provenance": [{"turn_id": user_turn.id, "session_id": session.id, "speaker": "user", "note": "Merged post-turn extraction."}]},
                    )
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
                    "fast_extraction",
                    "topic_route",
                    "research_detection",
                    "selective_retrieval",
                    "discussion",
                    "extraction",
                    "patch_validation",
                    "patch_persistence",
                ],
                message=processing_message,
            ),
            learning_delta_summary=self._learning_delta_summary(fast_extraction),
            artifacts_summary=TurnArtifactsSummary(
                artifact_ids=artifact_ids,
                patch_ids=patch_ids,
                source_ids=[source["id"] for source in source_cards if "id" in source],
                map_ids=map_ids,
            ),
        )

    def _learning_delta_summary(self, extraction) -> dict:
        return {
            "concepts": [node.label for node in extraction.node_candidates],
            "claims": [claim.text for claim in extraction.claims],
            "questions": [question.question for question in extraction.open_questions],
            "tensions": [tension.get("title") for tension in extraction.tensions],
            "bridges": [f"{bridge.from_label} -> {bridge.to_label}" for bridge in extraction.latent_bridges],
            "source_needs": extraction.source_needs,
        }

    def _remove_operational_support_pollution(self, user_text: str, extraction: PostTurnExtraction) -> PostTurnExtraction:
        haystack = self._extraction_text(user_text, extraction)
        has_operational_signal = any(phrase in haystack for phrase in OPERATIONAL_SUPPORT_PHRASES)
        if not has_operational_signal:
            return extraction
        has_domain_signal = any(phrase in haystack for phrase in DOMAIN_LEARNING_PHRASES)
        if not has_domain_signal:
            return PostTurnExtraction(notes="Operational app/support turn excluded from global learning topology.")

        return extraction.model_copy(
            update={
                "topics": [topic for topic in extraction.topics if not self._is_operational_text(topic)],
                "claims": [claim for claim in extraction.claims if not self._is_operational_text(claim.text)],
                "node_candidates": [node for node in extraction.node_candidates if not self._is_operational_text(f"{node.label} {node.description or ''}")],
                "edge_candidates": [
                    edge
                    for edge in extraction.edge_candidates
                    if not self._is_operational_text(f"{edge.from_label} {edge.to_label} {edge.label or ''} {edge.description or ''}")
                ],
                "open_questions": [question for question in extraction.open_questions if not self._is_operational_text(question.question)],
                "tensions": [
                    tension
                    for tension in extraction.tensions
                    if not self._is_operational_text(f"{tension.get('title', '')} {tension.get('description', '')}")
                ],
                "analogies": [
                    analogy
                    for analogy in extraction.analogies
                    if not self._is_operational_text(f"{analogy.source_concept} {analogy.target_concept} {analogy.useful_because or ''}")
                ],
                "latent_bridges": [
                    bridge
                    for bridge in extraction.latent_bridges
                    if not self._is_operational_text(f"{bridge.from_label} {bridge.to_label} {bridge.reason}")
                ],
                "source_needs": [need for need in extraction.source_needs if not self._is_operational_text(need)],
                "notes": f"{extraction.notes} Operational app/support candidates removed from learning topology.".strip(),
            }
        )

    def _is_operational_text(self, text: str) -> bool:
        lower = text.lower()
        return any(phrase in lower for phrase in OPERATIONAL_SUPPORT_PHRASES)

    def _extraction_text(self, user_text: str, extraction: PostTurnExtraction) -> str:
        pieces = [user_text, *extraction.topics, *[node.label for node in extraction.node_candidates], *[node.description or "" for node in extraction.node_candidates]]
        pieces.extend(claim.text for claim in extraction.claims)
        pieces.extend(question.question for question in extraction.open_questions)
        pieces.extend(str(tension.get("title", "")) for tension in extraction.tensions)
        pieces.extend(str(tension.get("description", "")) for tension in extraction.tensions)
        pieces.extend(bridge.reason for bridge in extraction.latent_bridges)
        return "\n".join(pieces).lower()
