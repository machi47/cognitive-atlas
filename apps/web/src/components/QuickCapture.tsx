import { useMutation, useQueryClient } from "@tanstack/react-query";
import React from "react";
import { useNavigate } from "react-router-dom";
import { createSession, submitTurn } from "../api/sessions";
import { useAppStore } from "../state/appStore";
import ChatActionsMenu from "./ChatActionsMenu";
import Composer from "./Composer";
import MessageBubble from "./MessageBubble";
import ModelErrorCard from "./ModelErrorCard";

export default function QuickCapture() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const mode = useAppStore((state) => state.responseMode);
  const setCurrentSessionId = useAppStore((state) => state.setCurrentSessionId);
  const [clearKey, setClearKey] = React.useState(0);
  const [actionsOpen, setActionsOpen] = React.useState(false);
  const [pendingUserMessage, setPendingUserMessage] = React.useState<string | null>(null);
  const capture = useMutation({
    mutationFn: async (content: string) => {
      const session = await createSession();
      setCurrentSessionId(session.id);
      await submitTurn(session.id, content, mode);
      return session;
    },
    onSuccess: (session) => {
      setPendingUserMessage(null);
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
        <span className="header-spacer desktop-only" />
        <h1>New chat</h1>
        <button className="header-button" onClick={() => setActionsOpen(true)} aria-label="Chat actions">...</button>
      </div>
      <div className="conversation-scroll empty-chat-scroll">
        {!pendingUserMessage && !capture.isPending && !capture.error && (
          <div className="empty-chat-prompt">
            <h2>What are we working through?</h2>
          </div>
        )}
        {pendingUserMessage && (
          <MessageBubble
            turn={{
              id: "pending-user-turn",
              session_id: "new-session",
              role: "user",
              content: pendingUserMessage,
              created_at: new Date().toISOString(),
              metadata: {},
            }}
          />
        )}
        {capture.isPending && <div className="processing-state">Thinking...</div>}
        {capture.error && <ModelErrorCard error={capture.error} onDismiss={() => capture.reset()} />}
      </div>
      <Composer
        onSend={(content) => {
          setPendingUserMessage(content);
          capture.mutate(content);
        }}
        disabled={capture.isPending}
        clearKey={clearKey}
        onPlus={() => setActionsOpen(true)}
      />
      {actionsOpen && (
        <ChatActionsMenu
          onClose={() => setActionsOpen(false)}
          onNewChat={() => {
            setActionsOpen(false);
            navigate("/");
          }}
        />
      )}
    </section>
  );
}
