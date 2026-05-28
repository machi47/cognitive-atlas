import { useQuery } from "@tanstack/react-query";
import { getRecentPatches } from "../api/atlas";
import { listSources } from "../api/sources";
import { useAppStore } from "../state/appStore";
import MapImpact from "./MapImpact";
import SourceCards from "./SourceCards";

export default function InspectorPanel() {
  const setInspectorOpen = useAppStore((state) => state.setInspectorOpen);
  const patches = useQuery({ queryKey: ["recent-patches"], queryFn: getRecentPatches });
  const sources = useQuery({ queryKey: ["sources"], queryFn: listSources });
  return (
    <aside className="inspector-panel">
      <div className="inspector-header">
        <h2>Inspector</h2>
        <button className="icon-button" onClick={() => setInspectorOpen(false)} aria-label="Close inspector">×</button>
      </div>
      <section>
        <h3>Impact</h3>
        <MapImpact patches={patches.data || []} />
      </section>
      <section>
        <h3>Sources</h3>
        <SourceCards sources={sources.data || []} />
      </section>
      <section>
        <h3>Questions</h3>
        <p className="muted">Open questions are shown on each map after extraction.</p>
      </section>
      <section>
        <h3>Trace</h3>
        <p className="muted">Debug traces stay out of the main conversation.</p>
      </section>
    </aside>
  );
}

