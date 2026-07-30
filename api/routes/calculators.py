from typing import List
from fastapi import APIRouter
from api.models.schemas import (
    FlightTimeRequest, FlightTimeResponse,
    RoiRequest, RoiResponse,
    ComplianceRequest, ComplianceResponse,
    RecommendRequest, DroneModel,
)
from api.services.mcp_service import (
    calculate_flight_time,
    calculate_roi,
    check_compliance,
    recommend_drones,
)

router = APIRouter(tags=["MCP Calculators"])

@router.post("/calculate/flight-time", response_model=FlightTimeResponse)
@router.post("/api/calculate/flight-time", response_model=FlightTimeResponse)
def flight_time_endpoint(req: FlightTimeRequest):
    return calculate_flight_time(req)

@router.post("/calculate/roi", response_model=RoiResponse)
@router.post("/api/calculate/roi", response_model=RoiResponse)
def roi_endpoint(req: RoiRequest):
    return calculate_roi(req)

@router.post("/check/compliance", response_model=ComplianceResponse)
@router.post("/api/check/compliance", response_model=ComplianceResponse)
def compliance_endpoint(req: ComplianceRequest):
    return check_compliance(req)

@router.post("/recommend/drone", response_model=List[DroneModel])
@router.post("/api/recommend/drone", response_model=List[DroneModel])
def recommend_endpoint(req: RecommendRequest):
    return recommend_drones(req)
