"""
Retrospective models for the complete workflow
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class Retrospective(Base):
    """Retrospective session model"""
    __tablename__ = "retrospectives"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    
    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sprint_name = Column(String(100), nullable=True)
    
    # Facilitation
    facilitator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Scheduling
    scheduled_start_time = Column(DateTime(timezone=True), nullable=True, index=True)
    scheduled_end_time = Column(DateTime(timezone=True), nullable=True)
    actual_start_time = Column(DateTime(timezone=True), nullable=True)
    actual_end_time = Column(DateTime(timezone=True), nullable=True)
    
    # Status and phase
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, cancelled
    current_phase = Column(String(20), default="input", index=True)  # input, grouping, voting, discussion, summary, completed
    
    # Phase completion tracking
    phase_completion = Column(JSON, default={
        "input": False,
        "grouping": False,
        "voting": False,
        "discussion": False,
        "summary": False
    })
    
    # Settings
    settings = Column(JSON, default={
        "votes_per_member": 10,
        "min_votes_for_discussion": 3,
        "discussion_time_per_topic": 15,
        "allow_anonymous": False
    })
    
    # AI-generated content
    ai_summary = Column(Text, nullable=True)
    ai_insights = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="retrospectives")
    facilitator = relationship("User", foreign_keys=[facilitator_id], back_populates="facilitated_retrospectives")
    participants = relationship("RetrospectiveParticipant", back_populates="retrospective", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="retrospective", cascade="all, delete-orphan")
    responses = relationship("RetrospectiveResponse", back_populates="retrospective", cascade="all, delete-orphan")
    theme_groups = relationship("ThemeGroup", back_populates="retrospective", cascade="all, delete-orphan")
    voting_sessions = relationship("VotingSession", back_populates="retrospective", cascade="all, delete-orphan")
    discussion_topics = relationship("DiscussionTopic", back_populates="retrospective", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="retrospective")
    
    def __repr__(self):
        return f"<Retrospective(id={self.id}, title='{self.title}', phase='{self.current_phase}')>"


class RetrospectiveParticipant(Base):
    """Retrospective participant tracking"""
    __tablename__ = "retrospective_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Participation tracking
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    joined_at = Column(DateTime(timezone=True), nullable=True)
    completed_input = Column(Boolean, default=False)
    completed_voting = Column(Boolean, default=False)
    
    # Notification tracking
    email_notification_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    
    # Relationships
    retrospective = relationship("Retrospective", back_populates="participants")
    user = relationship("User", back_populates="retrospective_participations")
    
    def __repr__(self):
        return f"<RetrospectiveParticipant(retro_id={self.retrospective_id}, user_id={self.user_id})>"


class ChatSession(Base):
    """Chat session for 4Ls input phase"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session info
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    session_type = Column(String(50), default="4ls_input")
    
    # Progress tracking
    current_category = Column(String(20), default="liked")  # liked, learned, lacked, longed_for
    categories_completed = Column(JSON, default={
        "liked": False,
        "learned": False,
        "lacked": False,
        "longed_for": False
    })
    
    # Session status
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    retrospective = relationship("Retrospective", back_populates="chat_sessions")
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    responses = relationship("RetrospectiveResponse", back_populates="chat_session")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}', category='{self.current_category}')>"


