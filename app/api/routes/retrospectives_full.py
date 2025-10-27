"""
Complete Retrospective Management Routes
Handles all 6 phases of retrospective
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.database.database import get_db
from app.models.retrospective_new import (
    Retrospective, RetrospectiveParticipant, ChatSession, ChatMessage,
    RetrospectiveResponse, ThemeGroup, VotingSession, VoteAllocation,
    DiscussionTopic, DiscussionMessage
)
from app.models.workspace import Workspace, WorkspaceMember
from app.models.user import User
from app.models.action_item import ActionItem
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/retrospectives", tags=["retrospectives"])


# Pydantic Models
class RetrospectiveCreate(BaseModel):
    workspace_id: int
    title: str
    description: str = None
    sprint_name: str = None
    scheduled_start_time: datetime
    scheduled_end_time: datetime


class RetrospectiveResponse(BaseModel):
    id: int
    workspace_id: int
    title: str
    description: str = None
    sprint_name: str = None
    facilitator_id: int
    scheduled_start_time: datetime = None
    scheduled_end_time: datetime = None
    status: str
    current_phase: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ParticipantResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    joined_at: datetime = None
    completed_input: bool = False
    completed_voting: bool = False
    
    class Config:
        from_attributes = True


# ============================================================================
# RETROSPECTIVE CREATION & SCHEDULING
# ============================================================================

@router.post("/", response_model=RetrospectiveResponse)
async def create_retrospective(
    retro_data: RetrospectiveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create and schedule a new retrospective
    """
    try:
        # Verify user is member of workspace
        membership = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == retro_data.workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.is_active == True
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="You are not a member of this workspace")
        
        # Check if user is facilitator or owner
        if membership.role not in ['owner', 'facilitator']:
            raise HTTPException(status_code=403, detail="Only facilitators and owners can create retrospectives")
        
        # Create retrospective
        new_retro = Retrospective(
            workspace_id=retro_data.workspace_id,
            title=retro_data.title,
            description=retro_data.description,
            sprint_name=retro_data.sprint_name,
            facilitator_id=current_user.id,
            scheduled_start_time=retro_data.scheduled_start_time,
            scheduled_end_time=retro_data.scheduled_end_time,
            status='scheduled',
            current_phase='input'
        )
        db.add(new_retro)
        db.flush()
        
        # Add all workspace members as participants
        members = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == retro_data.workspace_id,
            WorkspaceMember.is_active == True
        ).all()
        
        for member in members:
            participant = RetrospectiveParticipant(
                retrospective_id=new_retro.id,
                user_id=member.user_id
            )
            db.add(participant)
        
        db.commit()
        db.refresh(new_retro)
        
        # TODO: Send email notifications to all participants
        
        return RetrospectiveResponse(
            id=new_retro.id,
            workspace_id=new_retro.workspace_id,
            title=new_retro.title,
            description=new_retro.description,
            sprint_name=new_retro.sprint_name,
            facilitator_id=new_retro.facilitator_id,
            scheduled_start_time=new_retro.scheduled_start_time,
            scheduled_end_time=new_retro.scheduled_end_time,
            status=new_retro.status,
            current_phase=new_retro.current_phase,
            created_at=new_retro.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Create retrospective error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create retrospective: {str(e)}")


@router.get("/workspace/{workspace_id}", response_model=List[RetrospectiveResponse])
async def get_workspace_retrospectives(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all retrospectives for a workspace
    """
    try:
        # Verify membership
        membership = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.is_active == True
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="You are not a member of this workspace")
        
        # Get retrospectives
        retrospectives = db.query(Retrospective).filter(
            Retrospective.workspace_id == workspace_id
        ).order_by(Retrospective.created_at.desc()).all()
        
        return [RetrospectiveResponse(
            id=r.id,
            workspace_id=r.workspace_id,
            title=r.title,
            description=r.description,
            sprint_name=r.sprint_name,
            facilitator_id=r.facilitator_id,
            scheduled_start_time=r.scheduled_start_time,
            scheduled_end_time=r.scheduled_end_time,
            status=r.status,
            current_phase=r.current_phase,
            created_at=r.created_at
        ) for r in retrospectives]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get retrospectives error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch retrospectives: {str(e)}")


@router.get("/{retro_id}", response_model=RetrospectiveResponse)
async def get_retrospective(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific retrospective details
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        # Verify user is participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="You are not a participant in this retrospective")
        
        return RetrospectiveResponse(
            id=retro.id,
            workspace_id=retro.workspace_id,
            title=retro.title,
            description=retro.description,
            sprint_name=retro.sprint_name,
            facilitator_id=retro.facilitator_id,
            scheduled_start_time=retro.scheduled_start_time,
            scheduled_end_time=retro.scheduled_end_time,
            status=retro.status,
            current_phase=retro.current_phase,
            created_at=retro.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get retrospective error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch retrospective: {str(e)}")


@router.get("/{retro_id}/participants", response_model=List[ParticipantResponse])
async def get_participants(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all participants of a retrospective
    """
    try:
        # Verify user is participant
        is_participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not is_participant:
            raise HTTPException(status_code=403, detail="You are not a participant in this retrospective")
        
        # Get all participants
        participants = db.query(RetrospectiveParticipant, User).join(
            User, RetrospectiveParticipant.user_id == User.id
        ).filter(
            RetrospectiveParticipant.retrospective_id == retro_id
        ).all()
        
        result = []
        for participant, user in participants:
            result.append(ParticipantResponse(
                id=participant.id,
                user_id=participant.user_id,
                full_name=user.full_name,
                email=user.email,
                joined_at=participant.joined_at,
                completed_input=participant.completed_input,
                completed_voting=participant.completed_voting
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get participants error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch participants: {str(e)}")


@router.post("/{retro_id}/start")
async def start_retrospective(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a scheduled retrospective (facilitator only)
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        if retro.facilitator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the facilitator can start the retrospective")
        
        if retro.status != 'scheduled':
            raise HTTPException(status_code=400, detail=f"Retrospective is already {retro.status}")
        
        retro.status = 'in_progress'
        retro.actual_start_time = datetime.utcnow()
        retro.current_phase = 'input'
        
        db.commit()
        
        return {"message": "Retrospective started successfully", "status": "in_progress", "phase": "input"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Start retrospective error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start retrospective: {str(e)}")


@router.post("/{retro_id}/advance-phase")
async def advance_phase(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Advance to next phase (facilitator only)
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        if retro.facilitator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the facilitator can advance phases")
        
        phase_order = ['input', 'grouping', 'voting', 'discussion', 'summary', 'completed']
        current_index = phase_order.index(retro.current_phase)
        
        if current_index >= len(phase_order) - 1:
            raise HTTPException(status_code=400, detail="Already at final phase")
        
        next_phase = phase_order[current_index + 1]
        retro.current_phase = next_phase
        
        if next_phase == 'completed':
            retro.status = 'completed'
            retro.actual_end_time = datetime.utcnow()
        
        db.commit()
        
        return {"message": f"Advanced to {next_phase} phase", "phase": next_phase}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Advance phase error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to advance phase: {str(e)}")

