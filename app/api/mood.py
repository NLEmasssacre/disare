from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, MoodEntry
from app.services.ai import ai_service
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter()

class MoodEntryCreate(BaseModel):
    telegram_id: int
    mood_level: int  # 1-5 scale
    comment: Optional[str] = None

class MoodEntryResponse(BaseModel):
    id: int
    mood_level: int
    comment: Optional[str]
    sentiment_score: Optional[float]
    sentiment_text: Optional[str]
    created_at: datetime

@router.post("/track", response_model=MoodEntryResponse)
async def track_mood(
    mood_entry: MoodEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new mood entry with optional sentiment analysis"""
    user = db.query(User).filter(User.telegram_id == mood_entry.telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate mood level
    if not 1 <= mood_entry.mood_level <= 5:
        raise HTTPException(status_code=400, detail="Mood level must be between 1 and 5")

    # Analyze sentiment if comment is provided
    sentiment_score = None
    sentiment_text = None
    if mood_entry.comment:
        sentiment_score = await ai_service.analyze_sentiment(mood_entry.comment)
        sentiment_text = ai_service.interpret_sentiment_score(sentiment_score)

    # Create mood entry
    entry = MoodEntry(
        user_id=user.id,
        mood_level=mood_entry.mood_level,
        comment=mood_entry.comment,
        sentiment_score=sentiment_score
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return MoodEntryResponse(
        id=entry.id,
        mood_level=entry.mood_level,
        comment=entry.comment,
        sentiment_score=entry.sentiment_score,
        sentiment_text=sentiment_text,
        created_at=entry.created_at
    )

@router.get("/history/{telegram_id}")
async def get_mood_history(
    telegram_id: int,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """Get user's mood history"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = db.query(MoodEntry)\
        .filter(MoodEntry.user_id == user.id)\
        .order_by(MoodEntry.created_at.desc())\
        .limit(limit)\
        .all()

    return [
        {
            "mood_level": entry.mood_level,
            "comment": entry.comment,
            "sentiment_score": entry.sentiment_score,
            "sentiment_text": ai_service.interpret_sentiment_score(entry.sentiment_score) if entry.sentiment_score is not None else None,
            "created_at": entry.created_at
        }
        for entry in history
    ]

@router.get("/stats/{telegram_id}")
async def get_mood_stats(
    telegram_id: int,
    db: Session = Depends(get_db)
):
    """Get user's mood statistics"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get entries from the last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    entries = db.query(MoodEntry)\
        .filter(
            MoodEntry.user_id == user.id,
            MoodEntry.created_at >= week_ago
        )\
        .all()

    if not entries:
        return {
            "average_mood": None,
            "average_sentiment": None,
            "sentiment_distribution": None,
            "total_entries": 0
        }

    # Calculate statistics
    mood_scores = [e.mood_level for e in entries]
    sentiment_scores = [e.sentiment_score for e in entries if e.sentiment_score is not None]
    
    # Calculate sentiment distribution
    sentiment_distribution = {
        "very_positive": 0,
        "positive": 0,
        "neutral": 0,
        "negative": 0,
        "very_negative": 0
    }
    
    for score in sentiment_scores:
        if score > 0.5:
            sentiment_distribution["very_positive"] += 1
        elif score > 0.1:
            sentiment_distribution["positive"] += 1
        elif score > -0.1:
            sentiment_distribution["neutral"] += 1
        elif score > -0.5:
            sentiment_distribution["negative"] += 1
        else:
            sentiment_distribution["very_negative"] += 1

    return {
        "average_mood": sum(mood_scores) / len(mood_scores),
        "average_sentiment": sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else None,
        "sentiment_distribution": sentiment_distribution,
        "total_entries": len(entries)
    } 