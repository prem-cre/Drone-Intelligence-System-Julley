# Multi-stage Dockerfile for Drone Intelligence System
FROM python:3.12-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY api/ ./api/
COPY rag/ ./rag/
COPY mcp_server/ ./mcp_server/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Expose FastAPI port
EXPOSE 8000

# Run database seeding and start FastAPI server
CMD ["sh", "-c", "python scripts/generate_synthetic_data.py && python scripts/preprocess_data.py && python scripts/seed_vector_db.py && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000"]
