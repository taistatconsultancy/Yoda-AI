"""
Onboarding service for new users
Implements Brian's journey according to the user specification
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.models.onboarding import UserOnboarding
from datetime import datetime
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class OnboardingService:
    """Service to manage user onboarding flow"""
    
    @staticmethod
    def create_onboarding(db: Session, user_id: int) -> UserOnboarding:
        """Create onboarding record for new user"""
        onboarding = UserOnboarding(
            user_id=user_id,
            onboarding_data={"steps_completed": []}
        )
        db.add(onboarding)
        db.commit()
        db.refresh(onboarding)
        logger.info(f"Created onboarding for user {user_id}")
        return onboarding
    
    @staticmethod
    def get_onboarding(db: Session, user_id: int) -> Optional[UserOnboarding]:
        """Get user's onboarding status"""
        return db.query(UserOnboarding).filter(UserOnboarding.user_id == user_id).first()
    
    @staticmethod
    def complete_step(db: Session, user_id: int, step_name: str) -> UserOnboarding:
        """Mark an onboarding step as completed"""
        onboarding = OnboardingService.get_onboarding(db, user_id)
        
        if not onboarding:
            onboarding = OnboardingService.create_onboarding(db, user_id)
        
        # Update the specific step
        if step_name == "workspace_setup":
            onboarding.workspace_setup_completed = True
        elif step_name == "calendar_connected":
            onboarding.calendar_connected = True
        elif step_name == "team_members_added":
            onboarding.team_members_added = True
        elif step_name == "project_data_imported":
            onboarding.project_data_imported = True
        elif step_name == "first_retrospective_scheduled":
            onboarding.first_retrospective_scheduled = True
        elif step_name == "check_ins_configured":
            onboarding.check_ins_configured = True
        
        # Add to completed steps
        if onboarding.onboarding_data:
            steps = onboarding.onboarding_data.get("steps_completed", [])
            if step_name not in steps:
                steps.append(step_name)
                onboarding.onboarding_data["steps_completed"] = steps
        
        # Check if all steps are complete
        if OnboardingService.is_onboarding_complete(onboarding):
            onboarding.onboarding_completed = True
            onboarding.completed_at = datetime.now()
        
        db.commit()
        db.refresh(onboarding)
        logger.info(f"User {user_id} completed onboarding step: {step_name}")
        return onboarding
    
    @staticmethod
    def is_onboarding_complete(onboarding: UserOnboarding) -> bool:
        """Check if all essential onboarding steps are complete"""
        # Essential steps (workspace and first retro)
        essential_complete = (
            onboarding.workspace_setup_completed and 
            onboarding.first_retrospective_scheduled
        )
        return essential_complete
    
    @staticmethod
    def get_next_step(onboarding: UserOnboarding) -> Dict:
        """Get the next onboarding step for the user"""
        if not onboarding.workspace_setup_completed:
            return {
                "step": "workspace_setup",
                "title": "Set Up Your Workspace",
                "description": "Let's start by setting up your YodaAI workspace",
                "action": "Create workspace",
                "optional": False
            }
        
        if not onboarding.calendar_connected:
            return {
                "step": "calendar_connected",
                "title": "Connect Your Calendar",
                "description": "Connect your work calendar to schedule retrospectives automatically",
                "action": "Connect calendar",
                "optional": True
            }
        
        if not onboarding.team_members_added:
            return {
                "step": "team_members_added",
                "title": "Add Team Members",
                "description": "Add your team members and assign their roles",
                "action": "Add team members",
                "optional": True
            }
        
        if not onboarding.project_data_imported:
            return {
                "step": "project_data_imported",
                "title": "Import Project Data",
                "description": "Import existing project data and documents for AI analysis",
                "action": "Upload documents",
                "optional": True
            }
        
        if not onboarding.first_retrospective_scheduled:
            return {
                "step": "first_retrospective_scheduled",
                "title": "Schedule Your First Retrospective",
                "description": "Let's schedule your first AI-powered retrospective",
                "action": "Schedule retrospective",
                "optional": False
            }
        
        if not onboarding.check_ins_configured:
            return {
                "step": "check_ins_configured",
                "title": "Set Up Automated Check-ins",
                "description": "Configure automated check-ins for action item progress",
                "action": "Configure check-ins",
                "optional": True
            }
        
        return {
            "step": "complete",
            "title": "Onboarding Complete!",
            "description": "You're all set up and ready to conduct powerful retrospectives with AI",
            "action": "Get started",
            "optional": False
        }
    
    @staticmethod
    def get_onboarding_progress(onboarding: UserOnboarding) -> Dict:
        """Get onboarding progress summary"""
        total_steps = 6
        completed_steps = sum([
            onboarding.workspace_setup_completed,
            onboarding.calendar_connected,
            onboarding.team_members_added,
            onboarding.project_data_imported,
            onboarding.first_retrospective_scheduled,
            onboarding.check_ins_configured
        ])
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percentage": int((completed_steps / total_steps) * 100),
            "is_complete": onboarding.onboarding_completed,
            "next_step": OnboardingService.get_next_step(onboarding),
            "steps": {
                "workspace_setup": onboarding.workspace_setup_completed,
                "calendar_connected": onboarding.calendar_connected,
                "team_members_added": onboarding.team_members_added,
                "project_data_imported": onboarding.project_data_imported,
                "first_retrospective_scheduled": onboarding.first_retrospective_scheduled,
                "check_ins_configured": onboarding.check_ins_configured
            }
        }
    
    @staticmethod
    def skip_optional_step(db: Session, user_id: int, step_name: str) -> UserOnboarding:
        """Skip an optional onboarding step"""
        onboarding = OnboardingService.get_onboarding(db, user_id)
        
        if not onboarding:
            onboarding = OnboardingService.create_onboarding(db, user_id)
        
        # Add to skipped steps
        if onboarding.onboarding_data:
            skipped = onboarding.onboarding_data.get("steps_skipped", [])
            if step_name not in skipped:
                skipped.append(step_name)
                onboarding.onboarding_data["steps_skipped"] = skipped
        
        db.commit()
        db.refresh(onboarding)
        logger.info(f"User {user_id} skipped onboarding step: {step_name}")
        return onboarding

