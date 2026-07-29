import { useCallback, useState } from "react";
import { UploadCloud, FileText, Trash2, CheckCircle2, Loader2 } from "lucide-react";

interface Doc {
  id: string;
  name: string;
  category: string;
  chunks: number;
  ts: string;
  status: "parsing" | "chunking" | "embedding" | "indexing" | "ready";
}

const INITIAL: Doc[] = [
  { id: "1", name: "dgca_regulations_handbook.md", category: "Regulations", chunks: 342, ts: "2025-06-14 09:12", status: "ready" },
  { id: "2", name: "namo_drone_didi_2024.pdf", category: "Government Scheme", chunks: 128, ts: "2025-06-18 15:47", status: "ready" },
  { id: "3", name: "ideaforge_netra_v4_specs.pdf", category: "Specs", chunks: 87, ts: "2025-07-02 11:03", status: "ready" },
  { id: "4", name: "telangana_agri_drone_case_study.md", category: "Case Study", chunks: 54, ts: "2025-07-19 08:26", status: "ready" },
  { id: "5", name: "digitalsky_airspace.md", category: "Regulations", chunks: 96, ts: "2025-07-24 13:41", status: "ready" },
];

const STAGES: Doc["status"][] = ["parsing", "chunking", "embedding", "indexing", "ready"];
const STAGE_LABELS: Record<Doc["status"], string> = {
  parsing: "Parsing",
  chunking: "Chunking",
  embedding: "Generating Embeddings",
  indexing: "Vector Indexing",
  ready: "Ready",
};

export function DocumentsView() {
  const [docs, setDocs] = useState<Doc[]>(INITIAL);
  const [dragOver, setDragOver] = useState(false);

  const ingest = useCallback((files: File[]) => {
    files.forEach((f) => {
      const id = crypto.randomUUID();
      const category = f.name.endsWith(".pdf") ? "Specs" : "Regulations";
      const newDoc: Doc = {
        id,
        name: f.name,
        category,
        chunks: 0,
        ts: new Date().toISOString().slice(0, 16).replace("T", " "),
        status: "parsing",
      };
      setDocs((d) => [newDoc, ...d]);
      STAGES.forEach((stage, i) => {
        setTimeout(() => {
          setDocs((d) =>
            d.map((doc) =>
              doc.id === id
                ? {
                    ...doc,
                    status: stage,
                    chunks: stage === "ready" ? Math.floor(50 + Math.random() * 300) : doc.chunks,
                  }
                : doc,
            ),
          );
        }, (i + 1) * 700);
      });
    });
  }, []);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    ingest(Array.from(e.dataTransfer.files));
  };

  return (
    <div className="p-4 sm:p-6 space-y-6">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        className={`rounded-2xl border-2 border-dashed transition-all p-10 text-center ${
          dragOver
            ? "border-cyan-500 bg-cyan-500/10"
            : "border-slate-800 bg-slate-900/40 hover:border-cyan-500/40"
        }`}
      >
        <div className="mx-auto w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 grid place-items-center shadow-lg shadow-cyan-500/30 mb-4">
          <UploadCloud className="w-7 h-7 text-white" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100">Drop documents to ingest</h3>
        <p className="text-sm text-slate-400 mt-1">
          PDF · Markdown · TXT — parsed, chunked & vector-indexed for RAG retrieval
        </p>
        <label className="inline-flex mt-4 items-center gap-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/20 px-4 py-2 text-sm cursor-pointer transition">
          <UploadCloud className="w-4 h-4" /> Browse Files
          <input
            type="file"
            multiple
            accept=".pdf,.md,.txt"
            className="hidden"
            onChange={(e) => e.target.files && ingest(Array.from(e.target.files))}
          />
        </label>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Indexed Knowledge Base</h3>
            <p className="text-xs text-slate-500 mt-0.5">{docs.length} documents · {docs.reduce((s, d) => s + d.chunks, 0)} vector chunks</p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] uppercase tracking-wider text-slate-500 border-b border-slate-800">
                <th className="px-5 py-3 font-medium">File Name</th>
                <th className="px-5 py-3 font-medium">Category</th>
                <th className="px-5 py-3 font-medium">Chunks</th>
                <th className="px-5 py-3 font-medium">Ingested</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {docs.map((d) => (
                <tr
                  key={d.id}
                  className="border-b border-slate-800/60 hover:bg-slate-800/30 transition animate-fade-in"
                >
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-2 text-slate-200">
                      <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
                      <span className="font-mono text-xs truncate max-w-[280px]">{d.name}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3">
                    <span className="text-[10px] rounded-full bg-slate-800 border border-slate-700 text-slate-300 px-2 py-0.5">
                      {d.category}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-slate-300 font-mono">{d.chunks || "—"}</td>
                  <td className="px-5 py-3 text-slate-400 text-xs">{d.ts}</td>
                  <td className="px-5 py-3">
                    {d.status === "ready" ? (
                      <span className="inline-flex items-center gap-1 text-emerald-300 text-xs">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Ready
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-cyan-300 text-xs">
                        <Loader2 className="w-3.5 h-3.5 animate-spin" /> {STAGE_LABELS[d.status]}
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-3 text-right">
                    <button
                      onClick={() => setDocs((all) => all.filter((x) => x.id !== d.id))}
                      className="text-slate-500 hover:text-rose-400 transition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
