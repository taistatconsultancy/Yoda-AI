"""
Onboarding Routes - expose onboarding data/summary for workspaces
"""

from typing import Any, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database.database import get_db
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import (
    get_workspace_membership,
)
from app.models.workspace import Workspace, WorkspaceMember
from app.models.retrospective_new import Retrospective
from app.models.onboarding import UserOnboarding
from app.models.user import User
from app.core.config import settings

try:
    # Optional OpenAI client for summary generation
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

# Optional PDF parsing
try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None  # type: ignore


def _extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using pypdf if available; otherwise return empty string."""
    if PdfReader is None:
        return ""
    try:
        import io
        with io.BytesIO(pdf_bytes) as fh:
            reader = PdfReader(fh)
            texts = []
            for page in reader.pages:
                try:
                    texts.append(page.extract_text() or "")
                except Exception:
                    continue
            return "\n".join(t for t in texts if t)
    except Exception:
        return ""


router = APIRouter(prefix="/api/v1", tags=["onboarding"])


class OnboardingUpdateRequest(BaseModel):
    onboarding_data: Any


@router.get("/workspaces/{workspace_id}/onboarding")
def get_workspace_onboarding(
    workspace_id: int,
    membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db)
):
    """
    Return the owner's onboarding_data for a workspace.
    Any active workspace member can view this summary (regardless of role).
    """
    workspace: Optional[Workspace] = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    # Find onboarding record for the owner (created_by)
    owner_onboarding: Optional[UserOnboarding] = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == workspace.created_by
    ).first()

    # Compute dynamic onboarding flags based on live data
    members_count = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id, WorkspaceMember.is_active == True).count()
    has_team = members_count >= 2
    has_retro = db.query(Retrospective).filter(Retrospective.workspace_id == workspace_id).count() > 0
    data = owner_onboarding.onboarding_data if owner_onboarding and isinstance(owner_onboarding.onboarding_data, dict) else {}
    source_text = data.get("source_text", "") if isinstance(data, dict) else ""
    imported = bool(source_text and source_text.strip())

    # Update booleans on record if out of sync
    changed = False
    if owner_onboarding:
        if owner_onboarding.workspace_setup_completed != True:
            owner_onboarding.workspace_setup_completed = True; changed = True
        if owner_onboarding.team_members_added != has_team:
            owner_onboarding.team_members_added = has_team; changed = True
        if owner_onboarding.project_data_imported != imported:
            owner_onboarding.project_data_imported = imported; changed = True
        if owner_onboarding.first_retrospective_scheduled != has_retro:
            owner_onboarding.first_retrospective_scheduled = has_retro; changed = True
        if changed:
            db.commit()
            db.refresh(owner_onboarding)

    return {
        "workspace_id": workspace_id,
        "owner_user_id": workspace.created_by,
        "onboarding_data": owner_onboarding.onboarding_data if owner_onboarding else None,
        "status": {
            "workspace_setup_completed": True,
            "team_members_added": has_team,
            "project_data_imported": imported,
            "first_retrospective_scheduled": has_retro,
            "check_ins_configured": bool(owner_onboarding.check_ins_configured) if owner_onboarding else False,
            "onboarding_completed": bool(owner_onboarding.onboarding_completed) if owner_onboarding else False,
        }
    }


@router.put("/workspaces/{workspace_id}/onboarding")
def update_workspace_onboarding(
    workspace_id: int,
    payload: OnboardingUpdateRequest,
    membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db)
):
    """
    Update the owner's onboarding_data for the workspace.
    Requires Scrum Master or Project Manager membership in the workspace.
    # Enforce privileged roles (Scrum Master or Project Manager)
    role_update = (membership.role or '').strip().lower()
    if role_update not in ('scrum master', 'project manager'):
        raise HTTPException(status_code=403, detail="Requires Scrum Master or Project Manager privileges")
    """
    workspace: Optional[Workspace] = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    # Ensure an onboarding record exists for owner
    owner_onboarding: Optional[UserOnboarding] = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == workspace.created_by
    ).first()

    # Ensure JSON object structure for onboarding_data
    incoming: Any = payload.onboarding_data
    if isinstance(incoming, str):
        # Wrap raw string into structured JSON
        incoming = {"source_text": incoming, "ai_summary": None}
    elif not isinstance(incoming, dict):
        incoming = {"raw": incoming}

    incoming["updated_at"] = datetime.now(timezone.utc).isoformat()

    if not owner_onboarding:
        owner_onboarding = UserOnboarding(user_id=workspace.created_by, onboarding_data=incoming)
        db.add(owner_onboarding)
    else:
        # Preserve existing ai_summary unless explicitly provided
        existing = owner_onboarding.onboarding_data if isinstance(owner_onboarding.onboarding_data, dict) else {}
        if isinstance(incoming, dict):
            if "ai_summary" not in incoming and isinstance(existing, dict) and "ai_summary" in existing:
                incoming["ai_summary"] = existing.get("ai_summary")
        owner_onboarding.onboarding_data = incoming

    db.commit()
    db.refresh(owner_onboarding)

    return {
        "workspace_id": workspace_id,
        "owner_user_id": workspace.created_by,
        "onboarding_data": owner_onboarding.onboarding_data,
        "updated": True,
    }


# ====================== User Onboarding (Self) ======================

@router.get("/user-onboarding/me")
def get_my_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the authenticated user's onboarding record.
    """
    rec = db.query(UserOnboarding).filter(UserOnboarding.user_id == current_user.id).first()
    return {
        "user_id": current_user.id,
        "onboarding_data": rec.onboarding_data if rec else None
    }


