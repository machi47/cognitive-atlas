import { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Session } from "../api/types";
import { listTurns, submitTurn } from "../api/sessions";
import { getAtlasTree, getRecentPatches } from "../api/atlas";
import { useAppStore } from "../state/appStore";
import Composer from "./Composer";
import MessageBubble from "./MessageBubble";

export default function ConversationView({ session }: { session: Session }) {
  const queryClient = useQueryClient();
  const mode = useAppStore((state) => state.responseMode);
  const setMode = useAppStore((state) => state.setResponseMode);
  const setInspectorOpen = useAppStore((state) => state.setInspectorOpen);
  const turns = useQuery({ queryKey: ["turns", session.id], queryFn: () => listTurns(session.id) });
  const submit = useMutation({
    mutationFn: (content: string) => submitTurn(session.id, content, mode),
    onSuccess: () => {
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
        <div>
          <h1>{session.title}</h1>
          <p>{session.touched_map_ids.length ? `${session.touched_map_ids.length} maps touched` : "Ready for a messy thought"}</p>
        </div>
        <button className="ghost-action compact" onClick={() => setInspectorOpen(true)}>Inspector</button>
      </div>
      <div className="conversation-scroll">
        {turns.data?.map((turn) => <MessageBubble key={turn.id} turn={turn} onInspector={() => setInspectorOpen(true)} />)}
        {submit.isPending && <div className="processing-state">processing → mapping → updated</div>}
        {submit.error && <div className="error-state">{submit.error.message}</div>}
      </div>
      <Composer onSend={(content) => submit.mutate(content)} disabled={submit.isPending} mode={mode} onModeChange={setMode} />
    </section>
  );
}

