"""
Onboarding and user journey models
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class UserOnboarding(Base):
    """Track user onboarding progress"""
    __tablename__ = "user_onboarding"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Onboarding steps completion
    workspace_setup_completed = Column(Boolean, default=False)
    calendar_connected = Column(Boolean, default=False)
    team_members_added = Column(Boolean, default=False)
    project_data_imported = Column(Boolean, default=False)
    first_retrospective_scheduled = Column(Boolean, default=False)
    check_ins_configured = Column(Boolean, default=False)
    onboarding_completed = Column(Boolean, default=False)
    
    # Additional data
    onboarding_data = Column(JSON, nullable=True)  # Store additional onboarding information
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="onboarding")
    
    def __repr__(self):
        return f"<UserOnboarding(user_id={self.user_id}, completed={self.onboarding_completed})>"


class ScheduledRetrospective(Base):
    """Scheduled retrospectives with automated reminders"""
    __tablename__ = "scheduled_retrospectives"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Schedule details
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    
    # Workspace and creator
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status
    status = Column(String, default="scheduled")  # scheduled, in_progress, completed, cancelled
    
    # Related retrospective (when started)
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=True)
    
    # Reminder configuration
    send_1_week_reminder = Column(Boolean, default=True)
    send_24_hour_reminder = Column(Boolean, default=True)
    send_1_hour_reminder = Column(Boolean, default=False)
    
    # Reminder status
    week_reminder_sent = Column(Boolean, default=False)
    day_reminder_sent = Column(Boolean, default=False)
    hour_reminder_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workspace = relationship("Workspace")
    creator = relationship("User")
    retrospective = relationship("Retrospective")
    
    def __repr__(self):
        return f"<ScheduledRetrospective(id={self.id}, title='{self.title}', status='{self.status}')>"


class TeamPreparation(Base):
    """Team member preparation responses for upcoming retrospectives"""
    __tablename__ = "team_preparations"
    
    id = Column(Integer, primary_key=True, index=True)
    scheduled_retro_id = Column(Integer, ForeignKey("scheduled_retrospectives.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Preparation questions and responses
    questions = Column(JSON, nullable=True)  # List of preparation questions
    responses = Column(JSON, nullable=True)  # User's responses
    
    # Status
    completed = Column(Boolean, default=False)
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    scheduled_retrospective = relationship("ScheduledRetrospective")
    user = relationship("User")
    
    def __repr__(self):
        return f"<TeamPreparation(id={self.id}, user_id={self.user_id}, completed={self.completed})>"


class AutomatedReminder(Base):
    """Automated reminders and follow-ups"""
    __tablename__ = "automated_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Type of reminder
    reminder_type = Column(String, nullable=False)  # pre_retro, post_retro, action_item, weekly_report, monthly_report
    
    # Target
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheduled_retro_id = Column(Integer, ForeignKey("scheduled_retrospectives.id"), nullable=True)
    action_item_id = Column(Integer, ForeignKey("action_items.id"), nullable=True)
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=True)
    
    # Schedule
    scheduled_for = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String, default="pending")  # pending, sent, failed, cancelled
    
    # Content
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    reminder_data = Column(JSON, nullable=True)  # Additional data (renamed from metadata to avoid SQLAlchemy reserved word)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<AutomatedReminder(id={self.id}, type='{self.reminder_type}', status='{self.status}')>"

