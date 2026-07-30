// Frontend mock API service with a toggle for a real backend.
// Set USE_MOCK_API=false to use `http://localhost:8000`.

export const USE_MOCK_API = false;
const API_BASE = "http://localhost:8000";

const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));

export interface Citation {
  title: string;
  source: string;
  score: number;
  snippet: string;
}
export interface ToolCall {
  tool_name: string;
  input: Record<string, unknown>;
  output: Record<string, unknown>;
}
export interface ChatResponse {
  answer: string;
  citations: Citation[];
  tool_calls: ToolCall[];
}

export interface FlightTimeInput {
  battery_mah: number;
  empty_weight: number;
  payload: number;
  wind: number;
  temperature: number;
}
export interface FlightTimeResponse {
  flight_time_mins: number;
  max_range_km: number;
  battery_consumed_pct: number;
  advice: string;
  power_curve: { minute: number; power: number }[];
}

export interface RoiInput {
  sector: string;
  investment: number;
  monthly_opex: number;
  fee_per_acre: number;
  monthly_acres: number;
  subsidy_pct: number;
}
export interface RoiResponse {
  monthly_revenue: number;
  net_monthly_profit: number;
  payback_months: number;
  roi_3yr_pct: number;
  projection: { year: string; profit: number; revenue: number }[];
}

export interface ComplianceInput {
  weight_category: string;
  purpose: string;
  zone: "Green" | "Yellow" | "Red";
  altitude: number;
  rpc: boolean;
}
export interface ComplianceResponse {
  status: "APPROVED" | "RESTRICTED" | "PROHIBITED";
  zone: string;
  permits: string[];
  penalties: string;
  workflow: string[];
}

export interface DroneModel {
  model_name: string;
  manufacturer: string;
  price_lakhs: number;
  flight_time: number;
  payload: number;
  sector: string;
  match_score: number;
  pros: string[];
  cons: string[];
}
export interface RecommendInput {
  budget_lakhs: number;
  sector: string;
  min_flight_time: number;
  min_payload: number;
}

// ---------- Static domain data ----------

const DRONES: Omit<DroneModel, "match_score">[] = [
  {
    model_name: "Agribot MX",
    manufacturer: "IoTechWorld Avigation",
    price_lakhs: 7.5,
    flight_time: 22,
    payload: 10,
    sector: "Agriculture",
    pros: ["DGCA Type-Certified", "10L tank", "Namo Drone Didi eligible"],
    cons: ["Heavy transport", "Requires RPC pilot"],
  },
  {
    model_name: "AG365",
    manufacturer: "Marut Drones",
    price_lakhs: 9.2,
    flight_time: 25,
    payload: 10,
    sector: "Agriculture",
    pros: ["Made in India", "Precision spraying", "Subsidy eligible"],
    cons: ["Premium pricing"],
  },
  {
    model_name: "NETRA v4",
    manufacturer: "ideaForge",
    price_lakhs: 45,
    flight_time: 90,
    payload: 1.5,
    sector: "Defense",
    pros: ["VTOL", "Long endurance", "Battle-tested"],
    cons: ["Restricted to defense/enterprise"],
  },
  {
    model_name: "A410",
    manufacturer: "Asteria Aerospace",
    price_lakhs: 12,
    flight_time: 40,
    payload: 2,
    sector: "Survey",
    pros: ["High-res mapping", "SVAMITVA ready"],
    cons: ["Not for spraying"],
  },
  {
    model_name: "Kisan Drone 2.0",
    manufacturer: "Garuda Aerospace",
    price_lakhs: 6.8,
    flight_time: 20,
    payload: 10,
    sector: "Agriculture",
    pros: ["Affordable", "PLI beneficiary", "Rural service network"],
    cons: ["Shorter flight time"],
  },
  {
    model_name: "Defender VTOL",
    manufacturer: "Throttle Aerospace",
    price_lakhs: 28,
    flight_time: 75,
    payload: 3,
    sector: "Logistics",
    pros: ["VTOL cargo", "BVLOS capable"],
    cons: ["Regulatory heavy"],
  },
  {
    model_name: "Trinity F90+",
    manufacturer: "Quidich (India Ops)",
    price_lakhs: 18,
    flight_time: 60,
    payload: 1,
    sector: "Survey",
    pros: ["Fixed-wing efficiency"],
    cons: ["Runway launch needs space"],
  },
];

