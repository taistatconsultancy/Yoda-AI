"""
Action item schemas
"""

from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class ActionItemBase(BaseModel):
    """Base action item schema"""
    title: str
    description: Optional[str] = None
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    due_date: Optional[datetime] = None


class ActionItemCreate(ActionItemBase):
    """Schema for creating an action item"""
    assigned_to: Optional[int] = None
    retrospective_id: Optional[int] = None
    workspace_id: Optional[int] = None
    discussion_topic_id: Optional[int] = None
    progress_percentage: Optional[int] = 0


class ActionItemUpdate(BaseModel):
    """Schema for updating an action item"""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high", "critical"]] = None
    status: Optional[Literal["pending", "in_progress", "completed", "cancelled", "blocked"]] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    progress_percentage: Optional[int] = None


class ActionItemResponse(ActionItemBase):
    """Schema for action item response"""
    id: int
    status: str  # "pending", "in_progress", "completed", "cancelled", "blocked"
    assigned_to: Optional[int]
    created_by: int
    retrospective_id: Optional[int]
    workspace_id: Optional[int]
    discussion_topic_id: Optional[int] = None
    ai_generated: bool
    ai_confidence: Optional[int]
    progress_percentage: Optional[int] = 0
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
