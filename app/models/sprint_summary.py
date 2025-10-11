"""
Sprint summary and upload models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.database import Base


class SprintSummary(Base):
    """Sprint summary model for uploaded sprint data"""
    __tablename__ = "sprint_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    sprint_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Sprint metadata
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    team_size = Column(Integer, nullable=True)
    
    # Uploaded data
    raw_data = Column(JSON, nullable=True)  # Original uploaded data
    processed_data = Column(JSON, nullable=True)  # Processed/structured data
    
    # Upload information
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Processing status
    status = Column(String, default="uploaded")  # uploaded, processing, processed, error
    processing_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    uploader = relationship("User", back_populates="sprint_summaries")
    
    def __repr__(self):
        return f"<SprintSummary(id={self.id}, sprint_id='{self.sprint_id}', title='{self.title}')>"
