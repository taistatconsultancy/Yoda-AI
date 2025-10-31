"""
Action items routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.action_item import ActionItem
from app.schemas.action_item import ActionItemCreate, ActionItemResponse, ActionItemUpdate
from app.services.action_item_service import ActionItemService
from app.api.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ActionItemResponse)
async def create_action_item(
    action_item_data: ActionItemCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new action item"""
    service = ActionItemService(db)
    action_item = service.create_action_item(action_item_data, current_user.id)
    return ActionItemResponse.from_orm(action_item)


@router.get("/", response_model=List[ActionItemResponse])
async def get_action_items(
    skip: int = 0,
    limit: int = 100,
    retrospective_id: int = None,
    workspace_id: int = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get action items with optional filters"""
    service = ActionItemService(db)
    action_items = service.get_action_items(
        current_user.id, 
        skip=skip, 
        limit=limit,
        retrospective_id=retrospective_id,
        workspace_id=workspace_id,
        status=status
    )
    return [ActionItemResponse.from_orm(item) for item in action_items]


@router.get("/{action_item_id}", response_model=ActionItemResponse)
async def get_action_item(
    action_item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific action item"""
    service = ActionItemService(db)
    action_item = service.get_action_item(action_item_id, current_user.id)
    if not action_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found"
        )
    return ActionItemResponse.from_orm(action_item)


@router.put("/{action_item_id}", response_model=ActionItemResponse)
async def update_action_item(
    action_item_id: int,
    action_item_data: ActionItemUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an action item"""
    service = ActionItemService(db)
    action_item = service.update_action_item(action_item_id, action_item_data, current_user.id)
    if not action_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found"
        )
    return ActionItemResponse.from_orm(action_item)


@router.delete("/{action_item_id}")
async def delete_action_item(
    action_item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an action item"""
    service = ActionItemService(db)
    success = service.delete_action_item(action_item_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found"
        )
    return {"message": "Action item deleted successfully"}


@router.post("/{action_item_id}/complete")
async def complete_action_item(
    action_item_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark an action item as completed"""
    service = ActionItemService(db)
    success = service.complete_action_item(action_item_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action item not found"
        )
    return {"message": "Action item marked as completed"}
