"""
Retrospective scheduling and automation API routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.automation_service import AutomationService
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.models.onboarding import ScheduledRetrospective
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

router = APIRouter()


class ScheduleRetrospectiveRequest(BaseModel):
    """Request to schedule a retrospective"""
    title: str
    team_id: int
    scheduled_date: datetime
    description: Optional[str] = None
    duration_minutes: Optional[int] = 60
    send_1_week_reminder: Optional[bool] = True
    send_24_hour_reminder: Optional[bool] = True
    reminder_subject: Optional[str] = None
    reminder_message: Optional[str] = None


class PreparationQuestionResponse(BaseModel):
    """Team preparation question response"""
    scheduled_retro_id: int
    responses: dict


@router.post("/schedule", response_model=Dict)
async def schedule_retrospective(
    request: ScheduleRetrospectiveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Schedule a new retrospective with automated reminders
    This implements the pre-retrospective automation flow
    """
    try:
        scheduled_retro = AutomationService.schedule_retrospective(
            db=db,
            title=request.title,
            team_id=request.team_id,
            created_by=current_user.id,
            scheduled_date=request.scheduled_date,
            description=request.description,
            duration_minutes=request.duration_minutes,
            reminder_subject=request.reminder_subject,
            reminder_message=request.reminder_message,
        )
        
        # Update send_reminder preferences
        scheduled_retro.send_1_week_reminder = request.send_1_week_reminder
        scheduled_retro.send_24_hour_reminder = request.send_24_hour_reminder
        db.commit()
        
        return {
            "message": "Retrospective scheduled successfully",
            "scheduled_retrospective": {
                "id": scheduled_retro.id,
                "title": scheduled_retro.title,
                "scheduled_date": scheduled_retro.scheduled_date,
                "team_id": scheduled_retro.team_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{scheduled_retro_id}/send-preparation", response_model=Dict)
async def send_preparation_prompts(
    scheduled_retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send personalized preparation prompts to team members
    1 week before the retrospective
    """
    try:
        preparations = AutomationService.send_preparation_prompts(
            db, 
            scheduled_retro_id
        )
        
        return {
            "message": f"Preparation prompts sent to {len(preparations)} team members",
            "count": len(preparations)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{scheduled_retro_id}/start", response_model=Dict)
async def start_scheduled_retrospective(
    scheduled_retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a scheduled retrospective
    This transitions from scheduled to active retrospective
    """
    try:
        retrospective = AutomationService.start_retrospective(
            db, 
            scheduled_retro_id
        )
        
        return {
            "message": "Retrospective started successfully",
            "retrospective_id": retrospective.id,
            "title": retrospective.title,
            "status": retrospective.status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/retrospectives/{retrospective_id}/complete", response_model=Dict)
async def complete_retrospective(
    retrospective_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete a retrospective and trigger post-retrospective automation
    - Generates summary
    - Creates action items
    - Schedules follow-up reminders
    """
    try:
        result = AutomationService.complete_retrospective(
            db, 
            retrospective_id
        )
        
        return {
            "message": "Retrospective completed successfully",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/scheduled", response_model=List[Dict])
async def get_scheduled_retrospectives(
    team_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all scheduled retrospectives"""
    query = db.query(ScheduledRetrospective)
    
    if team_id:
        query = query.filter(ScheduledRetrospective.team_id == team_id)
    
    scheduled_retros = query.filter(
        ScheduledRetrospective.status.in_(["scheduled", "in_progress"])
    ).order_by(ScheduledRetrospective.scheduled_date).all()
    
    return [
        {
            "id": sr.id,
            "title": sr.title,
            "description": sr.description,
            "scheduled_date": sr.scheduled_date,
            "duration_minutes": sr.duration_minutes,
            "team_id": sr.team_id,
            "status": sr.status
        }
        for sr in scheduled_retros
    ]


@router.get("/team/{team_id}/monthly-report", response_model=Dict)
async def get_monthly_report(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get monthly retrospective effectiveness report
    This provides trend analysis and recommendations
    """
    try:
        report = AutomationService.generate_monthly_report(
            db, 
            team_id, 
            current_user.id
        )
        
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

