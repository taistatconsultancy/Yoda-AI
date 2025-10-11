"""
Retrospective and 4Ls response models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class Retrospective(Base):
    """Retrospective session model"""
    __tablename__ = "retrospectives"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    sprint_id = Column(String, nullable=True)  # Reference to sprint
    team_id = Column(String, nullable=True)    # Reference to team
    
    # Session status
    status = Column(String, default="active")  # active, completed, archived
    
    # User who created the retrospective
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    responses = relationship("RetrospectiveResponse", back_populates="retrospective")
    creator = relationship("User", back_populates="retrospectives")
    
    def __repr__(self):
        return f"<Retrospective(id={self.id}, title='{self.title}', status='{self.status}')>"


class RetrospectiveResponse(Base):
    """Individual 4Ls response model"""
    __tablename__ = "retrospective_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 4Ls categories
    liked = Column(Text, nullable=True)
    learned = Column(Text, nullable=True)
    lacked = Column(Text, nullable=True)
    longed_for = Column(Text, nullable=True)
    
    # AI-generated metadata
    sentiment_score = Column(Integer, nullable=True)  # -1 to 1
    sentiment_label = Column(String, nullable=True)   # positive, negative, neutral
    ai_summary = Column(Text, nullable=True)
    follow_up_questions = Column(JSON, nullable=True)  # List of generated questions
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    retrospective = relationship("Retrospective", back_populates="responses")
    user = relationship("User", back_populates="responses")
    
    def __repr__(self):
        return f"<RetrospectiveResponse(id={self.id}, retrospective_id={self.retrospective_id}, user_id={self.user_id})>"
