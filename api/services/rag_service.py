import os
import sys
import re
from typing import Dict, Any, List, Optional, Tuple

# Ensure project root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from api.models.schemas import ChatResponse, Citation, ToolCall
from mcp_server.server import MCPServer
from rag.retriever import get_relevant_documents
from rag.generator import generate_response

# Instantiate the official MCP Server
_mcp_server = MCPServer()

# Try to import full RAG pipeline
_rag_pipeline = None
try:
    from rag.pipeline import RAGPipeline
    _rag_pipeline = RAGPipeline()
except Exception as e:
    print(f"[RAG Service] RAG pipeline initialization warning ({e}). Using direct hybrid retriever.")


def _extract_flight_params(msg: str) -> dict:
    battery_match = re.search(r'(\d+)\s*mah', msg, re.IGNORECASE)
    payload_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|l|litre|liter)', msg, re.IGNORECASE)
    wind_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kmh|km/h|knot)', msg, re.IGNORECASE)
    temp_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:c|°c|degree)', msg, re.IGNORECASE)

    return {
        "battery_mah": float(battery_match.group(1)) if battery_match else 10000.0,
        "empty_weight": 3.0,
        "payload": float(payload_match.group(1)) if payload_match else 2.0,
        "wind": float(wind_match.group(1)) if wind_match else 10.0,
        "temperature": float(temp_match.group(1)) if temp_match else 28.0,
    }


def _extract_roi_params(msg: str) -> dict:
    acres_match = re.search(r'(\d+)\s*acre', msg, re.IGNORECASE)
    fee_match = re.search(r'(?:rs\.?|₹|\bfee\b)?\s*(\d+)\s*(?:/|\bper\b)?\s*acre', msg, re.IGNORECASE)
    budget_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l)', msg, re.IGNORECASE)
    subsidy_match = re.search(r'(\d+)\s*%', msg, re.IGNORECASE)

    return {
        "sector": "Agriculture",
        "investment": float(budget_match.group(1)) * 100000.0 if budget_match else 750000.0,
        "monthly_opex": 25000.0,
        "fee_per_acre": float(fee_match.group(1)) if fee_match else 400.0,
        "monthly_acres": float(acres_match.group(1)) if acres_match else 500.0,
        "subsidy_pct": float(subsidy_match.group(1)) if subsidy_match else 50.0,
    }


def _extract_compliance_params(msg: str) -> dict:
    msg_lower = msg.lower()
    zone = "Green"
    if "yellow" in msg_lower:
        zone = "Yellow"
    elif "red" in msg_lower:
        zone = "Red"

    weight = "Micro"
    if "nano" in msg_lower:
        weight = "Nano"
    elif "small" in msg_lower:
        weight = "Small"
    elif "medium" in msg_lower:
        weight = "Medium"
    elif "large" in msg_lower:
        weight = "Large"

    altitude_match = re.search(r'(\d+)\s*(?:ft|feet|m|meter)', msg, re.IGNORECASE)
    rpc = "rpc" in msg_lower or "pilot certificate" in msg_lower or "licensed" in msg_lower

    return {
        "weight_category": weight,
        "purpose": "Commercial" if "commercial" in msg_lower else "General",
        "zone": zone,
        "altitude": float(altitude_match.group(1)) if altitude_match else 200.0,
        "rpc": rpc,
    }


def _extract_recommend_params(msg: str) -> dict:
    budget_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|l)', msg, re.IGNORECASE)
    time_match = re.search(r'(\d+)\s*(?:min|mins|minutes)', msg, re.IGNORECASE)
    payload_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|l|litre)', msg, re.IGNORECASE)

    sector = "Agriculture"
    msg_lower = msg.lower()
    if "survey" in msg_lower or "mapping" in msg_lower:
        sector = "Survey"
    elif "defense" in msg_lower or "military" in msg_lower:
        sector = "Defense"
    elif "logistics" in msg_lower or "cargo" in msg_lower:
        sector = "Logistics"

    return {
        "budget_lakhs": float(budget_match.group(1)) if budget_match else 8.0,
        "sector": sector,
        "min_flight_time": float(time_match.group(1)) if time_match else 15.0,
        "min_payload": float(payload_match.group(1)) if payload_match else 8.0,
    }


