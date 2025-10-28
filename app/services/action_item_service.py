"""
Action item service for managing action items
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from app.models.action_item import ActionItem
from app.schemas.action_item import ActionItemCreate, ActionItemUpdate


class ActionItemService:
    """Service for action item management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_action_item(self, action_item_data: ActionItemCreate, user_id: int) -> ActionItem:
        """Create a new action item"""
        action_item = ActionItem(
            title=action_item_data.title,
            description=action_item_data.description,
            priority=action_item_data.priority,
            due_date=action_item_data.due_date,
            assigned_to=action_item_data.assigned_to,
            created_by=user_id,
            retrospective_id=action_item_data.retrospective_id
        )
        self.db.add(action_item)
        self.db.commit()
        self.db.refresh(action_item)
        return action_item
    
    def get_action_items(
        self, 
        user_id: int, 
        skip: int = 0,
        limit: int = 100,
        retrospective_id: Optional[int] = None,
        team_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[ActionItem]:
        """Get action items with optional filters"""
        query = self.db.query(ActionItem).filter(
            or_(
                ActionItem.assigned_to == user_id,
                ActionItem.created_by == user_id
            )
        )
        
        if retrospective_id:
            query = query.filter(ActionItem.retrospective_id == retrospective_id)
        
        if team_id:
            query = query.filter(ActionItem.team_id == team_id)
        
        if status:
            # Filter by status string directly
            query = query.filter(ActionItem.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def get_action_item(self, action_item_id: int, user_id: int) -> Optional[ActionItem]:
        """Get a specific action item if user has access"""
        return self.db.query(ActionItem).filter(
            and_(
                ActionItem.id == action_item_id,
                or_(
                    ActionItem.assigned_to == user_id,
                    ActionItem.created_by == user_id
                )
            )
        ).first()
    
    def update_action_item(self, action_item_id: int, action_item_data: ActionItemUpdate, user_id: int) -> Optional[ActionItem]:
        """Update an action item"""
        action_item = self.get_action_item(action_item_id, user_id)
        if not action_item:
            return None
        
        # Update fields
        if action_item_data.title is not None:
            action_item.title = action_item_data.title
        if action_item_data.description is not None:
            action_item.description = action_item_data.description
        if action_item_data.priority is not None:
            action_item.priority = action_item_data.priority
        if action_item_data.status is not None:
            action_item.status = action_item_data.status
            if action_item_data.status == "completed":
                action_item.completed_at = datetime.utcnow()
        if action_item_data.assigned_to is not None:
            action_item.assigned_to = action_item_data.assigned_to
        if action_item_data.due_date is not None:
            action_item.due_date = action_item_data.due_date
        
        self.db.commit()
        self.db.refresh(action_item)
        return action_item
    
    def delete_action_item(self, action_item_id: int, user_id: int) -> bool:
        """Delete an action item (only if user is creator)"""
        action_item = self.db.query(ActionItem).filter(
            and_(
                ActionItem.id == action_item_id,
                ActionItem.created_by == user_id
            )
        ).first()
        
        if not action_item:
            return False
        
        self.db.delete(action_item)
        self.db.commit()
        return True
    
    def complete_action_item(self, action_item_id: int, user_id: int) -> bool:
        """Mark an action item as completed"""
        action_item = self.get_action_item(action_item_id, user_id)
        if not action_item:
            return False
        
        action_item.status = "completed"
        action_item.completed_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    def get_overdue_action_items(self, user_id: int) -> List[ActionItem]:
        """Get overdue action items for a user"""
        now = datetime.utcnow()
        return self.db.query(ActionItem).filter(
            and_(
                or_(
                    ActionItem.assigned_to == user_id,
                    ActionItem.created_by == user_id
                ),
                ActionItem.status != "completed",
                ActionItem.due_date < now
            )
        ).all()
    
    def get_action_items_by_team(self, team_id: int, user_id: int) -> List[ActionItem]:
        """Get action items for a specific team"""
        return self.db.query(ActionItem).filter(
            and_(
                ActionItem.team_id == team_id,
                or_(
                    ActionItem.assigned_to == user_id,
                    ActionItem.created_by == user_id
                )
            )
        ).all()
    
    def get_action_items_by_retrospective(self, retrospective_id: int, user_id: int) -> List[ActionItem]:
        """Get action items for a specific retrospective"""
        return self.db.query(ActionItem).filter(
            and_(
                ActionItem.retrospective_id == retrospective_id,
                or_(
                    ActionItem.assigned_to == user_id,
                    ActionItem.created_by == user_id
                )
            )
        ).all()
