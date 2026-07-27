from typing import List, Dict, Any
from rag.vector_store import VectorStore

class Retriever:
    def __init__(self, vector_store: VectorStore = None):
        self.vector_store = vector_store or VectorStore()

    def get_relevant_documents(self, query: str, top_k: int = 4, category: str = None) -> List[Dict[str, Any]]:
        results = self.vector_store.similarity_search(query=query, top_k=top_k, filter_category=category)
        return results

    def format_context_with_citations(self, docs: List[Dict[str, Any]]) -> str:
        formatted_blocks = []
        for idx, d in enumerate(docs, 1):
            source = d["metadata"].get("source", "Unknown Document")
            title = d["metadata"].get("title", "Reference")
            score = d.get("score", 0.0)
            
            block = (
                f"[Citation {idx}]: {title} (Source: {source}, Relevance: {score})\n"
                f"{d['content']}\n"
            )
            formatted_blocks.append(block)
            
        return "\n-------------------\n".join(formatted_blocks)
