from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.reminder import ReminderCreate, ReminderResponse, ReminderUpdate
from app.services.reminder_service import ReminderService


router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])


@router.post("/", response_model=ReminderResponse)
def create_reminder(
    data: ReminderCreate,
    db: Session = Depends(get_db),
):
    service = ReminderService(db)
    reminder = service.create(data)
    return ReminderResponse.from_orm(reminder)


@router.get("/", response_model=List[ReminderResponse])
def list_reminders(
    user_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    scheduled_after: Optional[datetime] = Query(None),
    scheduled_before: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    service = ReminderService(db)
    reminders = service.list(
        user_id=user_id,
        status=status,
        scheduled_after=scheduled_after,
        scheduled_before=scheduled_before,
    )
    return [ReminderResponse.from_orm(r) for r in reminders]


@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    service = ReminderService(db)
    reminder = service.get(reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return ReminderResponse.from_orm(reminder)


@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(reminder_id: int, data: ReminderUpdate, db: Session = Depends(get_db)):
    service = ReminderService(db)
    reminder = service.update(reminder_id, data)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return ReminderResponse.from_orm(reminder)


@router.post("/{reminder_id}/cancel", response_model=ReminderResponse)
def cancel_reminder(reminder_id: int, db: Session = Depends(get_db)):
    service = ReminderService(db)
    reminder = service.cancel(reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return ReminderResponse.from_orm(reminder)


@router.post("/{reminder_id}/mark-sent", response_model=ReminderResponse)
def mark_sent(reminder_id: int, db: Session = Depends(get_db)):
    service = ReminderService(db)
    reminder = service.mark_sent(reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return ReminderResponse.from_orm(reminder)


