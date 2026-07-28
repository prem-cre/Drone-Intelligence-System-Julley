"""
ChromaDB-backed persistent vector store using LangChain Chroma wrapper.
"""
import os
from typing import List, Optional
from langchain_core.documents import Document
from langchain_chroma import Chroma
from rag.embeddings import get_embedding_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, "data", "processed", "chroma_db")
os.makedirs(CHROMA_DIR, exist_ok=True)

_embedding_model = None

def _get_embeddings():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = get_embedding_model()
    return _embedding_model

def get_vectorstore(collection_name: str = "drone_intelligence_hub") -> Chroma:
    """Returns a persistent LangChain Chroma vector store instance."""
    return Chroma(
        collection_name=collection_name,
        embedding_function=_get_embeddings(),
        persist_directory=CHROMA_DIR,
    )

def add_documents(docs: List[Document], collection_name: str = "drone_intelligence_hub"):
    """Adds LangChain Document objects to the ChromaDB collection."""
    vs = get_vectorstore(collection_name)
    vs.add_documents(docs)
    print(f"[VectorStore] Added {len(docs)} documents to ChromaDB collection '{collection_name}'.")

def similarity_search(
    query: str,
    top_k: int = 5,
    filter_dict: Optional[dict] = None,
    collection_name: str = "drone_intelligence_hub",
) -> List[Document]:
    """Performs similarity search and returns LangChain Document objects with scores."""
    vs = get_vectorstore(collection_name)
    if filter_dict:
        results = vs.similarity_search_with_score(query, k=top_k, filter=filter_dict)
    else:
        results = vs.similarity_search_with_score(query, k=top_k)
    # Attach score to document metadata for downstream use
    docs = []
    for doc, score in results:
        doc.metadata["score"] = round(1.0 - score, 4)  # cosine distance → similarity
        docs.append(doc)
    return docs
