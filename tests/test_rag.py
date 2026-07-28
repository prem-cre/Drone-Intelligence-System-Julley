import pytest
from langchain_core.documents import Document
from rag.vector_store import get_vectorstore, add_documents, similarity_search
from rag.generator import generate_response

def test_vector_store_add_and_search():
    vs = get_vectorstore("test_langchain_collection")
    test_docs = [
        Document(page_content="Micro drones weigh between 250 grams and 2 kg.", metadata={"source": "test.md", "title": "Micro Rules", "category": "regulations", "chunk_index": 1}),
        Document(page_content="Agricultural drones require 10L spraying tanks.", metadata={"source": "agri.md", "title": "Agri Specs", "category": "agriculture", "chunk_index": 1}),
    ]
    vs.add_documents(test_docs)
    results = similarity_search("What is the weight of micro drones?", top_k=1, collection_name="test_langchain_collection")
    assert len(results) >= 1

def test_rag_generator_local_synthesis():
    test_docs = [
        Document(page_content="Micro drones operating in green zones below 400ft require no flight permission.", metadata={"source": "dgca.md", "title": "Green Zone", "chunk_index": 1}),
    ]
    res = generate_response("Can I fly micro drones in green zones?", test_docs)
    assert "answer" in res
    assert len(res["citations"]) == 1

def test_reranker():
    from rag.reranker import reciprocal_rank_fusion
    doc_list_1 = [
        Document(page_content="Micro drone rules under DGCA 2021", metadata={"source": "rules.md", "chunk_index": 1}),
        Document(page_content="Agricultural spraying drone specs", metadata={"source": "agri.md", "chunk_index": 1}),
    ]
    doc_list_2 = [
        Document(page_content="Agricultural spraying drone specs", metadata={"source": "agri.md", "chunk_index": 1}),
        Document(page_content="Micro drone rules under DGCA 2021", metadata={"source": "rules.md", "chunk_index": 1}),
    ]
    results = reciprocal_rank_fusion([doc_list_1, doc_list_2], query="micro drone rules", top_n=2)
    assert len(results) == 2
    assert results[0].metadata["score"] > 0
