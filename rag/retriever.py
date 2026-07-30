"""
Advanced Hybrid Retriever module.
Combines Vector Similarity Search (Dense) and Lexical Keyword Search (Sparse BM25 / TF-IDF)
with Reciprocal Rank Fusion (RRF) reranking.
Includes zero-dependency TF-IDF fallback if rank_bm25 package is unavailable.
"""
import math
import re
from typing import List, Optional, Dict
from langchain_core.documents import Document
from rag.vector_store import get_vectorstore, similarity_search
from rag.reranker import reciprocal_rank_fusion


def _tokenize(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric terms."""
    return re.findall(r'\w+', text.lower())


def _builtin_lexical_search(documents: List[Document], query: str, top_k: int = 10) -> List[Document]:
    """
    Built-in TF-IDF / Term Frequency Lexical Retriever.
    Guarantees 100% reliable keyword matching even when rank_bm25 package is absent.
    """
    query_tokens = _tokenize(query)
    if not query_tokens or not documents:
        return documents[:top_k]

    # Calculate Term Frequencies & IDF
    num_docs = len(documents)
    doc_freqs: Dict[str, int] = {}
    doc_token_counts = []

    for doc in documents:
        tokens = _tokenize(doc.page_content + " " + doc.metadata.get("title", ""))
        unique_tokens = set(tokens)
        doc_token_counts.append(tokens)
        for token in unique_tokens:
            doc_freqs[token] = doc_freqs.get(token, 0) + 1

    idf = {}
    for token in set(query_tokens):
        df = doc_freqs.get(token, 0)
        idf[token] = math.log((num_docs + 1) / (df + 1)) + 1.0

    # Score each document using TF-IDF term overlap
    scored_docs = []
    for idx, doc in enumerate(documents):
        tokens = doc_token_counts[idx]
        if not tokens:
            continue
        
        doc_len = len(tokens)
        score = 0.0
        for q_token in query_tokens:
            if q_token in tokens:
                tf = tokens.count(q_token) / doc_len
                score += tf * idf.get(q_token, 1.0)
                
                # Title exact match boost
                title = doc.metadata.get("title", "").lower()
                if q_token in title:
                    score += 0.5

        if score > 0:
            doc_copy = Document(page_content=doc.page_content, metadata=dict(doc.metadata))
            doc_copy.metadata["bm25_score"] = score
            scored_docs.append((score, doc_copy))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored_docs[:top_k]]


class HybridRetriever:
    """
    Advanced Hybrid Retriever that blends:
    1. Vector Similarity Search (Dense Semantic Retrieval via ChromaDB)
    2. BM25 / TF-IDF Lexical Keyword Search (Sparse Term Matching)
    3. Hybrid Reranking via Reciprocal Rank Fusion (RRF) + Keyword Boost
    """

    def __init__(self, collection_name: str = "drone_intelligence_hub"):
        self.collection_name = collection_name

    def _get_lexical_docs(self, query: str, top_k: int = 10) -> List[Document]:
        """Retrieves documents using BM25 or built-in TF-IDF lexical search."""
        try:
            vs = get_vectorstore(self.collection_name)
            raw_data = vs.get()
            if not raw_data or not raw_data.get("documents"):
                return []
                
            documents = []
            metadatas = raw_data.get("metadatas") or []
            for idx, text in enumerate(raw_data["documents"]):
                meta = metadatas[idx] if idx < len(metadatas) and metadatas[idx] else {}
                documents.append(Document(page_content=text, metadata=meta))

            if not documents:
                return []

            # Try rank_bm25 first
            try:
                from langchain_community.retrievers import BM25Retriever
                bm25 = BM25Retriever.from_documents(documents)
                bm25.k = top_k
                return bm25.invoke(query)
            except Exception:
                # Fallback to zero-dependency built-in TF-IDF lexical search
                return _builtin_lexical_search(documents, query, top_k=top_k)

        except Exception as e:
            print(f"[HybridRetriever] Lexical search notice ({e})")
            return []

    def get_relevant_documents(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[dict] = None,
    ) -> List[Document]:
        """
        Retrieves relevant documents using Hybrid (Vector + Lexical Keyword) retrieval
        and Reciprocal Rank Fusion (RRF) reranking.
        """
        candidate_k = max(top_k * 2, 10)

        # 1. Vector Search (Dense)
        vector_docs = similarity_search(
            query,
            top_k=candidate_k,
            filter_dict=filter_dict,
            collection_name=self.collection_name,
        )

        # 2. Lexical Search (Sparse Keyword / TF-IDF / BM25)
        lexical_docs = self._get_lexical_docs(query, top_k=candidate_k)

        # 3. Combine document streams
        doc_lists = []
        if vector_docs:
            doc_lists.append(vector_docs)
        if lexical_docs:
            doc_lists.append(lexical_docs)

        if not doc_lists:
            return []

        # 4. Rerank using Reciprocal Rank Fusion (RRF) + Term overlap boost
        reranked_docs = reciprocal_rank_fusion(
            doc_lists=doc_lists,
            query=query,
            k=60,
            top_n=top_k,
        )
        return reranked_docs


def get_relevant_documents(
    query: str,
    top_k: int = 5,
    collection_name: str = "drone_intelligence_hub",
) -> List[Document]:
    """Retrieves relevant documents using Hybrid Vector + Lexical Keyword Search with RRF Reranking."""
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
