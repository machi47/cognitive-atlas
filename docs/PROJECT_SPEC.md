# CODEX CLI ONE-SHOT IMPLEMENTATION PROMPT
# Project: Cognitive Atlas / Conversation-Centered Learning Kernel
# Intended usage:
# - Paste this entire prompt into Codex CLI from an empty directory.
# - User may run Codex in plan mode first.
# - If in plan mode: produce the implementation plan, file tree, phases, and exact execution checklist, then be ready to implement immediately after approval.
# - If not in plan mode: implement the entire repo directly.
# - Do not ask clarifying questions unless absolutely blocked by missing credentials.
# - Use practical defaults.
# - Build a real working repo, not a demo-only sketch.
# - After implementation, run tests, commit, and push to GitHub if GitHub CLI auth is available.

--------------------------------------------------------------------------------
0. CORE INTENT
--------------------------------------------------------------------------------

Build a private, local-first, tailnet-accessible web application for high-bandwidth conversational learning.

This is not a normal notes app.
This is not a generic chatbot wrapper.
This is not a giant autonomous agent.
This is not a second coding agent.
This is not a Discord bot.
This is not a Telegram bot.
This is not OpenClaw.
This is not a knowledge graph toy.

It is a conversation-centered learning kernel.

The user learns through messy, associative discussion.
The user often has complex ideas spanning hardware, SoCs, chip fabrication, analog compute, compute-in-memory, AI systems, physics, software architecture, and agent systems.
The system must let the user speak or type messy thoughts without forcing structure upfront.
The system must provide a clean conversational response.
The system must quietly extract structured artifacts behind the scenes:
- topics
- claims
- source needs
- source cards
- map patches
- open questions
- surprising cross-links
- unresolved tensions
- session summaries
- atlas updates
- provenance traces

The human-facing answer must stay clean.
The backend must become structured.
The UI must feel simple enough that the user opens it for random ideas.
The UI must not overwhelm the user with graph vomit.
The atlas must preserve complexity without forcing the user to stare at all complexity at once.

The user's ideal:
- They can open the app instantly.
- Start a new thought/session without disrupting another session.
- Speak/type messy associative content.
- Get a compact useful response.
- Have backend memory update automatically.
- Later inspect how ideas formed across sessions.
- Have multiple historical conversations update an overarching knowledge plane.
- Have cutting-edge research grounded in sources when needed.
- Avoid context rot and LLM distraction.
- Avoid giant walls of text unless explicitly requested.
- Avoid fake claims about the user's internal beliefs.
- Avoid losing weird cross-domain insights where an "unimportant" relation becomes important under a novel juxtaposition.

--------------------------------------------------------------------------------
1. DEFAULTS
--------------------------------------------------------------------------------

Use these defaults unless local environment forces a fallback.

Project name:
- cognitive-atlas

Repo name:
- cognitive-atlas

Backend:
- Python 3.12+
- FastAPI
- Pydantic v2
- aiosqlite or SQLAlchemy async with SQLite
- httpx
- uvicorn
- structlog or standard logging with structured JSON formatter
- pytest
- pytest-asyncio

Frontend:
- TypeScript
- React
- Vite
- TanStack Query
- Zustand or equivalent lightweight state store
- CSS variables / plain CSS / CSS modules
- no heavy component framework unless needed
- PWA manifest
- service worker through vite-plugin-pwa if practical

Database:
- SQLite
- FTS5 for search
- append-only event store
- migration system through simple SQL migrations stored in repo
- no Postgres for v0
- no vector DB for v0, but create an interface for future vector search

Runtime LLM:
- Codex CLI adapter first
- OpenAI Responses API adapter later as optional placeholder/interface
- fake deterministic adapter for tests and offline development

Ports:
- backend production/app port: 8787
- frontend dev port: 5173
- bind backend to 127.0.0.1 by default
- expose through Tailscale Serve, not LAN bind by default

Data:
- ./data/cognitive_atlas.db
- ./data/artifacts/
- ./data/exports/
- ./data/imports/
- ./data/codex_runs/
- ./data/logs/
- ensure ./data is gitignored except maybe ./data/.gitkeep

Auth:
- tailnet-first
- local-only by default
- optional APP_ACCESS_TOKEN env var for simple bearer/session gate
- do not build a complex auth system in v0
- do not expose publicly

GitHub:
- initialize git
- create first commit
- if gh is authenticated, create private GitHub repo and push
- if gh is not authenticated, leave exact command in FINAL_STATUS.md

--------------------------------------------------------------------------------
2. PLAN MODE INSTRUCTIONS
--------------------------------------------------------------------------------

If Codex is running in plan mode:
- Do not merely summarize this prompt.
- Produce a concrete implementation plan with:
  - repo architecture
  - data model
  - API contracts
  - frontend components
  - worker pipeline
  - LLM adapter design
  - testing strategy
  - deployment strategy
  - exact file tree
  - exact packages
  - execution phases
- Keep the plan broad enough to cover the full system.
- Keep the plan actionable enough that implementation can proceed immediately.
- Do not ask the user to choose names, frameworks, or minor options.
- Use the defaults in this prompt.
- State clearly that implementation should proceed after plan approval.
- After approval, implement everything.

If Codex is not in plan mode:
- Implement everything directly.
- Create files.
- Install dependencies where appropriate.
- Run tests.
- Run linters/builds.
- Commit.
- Push if possible.

--------------------------------------------------------------------------------
3. NON-NEGOTIABLE PRODUCT PRINCIPLE
--------------------------------------------------------------------------------

The main conversation must remain clean.

The app can have:
- map forest
- source panel
- event trace
- pending patches
- session list
- atlas tree
- research queue
- claim ledger
- debug artifacts

But the main conversational response must not be polluted by:
- giant map dumps
- backend state dumps
- unrelated topic trees
- giant tables
- raw search logs
- full JSON artifacts
- model chain noise
- "see table 5" style audio-hostile output

The system must separate planes:

Conversation plane:
- user-facing
- compact
- readable
- one useful answer at a time
- no relation overload by default

Infrastructure plane:
- hidden workers
- routing
- extraction
- source search
- topic detection
- source cards
- map patches
- event store

State/rendering plane:
- sidebar
- maps
- source cards
- session history
- inspector
- debug trace
- all optional/expandable

The app observes conversation and emits structured residue.
The app does not shove the whole residue back into the conversational agent.

--------------------------------------------------------------------------------
4. CORE ARCHITECTURE
--------------------------------------------------------------------------------

Implement this pipeline:

User input:
- typed text
- pasted transcript
- future voice transcript support
- quick capture

Pipeline:
1. Turn intake
2. Session association
3. Topic segmentation
4. Topic routing
5. Research need detection
6. Source query planning
7. Source broker retrieval if needed
8. Source card generation
9. Conversational response generation
10. Post-turn extraction
11. Claim extraction
12. Map patch proposal
13. Map patch validation
14. Map patch application
15. Event persistence
16. FTS index update
17. UI state update
18. Export-ready session/map state

Important:
- Not every turn needs every step.
- Keep UI latency reasonable.
- Return the conversational answer as soon as possible.
- Run heavier extraction/research/map patching as background tasks when possible.
- Provide optimistic UI states: "processing", "mapping", "researching", "updated".

--------------------------------------------------------------------------------
5. THE MAP FOREST MODEL
--------------------------------------------------------------------------------

Do not create one giant map.
Do not create a new map for every compression.
Build a map forest.

