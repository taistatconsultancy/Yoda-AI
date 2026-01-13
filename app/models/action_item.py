"""
Action item models for tracking retrospective outcomes
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class ActionItem(Base):
    """Action item model"""
    __tablename__ = "action_items"
    
    id = Column(Integer, primary_key=True, index=True)
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True, index=True)
    discussion_topic_id = Column(Integer, ForeignKey("discussion_topics.id"), nullable=True)
    
    # Action item details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Assignment
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Priority and status
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    status = Column(String(20), default="pending", index=True)  # pending, in_progress, completed, cancelled, blocked
    
    # Dates
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # AI-generated metadata
    ai_generated = Column(Boolean, default=False)
    ai_confidence = Column(Numeric(3, 2), nullable=True)  # 0.0 to 1.0
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    retrospective = relationship("Retrospective", back_populates="action_items")
    workspace = relationship("Workspace")
    discussion_topic = relationship("DiscussionTopic", back_populates="action_items")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_action_items")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_action_items")
    
    def __repr__(self):
        return f"<ActionItem(id={self.id}, title='{self.title}', status='{self.status}')>"
