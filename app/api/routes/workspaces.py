"""
Workspace Management Routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets

from app.database.database import get_db
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceInvitation
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.services.email_service import EmailService

router = APIRouter(prefix="/api/v1/workspaces", tags=["workspaces"])
email_service = EmailService()


# Pydantic Models
class WorkspaceCreate(BaseModel):
    name: str
    description: str = None
    your_role: str = "Developer"  # Business role in workspace


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    description: str = None
    created_by: int
    is_active: bool
    member_count: int
    created_at: datetime
    my_role: str = None  # Current user's role in this workspace
    
    class Config:
        from_attributes = True


class InviteMember(BaseModel):
    email: EmailStr
    role: str = "member"
    message: str = None


class MemberResponse(BaseModel):
    id: int
    user_id: int
    workspace_id: int
    role: str
    is_active: bool
    email: str
    full_name: str
    joined_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# WORKSPACE ROUTES
# ============================================================================

@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(
    workspace_data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new workspace
    """
    try:
        # Enforce role-based workspace creation (only Scrum Master and Project Manager)
        allowed_creators = {"Scrum Master", "Project Manager"}
        if workspace_data.your_role not in allowed_creators:
            raise HTTPException(status_code=403, detail="Only Scrum Master or Project Manager can create a workspace")

        # Create workspace
        new_workspace = Workspace(
            name=workspace_data.name,
            description=workspace_data.description,
            created_by=current_user.id,
            is_active=True
        )
        db.add(new_workspace)
        db.flush()  # Get workspace ID
        
        # Add creator as member with specified role
        creator_membership = WorkspaceMember(
            workspace_id=new_workspace.id,
            user_id=current_user.id,
            # Store the business role directly
            role=workspace_data.your_role,
            is_active=True
        )
        db.add(creator_membership)
        db.commit()
        db.refresh(new_workspace)
        
        # Count members
        member_count = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == new_workspace.id,
            WorkspaceMember.is_active == True
        ).count()
        
        return WorkspaceResponse(
            id=new_workspace.id,
            name=new_workspace.name,
            description=new_workspace.description,
            created_by=new_workspace.created_by,
            is_active=new_workspace.is_active,
            member_count=member_count,
            created_at=new_workspace.created_at,
            my_role=workspace_data.your_role
        )
        
    except Exception as e:
        db.rollback()
        print(f"Create workspace error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create workspace: {str(e)}")


@router.post("/{workspace_id}/upload-pdf")
async def upload_workspace_pdf(
    workspace_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a reference PDF for the workspace and store path in settings.reference_pdf."""
    try:
        # Check membership
        membership = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.is_active == True
        ).first()

        if not membership:
            raise HTTPException(status_code=403, detail="You are not a member of this workspace")

        # Basic content type check
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Save file to disk under app/docs/uploads/workspaces/<id>/
        import os
        from pathlib import Path

        base_dir = Path("app/docs/uploads/workspaces") / str(workspace_id)
        base_dir.mkdir(parents=True, exist_ok=True)
        dest = base_dir / "reference.pdf"

        contents = await file.read()
        with open(dest, 'wb') as f:
            f.write(contents)

        # Update workspace settings JSON with reference_pdf path
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        settings_obj = workspace.settings or {}
        settings_obj["reference_pdf"] = str(dest)
        workspace.settings = settings_obj
        db.add(workspace)
        db.commit()

        return {"message": "PDF uploaded", "path": str(dest)}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload PDF: {e}")


@router.get("/", response_model=List[WorkspaceResponse])
async def get_my_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all workspaces the current user is a member of
    """
    try:
        # Get workspace IDs user is member of
        memberships = db.query(WorkspaceMember).filter(
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.is_active == True
        ).all()
        
        workspace_ids = [m.workspace_id for m in memberships]
        
        # Get workspaces
        workspaces = db.query(Workspace).filter(
            Workspace.id.in_(workspace_ids),
            Workspace.is_active == True
        ).all()
        
        result = []
        for workspace in workspaces:
            member_count = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace.id,
                WorkspaceMember.is_active == True
            ).count()
            
            # Find current user's role in this workspace
            user_membership = next((m for m in memberships if m.workspace_id == workspace.id), None)
            user_role = user_membership.role if user_membership else None
            
            result.append(WorkspaceResponse(
                id=workspace.id,
                name=workspace.name,
                description=workspace.description,
                created_by=workspace.created_by,
                is_active=workspace.is_active,
                member_count=member_count,
                created_at=workspace.created_at,
                my_role=user_role
            ))
        
        return result
        
    except Exception as e:
        print(f"Get workspaces error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch workspaces: {str(e)}")


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific workspace details
    """
    try:
        # Check membership
        membership = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.is_active == True
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="You are not a member of this workspace")
        
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        member_count = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.is_active == True
        ).count()
        
        return WorkspaceResponse(
            id=workspace.id,
            name=workspace.name,
            description=workspace.description,
            created_by=workspace.created_by,
            is_active=workspace.is_active,
            member_count=member_count,
            created_at=workspace.created_at,
            my_role=membership.role
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get workspace error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch workspace: {str(e)}")


# ============================================================================
# MEMBER MANAGEMENT
# ============================================================================

@router.get("/{workspace_id}/members", response_model=List[MemberResponse])
async def get_workspace_members(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all members of a workspace
    """
    try:
        # Check membership
        membership = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.is_active == True
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="You are not a member of this workspace")
        
        # Get all members
        members = db.query(WorkspaceMember, User).join(
            User, WorkspaceMember.user_id == User.id
        ).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.is_active == True
        ).all()
        
        result = []
        for member, user in members:
            result.append(MemberResponse(
                id=member.id,
                user_id=member.user_id,
                workspace_id=member.workspace_id,
                role=member.role,
                is_active=member.is_active,
                email=user.email,
                full_name=user.full_name,
                joined_at=member.joined_at
            ))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get members error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch members: {str(e)}")