Objects:
- Workspace
- Domain
- TopicMap
- SubMap
- ConceptNode
- RelationEdge
- Claim
- SourceCard
- OpenQuestion
- Tension
- Analogy
- LatentBridge
- Session
- Turn
- Artifact
- MapPatch
- Event

The atlas must support:
- multiple independent sessions
- sessions touching multiple maps
- one session updating the overarching plane
- multiple maps updated by one conversation
- new maps created when needed
- split map suggestions
- merge map suggestions
- bridge edges between maps
- archived branches
- parked branches
- active branches
- historical sessions
- cross-session evolution

Do not expose full graph complexity by default.
Expose it progressively.

Map forest example:
- Computing Systems
  - Analog Compute
    - Analog MAC Arrays
    - ADC/DAC Bottlenecks
    - Noise / Drift / Calibration
  - Compute-in-Memory
    - SRAM-CIM
    - RRAM / Memristor Crossbars
    - Compiler / Runtime Integration
  - SoCs
    - Interconnects
    - Memory Hierarchy
    - Accelerator Fabrics
- Semiconductor Fabrication
  - Lithography
  - Process Variation
  - Packaging
- Agent Systems
  - Codex Orchestration
  - Memory Compaction
  - Conversation UX

But do not hard-code these.
Seed examples only if useful.
The system should create maps organically.

--------------------------------------------------------------------------------
6. SESSIONS
--------------------------------------------------------------------------------

Implement sessions as first-class entities.

Requirements:
- User can create a new session instantly.
- Session has title auto-generated after first turn.
- User can rename session.
- User can archive session.
- User can resume session.
- User can fork session.
- User can search sessions.
- User can have unrelated sessions without polluting active conversation.
- Different sessions can update same atlas maps.
- Same session can touch multiple maps.
- Session history must be visible but not overwhelming.

Session object fields:
- id
- workspace_id
- title
- status: active | archived | pinned
- created_at
- updated_at
- last_turn_at
- user_summary
- system_summary
- active_map_ids
- touched_map_ids
- conversation_mode
- response_budget
- metadata JSON

UI:
- Left sidebar desktop: sessions + atlas
- Mobile: bottom nav with Sessions, Talk, Atlas
- Quick new session button always reachable
- "Capture unrelated thought" should create a lightweight session without destroying current one

--------------------------------------------------------------------------------
7. EPISTEMIC MODEL
--------------------------------------------------------------------------------

Do not write fake autobiography about the user.

Never store:
- "User now believes X"
- "User's intuition changed"
- "User learned Y"
- "User accepts Z"

Unless explicitly confirmed.

Instead store:
- user_asserted
- user_questioned
- user_rejected
- user_challenged
- user_ignored
- assistant_claimed
- assistant_inferred
- source_supported
- source_contested
- unconfirmed_candidate
- speculative_connection
- unresolved_tension

Every claim and relation must have:
- provenance
- status
- confidence
- evidence references
- origin turn id
- speaker/source attribution

Epistemic statuses:
- user_asserted
- user_confirmed
- user_rejected
- assistant_claimed
- assistant_inferred
- source_backed
- source_contested
- speculative
- unverified
- stale
- deprecated
- open_question
- needs_research

Relations are not just "contradictions".
Use:
- supports
- weakens
- requires
- depends_on
- causes
- constrains
- is_example_of
- is_counterexample_to
- is_analogy_for
- analogy_breaks_at
- generalizes_to
- specializes_to
- transfers_to
- interacts_with
- conflicts_under_assumption
- opens_question
- bridges_to
- same_as
- related_but_distinct

--------------------------------------------------------------------------------
8. CROSS-DOMAIN IMPORTANCE
--------------------------------------------------------------------------------

The user specifically worries that things deemed unimportant can become important when posited against other things never posited against before.

Implement support for this.

Do not only rank by local importance.
Also track:
- local_salience
- global_salience
- novelty_score
- bridge_potential
- surprise_score
- recurrence_count
- source_support_count
- user_attention_count
- unanswered_question_count
- cross_domain_touch_count

Implement LatentBridge:
- id
- from_node_id
- to_node_id
- bridge_type
- reason
- confidence
- status: hidden | suggested | accepted | rejected | archived
- discovered_by: deterministic | llm | user
- evidence_artifact_ids

LatentBridge examples:
- PCB trace impedance ↔ SoC interconnect signal integrity
- thermal constraints ↔ analog compute drift
- device variation ↔ calibration burden
- memory hierarchy ↔ compute-in-memory motivation
- ADC/DAC overhead ↔ analog accelerator system efficiency
- law of physics ↔ architecture constraint

UI rule:
- Do not dump all latent bridges.
- Show at most 1-3 "possibly relevant cross-links" when contextually useful.
- Allow "show why" expansion.
- Allow reject/hide.
- Allow pin.

Backend rule:
- Store more than UI shows.
- Keep artifacts inspectable.

--------------------------------------------------------------------------------
9. RESPONSE STYLE
--------------------------------------------------------------------------------

Default conversational response must be compact.

Default response budget:
- 120 to 250 words
- no tables unless asked
- no giant bullet lists unless asked
- one core answer
- one optional next branch
- one question maximum
- mark uncertainty clearly
- use concrete causal structure
- avoid "textbook dump"

Supported modes:
- discuss
- explain
- research
- critique
- map
- compress
- plan
- quiz
- source
- deep

Commands:
- /new
- /deepen
- /shorter
- /map
- /sources
- /criticize
- /compress
- /next
- /quiz
- /export
- /fork
- /pin
- /hide
- /research
- /trace

Implement commands in frontend/backend where practical.
At minimum parse commands and route mode.

Main agent must not output raw backend JSON to user.
Backend artifacts should appear in inspector/debug panels.

--------------------------------------------------------------------------------
10. LLM ADAPTER DESIGN
--------------------------------------------------------------------------------

Create abstraction:

LlmAdapter:
- async complete_text(request) -> LlmTextResult
- async complete_json(request, schema) -> LlmJsonResult
- async healthcheck() -> LlmHealth
- supports_web_search
- supports_schema_output
- provider_name

Implement:
1. FakeLlmAdapter
   - deterministic
   - used for tests
   - no network
   - returns plausible structured artifacts

2. CodexCliAdapter
   - invokes codex CLI through asyncio subprocess
   - configurable model per task
   - configurable search mode
   - configurable timeout
   - supports schema output via --output-schema when available
   - supports --json event stream parsing when enabled
   - writes run logs to data/codex_runs/
   - never blocks event loop
   - handles missing codex binary gracefully
   - handles auth failure gracefully
   - handles malformed JSON gracefully
   - logs structured error details
   - supports cancellation timeout
   - does not pass secrets in prompts
   - does not commit auth files
   - defaults to read-only sandbox for runtime calls when possible

3. OpenAIResponsesAdapter placeholder
   - interface only or minimal optional implementation
   - disabled unless OPENAI_API_KEY present
   - do not make API usage required for v0

Codex CLI runtime call pattern:
- construct a prompt packet
- write JSON schema to temp file if needed
- call codex exec
- pass prompt through stdin
- capture stdout/stderr
- parse final JSON or final message
- validate with pydantic/jsonschema
- return structured result

Do not let the app directly depend on Codex internals.
All Codex-specific code lives in one adapter module.

