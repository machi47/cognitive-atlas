import React, { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import type { Session } from "../api/types";
import { createSession, deleteSession, forkSession, listTurns, submitTurn } from "../api/sessions";
import { getAtlasTree, getRecentPatches } from "../api/atlas";
import { useAppStore } from "../state/appStore";
import ChatActionsMenu from "./ChatActionsMenu";
import Composer from "./Composer";
import MessageBubble from "./MessageBubble";
import ModelErrorCard from "./ModelErrorCard";

export default function ConversationView({ session }: { session: Session }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const mode = useAppStore((state) => state.responseMode);
  const setInspectorOpen = useAppStore((state) => state.setInspectorOpen);
  const setCurrentSessionId = useAppStore((state) => state.setCurrentSessionId);
  const [clearKey, setClearKey] = React.useState(0);
  const [actionsOpen, setActionsOpen] = React.useState(false);
  const [pendingUserMessage, setPendingUserMessage] = React.useState<string | null>(null);
  const turns = useQuery({ queryKey: ["turns", session.id], queryFn: () => listTurns(session.id) });
  const submit = useMutation({
    mutationFn: (content: string) => submitTurn(session.id, content, mode),
    onSuccess: () => {
      setPendingUserMessage(null);
      setClearKey((key) => key + 1);
      queryClient.invalidateQueries({ queryKey: ["turns", session.id] });
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      queryClient.invalidateQueries({ queryKey: ["atlas-tree"] });
      queryClient.invalidateQueries({ queryKey: ["recent-patches"] });
      getAtlasTree();
      getRecentPatches();
    }
  });
  const create = useMutation({
    mutationFn: () => createSession(),
    onSuccess: (created) => {
      setCurrentSessionId(created.id);
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      navigate(`/sessions/${created.id}`);
    }
  });
  const fork = useMutation({
    mutationFn: () => forkSession(session.id),
    onSuccess: (created) => {
      setCurrentSessionId(created.id);
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      navigate(`/sessions/${created.id}`);
    }
  });
  const remove = useMutation({
    mutationFn: () => deleteSession(session.id),
    onSuccess: () => {
      setCurrentSessionId(null);
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      navigate("/");
    }
  });

  useEffect(() => {
    const element = document.querySelector(".conversation-scroll");
    element?.scrollTo({ top: element.scrollHeight, behavior: "smooth" });
  }, [turns.data?.length, submit.isPending]);

  return (
    <section className="conversation-view">
      <div className="session-header">
        <a className="header-button mobile-only" href="/sessions">Chats</a>
        <span className="header-spacer desktop-only" />
        <div>
          <h1>{session.title}</h1>
        </div>
        <button className="header-button" onClick={() => setActionsOpen(true)} aria-label="Chat actions">...</button>
      </div>
      <div className="conversation-scroll">
        {turns.data?.map((turn) => <MessageBubble key={turn.id} turn={turn} onInspector={() => setInspectorOpen(true)} />)}
        {pendingUserMessage && (
          <MessageBubble
            turn={{
              id: "pending-user-turn",
              session_id: session.id,
              role: "user",
              content: pendingUserMessage,
              created_at: new Date().toISOString(),
              metadata: {},
            }}
            onInspector={() => setInspectorOpen(true)}
          />
        )}
        {submit.isPending && <div className="processing-state">Thinking...</div>}
        {submit.error && <ModelErrorCard error={submit.error} onDismiss={() => submit.reset()} />}
      </div>
      <Composer
        onSend={(content) => {
          setPendingUserMessage(content);
          submit.mutate(content);
        }}
        disabled={submit.isPending}
        clearKey={clearKey}
        onPlus={() => setActionsOpen(true)}
      />
      {actionsOpen && (
        <ChatActionsMenu
          session={session}
          onClose={() => setActionsOpen(false)}
          onNewChat={() => create.mutate()}
          onFork={() => fork.mutate()}
          onInspector={() => {
            setInspectorOpen(true);
            setActionsOpen(false);
          }}
          onDelete={() => {
            if (confirm(`Delete "${session.title}"? This removes the chat history.`)) {
              remove.mutate();
            }
          }}
        />
      )}
    </section>
  );
}
