"""
Action item models for tracking retrospective outcomes
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum


class PriorityLevel(enum.Enum):
    """Priority levels for action items"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActionItemStatus(enum.Enum):
    """Status of action items"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActionItem(Base):
    """Action item model"""
    __tablename__ = "action_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Priority and status
    priority = Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    status = Column(Enum(ActionItemStatus), default=ActionItemStatus.PENDING)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Related entities
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    
    # Due dates
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # AI-generated metadata
    ai_generated = Column(Boolean, default=False)
    ai_confidence = Column(Integer, nullable=True)  # 0-100 confidence score
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    retrospective = relationship("Retrospective", back_populates="action_items")
    team = relationship("Team", back_populates="action_items")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_action_items")
    creator = relationship("User", foreign_keys=[assigned_by], back_populates="created_action_items")
    
    def __repr__(self):
        return f"<ActionItem(id={self.id}, title='{self.title}', status='{self.status.value}')>"