Environment variables:
- ATLAS_LLM_PROVIDER=codex|fake|openai
- ATLAS_CODEX_BIN=codex
- ATLAS_CODEX_MODEL_DISCUSS=gpt-5.5
- ATLAS_CODEX_MODEL_EXTRACT=gpt-5.5
- ATLAS_CODEX_MODEL_ROUTE=gpt-5.5
- ATLAS_CODEX_MODEL_RESEARCH=gpt-5.5
- ATLAS_CODEX_REASONING_DISCUSS=medium
- ATLAS_CODEX_REASONING_EXTRACT=high
- ATLAS_CODEX_REASONING_ROUTE=low
- ATLAS_CODEX_REASONING_RESEARCH=high
- ATLAS_CODEX_LIVE_SEARCH=false
- ATLAS_CODEX_TIMEOUT_SECONDS=180
- ATLAS_DATA_DIR=./data
- APP_ACCESS_TOKEN=

Use config file:
- atlas.config.toml or .env
- document all env vars

--------------------------------------------------------------------------------
11. WORKER ROLES
--------------------------------------------------------------------------------

Implement worker services as separate backend classes.

TurnIntakeService:
- validates user input
- creates session if needed
- stores raw turn event
- normalizes whitespace
- preserves original text
- detects command prefix

TopicRouter:
- cheap/fast LLM or deterministic fallback
- outputs candidate topics
- outputs segment spans
- maps to existing TopicMap ids when likely
- suggests new maps when needed
- does not write directly to atlas

ResearchNeedDetector:
- detects whether current turn needs fresh/cutting-edge information
- detects terms needing verification
- detects source claims
- outputs research tasks

ResearchPlanner:
- creates focused search queries
- separates broad background queries from frontier queries
- produces source plan with search type:
  - web
  - arxiv
  - openalex
  - crossref
  - semantic_scholar_optional
  - manual_pdf_later

SourceBroker:
- runs deterministic source searches where implemented
- can call Codex web search through Researcher worker when needed
- deduplicates source candidates
- creates compact source cards
- stores sources in DB
- does not dump raw full pages into conversation context

ConversationalAgent:
- gets only:
  - current user message
  - recent dialogue window
  - command/mode
  - response budget
  - selected source cards if needed
  - tiny critical prior context if needed
- does not see the whole map forest
- outputs clean answer
- may include citations/source labels if source cards exist
- no raw artifacts

PostTurnExtractor:
- reads user turn + assistant answer + selected sources
- extracts:
  - claims
  - topics
  - open questions
  - possible edges
  - source needs
  - analogies
  - uncertainties
  - latent bridges
- emits structured artifact

MapPatchBuilder:
- converts extraction into map patch
- includes provenance
- chooses update existing vs create new vs bridge vs split suggestion
- never destructive rewrite
- patch is versioned

MapPatchValidator:
- checks schema
- checks for fake user belief inference
- checks duplicate nodes
- checks low-confidence risky updates
- checks relation overload
- can auto-apply safe patches
- sends risky patches to pending state

MapWriter:
- applies patches
- writes append-only events
- updates materialized tables
- updates FTS index
- supports rollback/undo by inverse patch or versioning

UiProjectionService:
- builds sidebar projections
- builds map view projections
- builds session list projections
- builds inspector projections
- applies salience budgets
- avoids overwhelming UI

ExportService:
- exports session markdown
- exports map markdown
- exports atlas JSON
- exports source bibliography JSON
- exports compact "textbook chapter" for a selected map

--------------------------------------------------------------------------------
12. DATABASE SCHEMA
--------------------------------------------------------------------------------

Use SQLite migrations.

Tables:

workspaces:
- id text primary key
- name text not null
- created_at text not null
- updated_at text not null
- settings_json text not null default '{}'

sessions:
- id text primary key
- workspace_id text not null
- title text not null
- status text not null
- mode text not null default 'discuss'
- response_budget_json text not null
- created_at text not null
- updated_at text not null
- last_turn_at text
- user_summary text
- system_summary text
- active_map_ids_json text not null default '[]'
- touched_map_ids_json text not null default '[]'
- metadata_json text not null default '{}'

turns:
- id text primary key
- session_id text not null
- role text not null
- content text not null
- original_content text
- created_at text not null
- token_estimate integer
- metadata_json text not null default '{}'

events:
- id text primary key
- workspace_id text not null
- session_id text
- event_type text not null
- aggregate_type text not null
- aggregate_id text not null
- payload_json text not null
- created_at text not null
- causation_id text
- correlation_id text

artifacts:
- id text primary key
- workspace_id text not null
- session_id text
- turn_id text
- artifact_type text not null
- title text
- content_json text not null
- status text not null
- created_at text not null
- metadata_json text not null default '{}'

domains:
- id text primary key
- workspace_id text not null
- name text not null
- description text
- parent_domain_id text
- status text not null
- created_at text not null
- updated_at text not null

topic_maps:
- id text primary key
- workspace_id text not null
- domain_id text
- parent_map_id text
- title text not null
- summary text
- status text not null
- created_at text not null
- updated_at text not null
- salience real not null default 0
- metadata_json text not null default '{}'

concept_nodes:
- id text primary key
- workspace_id text not null
- map_id text not null
- label text not null
- description text
- node_type text not null
- epistemic_status text not null
- confidence real not null default 0.5
- local_salience real not null default 0
- global_salience real not null default 0
- novelty_score real not null default 0
- bridge_potential real not null default 0
- recurrence_count integer not null default 0
- created_at text not null
- updated_at text not null
- provenance_json text not null default '[]'
- metadata_json text not null default '{}'

relation_edges:
- id text primary key
- workspace_id text not null
- map_id text
- from_node_id text not null
- to_node_id text not null
- relation_type text not null
- label text
- description text
- epistemic_status text not null
- confidence real not null default 0.5
- salience real not null default 0
- created_at text not null
- updated_at text not null
- provenance_json text not null default '[]'
- metadata_json text not null default '{}'

claims:
- id text primary key
- workspace_id text not null
- session_id text
- map_id text
- node_id text
- text text not null
- claim_type text not null
- epistemic_status text not null
- confidence real not null default 0.5
- created_at text not null
- updated_at text not null
- provenance_json text not null default '[]'
- source_ids_json text not null default '[]'
- metadata_json text not null default '{}'

open_questions:
- id text primary key
- workspace_id text not null
- session_id text
- map_id text
- question text not null
- status text not null
- priority real not null default 0
- created_at text not null
- updated_at text not null
- provenance_json text not null default '[]'
- metadata_json text not null default '{}'

tensions:
- id text primary key
- workspace_id text not null
- map_id text
- title text not null
- description text not null
- status text not null
- created_at text not null
- updated_at text not null
- node_ids_json text not null default '[]'
- claim_ids_json text not null default '[]'
- provenance_json text not null default '[]'

analogies:
- id text primary key
- workspace_id text not null
- map_id text
- source_concept text not null
- target_concept text not null
- useful_because text
- breaks_at text
- status text not null
- confidence real not null default 0.5
- created_at text not null
- provenance_json text not null default '[]'

latent_bridges:
- id text primary key
- workspace_id text not null
- from_node_id text not null
- to_node_id text not null
- bridge_type text not null
- reason text not null
- confidence real not null default 0.5
- status text not null
- discovered_by text not null
- created_at text not null
- updated_at text not null
- evidence_artifact_ids_json text not null default '[]'
- metadata_json text not null default '{}'

map_patches:
- id text primary key
- workspace_id text not null
- session_id text
- turn_id text
- target_map_ids_json text not null
- patch_json text not null
- status text not null
- risk_level text not null
- created_at text not null
- applied_at text
- rejected_at text
- metadata_json text not null default '{}'

