"""
Retrospective service for 4Ls management
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.retrospective_new import Retrospective, RetrospectiveResponse
from app.schemas.retrospective import RetrospectiveCreate, RetrospectiveResponseCreate


class RetrospectiveService:
    """Retrospective service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_retrospective(self, retrospective_data: RetrospectiveCreate, created_by: int) -> Retrospective:
        """Create a new retrospective"""
        db_retrospective = Retrospective(
            title=retrospective_data.title,
            description=retrospective_data.description,
            sprint_id=retrospective_data.sprint_id,
            team_id=retrospective_data.team_id,
            created_by=created_by
        )
        self.db.add(db_retrospective)
        self.db.commit()
        self.db.refresh(db_retrospective)
        return db_retrospective
    
    def get_retrospective(self, retrospective_id: int, user_id: int) -> Optional[Retrospective]:
        """Get a specific retrospective"""
        return self.db.query(Retrospective).filter(
            Retrospective.id == retrospective_id,
            Retrospective.created_by == user_id
        ).first()
    
    def get_user_retrospectives(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Retrospective]:
        """Get user's retrospectives"""
        return self.db.query(Retrospective).filter(
            Retrospective.created_by == user_id
        ).offset(skip).limit(limit).all()
    
    def create_response(self, retrospective_id: int, response_data: RetrospectiveResponseCreate, user_id: int) -> RetrospectiveResponse:
        """Create a 4Ls response"""
        # Check if user already has a response for this retrospective
        existing_response = self.db.query(RetrospectiveResponse).filter(
            RetrospectiveResponse.retrospective_id == retrospective_id,
            RetrospectiveResponse.user_id == user_id
        ).first()
        
        if existing_response:
            # Update existing response
            existing_response.liked = response_data.liked
            existing_response.learned = response_data.learned
            existing_response.lacked = response_data.lacked
            existing_response.longed_for = response_data.longed_for
            self.db.commit()
            self.db.refresh(existing_response)
            return existing_response
        else:
            # Create new response
            db_response = RetrospectiveResponse(
                retrospective_id=retrospective_id,
                user_id=user_id,
                liked=response_data.liked,
                learned=response_data.learned,
                lacked=response_data.lacked,
                longed_for=response_data.longed_for
            )
            self.db.add(db_response)
            self.db.commit()
            self.db.refresh(db_response)
            return db_response
    
    def get_retrospective_responses(self, retrospective_id: int) -> List[RetrospectiveResponse]:
        """Get all responses for a retrospective"""
        return self.db.query(RetrospectiveResponse).filter(
            RetrospectiveResponse.retrospective_id == retrospective_id
        ).all()
    
    def complete_retrospective(self, retrospective_id: int, user_id: int) -> Optional[Retrospective]:
        """Mark retrospective as completed"""
        retrospective = self.get_retrospective(retrospective_id, user_id)
        if retrospective:
            retrospective.status = "completed"
            self.db.commit()
            self.db.refresh(retrospective)
        return retrospective
