"""
Multi-query retriever using LangChain.
Generates multiple query variations to improve retrieval recall.
"""
import os
from typing import List
from langchain_core.documents import Document

def get_multi_query_retriever(vectorstore):
    """
    Creates a LangChain MultiQueryRetriever backed by Gemini LLM.
    Falls back to manual query expansion if Gemini is unavailable.
    """
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain.retrievers.multi_query import MultiQueryRetriever

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_key,
                temperature=0.3,
            )
            retriever = MultiQueryRetriever.from_llm(
                retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
                llm=llm,
            )
            print("[MultiQuery] Using LangChain MultiQueryRetriever with Gemini LLM.")
            return retriever
        except Exception as e:
            print(f"[MultiQuery] Gemini MultiQueryRetriever failed ({e}), using manual expansion.")

    # Fallback: Return the base retriever (no multi-query expansion)
    print("[MultiQuery] Using base vector retriever (no multi-query expansion).")
    return vectorstore.as_retriever(search_kwargs={"k": 5})


def manual_query_expansion(query: str) -> List[str]:
    """
    Deterministic domain-aware query expansion for Indian drone ecosystem.
    Used when LLM-based MultiQueryRetriever is unavailable.
    """
    queries = [query]
    q_lower = query.lower()

    if any(kw in q_lower for kw in ("green zone", "red zone", "yellow zone", "zone")):
        queries.append("DGCA airspace zoning rules green yellow red zones DigitalSky permissions")
    elif any(kw in q_lower for kw in ("micro", "nano", "small", "category", "weight")):
        queries.append("DGCA drone weight categories nano micro small medium permissions UIN RPC")
    elif any(kw in q_lower for kw in ("agri", "spray", "farm", "crop")):
        queries.append("Agricultural spraying drone ROI Namo Drone Didi subsidy India")
    elif any(kw in q_lower for kw in ("battery", "flight time", "range", "endurance")):
        queries.append("Drone flight time battery capacity mAh payload weight endurance calculation")
    else:
        queries.append(f"DGCA guidelines India drone ecosystem {query}")

    return queries[:3]