source_cards:
- id text primary key
- workspace_id text not null
- title text not null
- url text
- doi text
- arxiv_id text
- source_type text not null
- year integer
- authors_json text not null default '[]'
- venue text
- abstract text
- key_claims_json text not null default '[]'
- limitations_json text not null default '[]'
- relevance_score real not null default 0
- credibility_score real not null default 0
- freshness_score real not null default 0
- created_at text not null
- updated_at text not null
- metadata_json text not null default '{}'

research_tasks:
- id text primary key
- workspace_id text not null
- session_id text
- turn_id text
- query text not null
- task_type text not null
- status text not null
- priority real not null default 0
- created_at text not null
- updated_at text not null
- result_artifact_id text
- metadata_json text not null default '{}'

FTS:
- turns_fts
- concept_nodes_fts
- claims_fts
- source_cards_fts
- sessions_fts

Implement triggers or explicit indexing functions.
Explicit indexing is acceptable for v0.

--------------------------------------------------------------------------------
13. API ENDPOINTS
--------------------------------------------------------------------------------

Base path: /api

Health:
- GET /api/health
- GET /api/config/public

Sessions:
- GET /api/sessions
- POST /api/sessions
- GET /api/sessions/{session_id}
- PATCH /api/sessions/{session_id}
- POST /api/sessions/{session_id}/archive
- POST /api/sessions/{session_id}/fork
- GET /api/sessions/{session_id}/turns

Turns:
- POST /api/sessions/{session_id}/turns
  Input:
    content
    mode optional
    response_budget optional
    command optional
  Output:
    user_turn
    assistant_turn initially or final
    processing_state
    artifacts_summary
- GET /api/turns/{turn_id}
- GET /api/turns/{turn_id}/artifacts

Atlas:
- GET /api/atlas/tree
- GET /api/atlas/maps
- POST /api/atlas/maps
- GET /api/atlas/maps/{map_id}
- GET /api/atlas/maps/{map_id}/graph
- GET /api/atlas/maps/{map_id}/timeline
- GET /api/atlas/maps/{map_id}/sources
- GET /api/atlas/maps/{map_id}/questions

Patches:
- GET /api/patches?status=pending
- GET /api/patches/recent
- POST /api/patches/{patch_id}/apply
- POST /api/patches/{patch_id}/reject
- POST /api/patches/{patch_id}/undo

Sources:
- GET /api/sources
- GET /api/sources/{source_id}
- POST /api/sources/search
- POST /api/sources/manual
- PATCH /api/sources/{source_id}

Search:
- GET /api/search?q=
- POST /api/search

Commands:
- POST /api/commands
  Input:
    session_id optional
    command string
    args object

Exports:
- GET /api/export/session/{session_id}.md
- GET /api/export/map/{map_id}.md
- GET /api/export/atlas.json

Events/debug:
- GET /api/events/recent
- GET /api/artifacts/{artifact_id}
- GET /api/debug/llm-runs
- only expose debug if ATLAS_DEBUG=true

Streaming:
- Implement simple non-streaming first.
- If practical, implement SSE:
  - GET /api/sessions/{session_id}/stream
  - events: turn_started, assistant_reply, extraction_done, patch_applied, research_done

--------------------------------------------------------------------------------
14. FRONTEND UX
--------------------------------------------------------------------------------

The UI must be extremely fast to open and not feel like homework.

Layout desktop:
- App shell with three zones:
  1. Left sidebar
     - New Thought button
     - Sessions
     - Atlas tree
     - Search
  2. Main conversation
     - Current session title
     - Turns
     - Compact assistant replies
     - Sticky composer
     - mode selector
  3. Right inspector
     - collapsible
     - sources used
     - recent map changes
     - open questions
     - trace if debug enabled

Layout mobile Safari:
- Full-screen PWA feel
- Bottom nav:
  - Talk
  - Sessions
  - Atlas
  - Sources
- Sticky bottom composer with safe-area padding
- Big input target
- One-tap New Thought
- Swipe or simple buttons, but do not depend on complex gestures
- No tiny controls
- No horizontal overflow
- Support iOS dynamic viewport/safe areas:
  - env(safe-area-inset-bottom)
  - env(safe-area-inset-top)
  - min-height: 100dvh
- Use font sizes that prevent iOS auto zoom on inputs
- Must work well in Safari and installed PWA mode

Conversation UI:
- User messages can be messy and long
- Assistant messages default compact
- Provide expand/deepen button
- Provide "too much" and "good" feedback controls
- Provide "show map impact" button
- Provide "sources" button
- Provide "fork from here" button
- Provide "turn into map" button only if useful

Atlas UI:
- Tree, not giant graph by default
- Collapsible domains/maps/submaps
- Active/touched maps highlighted
- Map detail page:
  - summary
  - top nodes
  - top relations
  - open questions
  - latent bridges limited to top few
  - source cards
  - timeline
- Optional simple graph visualization using SVG/React Flow only if not heavy
- If using graph visualization, also provide a readable list fallback
- Do not make graph visualization the core experience

Session UI:
- Sessions list with search
- Active sessions
- Recently touched
- Archived
- Forks
- Sessions show map badges but not overwhelming counts

Composer:
- Placeholder examples:
  - "Dump the thought. It can be messy."
  - "Ask the thing before it disappears."
  - "Paste a transcript or paper link."
- Buttons:
  - Send
  - New Thought
  - Mode
  - Mic placeholder
- Voice:
  - Do not implement paid audio in v0.
  - Provide an input field compatible with OS/browser dictation.
  - Add placeholder for future audio.
  - Optionally add Web Speech API if available, but do not rely on it.

Native feel:
- Instant route transitions
- Local optimistic rendering
- Soft but not cute
- Dense enough for desktop, simple enough for phone
- Dark mode and light mode
- Respect prefers-color-scheme
- Keyboard shortcuts:
  - Cmd/Ctrl+K search
  - Cmd/Ctrl+N new thought
  - Cmd/Ctrl+Enter send
  - Esc close inspector
- PWA manifest:
  - name Cognitive Atlas
  - short_name Atlas
  - display standalone
  - theme colors
  - icons generated simple SVG/PNG if possible

--------------------------------------------------------------------------------
15. LEARNING FIT VALIDATION
--------------------------------------------------------------------------------

The user asked: how do we know this will actually help learning?

Build the app so this is testable.

Add lightweight feedback per assistant response:
- "good"
- "too much"
- "too vague"
- "wrong direction"
- "save this"
- "show deeper"

Track:
- session_created
- turn_submitted
- assistant_response_length
- user_deepened
- user_abandoned_session
- user_opened_map_impact
- user_rejected_patch
- user_pinned_bridge
- user_returned_to_session
- user_exported_map
- user_marked_overwhelming

Build LearningFitService:
- computes simple metrics:
  - average response length
  - too_much_rate
  - deepen_rate
  - return_rate
  - session_fragmentation
  - patch_rejection_rate
  - source_usage_rate
  - map_open_rate
- provides /api/learning-fit/report
- UI small report hidden under settings/debug

Important:
- Do not gamify.
- Do not create productivity shame.
- Use this to tune the app.

Add "Friction Review":
- After 7 days or 20 sessions, generate a report:
  - What made the app useful?
  - What made it overwhelming?
  - Which response budget worked?
  - Which topics created the most confusion?
  - Which maps are too broad and need splitting?
- This can be a manual command /fit-review.

--------------------------------------------------------------------------------
16. SOURCE AND RESEARCH SYSTEM
--------------------------------------------------------------------------------

The app must support cutting-edge research without relying on LLM vibes.

