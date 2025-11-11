"""
Complete Retrospective Management Routes
Handles all 6 phases of retrospective
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import secrets
import string
from pydantic import Field

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
from app.services.calendar_service import CalendarService
from app.services.email_service import EmailService
from app.core.config import settings

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
    code: str
    title: str
    description: Optional[str] = None
    sprint_name: Optional[str] = None
    facilitator_id: int
    scheduled_start_time: Optional[datetime] = None
    scheduled_end_time: Optional[datetime] = None
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
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
    joined_at: Optional[datetime] = None
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
        # Normalize timezone-aware UTC if naive
        now_utc = datetime.now(timezone.utc)
        start_time = retro_data.scheduled_start_time
        end_time = retro_data.scheduled_end_time

        # Normalize to timezone-aware UTC if naive
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time and end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        # Validate end time is after start time
        if end_time and end_time <= start_time:
            raise HTTPException(status_code=400, detail="scheduled_end_time must be after scheduled_start_time")

        # Verify user is member of workspace
        membership = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == retro_data.workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.is_active == True
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="You are not a member of this workspace")
        
        # Check if user is facilitator or owner (Scrum Master and Project Manager are facilitators)
        allowed_roles = ['owner', 'facilitator', 'Scrum Master', 'Project Manager']
        if membership.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Only facilitators and owners can create retrospectives")
        
        # Generate unique 5-character code
        def generate_code():
            """Generate a random 5-character alphanumeric code"""
            alphabet = string.ascii_uppercase + string.digits
            # Exclude similar-looking characters
            alphabet = ''.join(c for c in alphabet if c not in '0O1IL')
            while True:
                code = ''.join(secrets.choice(alphabet) for _ in range(5))
                # Check if code already exists
                existing = db.query(Retrospective).filter(Retrospective.code == code).first()
                if not existing:
                    return code
        
        retro_code = generate_code()
        
        # Create retrospective
        new_retro = Retrospective(
            workspace_id=retro_data.workspace_id,
            code=retro_code,
            title=retro_data.title,
            description=retro_data.description,
            sprint_name=retro_data.sprint_name,
            facilitator_id=current_user.id,
            created_by=current_user.id,
            scheduled_start_time=start_time,
            scheduled_end_time=end_time,
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
        
        # Generate calendar invites for all participants
        try:
            # Get workspace details
            workspace = db.query(Workspace).filter(Workspace.id == retro_data.workspace_id).first()
            
            # Generate .ics calendar file
            calendar_service = CalendarService()
            print(f"🔧 Generating calendar for retrospective: {new_retro.title}")
            print(f"   Start time: {new_retro.scheduled_start_time}")
            print(f"   End time: {new_retro.scheduled_end_time}")
            
            ics_content = calendar_service.generate_retrospective_calendar(
                retrospective_id=new_retro.id,
                title=new_retro.title,
                sprint_name=new_retro.sprint_name or "Sprint",
                start_time=new_retro.scheduled_start_time,
                end_time=new_retro.scheduled_end_time,
                workspace_name=workspace.name if workspace else "Workspace",
                facilitator_name=current_user.full_name
            )
            
            print(f"✅ Generated iCal content: {len(ics_content)} bytes")
            if b'\x00' in ics_content:
                print("⚠️ iCal content contains null bytes!")
            
            # Send calendar invites to all participants
            email_service = EmailService()
            # Send generic retrospective page link without code to avoid auto-starting sessions
            retro_link = f"{settings.APP_URL}/ui/retrospective.html"
            
            for member in members:
                user = db.query(User).filter(User.id == member.user_id).first()
                if user and user.email:
                    email_service.send_calendar_invite_email(
                        to_email=user.email,
                        full_name=user.full_name,
                        retrospective_title=new_retro.title,
                        sprint_name=new_retro.sprint_name or "Sprint",
                        start_time=new_retro.scheduled_start_time,
                        end_time=new_retro.scheduled_end_time,
                        workspace_name=workspace.name if workspace else "Workspace",
                        facilitator_name=current_user.full_name,
                        ics_content=ics_content,
                        retro_link=retro_link
                    )
        except Exception as email_error:
            # Don't fail retrospective creation if email fails
            print(f"Failed to send calendar invites: {email_error}")
        
        return RetrospectiveResponse(
            id=new_retro.id,
            workspace_id=new_retro.workspace_id,
            code=new_retro.code,
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


@router.get("/", response_model=List[RetrospectiveResponse])
async def get_retrospectives(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    workspace_id: Optional[int] = None
):
    """
    Get all retrospectives for the current user
    If workspace_id is provided, filter to that workspace
    """
    try:
        # Get workspaces the user is a member of
        user_workspaces = db.query(WorkspaceMember).filter(
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.is_active == True
        ).all()
        
        workspace_ids = [w.workspace_id for w in user_workspaces]
        
        if not workspace_ids:
            return []
        
        # Build query
        query = db.query(Retrospective).filter(
            Retrospective.workspace_id.in_(workspace_ids)
        )
        
        # Filter by workspace if specified
        if workspace_id:
            query = query.filter(Retrospective.workspace_id == workspace_id)
        
        # Get retrospectives where user is participant
        retrospectives = db.query(Retrospective).join(
            RetrospectiveParticipant,
            RetrospectiveParticipant.retrospective_id == Retrospective.id
        ).filter(
            RetrospectiveParticipant.user_id == current_user.id
        ).order_by(Retrospective.created_at.desc()).all()
        
        return [RetrospectiveResponse(
            id=r.id,
            workspace_id=r.workspace_id,
            code=r.code,
            title=r.title,
            description=r.description,
            sprint_name=r.sprint_name,
            facilitator_id=r.facilitator_id,
            scheduled_start_time=r.scheduled_start_time,
            scheduled_end_time=r.scheduled_end_time,
            actual_start_time=r.actual_start_time,
            actual_end_time=r.actual_end_time,
            status=r.status,
            current_phase=r.current_phase,
            created_at=r.created_at
        ) for r in retrospectives]
        
    except Exception as e:
        print(f"Get retrospectives error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch retrospectives: {str(e)}")


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
            code=r.code,
            title=r.title,
            description=r.description,
            sprint_name=r.sprint_name,
            facilitator_id=r.facilitator_id,
            scheduled_start_time=r.scheduled_start_time,
            scheduled_end_time=r.scheduled_end_time,
            actual_start_time=r.actual_start_time,
            actual_end_time=r.actual_end_time,
            status=r.status,
            current_phase=r.current_phase,
            created_at=r.created_at
        ) for r in retrospectives]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get retrospectives error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch retrospectives: {str(e)}")


@router.get("/code/{code}", response_model=RetrospectiveResponse)
async def get_retrospective_by_code(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get retrospective by access code
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.code == code).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        # Verify user is participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro.id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="You are not a participant in this retrospective")
        
        return RetrospectiveResponse(
            id=retro.id,
            workspace_id=retro.workspace_id,
            code=retro.code,
            title=retro.title,
            description=retro.description,
            sprint_name=retro.sprint_name,
            facilitator_id=retro.facilitator_id,
            scheduled_start_time=retro.scheduled_start_time,
            scheduled_end_time=retro.scheduled_end_time,
            actual_start_time=retro.actual_start_time,
            actual_end_time=retro.actual_end_time,
            status=retro.status,
            current_phase=retro.current_phase,
            created_at=retro.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get retrospective by code error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch retrospective: {str(e)}")


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
            code=retro.code,
            title=retro.title,
            description=retro.description,
            sprint_name=retro.sprint_name,
            facilitator_id=retro.facilitator_id,
            scheduled_start_time=retro.scheduled_start_time,
            scheduled_end_time=retro.scheduled_end_time,
            actual_start_time=retro.actual_start_time,
            actual_end_time=retro.actual_end_time,
            status=retro.status,
            current_phase=retro.current_phase,
            created_at=retro.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get retrospective error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch retrospective: {str(e)}")


@router.get("/{retro_id}/calendar")
async def download_calendar(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download .ics calendar file for retrospective
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
        
        # Get workspace and facilitator details
        workspace = db.query(Workspace).filter(Workspace.id == retro.workspace_id).first()
        facilitator = db.query(User).filter(User.id == retro.facilitator_id).first()
        
        # Generate calendar file
        calendar_service = CalendarService()
        ics_content = calendar_service.generate_retrospective_calendar(
            retrospective_id=retro.id,
            title=retro.title,
            sprint_name=retro.sprint_name or "Sprint",
            start_time=retro.scheduled_start_time,
            end_time=retro.scheduled_end_time,
            workspace_name=workspace.name if workspace else "Workspace",
            facilitator_name=facilitator.full_name if facilitator else "Facilitator"
        )
        
        # Return as downloadable file
        filename = f"retrospective_{retro.id}.ics"
        return Response(
            content=ics_content,
            media_type="text/calendar",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Download calendar error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate calendar file: {str(e)}")


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


@router.get("/{retro_id}/status")
async def get_retrospective_status(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get retrospective status with current phase and participants
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
        
        # Get all participants
        participants = db.query(RetrospectiveParticipant, User).join(
            User, RetrospectiveParticipant.user_id == User.id
        ).filter(
            RetrospectiveParticipant.retrospective_id == retro_id
        ).all()
        
        participants_list = []
        for p, user in participants:
            participants_list.append({
                "id": p.id,
                "user_id": p.user_id,
                "user_name": user.full_name,
                "full_name": user.full_name,
                "email": user.email,
                "joined_at": p.joined_at,
                "completed_input": p.completed_input,
                "completed_voting": p.completed_voting
            })
        
        return {
            "retrospective_id": retro.id,
            "current_phase": retro.current_phase,
            "status": retro.status,
            "participants": participants_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get retrospective status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch retrospective status: {str(e)}")


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
        
        # Allow starting retrospective at any time (no time constraint)
        now_utc = datetime.now(timezone.utc)
        
        retro.status = 'in_progress'
        retro.actual_start_time = now_utc
        retro.current_phase = 'input'
        
        db.commit()
        
        return {"message": "Retrospective started successfully", "status": "in_progress", "phase": "input"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Start retrospective error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start retrospective: {str(e)}")


@router.get("/user/dashboard")
async def get_user_dashboard_retrospectives(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's retrospectives grouped by status for dashboard
    Returns: upcoming (scheduled), in_progress, completed
    """
    try:
        # Get all retrospectives where user is participant
        retrospectives = db.query(Retrospective).join(
            RetrospectiveParticipant,
            RetrospectiveParticipant.retrospective_id == Retrospective.id
        ).filter(
            RetrospectiveParticipant.user_id == current_user.id
        ).order_by(Retrospective.scheduled_start_time.desc()).all()
        
        now_utc = datetime.now(timezone.utc)
        
        # Group by status
        upcoming = []
        in_progress = []
        completed = []
        
        for retro in retrospectives:
            retro_data = RetrospectiveResponse(
                id=retro.id,
                workspace_id=retro.workspace_id,
                code=retro.code,
                title=retro.title,
                description=retro.description,
                sprint_name=retro.sprint_name,
                facilitator_id=retro.facilitator_id,
                scheduled_start_time=retro.scheduled_start_time,
                scheduled_end_time=retro.scheduled_end_time,
                actual_start_time=retro.actual_start_time,
                actual_end_time=retro.actual_end_time,
                status=retro.status,
                current_phase=retro.current_phase,
                created_at=retro.created_at
            )
            
            if retro.status == 'completed':
                completed.append(retro_data)
            elif retro.status == 'in_progress':
                in_progress.append(retro_data)
            elif retro.status == 'scheduled':
                # Check if scheduled time has passed
                if retro.scheduled_start_time and retro.scheduled_start_time <= now_utc:
                    in_progress.append(retro_data)
                else:
                    upcoming.append(retro_data)
        
        return {
            "upcoming": upcoming,
            "in_progress": in_progress,
            "completed": completed
        }
        
    except Exception as e:
        print(f"Get dashboard retrospectives error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}")


