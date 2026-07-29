"""
Advanced Hybrid Retriever module.
Combines Vector Similarity Search (Dense) and BM25 Lexical Keyword Search (Sparse)
with Reciprocal Rank Fusion (RRF) reranking.
"""
from typing import List, Optional
from langchain_core.documents import Document
from rag.vector_store import get_vectorstore, similarity_search
from rag.reranker import reciprocal_rank_fusion


class HybridRetriever:
    """
    Advanced Hybrid Retriever that blends:
    1. Vector Similarity Search (Dense Semantic Retrieval via ChromaDB)
    2. BM25 Lexical Keyword Search (Sparse Term Matching)
    3. Hybrid Reranking via Reciprocal Rank Fusion (RRF) + Keyword Boost
    """

    def __init__(self, collection_name: str = "drone_intelligence_hub"):
        self.collection_name = collection_name

    def _get_bm25_retriever(self, top_k: int = 10):
        """Constructs a BM25 retriever dynamically from ChromaDB stored documents."""
        try:
            vs = get_vectorstore(self.collection_name)
            raw_data = vs.get()
            if raw_data and raw_data.get("documents"):
                documents = []
                metadatas = raw_data.get("metadatas") or []
                for idx, text in enumerate(raw_data["documents"]):
                    meta = metadatas[idx] if idx < len(metadatas) and metadatas[idx] else {}
                    documents.append(Document(page_content=text, metadata=meta))
                if documents:
                    from langchain_community.retrievers import BM25Retriever
                    bm25 = BM25Retriever.from_documents(documents)
                    bm25.k = top_k
                    return bm25
        except Exception as e:
            print(f"[HybridRetriever] BM25 initialization notice: {e}")
        return None

    def get_relevant_documents(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[dict] = None,
    ) -> List[Document]:
        """
        Retrieves relevant documents using Hybrid (Vector + Keyword) retrieval
        and Reciprocal Rank Fusion (RRF) reranking.
        """
        candidate_k = max(top_k * 2, 8)

        # 1. Vector Search (Dense)
        vector_docs = similarity_search(
            query,
            top_k=candidate_k,
            filter_dict=filter_dict,
            collection_name=self.collection_name,
        )

        # 2. BM25 Search (Sparse Keyword)
        bm25_docs = []
        bm25_retriever = self._get_bm25_retriever(top_k=candidate_k)
        if bm25_retriever:
            try:
                bm25_docs = bm25_retriever.invoke(query)
            except Exception as e:
                print(f"[HybridRetriever] BM25 query failed ({e}), using vector candidates only.")

        # 3. Combine document streams
        doc_lists = []
        if vector_docs:
            doc_lists.append(vector_docs)
        if bm25_docs:
            doc_lists.append(bm25_docs)

        if not doc_lists:
            return []

        # 4. Rerank using Reciprocal Rank Fusion (RRF) + BM25 term overlap boost
        reranked_docs = reciprocal_rank_fusion(
            doc_lists=doc_lists,
            query=query,
            k=60,
            top_n=top_k,
        )
        return reranked_docs


# Function interface for backward compatibility & simple calls
def get_relevant_documents(
    query: str,
    top_k: int = 5,
    collection_name: str = "drone_intelligence_hub",
) -> List[Document]:
    """Retrieves relevant documents using Hybrid Vector + BM25 Keyword Search with RRF Reranking."""
    retriever = HybridRetriever(collection_name=collection_name)
    return retriever.get_relevant_documents(query=query, top_k=top_k)


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
