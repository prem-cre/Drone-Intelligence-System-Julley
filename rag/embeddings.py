"""
Embedding model wrapper using LangChain.
Primary: Google Gemini text-embedding-004
Fallback: HuggingFace all-MiniLM-L6-v2
"""
import os

def get_embedding_model():
    """Returns a LangChain-compatible embedding model instance."""
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    # 1. Try Gemini Embeddings (best quality, free tier available)
    if gemini_key:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            model = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=gemini_key,
            )
            print("[Embeddings] Using Google Gemini text-embedding-004.")
            return model
        except Exception as e:
            print(f"[Embeddings] Gemini init failed ({e}), trying HuggingFace fallback.")

    # 2. Fallback: Local HuggingFace open-source model
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("[Embeddings] Using HuggingFace all-MiniLM-L6-v2 (local).")
        return model
    except Exception as e:
        print(f"[Embeddings] HuggingFace init failed ({e}), using lightweight fallback.")

    # 3. Last resort: deterministic hash-based vectorizer for zero-dep environments
    from langchain_community.embeddings import FakeEmbeddings
    print("[Embeddings] Using FakeEmbeddings fallback (384-d). Install sentence-transformers for real vectors.")
    return FakeEmbeddings(size=384)
