"""
RAG response generator using LangChain + Google Gemini LLM.
Retrieves top relevant chunks, sends to LLM, and explicitly includes document sources in responses.
Includes a domain synthesis engine with direct answer extraction when offline.
"""
import os
import re
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()


def _call_groq_llm(query: str, context: str, tool_info: str, groq_key: str) -> str:
    """Invokes Groq Llama 3.3 70B directly via HTTP REST API with zero external dependencies."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {groq_key.strip()}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    user_prompt = (
        f"Retrieved Context Chunks:\n{context}{tool_info}\n\n"
        f"User Question: {query}\n\n"
        f"Please answer the user question based on the retrieved context chunks above, and cite the source document names."
    )
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3
    }
    
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers)
    
    with urllib.request.urlopen(req, timeout=15) as response:
        res_json = json.loads(response.read().decode("utf-8"))
        return res_json["choices"][0]["message"]["content"]



SYSTEM_PROMPT = """You are India's premier Drone Intelligence System AI assistant.
Your goal is to provide accurate, authoritative, and structured technical and regulatory answers regarding drones in India.

Rules:
1. Base your answer strictly on the provided Retrieved Context chunks.
2. Always explicitly cite the source document name for every fact or rule (e.g. `[Source: dgca_regulations_handbook.md]` or `[Source: drone_models.json]`).
3. Structure your response cleanly using GitHub-style markdown (headings, bold text, bullet points).
4. When MCP Tool execution data is provided, incorporate the exact calculated numbers and metrics into your answer.
"""


def _extract_key_sentence(query: str, docs: List[Document]) -> str:
    """Extracts the most relevant direct answer sentence from the top document chunk."""
    if not docs:
        return "No specific document details retrieved."
    
    top_doc = docs[0]
    content = top_doc.page_content
    
    lines = content.split("\n")
    processed_text = ""
    for line in lines:
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue
        
        # Check if the line starts with a new section number (e.g. 4.1, 5., 5.1.2)
        starts_with_section = re.match(r'^\d+(\.\d+)*\s+', line_str)
        
        if processed_text and not processed_text.endswith((".", "!", "?", ";", ":")) and not starts_with_section:
            processed_text += " " + line_str
        else:
            processed_text += "\n" + line_str if processed_text else line_str
            
    sentences = []
    for paragraph in processed_text.split("\n"):
        pts = re.split(r'(?<=[.!?])\s+', paragraph)
        for pt in pts:
            pt_str = pt.strip()
            if pt_str:
                sentences.append(pt_str)
                
    q_words = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 2]
    best_sentence = sentences[0] if sentences else content[:250]
    best_score = 0
    
    for sent in sentences:
        s_lower = sent.lower()
        score = sum(1 for w in q_words if w in s_lower)
        if score > best_score:
            best_score = score
            best_sentence = sent
            
    return best_sentence



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

    # Try LLM generation via Groq or Gemini
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    answer_text = None
    error_reason = None
    llm_provider = None

    if groq_key and groq_key.strip():
        try:
            answer_text = _call_groq_llm(query, context, tool_info, groq_key)
            llm_provider = "Groq (Llama 3.3 70B)"
        except Exception as e:
            error_reason = f"[Groq LLM Error]: {str(e)}"
            print(f"[Generator] Groq direct LLM notice ({e}), checking fallback...")

    if not answer_text and gemini_key and gemini_key.strip():
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.prompts import ChatPromptTemplate

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=gemini_key.strip(),
                temperature=0.3,
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_PROMPT),
                ("human", "Retrieved Context Chunks:\n{context}{tool_info}\n\nUser Question: {query}\n\nPlease answer the user question based on the retrieved context chunks above, and cite the source document names."),
            ])
            chain = prompt | llm
            response = chain.invoke({"context": context, "tool_info": tool_info, "query": query})
            answer_text = response.content
            llm_provider = "Google Gemini 2.5 Flash"
        except Exception as e:
            if not error_reason:
                error_reason = f"[Gemini LLM Error]: {str(e)}"
            print(f"[Generator] Gemini LLM notice ({e}), falling back to local synthesis engine...")

    # Fallback: domain-aware synthesis with explicit document sources
    if not answer_text:
        answer_text = _synthesize_local_answer(query, docs, tool_name, tool_result)
        if error_reason:
            # Check for common quota/auth patterns
            error_label = "API Key Error / Connection Issue"
            if "quota" in error_reason.lower() or "429" in error_reason.lower():
                error_label = "API Quota Limit Hit (Rate Limit / Credit Exhausted)"
            elif "key" in error_reason.lower() or "400" in error_reason.lower() or "api key not valid" in error_reason.lower():
                error_label = "Invalid Gemini API Key"
                
            warning_callout = (
                f"> [!WARNING]\n"
                f"> **LLM Assistant Error**: {error_label}\n"
                f"> *Detail: {error_reason}*\n"
                f"> *Notice: The system automatically fell back to the Local Synthesis Engine to resolve your request.*\n\n"
            )
            answer_text = warning_callout + answer_text


    # Ensure source document section is appended if not already present
    if docs and "📄 **Source Documents:**" not in answer_text:
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
    """Local synthesis engine featuring direct answer extraction and source document attribution."""
    lines = [f"### Drone Intelligence Response\n"]

    if docs:
        top_doc = docs[0]
        top_source = top_doc.metadata.get("source", "Knowledge Base")
        key_ans = _extract_key_sentence(query, docs)
        lines.append(f"**Direct Answer** *(Source: `{top_source}`)*:\n{key_ans}\n")

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