@router.put("/user-onboarding")
def upsert_my_onboarding(
    payload: OnboardingUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update the authenticated user's onboarding record.
    """
    rec = db.query(UserOnboarding).filter(UserOnboarding.user_id == current_user.id).first()
    if not rec:
        rec = UserOnboarding(user_id=current_user.id, onboarding_data=payload.onboarding_data)
        db.add(rec)
    else:
        rec.onboarding_data = payload.onboarding_data
    db.commit()
    db.refresh(rec)
    return {
        "user_id": current_user.id,
        "onboarding_data": rec.onboarding_data,
        "updated": True
    }


# ====================== Upload and Generate Summary ======================

@router.post("/workspaces/{workspace_id}/onboarding/upload")
async def upload_onboarding_source(
    workspace_id: int,
    file: UploadFile = File(...),
    membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db)
):
    # Enforce privileged roles (Scrum Master or Project Manager)
    role = (membership.role or '').strip().lower()
    if role not in ('scrum master', 'project manager'):
        raise HTTPException(status_code=403, detail="Requires Scrum Master or Project Manager privileges")
    """
    Upload a text/markdown file to set onboarding_data for the workspace owner.
    Currently supports text/plain and markdown. PDFs not parsed here.
    """
    content_bytes = await file.read()
    text = ""
    filename_lower = (file.filename or "").lower()
    ctype = (file.content_type or "").lower()
    if ctype in ("application/pdf",) or filename_lower.endswith(".pdf"):
        text = _extract_text_from_pdf_bytes(content_bytes)
        if not text:
            raise HTTPException(status_code=415, detail="Unable to parse PDF. Ensure the file is not scanned or image-only.")
    else:
        # Treat as text/markdown
        try:
            text = content_bytes.decode("utf-8", errors="ignore")
        except Exception:
            text = ""
        if not text:
            raise HTTPException(status_code=415, detail="Unsupported file or empty content. Provide a valid .txt/.md or .pdf file.")

    workspace: Optional[Workspace] = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    owner_onboarding: Optional[UserOnboarding] = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == workspace.created_by
    ).first()
    # Build structured JSON
    data: Dict[str, Any] = {}
    if owner_onboarding and isinstance(owner_onboarding.onboarding_data, dict):
        data.update(owner_onboarding.onboarding_data)
    data["source_text"] = text
    # Do not overwrite ai_summary here; generation endpoint will set it
    data["updated_at"] = datetime.now(timezone.utc).isoformat()

    if not owner_onboarding:
        owner_onboarding = UserOnboarding(user_id=workspace.created_by, onboarding_data=data)
        db.add(owner_onboarding)
    else:
        owner_onboarding.onboarding_data = data

    db.commit()
    db.refresh(owner_onboarding)

    return {
        "workspace_id": workspace_id,
        "uploaded_filename": file.filename,
        "bytes": len(content_bytes),
        "onboarding_data_preview": (text[:200] + "...") if len(text) > 200 else text,
        "saved": True,
    }


def _get_openai_client():
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key or OpenAI is None:
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None


@router.post("/workspaces/{workspace_id}/onboarding/generate")
def generate_workspace_summary(
    workspace_id: int,
    membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db)
):
    # Enforce privileged roles (Scrum Master or Project Manager)
    role = (membership.role or '').strip().lower()
    if role not in ('scrum master', 'project manager'):
        raise HTTPException(status_code=403, detail="Requires Scrum Master or Project Manager privileges")
    """
    Generate an AI summary from the owner's onboarding_data and save it back.
    If OpenAI isn't configured, returns the first 800 chars as a fallback.
    """
    workspace: Optional[Workspace] = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    owner_onboarding: Optional[UserOnboarding] = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == workspace.created_by
    ).first()
    raw_data = owner_onboarding.onboarding_data if owner_onboarding else None
    source_text = ""
    if isinstance(raw_data, dict):
        source_text = raw_data.get("source_text", "") or ""
    elif isinstance(raw_data, str):
        # Backward compatibility
        source_text = raw_data

    if not isinstance(source_text, str) or source_text.strip() == "":
        raise HTTPException(status_code=400, detail="No onboarding data available to summarize. Please upload text first.")

    client = _get_openai_client()
    summary_text: str
    if client is None:
        # Fallback summary: truncate and label
        summary_text = (source_text[:800] + ("..." if len(source_text) > 800 else ""))
    else:
        try:
            prompt = (
                "Summarize the following workspace context into a clear, concise brief (<= 250 words). "
                "Highlight goals, scope, stakeholders, timelines, risks, and any constraints.\n\n" + source_text
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """
                            You are YodaAI, an intelligent product strategist that helps summarize project ideas into clear, concise MVP (Minimum Viable Product) descriptions.

                            Your task:
                            Given a user’s project idea or description, summarize it into a structured MVP overview.

                            Your summary must include:

                            Core Problem: What pain point or need does the project address?

                            Target Users: Who is it for?

                            Key Features (MVP Scope): What are the essential features needed for launch?

                            Technology/Tools: What stack or tools could be used (if applicable)?

                            Value Proposition: What makes this MVP valuable or unique?

                            Style:

                            Keep it short (150–250 words).

                            Use simple, professional, and engaging language.

                            Focus only on the minimum features needed to test the idea.

                            
                    """},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400,
            )
            summary_text = resp.choices[0].message.content.strip()
        except Exception:
            summary_text = (source_text[:800] + ("..." if len(source_text) > 800 else ""))

    # Save the summary into onboarding_data JSON under ai_summary
    data_out: Dict[str, Any] = {}
    if owner_onboarding and isinstance(owner_onboarding.onboarding_data, dict):
        data_out.update(owner_onboarding.onboarding_data)
    else:
        # Wrap legacy string source into structured JSON
        data_out = {"source_text": source_text}
    data_out["ai_summary"] = summary_text
    data_out["updated_at"] = datetime.now(timezone.utc).isoformat()

    if not owner_onboarding:
        owner_onboarding = UserOnboarding(user_id=workspace.created_by, onboarding_data=data_out)
        db.add(owner_onboarding)
    else:
        owner_onboarding.onboarding_data = data_out
    # Keep computed flags updated
    owner_onboarding.workspace_setup_completed = True
    owner_onboarding.project_data_imported = True if data_out.get("source_text") else owner_onboarding.project_data_imported
    db.commit()
    db.refresh(owner_onboarding)

    return {
        "workspace_id": workspace_id,
        "onboarding_data": owner_onboarding.onboarding_data,
        "generated": True,
    }


@router.post("/workspaces/{workspace_id}/onboarding/complete")
def mark_onboarding_complete(
    workspace_id: int,
    membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db)
):
    """Mark onboarding as completed and set completed_at timestamp."""
    role = (membership.role or '').strip().lower()
    if role not in ('scrum master', 'project manager'):
        raise HTTPException(status_code=403, detail="Requires Scrum Master or Project Manager privileges")

    workspace: Optional[Workspace] = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    owner_onboarding: Optional[UserOnboarding] = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == workspace.created_by
    ).first()
    if not owner_onboarding:
        owner_onboarding = UserOnboarding(user_id=workspace.created_by)
        db.add(owner_onboarding)

    owner_onboarding.onboarding_completed = True
    owner_onboarding.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(owner_onboarding)
    return {"workspace_id": workspace_id, "onboarding_completed": True}


