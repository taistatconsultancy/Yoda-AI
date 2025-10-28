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
    priority: Literal["low", "medium", "high"] = "medium"
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
    priority: Optional[Literal["low", "medium", "high"]] = None
    status: Optional[Literal["pending", "in_progress", "completed", "cancelled"]] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None


class ActionItemResponse(ActionItemBase):
    """Schema for action item response"""
    id: int
    status: str  # "pending", "in_progress", "completed", "cancelled"
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
