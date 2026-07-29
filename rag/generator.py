"""
RAG response generator using LangChain + Google Gemini LLM.
Supports both standard document RAG synthesis and MCP Tool-assisted response generation.
"""
import os
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document

SYSTEM_PROMPT = """You are India's premier Drone Intelligence System AI assistant.
Your goal is to provide accurate, authoritative, and structured technical and regulatory answers regarding drones in India.

Rules:
1. When MCP Tool execution data is provided, incorporate the exact numbers and metrics into your answer.
2. Integrate retrieved knowledge context and citations seamlessly.
3. Structure your response cleanly using GitHub-style markdown (headings, bold text, bullet points, advice quotes).
4. Always include explicit source citations inline (e.g. [Source: DGCA Handbook / DigitalSky]).
"""


def generate_response(
    query: str,
    docs: List[Document],
    tool_name: Optional[str] = None,
    tool_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generates a RAG response from retrieved documents and optional MCP tool output.
    Uses Gemini LLM via LangChain when available, otherwise falls back to domain synthesis.
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
    context = "\n---\n".join(context_blocks) if context_blocks else "No additional vector context retrieved."

    tool_info = ""
    if tool_name and tool_result:
        tool_info = f"\n\nMCP Tool Executed: '{tool_name}'\nMCP Tool Output:\n{tool_result}\n"

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
                ("human", "Retrieved Context:\n{context}{tool_info}\n\nUser Question: {query}\n\nPlease answer the user question based on the tool output and context above."),
            ])
            chain = prompt | llm
            response = chain.invoke({"context": context, "tool_info": tool_info, "query": query})
            answer_text = response.content
        except Exception as e:
            print(f"[Generator] Gemini LLM generation failed ({e}), falling back to domain synthesis.")

    # Fallback: domain-aware synthesis
    if not answer_text:
        answer_text = _synthesize_local_answer(query, docs, tool_name, tool_result)

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


def _synthesize_local_answer(
    query: str,
    docs: List[Document],
    tool_name: Optional[str] = None,
    tool_result: Optional[Dict[str, Any]] = None,
) -> str:
    """Local synthesis engine for tool execution + RAG context."""
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
        lines.append("\n---\n#### Retrieved Regulatory & Ecosystem Context:\n")
        for i, doc in enumerate(docs, 1):
            title = doc.metadata.get("title", f"Document {i}")
            source = doc.metadata.get("source", "Knowledge Base")
            lines.append(f"**{i}. {title}** ({source})")
            lines.append(f"{doc.page_content.strip()}\n")

    return "\n".join(lines)
