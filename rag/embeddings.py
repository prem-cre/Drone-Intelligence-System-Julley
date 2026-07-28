import os
import math
import re
from typing import List

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.use_gemini = bool(self.gemini_key)
        self.use_openai = bool(os.getenv("OPENAI_API_KEY")) and not self.use_gemini
        self._st_model = None
        
        if self.use_gemini:
            print(f"[Embeddings] Enabled Gemini Embeddings API (model: text-embedding-004).")
        elif self.use_openai:
            print(f"[Embeddings] Enabled OpenAI Embeddings API (model: text-embedding-3-small).")
        else:
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer(model_name)
                print(f"[Embeddings] Loaded SentenceTransformer '{model_name}'.")
            except Exception as e:
                print(f"[Embeddings] SentenceTransformer load skipped ({e}). Using lightweight Vectorizer.")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # 1. Gemini Embeddings
        if self.use_gemini:
            try:
                try:
                    from google import genai
                    client = genai.Client(api_key=self.gemini_key)
                    res = client.models.embed_content(
                        model="text-embedding-004",
                        contents=texts
                    )
                    return [item.values for item in res.embeddings]
                except ImportError:
                    import google.generativeai as gai
                    gai.configure(api_key=self.gemini_key)
                    embeddings = []
                    for txt in texts:
                        res = gai.embed_content(
                            model="models/text-embedding-004",
                            content=txt
                        )
                        embeddings.append(res['embedding'])
                    return embeddings
            except Exception as e:
                print(f"[Embeddings] Gemini embedding API call failed ({e}), falling back to local model.")

        # 2. OpenAI Embeddings
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

        # 3. SentenceTransformers
        if self._st_model:
            embeddings = self._st_model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()

        # 4. Deterministic lightweight TF-IDF / Bag of Words fallback vectorizer (384-d normalized)
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

