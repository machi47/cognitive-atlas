import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { createSession, submitTurn } from "../api/sessions";
import { useAppStore } from "../state/appStore";
import Composer from "./Composer";

export default function QuickCapture() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const mode = useAppStore((state) => state.responseMode);
  const setMode = useAppStore((state) => state.setResponseMode);
  const setCurrentSessionId = useAppStore((state) => state.setCurrentSessionId);
  const capture = useMutation({
    mutationFn: async (content: string) => {
      const session = await createSession();
      setCurrentSessionId(session.id);
      await submitTurn(session.id, content, mode);
      return session;
    },
    onSuccess: (session) => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      queryClient.invalidateQueries({ queryKey: ["atlas-tree"] });
      navigate(`/sessions/${session.id}`);
    }
  });

  return (
    <section className="quick-capture">
      <div>
        <h1>Start with a messy thought.</h1>
        <p>Type or dictate the idea before it disappears. Structure can happen after the conversation.</p>
      </div>
      <Composer onSend={(content) => capture.mutate(content)} disabled={capture.isPending} mode={mode} onModeChange={setMode} />
      {capture.isPending && <div className="processing-state">creating session → replying → mapping</div>}
      {capture.error && <div className="error-state">{capture.error.message}</div>}
    </section>
  );
}

