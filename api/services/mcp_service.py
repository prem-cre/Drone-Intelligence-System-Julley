from typing import List
from api.models.schemas import (
    FlightTimeRequest, FlightTimeResponse, PowerCurvePoint,
    RoiRequest, RoiResponse, YearProjection,
    ComplianceRequest, ComplianceResponse,
    RecommendRequest, DroneModel,
)

# Delegate directly to MCP server tools
from mcp_server.tools.flight_calculator import calculate_flight_time as mcp_flight_calc
from mcp_server.tools.roi_calculator import calculate_roi as mcp_roi_calc
from mcp_server.tools.compliance_checker import check_compliance as mcp_compliance_check
from mcp_server.tools.drone_recommender import recommend_drone as mcp_recommend_drone, DRONES_CATALOGUE


def calculate_flight_time(req: FlightTimeRequest) -> FlightTimeResponse:
    res = mcp_flight_calc(
        battery_mah=req.battery_mah,
        empty_weight=req.empty_weight,
        payload=req.payload,
        wind=req.wind,
        temperature=req.temperature,
    )
    curve = [PowerCurvePoint(**pt) for pt in res.get("power_curve", [])]
    return FlightTimeResponse(
        flight_time_mins=res["flight_time_mins"],
        max_range_km=res["max_range_km"],
        battery_consumed_pct=res["battery_consumed_pct"],
        advice=res["advice"],
        power_curve=curve,
    )


def calculate_roi(req: RoiRequest) -> RoiResponse:
    res = mcp_roi_calc(
        sector=req.sector,
        investment=req.investment,
        monthly_opex=req.monthly_opex,
        fee_per_acre=req.fee_per_acre,
        monthly_acres=req.monthly_acres,
        subsidy_pct=req.subsidy_pct,
    )
    projection = [YearProjection(**p) for p in res.get("projection", [])]
    return RoiResponse(
        monthly_revenue=res["monthly_revenue"],
        net_monthly_profit=res["net_monthly_profit"],
        payback_months=res["payback_months"],
        roi_3yr_pct=res["roi_3yr_pct"],
        projection=projection,
    )


def check_compliance(req: ComplianceRequest) -> ComplianceResponse:
    res = mcp_compliance_check(
        weight_category=req.weight_category,
        purpose=req.purpose,
        zone=req.zone,
        altitude=req.altitude,
        rpc=req.rpc,
    )
    return ComplianceResponse(
        status=res["status"],
        zone=res["zone"],
        permits=res["permits"],
        penalties=res["penalties"],
        workflow=res["workflow"],
    )


def recommend_drones(req: RecommendRequest) -> List[DroneModel]:
    recs = mcp_recommend_drone(
        budget_lakhs=req.budget_lakhs,
        sector=req.sector,
        min_flight_time=req.min_flight_time,
        min_payload=req.min_payload,
    )
    return [DroneModel(**r) for r in recs]
