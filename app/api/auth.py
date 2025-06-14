from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from pydantic import BaseModel
from typing import Optional
import hashlib
import hmac
import time

router = APIRouter()

class TelegramAuth(BaseModel):
    id: int
    first_name: str
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str

def verify_telegram_auth(auth_data: TelegramAuth, bot_token: str) -> bool:
    """Verify Telegram authentication data"""
    data_check_string = "\n".join([
        f"auth_date={auth_data.auth_date}",
        f"first_name={auth_data.first_name}",
        f"id={auth_data.id}",
        f"photo_url={auth_data.photo_url}" if auth_data.photo_url else "",
        f"username={auth_data.username}" if auth_data.username else ""
    ])
    
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    # Check if hash is valid and auth_date is not too old (within 24 hours)
    return (hash == auth_data.hash and 
            time.time() - auth_data.auth_date < 86400)

@router.post("/telegram")
async def telegram_auth(
    auth_data: TelegramAuth,
    db: Session = Depends(get_db)
):
    """Handle Telegram authentication"""
    # In production, get this from environment variables
    bot_token = "YOUR_BOT_TOKEN"
    
    if not verify_telegram_auth(auth_data, bot_token):
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    # Check if user exists
    user = db.query(User).filter(User.telegram_id == auth_data.id).first()
    
    if not user:
        # Create new user
        user = User(
            telegram_id=auth_data.id,
            username=auth_data.username
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return {
        "user_id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username
    }

@router.post("/phone")
async def add_phone(
    telegram_id: int,
    phone_number: str,
    db: Session = Depends(get_db)
):
    """Add phone number to user profile"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.phone_number = phone_number
    db.commit()
    db.refresh(user)
    
    return {"message": "Phone number added successfully"} 