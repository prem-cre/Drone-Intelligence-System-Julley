"""
Seeds the ChromaDB vector store with preprocessed document chunks.
Uses LangChain Document objects and the RAGPipeline.ingest_documents() method.
"""
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from rag.pipeline import RAGPipeline

PROCESSED_FILE = os.path.join(BASE_DIR, "data", "processed", "chunked_rag_docs.json")

def seed_database():
    if not os.path.exists(PROCESSED_FILE):
        print(f"[Seed] Processed file missing: {PROCESSED_FILE}. Run preprocess_data.py first.")
        return

    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"[Seed] Indexing {len(chunks)} chunks into ChromaDB via LangChain...")
    pipeline = RAGPipeline()
    count = pipeline.ingest_documents(chunks)
    print(f"[Seed] Successfully seeded {count} chunks into ChromaDB.")

if __name__ == "__main__":
    seed_database()
