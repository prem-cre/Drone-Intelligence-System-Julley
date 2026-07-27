# Drone Intelligence System (Julley) 🛸

An end-to-end AI-powered **Drone Intelligence Platform** integrating Retrieval-Augmented Generation (RAG), real-time flight telemetry analytics, DGCA regulations knowledge base, MCP server tooling, and a web dashboard (**Drone Sky Wisdom**).

---

## 🌟 Key Features

- 📚 **DGCA & Indian Drone Regulations RAG Engine**: Vector search and context-aware Q&A over official DGCA handbooks, drone policies, airspace rules, and industry use-cases.
- 📊 **Telemetry & ROI Analytics**: Synthetic flight telemetry analysis, farm ROI simulations, and logistics mission planning.
- 🔌 **MCP Server**: Model Context Protocol tool definitions for drone flight query execution and automated regulation lookup.
- 💻 **Drone Sky Wisdom Web Dashboard**: React + Vite + TanStack app featuring dynamic analytics, interactive ROI calculators, document explorer, and AI assistant chat.
- ⚙️ **Data Preprocessing & Synthetic Generation**: Automated data processing and vector database seeding pipelines.

---

## 📁 Repository Structure

```
Drone-Intelligence-System/
├── api/                   # Backend API service models, routes, and services
├── data/                  # Raw handbooks, processed chunks, synthetic telemetry & ROI data
│   ├── raw/               # DGCA regulations, drone models, case studies
│   ├── processed/         # Pre-chunked RAG vector dataset
│   └── synthetic/         # Telemetry CSVs, farm ROI simulations, logistics scenarios
├── docs/                  # Project documentation & guides
├── mcp_server/            # Model Context Protocol (MCP) server & custom tools
├── rag/                   # RAG architecture: Embeddings, Vector Store, Retriever, Generator
├── scripts/               # Data preprocessing, synthetic data generator, vector DB seeders
├── tests/                 # Integration and unit test suite
└── drone-sky-wisdom-main/ # Web frontend application (React + Vite + TanStack)
```

---

## 🚀 Getting Started

### Backend & RAG Engine Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/prem-cre/Drone-Intelligence-System-Julley.git
   cd Drone-Intelligence-System-Julley
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Preprocess data and seed vector database**:
   ```bash
   python scripts/preprocess_data.py
   python scripts/seed_vector_db.py
   ```

### Frontend Application Setup (Drone Sky Wisdom)

1. **Navigate to the frontend directory**:
   ```bash
   cd drone-sky-wisdom-main
   ```

2. **Install dependencies**:
   ```bash
   npm install # or bun install
   ```

3. **Launch dev server**:
   ```bash
   npm run dev
   ```

---

## 📜 License

MIT License. Developed for Drone Intelligence Platform - Julley project.