// ---------- Mock implementations ----------

async function mockChat(message: string): Promise<ChatResponse> {
  await wait(650);
  const lower = message.toLowerCase();

  if (lower.includes("flight time") || lower.includes("battery")) {
    const ft = await mockFlightTime({
      battery_mah: 10000,
      empty_weight: 3,
      payload: 2,
      wind: 10,
      temperature: 28,
    });
    return {
      answer: `### Flight Time Estimate\n\nFor a **10,000 mAh** battery with a **2 kg payload** in typical Indian conditions, I've run the MCP Flight Time tool.\n\n- **Estimated flight time:** ${ft.flight_time_mins} minutes\n- **Max operational range:** ${ft.max_range_km} km\n- **Battery drawdown:** ${ft.battery_consumed_pct}%\n\n> ${ft.advice}`,
      citations: [
        {
          title: "DGCA Drone Battery Safety Advisory",
          source: "dgca_battery_safety.md",
          score: 0.92,
          snippet: "Operators must maintain a 20% reserve battery capacity for safe RTH...",
        },
      ],
      tool_calls: [
        {
          tool_name: "flight_time_calculator",
          input: { battery_mah: 10000, payload: 2 },
          output: ft as unknown as Record<string, unknown>,
        },
      ],
    };
  }

  if (lower.includes("roi") || lower.includes("acre") || lower.includes("profit")) {
    const roi = await mockRoi({
      sector: "Agriculture",
      investment: 750000,
      monthly_opex: 25000,
      fee_per_acre: 400,
      monthly_acres: 500,
      subsidy_pct: 50,
    });
    return {
      answer: `### ROI Analysis — 500-acre Agricultural Spraying (Telangana)\n\nAssuming ₹400/acre and 50% Namo Drone Didi subsidy:\n\n- **Monthly Revenue:** ₹${roi.monthly_revenue.toLocaleString("en-IN")}\n- **Net Monthly Profit:** ₹${roi.net_monthly_profit.toLocaleString("en-IN")}\n- **Payback Period:** ${roi.payback_months} months\n- **3-Year ROI:** ${roi.roi_3yr_pct}%\n\nSubsidy dramatically shortens payback for SHGs under the **Namo Drone Didi** scheme.`,
      citations: [
        {
          title: "Namo Drone Didi Scheme Guidelines",
          source: "namo_drone_didi_2024.pdf",
          score: 0.89,
          snippet: "50–80% subsidy on drone kits for women-led SHGs across India...",
        },
      ],
      tool_calls: [
        {
          tool_name: "roi_calculator",
          input: { sector: "Agriculture", monthly_acres: 500 },
          output: roi as unknown as Record<string, unknown>,
        },
      ],
    };
  }

  if (lower.includes("dgca") || lower.includes("rule") || lower.includes("zone")) {
    return {
      answer: `### DGCA Drone Rules 2021 — Micro Drones in Green Zones\n\n**Micro drones** (250 g – 2 kg) flying in a **Green Zone** below **400 ft AGL** do **not require prior permission**, but you must comply with:\n\n1. **UIN** (Unique Identification Number) registration on DigitalSky\n2. **Remote Pilot Certificate** if operated commercially\n3. **NPNT** compliance (No Permission, No Take-off) on capable drones\n4. Maintain **VLOS** (Visual Line of Sight)\n5. No flying over crowds or near airports (5 km buffer)\n\nHobbyists flying nano drones (<250 g) are exempt from most requirements.`,
      citations: [
        {
          title: "Drone Rules 2021 — Ministry of Civil Aviation",
          source: "dgca_regulations_handbook.md",
          score: 0.96,
          snippet: "Micro category unmanned aircraft may be operated in green zones up to 60m/200ft without prior permission subject to NPNT...",
        },
        {
          title: "DigitalSky Airspace Map Guide",
          source: "digitalsky_airspace.md",
          score: 0.84,
          snippet: "Green zones are unrestricted airspace up to 400 feet AGL for micro and nano drones...",
        },
      ],
      tool_calls: [],
    };
  }

  if (lower.includes("recommend") || lower.includes("under")) {
    const rec = await mockRecommend({
      budget_lakhs: 8,
      sector: "Agriculture",
      min_flight_time: 15,
      min_payload: 8,
    });
    return {
      answer: `### Recommended Agricultural Spraying Drones under ₹8 Lakhs\n\nI matched **${rec.length} DGCA-certified Indian drones** meeting your criteria. Top pick: **${rec[0]?.model_name}** by ${rec[0]?.manufacturer} — eligible under the Namo Drone Didi subsidy scheme.`,
      citations: [
        {
          title: "PLI Scheme for Drones — DPIIT",
          source: "pli_drone_manufacturers.md",
          score: 0.87,
          snippet: "IoTechWorld, Garuda and Marut are Production-Linked Incentive beneficiaries...",
        },
      ],
      tool_calls: [
        {
          tool_name: "drone_recommender",
          input: { budget_lakhs: 8, sector: "Agriculture" },
          output: { count: rec.length } as Record<string, unknown>,
        },
      ],
    };
  }

  return {
    answer: `### Drone Intelligence Search Results for: "${message}"\n\nBased on India's drone ecosystem knowledge base:\n\n- **Precision Agriculture & Crop Spraying**: Precision agriculture using drones (IoTechWorld Agribot, Marut AG30, Garuda Kisan Drone) is active across **cotton, paddy, sugarcane, and chilli belts in Telangana, Andhra Pradesh, Punjab, and Maharashtra**.\n- **DGCA Regulations**: Operations follow the **Drone Rules 2021** (amended 2023). Green zones up to 400 ft AGL require no prior permission for registered UIN drones.\n- **Government Subsidies**: Under the **Namo Drone Didi** scheme, women Self-Help Groups (SHGs) receive an 80% capital subsidy (up to ₹8 Lakhs).\n\n---\n**📄 Source Documents:**\n- 📄 **Agricultural Drone Spraying & Economics** (\`agricultural_drone_case_study.md\`)\n- 📄 **DGCA Airspace Guidelines** (\`dgca_regulations_handbook.md\`)`,
    citations: [
      {
        title: "Agricultural Drone Spraying Case Study",
        source: "agricultural_drone_case_study.md",
        score: 0.94,
        snippet: "Precision agriculture powered by agricultural drones is transforming Indian farming across cotton, paddy, sugarcane, and chilli belts in Telangana, Andhra Pradesh, Punjab, and Maharashtra...",
      },
    ],
    tool_calls: [],
  };
}

