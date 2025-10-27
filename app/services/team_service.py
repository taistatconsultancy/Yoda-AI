"""
Team service for managing teams and team members
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.workspace import Workspace as Team, WorkspaceMember as TeamMember
from app.schemas.team import TeamCreate, TeamUpdate, TeamMemberCreate


class TeamService:
    """Service for team management"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_team(self, team_data: TeamCreate, user_id: int) -> Team:
        """Create a new team"""
        team = Team(
            name=team_data.name,
            description=team_data.description,
            settings=team_data.settings,
            created_by=user_id
        )
        self.db.add(team)
        self.db.commit()
        self.db.refresh(team)
        
        # Add creator as team member
        self.add_team_member(team.id, TeamMemberCreate(user_id=user_id, role="scrum-master"), user_id)
        
        return team
    
    def get_user_teams(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Team]:
        """Get teams where user is a member"""
        return self.db.query(Team).join(TeamMember).filter(
            and_(
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        ).offset(skip).limit(limit).all()
    
    def get_team(self, team_id: int, user_id: int) -> Optional[Team]:
        """Get a specific team if user is a member"""
        return self.db.query(Team).join(TeamMember).filter(
            and_(
                Team.id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        ).first()
    
    def update_team(self, team_id: int, team_data: TeamUpdate, user_id: int) -> Optional[Team]:
        """Update a team (only if user is creator or has admin role)"""
        team = self.get_team(team_id, user_id)
        if not team:
            return None
        
        # Check if user is creator or has admin role
        member = self.db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        ).first()
        
        if not member or (team.created_by != user_id and member.role not in ["scrum-master", "product-owner"]):
            return None
        
        # Update team
        if team_data.name is not None:
            team.name = team_data.name
        if team_data.description is not None:
            team.description = team_data.description
        if team_data.settings is not None:
            team.settings = team_data.settings
        
        self.db.commit()
        self.db.refresh(team)
        return team
    
    def delete_team(self, team_id: int, user_id: int) -> bool:
        """Delete a team (only if user is creator)"""
        team = self.db.query(Team).filter(
            and_(
                Team.id == team_id,
                Team.created_by == user_id
            )
        ).first()
        
        if not team:
            return False
        
        # Deactivate all team members
        self.db.query(TeamMember).filter(TeamMember.team_id == team_id).update(
            {"is_active": False}
        )
        
        self.db.delete(team)
        self.db.commit()
        return True
    
    def add_team_member(self, team_id: int, member_data: TeamMemberCreate, user_id: int) -> Optional[TeamMember]:
        """Add a member to a team"""
        # Check if user has permission to add members
        team = self.get_team(team_id, user_id)
        if not team:
            return None
        
        # Check if user is creator or has admin role
        member = self.db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        ).first()
        
        if not member or (team.created_by != user_id and member.role not in ["scrum-master", "product-owner"]):
            return None
        
        # Check if user is already a member
        existing_member = self.db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == member_data.user_id,
                TeamMember.is_active == True
            )
        ).first()
        
        if existing_member:
            return existing_member
        
        # Add new member
        new_member = TeamMember(
            team_id=team_id,
            user_id=member_data.user_id,
            role=member_data.role,
            permissions=member_data.permissions
        )
        self.db.add(new_member)
        self.db.commit()
        self.db.refresh(new_member)
        return new_member
    
    def remove_team_member(self, team_id: int, member_id: int, user_id: int) -> bool:
        """Remove a member from a team"""
        # Check if user has permission to remove members
        team = self.get_team(team_id, user_id)
        if not team:
            return False
        
        # Check if user is creator or has admin role
        member = self.db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.is_active == True
            )
        ).first()
        
        if not member or (team.created_by != user_id and member.role not in ["scrum-master", "product-owner"]):
            return False
        
        # Remove member
        target_member = self.db.query(TeamMember).filter(
            and_(
                TeamMember.id == member_id,
                TeamMember.team_id == team_id
            )
        ).first()
        
        if not target_member:
            return False
        
        target_member.is_active = False
        self.db.commit()
        return True
