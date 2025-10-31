"""
Workspace invitations API
"""

from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.dependencies.auth import get_current_user
from app.models.workspace import Workspace, WorkspaceMember
from app.models.workspace import WorkspaceInvitation
from app.core.config import settings
from app.services.email_service import EmailService


router = APIRouter(prefix="/api/v1/workspaces", tags=["workspace-invitations"])


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = "member"
    message: str | None = None


def generate_invite_token() -> str:
    # 43 chars ~ 256 bits entropy url-safe; trim as needed
    return secrets.token_urlsafe(32)


@router.post("/{workspace_id}/invitations")
async def create_workspace_invitation(
    workspace_id: int,
    payload: InvitationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # Ensure workspace exists and user has permission (owner/facilitator)
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

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

    # Create invitation with 12-hour expiry
    token = generate_invite_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=12)

    invitation = WorkspaceInvitation(
        workspace_id=workspace_id,
        invited_by=current_user.id,
        email=str(payload.email).lower(),
        role=payload.role,
        token=token,
        status="pending",
        message=payload.message,
        expires_at=expires_at,
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    # Send email invitation (if enabled)
    try:
        invite_link = f"{settings.APP_URL}/ui/yodaai-app.html?invite={token}"
        subject = f"You're invited to join {workspace.name} on YodaAI"
        html = f"""
          <p>Hello,</p>
          <p><strong>{getattr(current_user, 'full_name', current_user.email)}</strong> has invited you to join the workspace <strong>{workspace.name}</strong> as <strong>{invitation.role or 'member'}</strong>.</p>
          {f"<p>Message: {payload.message}</p>" if payload.message else ""}
          <p>This invitation expires in 12 hours.</p>
          <p><a href=\"{invite_link}\" style=\"background:#667eea;color:#fff;padding:10px 16px;border-radius:6px;text-decoration:none;\">Accept Invitation</a></p>
          <p>Or paste this link into your browser:<br>{invite_link}</p>
        """
        
        # Print invitation link to console for testing
        if not settings.ENABLE_EMAIL_NOTIFICATIONS:
            print("="*60)
            print("WORKSPACE INVITATION LINK (check console):")
            print("="*60)
            print(f"Invited by: {getattr(current_user, 'full_name', current_user.email)}")
            print(f"Workspace: {workspace.name}")
            print(f"Invitee: {invitation.email}")
            print(f"Role: {invitation.role or 'member'}")
            print(f"\nInvitation link: {invite_link}")
            print("="*60)
        
        EmailService().send_email(
            to_email=invitation.email,
            subject=subject,
            html_content=html,
            text_content=f"You were invited to {workspace.name}. Accept: {invite_link}"
        )
    except Exception as e:
        # Do not fail the API if email sending fails; invitations can also be accepted in-app
        print(f"Email sending error: {e}")

    return {
        "id": invitation.id,
        "email": invitation.email,
        "role": invitation.role,
        "token": invitation.token,
        "status": invitation.status,
        "expires_at": invitation.expires_at,
    }


# Standalone accept/decline endpoints under a neutral prefix for token-only flows
token_router = APIRouter(prefix="/api/v1/invitations", tags=["workspace-invitations"])


class InvitationToken(BaseModel):
    token: str


def _get_invitation_by_token(db: Session, token: str) -> WorkspaceInvitation | None:
    return db.query(WorkspaceInvitation).filter(WorkspaceInvitation.token == token).first()


@token_router.get("/{token}")
async def get_invitation_status(token: str, db: Session = Depends(get_db)):
    inv = _get_invitation_by_token(db, token)
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    now = datetime.now(timezone.utc)
    expired = inv.expires_at <= now and inv.accepted_at is None and inv.declined_at is None
    status = inv.status
    if expired and status != "expired":
        status = "expired"
    return {
        "email": inv.email,
        "workspace_id": inv.workspace_id,
        "message": inv.message,
        "status": status,
        "expires_at": inv.expires_at,
        "accepted_at": inv.accepted_at,
        "declined_at": inv.declined_at,
    }


@token_router.get("/mine")
async def get_my_invitations(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    invitations = (
        db.query(WorkspaceInvitation)
        .filter(
            WorkspaceInvitation.email == current_user.email,
            WorkspaceInvitation.accepted_at.is_(None),
            WorkspaceInvitation.declined_at.is_(None),
        )
        .all()
    )
    result = []
    for inv in invitations:
        status = inv.status
        if inv.expires_at <= now and status != "expired":
            status = "expired"
        result.append({
            "workspace_id": inv.workspace_id,
            "email": inv.email,
            "message": inv.message,
            "status": status,
            "expires_at": inv.expires_at,
            "token": inv.token,
        })
    return result


@token_router.post("/accept")
async def accept_invitation(body: InvitationToken, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    inv = _get_invitation_by_token(db, body.token)
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    now = datetime.now(timezone.utc)
    if inv.expires_at <= now:
        inv.status = "expired"
        inv.declined_at = now
        db.commit()
        raise HTTPException(status_code=410, detail="Invitation expired")
    if inv.accepted_at is not None:
        return {"detail": "Already accepted"}
    if inv.declined_at is not None:
        raise HTTPException(status_code=409, detail="Invitation already declined")
    # Ensure the accepter matches the invited email
    if current_user.email.lower() != inv.email.lower():
        raise HTTPException(status_code=403, detail="This invitation is for a different email")

    # Create membership
    from app.models.workspace import WorkspaceMember
    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == inv.workspace_id,
        WorkspaceMember.user_id == current_user.id,
    ).first()
    if existing:
        inv.accepted_at = now
        inv.status = "accepted"
        db.commit()
        return {"detail": "Already a member; invitation marked accepted"}

    membership = WorkspaceMember(
        workspace_id=inv.workspace_id,
        user_id=current_user.id,
        role=inv.role or "member",
    )
    db.add(membership)
    inv.accepted_at = now
    inv.status = "accepted"
    db.commit()
    return {"detail": "Invitation accepted"}


@token_router.post("/decline")
async def decline_invitation(body: InvitationToken, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    inv = _get_invitation_by_token(db, body.token)
    if not inv:
        raise HTTPException(status_code=404, detail="Invitation not found")
    now = datetime.now(timezone.utc)
    if inv.accepted_at is not None:
        raise HTTPException(status_code=409, detail="Invitation already accepted")
    if inv.declined_at is not None:
        return {"detail": "Already declined"}
    # Allow decline if same email or inviter; otherwise forbid
    if current_user.email.lower() != inv.email.lower() and current_user.id != inv.invited_by:
        raise HTTPException(status_code=403, detail="Not authorized to decline this invitation")
    inv.declined_at = now
    inv.status = "declined"
    db.commit()
    return {"detail": "Invitation declined"}


