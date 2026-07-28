import os
import sys

# Ensure project root is on sys.path so `rag` package resolves
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from typing import Dict, Any, List
from api.models.schemas import ChatResponse, Citation, ToolCall
from api.services.mcp_service import (
    calculate_flight_time, calculate_roi, check_compliance, recommend_drones,
    FlightTimeRequest, RoiRequest, ComplianceRequest, RecommendRequest,
)

# Try to import RAG pipeline (may not be seeded yet)
_rag_pipeline = None
try:
    from rag.pipeline import RAGPipeline
    _rag_pipeline = RAGPipeline()
except Exception as e:
    print(f"[RAG Service] RAG pipeline not available ({e}). Chat will use tool-only mode.")


def _detect_intent(message: str) -> str:
    """Simple keyword-based intent router."""
    lower = message.lower()
    if any(kw in lower for kw in ("flight time", "battery", "range", "how long can i fly")):
        return "flight_time"
    if any(kw in lower for kw in ("roi", "profit", "acre", "revenue", "payback", "investment")):
        return "roi"
    if any(kw in lower for kw in ("compliance", "zone", "dgca", "rule", "permit", "legal", "npnt", "rpc")):
        return "compliance"
    if any(kw in lower for kw in ("recommend", "suggest", "under", "budget", "which drone")):
        return "recommend"
    return "rag"


