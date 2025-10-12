"""
Action item schemas
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.action_item import PriorityLevel, ActionItemStatus


class ActionItemBase(BaseModel):
    """Base action item schema"""
    title: str
    description: Optional[str] = None
    priority: PriorityLevel = PriorityLevel.MEDIUM
    due_date: Optional[datetime] = None


class ActionItemCreate(ActionItemBase):
    """Schema for creating an action item"""
    assigned_to: Optional[int] = None
    retrospective_id: Optional[int] = None
    team_id: Optional[int] = None


class ActionItemUpdate(BaseModel):
    """Schema for updating an action item"""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[ActionItemStatus] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class ActionItemResponse(ActionItemBase):
    """Schema for action item response"""
    id: int
    status: ActionItemStatus
    assigned_to: Optional[int]
    assigned_by: int
    retrospective_id: Optional[int]
    team_id: Optional[int]
    ai_generated: bool
    ai_confidence: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
