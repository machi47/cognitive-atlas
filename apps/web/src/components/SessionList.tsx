import { Trash2 } from "lucide-react";
import { NavLink } from "react-router-dom";
import type { Session } from "../api/types";
import { useAppStore } from "../state/appStore";
import { formatShortTime } from "../utils/time";

export default function SessionList({ sessions, onDelete }: { sessions: Session[]; onDelete?: (session: Session) => void }) {
  const setCurrentSessionId = useAppStore((state) => state.setCurrentSessionId);
  if (!sessions.length) return <p className="muted">No sessions yet.</p>;
  return (
    <div className="session-list">
      {sessions.map((session) => (
        <div className="session-list-row" key={session.id}>
          <NavLink to={`/sessions/${session.id}`} onClick={() => setCurrentSessionId(session.id)}>
            <span>{session.title}</span>
            <small>{formatShortTime(session.last_turn_at || session.updated_at)}</small>
          </NavLink>
          {onDelete && (
            <button className="icon-button danger-button" aria-label={`Delete ${session.title}`} onClick={() => onDelete(session)}>
              <Trash2 size={16} />
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
