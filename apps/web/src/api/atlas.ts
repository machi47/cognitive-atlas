import { apiGet } from "./client";
import type { AtlasTree, Patch } from "./types";

export function getAtlasTree() {
  return apiGet<AtlasTree>("/atlas/tree");
}

export function getRecentPatches() {
  return apiGet<Patch[]>("/patches/recent");
}

export function searchAtlas(q: string) {
  return apiGet<Record<string, unknown[]>>(`/search?q=${encodeURIComponent(q)}`);
}

