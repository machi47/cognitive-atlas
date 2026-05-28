import type { SourceCard } from "../api/types";

export default function SourceCards({ sources }: { sources: SourceCard[] }) {
  if (!sources.length) return <p className="muted">No source cards yet.</p>;
  return (
    <div className="source-list">
      {sources.slice(0, 5).map((source) => (
        <details key={source.id} className="source-card">
          <summary>{source.title}</summary>
          <small>{source.source_type}{source.year ? ` · ${source.year}` : ""}</small>
          {source.abstract && <p>{source.abstract}</p>}
        </details>
      ))}
    </div>
  );
}

