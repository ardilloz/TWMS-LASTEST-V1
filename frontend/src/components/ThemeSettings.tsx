import { useEffect, useState } from "react";
import { Check, Moon, Palette, Sun } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ACCENTS, applyTheme, loadTheme, saveTheme, type ThemePref } from "@/lib/theme";
import { cn } from "@/lib/utils";

export function ThemeSettings({ userId }: { userId?: string }) {
  const [pref, setPref] = useState<ThemePref>(() => loadTheme(userId));

  useEffect(() => {
    const p = loadTheme(userId);
    setPref(p);
    applyTheme(p);
  }, [userId]);

  const update = (patch: Partial<ThemePref>) => {
    const next = { ...pref, ...patch };
    setPref(next);
    applyTheme(next);
    saveTheme(next, userId);
  };

  return (
    <Popover>
      <PopoverTrigger
        data-testid="theme-settings-button"
        aria-label="Pengaturan tampilan"
        className="grid size-9 shrink-0 place-items-center rounded-lg border border-sidebar-border bg-sidebar-accent/50 text-sidebar-foreground transition-colors duration-150 hover:bg-sidebar-accent"
      >
        <Palette className="size-4" />
      </PopoverTrigger>
      <PopoverContent align="start" side="bottom" className="w-64" data-testid="theme-settings-panel">
        <p className="font-heading text-sm font-semibold text-foreground">Tampilan Sistem</p>
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            data-testid="theme-mode-light"
            onClick={() => update({ mode: "light" })}
            className={cn(
              "flex items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors",
              pref.mode === "light" ? "border-primary bg-primary/10 font-semibold text-foreground" : "border-border text-muted-foreground hover:bg-muted",
            )}
          >
            <Sun className="size-4" /> Terang
          </button>
          <button
            type="button"
            data-testid="theme-mode-dark"
            onClick={() => update({ mode: "dark" })}
            className={cn(
              "flex items-center justify-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors",
              pref.mode === "dark" ? "border-primary bg-primary/10 font-semibold text-foreground" : "border-border text-muted-foreground hover:bg-muted",
            )}
          >
            <Moon className="size-4" /> Gelap
          </button>
        </div>
        <p className="mt-1 text-xs font-medium text-muted-foreground">Warna Aksen</p>
        <div className="grid grid-cols-6 gap-2">
          {ACCENTS.map((a) => (
            <button
              key={a.id}
              type="button"
              title={a.label}
              data-testid={`theme-accent-${a.id}`}
              onClick={() => update({ accent: a.id })}
              style={{ backgroundColor: a.primary }}
              className={cn(
                "grid size-8 place-items-center rounded-full ring-2 ring-offset-2 ring-offset-popover transition-transform hover:scale-110",
                pref.accent === a.id ? "ring-foreground" : "ring-transparent",
              )}
            >
              {pref.accent === a.id && <Check className="size-4 text-white" />}
            </button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
}
