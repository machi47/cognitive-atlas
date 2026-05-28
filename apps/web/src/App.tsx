import { useEffect } from "react";
import { Route, Routes, useNavigate } from "react-router-dom";
import AppShell from "./components/AppShell";
import TalkPage from "./pages/TalkPage";
import SessionsPage from "./pages/SessionsPage";
import AtlasPage from "./pages/AtlasPage";
import SourcesPage from "./pages/SourcesPage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  const navigate = useNavigate();

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const cmd = event.metaKey || event.ctrlKey;
      if (cmd && event.key.toLowerCase() === "k") {
        event.preventDefault();
        window.dispatchEvent(new CustomEvent("atlas:search"));
      }
      if (cmd && event.key.toLowerCase() === "n") {
        event.preventDefault();
        window.dispatchEvent(new CustomEvent("atlas:new-thought"));
        navigate("/");
      }
      if (event.key === "Escape") {
        window.dispatchEvent(new CustomEvent("atlas:escape"));
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [navigate]);

  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<TalkPage />} />
        <Route path="/sessions" element={<SessionsPage />} />
        <Route path="/sessions/:sessionId" element={<TalkPage />} />
        <Route path="/atlas" element={<AtlasPage />} />
        <Route path="/atlas/maps/:mapId" element={<AtlasPage />} />
        <Route path="/sources" element={<SourcesPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </AppShell>
  );
}

