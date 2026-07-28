import { useState, useEffect } from "react";
import { Header } from "@/components/dashboard/Header";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { ChatView, type Msg } from "@/components/dashboard/ChatView";
import { CalculatorsView } from "@/components/dashboard/CalculatorsView";
import { DocumentsView } from "@/components/dashboard/DocumentsView";
import { AnalyticsView } from "@/components/dashboard/AnalyticsView";
import type { ViewKey } from "@/components/dashboard/types";

export default function App() {
  const [view, setView] = useState<ViewKey>("chat");
  const [collapsed, setCollapsed] = useState(false);
  const [dark, setDark] = useState(true);
  const [messages, setMessages] = useState<Msg[]>([]);

  useEffect(() => {
    if (dark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [dark]);

  const viewTitles: Record<ViewKey, { title: string; sub: string }> = {
    chat: {
      title: "AI Chat Assistant",
      sub: "RAG Knowledge Retrieval & MCP Tool Agent",
    },
    calculators: {
      title: "Drone Calculators Suite",
      sub: "Flight Time, ROI, DGCA Compliance & Model Recommendation",
    },
    documents: {
      title: "Document Hub & Vector Ingestion",
      sub: "Manage & seed regulatory handbook documents into ChromaDB",
    },
    analytics: {
      title: "Analytics & Telemetry Dashboard",
      sub: "System usage statistics, latency, and flight telemetry logs",
    },
  };

  const t = viewTitles[view];

  const exportSession = () => {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(messages, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute(
      "download",
      `drone_intel_session_${Date.now()}.json`
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased selection:bg-cyan-500 selection:text-white">
      {/* Ambient gradient background */}
      <div className="pointer-events-none absolute inset-0 opacity-40">
        <div className="absolute -top-40 -left-20 w-[500px] h-[500px] bg-cyan-500/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -right-40 w-[600px] h-[600px] bg-blue-600/15 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/3 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative flex h-screen">
        <Sidebar
          active={view}
          onChange={setView}
          collapsed={collapsed}
          onToggle={() => setCollapsed((c) => !c)}
        />

        <div className="flex-1 flex flex-col min-w-0">
          <Header
            dark={dark}
            onToggleDark={() => setDark((d) => !d)}
            onExport={exportSession}
            onClear={() => setMessages([])}
          />

          <div className="px-4 sm:px-6 pt-5 pb-2 border-b border-slate-800/60 bg-slate-950/40">
            <div className="text-xs uppercase tracking-wider text-cyan-400">
              Workspace
            </div>
            <div className="mt-0.5 flex items-baseline gap-3">
              <h2 className="text-xl sm:text-2xl font-bold text-slate-100">
                {t.title}
              </h2>
              <span className="text-xs text-slate-500 hidden sm:inline">
                {t.sub}
              </span>
            </div>
          </div>

          <main className="flex-1 overflow-hidden">
            <div key={view} className="h-full overflow-y-auto">
              {view === "chat" && (
                <ChatView messages={messages} setMessages={setMessages} />
              )}
              {view === "calculators" && <CalculatorsView />}
              {view === "documents" && <DocumentsView />}
              {view === "analytics" && <AnalyticsView />}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
