import { apiGet, apiPost } from "./client";
import type { SourceCard } from "./types";

export function listSources() {
  return apiGet<SourceCard[]>("/sources");
}

export function searchSources(query: string) {
  return apiPost<{ sources: SourceCard[] }>("/sources/search", { query });
}

