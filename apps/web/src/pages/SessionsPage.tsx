import { useQuery } from "@tanstack/react-query";
import { listSessions } from "../api/sessions";
import SessionList from "../components/SessionList";

export default function SessionsPage() {
  const sessions = useQuery({ queryKey: ["sessions"], queryFn: listSessions });
  return (
    <section className="page-panel">
      <h1>Sessions</h1>
      <SessionList sessions={sessions.data || []} />
    </section>
  );
}

