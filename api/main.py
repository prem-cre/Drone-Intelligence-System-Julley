import os
import sys

# Ensure project root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.models.schemas import (
    ChatRequest, ChatResponse,
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
from api.services.rag_service import handle_chat

app = FastAPI(
    title="Drone Intelligence System API",
    description="FastAPI backend for India's Drone Intelligence System — RAG + MCP Tools",
    version="1.0.0",
)

# ── CORS ── Allow the React frontend (Vite dev server on 5173/3000/8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────
# Health check
# ──────────────────────────────────────
@app.get("/")
def root():
    return {"status": "operational", "service": "Drone Intelligence System API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


from api.models.schemas import (
    ChatRequest, ChatResponse, ChatHistoryResponse, ChatMessageItem,
    FlightTimeRequest, FlightTimeResponse,
    RoiRequest, RoiResponse,
    ComplianceRequest, ComplianceResponse,
    RecommendRequest, DroneModel,
)
from api.services.history_service import get_chat_history, clear_chat_history


# ──────────────────────────────────────
# POST /api/chat  —  RAG + MCP hybrid with persistent history
# ──────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        session_id = req.session_id or "default"
        result = handle_chat(req.message, session_id=session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/history/{session_id}", response_model=ChatHistoryResponse)
def api_get_chat_history(session_id: str):
    history = get_chat_history(session_id)
    items = [ChatMessageItem(**h) for h in history]
    return ChatHistoryResponse(session_id=session_id, messages=items)


@app.delete("/api/chat/history/{session_id}")
def api_clear_chat_history(session_id: str):
    clear_chat_history(session_id)
    return {"status": "success", "message": f"Cleared history for session '{session_id}'"}



# ──────────────────────────────────────
# POST /api/calculate/flight-time
# ──────────────────────────────────────
@app.post("/api/calculate/flight-time", response_model=FlightTimeResponse)
def api_flight_time(req: FlightTimeRequest):
    return calculate_flight_time(req)


# ──────────────────────────────────────
# POST /api/calculate/roi
# ──────────────────────────────────────
@app.post("/api/calculate/roi", response_model=RoiResponse)
def api_roi(req: RoiRequest):
    return calculate_roi(req)


# ──────────────────────────────────────
# POST /api/check/compliance
# ──────────────────────────────────────
@app.post("/api/check/compliance", response_model=ComplianceResponse)
def api_compliance(req: ComplianceRequest):
    return check_compliance(req)


# ──────────────────────────────────────
# POST /api/recommend/drone
# ──────────────────────────────────────
@app.post("/api/recommend/drone", response_model=List[DroneModel])
def api_recommend(req: RecommendRequest):
    return recommend_drones(req)
