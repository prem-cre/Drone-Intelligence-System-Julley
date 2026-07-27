import os
import json
import math
from typing import List, Dict, Any
from rag.embeddings import EmbeddingModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "data", "processed", "vector_store")
os.makedirs(DB_DIR, exist_ok=True)

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

class VectorStore:
    def __init__(self, collection_name: str = "drone_knowledge"):
        self.collection_name = collection_name
        self.embedding_model = EmbeddingModel()
        self.store_file = os.path.join(DB_DIR, f"{collection_name}.json")
        self.documents: List[Dict[str, Any]] = []
        self._load_store()

    def _load_store(self):
        if os.path.exists(self.store_file):
            try:
                with open(self.store_file, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
                print(f"[VectorStore] Loaded {len(self.documents)} vectors from '{self.store_file}'.")
            except Exception as e:
                print(f"[VectorStore] Error loading store ({e}). Initializing empty.")
                self.documents = []

    def save_store(self):
        with open(self.store_file, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=2)
        print(f"[VectorStore] Saved {len(self.documents)} vectors to '{self.store_file}'.")

    def add_documents(self, docs: List[Dict[str, Any]]):
        """
        docs is a list of dicts: [{'id': str, 'content': str, 'metadata': dict}]
        """
        texts = [d["content"] for d in docs]
        embeddings = self.embedding_model.embed_texts(texts)

        for doc, emb in zip(docs, embeddings):
            # Check for existing document to avoid duplicate IDs
            self.documents = [d for d in self.documents if d["id"] != doc["id"]]
            self.documents.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc.get("metadata", {}),
                "embedding": emb
            })
        self.save_store()

    def similarity_search(self, query: str, top_k: int = 5, filter_category: str = None) -> List[Dict[str, Any]]:
        if not self.documents:
            return []

        query_emb = self.embedding_model.embed_query(query)
        scored_results = []

        query_words = set(query.lower().split())

        for doc in self.documents:
            if filter_category and doc["metadata"].get("category") != filter_category:
                continue

            vector_score = cosine_similarity(query_emb, doc["embedding"])
            
            # Keyword score boost for exact term matches
            content_words = set(doc["content"].lower().split())
            common_words = query_words.intersection(content_words)
            keyword_score = len(common_words) / max(1, len(query_words)) * 0.35

            final_score = vector_score + keyword_score

            scored_results.append({
                "id": doc["id"],
                "content": doc["content"],
                "metadata": doc["metadata"],
                "score": round(final_score, 4)
            })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]
