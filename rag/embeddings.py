"""
Embedding model wrapper using LangChain.
Primary: Google Gemini text-embedding-004
Fallback: HuggingFace all-MiniLM-L6-v2 / FakeEmbeddings
Uses a Safe Embedding Wrapper proxy to catch runtime API or key errors and handle fallback.
"""
import os
from typing import List

class SafeEmbeddings:
    """
    Proxy embedding class that catches runtime API / quota / authorization exceptions
    and falls back to a local model or fake embeddings dynamically.
    """
    def __init__(self, primary, fallback):
        self.primary = primary
        self.fallback = fallback
        self.use_fallback = False

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.use_fallback and self.primary:
            try:
                return self.primary.embed_documents(texts)
            except Exception as e:
                print(f"[Embeddings] Gemini embedding execution failed ({e}). Switching to local fallback.")
                self.use_fallback = True
        return self.fallback.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        if not self.use_fallback and self.primary:
            try:
                return self.primary.embed_query(text)
            except Exception as e:
                print(f"[Embeddings] Gemini query embedding execution failed ({e}). Switching to local fallback.")
                self.use_fallback = True
        return self.fallback.embed_query(text)


def _get_local_fallback():
    """Returns local HuggingFace or FakeEmbeddings fallback."""
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("[Embeddings] Initialized HuggingFace all-MiniLM-L6-v2 (local).")
        return model
    except Exception as e:
        print(f"[Embeddings] HuggingFace initialization failed ({e}), using FakeEmbeddings.")
        
    from langchain_community.embeddings import FakeEmbeddings
    return FakeEmbeddings(size=384)


def get_embedding_model():
    """Returns a LangChain-compatible embedding model instance wrapped in a SafeEmbeddings proxy."""
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    primary = None
    if gemini_key:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            primary = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=gemini_key,
            )
            print("[Embeddings] Configured Google Gemini text-embedding-004.")
        except Exception as e:
            print(f"[Embeddings] Gemini configuration failed ({e}).")

    fallback = _get_local_fallback()
    return SafeEmbeddings(primary=primary, fallback=fallback)
