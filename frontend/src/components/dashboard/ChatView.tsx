import { useEffect, useRef, useState } from "react";
import { Send, Sparkles, Bot, User, BookOpen, Wrench, ChevronDown, Paperclip, Loader2 } from "lucide-react";
import { api, type ChatResponse } from "@/services/api";

interface Msg {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
  ts: number;
}

const QUICK_PROMPTS = [
  "What are DGCA rules for micro drones in green zones?",
  "Calculate flight time for 10000mAh battery & 2kg payload",
  "Check ROI for 500-acre agricultural spraying drone in Telangana",
  "Recommend an agricultural spraying drone under ₹8 Lakhs",
];

export function ChatView({ messages, setMessages }: {
  messages: Msg[];
  setMessages: React.Dispatch<React.SetStateAction<Msg[]>>;
}) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    textRef.current?.focus();
  }, []);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: Msg = { id: crypto.randomUUID(), role: "user", content: text, ts: Date.now() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.chat(text);
      setMessages((m) => [
        ...m,
        { id: crypto.randomUUID(), role: "assistant", content: res.answer, response: res, ts: Date.now() },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "⚠️ The intelligence agent is temporarily unavailable. Please retry.",
          ts: Date.now(),
        },
      ]);
    } finally {
      setLoading(false);
      textRef.current?.focus();
    }
  };

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Quick prompts */}
      <div className="px-4 sm:px-6 pt-4">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="inline-flex items-center gap-1.5 text-[11px] uppercase tracking-wider text-slate-500">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Quick Prompts
          </span>
          {QUICK_PROMPTS.map((p) => (
            <button
              key={p}
              onClick={() => send(p)}
              disabled={loading}
              className="text-xs rounded-full border border-slate-800 bg-slate-900/60 hover:border-cyan-500/50 hover:text-cyan-300 text-slate-300 px-3 py-1.5 transition disabled:opacity-50"
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Feed */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-6">
        {messages.length === 0 && <EmptyState onPick={send} />}
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex gap-3 animate-fade-in ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
              {m.role === "assistant" && (
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 grid place-items-center shrink-0 shadow-lg shadow-cyan-500/20">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <div className={`max-w-[85%] ${m.role === "user" ? "order-first" : ""}`}>
                {m.role === "user" ? (
                  <div className="rounded-2xl rounded-tr-sm bg-gradient-to-br from-cyan-500 to-blue-600 text-white px-4 py-2.5 shadow-lg shadow-cyan-500/10">
                    {m.content}
                  </div>
                ) : (
                  <AssistantMessage msg={m} />
                )}
              </div>
              {m.role === "user" && (
                <div className="w-9 h-9 rounded-xl bg-slate-800 border border-slate-700 grid place-items-center shrink-0">
                  <User className="w-4 h-4 text-slate-300" />
                </div>
              )}
            </div>
          ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 grid place-items-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="rounded-2xl bg-slate-900/60 border border-slate-800 px-4 py-3 flex items-center gap-2 text-slate-400 text-sm">
              <Loader2 className="w-4 h-4 animate-spin text-cyan-400" /> Analyzing knowledge base & MCP tools…
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-slate-800/80 bg-slate-950/70 backdrop-blur-xl p-4">
        <div className="relative flex items-end gap-2 rounded-2xl border border-slate-800 bg-slate-900/70 focus-within:border-cyan-500/50 focus-within:shadow-[0_0_0_3px_rgba(6,182,212,0.1)] transition p-2">
          <button className="w-9 h-9 grid place-items-center rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-slate-800/60">
            <Paperclip className="w-4 h-4" />
          </button>
          <textarea
            ref={textRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            rows={1}
            placeholder="Ask about DGCA rules, calculate flight time, ROI, or drone recommendations…"
            className="flex-1 resize-none bg-transparent text-sm text-slate-100 placeholder:text-slate-500 outline-none max-h-40 py-2"
          />
          <button
            onClick={() => send(input)}
            disabled={!input.trim() || loading}
            className="h-9 px-4 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5 shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/40 transition-shadow"
          >
            <Send className="w-3.5 h-3.5" /> Send
          </button>
        </div>
        <div className="mt-2 text-[10px] text-slate-500 flex justify-between px-1">
          <span>Enter to send · Shift+Enter for newline</span>
          <span>MCP Tools · RAG · DGCA 2021</span>
        </div>
      </div>
    </div>
  );
}

function EmptyState({ onPick }: { onPick: (s: string) => void }) {
  return (
    <div className="max-w-2xl mx-auto text-center pt-8">
      <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-2xl shadow-cyan-500/40 items-center justify-center mb-4">
        <Bot className="w-8 h-8 text-white" />
      </div>
      <h2 className="text-2xl font-semibold text-slate-100">
        Ask India's <span className="text-cyan-400">Drone Intelligence</span> Agent
      </h2>
      <p className="mt-2 text-sm text-slate-400">
        RAG-powered knowledge across DGCA regulations, MCP calculators, and India's drone ecosystem.
      </p>
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
        {QUICK_PROMPTS.map((p) => (
          <button
            key={p}
            onClick={() => onPick(p)}
            className="rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-sm text-slate-300 hover:border-cyan-500/40 hover:text-cyan-200 transition"
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  );
}

function AssistantMessage({ msg }: { msg: Msg }) {
  const [showCitations, setShowCitations] = useState(false);
  const res = msg.response;

  return (
    <div className="rounded-2xl rounded-tl-sm border border-slate-800 bg-slate-900/70 backdrop-blur-md">
      <div className="px-4 py-3">
        <Markdown text={msg.content} />
      </div>

      {res?.tool_calls?.map((tc, idx) => (
        <ToolCallCard key={idx} tc={tc} />
      ))}

      {res?.citations && res.citations.length > 0 && (
        <div className="border-t border-slate-800">
          <button
            onClick={() => setShowCitations((s) => !s)}
            className="w-full flex items-center justify-between px-4 py-2 text-xs text-slate-400 hover:text-cyan-300 transition"
          >
            <span className="inline-flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5" /> {res.citations.length} Sources & Citations
            </span>
            <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showCitations ? "rotate-180" : ""}`} />
          </button>
          {showCitations && (
            <div className="px-4 pb-3 space-y-2">
              {res.citations.map((c, i) => (
                    <div key={i} className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-medium text-slate-200 truncate">{c.title}</span>
                        <span className="text-[10px] rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 px-2 py-0.5">
                          {(c.score * 100).toFixed(0)}% match
                        </span>
                      </div>
                      <div className="mt-1 text-[10px] font-mono text-cyan-400">{c.source}</div>
                      <p className="mt-1.5 text-xs text-slate-400 italic">"{c.snippet}"</p>
                    </div>
                  ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ToolCallCard({ tc }: { tc: { tool_name: string; output: Record<string, unknown> } }) {
  const entries = Object.entries(tc.output).filter(
    ([, v]) => typeof v === "string" || typeof v === "number",
  );
  return (
    <div className="mx-4 mb-3 rounded-xl border border-cyan-500/30 bg-gradient-to-br from-cyan-500/10 via-blue-500/5 to-transparent p-3">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-6 h-6 rounded-md bg-cyan-500/20 grid place-items-center">
          <Wrench className="w-3 h-3 text-cyan-300" />
        </div>
        <span className="text-[11px] uppercase tracking-wider text-cyan-300 font-medium">
          MCP Tool: {tc.tool_name}
        </span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        {entries.slice(0, 6).map(([k, v]) => (
          <div key={k} className="rounded-lg bg-slate-950/50 border border-slate-800 p-2">
            <div className="text-[10px] uppercase text-slate-500 tracking-wide">{k.replace(/_/g, " ")}</div>
            <div className="text-sm font-semibold text-slate-100">{String(v)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Lightweight markdown renderer (headings, bold, lists, code, blockquote)
function Markdown({ text }: { text: string }) {
  const lines = text.split("\n");
  const blocks: React.ReactNode[] = [];
  let list: string[] = [];
  const flushList = (i: number) => {
    if (list.length) {
      blocks.push(
        <ul key={`ul-${i}`} className="my-2 space-y-1 pl-4 list-disc marker:text-cyan-400">
          {list.map((li, k) => (
            <li key={k} className="text-sm text-slate-300">
              {inline(li)}
            </li>
          ))}
        </ul>,
      );
      list = [];
    }
  };

  lines.forEach((raw, i) => {
    const line = raw;
    if (line.startsWith("### ")) {
      flushList(i);
      blocks.push(
        <h3 key={i} className="mt-2 mb-1 text-base font-semibold text-cyan-300">
          {line.slice(4)}
        </h3>,
      );
    } else if (line.startsWith("## ")) {
      flushList(i);
      blocks.push(
        <h2 key={i} className="mt-2 mb-1 text-lg font-semibold text-slate-100">
          {line.slice(3)}
        </h2>,
      );
    } else if (line.startsWith("> ")) {
      flushList(i);
      blocks.push(
        <blockquote key={i} className="my-2 border-l-2 border-cyan-500/60 pl-3 text-sm text-slate-400 italic">
          {inline(line.slice(2))}
        </blockquote>,
      );
    } else if (/^[-*] /.test(line)) {
      list.push(line.replace(/^[-*] /, ""));
    } else if (/^\d+\.\s/.test(line)) {
      list.push(line.replace(/^\d+\.\s/, ""));
    } else if (line.trim() === "") {
      flushList(i);
    } else {
      flushList(i);
      blocks.push(
        <p key={i} className="my-1 text-sm text-slate-300 leading-relaxed">
          {inline(line)}
        </p>,
      );
    }
  });
  flushList(lines.length);
  return <div className="space-y-0.5">{blocks}</div>;
}

function inline(text: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  const regex = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let k = 0;
  while ((m = regex.exec(text))) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    const t = m[0];
    if (t.startsWith("**"))
      parts.push(
        <strong key={k++} className="font-semibold text-slate-100">
          {t.slice(2, -2)}
        </strong>,
      );
    else
      parts.push(
        <code key={k++} className="rounded bg-slate-800 border border-slate-700 px-1.5 py-0.5 text-[11px] text-cyan-300 font-mono">
          {t.slice(1, -1)}
        </code>,
      );
    last = m.index + t.length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

export type { Msg };
