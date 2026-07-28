# 🇮🇳 Drone Intelligence System for India

An end-to-end production AI/ML application engineered for **Julley's AI Internship Project (Round 1)**.

The system serves as India's comprehensive drone knowledge hub, featuring a **Multi-Query RAG Pipeline** with persistent **ChromaDB**, **Model Context Protocol (MCP) Calculation Server**, **FastAPI Backend**, and interactive **React Dashboard**.

---

## 🏛 System Architecture

```
                          User Interface (React + Tailwind CSS Dashboard)
                                               │
                                               ▼
                                 FastAPI Backend (/api/routes)
                                               │
                 ┌─────────────────────────────┼─────────────────────────────┐
                 │                             │                             │
                 ▼                             ▼                             ▼
       RAG System Pipeline              MCP Tool Server              Analytics & Logging
  (Embeddings + ChromaDB + LLM)   (Flight, ROI, Compliance, Rec)    (Query stats, latency)
                 │                             │
                 ▼                             ▼
   Indian Drone Knowledge Base           Domain Calculators
 (DGCA Rules, Specs, Startups)        & Regulatory Logic Engine
```

---

## 🌟 Key Features

### 1. Advanced RAG Pipeline (`/rag`)
- **Semantic Section Chunker**: Header-aware (`#`, `##`, `###`) recursive splitting.
- **Persistent ChromaDB Store**: Stores vector representations using Open-Source SentenceTransformers (`all-MiniLM-L6-v2` / `BAAI/bge-small-en-v1.5`).
- **Multi-Query Expansion**: Generates 3-4 query variations to maximize vector search recall.
- **Hybrid RRF + BM25 Reranker**: Reciprocal Rank Fusion re-ranking combining semantic vector distance + term frequency match.
- **Gemini LLM Integration**: Synthesizes responses using Google Gemini API with explicit source citations.

### 2. MCP Server & Tool Suite (`/mcp_server`)
- `flight_time_calculator`: Calculates duration, range, battery consumption curve.
- `roi_calculator`: Financial ROI timeline, payback period in months, 3-year projection.
- `compliance_checker`: Evaluates DGCA Drone Rules 2021 across Green/Yellow/Red zones.
- `drone_recommender`: Ranks Indian drone models (ideaForge, Marut, Garuda, IoTechWorld) matching budget & specs.

### 3. FastAPI REST Backend (`/api`)
- `POST /api/chat`
- `POST /api/calculate/flight-time`
- `POST /api/calculate/roi`
- `POST /api/check/compliance`
- `POST /api/recommend/drone`
- `GET /health`

### 4. Interactive React Dashboard (`/frontend`)
- React 19 + TypeScript (`.tsx`) + Tailwind CSS + Lucide Icons + Recharts.
- Dark theme with glassmorphic cards, tool cards, citations drawer, and session export.

---

## 📁 Repository Structure

```
drone-intelligence-system/
├── data/
│   ├── raw/           # DGCA handbook, drone specs, use cases, ecosystem
│   ├── processed/     # Chunked JSON vector documents & ChromaDB
│   └── synthetic/     # Flight telemetry, farm ROI simulations, logistics
├── rag/               # Chunker, Embeddings, ChromaDB, MultiQuery, Reranker, Generator, Pipeline
├── mcp_server/        # MCP server & calculation tools
│   └── tools/
├── api/               # FastAPI entry point, routes, schemas, services
│   ├── routes/
│   ├── models/
│   └── services/
├── frontend/          # React + Vite + Tailwind CSS dashboard
│   ├── public/
│   └── src/
├── tests/             # Pytest test suite (14 passing tests)
├── scripts/           # Data generation, preprocessing, seeding scripts
├── docs/              # Architecture diagram, API docs, user guide
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Install & Seed Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate synthetic data & seed ChromaDB vector store
python scripts/generate_synthetic_data.py
python scripts/preprocess_data.py
python scripts/seed_vector_db.py

# Start FastAPI server
python -m uvicorn api.main:app --port 8000 --reload
```

### 2. Install & Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Run Automated Test Suite
```bash
pytest tests/
```

---

## 🐳 Docker Deployment
```bash
docker-compose up --build
```
- Backend API: `http://localhost:8000`
- Frontend Dashboard: `http://localhost:5173`
