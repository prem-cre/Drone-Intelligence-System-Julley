import os
import sys

# Ensure project root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.chat import router as chat_router
from api.routes.upload import router as upload_router
from api.routes.calculators import router as calculators_router
from api.routes.analytics import router as analytics_router

app = FastAPI(
    title="Drone Intelligence System API",
    description="FastAPI backend for India's Drone Intelligence System — RAG + MCP Tools",
    version="1.0.0",
)

# CORS middleware for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register modular routes
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(calculators_router)
app.include_router(analytics_router)

@app.get("/")
def root():
    return {"status": "operational", "service": "Drone Intelligence System API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}