V0 source broker should include:
- Manual source cards
- URL placeholder ingestion
- arXiv search if easy
- Crossref search if easy
- OpenAlex search if easy
- Codex web search through LLM adapter for frontier/fresh synthesis
- Semantic Scholar optional if easy and no key required; otherwise placeholder

Use httpx async.
Use rate limits.
Use timeouts.
Use graceful failures.

SourceCard fields:
- title
- authors
- year
- venue
- url
- doi
- arxiv_id
- source_type
- abstract
- key_claims
- limitations
- relevance_score
- credibility_score
- freshness_score

Research flow:
- Do not browse every turn.
- Detect if freshness matters.
- Detect if topic is frontier/recent.
- Detect if user explicitly requests research/source/current.
- Generate focused queries.
- Fetch candidates.
- Deduplicate by DOI/arXiv/title similarity.
- Create source cards.
- Select at most 3-5 source cards for conversational context.
- Store all candidates in source table.
- Mark claims source-backed only when supported.

Cutting-edge topics examples:
- analog compute
- compute-in-memory
- chip fabrication
- SoCs
- advanced packaging
- HBM
- neuromorphic computing
- photonic compute
- in-memory MAC arrays
- SRAM-CIM
- RRAM-CIM
- ADC/DAC overhead
- mixed-signal accelerators
- wafer-scale systems
- process variation
- chiplets
- interconnects

For these topics:
- prefer recent survey + recent papers + authoritative technical sources
- store publication year
- mark stale sources
- distinguish speculation from source-backed

Do not generate fake citations.
If no sources found, say so in source artifact.
Do not let the conversational agent pretend it researched when it did not.

--------------------------------------------------------------------------------
17. CONTEXT ISOLATION
--------------------------------------------------------------------------------

The conversational agent must not see:
- full map forest
- entire database
- full source corpus
- all prior sessions
- all unresolved questions
- sidebar projection
- debug traces
- raw worker artifacts unless specifically relevant

The conversational agent may see:
- current user message
- recent session turns
- user-selected mode
- response budget
- a tiny critical memory snippet if needed
- selected source cards if current turn triggered research
- active session summary if needed

Backend workers may see richer artifacts depending on task.

Implement ContextBroker:
- builds context packets per role
- enforces token/character budgets
- logs what context was included
- rejects oversized context
- summarizes/drops low relevance context
- separates:
  - DiscussionContext
  - ExtractionContext
  - ResearchContext
  - MapPatchContext
  - CriticContext

Context budgets:
- discussion max chars default 12000
- extraction max chars default 24000
- research max chars default 18000
- map patch max chars default 24000

No whole-workspace stuffing.

--------------------------------------------------------------------------------
18. STRUCTURED SCHEMAS
--------------------------------------------------------------------------------

Create JSON schemas and Pydantic models.

Models:
- TopicRouteResult
- Segment
- ResearchNeedResult
- ResearchPlan
- SourceCardModel
- DiscussionReply
- PostTurnExtraction
- ClaimCandidate
- NodeCandidate
- EdgeCandidate
- OpenQuestionCandidate
- AnalogyCandidate
- LatentBridgeCandidate
- MapPatch
- MapPatchValidationResult
- LearningFitReport

Store JSON schemas in:
- schemas/topic_route.schema.json
- schemas/research_need.schema.json
- schemas/research_plan.schema.json
- schemas/discussion_reply.schema.json
- schemas/post_turn_extraction.schema.json
- schemas/map_patch.schema.json
- schemas/map_patch_validation.schema.json

Use schemas with Codex CLI adapter when possible.

DiscussionReply schema:
- message: string
- response_mode: string
- source_ids_used: array
- suggested_followups: array max 3
- uncertainty_notes: array
- should_research_more: boolean

PostTurnExtraction schema:
- topics: array
- claims: array
- open_questions: array
- node_candidates: array
- edge_candidates: array
- analogies: array
- latent_bridges: array
- source_needs: array
- user_state_claims_forbidden: array
- notes: string

MapPatch schema:
- action: update_existing | create_new | bridge_maps | split_suggest | merge_suggest | no_op
- target_map_ids
- create_maps
- add_nodes
- update_nodes
- add_edges
- add_claims
- add_questions
- add_tensions
- add_analogies
- add_latent_bridges
- provenance
- confidence
- risk_level

Validator must reject:
- fake user belief claims
- no provenance
- destructive overwrites
- hallucinated source-backed status without source id
- too many low-confidence edges
- giant patch with unrelated topics

--------------------------------------------------------------------------------
19. BACKGROUND PROCESSING
--------------------------------------------------------------------------------

Implement simple async background tasks.

FastAPI can use BackgroundTasks for v0.
Better: internal asyncio task queue service.
No Celery/Redis for v0.

When user submits turn:
- store user turn
- start pipeline
- return assistant response when ready
- run extraction/map patch after response if needed
- UI polls or SSE receives state

If SSE is too much, implement polling:
- /api/sessions/{id}/turns
- /api/patches/recent
- /api/events/recent

Use status fields:
- queued
- running
- succeeded
- failed
- skipped

Failure behavior:
- If route fails, still respond with fallback.
- If research fails, respond without research and show source error in inspector.
- If extraction fails, do not lose conversation.
- If map patch fails, leave artifact with error.
- If Codex missing, app still runs in fake/offline mode with clear UI banner.

--------------------------------------------------------------------------------
20. FILE STRUCTURE
--------------------------------------------------------------------------------

Create a repo like:

cognitive-atlas/
  README.md
  FINAL_STATUS.md
  .gitignore
  .env.example
  atlas.config.example.toml
  Makefile
  package.json
  pnpm-workspace.yaml optional
  docker-compose.yml optional

  apps/
    api/
      pyproject.toml
      README.md
      atlas_api/
        __init__.py
        main.py
        config.py
        logging_config.py
        security.py
        dependencies.py
        errors.py

        db/
          __init__.py
          connection.py
          migrations.py
          migrate.py
          schema.sql
          fts.py
          repositories.py

        models/
          __init__.py
          common.py
          sessions.py
          turns.py
          events.py
          atlas.py
          sources.py
          patches.py
          llm.py
          learning_fit.py

        services/
          __init__.py
          turn_intake.py
          context_broker.py
          topic_router.py
          research_need.py
          research_planner.py
          source_broker.py
          conversational_agent.py
          post_turn_extractor.py
          map_patch_builder.py
          map_patch_validator.py
          map_writer.py
          ui_projection.py
          export_service.py
          learning_fit.py
          command_router.py

        llm/
          __init__.py
          base.py
          fake_adapter.py
          codex_cli_adapter.py
          openai_responses_adapter.py
          prompts.py
          schemas.py

        sources/
          __init__.py
          base.py
          arxiv.py
          crossref.py
          openalex.py
          manual.py
          dedupe.py

        api/
          __init__.py
          routes_health.py
          routes_sessions.py
          routes_turns.py
          routes_atlas.py
          routes_patches.py
          routes_sources.py
          routes_search.py
          routes_exports.py
          routes_events.py

        workers/
          __init__.py
          pipeline.py
          queue.py

        util/
          __init__.py
          ids.py
          time.py
          json.py
          text.py
          token_budget.py

      tests/
        test_health.py
        test_db_migrations.py
        test_sessions.py
        test_turn_pipeline_fake.py
        test_context_broker.py
        test_map_patch_validator.py
        test_fts_search.py
        test_exports.py

    web/
      package.json
      vite.config.ts
      tsconfig.json
      index.html
      public/
        manifest.webmanifest
        icons/
      src/
        main.tsx
        App.tsx
        api/
          client.ts
          types.ts
          sessions.ts
          atlas.ts
          sources.ts
          patches.ts
        state/
          appStore.ts
        components/
          AppShell.tsx
          LeftSidebar.tsx
          MobileNav.tsx
          ConversationView.tsx
          Composer.tsx
          MessageBubble.tsx
          SessionList.tsx
          AtlasTree.tsx
          InspectorPanel.tsx
          SourceCards.tsx
          MapImpact.tsx
          QuickCapture.tsx
          SearchOverlay.tsx
          SettingsPanel.tsx
          EmptyStates.tsx
          LoadingStates.tsx
        pages/
          TalkPage.tsx
          SessionsPage.tsx
          AtlasPage.tsx
          SourcesPage.tsx
          SettingsPage.tsx
        styles/
          globals.css
          layout.css
          mobile.css
          theme.css
        utils/
          time.ts
          commands.ts
          text.ts

  schemas/
    topic_route.schema.json
    research_need.schema.json
    research_plan.schema.json
    discussion_reply.schema.json
    post_turn_extraction.schema.json
    map_patch.schema.json
    map_patch_validation.schema.json

  scripts/
    dev.sh
    test.sh
    build.sh
    run_api.sh
    run_web.sh
    migrate.sh
    create_github_repo.sh
    deploy_tailnet.sh
    install_systemd.sh
    tailscale_serve.sh
    smoke_test.sh

  deploy/
    cognitive-atlas.service
    nginx.example.conf optional
    README_tailnet.md

  docs/
    ARCHITECTURE.md
    DATA_MODEL.md
    LLM_ADAPTERS.md
    UI_PRINCIPLES.md
    DEPLOYMENT.md
    LEARNING_FIT.md

