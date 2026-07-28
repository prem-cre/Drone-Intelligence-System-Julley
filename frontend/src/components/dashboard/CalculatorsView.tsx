import { useEffect, useState } from "react";
import {
  Battery,
  Coins,
  ShieldCheck,
  Search,
  Wind,
  Thermometer,
  Weight,
  Gauge,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Award,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  api,
  type ComplianceResponse,
  type DroneModel,
  type FlightTimeResponse,
  type RoiResponse,
} from "@/services/api";

type Tab = "flight" | "roi" | "compliance" | "select";

const TABS: { key: Tab; label: string; icon: typeof Battery; color: string }[] = [
  { key: "flight", label: "Flight Time & Range", icon: Battery, color: "cyan" },
  { key: "roi", label: "Agriculture & ROI", icon: Coins, color: "emerald" },
  { key: "compliance", label: "DGCA Compliance", icon: ShieldCheck, color: "blue" },
  { key: "select", label: "Drone Selection", icon: Search, color: "amber" },
];

export function CalculatorsView() {
  const [tab, setTab] = useState<Tab>("flight");

  return (
    <div className="p-4 sm:p-6 space-y-4">
      <div className="flex flex-wrap gap-2">
        {TABS.map((t) => {
          const Icon = t.icon;
          const active = tab === t.key;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`relative inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                active
                  ? "text-white bg-gradient-to-r from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20"
                  : "text-slate-300 border border-slate-800 bg-slate-900/60 hover:border-cyan-500/40 hover:text-cyan-200"
              }`}
            >
              <Icon className="w-4 h-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={tab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2 }}
        >
          {tab === "flight" && <FlightCalc />}
          {tab === "roi" && <RoiCalc />}
          {tab === "compliance" && <ComplianceCalc />}
          {tab === "select" && <DroneSelect />}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

// ============ SHARED ============

function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md ${className}`}>
      {children}
    </div>
  );
}

function Slider({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  unit,
  icon: Icon,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  icon?: typeof Battery;
}) {
  return (
    <div>
      <div className="flex items-center justify-between text-xs mb-2">
        <span className="inline-flex items-center gap-1.5 text-slate-400">
          {Icon && <Icon className="w-3.5 h-3.5 text-cyan-400" />} {label}
        </span>
        <span className="text-cyan-300 font-mono font-semibold">
          {value.toLocaleString()} {unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(+e.target.value)}
        className="w-full accent-cyan-500 h-1.5"
      />
    </div>
  );
}

function Stat({
  label,
  value,
  hint,
  tone = "cyan",
}: {
  label: string;
  value: string | number;
  hint?: string;
  tone?: "cyan" | "emerald" | "amber" | "rose" | "blue";
}) {
  const toneMap = {
    cyan: "from-cyan-500/20 to-cyan-500/0 border-cyan-500/30 text-cyan-300",
    emerald: "from-emerald-500/20 to-emerald-500/0 border-emerald-500/30 text-emerald-300",
    amber: "from-amber-500/20 to-amber-500/0 border-amber-500/30 text-amber-300",
    rose: "from-rose-500/20 to-rose-500/0 border-rose-500/30 text-rose-300",
    blue: "from-blue-500/20 to-blue-500/0 border-blue-500/30 text-blue-300",
  }[tone];
  return (
    <div className={`rounded-xl border bg-gradient-to-br ${toneMap} p-4`}>
      <div className="text-[10px] uppercase tracking-wider opacity-80">{label}</div>
      <div className="mt-1 text-2xl font-bold text-slate-100">{value}</div>
      {hint && <div className="mt-1 text-[10px] text-slate-500">{hint}</div>}
    </div>
  );
}

// ============ FLIGHT TIME ============

function FlightCalc() {
  const [battery, setBattery] = useState(10000);
  const [weight, setWeight] = useState(3);
  const [payload, setPayload] = useState(2);
  const [wind, setWind] = useState(10);
  const [temp, setTemp] = useState(28);
  const [res, setRes] = useState<FlightTimeResponse | null>(null);

  useEffect(() => {
    let cancel = false;
    api
      .flightTime({ battery_mah: battery, empty_weight: weight, payload, wind, temperature: temp })
      .then((r) => !cancel && setRes(r));
    return () => {
      cancel = true;
    };
  }, [battery, weight, payload, wind, temp]);

  const pct = res ? Math.min(1, res.flight_time_mins / 60) : 0;

  return (
    <div className="grid lg:grid-cols-2 gap-4">
      <Card className="p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
          <Battery className="w-4 h-4 text-cyan-400" /> Flight Parameters
        </h3>
        <Slider label="Battery Capacity" value={battery} onChange={setBattery} min={2000} max={30000} step={500} unit="mAh" icon={Battery} />
        <Slider label="Drone Empty Weight" value={weight} onChange={setWeight} min={0.25} max={20} step={0.25} unit="kg" icon={Weight} />
        <Slider label="Payload Weight" value={payload} onChange={setPayload} min={0} max={15} step={0.5} unit="kg" />
        <Slider label="Wind Speed" value={wind} onChange={setWind} min={0} max={40} step={1} unit="km/h" icon={Wind} />
        <Slider label="Temperature" value={temp} onChange={setTemp} min={-5} max={50} step={1} unit="°C" icon={Thermometer} />
      </Card>

      <div className="space-y-4">
        <Card className="p-5">
          <div className="flex items-center gap-4">
            <div className="relative w-32 h-32 shrink-0">
              <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
                <circle cx="60" cy="60" r="52" fill="none" stroke="rgb(30 41 59)" strokeWidth="10" />
                <circle
                  cx="60"
                  cy="60"
                  r="52"
                  fill="none"
                  stroke="url(#g)"
                  strokeWidth="10"
                  strokeLinecap="round"
                  strokeDasharray={2 * Math.PI * 52}
                  strokeDashoffset={2 * Math.PI * 52 * (1 - pct)}
                  className="transition-all duration-500"
                />
                <defs>
                  <linearGradient id="g" x1="0" x2="1">
                    <stop offset="0" stopColor="#06b6d4" />
                    <stop offset="1" stopColor="#10b981" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className="text-2xl font-bold text-slate-100">{res?.flight_time_mins ?? "—"}</div>
                <div className="text-[10px] text-slate-500 uppercase">Minutes</div>
              </div>
            </div>
            <div className="flex-1 grid grid-cols-2 gap-2">
              <Stat label="Max Range" value={`${res?.max_range_km ?? 0} km`} tone="cyan" />
              <Stat label="Battery Used" value={`${res?.battery_consumed_pct ?? 0}%`} tone="emerald" />
            </div>
          </div>
          {res && (
            <div className="mt-4 flex items-start gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 p-3">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <p className="text-xs text-amber-200/90">{res.advice}</p>
            </div>
          )}
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2 mb-3">
            <Gauge className="w-4 h-4 text-cyan-400" />
            <span className="text-sm font-semibold text-slate-100">Power Consumption Curve</span>
          </div>
          <div className="h-40">
            <ResponsiveContainer>
              <LineChart data={res?.power_curve ?? []}>
                <CartesianGrid stroke="rgb(30 41 59)" strokeDasharray="3 3" />
                <XAxis dataKey="minute" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} unit="%" />
                <Tooltip contentStyle={{ background: "rgb(2 6 23)", border: "1px solid rgb(30 41 59)", borderRadius: 8 }} />
                <Line type="monotone" dataKey="power" stroke="#06b6d4" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}

// ============ ROI ============

function RoiCalc() {
  const [sector, setSector] = useState("Agriculture");
  const [investment, setInvestment] = useState(750000);
  const [opex, setOpex] = useState(25000);
  const [fee, setFee] = useState(400);
  const [acres, setAcres] = useState(500);
  const [subsidy, setSubsidy] = useState(50);
  const [res, setRes] = useState<RoiResponse | null>(null);

  useEffect(() => {
    let c = false;
    api
      .roi({ sector, investment, monthly_opex: opex, fee_per_acre: fee, monthly_acres: acres, subsidy_pct: subsidy })
      .then((r) => !c && setRes(r));
    return () => {
      c = true;
    };
  }, [sector, investment, opex, fee, acres, subsidy]);

  return (
    <div className="grid lg:grid-cols-2 gap-4">
      <Card className="p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
          <Coins className="w-4 h-4 text-emerald-400" /> Business Parameters
        </h3>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Sector</label>
          <select
            value={sector}
            onChange={(e) => setSector(e.target.value)}
            className="w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-emerald-500/50 outline-none"
          >
            <option>Agriculture</option>
            <option>Mapping</option>
            <option>Logistics</option>
          </select>
        </div>
        <NumInput label="Initial Investment (₹)" value={investment} setValue={setInvestment} step={10000} />
        <NumInput label="Monthly Operating Cost (₹)" value={opex} setValue={setOpex} step={1000} />
        <NumInput label="Service Fee per Acre (₹)" value={fee} setValue={setFee} step={25} />
        <Slider label="Expected Monthly Acres" value={acres} onChange={setAcres} min={50} max={1000} step={10} unit="ac" />
        <div>
          <div className="text-xs text-slate-400 mb-2">Government Subsidy</div>
          <div className="flex gap-2">
            {[0, 40, 50, 80].map((s) => (
              <button
                key={s}
                onClick={() => setSubsidy(s)}
                className={`flex-1 rounded-lg py-2 text-xs font-medium border transition ${
                  subsidy === s
                    ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-300"
                    : "border-slate-800 bg-slate-950/60 text-slate-400 hover:border-emerald-500/30"
                }`}
              >
                {s}%
              </button>
            ))}
          </div>
          <div className="mt-1.5 text-[10px] text-slate-500">80% under Namo Drone Didi (women SHGs)</div>
        </div>
      </Card>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Stat label="Monthly Revenue" value={`₹${(res?.monthly_revenue ?? 0).toLocaleString("en-IN")}`} tone="cyan" />
          <Stat label="Net Profit / Month" value={`₹${(res?.net_monthly_profit ?? 0).toLocaleString("en-IN")}`} tone="emerald" />
          <Stat
            label="Payback Period"
            value={res?.payback_months && res.payback_months < 999 ? `${res.payback_months} mo` : "—"}
            tone="amber"
          />
          <Stat label="3-Year ROI" value={`${res?.roi_3yr_pct ?? 0}%`} tone="blue" />
        </div>

        <Card className="p-5">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-semibold text-slate-100">3-Year Profitability Projection</span>
          </div>
          <div className="h-56">
            <ResponsiveContainer>
              <BarChart data={res?.projection ?? []}>
                <CartesianGrid stroke="rgb(30 41 59)" strokeDasharray="3 3" />
                <XAxis dataKey="year" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} tickFormatter={(v) => `₹${(v / 100000).toFixed(0)}L`} />
                <Tooltip
                  contentStyle={{ background: "rgb(2 6 23)", border: "1px solid rgb(30 41 59)", borderRadius: 8 }}
                  formatter={(v: number) => `₹${v.toLocaleString("en-IN")}`}
                />
                <Bar dataKey="revenue" fill="#06b6d4" radius={[6, 6, 0, 0]} />
                <Bar dataKey="profit" fill="#10b981" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}

function NumInput({
  label,
  value,
  setValue,
  step = 1,
}: {
  label: string;
  value: number;
  setValue: (v: number) => void;
  step?: number;
}) {
  return (
    <div>
      <label className="text-xs text-slate-400 mb-1 block">{label}</label>
      <input
        type="number"
        value={value}
        step={step}
        onChange={(e) => setValue(+e.target.value)}
        className="w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-emerald-500/50 outline-none"
      />
    </div>
  );
}

// ============ COMPLIANCE ============

function ComplianceCalc() {
  const [weightCat, setWeightCat] = useState("Small");
  const [purpose, setPurpose] = useState("Commercial");
  const [zone, setZone] = useState<"Green" | "Yellow" | "Red">("Green");
  const [altitude, setAltitude] = useState(200);
  const [rpc, setRpc] = useState(true);
  const [res, setRes] = useState<ComplianceResponse | null>(null);

  useEffect(() => {
    let c = false;
    api.compliance({ weight_category: weightCat, purpose, zone, altitude, rpc }).then((r) => !c && setRes(r));
    return () => {
      c = true;
    };
  }, [weightCat, purpose, zone, altitude, rpc]);

  const statusConfig = {
    APPROVED: { color: "emerald", Icon: CheckCircle2, label: "Approved for Flight" },
    RESTRICTED: { color: "amber", Icon: AlertTriangle, label: "Requires Permits" },
    PROHIBITED: { color: "rose", Icon: XCircle, label: "Flight Prohibited" },
  } as const;
  const cfg = res ? statusConfig[res.status] : null;

  return (
    <div className="grid lg:grid-cols-2 gap-4">
      <Card className="p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-blue-400" /> Operation Details
        </h3>
        <Select label="Drone Weight Category (MTOW)" value={weightCat} onChange={setWeightCat} options={["Nano", "Micro", "Small", "Medium", "Large"]} />
        <Select label="Purpose" value={purpose} onChange={setPurpose} options={["Commercial", "Defense", "R&D", "Hobby"]} />
        <div>
          <label className="text-xs text-slate-400 mb-2 block">Operating Airspace Zone</label>
          <div className="grid grid-cols-3 gap-2">
            {(["Green", "Yellow", "Red"] as const).map((z) => {
              const tone = z === "Green" ? "emerald" : z === "Yellow" ? "amber" : "rose";
              const active = zone === z;
              return (
                <button
                  key={z}
                  onClick={() => setZone(z)}
                  className={`rounded-lg py-2 text-xs font-medium border transition ${
                    active
                      ? tone === "emerald"
                        ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-300"
                        : tone === "amber"
                        ? "bg-amber-500/20 border-amber-500/50 text-amber-300"
                        : "bg-rose-500/20 border-rose-500/50 text-rose-300"
                      : "border-slate-800 bg-slate-950/60 text-slate-400"
                  }`}
                >
                  {z} Zone
                </button>
              );
            })}
          </div>
        </div>
        <Slider label="Altitude" value={altitude} onChange={setAltitude} min={50} max={1000} step={50} unit="ft" />
        <label className="flex items-center gap-3 text-sm text-slate-300 cursor-pointer">
          <input type="checkbox" checked={rpc} onChange={(e) => setRpc(e.target.checked)} className="accent-cyan-500 w-4 h-4" />
          Pilot holds valid Remote Pilot Certificate (RPC)
        </label>
      </Card>

      <div className="space-y-4">
        {cfg && res && (
          <Card
            className={`p-5 ${
              cfg.color === "emerald"
                ? "border-emerald-500/40 bg-gradient-to-br from-emerald-500/15 to-transparent"
                : cfg.color === "amber"
                ? "border-amber-500/40 bg-gradient-to-br from-amber-500/15 to-transparent"
                : "border-rose-500/40 bg-gradient-to-br from-rose-500/15 to-transparent"
            }`}
          >
            <div className="flex items-center gap-3">
              <cfg.Icon
                className={`w-8 h-8 ${
                  cfg.color === "emerald" ? "text-emerald-400" : cfg.color === "amber" ? "text-amber-400" : "text-rose-400"
                }`}
              />
              <div>
                <div className="text-[10px] uppercase tracking-wider text-slate-400">Compliance Status</div>
                <div
                  className={`text-xl font-bold ${
                    cfg.color === "emerald"
                      ? "text-emerald-300"
                      : cfg.color === "amber"
                      ? "text-amber-300"
                      : "text-rose-300"
                  }`}
                >
                  {res.status} · {cfg.label}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">{res.zone}</div>
              </div>
            </div>
          </Card>
        )}

        {res && res.permits.length > 0 && (
          <Card className="p-5">
            <div className="text-sm font-semibold text-slate-100 mb-3">Required Permits & Licenses</div>
            <ul className="space-y-2">
              {res.permits.map((p) => (
                <li key={p} className="flex items-start gap-2 text-sm text-slate-300">
                  <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                  {p}
                </li>
              ))}
            </ul>
          </Card>
        )}

        {res && (
          <Card className="p-5">
            <div className="text-sm font-semibold text-slate-100 mb-3">DigitalSky Approval Workflow</div>
            <ol className="space-y-2">
              {res.workflow.map((w, i) => (
                <li key={w} className="flex items-start gap-3 text-sm text-slate-300">
                  <span className="w-5 h-5 rounded-full bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 text-[10px] grid place-items-center shrink-0 mt-0.5">
                    {i + 1}
                  </span>
                  {w}
                </li>
              ))}
            </ol>
          </Card>
        )}

        {res && res.status !== "APPROVED" && (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <p className="text-xs text-rose-200/90">{res.penalties}</p>
          </div>
        )}
      </div>
    </div>
  );
}

function Select({ label, value, onChange, options }: { label: string; value: string; onChange: (v: string) => void; options: string[] }) {
  return (
    <div>
      <label className="text-xs text-slate-400 mb-1 block">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-cyan-500/50 outline-none"
      >
        {options.map((o) => (
          <option key={o}>{o}</option>
        ))}
      </select>
    </div>
  );
}

// ============ DRONE SELECT ============

function DroneSelect() {
  const [budget, setBudget] = useState(15);
  const [sector, setSector] = useState("Agriculture");
  const [minFT, setMinFT] = useState(20);
  const [minPayload, setMinPayload] = useState(2);
  const [drones, setDrones] = useState<DroneModel[]>([]);

  useEffect(() => {
    let c = false;
    api
      .recommend({ budget_lakhs: budget, sector, min_flight_time: minFT, min_payload: minPayload })
      .then((r) => !c && setDrones(r));
    return () => {
      c = true;
    };
  }, [budget, sector, minFT, minPayload]);

  return (
    <div className="space-y-4">
      <Card className="p-5 grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Slider label="Budget" value={budget} onChange={setBudget} min={3} max={50} step={0.5} unit="Lakhs ₹" />
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Sector</label>
          <select
            value={sector}
            onChange={(e) => setSector(e.target.value)}
            className="w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100"
          >
            <option>Any</option>
            <option>Agriculture</option>
            <option>Survey</option>
            <option>Defense</option>
            <option>Logistics</option>
          </select>
        </div>
        <Slider label="Min Flight Time" value={minFT} onChange={setMinFT} min={10} max={90} step={5} unit="min" />
        <Slider label="Min Payload" value={minPayload} onChange={setMinPayload} min={0} max={10} step={0.5} unit="kg" />
      </Card>

      {drones.length === 0 ? (
        <Card className="p-10 text-center text-sm text-slate-500">
          No matching Indian drones. Try adjusting the budget or payload sliders.
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
          {drones.map((d, i) => (
            <motion.div key={d.model_name} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
              <Card className="p-5 h-full flex flex-col">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <div className="text-xs text-slate-500">{d.manufacturer}</div>
                    <div className="text-lg font-semibold text-slate-100 truncate">{d.model_name}</div>
                  </div>
                  <div className="shrink-0 inline-flex items-center gap-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 px-2 py-0.5">
                    <Award className="w-3 h-3 text-emerald-300" />
                    <span className="text-[10px] font-semibold text-emerald-300">{d.match_score}% match</span>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 my-4">
                  <MiniStat label="Price" value={`₹${d.price_lakhs}L`} />
                  <MiniStat label="Flight" value={`${d.flight_time}m`} />
                  <MiniStat label="Payload" value={`${d.payload}kg`} />
                </div>
                <div className="space-y-1.5 text-xs flex-1">
                  {d.pros.map((p) => (
                    <div key={p} className="flex items-start gap-1.5 text-emerald-300/90">
                      <CheckCircle2 className="w-3 h-3 mt-0.5 shrink-0" /> {p}
                    </div>
                  ))}
                  {d.cons.map((p) => (
                    <div key={p} className="flex items-start gap-1.5 text-rose-300/80">
                      <XCircle className="w-3 h-3 mt-0.5 shrink-0" /> {p}
                    </div>
                  ))}
                </div>
                <div className="mt-4 text-[10px] uppercase tracking-wider text-cyan-400">{d.sector}</div>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-950/60 border border-slate-800 p-2 text-center">
      <div className="text-[9px] uppercase text-slate-500">{label}</div>
      <div className="text-sm font-semibold text-slate-100">{value}</div>
    </div>
  );
}
