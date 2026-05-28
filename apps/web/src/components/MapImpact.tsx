import type { Patch } from "../api/types";
import { formatShortTime } from "../utils/time";

export default function MapImpact({ patches }: { patches: Patch[] }) {
  if (!patches.length) return <p className="muted">No map changes yet.</p>;
  return (
    <div className="impact-list">
      {patches.slice(0, 5).map((patch) => (
        <article key={patch.id} className="impact-item">
          <strong>{patch.status}</strong>
          <span>{patch.risk_level} risk · {formatShortTime(patch.created_at)}</span>
          <small>{patch.target_map_ids.length} target maps</small>
        </article>
      ))}
    </div>
  );
}

