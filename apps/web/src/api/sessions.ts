import { apiGet, apiPatch, apiPost } from "./client";
import type { Session, Turn, TurnResponse } from "./types";

export function listSessions() {
  return apiGet<Session[]>("/sessions");
}

export function createSession(title?: string) {
  return apiPost<Session>("/sessions", { title });
}

export function getSession(sessionId: string) {
  return apiGet<Session>(`/sessions/${sessionId}`);
}

export function renameSession(sessionId: string, title: string) {
  return apiPatch<Session>(`/sessions/${sessionId}`, { title });
}

export function archiveSession(sessionId: string) {
  return apiPost<Session>(`/sessions/${sessionId}/archive`);
}

export function forkSession(sessionId: string) {
  return apiPost<Session>(`/sessions/${sessionId}/fork`);
}

export function listTurns(sessionId: string) {
  return apiGet<Turn[]>(`/sessions/${sessionId}/turns`);
}

export function submitTurn(sessionId: string, content: string, mode: string) {
  return apiPost<TurnResponse>(`/sessions/${sessionId}/turns`, { content, mode });
}

