import { Plus } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { createSession, deleteSession, listSessions } from "../api/sessions";
import SessionList from "../components/SessionList";
import { useAppStore } from "../state/appStore";

export default function SessionsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const setCurrentSessionId = useAppStore((state) => state.setCurrentSessionId);
  const sessions = useQuery({ queryKey: ["sessions"], queryFn: listSessions });
  const create = useMutation({
    mutationFn: () => createSession(),
    onSuccess: (session) => {
      setCurrentSessionId(session.id);
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      navigate(`/sessions/${session.id}`);
    }
  });
  const remove = useMutation({
    mutationFn: deleteSession,
    onSuccess: (_, sessionId) => {
      if (window.localStorage.getItem("atlas.currentSessionId") === sessionId) {
        setCurrentSessionId(null);
      }
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      navigate("/sessions");
    }
  });
  return (
    <section className="page-panel">
      <div className="page-header-row">
        <h1>Chats</h1>
        <button className="primary-action" onClick={() => create.mutate()}><Plus size={18} /> New chat</button>
      </div>
      <SessionList
        sessions={sessions.data || []}
        onDelete={(session) => {
          if (confirm(`Delete "${session.title}"? This removes the chat history.`)) {
            remove.mutate(session.id);
          }
        }}
      />
    </section>
  );
}
