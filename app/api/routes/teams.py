"""
Team management routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.workspace import Workspace as Team, WorkspaceMember as TeamMember
from app.schemas.team import TeamCreate, TeamResponse, TeamUpdate, TeamMemberCreate, TeamMemberResponse
from app.services.team_service import TeamService
from app.api.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new team"""
    service = TeamService(db)
    team = service.create_team(team_data, current_user.id)
    return TeamResponse.from_orm(team)


@router.get("/", response_model=List[TeamResponse])
async def get_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's teams"""
    service = TeamService(db)
    teams = service.get_user_teams(current_user.id, skip=skip, limit=limit)
    return [TeamResponse.from_orm(team) for team in teams]


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific team"""
    service = TeamService(db)
    team = service.get_team(team_id, current_user.id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    return TeamResponse.from_orm(team)


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a team"""
    service = TeamService(db)
    team = service.update_team(team_id, team_data, current_user.id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    return TeamResponse.from_orm(team)


@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a team"""
    service = TeamService(db)
    success = service.delete_team(team_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    return {"message": "Team deleted successfully"}


@router.post("/{team_id}/members", response_model=TeamMemberResponse)
async def add_team_member(
    team_id: int,
    member_data: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a member to a team"""
    service = TeamService(db)
    member = service.add_team_member(team_id, member_data, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found or user not authorized"
        )
    return TeamMemberResponse.from_orm(member)


@router.delete("/{team_id}/members/{member_id}")
async def remove_team_member(
    team_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove a member from a team"""
    service = TeamService(db)
    success = service.remove_team_member(team_id, member_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found or user not authorized"
        )
    return {"message": "Team member removed successfully"}
