"""
Automation service for retrospective workflows
Handles pre-retrospective preparation, reminders, and post-retrospective follow-ups
"""

from sqlalchemy.orm import Session
from app.models.onboarding import ScheduledRetrospective, TeamPreparation, AutomatedReminder
from app.models.retrospective_new import Retrospective
from app.models.workspace import Workspace as Team, WorkspaceMember as TeamMember
from app.models.action_item import ActionItem
from app.models.user import User
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AutomationService:
    """Service to manage automated retrospective workflows"""
    
    # ===== Pre-Retrospective Automation =====
    
    @staticmethod
    def schedule_retrospective(
        db: Session,
        title: str,
        team_id: int,
        created_by: int,
        scheduled_date: datetime,
        description: Optional[str] = None,
        duration_minutes: int = 60,
        reminder_subject: Optional[str] = None,
        reminder_message: Optional[str] = None,
    ) -> ScheduledRetrospective:
        """Schedule a new retrospective with automated reminders"""
        scheduled_retro = ScheduledRetrospective(
            title=title,
            description=description,
            scheduled_date=scheduled_date,
            duration_minutes=duration_minutes,
            team_id=team_id,
            created_by=created_by
        )
        
        db.add(scheduled_retro)
        db.commit()
        db.refresh(scheduled_retro)
        
        # Create automated reminders
        AutomationService._create_reminders(
            db, scheduled_retro,
            reminder_subject=reminder_subject,
            reminder_message=reminder_message,
        )
        
        logger.info(f"Scheduled retrospective {scheduled_retro.id} for {scheduled_date}")
        return scheduled_retro
    
    @staticmethod
    def _create_reminders(
        db: Session,
        scheduled_retro: ScheduledRetrospective,
        reminder_subject: Optional[str] = None,
        reminder_message: Optional[str] = None,
    ):
        """Create automated reminders for scheduled retrospective"""
        # Get team members
        team = db.query(Team).filter(Team.id == scheduled_retro.team_id).first()
        if not team:
            return
        
        members = db.query(TeamMember).filter(TeamMember.team_id == team.id).all()
        
        for member in members:
            # 1 week before reminder
            if scheduled_retro.send_1_week_reminder:
                week_reminder = AutomatedReminder(
                    reminder_type="pre_retro",
                    user_id=member.user_id,
                    scheduled_retro_id=scheduled_retro.id,
                    scheduled_for=scheduled_retro.scheduled_date - timedelta(days=7),
                    subject=(reminder_subject or f"Retrospective in 1 week: {scheduled_retro.title}"),
                    message=(reminder_message or AutomationService._generate_week_before_message(scheduled_retro))
                )
                db.add(week_reminder)
            
            # 24 hours before reminder
            if scheduled_retro.send_24_hour_reminder:
                day_reminder = AutomatedReminder(
                    reminder_type="pre_retro",
                    user_id=member.user_id,
                    scheduled_retro_id=scheduled_retro.id,
                    scheduled_for=scheduled_retro.scheduled_date - timedelta(hours=24),
                    subject=(reminder_subject or f"Retrospective tomorrow: {scheduled_retro.title}"),
                    message=(reminder_message or AutomationService._generate_day_before_message(scheduled_retro))
                )
                db.add(day_reminder)
        
        db.commit()
        logger.info(f"Created reminders for retrospective {scheduled_retro.id}")
    
    @staticmethod
    def send_preparation_prompts(
        db: Session,
        scheduled_retro_id: int
    ) -> List[TeamPreparation]:
        """Send personalized preparation prompts to team members"""
        scheduled_retro = db.query(ScheduledRetrospective).filter(
            ScheduledRetrospective.id == scheduled_retro_id
        ).first()
        
        if not scheduled_retro:
            return []
        
        # Get team members
        members = db.query(TeamMember).filter(
            TeamMember.team_id == scheduled_retro.team_id
        ).all()
        
        preparations = []
        questions = AutomationService._generate_preparation_questions(db, scheduled_retro)
        
        for member in members:
            prep = TeamPreparation(
                scheduled_retro_id=scheduled_retro_id,
                user_id=member.user_id,
                questions=questions
            )
            db.add(prep)
            preparations.append(prep)
        
        db.commit()
        logger.info(f"Sent preparation prompts for retrospective {scheduled_retro_id}")
        return preparations
    
    @staticmethod
    def _generate_preparation_questions(
        db: Session,
        scheduled_retro: ScheduledRetrospective
    ) -> List[Dict]:
        """Generate personalized preparation questions"""
        # Get previous retrospective data
        previous_retros = db.query(Retrospective).filter(
            Retrospective.team_id == scheduled_retro.team_id,
            Retrospective.status == "completed"
        ).order_by(Retrospective.created_at.desc()).limit(3).all()
        
        # Get pending action items
        pending_actions = db.query(ActionItem).filter(
            ActionItem.team_id == scheduled_retro.team_id,
            ActionItem.status != "completed"
        ).all()
        
        questions = [
            {
                "id": "liked",
                "question": "What went well since our last retrospective?",
                "category": "4ls_liked"
            },
            {
                "id": "learned",
                "question": "What have you learned recently?",
                "category": "4ls_learned"
            },
            {
                "id": "lacked",
                "question": "What challenges have you faced?",
                "category": "4ls_lacked"
            },
            {
                "id": "longed_for",
                "question": "What would you like to see improved?",
                "category": "4ls_longed_for"
            }
        ]
        
        # Add question about pending action items if any
        if pending_actions:
            questions.append({
                "id": "action_items",
                "question": f"We have {len(pending_actions)} pending action items. Any updates or blockers?",
                "category": "action_items_status"
            })
        
        return questions
    
    @staticmethod
    def _generate_week_before_message(scheduled_retro: ScheduledRetrospective) -> str:
        """Generate 1-week before reminder message"""
        return f"""Hi there!

This is a friendly reminder that we have a retrospective coming up in one week:

**{scheduled_retro.title}**
Date: {scheduled_retro.scheduled_date.strftime('%B %d, %Y at %I:%M %p')}
Duration: {scheduled_retro.duration_minutes} minutes

To help make this retrospective productive, please take a few moments to think about:
- What has gone well since our last retrospective
- What you've learned recently
- Any challenges or blockers you've encountered
- What you'd like to see improved

YodaAI will guide us through a structured 4Ls retrospective. See you there!

Best regards,
YodaAI Team
"""
    
    @staticmethod
    def _generate_day_before_message(scheduled_retro: ScheduledRetrospective) -> str:
        """Generate 24-hour before reminder message"""
        return f"""Hi there!

Quick reminder - our retrospective is tomorrow:

**{scheduled_retro.title}**
Date: {scheduled_retro.scheduled_date.strftime('%B %d, %Y at %I:%M %p')}

Please make sure you've completed your preparation questions (if sent) and are ready to participate.

Looking forward to a productive session!

Best regards,
YodaAI Team
"""
    
    # ===== During Retrospective Automation =====
    
    @staticmethod
    def start_retrospective(
        db: Session,
        scheduled_retro_id: int
    ) -> Retrospective:
        """Start a scheduled retrospective"""
        scheduled_retro = db.query(ScheduledRetrospective).filter(
            ScheduledRetrospective.id == scheduled_retro_id
        ).first()
        
        if not scheduled_retro:
            raise ValueError(f"Scheduled retrospective {scheduled_retro_id} not found")
        
        # Create actual retrospective
        retrospective = Retrospective(
            title=scheduled_retro.title,
            description=scheduled_retro.description,
            team_id=scheduled_retro.team_id,
            created_by=scheduled_retro.created_by,
            status="active"
        )
        
        db.add(retrospective)
        db.commit()
        db.refresh(retrospective)
        
        # Update scheduled retrospective
        scheduled_retro.status = "in_progress"
        scheduled_retro.retrospective_id = retrospective.id
        db.commit()
        
        logger.info(f"Started retrospective {retrospective.id} from scheduled retro {scheduled_retro_id}")
        return retrospective
    
    # ===== Post-Retrospective Automation =====
    
    @staticmethod
    def complete_retrospective(
        db: Session,
        retrospective_id: int
    ) -> Dict:
        """Complete retrospective and trigger post-retro automation"""
        retrospective = db.query(Retrospective).filter(
            Retrospective.id == retrospective_id
        ).first()
        
        if not retrospective:
            raise ValueError(f"Retrospective {retrospective_id} not found")
        
        # Mark as completed
        retrospective.status = "completed"
        retrospective.completed_at = datetime.now()
        db.commit()
        
        # Generate and send summary
        summary = AutomationService._generate_retrospective_summary(db, retrospective)
        
        # Create action items from insights
        action_items = AutomationService._create_action_items_from_retrospective(db, retrospective)
        
        # Schedule follow-up reminders
        AutomationService._schedule_follow_up_reminders(db, retrospective)
        
        logger.info(f"Completed retrospective {retrospective_id}")
        
        return {
            "retrospective_id": retrospective_id,
            "summary": summary,
            "action_items_created": len(action_items),
            "completed_at": retrospective.completed_at
        }
    
    @staticmethod
    def _generate_retrospective_summary(
        db: Session,
        retrospective: Retrospective
    ) -> Dict:
        """Generate comprehensive retrospective summary"""
        # Get all responses
        from app.models.retrospective_new import RetrospectiveResponse
        
        responses = db.query(RetrospectiveResponse).filter(
            RetrospectiveResponse.retrospective_id == retrospective.id
        ).all()
        
        summary = {
            "retrospective_id": retrospective.id,
            "title": retrospective.title,
            "date": retrospective.created_at,
            "participants": len(responses),
            "key_themes": {
                "liked": [],
                "learned": [],
                "lacked": [],
                "longed_for": []
            }
        }
        
        # Aggregate responses
        for response in responses:
            if response.liked:
                summary["key_themes"]["liked"].append(response.liked)
            if response.learned:
                summary["key_themes"]["learned"].append(response.learned)
            if response.lacked:
                summary["key_themes"]["lacked"].append(response.lacked)
            if response.longed_for:
                summary["key_themes"]["longed_for"].append(response.longed_for)
        
        return summary
    
    @staticmethod
    def _create_action_items_from_retrospective(
        db: Session,
        retrospective: Retrospective
    ) -> List[ActionItem]:
        """Create action items based on retrospective insights"""
        # This would use AI to analyze responses and suggest action items
        # For now, return empty list (to be implemented with AI service)
        return []
    
    @staticmethod
    def _schedule_follow_up_reminders(
        db: Session,
        retrospective: Retrospective
    ):
        """Schedule follow-up reminders for action items"""
        # Get team members
        if not retrospective.team_id:
            return
        
        members = db.query(TeamMember).filter(TeamMember.team_id == retrospective.team_id).all()
        
        for member in members:
            # Weekly check-in reminder
            weekly_reminder = AutomatedReminder(
                reminder_type="weekly_report",
                user_id=member.user_id,
                retrospective_id=retrospective.id,
                scheduled_for=datetime.now() + timedelta(days=7),
                subject="Weekly Action Items Check-in",
                message=AutomationService._generate_weekly_checkin_message(retrospective)
            )
            db.add(weekly_reminder)
        
        db.commit()
        logger.info(f"Scheduled follow-up reminders for retrospective {retrospective.id}")
    
    @staticmethod
    def _generate_weekly_checkin_message(retrospective: Retrospective) -> str:
        """Generate weekly check-in message"""
        return f"""Hi there!

It's been a week since our retrospective: **{retrospective.title}**

How are the action items progressing? Please take a moment to update their status in YodaAI.

If you're facing any blockers, don't hesitate to reach out to your team!

Best regards,
YodaAI Team
"""
    
    # ===== Ongoing Support =====
    
    @staticmethod
    def generate_monthly_report(
        db: Session,
        team_id: int,
        user_id: int
    ) -> Dict:
        """Generate monthly retrospective effectiveness report"""
        # Get retrospectives from the last month
        one_month_ago = datetime.now() - timedelta(days=30)
        
        retrospectives = db.query(Retrospective).filter(
            Retrospective.team_id == str(team_id),
            Retrospective.created_at >= one_month_ago,
            Retrospective.status == "completed"
        ).all()
        
        # Get action items
        action_items = db.query(ActionItem).filter(
            ActionItem.team_id == team_id,
            ActionItem.created_at >= one_month_ago
        ).all()
        
        completed_actions = [ai for ai in action_items if ai.status.value == "completed"]
        
        report = {
            "period": "Last 30 days",
            "team_id": team_id,
            "retrospectives_conducted": len(retrospectives),
            "action_items_created": len(action_items),
            "action_items_completed": len(completed_actions),
            "completion_rate": (len(completed_actions) / len(action_items) * 100) if action_items else 0,
            "trends": [],
            "recommendations": []
        }
        
        return report

