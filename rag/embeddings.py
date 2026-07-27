import os
import math
import re
from typing import List

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.use_openai = bool(os.getenv("OPENAI_API_KEY"))
        self._st_model = None
        
        if not self.use_openai:
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer(model_name)
                print(f"[Embeddings] Loaded SentenceTransformer '{model_name}'.")
            except Exception as e:
                print(f"[Embeddings] SentenceTransformer load skipped ({e}). Using lightweight Vectorizer.")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if self.use_openai:
            try:
                import openai
                client = openai.OpenAI()
                response = client.embeddings.create(
                    input=texts,
                    model="text-embedding-3-small"
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                print(f"[Embeddings] OpenAI embedding call failed ({e}), falling back to local model.")

        if self._st_model:
            embeddings = self._st_model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()

        # Deterministic lightweight TF-IDF / Bag of Words fallback vectorizer (384-d normalized)
        return [self._fallback_vectorize(text) for text in texts]

    def embed_query(self, query: str) -> List[float]:
        return self.embed_texts([query])[0]

    def _fallback_vectorize(self, text: str, dim: int = 384) -> List[float]:
        words = re.findall(r'\w+', text.lower())
        vec = [0.0] * dim
        for w in words:
            h = hash(w) % dim
            vec[h] += 1.0
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec
