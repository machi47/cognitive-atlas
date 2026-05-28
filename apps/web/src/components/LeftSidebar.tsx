import { Plus, Search } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { createSession, listSessions } from "../api/sessions";
import { getAtlasTree } from "../api/atlas";
import { useAppStore } from "../state/appStore";
import SessionList from "./SessionList";
import AtlasTree from "./AtlasTree";

export default function LeftSidebar() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const setCurrentSessionId = useAppStore((state) => state.setCurrentSessionId);
  const sessions = useQuery({ queryKey: ["sessions"], queryFn: listSessions });
  const atlas = useQuery({ queryKey: ["atlas-tree"], queryFn: getAtlasTree });
  const create = useMutation({
    mutationFn: () => createSession(),
    onSuccess: (session) => {
      setCurrentSessionId(session.id);
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      navigate(`/sessions/${session.id}`);
    }
  });

  return (
    <aside className="left-sidebar">
      <div className="brand">
        <span className="brand-mark" />
        <strong>Cognitive Atlas</strong>
      </div>
      <button className="primary-action" onClick={() => create.mutate()}>
        <Plus size={18} /> New Thought
      </button>
      <button className="ghost-action" onClick={() => window.dispatchEvent(new CustomEvent("atlas:search"))}>
        <Search size={16} /> Search
      </button>
      <section>
        <h2>Sessions</h2>
        <SessionList sessions={sessions.data || []} />
      </section>
      <section>
        <h2>Atlas</h2>
        <AtlasTree tree={atlas.data} />
      </section>
    </aside>
  );
}

