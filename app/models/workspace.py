"""
Workspace model for team organization
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class Workspace(Base):
    """Workspace model for organizing teams"""
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Owner
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Settings
    settings = Column(JSON, default={
        "allow_anonymous_responses": False,
        "require_email_verification": True,
        "auto_archive_after_days": 90,
        "max_members": 100
    })
    
    # Status
    is_active = Column(Boolean, default=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_workspaces")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    invitations = relationship("WorkspaceInvitation", back_populates="workspace", cascade="all, delete-orphan")
    retrospectives = relationship("Retrospective", back_populates="workspace", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workspace(id={self.id}, name='{self.name}')>"


class WorkspaceMember(Base):
    """Workspace membership model"""
    __tablename__ = "workspace_members"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), nullable=False, default="member")  # owner, facilitator, member, viewer
    
    # Status
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")
    
    def __repr__(self):
        return f"<WorkspaceMember(workspace_id={self.workspace_id}, user_id={self.user_id}, role='{self.role}')>"


class WorkspaceInvitation(Base):
    """Workspace invitation model"""
    __tablename__ = "workspace_invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Invitee info
    email = Column(String(255), nullable=False)
    role = Column(String(50), default="member")
    
    # Invitation details
    token = Column(String(255), nullable=False, unique=True)
    status = Column(String(20), default="pending")  # pending, accepted, declined, expired
    message = Column(Text, nullable=True)
    
    # Timestamps
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    declined_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by])
    
    def __repr__(self):
        return f"<WorkspaceInvitation(email='{self.email}', status='{self.status}')>"

