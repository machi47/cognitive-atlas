from __future__ import annotations

from typing import Any

from atlas_api.llm.base import LlmAdapter
from atlas_api.models.llm import LlmHealth, LlmJsonRequest, LlmJsonResult, LlmTextRequest, LlmTextResult
from atlas_api.util.text import keywords_title, normalize_whitespace


class FakeLlmAdapter(LlmAdapter):
    provider_name = "fake"
    supports_web_search = False
    supports_schema_output = True

    async def complete_text(self, request: LlmTextRequest) -> LlmTextResult:
        return LlmTextResult(text=self._discussion_message(request.prompt), provider_name=self.provider_name)

    async def complete_json(self, request: LlmJsonRequest, schema: dict[str, Any] | None = None) -> LlmJsonResult:
        task = request.task.lower()
        prompt = request.prompt
        if "discussion" in task:
            data = {
                "message": self._discussion_message(prompt),
                "response_mode": request.metadata.get("mode", "discuss"),
                "source_ids_used": [],
                "suggested_followups": self._followups(prompt),
                "uncertainty_notes": [],
                "should_research_more": self._needs_research(prompt),
            }
        elif "extraction" in task:
            data = self._extraction(prompt)
        elif "topic" in task:
            topic = keywords_title(prompt)
            data = {
                "segments": [{"text": normalize_whitespace(prompt)[:500], "candidate_topic": topic, "confidence": 0.72}],
                "candidate_new_maps": [{"title": topic, "parent_hint": None, "reason": "Deterministic keyword route.", "confidence": 0.7}],
                "matched_map_ids": [],
                "notes": "Fake deterministic topic route.",
            }
        elif "research" in task:
            data = {
                "needs_research": self._needs_research(prompt),
                "freshness_required": self._needs_research(prompt),
                "reasons": ["Detected frontier/current technical topic." if self._needs_research(prompt) else "No explicit freshness need detected."],
                "query_intents": [keywords_title(prompt)],
                "source_types": ["openalex", "crossref", "arxiv"],
                "priority": 0.7 if self._needs_research(prompt) else 0.1,
            }
        else:
            data = {}
        return LlmJsonResult(data=data, provider_name=self.provider_name, raw={"task": request.task})

    async def healthcheck(self) -> LlmHealth:
        return LlmHealth(provider_name=self.provider_name, available=True, message="Fake LLM test mode")

    def _discussion_message(self, prompt: str) -> str:
        message = self._current_message(prompt)
        lower = message.lower()
        if "substratecad" in lower or "substrate cad" in lower:
            return (
                "Yeah - for substrateCAD from first principles, the first move is defining what substrate means: PCB substrate, IC/package substrate, "
                "or a broader fabrication-aware CAD system. The foundation stack is roughly: a CAD/geometry kernel, a substrate object schema, layers, "
                "materials, vias, traces/features, fabrication and process constraints, electrical/physical constraints, manufacturability rules, and "
                "simulation/verification. I would start by defining the minimum object system: layers, materials, features, vias, constraints, and process rules."
            )
        if "analog" in lower or "compute in memory" in lower or "compute-in-memory" in lower:
            return (
                "Yes - the link is data movement. Compute-in-memory tries to reduce the energy and latency of moving operands back and forth, "
                "while analog compute can make dense MAC-like work cheap near the data. The catch is exactly the ADC/DAC boundary: if conversion, "
                "control, calibration, or precision overhead happens too often, it can erase the win. The useful question is where the analog block sits "
                "so conversion overhead is paid rarely enough to matter."
            )
        if "pcb" in lower or "trace impedance" in lower or "soc interconnect" in lower or "package substrate" in lower:
            return (
                "That relation is plausible, but I would keep it tentative. PCB trace impedance, package substrate interconnects, and SoC interconnects all sit in "
                "the same broad problem family: geometry plus materials plus constrained physical signal behavior. The bridge is useful for substrateCAD because a "
                "fabrication-aware CAD system needs to represent layered media, conductor geometry, material stackups, and verification rules without assuming the "
                "PCB, package, and on-chip cases are identical."
            )
        if "agent" in lower or "conversation plane" in lower or "map forest" in lower:
            return (
                "The clean split is: conversation stays narrow and useful, while extraction workers quietly turn the residue into map updates, questions, "
                "claims, and bridges. That avoids making the chat agent carry the whole atlas in its head. The map forest then becomes a memory substrate, "
                "not the thing you have to stare at every time you think."
            )
        topic = keywords_title(message)
        return (
            f"I would start with {topic}. The useful move is to answer the concrete thing you asked, then keep track of the uncertainty and next question in the background."
        )

    def _followups(self, prompt: str) -> list[str]:
        lower = self._current_message(prompt).lower()
        if "analog" in lower:
            return ["Check conversion overhead assumptions", "Map data movement constraints"]
        if "agent" in lower:
            return ["Inspect conversation versus infrastructure split", "Map memory boundaries"]
        return ["Turn this into a map", "Ask for a sharper critique"]

    def _needs_research(self, prompt: str) -> bool:
        lower = self._current_message(prompt).lower()
        frontier_terms = [
            "current",
            "latest",
            "recent",
            "paper",
            "research",
            "analog compute",
            "compute-in-memory",
            "chiplet",
            "hbm",
            "advanced packaging",
            "sram-cim",
            "rram",
            "photonic",
        ]
        return any(term in lower for term in frontier_terms)

    def _extraction(self, prompt: str) -> dict[str, Any]:
        lower = self._current_message(prompt).lower()
        if "substratecad" in lower or "substrate cad" in lower:
            return {
                "topics": ["substrateCAD", "fabrication-aware CAD", "geometry kernel"],
                "claims": [
                    {
                        "text": "Building substrateCAD from first principles requires a geometry/CAD kernel plus a substrate/process object model.",
                        "claim_type": "learning_goal",
                        "epistemic_status": "user_asserted",
                        "confidence": 0.72,
                        "source_ids": [],
                    }
                ],
                "node_candidates": [
                    {"label": "substrateCAD", "description": "A CAD system for substrate design grounded in fabrication and physical constraints.", "node_type": "project_goal", "epistemic_status": "user_asserted", "confidence": 0.8, "local_salience": 0.9, "global_salience": 0.6, "novelty_score": 0.6, "bridge_potential": 0.8},
                    {"label": "geometry kernel", "description": "Core geometric representation and operations for CAD entities.", "node_type": "foundation", "epistemic_status": "assistant_inferred", "confidence": 0.7, "local_salience": 0.8, "global_salience": 0.5, "novelty_score": 0.4, "bridge_potential": 0.5},
                    {"label": "fabrication process constraints", "description": "Rules imposed by manufacturable layers, materials, vias, traces, and process limits.", "node_type": "constraint", "epistemic_status": "assistant_inferred", "confidence": 0.7, "local_salience": 0.8, "global_salience": 0.6, "novelty_score": 0.5, "bridge_potential": 0.8},
                ],
                "edge_candidates": [
                    {"from_label": "fabrication process constraints", "to_label": "substrateCAD", "relation_type": "constrains", "label": "constrains", "description": "Process limits constrain valid substrateCAD geometry and layout.", "epistemic_status": "assistant_inferred", "confidence": 0.68, "salience": 0.8}
                ],
                "open_questions": [
                    {"question": "Does substrate mean PCB substrate, IC/package substrate, or a broader fabrication-aware CAD system?", "status": "open", "priority": 0.9}
                ],
                "tensions": [],
                "analogies": [],
                "latent_bridges": [],
                "source_needs": ["Foundational CAD kernels and fabrication/process-rule references."],
                "forbidden_user_state_claims": [],
                "notes": "Fake extraction for test-only substrateCAD flow.",
            }
        if "analog" in lower or "compute in memory" in lower or "compute-in-memory" in lower:
            return {
                "topics": ["analog compute", "compute-in-memory", "SoC design"],
                "claims": [
                    {
                        "text": "Analog compute and compute-in-memory are connected to SoC design through data movement costs.",
                        "claim_type": "user_claim",
                        "epistemic_status": "user_asserted",
                        "confidence": 0.78,
                        "source_ids": [],
                    }
                ],
                "node_candidates": [
                    {"label": "analog compute", "description": "Mixed-signal compute that performs operations in analog domains.", "node_type": "concept", "epistemic_status": "user_asserted", "confidence": 0.78, "local_salience": 0.8, "global_salience": 0.5, "novelty_score": 0.5, "bridge_potential": 0.8},
                    {"label": "compute-in-memory", "description": "Architectures that reduce operand movement by computing near or inside memory.", "node_type": "concept", "epistemic_status": "user_asserted", "confidence": 0.78, "local_salience": 0.8, "global_salience": 0.5, "novelty_score": 0.4, "bridge_potential": 0.8},
                    {"label": "ADC/DAC overhead", "description": "Conversion overhead that can dominate mixed-signal accelerator efficiency.", "node_type": "constraint", "epistemic_status": "user_questioned", "confidence": 0.74, "local_salience": 0.9, "global_salience": 0.6, "novelty_score": 0.6, "bridge_potential": 0.9},
                    {"label": "data movement cost", "description": "Energy and latency cost of moving operands through the memory hierarchy.", "node_type": "constraint", "epistemic_status": "assistant_claimed", "confidence": 0.72, "local_salience": 0.8, "global_salience": 0.6, "novelty_score": 0.4, "bridge_potential": 0.8},
                ],
                "edge_candidates": [
                    {"from_label": "data movement cost", "to_label": "compute-in-memory", "relation_type": "motivates", "label": "motivates", "description": "Data movement cost motivates compute-in-memory designs.", "epistemic_status": "assistant_inferred", "confidence": 0.68, "salience": 0.7},
                    {"from_label": "ADC/DAC overhead", "to_label": "analog compute", "relation_type": "constrains", "label": "constrains", "description": "Conversion overhead can erase analog compute efficiency gains.", "epistemic_status": "user_questioned", "confidence": 0.72, "salience": 0.9},
                    {"from_label": "ADC/DAC overhead", "to_label": "compute-in-memory", "relation_type": "constrains", "label": "constrains", "description": "Interface conversion can constrain mixed-signal CIM system value.", "epistemic_status": "speculative", "confidence": 0.62, "salience": 0.8},
                ],
                "open_questions": [
                    {"question": "When does conversion overhead erase compute-in-memory or analog compute benefit?", "status": "open", "priority": 0.9}
                ],
                "tensions": [],
                "analogies": [],
                "latent_bridges": [
                    {"from_label": "ADC/DAC overhead", "to_label": "data movement cost", "bridge_type": "bridges_to", "reason": "Both are system-level overheads that can dominate local compute efficiency.", "confidence": 0.62, "status": "suggested", "discovered_by": "deterministic", "evidence_artifact_ids": []}
                ],
                "source_needs": ["Recent surveys on analog compute and compute-in-memory conversion overhead."],
                "forbidden_user_state_claims": [],
                "notes": "Fake extraction preserves user uncertainty instead of inferring belief.",
            }
        if "agent" in lower or "conversation plane" in lower or "map forest" in lower:
            return {
                "topics": ["learning agent architecture", "conversation UX", "map forest"],
                "claims": [
                    {"text": "Conversation output should stay separate from backend extraction artifacts.", "claim_type": "design_principle", "epistemic_status": "user_asserted", "confidence": 0.76, "source_ids": []}
                ],
                "node_candidates": [
                    {"label": "conversation plane", "description": "The compact user-facing discussion surface.", "node_type": "system_plane", "epistemic_status": "user_asserted", "confidence": 0.8, "local_salience": 0.8, "global_salience": 0.7, "novelty_score": 0.4, "bridge_potential": 0.7},
                    {"label": "backend extraction", "description": "Worker layer that emits structured residue from conversation.", "node_type": "system_plane", "epistemic_status": "user_asserted", "confidence": 0.8, "local_salience": 0.7, "global_salience": 0.7, "novelty_score": 0.4, "bridge_potential": 0.7},
                    {"label": "map forest", "description": "Multiple evolving maps instead of one giant graph.", "node_type": "memory_model", "epistemic_status": "user_asserted", "confidence": 0.8, "local_salience": 0.8, "global_salience": 0.8, "novelty_score": 0.5, "bridge_potential": 0.8},
                ],
                "edge_candidates": [
                    {"from_label": "backend extraction", "to_label": "map forest", "relation_type": "updates", "label": "updates", "description": "Extraction emits patches for the map forest.", "epistemic_status": "assistant_inferred", "confidence": 0.7, "salience": 0.7},
                    {"from_label": "conversation plane", "to_label": "backend extraction", "relation_type": "separates_from", "label": "separates from", "description": "The clean answer should not expose raw artifacts.", "epistemic_status": "user_asserted", "confidence": 0.72, "salience": 0.8},
                ],
                "open_questions": [{"question": "Which artifacts are useful enough to surface without overwhelming the conversation?", "status": "open", "priority": 0.6}],
                "tensions": [],
                "analogies": [],
                "latent_bridges": [],
                "source_needs": [],
                "forbidden_user_state_claims": [],
                "notes": "Fake extraction for agent architecture.",
            }
        topic = keywords_title(prompt)
        return {
            "topics": [topic],
            "claims": [{"text": normalize_whitespace(prompt)[:240], "claim_type": "raw_thought", "epistemic_status": "user_asserted", "confidence": 0.45, "source_ids": []}],
            "node_candidates": [{"label": topic, "description": "Topic inferred from the current turn.", "node_type": "concept", "epistemic_status": "unverified", "confidence": 0.45, "local_salience": 0.5, "global_salience": 0.2, "novelty_score": 0.4, "bridge_potential": 0.3}],
            "edge_candidates": [],
            "open_questions": [{"question": f"What is the sharpest unresolved question inside {topic}?", "status": "open", "priority": 0.4}],
            "tensions": [],
            "analogies": [],
            "latent_bridges": [],
            "source_needs": [],
            "forbidden_user_state_claims": [],
            "notes": "Generic fake extraction.",
        }

    def _current_message(self, prompt: str) -> str:
        marker = "Current user message:"
        if marker in prompt:
            return prompt.split(marker, 1)[1].strip()
        marker = "User:"
        if marker in prompt:
            value = prompt.split(marker, 1)[1]
            for next_marker in ["\nResearch Partner:", "\nAssistant:"]:
                value = value.split(next_marker, 1)[0]
            return value.strip()
        return prompt
