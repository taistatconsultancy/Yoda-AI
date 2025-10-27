"""
Onboarding API routes
Implements Brian's user journey
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.onboarding_service import OnboardingService
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, Dict

router = APIRouter()


class OnboardingStepRequest(BaseModel):
    """Request to complete/skip an onboarding step"""
    step_name: str
    skip: Optional[bool] = False


class OnboardingResponse(BaseModel):
    """Onboarding status response"""
    user_id: int
    progress_percentage: int
    is_complete: bool
    next_step: Dict
    steps: Dict


@router.post("/start", response_model=Dict)
async def start_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start onboarding for a new user
    This is called automatically after signup
    """
    onboarding = OnboardingService.create_onboarding(db, current_user.id)
    progress = OnboardingService.get_onboarding_progress(onboarding)
    
    return {
        "message": "Welcome to YodaAI! Let's get you started.",
        "onboarding": progress
    }


@router.get("/status", response_model=OnboardingResponse)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current onboarding status"""
    onboarding = OnboardingService.get_onboarding(db, current_user.id)
    
    if not onboarding:
        # Create if doesn't exist
        onboarding = OnboardingService.create_onboarding(db, current_user.id)
    
    progress = OnboardingService.get_onboarding_progress(onboarding)
    
    return OnboardingResponse(
        user_id=current_user.id,
        progress_percentage=progress["progress_percentage"],
        is_complete=progress["is_complete"],
        next_step=progress["next_step"],
        steps=progress["steps"]
    )


@router.post("/complete-step", response_model=Dict)
async def complete_onboarding_step(
    request: OnboardingStepRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete an onboarding step"""
    if request.skip:
        onboarding = OnboardingService.skip_optional_step(
            db, 
            current_user.id, 
            request.step_name
        )
        message = f"Skipped step: {request.step_name}"
    else:
        onboarding = OnboardingService.complete_step(
            db, 
            current_user.id, 
            request.step_name
        )
        message = f"Completed step: {request.step_name}"
    
    progress = OnboardingService.get_onboarding_progress(onboarding)
    
    return {
        "message": message,
        "progress": progress
    }


@router.get("/next-step", response_model=Dict)
async def get_next_onboarding_step(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the next onboarding step"""
    onboarding = OnboardingService.get_onboarding(db, current_user.id)
    
    if not onboarding:
        onboarding = OnboardingService.create_onboarding(db, current_user.id)
    
    next_step = OnboardingService.get_next_step(onboarding)
    
    return {
        "next_step": next_step,
        "can_skip": next_step.get("optional", False)
    }

