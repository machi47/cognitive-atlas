import { apiPost } from "./client";
import type { Patch } from "./types";

export function rejectPatch(patchId: string) {
  return apiPost<Patch>(`/patches/${patchId}/reject`);
}

export function undoPatch(patchId: string) {
  return apiPost<Patch>(`/patches/${patchId}/undo`);
}

