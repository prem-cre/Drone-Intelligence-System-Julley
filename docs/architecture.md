# Architecture & System Design — Drone Intelligence System for India

## Overview
The **Drone Intelligence System** is an end-to-end production AI application engineered to serve as India's comprehensive knowledge hub for drone regulations, specs, use cases, and business economics.

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

## 1. RAG System Architecture
- **Hierarchical Section Chunker**: Splitting text by `#`, `##`, `###` headers + paragraph boundaries (400 char target size, 50 overlap).
- **Embeddings**: Open-source SentenceTransformers (`all-MiniLM-L6-v2` / `BAAI/bge-small-en-v1.5`).
- **Vector Database**: Native persistent **ChromaDB** storing vector representations with HNSW cosine index.
- **Multi-Query Expansion**: Expands user query into 3-4 semantic query variations.
- **Reranker**: Reciprocal Rank Fusion (RRF) + BM25 keyword match scoring.
- **LLM Generator**: Google Gemini API (`gemini-2.0-flash` / `gemini-1.5-flash`) formatting responses with explicit inline source citations.

---

## 2. MCP Server & Tool Architecture
Exposes 4 core domain tools:
1. `flight_time_calculator`: Computes duration, range, battery consumption curve.
2. `roi_calculator`: Computes monthly revenue, net profit, payback timeline, and 3-year financial projection.
3. `compliance_checker`: Evaluates flight operation safety under Drone Rules 2021 across Green/Yellow/Red zones.
4. `drone_recommender`: Ranks Indian drone models matching budget and technical requirements.
