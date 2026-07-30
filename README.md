# 🇮🇳 AI/ML Internship Project: Drone Intelligence System for India

[![CI/CD Pipeline](https://github.com/drone-intelligence/drone-intelligence-system/actions/workflows/ci.yml/badge.svg)](https://github.com/drone-intelligence/drone-intelligence-system/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![LangChain](https://img.shields.io/badge/LangChain-LangGraph-1C3C3C.svg?style=flat)](https://langchain.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorStore-FF6F00.svg?style=flat)](https://trychroma.com)
[![Python Tests](https://img.shields.io/badge/Tests-18%20Passed-brightgreen.svg?style=flat)](./tests)

An end-to-end production AI/ML system built for the **JulleyOnline AI/ML Internship Assessment**. This application serves as India's comprehensive drone knowledge hub, featuring an advanced **Multi-Query RAG Pipeline** with persistent **ChromaDB**, a **Model Context Protocol (MCP) Calculation Server**, a **FastAPI REST Backend**, and an interactive **React Dashboard**.

---

## 📋 Table of Contents
- [Problem Statement & Project Objectives](#-problem-statement--project-objectives)
- [System Architecture](#-system-architecture)
- [Phase-by-Phase Implementation](#-phase-by-phase-implementation)
  - [Phase 1: Research & Data Collection](#phase-1-research--data-collection)
  - [Phase 2: Data Generation & Dataset Creation](#phase-2-data-generation--dataset-creation)
  - [Phase 3: RAG System Implementation](#phase-3-rag-system-implementation)
  - [Phase 4: MCP Server Development](#phase-4-mcp-server-development)
  - [Phase 5: FastAPI Backend Development](#phase-5-fastapi-backend-development)
  - [Phase 6: Interactive Dashboard](#phase-6-interactive-dashboard)
- [Repository Structure](#-repository-structure)
- [Quick Start Guide](#-quick-start-guide)
- [API Documentation](#-api-documentation)
- [Automated Testing](#-automated-testing)
- [Docker & CI/CD Deployment](#-docker--cicd-deployment)
- [Submission Guidelines & Contact](#-submission-guidelines--contact)

---

## 🎯 Problem Statement & Project Objectives

India's drone industry is undergoing exponential growth across agriculture (spraying/monitoring), logistics (BVLOS medical delivery), infrastructure inspection, and defense. However, no centralized platform exists that provides comprehensive drone regulations, hardware specifications, operational use cases, and business ROI tools tailored specifically to India.

### Core Objectives:
1. **Research & Data Collection**: Compile authoritative data on Indian drone OEMs, DGCA Drone Rules 2021 (amended 2023), DigitalSky airspace zones, and government policies (PLI scheme, Namo Drone Didi).
2. **Dataset Creation**: Build structured catalogs, unstructured handbooks, and synthetic telemetry/ROI datasets.
3. **Advanced RAG Pipeline**: Build a LangGraph-driven RAG pipeline with ChromaDB vector search, Multi-Query expansion, Hybrid BM25 retrieval, Reciprocal Rank Fusion (RRF) reranking, and Gemini LLM synthesis.
4. **MCP Server**: Develop a standalone Model Context Protocol server featuring 4 domain-specific calculation tools.
5. **FastAPI Backend**: Expose REST endpoints with an intelligent 95% tool-relevance router and persistent SQLite chat history.
6. **Interactive Dashboard**: Build a responsive React 19 + TypeScript dashboard with dark/light mode, real-time AI agent chat, tool panels, visual Recharts analytics, and document ingestion.

---

## 🏛 System Architecture

```
                          ┌─────────────────────────────────────────┐
                          │   React 19 + TypeScript Dashboard UI    │
                          │     (Chat, Calculators, Analytics)      │
                          └────────────────────┬────────────────────┘
                                               │ HTTP / REST
                                               ▼
                          ┌─────────────────────────────────────────┐
                          │         FastAPI REST Backend            │
                          │   (Intelligent 95% Tool Router & Auth)  │
                          └──────────┬───────────────────┬──────────┘
                                     │                   │
                     Relevance < 95% │                   │ Relevance ≥ 95%
                                     ▼                   ▼
┌──────────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│      LangGraph RAG StateGraph            │   │         MCP Tool Server Engine           │
│ ┌──────────────────────────────────────┐ │   │ ┌──────────────────────────────────────┐ │
│ │ 1. Multi-Query Expansion             │ │   │ │ • Flight Time Calculator             │ │
│ │ 2. Hybrid BM25 + Dense Vector Search │ │   │ │ • Agriculture ROI Calculator         │ │
│ │ 3. Reciprocal Rank Fusion (RRF)      │ │   │ │ • DGCA Compliance Checker            │ │
│ │ 4. Gemini LLM + Source Attribution   │ │   │ │ • Drone Selection Assistant          │ │
│ └──────────────────┬───────────────────┘ │   │ └──────────────────┬───────────────────┘ │
└────────────────────┼─────────────────────┘   └────────────────────┼─────────────────────┘
                     │                                              │
                     ▼                                              ▼
┌──────────────────────────────────────────┐   ┌──────────────────────────────────────────┐
│   Persistent ChromaDB & Knowledge Base   │   │  Persistent SQLite Conversation History  │
│  (rules_regulations.json, handbooks, etc)│   │       (data/sessions/chat_history.db)    │
└──────────────────────────────────────────┘   └──────────────────────────────────────────┘
```

---

## 🔬 Phase-by-Phase Implementation

### Phase 1: Research & Data Collection
Comprehensive research on India's drone ecosystem documented in `data/raw/`:
- **Use Cases**: Agriculture (crop spraying/monitoring), BVLOS Logistics, Solar/Wind Inspection, Defense ISR, SVAMITVA Surveying.
- **Rules & Regulations**: DGCA Drone Rules 2021 (amended 2023), Green/Yellow/Red airspace zones, UIN registration, Remote Pilot Certificate (RPC), NPNT compliance, Rule 24 penalties.
- **Business Scope**: Namo Drone Didi 50–80% capital subsidy, Production Linked Incentive (PLI) scheme, Indian OEMs (ideaForge, Marut Drones, IoTechWorld, Garuda, Asteria, Throttle).

### Phase 2: Data Generation & Dataset Creation
- **Structured Data (`data/raw/`)**: `drone_models.json`, `rules_regulations.json`, `use_cases.json`, `indian_drone_ecosystem.json`.
- **Unstructured Data (`data/raw/`)**: `dgca_regulations_handbook.md`, `agricultural_drone_case_study.md`, `drone_logistics_and_inspection.md`.
- **Synthetic Data Generation (`scripts/generate_synthetic_data.py`)**:
  - `data/synthetic/flight_telemetry.csv`: 500+ minute-by-minute flight telemetry records (battery, wind, temperature, altitude, drawdown).
  - `data/synthetic/farm_roi_simulations.csv`: 100+ operational farm ROI business scenarios across land sizes and subsidy tiers.
  - `data/synthetic/logistics_scenarios.json`: BVLOS medical delivery corridors and risk profiles.
- **Preprocessing Pipeline (`scripts/preprocess_data.py`)**: Section-aware Markdown splitting (`#`, `##`, `###`), structured JSON metadata enrichment, and chunking.

### Phase 3: RAG System Implementation
- **Vector Database**: Persistent **ChromaDB** (`data/processed/chroma_db`) storing 49+ header-aware document chunks.
- **Embedding Model**: `GoogleGenerativeAIEmbeddings` (`text-embedding-004`) with SentenceTransformers fallback.
- **Multi-Query Expansion**: Expands user query into 3 distinct variations using Gemini LLM to maximize vector recall.
- **Hybrid Retrieval & Reranking**: Combines Dense Vector Search + Sparse Lexical BM25 Search, reranked via **Reciprocal Rank Fusion (RRF)** with keyword overlap boosting (`rag/reranker.py`).
- **Generation & Citation**: Uses Google Gemini LLM (`gemini-2.0-flash`) via LangChain to synthesize responses, explicitly attributing source document filenames (e.g. `📄 Source: dgca_regulations_handbook.md`).

### Phase 4: MCP Server Development
Standalone Model Context Protocol server (`mcp_server/server.py`) exposing 4 tools:
1. **`flight_time_calculator`**: Physics-based flight time, operational range, battery drawdown curve, and wind/temperature safety advice.
2. **`roi_calculator`**: Financial payback period in months, net monthly profit, 3-year projection, and Namo Drone Didi subsidy tiers.
3. **`compliance_checker`**: DGCA compliance status (`APPROVED`, `RESTRICTED`, `PROHIBITED`), required permits, penalties, and DigitalSky workflow steps.
4. **`drone_recommender`**: Matches Indian drone models by budget, sector, flight time, and payload with percentage match scores.

### Phase 5: FastAPI Backend Development
Modular FastAPI architecture (`api/routes/`):
- `POST /api/chat` (or `/chat`): Hybrid RAG + MCP router with automatic SQLite session persistence.
- `POST /api/upload` (or `/upload`): Accepts PDF/Markdown documents, parses text & tables (`pypdf`), chunks content, and seeds ChromaDB live.
- `POST /api/calculate/flight-time`
- `POST /api/calculate/roi`
- `POST /api/check/compliance`
- `POST /api/recommend/drone`
- `GET /api/analytics` (or `/analytics`): System usage statistics, latency benchmarks (P50/P95/P99), popular queries, and chunk counts.
- `GET /api/chat/history/{session_id}` & `DELETE /api/chat/history/{session_id}`: History management endpoints.

### Phase 6: Interactive Dashboard
Modern React 19 + TypeScript + Tailwind CSS UI (`frontend/`):
- **AI Agent Chat**: Real-time response streaming, interactive citations drawer, tool call indicators, and clear history controls.
- **Interactive Calculators**: Live sliders for flight parameters, farm ROI, DGCA compliance, and drone matching.
- **Document Hub**: Drag-and-drop document upload with real-time parsing, chunking, and indexing status indicators.
- **Analytics View**: Interactive Recharts visualizations (latency, query volume, intent breakdown, telemetry scatter plot).
- **UX Excellence**: Dark/Light mode toggle, glassmorphic styling, and fully responsive layout.

---

## 📁 Repository Structure

```
Drone Intelligence System/
├── data/
│   ├── raw/                  # Ground-truth JSON & Markdown handbooks
│   ├── processed/            # Chunked docs & persistent ChromaDB store
│   └── synthetic/            # Flight telemetry, farm ROI CSVs, BVLOS routes
│   └── real_pdfs/            # Real official government PDF documents
├── rag/                      # LangGraph pipeline, embeddings, retriever, reranker, generator
├── mcp_server/               # MCP server & calculation tools
│   └── tools/                # flight_calculator.py, roi_calculator.py, compliance_checker.py, drone_recommender.py
├── api/                      # FastAPI entrypoint, models, services, modular routes
│   ├── routes/               # chat.py, upload.py, calculators.py, analytics.py
│   ├── models/               # Pydantic schemas (schemas.py)
│   └── services/             # rag_service.py, mcp_service.py, history_service.py, upload_service.py
├── frontend/                 # React 19 + TypeScript dashboard
│   ├── public/
│   └── src/                  # Components, services, styles
├── tests/                    # Pytest suite (18 unit & integration tests)
├── scripts/                  # Data generation, preprocessing, vector DB seeding scripts
├── docs/                     # Architecture documentation, API specs, user guide
├── .github/workflows/        # GitHub Actions CI/CD workflow (ci.yml)
├── Dockerfile                # Multi-stage backend container configuration
├── docker-compose.yml        # Orchestrates Backend (:8000) & Frontend (:5173)
├── requirements.txt          # Python dependencies
└── README.md                 # System documentation & setup guide
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.12+
- Node.js 20+ & npm
- Google Gemini API Key (`GEMINI_API_KEY`)

### Option A: Local Execution

1. **Clone Repository & Set Up Virtual Environment**:
   ```bash
   git clone https://github.com/drone-intelligence/drone-intelligence-system.git
   cd "Drone Intelligence System"
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Generate Data & Seed Vector Database**:
   ```bash
   python scripts/generate_synthetic_data.py
   python scripts/preprocess_data.py
   python scripts/seed_vector_db.py
   ```

3. **Start FastAPI Backend Server**:
   ```bash
   python -m uvicorn api.main:app --reload --port 8000
   ```
   - Swagger API Docs: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

4. **Start React Frontend Dashboard**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - Open browser: `http://localhost:5173`

---

## 📡 API Documentation

| Endpoint | Method | Description | Payload Example |
|---|---|---|---|
| `/api/chat` | `POST` | RAG + MCP Hybrid Query with Chat History | `{"message": "What are DGCA rules for micro drones?", "session_id": "s1"}` |
| `/api/upload` | `POST` | Upload & Index New PDF/Markdown Document | `{"file_name": "rules.md", "content": "# Rules..."}` |
| `/api/calculate/flight-time` | `POST` | Calculate Flight Time & Range | `{"battery_mah": 10000, "empty_weight": 3.0, "payload": 2.0, "wind": 10, "temperature": 28}` |
| `/api/calculate/roi` | `POST` | Compute Agriculture Operational ROI | `{"sector": "Agriculture", "investment": 750000, "monthly_opex": 25000, "fee_per_acre": 400, "monthly_acres": 500, "subsidy_pct": 50}` |
| `/api/check/compliance` | `POST` | DGCA Airspace Compliance Evaluation | `{"weight_category": "Small", "purpose": "Commercial", "zone": "Green", "altitude": 200, "rpc": true}` |
| `/api/recommend/drone` | `POST` | Indian Drone Model Recommendation | `{"budget_lakhs": 10.0, "sector": "Agriculture", "min_flight_time": 15, "min_payload": 8}` |
| `/api/analytics` | `GET` | Usage Statistics & System Latency | N/A |
| `/api/chat/history/{session_id}` | `GET` / `DELETE` | Retrieve or Clear Session History | N/A |

---

## 🧪 Automated Testing

The repository includes a comprehensive `pytest` test suite covering API endpoints, MCP tool logic, and RAG retrieval components.

```bash
pytest tests/ -v
```

### Test Results:
```
tests/test_api.py::test_health_check PASSED                              [  5%]
tests/test_api.py::test_chat_endpoint PASSED                             [ 11%]
tests/test_api.py::test_calculate_flight_time_endpoint PASSED            [ 16%]
tests/test_api.py::test_calculate_roi_endpoint PASSED                    [ 22%]
tests/test_api.py::test_check_compliance_endpoint PASSED                 [ 27%]
tests/test_api.py::test_recommend_drone_endpoint PASSED                  [ 33%]
tests/test_api.py::test_chat_history_persistence PASSED                  [ 38%]
tests/test_api.py::test_analytics_endpoint PASSED                        [ 44%]
tests/test_api.py::test_upload_endpoint PASSED                           [ 50%]
tests/test_mcp_tools.py::test_flight_time_calculator PASSED              [ 55%]
tests/test_mcp_tools.py::test_roi_calculator PASSED                      [ 61%]
tests/test_mcp_tools.py::test_compliance_checker_green_zone PASSED       [ 66%]
tests/test_mcp_tools.py::test_compliance_checker_red_zone PASSED         [ 72%]
tests/test_mcp_tools.py::test_drone_recommender PASSED                   [ 77%]
tests/test_rag.py::test_vector_store_add_and_search PASSED               [ 83%]
tests/test_rag.py::test_rag_generator_local_synthesis PASSED             [ 88%]
tests/test_rag.py::test_reranker PASSED                                  [ 94%]
tests/test_rag.py::test_hybrid_retriever PASSED                          [100%]

======================= 18 passed in 2.46s =======================
```

---

## 🐳 Docker & CI/CD Deployment

### Run Containerized System via Docker Compose:
```bash
docker-compose up --build
```
- **Backend API Container**: Runs on port `8000`
- **Frontend Dashboard Container**: Runs on port `5173`

### CI/CD Pipeline:
GitHub Actions workflow (`.github/workflows/ci.yml`) automatically runs:
1. Python 3.12 dependency installation & data pipeline execution.
2. Pytest suite execution across API, RAG, and MCP modules.
3. Node.js 20 frontend production bundle build (`npm run build`).

