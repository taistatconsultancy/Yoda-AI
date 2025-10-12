"""
Team and team member schemas
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class TeamMemberBase(BaseModel):
    """Base team member schema"""
    role: str
    permissions: Optional[dict] = None


class TeamMemberCreate(TeamMemberBase):
    """Schema for creating a team member"""
    user_id: int


class TeamMemberResponse(TeamMemberBase):
    """Schema for team member response"""
    id: int
    team_id: int
    user_id: int
    is_active: bool
    joined_at: datetime
    
    class Config:
        from_attributes = True


class TeamBase(BaseModel):
    """Base team schema"""
    name: str
    description: Optional[str] = None
    settings: Optional[dict] = None


class TeamCreate(TeamBase):
    """Schema for creating a team"""
    pass


class TeamResponse(TeamBase):
    """Schema for team response"""
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    members: List[TeamMemberResponse] = []
    
    class Config:
        from_attributes = True


class TeamUpdate(BaseModel):
    """Schema for updating a team"""
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[dict] = None
