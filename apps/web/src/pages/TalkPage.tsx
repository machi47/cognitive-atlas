import { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate, useParams } from "react-router-dom";
import { createSession, getSession } from "../api/sessions";
import { useAppStore } from "../state/appStore";
import ConversationView from "../components/ConversationView";
import QuickCapture from "../components/QuickCapture";
import { LoadingState } from "../components/LoadingStates";

export default function TalkPage() {
  const params = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const setCurrentSessionId = useAppStore((state) => state.setCurrentSessionId);
  const sessionId = params.sessionId || null;
  const session = useQuery({ queryKey: ["session", sessionId], queryFn: () => getSession(sessionId!), enabled: Boolean(sessionId) });
  const create = useMutation({
    mutationFn: () => createSession(),
    onSuccess: (created) => {
      setCurrentSessionId(created.id);
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      navigate(`/sessions/${created.id}`);
    }
  });

  useEffect(() => {
    const newThought = () => create.mutate();
    window.addEventListener("atlas:new-thought", newThought);
    return () => window.removeEventListener("atlas:new-thought", newThought);
  }, [create]);

  useEffect(() => {
    if (params.sessionId) setCurrentSessionId(params.sessionId);
  }, [params.sessionId, setCurrentSessionId]);

  if (!sessionId) return <QuickCapture />;
  if (session.isLoading) return <LoadingState />;
  if (!session.data) return <QuickCapture />;
  return <ConversationView session={session.data} />;
}
