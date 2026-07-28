"""
RAG response generator using LangChain + Google Gemini LLM.
Falls back to a domain-aware local synthesis engine when no API key is available.
"""
import os
from typing import List, Dict, Any
from langchain_core.documents import Document

SYSTEM_PROMPT = """You are India's premier Drone Intelligence System AI assistant.
Your goal is to provide accurate, authoritative, and structured technical and regulatory answers regarding drones in India based strictly on retrieved knowledge context.

Rules:
1. Always base your answers on the provided Context & Citations.
2. Structure your response cleanly using GitHub-style markdown (headings, tables, bullet points).
3. Always include explicit source citations inline (e.g. [Source: DGCA Handbook]).
4. If the context does not contain enough information, state what is known and clearly outline caveats.
"""


def generate_response(query: str, docs: List[Document]) -> Dict[str, Any]:
    """
    Generates a RAG response from retrieved documents.
    Uses Gemini LLM via LangChain when available, otherwise falls back to local synthesis.
    """
    # Format context from retrieved documents
    context_blocks = []
    for idx, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Document")
        section = doc.metadata.get("section", "Section")
        score = doc.metadata.get("score", 0.0)
        context_blocks.append(
            f"[Citation {idx}] {section} (Source: {source}, Score: {score})\n{doc.page_content}"
        )
    context = "\n---\n".join(context_blocks)

    # Try LLM generation
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    answer_text = None

    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.prompts import ChatPromptTemplate

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=gemini_key,
                temperature=0.3,
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "Retrieved Context:\n{context}\n\nUser Question: {query}\n\nPlease answer the user question based on the context above."),
            ])
            chain = prompt | llm
            response = chain.invoke({"context": context, "query": query})
            answer_text = response.content
        except Exception as e:
            print(f"[Generator] Gemini LLM generation failed ({e}), falling back to local synthesis.")

    # Fallback: domain-aware local synthesis
    if not answer_text:
        answer_text = _synthesize_local_answer(query, docs)

    # Package result with citations
    citations = []
    for doc in docs:
        citations.append({
            "id": doc.metadata.get("source", "doc") + "-" + str(doc.metadata.get("chunk_index", 0)),
            "source": doc.metadata.get("source", "Unknown"),
            "title": doc.metadata.get("title", "Reference"),
            "score": doc.metadata.get("score", 0.0),
            "snippet": doc.page_content[:180] + "...",
        })

    return {"answer": answer_text, "citations": citations}


def _synthesize_local_answer(query: str, docs: List[Document]) -> str:
    """Local synthesis engine for when no LLM API key is available."""
    if not docs:
        return "I searched the India Drone Intelligence Knowledge Base, but could not find specific matches. Please rephrase or try another query."

    lines = [
        f"### Drone Intelligence Response: {query.strip('?').title()}\n",
        "Based on the **DGCA Drone Rules & Indian Drone Ecosystem Knowledge Base**, here are the details:\n",
    ]
    for i, doc in enumerate(docs, 1):
        title = doc.metadata.get("title", f"Document {i}")
        source = doc.metadata.get("source", "Knowledge Base")
        lines.append(f"#### {i}. {title}")
        lines.append(f"{doc.page_content.strip()}\n")
        lines.append(f"*Source: [{source}]*\n")

    lines.append("\n---\n**Compliance Notes:**")
    lines.append("- Ensure all flights adhere to **Drone Rules 2021** (amended 2023).")
    lines.append("- Check airspace zone on the **DigitalSky Portal** before taking off.")
    lines.append("- Commercial micro/small drone operations require a **Remote Pilot Certificate (RPC)**.")

    return "\n".join(lines)
