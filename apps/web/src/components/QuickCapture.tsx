import { useMutation, useQueryClient } from "@tanstack/react-query";
import React from "react";
import { useNavigate } from "react-router-dom";
import { createSession, submitTurn } from "../api/sessions";
import { useAppStore } from "../state/appStore";
import Composer from "./Composer";
import ModelErrorCard from "./ModelErrorCard";

export default function QuickCapture() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const mode = useAppStore((state) => state.responseMode);
  const setCurrentSessionId = useAppStore((state) => state.setCurrentSessionId);
  const [clearKey, setClearKey] = React.useState(0);
  const capture = useMutation({
    mutationFn: async (content: string) => {
      const session = await createSession();
      setCurrentSessionId(session.id);
      await submitTurn(session.id, content, mode);
      return session;
    },
    onSuccess: (session) => {
      setClearKey((key) => key + 1);
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      queryClient.invalidateQueries({ queryKey: ["atlas-tree"] });
      navigate(`/sessions/${session.id}`);
    }
  });

  return (
    <section className="quick-capture">
      <div className="session-header empty-chat-header">
        <a className="header-button mobile-only" href="/sessions">Chats</a>
        <h1>New chat</h1>
        <span className="header-spacer" />
      </div>
      <div className="conversation-scroll empty-chat-scroll">
        {capture.isPending && <div className="processing-state">Thinking...</div>}
        {capture.error && <ModelErrorCard error={capture.error} onDismiss={() => capture.reset()} />}
      </div>
      <Composer onSend={(content) => capture.mutate(content)} disabled={capture.isPending} clearKey={clearKey} />
    </section>
  );
}
