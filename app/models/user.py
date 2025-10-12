"""
User model for authentication and user management
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)  # For local auth
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # External auth provider info
    provider = Column(String, nullable=True)  # 'firebase', 'auth0', 'local'
    provider_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    retrospectives = relationship("Retrospective", back_populates="creator")
    responses = relationship("RetrospectiveResponse", back_populates="user")
    sprint_summaries = relationship("SprintSummary", back_populates="uploader")
    created_teams = relationship("Team", back_populates="creator")
    team_memberships = relationship("TeamMember", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    assigned_action_items = relationship("ActionItem", foreign_keys="ActionItem.assigned_to", back_populates="assignee")
    created_action_items = relationship("ActionItem", foreign_keys="ActionItem.assigned_by", back_populates="creator")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