class ChatMessage(Base):
    """Chat messages"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    
    # AI metadata
    ai_model = Column(String(50), nullable=True)
    ai_tokens_used = Column(Integer, nullable=True)
    
    # Context
    current_category = Column(String(20), nullable=True)
    message_metadata = Column('metadata', JSON, nullable=True)  # Maps to 'metadata' column in DB
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, type='{self.message_type}')>"


class RetrospectiveResponse(Base):
    """User responses extracted from chat"""
    __tablename__ = "retrospective_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)
    
    # Response content
    category = Column(String(20), nullable=False, index=True)  # liked, learned, lacked, longed_for
    content = Column(Text, nullable=False)
    
    # AI analysis
    sentiment_score = Column(Numeric(3, 2), nullable=True)  # -1.0 to 1.0
    keywords = Column(JSON, nullable=True)
    
    # Grouping (populated during grouping phase)
    theme_group_id = Column(Integer, ForeignKey("theme_groups.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    retrospective = relationship("Retrospective", back_populates="responses")
    user = relationship("User", back_populates="retrospective_responses")
    chat_session = relationship("ChatSession", back_populates="responses")
    theme_group = relationship("ThemeGroup", back_populates="responses")
    
    def __repr__(self):
        return f"<RetrospectiveResponse(id={self.id}, category='{self.category}')>"


class ThemeGroup(Base):
    """AI-generated theme groups"""
    __tablename__ = "theme_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=False)
    
    # Group info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # AI-generated
    ai_generated = Column(Boolean, default=True)
    ai_confidence = Column(Numeric(3, 2), nullable=True)  # 0.0 to 1.0
    
    # Categorization
    primary_category = Column(String(20), nullable=True)  # liked, learned, lacked, longed_for
    
    # Display
    display_order = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    retrospective = relationship("Retrospective", back_populates="theme_groups")
    responses = relationship("RetrospectiveResponse", back_populates="theme_group")
    vote_allocations = relationship("VoteAllocation", back_populates="theme_group")
    discussion_topics = relationship("DiscussionTopic", back_populates="theme_group")
    
    def __repr__(self):
        return f"<ThemeGroup(id={self.id}, title='{self.title}')>"


class VotingSession(Base):
    """Voting session"""
    __tablename__ = "voting_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=False)
    
    # Configuration
    votes_per_member = Column(Integer, default=10)
    min_votes_to_discuss = Column(Integer, default=3)
    
    # Status
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    retrospective = relationship("Retrospective", back_populates="voting_sessions")
    vote_allocations = relationship("VoteAllocation", back_populates="voting_session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VotingSession(id={self.id}, retro_id={self.retrospective_id})>"


class VoteAllocation(Base):
    """Individual vote allocations"""
    __tablename__ = "vote_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    voting_session_id = Column(Integer, ForeignKey("voting_sessions.id"), nullable=False)
    theme_group_id = Column(Integer, ForeignKey("theme_groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Vote details
    votes_allocated = Column(Integer, nullable=False, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    voting_session = relationship("VotingSession", back_populates="vote_allocations")
    theme_group = relationship("ThemeGroup", back_populates="vote_allocations")
    user = relationship("User", back_populates="vote_allocations")
    
    def __repr__(self):
        return f"<VoteAllocation(theme_id={self.theme_group_id}, user_id={self.user_id}, votes={self.votes_allocated})>"


class DiscussionTopic(Base):
    """Discussion topics (top voted themes)"""
    __tablename__ = "discussion_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    retrospective_id = Column(Integer, ForeignKey("retrospectives.id"), nullable=False)
    theme_group_id = Column(Integer, ForeignKey("theme_groups.id"), nullable=False)
    
    # Topic metadata
    total_votes = Column(Integer, default=0)
    rank = Column(Integer, nullable=True, index=True)
    
    # Discussion tracking
    time_allocated_minutes = Column(Integer, default=15)
    discussion_started_at = Column(DateTime(timezone=True), nullable=True)
    discussion_ended_at = Column(DateTime(timezone=True), nullable=True)
    is_discussed = Column(Boolean, default=False)
    
    # AI facilitation
    ai_summary = Column(Text, nullable=True)
    key_points = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    retrospective = relationship("Retrospective", back_populates="discussion_topics")
    theme_group = relationship("ThemeGroup", back_populates="discussion_topics")
    messages = relationship("DiscussionMessage", back_populates="discussion_topic", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="discussion_topic")
    
    def __repr__(self):
        return f"<DiscussionTopic(id={self.id}, rank={self.rank}, votes={self.total_votes})>"


class DiscussionMessage(Base):
    """Discussion messages"""
    __tablename__ = "discussion_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    discussion_topic_id = Column(Integer, ForeignKey("discussion_topics.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user', 'ai_facilitator', 'system'
    
    # AI metadata
    ai_model = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    discussion_topic = relationship("DiscussionTopic", back_populates="messages")
    
    def __repr__(self):
        return f"<DiscussionMessage(id={self.id}, type='{self.message_type}')>"

