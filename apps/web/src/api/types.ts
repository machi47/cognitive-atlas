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

export type Patch = {
  id: string;
  status: string;
  risk_level: string;
  created_at: string;
  target_map_ids: string[];
  patch: Record<string, unknown>;
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

