from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReminderBase(BaseModel):
    reminder_type: str
    user_id: int
    scheduled_retro_id: Optional[int] = None
    action_item_id: Optional[int] = None
    retrospective_id: Optional[int] = None
    scheduled_for: datetime
    subject: str
    message: str


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(BaseModel):
    status: Optional[str] = None  # pending, sent, failed, cancelled
    sent_at: Optional[datetime] = None


class ReminderResponse(ReminderBase):
    id: int
    status: str
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


