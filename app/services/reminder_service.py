from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.onboarding import AutomatedReminder
from app.schemas.reminder import ReminderCreate, ReminderUpdate


class ReminderService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: ReminderCreate) -> AutomatedReminder:
        reminder = AutomatedReminder(
            reminder_type=data.reminder_type,
            user_id=data.user_id,
            scheduled_retro_id=data.scheduled_retro_id,
            action_item_id=data.action_item_id,
            retrospective_id=data.retrospective_id,
            scheduled_for=data.scheduled_for,
            subject=data.subject,
            message=data.message,
        )
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def list(
        self,
        *,
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        scheduled_after: Optional[datetime] = None,
        scheduled_before: Optional[datetime] = None,
    ) -> List[AutomatedReminder]:
        query = self.db.query(AutomatedReminder)
        if user_id is not None:
            query = query.filter(AutomatedReminder.user_id == user_id)
        if status is not None:
            query = query.filter(AutomatedReminder.status == status)
        if scheduled_after is not None:
            query = query.filter(AutomatedReminder.scheduled_for >= scheduled_after)
        if scheduled_before is not None:
            query = query.filter(AutomatedReminder.scheduled_for <= scheduled_before)
        return query.order_by(AutomatedReminder.scheduled_for).all()

    def get(self, reminder_id: int) -> Optional[AutomatedReminder]:
        return (
            self.db.query(AutomatedReminder)
            .filter(AutomatedReminder.id == reminder_id)
            .first()
        )

    def update(self, reminder_id: int, data: ReminderUpdate) -> Optional[AutomatedReminder]:
        reminder = self.get(reminder_id)
        if not reminder:
            return None
        if data.status is not None:
            reminder.status = data.status
        if data.sent_at is not None:
            reminder.sent_at = data.sent_at
        self.db.commit()
        self.db.refresh(reminder)
        return reminder

    def cancel(self, reminder_id: int) -> Optional[AutomatedReminder]:
        return self.update(reminder_id, ReminderUpdate(status="cancelled"))

    def mark_sent(self, reminder_id: int) -> Optional[AutomatedReminder]:
        return self.update(reminder_id, ReminderUpdate(status="sent", sent_at=datetime.utcnow()))


