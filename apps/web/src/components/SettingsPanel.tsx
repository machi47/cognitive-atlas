import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../api/client";
import type { PublicConfig } from "../api/types";

export default function SettingsPanel() {
  const config = useQuery({ queryKey: ["config"], queryFn: () => apiGet<PublicConfig>("/config/public") });
  return (
    <section className="settings-panel">
      <h1>Settings</h1>
      <div className="settings-grid">
        <article>
          <h2>Provider</h2>
          <p>{config.data?.provider_health?.message || "Checking provider"}</p>
          <small>{config.data?.llm_provider}</small>
        </article>
        <article>
          <h2>Data</h2>
          <p>{config.data?.data_dir}</p>
          <small>Local-first SQLite and artifacts.</small>
        </article>
        <article>
          <h2>Tailscale</h2>
          <p>Run the backend on localhost, then expose it with Tailscale Serve.</p>
          <code>tailscale serve localhost:8787</code>
        </article>
      </div>
    </section>
  );
}

