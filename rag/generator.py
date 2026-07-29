"""
RAG response generator using LangChain + Google Gemini LLM.
Retrieves top relevant chunks, sends to LLM, and explicitly includes document sources in responses.
"""
import os
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document

SYSTEM_PROMPT = """You are India's premier Drone Intelligence System AI assistant.
Your goal is to provide accurate, authoritative, and structured technical and regulatory answers regarding drones in India.

Rules:
1. Base your answer strictly on the provided Retrieved Context chunks.
2. Always explicitly cite the source document name for every fact or rule (e.g. `[Source: dgca_regulations_handbook.md]` or `[Source: drone_models.json]`).
3. Structure your response cleanly using GitHub-style markdown (headings, bold text, bullet points).
4. When MCP Tool execution data is provided, incorporate the exact calculated numbers and metrics into your answer.
"""


def generate_response(
    query: str,
    docs: List[Document],
    tool_name: Optional[str] = None,
    tool_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generates a RAG response from retrieved top chunks and optional MCP tool output.
    Explicitly includes source document citations in both the LLM answer and response metadata.
    """
    # Format context from retrieved top document chunks
    context_blocks = []
    for idx, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Document.md")
        title = doc.metadata.get("title", "Reference")
        score = doc.metadata.get("score", 0.0)
        context_blocks.append(
            f"[Chunk {idx}] Document: '{source}' | Title: '{title}' | Score: {score}\n{doc.page_content}"
        )
    context = "\n---\n".join(context_blocks) if context_blocks else "No relevant vector context retrieved."

    tool_info = ""
    if tool_name and tool_result:
        tool_info = f"\n\nMCP Tool Executed: '{tool_name}'\nMCP Tool Output:\n{tool_result}\n"

    # Try LLM generation via Gemini
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
                ("human", "Retrieved Context Chunks:\n{context}{tool_info}\n\nUser Question: {query}\n\nPlease answer the user question based on the retrieved context chunks above, and cite the source document names."),
            ])
            chain = prompt | llm
            response = chain.invoke({"context": context, "tool_info": tool_info, "query": query})
            answer_text = response.content
        except Exception as e:
            print(f"[Generator] Gemini LLM generation notice ({e}), using domain synthesis engine.")

    # Fallback: domain-aware synthesis with explicit document sources
    if not answer_text:
        answer_text = _synthesize_local_answer(query, docs, tool_name, tool_result)

    # Ensure source document section is appended if not already present
    if docs and "📄 **Source Documents:**" not in answer_text and "Retrieved Regulatory" not in answer_text:
        unique_sources = {}
        for d in docs:
            src = d.metadata.get("source", "Unknown")
            title = d.metadata.get("title", "Reference Document")
            if src not in unique_sources:
                unique_sources[src] = title
        
        sources_summary = "\n\n---\n**📄 Source Documents:**\n"
        for src, title in unique_sources.items():
            sources_summary += f"- 📄 **{title}** (`{src}`)\n"
        answer_text += sources_summary

    # Package result with structured citations list
    citations = []
    for doc in docs:
        citations.append({
            "id": str(doc.metadata.get("source", "doc")) + "-" + str(doc.metadata.get("chunk_index", 0)),
            "source": doc.metadata.get("source", "Unknown"),
            "title": doc.metadata.get("title", "Reference"),
            "score": doc.metadata.get("score", 0.0),
            "snippet": doc.page_content[:180] + "...",
        })

    return {"answer": answer_text, "citations": citations}


def _synthesize_local_answer(
    query: str,
    docs: List[Document],
    tool_name: Optional[str] = None,
    tool_result: Optional[Dict[str, Any]] = None,
) -> str:
    """Local synthesis engine featuring explicit source document attribution."""
    lines = [f"### Drone Intelligence Response: {query.strip('?').title()}\n"]

    if tool_name == "flight_time_calculator" and tool_result:
        lines.append(f"Ran the **MCP Flight Time Calculator** tool:\n")
        lines.append(f"- **Estimated Flight Duration:** `{tool_result.get('flight_time_mins')}` minutes")
        lines.append(f"- **Max Operational Range:** `{tool_result.get('max_range_km')}` km")
        lines.append(f"- **Battery Drawdown:** `{tool_result.get('battery_consumed_pct')}%`")
        lines.append(f"\n> **Safety Advisory:** {tool_result.get('advice')}\n")

    elif tool_name == "roi_calculator" and tool_result:
        lines.append(f"Executed the **MCP ROI Calculator** tool:\n")
        lines.append(f"- **Estimated Monthly Revenue:** ₹{tool_result.get('monthly_revenue', 0):,}")
        lines.append(f"- **Net Monthly Profit:** ₹{tool_result.get('net_monthly_profit', 0):,}")
        lines.append(f"- **Payback Period:** {tool_result.get('payback_months')} months")
        lines.append(f"- **3-Year Operational ROI:** {tool_result.get('roi_3yr_pct')}%\n")

    elif tool_name == "compliance_checker" and tool_result:
        lines.append(f"Evaluated DGCA Compliance using **MCP Compliance Checker**:\n")
        lines.append(f"- **Status:** `{tool_result.get('status')}` ({tool_result.get('zone')})")
        lines.append(f"- **Required Permits:** {', '.join(tool_result.get('permits', [])) or 'None'}")
        lines.append(f"- **Penalties:** {tool_result.get('penalties')}\n")

    elif tool_name == "drone_recommender" and tool_result:
        count = len(tool_result) if isinstance(tool_result, list) else 0
        lines.append(f"Matched **{count} DGCA-certified drone models** via **MCP Drone Recommender**:\n")
        if isinstance(tool_result, list) and tool_result:
            top = tool_result[0]
            lines.append(f"Top Recommendation: **{top.get('model_name')}** by {top.get('manufacturer')}")
            lines.append(f"- Price: ₹{top.get('price_lakhs')} Lakhs | Flight Time: {top.get('flight_time')} mins | Payload: {top.get('payload')} kg")
            lines.append(f"- Match Score: {top.get('match_score')}%")

    if docs:
        lines.append("\n---\n#### 📄 Retrieved Context Chunks & Document Sources:\n")
        for i, doc in enumerate(docs, 1):
            title = doc.metadata.get("title", f"Document {i}")
            source = doc.metadata.get("source", "Knowledge Base")
            lines.append(f"**{i}. {title}** *(Source Document: `{source}`)*")
            lines.append(f"{doc.page_content.strip()}\n")

    return "\n".join(lines)
