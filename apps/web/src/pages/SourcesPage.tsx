import { useQuery } from "@tanstack/react-query";
import { listSources } from "../api/sources";
import SourceCards from "../components/SourceCards";

export default function SourcesPage() {
  const sources = useQuery({ queryKey: ["sources"], queryFn: listSources });
  return (
    <section className="page-panel">
      <h1>Sources</h1>
      <SourceCards sources={sources.data || []} />
    </section>
  );
}

