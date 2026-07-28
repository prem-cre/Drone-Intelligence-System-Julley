import { Download, Moon, Sun, Trash2, ShieldCheck } from "lucide-react";

interface Props {
  dark: boolean;
  onToggleDark: () => void;
  onExport: () => void;
  onClear: () => void;
}

export function Header({ dark, onToggleDark, onExport, onClear }: Props) {
  return (
    <header className="h-16 shrink-0 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl flex items-center px-6 gap-4">
      <div className="flex items-center gap-3 min-w-0">
        <h1 className="text-base sm:text-lg font-semibold text-slate-100 truncate">
          Drone Intelligence System <span className="text-slate-500">—</span>{" "}
          <span className="bg-gradient-to-r from-cyan-400 to-emerald-400 bg-clip-text text-transparent">India</span>
        </h1>
      </div>

      <div className="hidden md:flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 pl-2 pr-3 py-1">
        <span className="relative flex w-2 h-2">
          <span className="absolute inline-flex w-full h-full rounded-full bg-emerald-400 opacity-60 animate-ping" />
          <span className="relative inline-flex w-2 h-2 rounded-full bg-emerald-400" />
        </span>
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span className="text-[11px] font-medium text-emerald-300 tracking-wide">
          System Operational · DGCA Rules 2021
        </span>
      </div>

      <div className="ml-auto flex items-center gap-2">
        <button
          onClick={onExport}
          className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-1.5 text-xs text-slate-300 hover:text-cyan-300 hover:border-cyan-500/40 transition"
        >
          <Download className="w-3.5 h-3.5" /> Export
        </button>
        <button
          onClick={onClear}
          className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-1.5 text-xs text-slate-300 hover:text-rose-300 hover:border-rose-500/40 transition"
        >
          <Trash2 className="w-3.5 h-3.5" /> Clear
        </button>
        <button
          onClick={onToggleDark}
          className="inline-flex items-center justify-center w-9 h-9 rounded-lg border border-slate-800 bg-slate-900/60 text-slate-300 hover:text-cyan-300 hover:border-cyan-500/40 transition"
          aria-label="Toggle theme"
        >
          {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </div>
    </header>
  );
}
