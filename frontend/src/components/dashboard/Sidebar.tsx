import { Bot, Calculator, FolderUp, LineChart, Plane, ChevronLeft } from "lucide-react";
import type { ViewKey } from "./types";

const items: { key: ViewKey; label: string; icon: typeof Bot; hint: string }[] = [
  { key: "chat", label: "AI Chat Assistant", icon: Bot, hint: "RAG + MCP Agent" },
  { key: "calculators", label: "Drone Calculators", icon: Calculator, hint: "MCP Tools Suite" },
  { key: "documents", label: "Document Hub", icon: FolderUp, hint: "Vector Ingestion" },
  { key: "analytics", label: "Analytics", icon: LineChart, hint: "System Telemetry" },
];

interface Props {
  active: ViewKey;
  onChange: (k: ViewKey) => void;
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ active, onChange, collapsed, onToggle }: Props) {
  return (
    <aside
      className={`${collapsed ? "w-20" : "w-64"} shrink-0 transition-all duration-300 border-r border-slate-800/80 bg-slate-950/80 backdrop-blur-xl flex flex-col`}
    >
      <div className="h-16 flex items-center gap-3 px-4 border-b border-slate-800/80">
        <div className="relative shrink-0">
          <div className="absolute inset-0 bg-cyan-500/40 blur-lg rounded-full" />
          <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 grid place-items-center shadow-lg shadow-cyan-500/30">
            <Plane className="w-5 h-5 text-white" />
          </div>
        </div>
        {!collapsed && (
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-slate-100 truncate">Drone Intel</div>
            <div className="text-[10px] text-cyan-400 uppercase tracking-wider">India OS</div>
          </div>
        )}
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {items.map((it) => {
          const Icon = it.icon;
          const isActive = active === it.key;
          return (
            <button
              key={it.key}
              onClick={() => onChange(it.key)}
              className={`w-full group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all ${
                isActive
                  ? "bg-gradient-to-r from-cyan-500/15 to-blue-500/10 text-cyan-300 border border-cyan-500/30"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/50 border border-transparent"
              }`}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full bg-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.8)]" />
              )}
              <Icon className={`w-5 h-5 shrink-0 ${isActive ? "text-cyan-400" : ""}`} />
              {!collapsed && (
                <div className="flex-1 text-left min-w-0">
                  <div className="font-medium truncate">{it.label}</div>
                  <div className="text-[10px] text-slate-500 truncate">{it.hint}</div>
                </div>
              )}
            </button>
          );
        })}
      </nav>

      <button
        onClick={onToggle}
        className="m-3 flex items-center justify-center gap-2 rounded-lg border border-slate-800 bg-slate-900/60 py-2 text-xs text-slate-400 hover:text-cyan-300 hover:border-cyan-500/40 transition"
      >
        <ChevronLeft className={`w-4 h-4 transition-transform ${collapsed ? "rotate-180" : ""}`} />
        {!collapsed && <span>Collapse</span>}
      </button>
    </aside>
  );
}
