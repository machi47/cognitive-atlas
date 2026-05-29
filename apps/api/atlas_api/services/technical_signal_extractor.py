from __future__ import annotations

from collections.abc import Iterable

from atlas_api.models.patches import (
    ClaimCandidate,
    EdgeCandidate,
    LatentBridgeCandidate,
    NodeCandidate,
    OpenQuestionCandidate,
    PostTurnExtraction,
)


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


class TechnicalSignalExtractor:
    """Fast deterministic extraction for high-signal technical learning turns.

    This is intentionally narrow. It creates structured candidates for concepts,
    constraints, bridges, source needs, and questions without presenting them as
    model-generated certainty.
    """

    def extract(self, text: str, existing_labels: list[str] | None = None) -> PostTurnExtraction:
        lower = text.lower()
        existing = {label.lower() for label in existing_labels or []}
        extraction = PostTurnExtraction(notes="Deterministic technical signal extraction from user turn.")

        if _contains_any(lower, ["substratecad", "substrate cad"]):
            self._add_substratecad(extraction)

        if self._looks_like_physical_interconnect(lower):
            self._add_physical_signal_integrity(extraction, existing)

        if _contains_any(lower, ["analog compute", "analog computing", "compute-in-memory", "compute in memory", "adc", "dac", "cim"]):
            self._add_analog_cim(extraction)

        return self._dedupe(extraction)

    def merge(self, primary: PostTurnExtraction, secondary: PostTurnExtraction) -> PostTurnExtraction:
        merged = PostTurnExtraction(
            topics=[*primary.topics, *secondary.topics],
            claims=[*primary.claims, *secondary.claims],
            node_candidates=[*primary.node_candidates, *secondary.node_candidates],
            edge_candidates=[*primary.edge_candidates, *secondary.edge_candidates],
            open_questions=[*primary.open_questions, *secondary.open_questions],
            tensions=[*primary.tensions, *secondary.tensions],
            analogies=[*primary.analogies, *secondary.analogies],
            latent_bridges=[*primary.latent_bridges, *secondary.latent_bridges],
            source_needs=[*primary.source_needs, *secondary.source_needs],
            forbidden_user_state_claims=[*primary.forbidden_user_state_claims, *secondary.forbidden_user_state_claims],
            notes="Merged deterministic and post-turn extraction.",
        )
        return self._dedupe(merged)

    def _add_substratecad(self, extraction: PostTurnExtraction) -> None:
        extraction.topics.extend(["substrateCAD", "fabrication-aware CAD", "geometry kernel"])
        extraction.claims.append(
            ClaimCandidate(
                text="The user stated substrateCAD as a first-principles learning and build goal.",
                claim_type="learning_goal",
                epistemic_status="user_stated",
                confidence=0.86,
            )
        )
        extraction.node_candidates.extend(
            [
                NodeCandidate(
                    label="substrateCAD",
                    description="A project goal to build a fabrication-aware substrate CAD system from first principles.",
                    node_type="project_goal",
                    epistemic_status="user_stated",
                    confidence=0.9,
                    local_salience=0.95,
                    global_salience=0.75,
                    novelty_score=0.6,
                    bridge_potential=0.85,
                ),
                NodeCandidate(
                    label="geometry kernel",
                    description="The geometric representation and operation layer needed for CAD entities.",
                    node_type="foundation",
                    epistemic_status="assistant_inferred",
                    confidence=0.78,
                    local_salience=0.86,
                    global_salience=0.55,
                    bridge_potential=0.55,
                ),
                NodeCandidate(
                    label="substrate object model",
                    description="Objects for layers, materials, vias, traces, features, and stackups.",
                    node_type="foundation",
                    epistemic_status="assistant_inferred",
                    confidence=0.78,
                    local_salience=0.84,
                    global_salience=0.55,
                    bridge_potential=0.72,
                ),
                NodeCandidate(
                    label="layers/features/vias/traces/materials",
                    description="The concrete substrate primitives and material stack needed by the object model.",
                    node_type="concept_cluster",
                    epistemic_status="assistant_inferred",
                    confidence=0.74,
                    local_salience=0.8,
                    global_salience=0.52,
                    bridge_potential=0.78,
                ),
                NodeCandidate(
                    label="fabrication/process constraints",
                    description="Process limits and manufacturing rules that constrain valid geometry.",
                    node_type="constraint",
                    epistemic_status="assistant_inferred",
                    confidence=0.8,
                    local_salience=0.86,
                    global_salience=0.66,
                    bridge_potential=0.86,
                ),
                NodeCandidate(
                    label="electrical/physical constraints",
                    description="Electrical and physical behavior constraints such as impedance, parasitics, and signal propagation.",
                    node_type="constraint",
                    epistemic_status="assistant_inferred",
                    confidence=0.75,
                    local_salience=0.78,
                    global_salience=0.62,
                    bridge_potential=0.88,
                ),
                NodeCandidate(
                    label="simulation/verification",
                    description="Checking geometry and physics against design intent and constraints.",
                    node_type="foundation",
                    epistemic_status="assistant_inferred",
                    confidence=0.72,
                    local_salience=0.72,
                    global_salience=0.48,
                ),
                NodeCandidate(
                    label="manufacturability rules",
                    description="Rules that distinguish drawable geometry from buildable geometry.",
                    node_type="constraint",
                    epistemic_status="assistant_inferred",
                    confidence=0.78,
                    local_salience=0.8,
                    global_salience=0.58,
                    bridge_potential=0.8,
                ),
            ]
        )
        extraction.edge_candidates.extend(
            [
                EdgeCandidate(from_label="geometry kernel", to_label="substrateCAD", relation_type="foundation_for", label="foundation for", epistemic_status="assistant_inferred", confidence=0.76, salience=0.84),
                EdgeCandidate(from_label="substrate object model", to_label="substrateCAD", relation_type="foundation_for", label="foundation for", epistemic_status="assistant_inferred", confidence=0.78, salience=0.84),
                EdgeCandidate(from_label="layers/features/vias/traces/materials", to_label="substrate object model", relation_type="composes", label="composes", epistemic_status="assistant_inferred", confidence=0.72, salience=0.78),
                EdgeCandidate(from_label="fabrication/process constraints", to_label="substrateCAD", relation_type="constrains", label="constrains", epistemic_status="assistant_inferred", confidence=0.78, salience=0.86),
                EdgeCandidate(from_label="electrical/physical constraints", to_label="substrateCAD", relation_type="constrains", label="constrains", epistemic_status="assistant_inferred", confidence=0.72, salience=0.76),
                EdgeCandidate(from_label="simulation/verification", to_label="substrateCAD", relation_type="validates", label="validates", epistemic_status="assistant_inferred", confidence=0.68, salience=0.7),
                EdgeCandidate(from_label="manufacturability rules", to_label="fabrication/process constraints", relation_type="part_of", label="part of", epistemic_status="assistant_inferred", confidence=0.7, salience=0.74),
            ]
        )
        extraction.open_questions.extend(
            [
                OpenQuestionCandidate(question="Does substrate mean PCB, IC/package substrate, or a broader fabrication-aware CAD target?", priority=0.92),
                OpenQuestionCandidate(question="Which minimal geometry kernel operations are required before substrate-specific objects can exist?", priority=0.72),
                OpenQuestionCandidate(question="Which fabrication/process constraints should be first-class in substrateCAD rather than external checks?", priority=0.78),
            ]
        )
        extraction.source_needs.extend(
            [
                "Foundational references on CAD geometry kernels for constraint-aware layout.",
                "References on PCB/package substrate fabrication rules, layer stackups, vias, traces, and manufacturability constraints.",
            ]
        )

    def _looks_like_physical_interconnect(self, lower: str) -> bool:
        return (
            _contains_any(lower, ["pcb", "trace impedance", "controlled impedance", "signal integrity"])
            or _contains_any(lower, ["soc interconnect", "on-chip interconnect", "package substrate", "package interconnect"])
            or ("substrate" in lower and _contains_any(lower, ["interconnect", "signal", "impedance"]))
        )

    def _add_physical_signal_integrity(self, extraction: PostTurnExtraction, existing: set[str]) -> None:
        extraction.topics.extend(["physical signal integrity", "interconnect constraints", "manufacturable layered media"])
        extraction.claims.append(
            ClaimCandidate(
                text="The user suggested a tentative relation between trace impedance, package substrates, and SoC interconnects through physical signal integrity.",
                claim_type="user_hypothesis",
                epistemic_status="user_stated",
                confidence=0.78,
            )
        )
        extraction.node_candidates.extend(
            [
                NodeCandidate(label="PCB trace impedance", description="Impedance behavior of PCB traces shaped by geometry, dielectric materials, and stackup.", node_type="concept", epistemic_status="user_stated", confidence=0.82, local_salience=0.86, global_salience=0.58, bridge_potential=0.9),
                NodeCandidate(label="SoC interconnects", description="On-chip communication wires and networks constrained by physical signaling and integration limits.", node_type="concept", epistemic_status="user_stated", confidence=0.78, local_salience=0.78, global_salience=0.55, bridge_potential=0.86),
                NodeCandidate(label="package substrate interconnect", description="Interconnect structures in package substrates bridging die, board, and system-level signaling.", node_type="concept", epistemic_status="user_stated", confidence=0.8, local_salience=0.82, global_salience=0.6, bridge_potential=0.9),
                NodeCandidate(label="physical signal integrity", description="Cross-domain abstraction for signal behavior through geometry, materials, and constrained media.", node_type="cross_domain_abstraction", epistemic_status="assistant_inferred", confidence=0.72, local_salience=0.88, global_salience=0.7, bridge_potential=0.95),
                NodeCandidate(label="manufacturable layered media", description="The shared substrate idea of patterned conductive and dielectric layers under process constraints.", node_type="cross_domain_abstraction", epistemic_status="assistant_inferred", confidence=0.7, local_salience=0.78, global_salience=0.64, bridge_potential=0.9),
                NodeCandidate(label="SoC physical signaling constraints", description="Physical limits on on-chip signaling, interconnect parasitics, timing, and integrity.", node_type="constraint", epistemic_status="assistant_inferred", confidence=0.68, local_salience=0.72, global_salience=0.56, bridge_potential=0.84),
            ]
        )
        extraction.edge_candidates.extend(
            [
                EdgeCandidate(from_label="PCB trace impedance", to_label="physical signal integrity", relation_type="instance_of", label="instance of", epistemic_status="user_stated", confidence=0.72, salience=0.82),
                EdgeCandidate(from_label="package substrate interconnect", to_label="physical signal integrity", relation_type="instance_of", label="instance of", epistemic_status="user_stated", confidence=0.7, salience=0.82),
                EdgeCandidate(from_label="SoC interconnects", to_label="SoC physical signaling constraints", relation_type="constrained_by", label="constrained by", epistemic_status="assistant_inferred", confidence=0.66, salience=0.74),
                EdgeCandidate(from_label="SoC physical signaling constraints", to_label="physical signal integrity", relation_type="instance_of", label="instance of", epistemic_status="speculative", confidence=0.62, salience=0.68),
                EdgeCandidate(from_label="manufacturable layered media", to_label="package substrate interconnect", relation_type="shapes", label="shapes", epistemic_status="assistant_inferred", confidence=0.66, salience=0.7),
            ]
        )
        extraction.latent_bridges.append(
            LatentBridgeCandidate(
                from_label="PCB trace impedance",
                to_label="SoC physical signaling constraints",
                reason="Tentative bridge: PCB trace impedance -> package substrate interconnect -> SoC physical signaling constraints, because all involve geometry, materials, and physical signal behavior in constrained media.",
                confidence=0.62,
                status="suggested",
                metadata={"path": ["PCB trace impedance", "package substrate interconnect", "SoC physical signaling constraints"]},
            )
        )
        if "substratecad" in existing:
            extraction.latent_bridges.append(
                LatentBridgeCandidate(
                    from_label="physical signal integrity",
                    to_label="substrateCAD",
                    reason="Physical signal integrity may be a foundation for substrateCAD because substrateCAD needs geometry/material/process models that affect signal behavior.",
                    confidence=0.58,
                    status="suggested",
                    metadata={"linked_project": "substrateCAD"},
                )
            )
        extraction.open_questions.append(
            OpenQuestionCandidate(
                question="Which parts of PCB controlled impedance transfer cleanly to package substrate and SoC interconnect reasoning, and where does the analogy break?",
                priority=0.78,
            )
        )
        extraction.source_needs.append("Technical references comparing PCB trace impedance, package substrate interconnects, and SoC interconnect physical signaling constraints.")

    def _add_analog_cim(self, extraction: PostTurnExtraction) -> None:
        extraction.topics.extend(["analog compute", "compute-in-memory", "ADC/DAC overhead"])
        extraction.claims.append(
            ClaimCandidate(
                text="The user is worried that ADC/DAC conversion overhead may erase the benefit of analog compute or compute-in-memory.",
                claim_type="user_tension",
                epistemic_status="user_stated",
                confidence=0.86,
            )
        )
        extraction.node_candidates.extend(
            [
                NodeCandidate(label="analog compute", description="Compute that uses analog physical behavior for operations such as MAC-like accumulation.", node_type="concept", epistemic_status="user_stated", confidence=0.84, local_salience=0.84, global_salience=0.58, bridge_potential=0.78),
                NodeCandidate(label="compute-in-memory", description="Architectures that place compute near or inside memory to reduce data movement.", node_type="concept", epistemic_status="user_stated", confidence=0.86, local_salience=0.84, global_salience=0.6, bridge_potential=0.78),
                NodeCandidate(label="data movement cost", description="Energy and latency cost of moving data between memory, compute, and conversion boundaries.", node_type="constraint", epistemic_status="assistant_inferred", confidence=0.76, local_salience=0.8, global_salience=0.66, bridge_potential=0.86),
                NodeCandidate(label="ADC/DAC overhead", description="Conversion, precision, and interface overhead around analog or mixed-signal compute blocks.", node_type="constraint", epistemic_status="user_stated", confidence=0.88, local_salience=0.92, global_salience=0.72, bridge_potential=0.9),
                NodeCandidate(label="conversion/control overhead", description="System overhead from conversion, control, calibration, and orchestration around local compute.", node_type="constraint", epistemic_status="assistant_inferred", confidence=0.72, local_salience=0.72, global_salience=0.56, bridge_potential=0.82),
            ]
        )
        extraction.edge_candidates.extend(
            [
                EdgeCandidate(from_label="data movement cost", to_label="compute-in-memory", relation_type="motivates", label="motivates", epistemic_status="assistant_inferred", confidence=0.7, salience=0.78),
                EdgeCandidate(from_label="ADC/DAC overhead", to_label="analog compute", relation_type="constrains", label="constrains", epistemic_status="user_stated", confidence=0.8, salience=0.9),
                EdgeCandidate(from_label="ADC/DAC overhead", to_label="compute-in-memory", relation_type="constrains", label="constrains", epistemic_status="speculative", confidence=0.78, salience=0.86),
                EdgeCandidate(from_label="conversion/control overhead", to_label="ADC/DAC overhead", relation_type="includes", label="includes", epistemic_status="assistant_inferred", confidence=0.66, salience=0.68),
            ]
        )
        extraction.tensions.append(
            {
                "title": "Analog/CIM conversion overhead tension",
                "description": "Local MAC efficiency may be erased by conversion/control overhead, including conversion overhead, calibration, or precision requirements.",
                "status": "open",
                "node_labels": ["analog compute", "compute-in-memory", "ADC/DAC overhead", "conversion/control overhead"],
                "confidence": 0.82,
            }
        )
        extraction.open_questions.append(
            OpenQuestionCandidate(question="When does conversion overhead erase compute-in-memory or analog compute benefit?", priority=0.92)
        )
        extraction.latent_bridges.append(
            LatentBridgeCandidate(
                from_label="ADC/DAC overhead",
                to_label="data movement cost",
                reason="Both are system-level costs that can dominate local compute efficiency even if the local operation is cheap.",
                confidence=0.64,
                status="suggested",
            )
        )
        extraction.source_needs.append("Recent technical work on analog compute and compute-in-memory ADC/DAC conversion overhead, precision, calibration, and energy tradeoffs.")

    def _dedupe(self, extraction: PostTurnExtraction) -> PostTurnExtraction:
        extraction.topics = self._unique_strings(extraction.topics)
        extraction.source_needs = self._unique_strings(extraction.source_needs)
        extraction.forbidden_user_state_claims = self._unique_strings(extraction.forbidden_user_state_claims)
        extraction.node_candidates = list({node.label.lower(): node for node in extraction.node_candidates}.values())
        extraction.claims = list({claim.text.lower(): claim for claim in extraction.claims}.values())
        extraction.edge_candidates = list({(edge.from_label.lower(), edge.to_label.lower(), edge.relation_type): edge for edge in extraction.edge_candidates}.values())
        extraction.open_questions = list({question.question.lower(): question for question in extraction.open_questions}.values())
        extraction.latent_bridges = list({(bridge.from_label.lower(), bridge.to_label.lower(), bridge.reason.lower()): bridge for bridge in extraction.latent_bridges}.values())
        seen_tensions: dict[str, dict] = {}
        for tension in extraction.tensions:
            title = str(tension.get("title", "")).lower()
            if title:
                seen_tensions[title] = tension
        extraction.tensions = list(seen_tensions.values())
        return extraction

    def _unique_strings(self, values: list[str]) -> list[str]:
        out: list[str] = []
        seen: set[str] = set()
        for value in values:
            key = value.strip().lower()
            if value.strip() and key not in seen:
                seen.add(key)
                out.append(value.strip())
        return out
