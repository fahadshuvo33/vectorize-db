from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("/", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    """Basic chat endpoint - placeholder for now"""
    if not chat_message.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    return ChatResponse(
        response=f"Echo: {chat_message.message} (Chat functionality to be implemented)",
        session_id=chat_message.session_id or "default-session"
    )


@router.get("/sessions")
async def list_sessions():
    """List chat sessions - placeholder for now"""
    return {
        "message": "List sessions - to be implemented",
        "sessions": []
    }

