"""
Reciprocal Rank Fusion (RRF) reranker compatible with LangChain Documents.
Fuses results from multiple retrieval queries and applies BM25 keyword boost.
"""
import re
from typing import List
from langchain_core.documents import Document


def reciprocal_rank_fusion(
    doc_lists: List[List[Document]],
    query: str,
    k: int = 60,
    top_n: int = 5,
) -> List[Document]:
    """
    Applies Reciprocal Rank Fusion across multiple ranked document lists.

    RRF Formula: score(d) = sum( 1 / (k + rank(d, q)) ) for each query q
    Plus BM25 exact keyword match boost for term overlap.

    Args:
        doc_lists: List of ranked document lists (one per query variation).
        query: Original user query for keyword matching.
        k: RRF constant (default 60).
        top_n: Number of top documents to return.

    Returns:
        List of top_n LangChain Documents with score in metadata.
    """
    doc_scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}
    query_words = set(re.findall(r'\w+', query.lower()))

    # Step 1: RRF scoring across all query result lists
    for doc_list in doc_lists:
        for rank, doc in enumerate(doc_list, 1):
            doc_id = doc.metadata.get("source", "") + ":" + str(doc.metadata.get("chunk_index", id(doc)))
            doc_map[doc_id] = doc
            rrf_score = 1.0 / (k + rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0.0) + rrf_score

    # Step 2: BM25 keyword overlap boost
    results = []
    for doc_id, rrf_score in doc_scores.items():
        doc = doc_map[doc_id]
        content_words = set(re.findall(r'\w+', doc.page_content.lower()))
        overlap = query_words.intersection(content_words)
        bm25_boost = (len(overlap) / max(1, len(query_words))) * 0.15

        combined_score = round(rrf_score + bm25_boost, 4)
        doc.metadata["score"] = combined_score
        results.append(doc)

    # Sort by combined score descending
    results.sort(key=lambda d: d.metadata.get("score", 0), reverse=True)
    return results[:top_n]
