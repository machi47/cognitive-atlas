PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

CREATE TABLE IF NOT EXISTS schema_versions (
  version integer primary key,
  applied_at text not null
);

CREATE TABLE IF NOT EXISTS workspaces (
  id text primary key,
  name text not null,
  created_at text not null,
  updated_at text not null,
  settings_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS sessions (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  title text not null,
  status text not null,
  mode text not null default 'discuss',
  response_budget_json text not null,
  created_at text not null,
  updated_at text not null,
  last_turn_at text,
  user_summary text,
  system_summary text,
  active_map_ids_json text not null default '[]',
  touched_map_ids_json text not null default '[]',
  metadata_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS turns (
  id text primary key,
  session_id text not null references sessions(id) on delete cascade,
  role text not null,
  content text not null,
  original_content text,
  created_at text not null,
  token_estimate integer,
  metadata_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS events (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  session_id text references sessions(id) on delete set null,
  event_type text not null,
  aggregate_type text not null,
  aggregate_id text not null,
  payload_json text not null,
  created_at text not null,
  causation_id text,
  correlation_id text
);

CREATE TABLE IF NOT EXISTS artifacts (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  session_id text references sessions(id) on delete set null,
  turn_id text references turns(id) on delete set null,
  artifact_type text not null,
  title text,
  content_json text not null,
  status text not null,
  created_at text not null,
  metadata_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS domains (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  name text not null,
  description text,
  parent_domain_id text references domains(id) on delete set null,
  status text not null,
  created_at text not null,
  updated_at text not null
);

CREATE TABLE IF NOT EXISTS topic_maps (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  domain_id text references domains(id) on delete set null,
  parent_map_id text references topic_maps(id) on delete set null,
  title text not null,
  summary text,
  status text not null,
  created_at text not null,
  updated_at text not null,
  salience real not null default 0,
  metadata_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS concept_nodes (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  map_id text not null references topic_maps(id) on delete cascade,
  label text not null,
  description text,
  node_type text not null,
  epistemic_status text not null,
  confidence real not null default 0.5,
  local_salience real not null default 0,
  global_salience real not null default 0,
  novelty_score real not null default 0,
  bridge_potential real not null default 0,
  recurrence_count integer not null default 0,
  created_at text not null,
  updated_at text not null,
  provenance_json text not null default '[]',
  metadata_json text not null default '{}',
  unique(map_id, label)
);

CREATE TABLE IF NOT EXISTS relation_edges (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  map_id text references topic_maps(id) on delete cascade,
  from_node_id text not null references concept_nodes(id) on delete cascade,
  to_node_id text not null references concept_nodes(id) on delete cascade,
  relation_type text not null,
  label text,
  description text,
  epistemic_status text not null,
  confidence real not null default 0.5,
  salience real not null default 0,
  created_at text not null,
  updated_at text not null,
  provenance_json text not null default '[]',
  metadata_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS claims (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  session_id text references sessions(id) on delete set null,
  map_id text references topic_maps(id) on delete set null,
  node_id text references concept_nodes(id) on delete set null,
  text text not null,
  claim_type text not null,
  epistemic_status text not null,
  confidence real not null default 0.5,
  created_at text not null,
  updated_at text not null,
  provenance_json text not null default '[]',
  source_ids_json text not null default '[]',
  metadata_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS open_questions (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  session_id text references sessions(id) on delete set null,
  map_id text references topic_maps(id) on delete cascade,
  question text not null,
  status text not null,
  priority real not null default 0,
  created_at text not null,
  updated_at text not null,
  provenance_json text not null default '[]',
  metadata_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS tensions (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  map_id text references topic_maps(id) on delete cascade,
  title text not null,
  description text not null,
  status text not null,
  created_at text not null,
  updated_at text not null,
  node_ids_json text not null default '[]',
  claim_ids_json text not null default '[]',
  provenance_json text not null default '[]'
);

CREATE TABLE IF NOT EXISTS analogies (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  map_id text references topic_maps(id) on delete cascade,
  source_concept text not null,
  target_concept text not null,
  useful_because text,
  breaks_at text,
  status text not null,
  confidence real not null default 0.5,
  created_at text not null,
  provenance_json text not null default '[]'
);

CREATE TABLE IF NOT EXISTS latent_bridges (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  from_node_id text not null references concept_nodes(id) on delete cascade,
  to_node_id text not null references concept_nodes(id) on delete cascade,
  bridge_type text not null,
  reason text not null,
  confidence real not null default 0.5,
  status text not null,
  discovered_by text not null,
  created_at text not null,
  updated_at text not null,
  evidence_artifact_ids_json text not null default '[]',
  metadata_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS map_patches (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  session_id text references sessions(id) on delete set null,
  turn_id text references turns(id) on delete set null,
  target_map_ids_json text not null,
  patch_json text not null,
  status text not null,
  risk_level text not null,
  created_at text not null,
  applied_at text,
  rejected_at text,
  metadata_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS source_cards (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  title text not null,
  url text,
  doi text,
  arxiv_id text,
  source_type text not null,
  year integer,
  authors_json text not null default '[]',
  venue text,
  abstract text,
  key_claims_json text not null default '[]',
  limitations_json text not null default '[]',
  relevance_score real not null default 0,
  credibility_score real not null default 0,
  freshness_score real not null default 0,
  created_at text not null,
  updated_at text not null,
  metadata_json text not null default '{}'
);

CREATE TABLE IF NOT EXISTS research_tasks (
  id text primary key,
  workspace_id text not null references workspaces(id) on delete cascade,
  session_id text references sessions(id) on delete set null,
  turn_id text references turns(id) on delete set null,
  query text not null,
  task_type text not null,
  status text not null,
  priority real not null default 0,
  created_at text not null,
  updated_at text not null,
  result_artifact_id text references artifacts(id) on delete set null,
  metadata_json text not null default '{}'
);

CREATE VIRTUAL TABLE IF NOT EXISTS turns_fts USING fts5(turn_id UNINDEXED, session_id UNINDEXED, content);
CREATE VIRTUAL TABLE IF NOT EXISTS concept_nodes_fts USING fts5(node_id UNINDEXED, map_id UNINDEXED, label, description);
CREATE VIRTUAL TABLE IF NOT EXISTS claims_fts USING fts5(claim_id UNINDEXED, session_id UNINDEXED, text);
CREATE VIRTUAL TABLE IF NOT EXISTS source_cards_fts USING fts5(source_id UNINDEXED, title, abstract, key_claims);
CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(session_id UNINDEXED, title, summary);

CREATE INDEX IF NOT EXISTS idx_sessions_workspace_updated ON sessions(workspace_id, updated_at desc);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_turns_session_created ON turns(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_events_workspace_created ON events(workspace_id, created_at desc);
CREATE INDEX IF NOT EXISTS idx_artifacts_session_created ON artifacts(session_id, created_at desc);
CREATE INDEX IF NOT EXISTS idx_topic_maps_workspace_updated ON topic_maps(workspace_id, updated_at desc);
CREATE INDEX IF NOT EXISTS idx_concept_nodes_map ON concept_nodes(map_id);
CREATE INDEX IF NOT EXISTS idx_relation_edges_map ON relation_edges(map_id);
CREATE INDEX IF NOT EXISTS idx_claims_workspace_updated ON claims(workspace_id, updated_at desc);
CREATE INDEX IF NOT EXISTS idx_open_questions_map ON open_questions(map_id);
CREATE INDEX IF NOT EXISTS idx_map_patches_workspace_created ON map_patches(workspace_id, created_at desc);
CREATE INDEX IF NOT EXISTS idx_source_cards_workspace_updated ON source_cards(workspace_id, updated_at desc);
CREATE INDEX IF NOT EXISTS idx_research_tasks_status ON research_tasks(workspace_id, status);

