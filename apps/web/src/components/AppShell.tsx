import { PropsWithChildren, useEffect, useState } from "react";
import { useAppStore } from "../state/appStore";
import LeftSidebar from "./LeftSidebar";
import InspectorPanel from "./InspectorPanel";
import SearchOverlay from "./SearchOverlay";

export default function AppShell({ children }: PropsWithChildren) {
  const inspectorOpen = useAppStore((state) => state.inspectorOpen);
  const setInspectorOpen = useAppStore((state) => state.setInspectorOpen);
  const [searchOpen, setSearchOpen] = useState(false);
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

  return (
    <div className="app-shell">
      <LeftSidebar />
      <main className="main-plane">
        {children}
      </main>
      {inspectorOpen && <InspectorPanel />}
      {searchOpen && <SearchOverlay onClose={() => setSearchOpen(false)} />}
    </div>
  );
}
