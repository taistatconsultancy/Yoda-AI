"""
AI chat schemas
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatMessageBase(BaseModel):
    """Base chat message schema"""
    content: str
    message_type: str  # 'user', 'ai', 'system'


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message"""
    session_id: int
    context: Optional[dict] = None


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message response"""
    id: int
    session_id: int
    ai_model: Optional[str]
    ai_confidence: Optional[int]
    ai_metadata: Optional[dict]
    context: Optional[dict]
    follow_up_questions: Optional[List[str]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    """Base chat session schema"""
    session_type: str  # 'retrospective', 'general', 'action_planning'
    current_step: Optional[str] = None
    context: Optional[dict] = None


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating a chat session"""
    retrospective_id: Optional[int] = None


class ChatSessionResponse(ChatSessionBase):
    """Schema for chat session response"""
    id: int
    session_id: str
    retrospective_id: Optional[int]
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    ended_at: Optional[datetime]
    messages: List[ChatMessageResponse] = []
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str
    session_id: Optional[str] = None
    context: Optional[dict] = None
