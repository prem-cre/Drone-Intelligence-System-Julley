from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# ── Chat ──
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class Citation(BaseModel):
    title: str
    source: str
    score: float
    snippet: str

class ToolCall(BaseModel):
    tool_name: str
    input: Dict[str, Any]
    output: Dict[str, Any]

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    tool_calls: List[ToolCall]

class ChatMessageItem(BaseModel):
    id: str
    role: str
    content: str
    response: Optional[ChatResponse] = None
    timestamp: Optional[str] = None

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageItem]

class DocumentUploadRequest(BaseModel):
    file_name: str
    content: str



# ── Flight Time ──
class FlightTimeRequest(BaseModel):
    battery_mah: float
    empty_weight: float
    payload: float
    wind: float
    temperature: float

class PowerCurvePoint(BaseModel):
    minute: int
    power: int

class FlightTimeResponse(BaseModel):
    flight_time_mins: float
    max_range_km: float
    battery_consumed_pct: float
    advice: str
    power_curve: List[PowerCurvePoint]

# ── ROI ──
class RoiRequest(BaseModel):
    sector: str
    investment: float
    monthly_opex: float
    fee_per_acre: float
    monthly_acres: float
    subsidy_pct: float

class YearProjection(BaseModel):
    year: str
    profit: float
    revenue: float

class RoiResponse(BaseModel):
    monthly_revenue: float
    net_monthly_profit: float
    payback_months: float
    roi_3yr_pct: float
    projection: List[YearProjection]

# ── Compliance ──
class ComplianceRequest(BaseModel):
    weight_category: str
    purpose: str
    zone: str  # "Green" | "Yellow" | "Red"
    altitude: float
    rpc: bool

class ComplianceResponse(BaseModel):
    status: str  # "APPROVED" | "RESTRICTED" | "PROHIBITED"
    zone: str
    permits: List[str]
    penalties: str
    workflow: List[str]

# ── Drone Recommendation ──
class RecommendRequest(BaseModel):
    budget_lakhs: float
    sector: str
    min_flight_time: float
    min_payload: float

class DroneModel(BaseModel):
    model_name: str
    manufacturer: str
    price_lakhs: float
    flight_time: float
    payload: float
    sector: str
    match_score: float
    pros: List[str]
    cons: List[str]
