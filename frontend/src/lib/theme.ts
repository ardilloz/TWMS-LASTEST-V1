// Per-user appearance: light/dark mode + accent color.
// Source of truth: the user account (synced across devices); localStorage mirrors it for instant apply.
import { apiPut } from "./api";

export type ThemeMode = "light" | "dark";

export type Accent = {
  id: string;
  label: string;
  primary: string;      // used in light mode
  primaryDark: string;  // brighter variant for dark mode
  primaryFg: string;    // text on primary (light mode)
  ring: string;
  sidebar: string;
  sidebarPrimary: string;
};

// Curated palettes — each has a light & a dark-mode primary so contrast stays good in both shells.
export const ACCENTS: Accent[] = [
  { id: "tobacco", label: "Tembakau", primary: "#7A4A1F", primaryDark: "#E69C24", primaryFg: "#FFFFFF", ring: "#D9822B", sidebar: "#29180C", sidebarPrimary: "#E69C24" },
  { id: "emerald", label: "Hijau", primary: "#047857", primaryDark: "#34D399", primaryFg: "#FFFFFF", ring: "#10B981", sidebar: "#0B2E22", sidebarPrimary: "#34D399" },
  { id: "ocean", label: "Biru", primary: "#1D4ED8", primaryDark: "#60A5FA", primaryFg: "#FFFFFF", ring: "#3B82F6", sidebar: "#0C1E3A", sidebarPrimary: "#60A5FA" },
  { id: "plum", label: "Ungu", primary: "#7E22CE", primaryDark: "#C084FC", primaryFg: "#FFFFFF", ring: "#A855F7", sidebar: "#241033", sidebarPrimary: "#C084FC" },
  { id: "rose", label: "Merah Muda", primary: "#BE185D", primaryDark: "#F472B6", primaryFg: "#FFFFFF", ring: "#EC4899", sidebar: "#36091F", sidebarPrimary: "#F472B6" },
  { id: "slate", label: "Abu Gelap", primary: "#334155", primaryDark: "#94A3B8", primaryFg: "#FFFFFF", ring: "#64748B", sidebar: "#0F172A", sidebarPrimary: "#94A3B8" },
];

export type ThemePref = { mode: ThemeMode; accent: string };
export const DEFAULT_THEME: ThemePref = { mode: "light", accent: "tobacco" };

const keyFor = (userId?: string) => `twms-theme-${userId ?? "anon"}`;

export function loadTheme(userId?: string): ThemePref {
  try {
    const raw = localStorage.getItem(keyFor(userId));
    if (raw) return { ...DEFAULT_THEME, ...(JSON.parse(raw) as Partial<ThemePref>) };
  } catch { /* ignore */ }
  return { ...DEFAULT_THEME };
}

export function saveTheme(pref: ThemePref, userId?: string) {
  try { localStorage.setItem(keyFor(userId), JSON.stringify(pref)); } catch { /* ignore */ }
}

// Persist to the logged-in user's account so it follows them to other devices.
export async function pushTheme(pref: ThemePref) {
  try { await apiPut("/meta/theme", pref); } catch { /* non-blocking */ }
}

export function applyTheme(pref: ThemePref) {
  const root = document.documentElement;
  const dark = pref.mode === "dark";
  root.classList.toggle("dark", dark);
  const a = ACCENTS.find((x) => x.id === pref.accent) ?? ACCENTS[0];
  const primary = dark ? a.primaryDark : a.primary;
  root.style.setProperty("--primary", primary);
  root.style.setProperty("--primary-foreground", dark ? "#1C1917" : a.primaryFg);
  root.style.setProperty("--ring", dark ? a.primaryDark : a.ring);
  root.style.setProperty("--chart-1", primary);
  root.style.setProperty("--sidebar", a.sidebar);
  root.style.setProperty("--sidebar-primary", a.sidebarPrimary);
  root.style.setProperty("--sidebar-primary-foreground", a.sidebar);
  root.style.setProperty("--sidebar-ring", a.sidebarPrimary);
}
