"""
User model for authentication and user management
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    
    # Email verification
    email_verified = Column(Boolean, default=False, index=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # OAuth
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    profile_picture_url = Column(String, nullable=True)
    
    # User preferences
    default_role = Column(String(20), default="member")  # facilitator, member, admin
    timezone = Column(String(50), default="UTC")
    notification_preferences = Column(JSON, default={"email": True, "in_app": True})
    
    # User profile information
    country_name = Column(String(100), nullable=True)
    company_name = Column(String(255), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    verification_tokens = relationship("EmailVerificationToken", back_populates="user", cascade="all, delete-orphan")
    created_workspaces = relationship("Workspace", foreign_keys="Workspace.created_by", back_populates="creator")
    workspace_memberships = relationship("WorkspaceMember", back_populates="user", cascade="all, delete-orphan")
    sent_invitations = relationship("WorkspaceInvitation", back_populates="inviter", cascade="all, delete-orphan")
    facilitated_retrospectives = relationship("Retrospective", foreign_keys="Retrospective.facilitator_id", back_populates="facilitator")
    retrospective_participations = relationship("RetrospectiveParticipant", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    retrospective_responses = relationship("RetrospectiveResponse", back_populates="user")
    vote_allocations = relationship("VoteAllocation", back_populates="user")
    assigned_action_items = relationship("ActionItem", foreign_keys="ActionItem.assigned_to", back_populates="assignee")
    created_action_items = relationship("ActionItem", foreign_keys="ActionItem.created_by", back_populates="creator")
    onboarding = relationship("UserOnboarding", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
