from fastapi import APIRouter, HTTPException
from api.models.schemas import ChatRequest, ChatResponse, ChatHistoryResponse, ChatMessageItem
from api.services.rag_service import handle_chat
from api.services.history_service import (
    get_chat_history,
    clear_chat_history,
    get_all_chat_sessions,
    create_new_chat_session,
)

router = APIRouter(tags=["Chat & RAG"])

@router.get("/api/chat/sessions")
@router.get("/chat/sessions")
def get_sessions_endpoint():
    return get_all_chat_sessions()

@router.post("/api/chat/sessions")
@router.post("/chat/sessions")
def create_session_endpoint():
    return create_new_chat_session()

@router.post("/chat", response_model=ChatResponse)
@router.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    try:
        session_id = req.session_id or "default"
        return handle_chat(req.message, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/chat/history/{session_id}", response_model=ChatHistoryResponse)
@router.get("/chat/history/{session_id}", response_model=ChatHistoryResponse)
def get_history_endpoint(session_id: str):
    history = get_chat_history(session_id)
    items = [ChatMessageItem(**h) for h in history]
    return ChatHistoryResponse(session_id=session_id, messages=items)

@router.delete("/api/chat/history/{session_id}")
@router.delete("/chat/history/{session_id}")
def clear_history_endpoint(session_id: str):
    clear_chat_history(session_id)
    return {"status": "success", "message": f"Cleared history for session '{session_id}'"}
