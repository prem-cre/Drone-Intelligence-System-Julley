import math
import random
from typing import List, Dict, Any
from api.models.schemas import (
    FlightTimeRequest, FlightTimeResponse, PowerCurvePoint,
    RoiRequest, RoiResponse, YearProjection,
    ComplianceRequest, ComplianceResponse,
    RecommendRequest, DroneModel,
)

# ──────────────────────────────────────────────────────────
# Static drone catalogue (mirrors the frontend DRONES array)
# ──────────────────────────────────────────────────────────
DRONES: List[Dict[str, Any]] = [
    {
        "model_name": "Agribot MX",
        "manufacturer": "IoTechWorld Avigation",
        "price_lakhs": 7.5,
        "flight_time": 22,
        "payload": 10,
        "sector": "Agriculture",
        "pros": ["DGCA Type-Certified", "10L tank", "Namo Drone Didi eligible"],
        "cons": ["Heavy transport", "Requires RPC pilot"],
    },
    {
        "model_name": "AG365",
        "manufacturer": "Marut Drones",
        "price_lakhs": 9.2,
        "flight_time": 25,
        "payload": 10,
        "sector": "Agriculture",
        "pros": ["Made in India", "Precision spraying", "Subsidy eligible"],
        "cons": ["Premium pricing"],
    },
    {
        "model_name": "NETRA v4",
        "manufacturer": "ideaForge",
        "price_lakhs": 45,
        "flight_time": 90,
        "payload": 1.5,
        "sector": "Defense",
        "pros": ["VTOL", "Long endurance", "Battle-tested"],
        "cons": ["Restricted to defense/enterprise"],
    },
    {
        "model_name": "A410",
        "manufacturer": "Asteria Aerospace",
        "price_lakhs": 12,
        "flight_time": 40,
        "payload": 2,
        "sector": "Survey",
        "pros": ["High-res mapping", "SVAMITVA ready"],
        "cons": ["Not for spraying"],
    },
    {
        "model_name": "Kisan Drone 2.0",
        "manufacturer": "Garuda Aerospace",
        "price_lakhs": 6.8,
        "flight_time": 20,
        "payload": 10,
        "sector": "Agriculture",
        "pros": ["Affordable", "PLI beneficiary", "Rural service network"],
        "cons": ["Shorter flight time"],
    },
    {
        "model_name": "Defender VTOL",
        "manufacturer": "Throttle Aerospace",
        "price_lakhs": 28,
        "flight_time": 75,
        "payload": 3,
        "sector": "Logistics",
        "pros": ["VTOL cargo", "BVLOS capable"],
        "cons": ["Regulatory heavy"],
    },
    {
        "model_name": "Trinity F90+",
        "manufacturer": "Quidich (India Ops)",
        "price_lakhs": 18,
        "flight_time": 60,
        "payload": 1,
        "sector": "Survey",
        "pros": ["Fixed-wing efficiency"],
        "cons": ["Runway launch needs space"],
    },
]


def calculate_flight_time(req: FlightTimeRequest) -> FlightTimeResponse:
    base_time = (req.battery_mah / 1000) * 3.2
    payload_factor = 1 - (req.payload / 15) * 0.35
    wind_factor = 1 - (req.wind / 40) * 0.2
    temp_factor = 0.9 if (req.temperature > 35 or req.temperature < 5) else 1.0
    flight = max(3.0, base_time * payload_factor * wind_factor * temp_factor)
    range_km = flight * 0.28

    curve = []
    for idx in range(12):
        curve.append(PowerCurvePoint(
            minute=round((flight / 11) * idx),
            power=max(0, round(100 - (idx / 11) * 80 - random.random() * 4)),
        ))

    advice = (
        "Heavy payload — maintain 25% battery reserve for safe RTH."
        if req.payload > 8
        else "Nominal conditions. Standard 20% reserve advised per DGCA safety guidelines."
    )

    return FlightTimeResponse(
        flight_time_mins=round(flight, 1),
        max_range_km=round(range_km, 1),
        battery_consumed_pct=82,
        advice=advice,
        power_curve=curve,
    )


def calculate_roi(req: RoiRequest) -> RoiResponse:
    revenue = req.fee_per_acre * req.monthly_acres
    net_profit = revenue - req.monthly_opex
    effective_investment = req.investment * (1 - req.subsidy_pct / 100)
    payback = math.ceil(effective_investment / net_profit) if net_profit > 0 else 999
    roi_3yr = (
        round(((net_profit * 36 - effective_investment) / effective_investment) * 100)
        if net_profit > 0 else 0
    )

    projection = []
    for y in range(1, 4):
        projection.append(YearProjection(
            year=f"Year {y}",
            revenue=revenue * 12 * y,
            profit=net_profit * 12 * y - (effective_investment if y == 1 else 0),
        ))

    return RoiResponse(
        monthly_revenue=round(revenue),
        net_monthly_profit=round(net_profit),
        payback_months=payback,
        roi_3yr_pct=roi_3yr,
        projection=projection,
    )


def check_compliance(req: ComplianceRequest) -> ComplianceResponse:
    status = "APPROVED"
    permits: List[str] = []
    penalties = "No penalties expected under Drone Rules 2021."

    if req.zone == "Red":
        status = "PROHIBITED"
        penalties = "Flying in Red Zone attracts fines up to ₹1,00,000 + drone seizure under Rule 24, Drone Rules 2021."
    elif req.zone == "Yellow":
        status = "RESTRICTED"
        permits.append("ATC Clearance via DigitalSky")
        permits.append("Prior flight plan filing (24h notice)")
        penalties = "Unauthorized Yellow Zone flight: ₹25,000 – ₹50,000 penalty."

    if req.altitude > 400:
        if status == "APPROVED":
            status = "RESTRICTED"
        permits.append("Altitude Exemption from DGCA")

    if req.weight_category in ("Small", "Medium", "Large") and not req.rpc:
        status = "RESTRICTED"
        permits.append("Remote Pilot Certificate (RPC) from approved RPTO")

    if req.weight_category != "Nano":
        permits.append("UIN Registration on DigitalSky")
        permits.append("NPNT-Compliant Drone Hardware")

    workflow = [
        "Register drone on DigitalSky Platform",
        "Obtain UIN (Unique Identification Number)",
        "Complete Remote Pilot Certification (if applicable)",
        "File flight plan & obtain airspace clearance",
        "Ensure NPNT firmware compliance",
        "Conduct pre-flight safety check",
    ]

    return ComplianceResponse(
        status=status,
        zone=f"{req.zone} Zone",
        permits=list(set(permits)),
        penalties=penalties,
        workflow=workflow,
    )


def recommend_drones(req: RecommendRequest) -> List[DroneModel]:
    results = []
    for d in DRONES:
        if d["price_lakhs"] > req.budget_lakhs:
            continue
        if req.sector != "Any" and d["sector"] != req.sector:
            continue
        if d["flight_time"] < req.min_flight_time:
            continue
        if d["payload"] < req.min_payload:
            continue

        score = min(
            99,
            round(
                70
                + (req.budget_lakhs - d["price_lakhs"]) * 2
                + (d["flight_time"] - req.min_flight_time) * 0.4
                + (d["payload"] - req.min_payload) * 0.6
            ),
        )
        results.append(DroneModel(
            model_name=d["model_name"],
            manufacturer=d["manufacturer"],
            price_lakhs=d["price_lakhs"],
            flight_time=d["flight_time"],
            payload=d["payload"],
            sector=d["sector"],
            match_score=score,
            pros=d["pros"],
            cons=d["cons"],
        ))

    results.sort(key=lambda x: x.match_score, reverse=True)
    return results
