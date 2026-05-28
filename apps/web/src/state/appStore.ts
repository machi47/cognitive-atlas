import { create } from "zustand";

type MobileTab = "talk" | "sessions" | "atlas" | "sources" | "settings";

type AppStore = {
  currentSessionId: string | null;
  inspectorOpen: boolean;
  selectedMapId: string | null;
  mobileTab: MobileTab;
  theme: "system" | "light" | "dark";
  responseMode: string;
  debugMode: boolean;
  setCurrentSessionId: (id: string | null) => void;
  setInspectorOpen: (open: boolean) => void;
  setSelectedMapId: (id: string | null) => void;
  setMobileTab: (tab: MobileTab) => void;
  setResponseMode: (mode: string) => void;
  setTheme: (theme: "system" | "light" | "dark") => void;
  setDebugMode: (debug: boolean) => void;
};

export const useAppStore = create<AppStore>((set) => ({
  currentSessionId: window.localStorage.getItem("atlas.currentSessionId"),
  inspectorOpen: window.innerWidth >= 960,
  selectedMapId: null,
  mobileTab: "talk",
  theme: "system",
  responseMode: "discuss",
  debugMode: false,
  setCurrentSessionId: (id) => {
    if (id) window.localStorage.setItem("atlas.currentSessionId", id);
    else window.localStorage.removeItem("atlas.currentSessionId");
    set({ currentSessionId: id });
  },
  setInspectorOpen: (open) => set({ inspectorOpen: open }),
  setSelectedMapId: (id) => set({ selectedMapId: id }),
  setMobileTab: (tab) => set({ mobileTab: tab }),
  setResponseMode: (mode) => set({ responseMode: mode }),
  setTheme: (theme) => set({ theme }),
  setDebugMode: (debug) => set({ debugMode: debug })
}));