--------------------------------------------------------------------------------
21. BACKEND IMPLEMENTATION DETAILS
--------------------------------------------------------------------------------

Use async where practical.
Use dependency injection through FastAPI dependencies and service constructors.
Avoid globals except config singleton.
Use structured logs.
Handle errors.

Implement Config:
- loads env
- loads atlas.config.toml if present
- supports data dir creation
- validates paths
- exposes public config safely

Implement DB:
- async connection manager
- migration runner on startup
- schema version table
- WAL mode
- foreign keys on
- busy timeout
- row factory dict-like
- transaction helper
- repositories

IDs:
- use uuid7 if available package, else uuid4
- prefix optional:
  - ses_
  - turn_
  - map_
  - node_
  - edge_
  - claim_
  - src_
  - patch_
  - evt_

Time:
- UTC ISO timestamps

Logging:
- include request id
- include session id where known
- include task role
- no prompt content in logs by default unless debug

Security:
- if APP_ACCESS_TOKEN set:
  - require bearer token or secure cookie
- if unset:
  - allow local/tailnet operation
- add CORS config for dev frontend
- production same-origin preferred

--------------------------------------------------------------------------------
22. CODEX CLI ADAPTER DETAILS
--------------------------------------------------------------------------------

Implement CodexCliAdapter robustly.

Pseudo behavior:
- healthcheck:
  - run "codex --version" with timeout
  - return installed true/false
- complete_json:
  - create temp dir under data/codex_runs/{run_id}
  - write prompt.md
  - write schema.json
  - run:
    codex exec
      --skip-git-repo-check
      --json
      --model {model}
      --output-schema {schema_path}
      -c model_reasoning_effort={effort}
      optional --search if live search enabled for task
      -
  - stdin = prompt
  - parse stdout
  - parse final assistant message
  - validate JSON
  - if schema parse fails:
    - try extracting JSON object from final message
    - validate again
  - return result or structured error

- complete_text:
  - similar but no schema required
  - allow --output-last-message to file if useful

Avoid:
- putting whole DB in prompt
- letting model modify repo at app runtime
- yolo flags at app runtime
- shell command execution beyond Codex's internal behavior
- app crashing if Codex returns nonzero

Runtime prompt templates:
- Topic route prompt
- Research need prompt
- Research plan prompt
- Discussion prompt
- Extraction prompt
- Map patch prompt
- Validation prompt

Prompts must emphasize:
- do not infer user beliefs without evidence
- output only schema for JSON tasks
- separate user claims from assistant claims
- source-backed requires explicit source id
- be compact
- no fake citations

--------------------------------------------------------------------------------
23. PROMPT CONTENT FOR WORKERS
--------------------------------------------------------------------------------

Topic router:
- Input:
  - current turn
  - session title/summary
  - small list of existing map titles only, not full maps
- Output:
  - segments
  - candidate topics
  - existing map matches
  - new map suggestions
  - confidence
- Instruction:
  - route; do not answer user

Research detector:
- Input:
  - current turn
  - topic candidates
- Output:
  - needs_research boolean
  - reasons
  - freshness_required
  - search_intents
  - risk if answering from memory
- Instruction:
  - mark cutting-edge tech as likely needing sources

Discussion:
- Input:
  - current turn
  - recent turns
  - selected source cards only if any
  - response budget
  - mode
- Output:
  - message
  - source ids used
  - uncertainty notes
  - suggested followups
- Instruction:
  - answer user clearly
  - avoid giant response
  - do not mention backend artifacts unless asked
  - no tables unless asked
  - if sources are used, refer to them naturally

Post-turn extraction:
- Input:
  - user turn
  - assistant turn
  - source cards used
- Output:
  - claims
  - topics
  - nodes
  - edges
  - questions
  - analogies
  - latent bridges
  - forbidden user-state claims detected
- Instruction:
  - extract cognitive residue
  - preserve uncertainty
  - do not hallucinate acceptance

Map patch builder:
- Input:
  - extraction
  - target map summaries
  - existing nodes/edges relevant to targets
- Output:
  - patch
- Instruction:
  - patch, do not regenerate
  - create maps only when necessary
  - bridge when cross-domain
  - split when map too broad

Validator:
- Input:
  - patch
- Output:
  - valid
  - risk_level
  - issues
  - auto_apply
  - cleaned_patch optional
- Instruction:
  - reject fake belief memory
  - reject unsupported source-backed claims
  - cap relation overload

--------------------------------------------------------------------------------
24. UI IMPLEMENTATION DETAILS
--------------------------------------------------------------------------------

Use React with routes:
- /
- /sessions
- /sessions/:sessionId
- /atlas
- /atlas/maps/:mapId
- /sources
- /settings

Main landing:
- If no session:
  - QuickCapture centered
  - "Start with a messy thought"
- If active session:
  - open TalkPage

App state:
- currentSessionId
- inspectorOpen
- selectedMapId
- mobileTab
- theme
- responseMode
- debugMode

Components:

AppShell:
- handles desktop/mobile responsive layout
- safe areas
- global shortcuts

LeftSidebar:
- New Thought button
- Sessions list
- Atlas tree
- Search button
- collapsible sections

MobileNav:
- Talk
- Sessions
- Atlas
- Sources
- Settings optional

ConversationView:
- session title
- turns
- processing states
- feedback buttons
- map impact chips
- sources chips
- composer

Composer:
- textarea auto-resize
- send on Cmd/Ctrl+Enter
- mode selector
- command detection
- "New Thought" action
- supports paste of long text
- mobile safe area
- font size at least 16px

MessageBubble:
- user/assistant roles
- compact display
- expand long user turns
- assistant action row:
  - deepen
  - sources
  - map impact
  - fork
  - feedback

AtlasTree:
- fetched from /api/atlas/tree
- collapsible
- active/touched highlights
- no graph overload