@router.post("/{workspace_id}/invite")
async def invite_member(
    workspace_id: int,
    invite_data: InviteMember,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite a member to workspace via email
    """
    try:
        # Check if user is owner or facilitator
        membership = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.is_active == True
        ).first()
        
        # Allow Scrum Master and Project Manager (workspace creators) to invite
        allowed_roles = ['owner', 'facilitator', 'Scrum Master', 'Project Manager']
        if not membership or membership.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Only owners and facilitators can invite members")
        
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Check if user already invited or is member
        existing_invitation = db.query(WorkspaceInvitation).filter(
            WorkspaceInvitation.workspace_id == workspace_id,
            WorkspaceInvitation.email == invite_data.email,
            WorkspaceInvitation.status == 'pending'
        ).first()
        
        if existing_invitation:
            raise HTTPException(status_code=400, detail="User already invited")
        
        # Check if user is already a member
        invited_user = db.query(User).filter(User.email == invite_data.email).first()
        if invited_user:
            existing_member = db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == invited_user.id,
                WorkspaceMember.is_active == True
            ).first()
            
            if existing_member:
                raise HTTPException(status_code=400, detail="User is already a member")
        
        # Create invitation
        token = secrets.token_urlsafe(32)
        invitation = WorkspaceInvitation(
            workspace_id=workspace_id,
            invited_by=current_user.id,
            email=invite_data.email,
            role=invite_data.role,
            token=token,
            status='pending',
            message=invite_data.message,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.add(invitation)
        db.commit()
        
        # Send invitation email (background task)
        # For now, just return success
        # TODO: Implement email sending
        
        return {
            "message": f"Invitation sent to {invite_data.email}",
            "invitation_token": token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Invite member error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to invite member: {str(e)}")


@router.post("/join/{token}")
async def join_workspace_via_invite(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Join workspace using invitation token
    """
    try:
        # Find invitation
        invitation = db.query(WorkspaceInvitation).filter(
            WorkspaceInvitation.token == token,
            WorkspaceInvitation.status == 'pending'
        ).first()
        
        if not invitation:
            raise HTTPException(status_code=404, detail="Invalid or expired invitation")
        
        # Check if expired
        if invitation.expires_at < datetime.utcnow():
            invitation.status = 'expired'
            db.commit()
            raise HTTPException(status_code=400, detail="Invitation has expired")
        
        # Check if email matches
        if invitation.email != current_user.email:
            raise HTTPException(status_code=403, detail="This invitation is for a different email address")
        
        # Check if already a member
        existing_member = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == invitation.workspace_id,
            WorkspaceMember.user_id == current_user.id,
            WorkspaceMember.is_active == True
        ).first()
        
        if existing_member:
            raise HTTPException(status_code=400, detail="You are already a member of this workspace")
        
        # Add as member
        new_member = WorkspaceMember(
            workspace_id=invitation.workspace_id,
            user_id=current_user.id,
            role=invitation.role,
            is_active=True
        )
        db.add(new_member)
        
        # Update invitation status
        invitation.status = 'accepted'
        invitation.accepted_at = datetime.utcnow()
        
        db.commit()
        
        # Get workspace details
        workspace = db.query(Workspace).filter(Workspace.id == invitation.workspace_id).first()
        
        return {
            "message": f"Successfully joined {workspace.name}",
            "workspace_id": workspace.id,
            "workspace_name": workspace.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Join workspace error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to join workspace: {str(e)}")