async function mockFlightTime(i: FlightTimeInput): Promise<FlightTimeResponse> {
  await wait(400);
  const baseTime = (i.battery_mah / 1000) * 3.2;
  const payloadFactor = 1 - (i.payload / 15) * 0.35;
  const windFactor = 1 - (i.wind / 40) * 0.2;
  const tempFactor = i.temperature > 35 || i.temperature < 5 ? 0.9 : 1;
  const flight = Math.max(3, baseTime * payloadFactor * windFactor * tempFactor);
  const range = flight * 0.28;
  const curve = Array.from({ length: 12 }).map((_, idx) => ({
    minute: Math.round((flight / 11) * idx),
    power: Math.round(100 - (idx / 11) * 80 - Math.random() * 4),
  }));
  return {
    flight_time_mins: +flight.toFixed(1),
    max_range_km: +range.toFixed(1),
    battery_consumed_pct: 82,
    advice:
      i.payload > 8
        ? "Heavy payload — maintain 25% battery reserve for safe RTH."
        : "Nominal conditions. Standard 20% reserve advised per DGCA safety guidelines.",
    power_curve: curve,
  };
}

async function mockRoi(i: RoiInput): Promise<RoiResponse> {
  await wait(400);
  const revenue = i.fee_per_acre * i.monthly_acres;
  const netProfit = revenue - i.monthly_opex;
  const effectiveInvestment = i.investment * (1 - i.subsidy_pct / 100);
  const payback = netProfit > 0 ? Math.ceil(effectiveInvestment / netProfit) : 999;
  const roi3yr = netProfit > 0 ? Math.round(((netProfit * 36 - effectiveInvestment) / effectiveInvestment) * 100) : 0;
  const projection = [1, 2, 3].map((y) => ({
    year: `Year ${y}`,
    revenue: revenue * 12 * y,
    profit: netProfit * 12 * y - (y === 1 ? effectiveInvestment : 0),
  }));
  return {
    monthly_revenue: Math.round(revenue),
    net_monthly_profit: Math.round(netProfit),
    payback_months: payback,
    roi_3yr_pct: roi3yr,
    projection,
  };
}

