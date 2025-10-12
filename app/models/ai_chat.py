"""
AI chat and conversation models for retrospective assistance
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class ChatSession(Base):
    """AI chat session model"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False)
    
    # Related entities
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session metadata
    session_type = Column(String, nullable=False)  # 'retrospective', 'general', 'action_planning'
    current_step = Column(String, nullable=True)  # 'liked', 'learned', 'lacked', 'longed_for'
    
    # Session status
    is_active = Column(Boolean, default=True)
    context = Column(JSON, nullable=True)  # Store session context and state
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    retrospective = relationship("Retrospective", back_populates="chat_sessions")
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}', type='{self.session_type}')>"


class ChatMessage(Base):
    """Individual chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String, nullable=False)  # 'user', 'ai', 'system'
    
    # AI-specific metadata
    ai_model = Column(String, nullable=True)  # Which AI model generated this
    ai_confidence = Column(Integer, nullable=True)  # 0-100 confidence score
    ai_metadata = Column(JSON, nullable=True)  # Additional AI metadata
    
    # Message context
    context = Column(JSON, nullable=True)  # Store message context
    follow_up_questions = Column(JSON, nullable=True)  # AI-generated follow-up questions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, type='{self.message_type}', session_id={self.session_id})>"