InspectorPanel:
- tabs:
  - Impact
  - Sources
  - Questions
  - Trace
- hidden by default on mobile
- open from buttons

SourceCards:
- compact cards
- title, year, source type, relevance
- expand for abstract/key claims
- no huge raw text

MapImpact:
- shows recent patches:
  - nodes added
  - edges added
  - questions added
  - bridges suggested
- buttons:
  - undo
  - hide
  - open map

SearchOverlay:
- global search across sessions, turns, maps, claims, sources

Settings:
- provider health
- response budget
- theme
- debug
- export
- tailnet deployment notes

CSS:
- implement strong responsive design
- CSS variables:
  - --bg
  - --panel
  - --panel-elevated
  - --text
  - --muted
  - --border
  - --accent
  - --danger
  - --success
- mobile:
  - 100dvh
  - safe-area padding
  - bottom composer
- desktop:
  - left sidebar width 280
  - inspector width 360
  - main max width readable but not too narrow
- use subtle animations but respect prefers-reduced-motion

--------------------------------------------------------------------------------
25. PWA
--------------------------------------------------------------------------------

Implement:
- manifest.webmanifest
- app icons
- theme-color
- service worker for app shell caching
- offline fallback page
- installable PWA
- no aggressive caching of API responses unless safe

Safari considerations:
- apple-mobile-web-app-capable meta
- apple-mobile-web-app-title
- viewport-fit=cover
- touch icons if possible
- input font size 16px+
- avoid hover-only controls
- avoid fixed position bugs as much as possible with 100dvh and safe areas

--------------------------------------------------------------------------------
26. EXPORTS
--------------------------------------------------------------------------------

Export session markdown:
- title
- created/updated
- turns
- sources used
- map impacts
- open questions

Export map markdown:
- title
- summary
- core concepts
- relations
- claims
- tensions
- open questions
- source cards
- latent bridges
- timeline
- provenance summary

Export atlas JSON:
- full workspace excluding secrets and raw logs
- include version
- include generated_at

Export should not require LLM.

--------------------------------------------------------------------------------
27. TESTING
--------------------------------------------------------------------------------

Implement tests.

Backend tests:
- health
- config
- DB migration creates tables
- create session
- add turn with FakeLlmAdapter
- pipeline returns assistant turn
- extraction creates artifact
- map patch validator rejects fake user belief
- map patch writer applies safe patch
- FTS search works
- source broker handles failure
- export session markdown works

Frontend tests:
- if practical, minimal vitest tests for command parser and API types
- build must pass

E2E:
- optional Playwright if not too much
- at least smoke script:
  - start backend
  - create session via API
  - post turn
  - fetch atlas tree
  - fetch search

CI:
- GitHub Actions optional but nice:
  - backend tests
  - frontend build
- Do not block final if Actions setup takes too long.

--------------------------------------------------------------------------------
28. DEPLOYMENT
--------------------------------------------------------------------------------

Local dev:
- scripts/dev.sh starts backend and frontend
- backend at http://127.0.0.1:8787
- frontend dev at http://127.0.0.1:5173
- Vite proxies /api to backend

Production local:
- build frontend
- backend serves static frontend
- run:
  - scripts/build.sh
  - scripts/run_api.sh
- app at http://127.0.0.1:8787

Tailscale:
- deploy/tailnet README
- script scripts/tailscale_serve.sh:
  - checks tailscale exists
  - prints status
  - suggests:
    tailscale serve 8787
  - or:
    tailscale serve localhost:8787
- Do not require public exposure.
- Do not use Funnel.
- Bind app to localhost.

systemd:
- deploy/cognitive-atlas.service
- scripts/install_systemd.sh:
  - installs service for current user or system
  - configurable install dir
  - does not hard-code username
- Include commands in docs.

Docker:
- optional docker-compose if time:
  - one service backend serving frontend
  - volume ./data:/app/data
- Do not make Docker required.

--------------------------------------------------------------------------------
29. GITHUB
--------------------------------------------------------------------------------

After implementation:
- git init if needed
- git add .
- git commit -m "Initial cognitive atlas implementation"
- If gh exists and gh auth status succeeds:
  - gh repo create cognitive-atlas --private --source=. --remote=origin --push
- If repo exists:
  - set remote if absent
  - push
- If gh unavailable:
  - write FINAL_STATUS.md with:
    - tests run
    - how to push
    - command:
      gh repo create cognitive-atlas --private --source=. --remote=origin --push
