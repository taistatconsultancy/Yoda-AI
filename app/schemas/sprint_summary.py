"""
Sprint summary schemas
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class SprintSummaryBase(BaseModel):
    """Base sprint summary schema"""
    sprint_id: str
    title: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    team_size: Optional[int] = None


class SprintSummaryCreate(SprintSummaryBase):
    """Sprint summary creation schema"""
    pass


class SprintSummaryResponse(SprintSummaryBase):
    """Sprint summary response schema"""
    id: int
    uploaded_by: int
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    processing_notes: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    processed_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
