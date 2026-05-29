import { apiGet } from "./client";
import type { AtlasTree, LearnOverview, LearnTextbook, MapGraph, Patch, TopicMap } from "./types";

export function getAtlasTree() {
  return apiGet<AtlasTree>("/atlas/tree");
}

export function listMaps() {
  return apiGet<TopicMap[]>("/atlas/maps");
}

export function getMapGraph(mapId: string) {
  return apiGet<MapGraph>(`/atlas/maps/${mapId}/graph`);
}

export function getRecentPatches() {
  return apiGet<Patch[]>("/patches/recent");
}

export function searchAtlas(q: string) {
  return apiGet<Record<string, unknown[]>>(`/search?q=${encodeURIComponent(q)}`);
}

export function getLearnOverview() {
  return apiGet<LearnOverview>("/learn/overview");
}

export function getLearnTextbook() {
  return apiGet<LearnTextbook>("/learn/textbook");
}
