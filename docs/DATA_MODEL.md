# Data Model

SQLite stores the atlas, sessions, events, artifacts, source cards, and map patches. FTS tables support search across sessions, turns, claims, source cards, and concept nodes.

Important entities:

- `sessions`, `turns`: first-class conversation history.
- `events`: append-only event store.
- `artifacts`: structured residue from workers.
- `topic_maps`, `concept_nodes`, `relation_edges`: map forest materialization.
- `claims`, `open_questions`, `tensions`, `analogies`, `latent_bridges`: epistemic and cross-domain structure.
- `map_patches`: versioned change proposals and applied patches.
- `source_cards`, `research_tasks`: source and research substrate.

Claims and relations keep epistemic status, confidence, source references, and provenance. The system stores what was asserted, questioned, inferred, or source-backed; it does not store fake autobiography about the user.

