"""
Retrospective schemas
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RetrospectiveBase(BaseModel):
    """Base retrospective schema"""
    title: str
    description: Optional[str] = None
    sprint_id: Optional[str] = None
    team_id: Optional[str] = None


class RetrospectiveCreate(RetrospectiveBase):
    """Retrospective creation schema"""
    pass


class RetrospectiveResponse(RetrospectiveBase):
    """Retrospective response schema"""
    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RetrospectiveResponseBase(BaseModel):
    """Base 4Ls response schema"""
    liked: Optional[str] = None
    learned: Optional[str] = None
    lacked: Optional[str] = None
    longed_for: Optional[str] = None


class RetrospectiveResponseCreate(RetrospectiveResponseBase):
    """4Ls response creation schema"""
    pass


class RetrospectiveResponseResponse(RetrospectiveResponseBase):
    """4Ls response response schema"""
    id: int
    retrospective_id: int
    user_id: int
    sentiment_score: Optional[int] = None
    sentiment_label: Optional[str] = None
    ai_summary: Optional[str] = None
    follow_up_questions: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
