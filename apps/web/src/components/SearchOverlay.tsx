import { FormEvent, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { searchAtlas } from "../api/atlas";

export default function SearchOverlay({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState("");
  const results = useQuery({ queryKey: ["search", submitted], queryFn: () => searchAtlas(submitted), enabled: submitted.length > 1 });
  const submit = (event: FormEvent) => {
    event.preventDefault();
    setSubmitted(query);
  };
  return (
    <div className="overlay-backdrop">
      <div className="search-overlay">
        <form onSubmit={submit}>
          <input value={query} onChange={(event) => setQuery(event.target.value)} autoFocus placeholder="Search sessions, turns, maps, claims, sources" />
          <button>Search</button>
          <button type="button" onClick={onClose}>Close</button>
        </form>
        <div className="search-results">
          {results.data && Object.entries(results.data).map(([group, items]) => (
            <section key={group}>
              <h3>{group}</h3>
              {(items as Record<string, unknown>[]).slice(0, 8).map((item, index) => (
                <pre key={index}>{JSON.stringify(item, null, 2)}</pre>
              ))}
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}

