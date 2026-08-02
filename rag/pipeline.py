"""
RAG Pipeline built with LangGraph StateGraph.

Flow:  retrieve → rerank → generate

Uses:
- LangChain Chroma for vector retrieval
- MultiQueryRetriever (Gemini) for query expansion
- Reciprocal Rank Fusion (RRF) + BM25 for reranking
- Google Gemini (gemini-2.0-flash) for response generation
"""
import os
import sys
from typing import TypedDict, List, Dict, Any

from langchain_core.documents import Document
from langgraph.graph import StateGraph, END

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from rag.vector_store import get_vectorstore, add_documents, similarity_search
from rag.multi_query import manual_query_expansion, get_multi_query_retriever
from rag.reranker import reciprocal_rank_fusion
from rag.generator import generate_response


# ── LangGraph State ──
class RAGState(TypedDict):
    query: str
    chat_history: str
    expanded_queries: List[str]
    retrieved_docs: List[List[Document]]
    reranked_docs: List[Document]
    answer: str
    citations: List[Dict[str, Any]]


# ── Node Functions ──

def retrieve_node(state: RAGState) -> dict:
    """Retrieves documents using Hybrid Vector + Lexical Keyword Search."""
    query = state["query"]
    from rag.retriever import get_relevant_documents
    
    docs = get_relevant_documents(query, top_k=5)
    print(f"[RAG:Retrieve] HybridRetriever returned {len(docs)} documents.")
    return {"retrieved_docs": [docs]}


def rerank_node(state: RAGState) -> dict:
    """Reranks retrieved documents using Reciprocal Rank Fusion + BM25."""
    doc_lists = state.get("retrieved_docs", [])
    query = state["query"]

    if not doc_lists or all(len(dl) == 0 for dl in doc_lists):
        print("[RAG:Rerank] No documents to rerank.")
        return {"reranked_docs": []}

    reranked = reciprocal_rank_fusion(doc_lists, query=query, top_n=4)
    print(f"[RAG:Rerank] RRF reranked to top {len(reranked)} documents.")
    return {"reranked_docs": reranked}


def generate_node(state: RAGState) -> dict:
    """Generates final answer using Gemini / Groq LLM with retrieved context and conversation history."""
    docs = state.get("reranked_docs", [])
    query = state["query"]
    chat_history = state.get("chat_history", "")

    result = generate_response(query, docs, chat_history=chat_history)
    return {"answer": result["answer"], "citations": result["citations"]}


from langgraph.checkpoint.memory import MemorySaver


# ── Build LangGraph ──

def build_rag_graph(checkpointer=None) -> StateGraph:
    """Constructs the LangGraph RAG pipeline: retrieve → rerank → generate."""
    graph = StateGraph(RAGState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "generate")
    graph.add_edge("generate", END)

    if checkpointer:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()


# ── High-Level Pipeline Class ──

class RAGPipeline:
    """
    Production RAG Pipeline powered by LangChain + LangGraph.

    Architecture:
    - LangChain Chroma for persistent vector storage
    - MultiQueryRetriever with Gemini LLM for query expansion
    - Reciprocal Rank Fusion (RRF) + BM25 for hybrid reranking
    - Google Gemini / Groq Llama 3.3 for response generation
    - LangGraph StateGraph with MemorySaver thread_id checkpointer for session state
    """

    def __init__(self):
        self.checkpointer = MemorySaver()
        self.graph = build_rag_graph(checkpointer=self.checkpointer)
        print("[RAGPipeline] LangGraph RAG pipeline initialized with thread MemorySaver state checkpointing.")

    def query(
        self,
        question: str,
        session_id: str = "default",
        chat_history: str = "",
        top_k: int = 4,
        category: str = None
    ) -> Dict[str, Any]:
        """Execute the full RAG pipeline for a user question with session thread persistence."""
        initial_state: RAGState = {
            "query": question,
            "chat_history": chat_history,
            "expanded_queries": [],
            "retrieved_docs": [],
            "reranked_docs": [],
            "answer": "",
            "citations": [],
        }
        config = {"configurable": {"thread_id": session_id}}
        result = self.graph.invoke(initial_state, config=config)
        return {
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
        }

    def ingest_documents(self, docs: List[Dict[str, Any]]) -> int:
        """Ingests document dicts into ChromaDB via LangChain."""
        lc_docs = []
        for d in docs:
            lc_docs.append(Document(
                page_content=d["content"],
                metadata=d.get("metadata", {}),
            ))
        add_documents(lc_docs)
        return len(lc_docs)
