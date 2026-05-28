import { NavLink } from "react-router-dom";
import type { Session } from "../api/types";
import { useAppStore } from "../state/appStore";
import { formatShortTime } from "../utils/time";

export default function SessionList({ sessions }: { sessions: Session[] }) {
  const setCurrentSessionId = useAppStore((state) => state.setCurrentSessionId);
  if (!sessions.length) return <p className="muted">No sessions yet.</p>;
  return (
    <div className="session-list">
      {sessions.map((session) => (
        <NavLink key={session.id} to={`/sessions/${session.id}`} onClick={() => setCurrentSessionId(session.id)}>
          <span>{session.title}</span>
          <small>{formatShortTime(session.last_turn_at || session.updated_at)}</small>
        </NavLink>
      ))}
    </div>
  );
}