async function mockCompliance(i: ComplianceInput): Promise<ComplianceResponse> {
  await wait(350);
  let status: ComplianceResponse["status"] = "APPROVED";
  const permits: string[] = [];
  let penalties = "No penalties expected under Drone Rules 2021.";

  if (i.zone === "Red") {
    status = "PROHIBITED";
    penalties = "Flying in Red Zone attracts fines up to ₹1,00,000 + drone seizure under Rule 24, Drone Rules 2021.";
  } else if (i.zone === "Yellow") {
    status = "RESTRICTED";
    permits.push("ATC Clearance via DigitalSky");
    permits.push("Prior flight plan filing (24h notice)");
    penalties = "Unauthorized Yellow Zone flight: ₹25,000 – ₹50,000 penalty.";
  }

  if (i.altitude > 400) {
    status = status === "APPROVED" ? "RESTRICTED" : status;
    permits.push("Altitude Exemption from DGCA");
  }
  if (["Small", "Medium", "Large"].includes(i.weight_category) && !i.rpc) {
    status = "RESTRICTED";
    permits.push("Remote Pilot Certificate (RPC) from approved RPTO");
  }
  if (i.weight_category !== "Nano") {
    permits.push("UIN Registration on DigitalSky");
    permits.push("NPNT-Compliant Drone Hardware");
  }

  return {
    status,
    zone: `${i.zone} Zone`,
    permits: Array.from(new Set(permits)),
    penalties,
    workflow: [
      "Register drone on DigitalSky Platform",
      "Obtain UIN (Unique Identification Number)",
      "Complete Remote Pilot Certification (if applicable)",
      "File flight plan & obtain airspace clearance",
      "Ensure NPNT firmware compliance",
      "Conduct pre-flight safety check",
    ],
  };
}

async function mockRecommend(i: RecommendInput): Promise<DroneModel[]> {
  await wait(350);
  return DRONES.filter(
    (d) =>
      d.price_lakhs <= i.budget_lakhs &&
      (i.sector === "Any" || d.sector === i.sector) &&
      d.flight_time >= i.min_flight_time &&
      d.payload >= i.min_payload,
  )
    .map((d) => ({
      ...d,
      match_score: Math.min(
        99,
        Math.round(
          70 +
            (i.budget_lakhs - d.price_lakhs) * 2 +
            (d.flight_time - i.min_flight_time) * 0.4 +
            (d.payload - i.min_payload) * 0.6,
        ),
      ),
    }))
    .sort((a, b) => b.match_score - a.match_score);
}

// ---------- Public API surface ----------

async function post<T>(path: string, body: unknown, mock: () => Promise<T>): Promise<T> {
  if (USE_MOCK_API) return mock();
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
    return (await res.json()) as T;
  } catch (err) {
    console.warn(`[API ${path}] Network request failed, using instant local calculator fallback:`, err);
    return mock();
  }
}

export const api = {
  chat: (message: string) => post("/api/chat", { message }, () => mockChat(message)),
  flightTime: (i: FlightTimeInput) => post("/api/calculate/flight-time", i, () => mockFlightTime(i)),
  roi: (i: RoiInput) => post("/api/calculate/roi", i, () => mockRoi(i)),
  compliance: (i: ComplianceInput) => post("/api/check/compliance", i, () => mockCompliance(i)),
  recommend: (i: RecommendInput) => post("/api/recommend/drone", i, () => mockRecommend(i)),
};

export { DRONES };