def _evaluate_tool_relevance(message: str) -> Tuple[Optional[str], float, dict]:
    """
    Evaluates query relevance for MCP tool execution.
    Only triggers MCP tool execution if relevance confidence is >= 0.95 (95%).
    Otherwise returns (None, 0.0, {}) to route to pure RAG retrieval.
    """
    lower = message.lower()

    # 1. Flight Time Calculator
    is_flight_calc = any(kw in lower for kw in (
        "calculate flight time", "flight time for", "battery mah",
        "power curve calculation", "how long can i fly"
    ))
    if is_flight_calc:
        params = _extract_flight_params(message)
        score = 0.98 if (re.search(r'\d+\s*mah', lower) or re.search(r'\d+\s*kg', lower)) else 0.96
        return ("flight_time_calculator", score, params)

    # 2. ROI Calculator
    is_roi_calc = any(kw in lower for kw in (
        "calculate roi", "check roi", "roi for", "payback period calculation",
        "roi of drone", "profit for acre"
    ))
    if is_roi_calc:
        params = _extract_roi_params(message)
        score = 0.98 if (re.search(r'\d+\s*acre', lower) or re.search(r'rs|₹|\bfee\b|\blakh\b', lower)) else 0.96
        return ("roi_calculator", score, params)

    # 3. Compliance Checker
    is_compliance_check = any(kw in lower for kw in (
        "check compliance", "verify compliance", "compliance check for",
        "can i fly in red zone", "can i fly in yellow zone", "is it legal to fly in red zone"
    ))
    if is_compliance_check:
        params = _extract_compliance_params(message)
        score = 0.97
        return ("compliance_checker", score, params)

    # 4. Drone Recommender
    is_recommend_check = any(kw in lower for kw in (
        "recommend a drone", "suggest a drone", "drone under",
        "best drone under", "recommend drone under"
    ))
    if is_recommend_check:
        params = _extract_recommend_params(message)
        score = 0.97
        return ("drone_recommender", score, params)

    # Low relevance (< 95%) -> Pure RAG Retrieval
    return (None, 0.0, {})


def handle_chat(message: str) -> Dict[str, Any]:
    """
    Evaluates query relevance:
    - If MCP Tool relevance >= 95%, calls specific MCP tool + RAG context.
    - If MCP Tool relevance < 95%, performs pure RAG document retrieval.
    """
    tool_name, relevance_score, tool_params = _evaluate_tool_relevance(message)
    print(f"[RAG Router] Query: '{message}' | Tool: '{tool_name}' | Relevance: {relevance_score * 100:.1f}%")

    tool_calls: List[ToolCall] = []
    mcp_result = None

    # Condition: Relevance >= 95% -> Execute MCP Tool
    if tool_name and relevance_score >= 0.95:
        try:
            mcp_result = _mcp_server.call_tool(tool_name, **tool_params)
            tool_calls.append(ToolCall(
                tool_name=tool_name,
                input=tool_params,
                output=mcp_result if isinstance(mcp_result, dict) else {"results": mcp_result},
            ))
            print(f"[RAG Router] Invoked MCP tool '{tool_name}' (Relevance: {relevance_score * 100:.1f}%)")
        except Exception as e:
            print(f"[RAG Router] MCP tool execution error: {e}")

    # Step 2: Retrieve document context from ChromaDB (Hybrid Vector + BM25)
    retrieved_docs = []
    if _rag_pipeline and not tool_name:
        try:
            rag_res = _rag_pipeline.query(message, top_k=4)
            citations = [
                Citation(
                    title=c.get("title", "Reference"),
                    source=c.get("source", "Unknown"),
                    score=c.get("score", 0.0),
                    snippet=c.get("snippet", ""),
                )
                for c in rag_res.get("citations", [])
            ]
            return ChatResponse(
                answer=rag_res.get("answer", "No relevant context found."),
                citations=citations,
                tool_calls=[],
            ).model_dump()
        except Exception as e:
            print(f"[RAG Router] LangGraph pipeline fallback ({e})")

    try:
        retrieved_docs = get_relevant_documents(message, top_k=4)
    except Exception as e:
        print(f"[RAG Router] Hybrid retrieval error ({e})")

    # Step 3: Synthesize final answer incorporating MCP tool output (if tool ran) or RAG context
    gen_result = generate_response(
        query=message,
        docs=retrieved_docs,
        tool_name=tool_name,
        tool_result=mcp_result if isinstance(mcp_result, dict) else ({"recommendations": mcp_result} if mcp_result else None),
    )

    citations = [
        Citation(
            title=c.get("title", "Reference"),
            source=c.get("source", "Unknown"),
            score=c.get("score", 0.0),
            snippet=c.get("snippet", ""),
        )
        for c in gen_result.get("citations", [])
    ]

    return ChatResponse(
        answer=gen_result.get("answer", "No response generated."),
        citations=citations,
        tool_calls=tool_calls,
    ).model_dump()
