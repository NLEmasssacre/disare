from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, ChatHistory
from app.services.ai import ai_service
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()

class ChatMessage(BaseModel):
    telegram_id: int
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime

@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_message: ChatMessage,
    db: Session = Depends(get_db)
):
    """Send a message to the AI and get a response"""
    # Verify user exists
    user = db.query(User).filter(User.telegram_id == chat_message.telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get AI response
    response = await ai_service.get_chat_response(chat_message.message)

    # Save to chat history
    chat_history = ChatHistory(
        user_id=user.id,
        message=chat_message.message,
        response=response
    )
    db.add(chat_history)
    db.commit()

    return ChatResponse(
        response=response,
        timestamp=datetime.utcnow()
    )

@router.get("/history/{telegram_id}")
async def get_chat_history(
    telegram_id: int,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """Get user's chat history"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = db.query(ChatHistory)\
        .filter(ChatHistory.user_id == user.id)\
        .order_by(ChatHistory.created_at.desc())\
        .limit(limit)\
        .all()

    return [
        {
            "message": entry.message,
            "response": entry.response,
            "timestamp": entry.created_at
        }
        for entry in reversed(history)
    ] 