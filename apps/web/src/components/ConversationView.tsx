import React, { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Session } from "../api/types";
import { listTurns, submitTurn } from "../api/sessions";
import { getAtlasTree, getRecentPatches } from "../api/atlas";
import { useAppStore } from "../state/appStore";
import Composer from "./Composer";
import MessageBubble from "./MessageBubble";
import ModelErrorCard from "./ModelErrorCard";

export default function ConversationView({ session }: { session: Session }) {
  const queryClient = useQueryClient();
  const mode = useAppStore((state) => state.responseMode);
  const setInspectorOpen = useAppStore((state) => state.setInspectorOpen);
  const [clearKey, setClearKey] = React.useState(0);
  const turns = useQuery({ queryKey: ["turns", session.id], queryFn: () => listTurns(session.id) });
  const submit = useMutation({
    mutationFn: (content: string) => submitTurn(session.id, content, mode),
    onSuccess: () => {
      setClearKey((key) => key + 1);
      queryClient.invalidateQueries({ queryKey: ["turns", session.id] });
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      queryClient.invalidateQueries({ queryKey: ["atlas-tree"] });
      queryClient.invalidateQueries({ queryKey: ["recent-patches"] });
      getAtlasTree();
      getRecentPatches();
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
        <div>
          <h1>{session.title}</h1>
        </div>
        <button className="header-button" onClick={() => setInspectorOpen(true)}>...</button>
      </div>
      <div className="conversation-scroll">
        {turns.data?.map((turn) => <MessageBubble key={turn.id} turn={turn} onInspector={() => setInspectorOpen(true)} />)}
        {submit.isPending && <div className="processing-state">Thinking...</div>}
        {submit.error && <ModelErrorCard error={submit.error} onDismiss={() => submit.reset()} />}
      </div>
      <Composer onSend={(content) => submit.mutate(content)} disabled={submit.isPending} clearKey={clearKey} />
    </section>
  );
}
