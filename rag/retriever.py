"""
Retriever module - now delegates to LangChain vector store.
Kept for backward compatibility with any imports.
"""
from typing import List
from langchain_core.documents import Document
from rag.vector_store import get_vectorstore, similarity_search


def get_relevant_documents(query: str, top_k: int = 5) -> List[Document]:
    """Retrieves relevant LangChain Documents from ChromaDB."""
    return similarity_search(query, top_k=top_k)


def format_context(docs: List[Document]) -> str:
    """Formats retrieved documents into a readable context string with citations."""
    blocks = []
    for idx, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        title = doc.metadata.get("title", "Reference")
        score = doc.metadata.get("score", 0.0)
        blocks.append(
            f"[Citation {idx}]: {title} (Source: {source}, Score: {score})\n{doc.page_content}"
        )
    return "\n---\n".join(blocks)
