export type Session = {
  id: string;
  workspace_id: string;
  title: string;
  status: string;
  mode: string;
  response_budget: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  last_turn_at?: string | null;
  active_map_ids: string[];
  touched_map_ids: string[];
  metadata: Record<string, unknown>;
};

export type Turn = {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  original_content?: string | null;
  created_at: string;
  token_estimate?: number | null;
  metadata: Record<string, unknown>;
};

export type TurnResponse = {
  session: Session;
  user_turn: Turn;
  assistant_turn: Turn;
  processing_state: { status: string; steps: string[]; message?: string | null };
  artifacts_summary: { artifact_ids: string[]; patch_ids: string[]; source_ids: string[]; map_ids: string[] };
};

export type AtlasTreeMap = {
  id: string;
  title: string;
  summary?: string | null;
  status: string;
  node_count: number;
  question_count: number;
  salience: number;
  children: AtlasTreeMap[];
};

export type AtlasTree = {
  workspace_id: string;
  domains: { id: string; name: string; status: string; maps: AtlasTreeMap[] }[];
  uncategorized_maps: AtlasTreeMap[];
};

export type TopicMap = {
  id: string;
  workspace_id: string;
  title: string;
  summary?: string | null;
  status: string;
  salience: number;
  created_at: string;
  updated_at: string;
};

export type ConceptNode = {
  id: string;
  map_id: string;
  label: string;
  description?: string | null;
  node_type: string;
  epistemic_status: string;
  confidence: number;
  local_salience: number;
  global_salience: number;
  recurrence_count: number;
};

export type RelationEdge = {
  id: string;
  map_id?: string | null;
  from_node_id: string;
  to_node_id: string;
  relation_type: string;
  label?: string | null;
  description?: string | null;
  epistemic_status: string;
  confidence: number;
};

export type OpenQuestion = {
  id: string;
  session_id?: string | null;
  map_id?: string | null;
  question: string;
  status: string;
  priority: number;
};

export type MapGraph = {
  map: TopicMap;
  nodes: ConceptNode[];
  edges: RelationEdge[];
  questions: OpenQuestion[];
  latent_bridges: Record<string, unknown>[];
};

export type Patch = {
  id: string;
  status: string;
  risk_level: string;
  created_at: string;
  target_map_ids: string[];
  patch: Record<string, unknown>;
};

export type LearnContributor = {
  session_id: string;
  session_title: string;
  status?: string | null;
};

export type LearnConcept = {
  id: string;
  map_id: string;
  map_title: string;
  label: string;
  description?: string | null;
  node_type: string;
  epistemic_status: string;
  confidence: number;
  contributors: LearnContributor[];
};

export type LearnQuestion = {
  id: string;
  question: string;
  status: string;
  priority: number;
  map_title?: string | null;
  contributors: LearnContributor[];
};

export type LearnTension = {
  id: string;
  title: string;
  description: string;
  status: string;
  node_labels: string[];
  contributors: LearnContributor[];
};

export type LearnBridge = {
  id: string;
  from_label: string;
  to_label: string;
  reason: string;
  confidence: number;
  status: string;
  contributors: LearnContributor[];
};

export type LearnSourceNeed = {
  id: string;
  query: string;
  status: string;
  priority: number;
  contributors: LearnContributor[];
};

export type LearnTextbookSection = {
  title: string;
  body: string;
  bullets: string[];
  provenance?: LearnContributor[];
};

export type LearnTextbook = {
  map_id?: string | null;
  sections: LearnTextbookSection[];
  empty: boolean;
  generated_from: string[];
};

export type LearnOverview = {
  current_frame: {
    project?: string | null;
    foundation_stack: string[];
    status: string;
  };
  project_goals: LearnConcept[];
  topology: {
    maps: { id: string; title: string; summary?: string | null; concept_count: number; relation_count: number; question_count: number }[];
    concepts: LearnConcept[];
    bridges: LearnBridge[];
  };
  concepts: LearnConcept[];
  open_questions: LearnQuestion[];
  tensions: LearnTension[];
  bridges: LearnBridge[];
  source_needs: LearnSourceNeed[];
  recent_updates: Record<string, unknown>[];
  textbook: LearnTextbook;
  empty: boolean;
};

export type SourceCard = {
  id: string;
  title: string;
  url?: string | null;
  source_type: string;
  year?: number | null;
  authors: string[];
  abstract?: string | null;
  key_claims: string[];
  relevance_score: number;
};

export type PublicConfig = {
  app_name: string;
  llm_provider: string;
  debug: boolean;
  require_token: boolean;
  data_dir: string;
  provider_health: { provider_name: string; available: boolean; message: string; details?: Record<string, unknown> };
};
