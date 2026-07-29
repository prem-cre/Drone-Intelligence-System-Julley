import { useEffect, useState } from "react";
import { Activity, Database, Gauge, Layers } from "lucide-react";
import {
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const queryData = [
  { day: "Mon", queries: 142, latency: 320 },
  { day: "Tue", queries: 198, latency: 285 },
  { day: "Wed", queries: 267, latency: 302 },
  { day: "Thu", queries: 231, latency: 268 },
  { day: "Fri", queries: 312, latency: 254 },
  { day: "Sat", queries: 189, latency: 240 },
  { day: "Sun", queries: 156, latency: 232 },
];

const intentData = [
  { name: "RAG Knowledge", value: 42, color: "#06b6d4" },
  { name: "MCP Calculators", value: 31, color: "#10b981" },
  { name: "Compliance Checks", value: 18, color: "#3b82f6" },
  { name: "Drone Recommendations", value: 9, color: "#f59e0b" },
];

const telemetry = Array.from({ length: 40 }, () => ({
  wind: +(Math.random() * 30).toFixed(1),
  battery: +(60 + Math.random() * 40).toFixed(1),
}));

export function AnalyticsView() {
  const [metrics, setMetrics] = useState({
    total_queries: "1,495",
    avg_latency_ms: "271",
    top_category: "Agriculture",
    vector_chunks: "49",
  });

  useEffect(() => {
    fetch("http://localhost:8000/api/analytics")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.total_queries) {
          setMetrics({
            total_queries: data.total_queries.toLocaleString(),
            avg_latency_ms: String(data.avg_latency_ms),
            top_category: data.top_category,
            vector_chunks: String(data.vector_chunks),
          });
        }
      })
      .catch(() => {});
  }, []);

  const stats = [
    { icon: Activity, label: "Total Queries", value: metrics.total_queries, tone: "cyan", hint: "Last 7 days" },
    { icon: Gauge, label: "Avg Latency", value: `${metrics.avg_latency_ms} ms`, tone: "emerald", hint: "P50 response" },
    { icon: Layers, label: "Top Category", value: metrics.top_category, tone: "amber", hint: "38% of queries" },
    { icon: Database, label: "Vector Chunks", value: metrics.vector_chunks, tone: "blue", hint: "Indexed ChromaDB" },
  ];

  return (
    <div className="p-4 sm:p-6 space-y-4">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <div
              key={s.label}
              className="animate-fade-in rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md p-5"
            >
              <div className="flex items-center justify-between">
                <div className="text-[10px] uppercase tracking-wider text-slate-500">{s.label}</div>
                <Icon
                  className={`w-4 h-4 ${
                    s.tone === "cyan"
                      ? "text-cyan-400"
                      : s.tone === "emerald"
                      ? "text-emerald-400"
                      : s.tone === "amber"
                      ? "text-amber-400"
                      : "text-blue-400"
                  }`}
                />
              </div>
              <div className="text-2xl font-bold text-slate-100 mt-2">{s.value}</div>
              <div className="text-[10px] text-slate-500 mt-1">{s.hint}</div>
            </div>
          );
        })}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md p-5">
          <h3 className="text-sm font-semibold text-slate-100 mb-3">Queries & System Performance (7d)</h3>
          <div className="h-64">
            <ResponsiveContainer>
              <LineChart data={queryData}>
                <CartesianGrid stroke="rgb(30 41 59)" strokeDasharray="3 3" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis yAxisId="l" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis yAxisId="r" orientation="right" stroke="#64748b" fontSize={10} tickLine={false} />
                <Tooltip contentStyle={{ background: "rgb(2 6 23)", border: "1px solid rgb(30 41 59)", borderRadius: 8 }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line yAxisId="l" type="monotone" dataKey="queries" stroke="#06b6d4" strokeWidth={2} dot={{ r: 3 }} />
                <Line yAxisId="r" type="monotone" dataKey="latency" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md p-5">
          <h3 className="text-sm font-semibold text-slate-100 mb-3">User Intent & Popular Queries</h3>
          <div className="h-64">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={intentData} dataKey="value" innerRadius={45} outerRadius={80} paddingAngle={3}>
                  {intentData.map((d) => (
                    <Cell key={d.name} fill={d.color} stroke="rgb(15 23 42)" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "rgb(2 6 23)", border: "1px solid rgb(30 41 59)", borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-1.5 mt-2">
            {intentData.map((d) => (
              <div key={d.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ background: d.color }} />
                  <span className="text-slate-300">{d.name}</span>
                </div>
                <span className="text-slate-400 font-mono">{d.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md p-5">
        <h3 className="text-sm font-semibold text-slate-100 mb-3">Flight Telemetry — Battery Consumption vs Wind Speed</h3>
        <div className="h-64">
          <ResponsiveContainer>
            <ScatterChart>
              <CartesianGrid stroke="rgb(30 41 59)" strokeDasharray="3 3" />
              <XAxis type="number" dataKey="wind" name="Wind" unit="km/h" stroke="#64748b" fontSize={11} />
              <YAxis type="number" dataKey="battery" name="Battery Use" unit="%" stroke="#64748b" fontSize={11} />
              <Tooltip contentStyle={{ background: "rgb(2 6 23)", border: "1px solid rgb(30 41 59)", borderRadius: 8 }} cursor={{ strokeDasharray: "3 3" }} />
              <Scatter data={telemetry} fill="#06b6d4" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