@router.post("/{retro_id}/complete-chat-sessions")
async def complete_chat_sessions(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete all active chat sessions for a retrospective (facilitator only)
    Called when moving from input phase to grouping
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        if retro.facilitator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the facilitator can complete chat sessions")
        
        # Find all active chat sessions for this retrospective
        sessions = db.query(ChatSession).filter(
            ChatSession.retrospective_id == retro_id,
            ChatSession.is_completed == False
        ).all()
        
        now_utc = datetime.now(timezone.utc)
        
        # Complete all sessions
        for session in sessions:
            session.is_completed = True
            session.completed_at = now_utc
            session.is_active = False
        
        db.commit()
        
        return {"message": f"Completed {len(sessions)} chat session(s)"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Complete chat sessions error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete chat sessions: {str(e)}")


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
        now_utc = datetime.now(timezone.utc)
        
        # If leaving voting phase, ensure all participants submitted votes and update allocations
        if retro.current_phase == 'voting':
            pending_participants = db.query(RetrospectiveParticipant, User).join(
                User, RetrospectiveParticipant.user_id == User.id
            ).filter(
                RetrospectiveParticipant.retrospective_id == retro_id,
                RetrospectiveParticipant.completed_voting == False
            ).all()
            
            if pending_participants:
                waiting_on = [
                    (user.full_name or user.email or f"User {user.id}").strip()
                    for _, user in pending_participants
                ]
                names = ', '.join(waiting_on)
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot advance to discussion. Waiting for votes from: {names}"
                )
            
            # Get active voting session
            session = db.query(VotingSession).filter(
                VotingSession.retrospective_id == retro_id,
                VotingSession.is_active == True
            ).first()
            if session:
                # Update all vote allocations for this session
                allocations = db.query(VoteAllocation).filter(
                    VoteAllocation.voting_session_id == session.id
                ).all()
                for allocation in allocations:
                    allocation.updated_at = now_utc
        
        # If leaving discussion phase, mark all discussion topics as ended
        if retro.current_phase == 'discussion':
            topics = db.query(DiscussionTopic).filter(
                DiscussionTopic.retrospective_id == retro_id,
                DiscussionTopic.discussion_ended_at == None
            ).all()
            for topic in topics:
                topic.discussion_ended_at = now_utc
        
        retro.current_phase = next_phase
        
        if next_phase == 'completed':
            retro.status = 'completed'
            retro.actual_end_time = datetime.now(timezone.utc)
        
        db.commit()
        
        return {"message": f"Advanced to {next_phase} phase", "current_phase": next_phase, "phase": next_phase}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Advance phase error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to advance phase: {str(e)}")

