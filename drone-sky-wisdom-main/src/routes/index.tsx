import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Header } from "@/components/dashboard/Header";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { ChatView, type Msg } from "@/components/dashboard/ChatView";
import { CalculatorsView } from "@/components/dashboard/CalculatorsView";
import { DocumentsView } from "@/components/dashboard/DocumentsView";
import { AnalyticsView } from "@/components/dashboard/AnalyticsView";
import type { ViewKey } from "@/components/dashboard/types";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Drone Intelligence System — India | AI Hub & MCP Tools" },
      {
        name: "description",
        content:
          "End-to-end AI Knowledge Hub for India's drone ecosystem — DGCA compliance, flight time & ROI calculators, drone recommendations, powered by RAG + MCP.",
      },
      { property: "og:title", content: "Drone Intelligence System — India" },
      {
        property: "og:description",
        content: "AI-powered knowledge hub & MCP calculator suite for India's drone ecosystem.",
      },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const [view, setView] = useState<ViewKey>("chat");
  const [collapsed, setCollapsed] = useState(false);
  const [dark, setDark] = useState(true);
  const [messages, setMessages] = useState<Msg[]>([]);

  useEffect(() => {
    const root = document.documentElement;
    if (dark) root.classList.add("dark");
    else root.classList.remove("dark");
  }, [dark]);

  const exportSession = () => {
    const blob = new Blob([JSON.stringify({ exported: new Date().toISOString(), messages }, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `drone-intel-session-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const titles: Record<ViewKey, { title: string; sub: string }> = {
    chat: { title: "AI Chat Assistant", sub: "RAG-powered agent with MCP tool execution" },
    calculators: { title: "Drone Calculators", sub: "MCP Tools Suite — India's DGCA-aligned calculations" },
    documents: { title: "Document Hub", sub: "Ingest documents into the vector knowledge base" },
    analytics: { title: "Analytics & Telemetry", sub: "System performance and query insights" },
  };
  const t = titles[view];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 relative overflow-hidden">
      {/* Ambient gradient background */}
      <div className="pointer-events-none absolute inset-0 opacity-40">
        <div className="absolute -top-40 -left-20 w-[500px] h-[500px] bg-cyan-500/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -right-40 w-[600px] h-[600px] bg-blue-600/15 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/3 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative flex h-screen">
        <Sidebar active={view} onChange={setView} collapsed={collapsed} onToggle={() => setCollapsed((c) => !c)} />

        <div className="flex-1 flex flex-col min-w-0">
          <Header dark={dark} onToggleDark={() => setDark((d) => !d)} onExport={exportSession} onClear={() => setMessages([])} />

          <div className="px-4 sm:px-6 pt-5 pb-2 border-b border-slate-800/60 bg-slate-950/40">
            <div className="text-xs uppercase tracking-wider text-cyan-400">Workspace</div>
            <div className="mt-0.5 flex items-baseline gap-3">
              <h2 className="text-xl sm:text-2xl font-bold text-slate-100">{t.title}</h2>
              <span className="text-xs text-slate-500 hidden sm:inline">{t.sub}</span>
            </div>
          </div>

          <main className="flex-1 overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.div
                key={view}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
                className="h-full overflow-y-auto"
              >
                {view === "chat" && <ChatView messages={messages} setMessages={setMessages} />}
                {view === "calculators" && <CalculatorsView />}
                {view === "documents" && <DocumentsView />}
                {view === "analytics" && <AnalyticsView />}
              </motion.div>
            </AnimatePresence>
          </main>
        </div>
      </div>
    </div>
  );
}