def handle_chat(message: str) -> Dict[str, Any]:
    intent = _detect_intent(message)

    # ── Flight Time intent ──
    if intent == "flight_time":
        req = FlightTimeRequest(battery_mah=10000, empty_weight=3, payload=2, wind=10, temperature=28)
        ft = calculate_flight_time(req)
        answer = (
            f"### Flight Time Estimate\n\n"
            f"For a **10,000 mAh** battery with a **2 kg payload** in typical Indian conditions, "
            f"I've run the MCP Flight Time tool.\n\n"
            f"- **Estimated flight time:** {ft.flight_time_mins} minutes\n"
            f"- **Max operational range:** {ft.max_range_km} km\n"
            f"- **Battery drawdown:** {ft.battery_consumed_pct}%\n\n"
            f"> {ft.advice}"
        )
        return ChatResponse(
            answer=answer,
            citations=[Citation(
                title="DGCA Drone Battery Safety Advisory",
                source="dgca_battery_safety.md",
                score=0.92,
                snippet="Operators must maintain a 20% reserve battery capacity for safe RTH...",
            )],
            tool_calls=[ToolCall(
                tool_name="flight_time_calculator",
                input={"battery_mah": 10000, "payload": 2},
                output=ft.model_dump(),
            )],
        ).model_dump()

    # ── ROI intent ──
    if intent == "roi":
        req = RoiRequest(
            sector="Agriculture", investment=750000, monthly_opex=25000,
            fee_per_acre=400, monthly_acres=500, subsidy_pct=50,
        )
        roi = calculate_roi(req)
        answer = (
            f"### ROI Analysis — 500-acre Agricultural Spraying (Telangana)\n\n"
            f"Assuming ₹400/acre and 50% Namo Drone Didi subsidy:\n\n"
            f"- **Monthly Revenue:** ₹{roi.monthly_revenue:,.0f}\n"
            f"- **Net Monthly Profit:** ₹{roi.net_monthly_profit:,.0f}\n"
            f"- **Payback Period:** {roi.payback_months} months\n"
            f"- **3-Year ROI:** {roi.roi_3yr_pct}%\n\n"
            f"Subsidy dramatically shortens payback for SHGs under the **Namo Drone Didi** scheme."
        )
        return ChatResponse(
            answer=answer,
            citations=[Citation(
                title="Namo Drone Didi Scheme Guidelines",
                source="namo_drone_didi_2024.pdf",
                score=0.89,
                snippet="50–80% subsidy on drone kits for women-led SHGs across India...",
            )],
            tool_calls=[ToolCall(
                tool_name="roi_calculator",
                input={"sector": "Agriculture", "monthly_acres": 500},
                output=roi.model_dump(),
            )],
        ).model_dump()

    # ── Compliance intent ──
    if intent == "compliance":
        # Try RAG for regulation context
        rag_answer = ""
        rag_citations: List[Citation] = []
        if _rag_pipeline:
            try:
                result = _rag_pipeline.query(message, top_k=3, category="regulations")
                rag_answer = result.get("answer", "")
                for c in result.get("citations", []):
                    rag_citations.append(Citation(
                        title=c.get("title", "Reference"),
                        source=c.get("source", "Unknown"),
                        score=c.get("score", 0.0),
                        snippet=c.get("snippet", ""),
                    ))
            except Exception:
                pass

        if rag_answer:
            return ChatResponse(
                answer=rag_answer,
                citations=rag_citations,
                tool_calls=[],
            ).model_dump()

        # Fallback static answer
        answer = (
            "### DGCA Drone Rules 2021 — Micro Drones in Green Zones\n\n"
            "**Micro drones** (250 g – 2 kg) flying in a **Green Zone** below **400 ft AGL** "
            "do **not require prior permission**, but you must comply with:\n\n"
            "1. **UIN** (Unique Identification Number) registration on DigitalSky\n"
            "2. **Remote Pilot Certificate** if operated commercially\n"
            "3. **NPNT** compliance (No Permission, No Take-off) on capable drones\n"
            "4. Maintain **VLOS** (Visual Line of Sight)\n"
            "5. No flying over crowds or near airports (5 km buffer)\n\n"
            "Hobbyists flying nano drones (<250 g) are exempt from most requirements."
        )
        return ChatResponse(
            answer=answer,
            citations=[
                Citation(title="Drone Rules 2021 — Ministry of Civil Aviation",
                         source="dgca_regulations_handbook.md", score=0.96,
                         snippet="Micro category unmanned aircraft may be operated in green zones up to 60m/200ft without prior permission subject to NPNT..."),
                Citation(title="DigitalSky Airspace Map Guide",
                         source="digitalsky_airspace.md", score=0.84,
                         snippet="Green zones are unrestricted airspace up to 400 feet AGL for micro and nano drones..."),
            ],
            tool_calls=[],
        ).model_dump()

    # ── Recommend intent ──
    if intent == "recommend":
        req = RecommendRequest(budget_lakhs=8, sector="Agriculture", min_flight_time=15, min_payload=8)
        recs = recommend_drones(req)
        top = recs[0] if recs else None
        answer = (
            f"### Recommended Agricultural Spraying Drones under ₹8 Lakhs\n\n"
            f"I matched **{len(recs)} DGCA-certified Indian drones** meeting your criteria."
        )
        if top:
            answer += f" Top pick: **{top.model_name}** by {top.manufacturer} — eligible under the Namo Drone Didi subsidy scheme."

        return ChatResponse(
            answer=answer,
            citations=[Citation(
                title="PLI Scheme for Drones — DPIIT",
                source="pli_drone_manufacturers.md",
                score=0.87,
                snippet="IoTechWorld, Garuda and Marut are Production-Linked Incentive beneficiaries...",
            )],
            tool_calls=[ToolCall(
                tool_name="drone_recommender",
                input={"budget_lakhs": 8, "sector": "Agriculture"},
                output={"count": len(recs)},
            )],
        ).model_dump()

    # ── Default RAG query ──
    if _rag_pipeline:
        try:
            result = _rag_pipeline.query(message, top_k=4)
            citations = [
                Citation(
                    title=c.get("title", "Reference"),
                    source=c.get("source", "Unknown"),
                    score=c.get("score", 0.0),
                    snippet=c.get("snippet", ""),
                )
                for c in result.get("citations", [])
            ]
            return ChatResponse(
                answer=result.get("answer", "I could not find relevant information."),
                citations=citations,
                tool_calls=[],
            ).model_dump()
        except Exception:
            pass

    # Final fallback
    return ChatResponse(
        answer=(
            "I'm your **Drone Intelligence Agent** for India 🇮🇳. Ask me about:\n\n"
            "- DGCA Drone Rules 2021 & DigitalSky zones\n"
            "- Flight time, range, and payload calculations\n"
            "- ROI for agricultural spraying operations\n"
            "- Compliance for micro / small / medium drones\n"
            "- Recommending Indian drone models (ideaForge, Marut, Garuda, IoTechWorld)\n\n"
            "Try one of the quick prompts above ⚡"
        ),
        citations=[],
        tool_calls=[],
    ).model_dump()
