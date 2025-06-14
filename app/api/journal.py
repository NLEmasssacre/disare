from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, JournalEntry
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, timedelta

router = APIRouter()

class JournalEntryCreate(BaseModel):
    telegram_id: int
    sleep_start: Optional[datetime] = None
    sleep_end: Optional[datetime] = None
    nutrition_notes: Optional[str] = None

class JournalEntryResponse(BaseModel):
    id: int
    sleep_start: Optional[datetime]
    sleep_end: Optional[datetime]
    nutrition_notes: Optional[str]
    created_at: datetime

@router.post("/entry", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new journal entry"""
    user = db.query(User).filter(User.telegram_id == entry.telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate sleep times if provided
    if entry.sleep_start and entry.sleep_end:
        if entry.sleep_start >= entry.sleep_end:
            raise HTTPException(
                status_code=400,
                detail="Sleep start time must be before sleep end time"
            )

    # Create journal entry
    journal_entry = JournalEntry(
        user_id=user.id,
        sleep_start=entry.sleep_start,
        sleep_end=entry.sleep_end,
        nutrition_notes=entry.nutrition_notes
    )
    db.add(journal_entry)
    db.commit()
    db.refresh(journal_entry)

    return JournalEntryResponse(
        id=journal_entry.id,
        sleep_start=journal_entry.sleep_start,
        sleep_end=journal_entry.sleep_end,
        nutrition_notes=journal_entry.nutrition_notes,
        created_at=journal_entry.created_at
    )

@router.get("/entries/{telegram_id}")
async def get_journal_entries(
    telegram_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """Get user's journal entries with optional date filtering"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(JournalEntry).filter(JournalEntry.user_id == user.id)

    if start_date:
        query = query.filter(JournalEntry.created_at >= start_date)
    if end_date:
        query = query.filter(JournalEntry.created_at <= end_date)

    entries = query.order_by(JournalEntry.created_at.desc()).limit(limit).all()

    return [
        {
            "sleep_start": entry.sleep_start,
            "sleep_end": entry.sleep_end,
            "nutrition_notes": entry.nutrition_notes,
            "created_at": entry.created_at
        }
        for entry in entries
    ]

@router.get("/stats/{telegram_id}")
async def get_journal_stats(
    telegram_id: int,
    db: Session = Depends(get_db)
):
    """Get user's journal statistics"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get entries from the last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    entries = db.query(JournalEntry)\
        .filter(
            JournalEntry.user_id == user.id,
            JournalEntry.created_at >= week_ago,
            JournalEntry.sleep_start.isnot(None),
            JournalEntry.sleep_end.isnot(None)
        )\
        .all()

    if not entries:
        return {
            "average_sleep_duration": None,
            "total_entries": 0
        }

    # Calculate average sleep duration in hours
    sleep_durations = [
        (entry.sleep_end - entry.sleep_start).total_seconds() / 3600
        for entry in entries
    ]

    return {
        "average_sleep_duration": sum(sleep_durations) / len(sleep_durations),
        "total_entries": len(entries)
    } 