- Never commit:
  - data/*.db
  - data/logs
  - .env
  - auth tokens
  - ~/.codex
  - secrets

--------------------------------------------------------------------------------
30. DOCUMENTATION
--------------------------------------------------------------------------------

README.md must include:
- what this is
- what it is not
- quick start
- dev start
- production start
- Tailscale access
- Codex CLI adapter setup
- fake adapter mode
- environment variables
- data location
- GitHub push
- troubleshooting

ARCHITECTURE.md:
- planes:
  - conversation
  - infrastructure
  - state/rendering
- pipeline diagram
- worker roles
- context isolation
- why not one giant map
- why map patches

DATA_MODEL.md:
- schema overview
- event sourcing
- map forest
- provenance
- epistemic status

LLM_ADAPTERS.md:
- fake adapter
- Codex CLI adapter
- future OpenAI adapter
- schemas
- prompt roles
- failure modes

UI_PRINCIPLES.md:
- no overwhelm
- progressive disclosure
- native mobile/desktop
- quick capture
- sessions
- atlas

DEPLOYMENT.md:
- Mac local
- home machine
- Tailscale Serve
- systemd
- backups

LEARNING_FIT.md:
- how to evaluate if this helps
- feedback controls
- fit report
- signs it is failing
- how to tune

--------------------------------------------------------------------------------
31. IMPLEMENTATION PHASES
--------------------------------------------------------------------------------

Phase 1:
- repo skeleton
- backend config/logging/db/migrations
- frontend shell
- scripts
- tests setup

Phase 2:
- sessions/turns/events APIs
- fake LLM pipeline
- conversation UI
- quick capture
- new sessions

Phase 3:
- atlas schema
- map patches
- extraction artifacts
- atlas tree UI
- map impact inspector

Phase 4:
- Codex CLI adapter
- JSON schema prompts
- provider health
- fallback behavior

Phase 5:
- source broker
- research tasks
- source cards UI

Phase 6:
- PWA polish
- mobile Safari polish
- desktop polish
- keyboard shortcuts

Phase 7:
- exports
- learning fit report
- deployment scripts
- docs
- tests
- commit/push

If time constraints occur:
- Do not skip core loop:
  - create session
  - post turn
  - get assistant reply
  - extract artifact
  - create/apply map patch
  - show atlas tree
- UI polish can be v0 but must be usable.

--------------------------------------------------------------------------------
32. ACCEPTANCE CRITERIA
--------------------------------------------------------------------------------

Must pass:

1. From empty directory, repo is created.
2. Backend starts.
3. Frontend starts.
4. User can open app.
5. User can create new session.
6. User can submit messy thought.
7. App returns compact assistant response.
8. App stores raw user turn.
9. App stores assistant turn.
10. App creates artifacts.
11. App updates atlas tree or no-op patch.
12. User can open session history.
13. User can create another unrelated session.
14. Both sessions can touch overarching atlas.
15. Search works.
16. Export works.
17. App works with fake LLM adapter.
18. App attempts Codex adapter if configured.
19. Missing Codex does not crash app.
20. Mobile layout works at narrow width.
21. Desktop layout works wide.
22. PWA manifest exists.
23. Tailscale serve docs/scripts exist.
24. Tests run.
25. Git commit exists.
26. GitHub push attempted when possible.

--------------------------------------------------------------------------------
33. QUALITY BAR
--------------------------------------------------------------------------------

Do not produce placeholder-only code for the core loop.
Do not leave TODOs in the main path.
Do not generate a pretty frontend with no backend.
Do not generate a backend with no usable UI.
Do not implement a generic chat app and call it done.
Do not implement a graph visualization that overwhelms.
Do not rely on API keys.
Do not require Docker.
Do not require Postgres.
Do not require cloud.
Do not lose original user text.
Do not overwrite maps destructively.
Do not put the whole atlas in the chat prompt.
Do not write fake psychology about the user.
Do not claim research happened if it did not.

Prefer boring reliable code.

--------------------------------------------------------------------------------
34. CONCRETE INITIAL SEED BEHAVIOR
--------------------------------------------------------------------------------

When the app is first opened:
- create default workspace if none exists
- show QuickCapture
- show "Start with a messy thought."
- provider banner:
  - if fake adapter: "Offline/fake LLM mode"
  - if codex healthy: "Codex CLI ready"
  - if codex missing: "Codex CLI not found; app still works in fake mode"

When first user message is submitted:
- create session title from first sentence or generated fallback
- use fake adapter if Codex not configured
- assistant says compact helpful response
- extractor creates topics
- map patch creates first map if appropriate
- atlas tree updates

Fake adapter behavior:
- For input mentioning "analog compute", create:
  - map: Analog Compute
  - nodes: analog compute, compute-in-memory, ADC/DAC overhead
  - question: how much conversion overhead erodes benefit?
- For input mentioning "agent", create:
  - map: Learning Agent Architecture
  - nodes: conversation plane, backend extraction, map forest
- For unknown input:
  - create topic based on keywords
  - simple response
  - one open question

This makes app demonstrable without Codex.

--------------------------------------------------------------------------------
35. SCHEMA EXAMPLES
--------------------------------------------------------------------------------

TopicRouteResult:
- segments:
  - text
  - start_char optional
  - end_char optional
  - candidate_topic
  - existing_map_id optional
  - confidence
- candidate_new_maps:
  - title
  - parent_hint
  - reason
  - confidence
- matched_map_ids
- notes

ResearchNeedResult:
- needs_research
- freshness_required
- reasons
- query_intents
- source_types
- priority

DiscussionReply:
- message
- response_mode
- source_ids_used
- suggested_followups
- uncertainty_notes
- should_research_more

PostTurnExtraction:
- topics
- claims
- node_candidates
- edge_candidates
- open_questions
- tensions
- analogies
- latent_bridges
- source_needs
- forbidden_user_state_claims
- notes

MapPatch:
- action
- target_map_ids
- create_maps
- add_nodes
- update_nodes
- add_edges
- add_claims
- add_questions
- add_tensions
- add_analogies
- add_latent_bridges
- confidence
- risk_level
- provenance

--------------------------------------------------------------------------------
36. EXAMPLE USER TURN HANDLING
--------------------------------------------------------------------------------

Input:
"I think analog compute and compute in memory are connected to SoC design because data movement kills you, but I also don't know whether ADC overhead makes the whole thing fake."

Human-facing answer should be compact:
"Yes — the link is data movement. Compute-in-memory tries to reduce the energy and latency of hauling operands back and forth, while analog compute can make dense MAC-like operations cheap inside or near memory. The catch is exactly what you named: ADC/DAC conversion can erase the benefit if the system needs too much precision or too much conversion per operation. So the real question is not 'does analog compute work?' but 'where does the analog block sit so conversion/control overhead does not dominate?'"

Backend extraction should create:
- topics:
  - analog compute
  - compute-in-memory
  - SoC design
- nodes:
  - data movement cost
  - ADC/DAC overhead
  - analog MAC
- edge:
  - ADC/DAC overhead constrains analog compute system efficiency
- question:
  - when does conversion overhead erase CIM/analog benefit?
- map patch:
  - update Analog Compute or create it
  - bridge to SoC architecture if exists

Main agent should not show the patch unless user opens inspector.

--------------------------------------------------------------------------------
37. IMPLEMENTATION COMMANDS
--------------------------------------------------------------------------------

Use commands as needed.
Prefer:
- uv for Python if available
- python -m venv fallback
- pnpm for frontend if available
- npm fallback

Scripts should abstract this.

Makefile targets:
- make install
- make dev
- make test
- make build
- make run
- make migrate
- make smoke
- make push

scripts/dev.sh:
- starts backend and frontend
- handles missing dependencies helpfully

scripts/build.sh:
- builds frontend
- copies dist into backend static directory or configures backend to serve it

Backend should serve static frontend in production:
- if apps/web/dist exists
- mount StaticFiles
- fallback to index.html for SPA routes

--------------------------------------------------------------------------------
38. ERROR HANDLING
--------------------------------------------------------------------------------

Create AppError types:
- NotFound
- Validation
- LlmUnavailable
- LlmMalformedOutput
- SourceSearchFailed
- PatchValidationFailed
- AuthRequired
- RateLimited
- Internal

API error shape:
- error:
  - code
  - message
  - details optional
  - request_id

Frontend:
- show friendly error
- keep user text if send fails
- retry option
- provider health indicator
- do not blank screen

--------------------------------------------------------------------------------
39. PERFORMANCE
--------------------------------------------------------------------------------

Keep v0 fast.

Backend:
- SQLite WAL
- indexes on workspace_id, session_id, map_id, updated_at
- FTS for search
- avoid loading whole DB
- paginate sessions/turns/sources
- lazy-load atlas details
- only fetch tree summaries for sidebar

Frontend:
- cache API with TanStack Query
- optimistic add user message
- skeleton loading
- no huge graph on initial load
- virtualize long sessions if easy
- truncate long messages with expand

--------------------------------------------------------------------------------
40. BACKUPS
--------------------------------------------------------------------------------

Add scripts/backup.sh if practical:
- copies SQLite DB with sqlite backup or safe copy
- writes to data/backups/
- timestamped
- excludes logs
- docs mention copying data directory to home machine

Add restore docs.

--------------------------------------------------------------------------------
41. SECURITY / PRIVACY
--------------------------------------------------------------------------------

Do not commit:
- .env
- data
- auth
- logs with prompts unless debug user chooses
- Codex run raw prompts if ATLAS_STORE_LLM_PROMPTS=false

Config:
- ATLAS_STORE_LLM_PROMPTS=false default
- ATLAS_DEBUG=false default
- ATLAS_REQUIRE_TOKEN=false default unless APP_ACCESS_TOKEN set

If storing prompts for debugging:
- store locally only
- data/codex_runs gitignored

--------------------------------------------------------------------------------
42. FINAL STATUS
--------------------------------------------------------------------------------

At the end, create FINAL_STATUS.md with:
- implemented features
- tests run and results
- build result
- how to run local dev
- how to run production
- how to expose through Tailscale
- Codex adapter status
- fake adapter status
- GitHub repo status
- known limitations
- next steps

Also print final terminal summary.

--------------------------------------------------------------------------------
43. START IMPLEMENTATION NOW
--------------------------------------------------------------------------------

You are Codex in an empty directory.

Task:
- Build this repo.
- Use the architecture above.
- Make all reasonable engineering decisions.
- Do not ask minor clarifying questions.
- If plan mode, produce full implementation plan now.
- If implementation mode, create the files and run the build/test loop.

Proceed.
