import { PropsWithChildren, useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "../api/client";
import type { PublicConfig } from "../api/types";
import { useAppStore } from "../state/appStore";
import LeftSidebar from "./LeftSidebar";
import MobileNav from "./MobileNav";
import InspectorPanel from "./InspectorPanel";
import SearchOverlay from "./SearchOverlay";

export default function AppShell({ children }: PropsWithChildren) {
  const inspectorOpen = useAppStore((state) => state.inspectorOpen);
  const setInspectorOpen = useAppStore((state) => state.setInspectorOpen);
  const [searchOpen, setSearchOpen] = useState(false);
  const config = useQuery({ queryKey: ["config"], queryFn: () => apiGet<PublicConfig>("/config/public") });

  useEffect(() => {
    const openSearch = () => setSearchOpen(true);
    const closeInspector = () => setInspectorOpen(false);
    window.addEventListener("atlas:search", openSearch);
    window.addEventListener("atlas:escape", closeInspector);
    return () => {
      window.removeEventListener("atlas:search", openSearch);
      window.removeEventListener("atlas:escape", closeInspector);
    };
  }, [setInspectorOpen]);

  const banner = config.data?.provider_health?.message || "Checking provider";

  return (
    <div className="app-shell">
      <LeftSidebar />
      <main className="main-plane">
        <div className="provider-banner" data-ready={config.data?.provider_health?.available ? "true" : "false"}>
          {banner}
        </div>
        {children}
      </main>
      {inspectorOpen && <InspectorPanel />}
      <MobileNav />
      {searchOpen && <SearchOverlay onClose={() => setSearchOpen(false)} />}
    </div>
  );
}

