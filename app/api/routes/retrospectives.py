"""
Retrospective routes for 4Ls management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.retrospective_new import Retrospective, RetrospectiveResponse
from app.schemas.retrospective import (
    RetrospectiveCreate, 
    RetrospectiveResponse as RetrospectiveResponseSchema,
    RetrospectiveResponseCreate
)
from app.services.retrospective_service import RetrospectiveService
from app.api.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=RetrospectiveResponseSchema)
async def create_retrospective(
    retrospective_data: RetrospectiveCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new retrospective session"""
    service = RetrospectiveService(db)
    retrospective = service.create_retrospective(retrospective_data, current_user.id)
    return RetrospectiveResponseSchema.from_orm(retrospective)


@router.get("/", response_model=List[RetrospectiveResponseSchema])
async def get_retrospectives(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's retrospectives"""
    service = RetrospectiveService(db)
    retrospectives = service.get_user_retrospectives(current_user.id, skip=skip, limit=limit)
    return [RetrospectiveResponseSchema.from_orm(r) for r in retrospectives]


@router.get("/{retrospective_id}", response_model=RetrospectiveResponseSchema)
async def get_retrospective(
    retrospective_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific retrospective"""
    service = RetrospectiveService(db)
    retrospective = service.get_retrospective(retrospective_id, current_user.id)
    if not retrospective:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retrospective not found"
        )
    return RetrospectiveResponseSchema.from_orm(retrospective)


@router.post("/{retrospective_id}/responses")
async def submit_4ls_response(
    retrospective_id: int,
    response_data: RetrospectiveResponseCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit 4Ls response for a retrospective"""
    service = RetrospectiveService(db)
    response = service.create_response(retrospective_id, response_data, current_user.id)
    return {"message": "Response submitted successfully", "response_id": response.id}
