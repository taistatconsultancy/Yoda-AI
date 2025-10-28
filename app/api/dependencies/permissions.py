"""
Permission and access control dependencies for FastAPI routes
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.api.dependencies.auth import get_current_user


# Define role hierarchy for permission checking
ROLE_HIERARCHY = {
    'owner': 4,
    'facilitator': 3,
    'member': 2,
    'viewer': 1
}


def has_role_or_above(user_role: str, required_role: str) -> bool:
    """
    Check if user's role has sufficient permissions.
    Returns True if user_role has equal or higher permissions than required_role.
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 0)
    return user_level >= required_level


def get_workspace_membership(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> WorkspaceMember:
    """
    Dependency to get user's membership in a workspace.
    Raises 403 if user is not a member, or 404 if workspace doesn't exist.
    """
    # Check if workspace exists
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Check membership
    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id,
        WorkspaceMember.is_active == True
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace"
        )
    
    return membership


def require_workspace_role(
    workspace_id: int,
    required_role: str = "member",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> WorkspaceMember:
    """
    Dependency to require a specific role in a workspace.
    Checks membership and role permissions.
    """
    membership = get_workspace_membership(workspace_id, current_user, db)
    
    # Check role permissions
    if not has_role_or_above(membership.role, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This action requires {required_role} role or higher. Your role: {membership.role}"
        )
    
    return membership


def require_workspace_owner(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> WorkspaceMember:
    """Dependency to require owner role in a workspace."""
    return require_workspace_role(workspace_id, "owner", current_user, db)


def require_workspace_facilitator(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> WorkspaceMember:
    """Dependency to require facilitator role or higher in a workspace."""
    return require_workspace_role(workspace_id, "facilitator", current_user, db)


def require_workspace_member(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> WorkspaceMember:
    """Dependency to require member role or higher in a workspace."""
    return require_workspace_role(workspace_id, "member", current_user, db)
