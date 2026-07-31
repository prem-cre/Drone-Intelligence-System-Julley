import os
import sqlite3
import json
import uuid
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SESSIONS_DIR = os.path.join(BASE_DIR, "data", "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)
DB_PATH = os.path.join(SESSIONS_DIR, "chat_history.db")


def init_history_db():
    """Initializes the SQLite database table for persistent conversation history."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            response_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON chat_messages(session_id)")
    conn.commit()
    conn.close()


def save_chat_message(
    session_id: str,
    role: str,
    content: str,
    msg_id: Optional[str] = None,
    response_data: Optional[Dict[str, Any]] = None,
):
    """Saves a user or assistant message to persistent SQLite storage."""
    init_history_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    unique_id = msg_id or str(uuid.uuid4())
    response_json = json.dumps(response_data) if response_data else None
    cursor.execute(
        "INSERT OR REPLACE INTO chat_messages (id, session_id, role, content, response_json) VALUES (?, ?, ?, ?, ?)",
        (unique_id, session_id, role, content, response_json)
    )
    conn.commit()
    conn.close()


def get_chat_history(session_id: str = "default") -> List[Dict[str, Any]]:
    """Retrieves chronological conversation history for a given session."""
    init_history_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, role, content, response_json, timestamp FROM chat_messages WHERE session_id = ? ORDER BY rowid ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    history = []
    for r in rows:
        history.append({
            "id": r[0],
            "role": r[1],
            "content": r[2],
            "response": json.loads(r[3]) if r[3] else None,
            "timestamp": r[4]
        })
    return history


def clear_chat_history(session_id: str = "default"):
    """Clears saved conversation history for a given session."""
    init_history_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


def get_all_chat_sessions() -> List[Dict[str, Any]]:
    """Retrieves all distinct chat session threads with titles and timestamps."""
    init_history_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT session_id, role, content, timestamp 
        FROM chat_messages 
        ORDER BY rowid ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    sessions_map: Dict[str, Dict[str, Any]] = {}
    for session_id, role, content, ts in rows:
        if session_id not in sessions_map:
            title = content[:35] + "..." if len(content) > 35 else content
            sessions_map[session_id] = {
                "session_id": session_id,
                "title": title if role == "user" else f"Chat Thread ({session_id[:6]})",
                "created_at": ts,
                "last_message": content[:50],
            }
        else:
            sessions_map[session_id]["created_at"] = ts
            sessions_map[session_id]["last_message"] = content[:50]

    return list(sessions_map.values())


def create_new_chat_session() -> Dict[str, Any]:
    """Generates a new chat session thread ID."""
    new_id = f"session-{str(uuid.uuid4())[:8]}"
    return {
        "session_id": new_id,
        "title": "New Chat",
        "created_at": None,
        "last_message": "",
    }

