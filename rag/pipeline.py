from typing import Dict, Any, List
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.generator import RAGGenerator

class RAGPipeline:
    def __init__(self, collection_name: str = "drone_knowledge"):
        self.vector_store = VectorStore(collection_name=collection_name)
        self.retriever = Retriever(vector_store=self.vector_store)
        self.generator = RAGGenerator()

    def query(self, question: str, top_k: int = 4, category: str = None) -> Dict[str, Any]:
        docs = self.retriever.get_relevant_documents(query=question, top_k=top_k, category=category)
        formatted_context = self.retriever.format_context_with_citations(docs)
        result = self.generator.generate_response(query=question, context=formatted_context, docs=docs)
        return result

    def ingest_documents(self, docs: List[Dict[str, Any]]) -> int:
        self.vector_store.add_documents(docs)
        return len(docs)
