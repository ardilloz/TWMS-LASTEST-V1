// Per-user appearance: light/dark mode + accent color. Stored in localStorage (per device, per user).
export type ThemeMode = "light" | "dark";

export type Accent = {
  id: string;
  label: string;
  primary: string;
  primaryFg: string;
  ring: string;
  sidebar: string;
  sidebarPrimary: string;
};

// Curated palettes — each retains good contrast in both light & dark shells.
export const ACCENTS: Accent[] = [
  { id: "tobacco", label: "Tembakau", primary: "#7A4A1F", primaryFg: "#FFFFFF", ring: "#D9822B", sidebar: "#29180C", sidebarPrimary: "#E69C24" },
  { id: "emerald", label: "Hijau", primary: "#047857", primaryFg: "#FFFFFF", ring: "#10B981", sidebar: "#0B2E22", sidebarPrimary: "#34D399" },
  { id: "ocean", label: "Biru", primary: "#1D4ED8", primaryFg: "#FFFFFF", ring: "#3B82F6", sidebar: "#0C1E3A", sidebarPrimary: "#60A5FA" },
  { id: "plum", label: "Ungu", primary: "#7E22CE", primaryFg: "#FFFFFF", ring: "#A855F7", sidebar: "#241033", sidebarPrimary: "#C084FC" },
  { id: "rose", label: "Merah Muda", primary: "#BE185D", primaryFg: "#FFFFFF", ring: "#EC4899", sidebar: "#36091F", sidebarPrimary: "#F472B6" },
  { id: "slate", label: "Abu Gelap", primary: "#334155", primaryFg: "#FFFFFF", ring: "#64748B", sidebar: "#0F172A", sidebarPrimary: "#94A3B8" },
];

export type ThemePref = { mode: ThemeMode; accent: string };
const DEFAULT: ThemePref = { mode: "light", accent: "tobacco" };

const keyFor = (userId?: string) => `twms-theme-${userId ?? "anon"}`;

export function loadTheme(userId?: string): ThemePref {
  try {
    const raw = localStorage.getItem(keyFor(userId));
    if (raw) return { ...DEFAULT, ...(JSON.parse(raw) as Partial<ThemePref>) };
  } catch { /* ignore */ }
  return { ...DEFAULT };
}

export function saveTheme(pref: ThemePref, userId?: string) {
  try { localStorage.setItem(keyFor(userId), JSON.stringify(pref)); } catch { /* ignore */ }
}

export function applyTheme(pref: ThemePref) {
  const root = document.documentElement;
  root.classList.toggle("dark", pref.mode === "dark");
  const a = ACCENTS.find((x) => x.id === pref.accent) ?? ACCENTS[0];
  root.style.setProperty("--primary", a.primary);
  root.style.setProperty("--primary-foreground", a.primaryFg);
  root.style.setProperty("--ring", a.ring);
  root.style.setProperty("--chart-1", a.primary);
  root.style.setProperty("--sidebar", a.sidebar);
  root.style.setProperty("--sidebar-primary", a.sidebarPrimary);
  root.style.setProperty("--sidebar-ring", a.sidebarPrimary);
}
