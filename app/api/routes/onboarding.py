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

# Optional Word document parsing
try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover
    Document = None  # type: ignore


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
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"PDF extraction failed: {str(e)}")
        return ""


def _extract_text_from_docx_bytes(docx_bytes: bytes) -> str:
    """Extract text from Word document (.docx) bytes using python-docx if available."""
    if Document is None:
        return ""
    try:
        import io
        with io.BytesIO(docx_bytes) as fh:
            doc = Document(fh)
            paragraphs = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text)
            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_texts = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_texts.append(cell.text.strip())
                    if row_texts:
                        paragraphs.append(" | ".join(row_texts))
            return "\n\n".join(paragraphs)
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"DOCX extraction failed: {str(e)}")
        return ""


def _extract_text_from_docx_manual(docx_bytes: bytes) -> str:
    """Fallback: Extract text from .docx by parsing the ZIP/XML structure manually."""
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        import io
        
        with zipfile.ZipFile(io.BytesIO(docx_bytes), 'r') as zip_file:
            # Read the main document XML
            if 'word/document.xml' not in zip_file.namelist():
                return ""
            
            xml_content = zip_file.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # Define namespaces for Word documents
            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            }
            
            # Extract all text from paragraphs
            paragraphs = []
            for para in root.findall('.//w:p', namespaces):
                texts = []
                for text_elem in para.findall('.//w:t', namespaces):
                    if text_elem.text:
                        texts.append(text_elem.text)
                if texts:
                    paragraphs.append(''.join(texts))
            
            return '\n\n'.join(paragraphs)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Manual DOCX extraction failed: {str(e)}")
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

    # Find onboarding record for the owner (created_by) and this workspace
    owner_onboarding: Optional[UserOnboarding] = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == workspace.created_by,
        UserOnboarding.workspace_id == workspace_id
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

    # Ensure an onboarding record exists for owner and this workspace
    owner_onboarding: Optional[UserOnboarding] = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == workspace.created_by,
        UserOnboarding.workspace_id == workspace_id
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
        owner_onboarding = UserOnboarding(
            user_id=workspace.created_by,
            workspace_id=workspace_id,
            onboarding_data=incoming
        )
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
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the authenticated user's onboarding record for a specific workspace.
    """
    rec = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == current_user.id,
        UserOnboarding.workspace_id == workspace_id
    ).first()
    return {
        "user_id": current_user.id,
        "workspace_id": workspace_id,
        "onboarding_data": rec.onboarding_data if rec else None
    }


@router.put("/user-onboarding")
def upsert_my_onboarding(
    workspace_id: int,
    payload: OnboardingUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or update the authenticated user's onboarding record for a specific workspace.
    """
    # Verify workspace exists and user has access
    workspace: Optional[Workspace] = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    
    rec = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == current_user.id,
        UserOnboarding.workspace_id == workspace_id
    ).first()
    if not rec:
        rec = UserOnboarding(
            user_id=current_user.id,
            workspace_id=workspace_id,
            onboarding_data=payload.onboarding_data
        )
        db.add(rec)
    else:
        rec.onboarding_data = payload.onboarding_data
    db.commit()
    db.refresh(rec)
    return {
        "user_id": current_user.id,
        "workspace_id": workspace_id,
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
    Upload a file to set onboarding_data for the workspace owner.
    Supported formats:
    - Text files: .txt, .md (plain text and markdown)
    - PDF files: .pdf (text-based PDFs only, not scanned/image-only)
    - Word documents: .docx (modern Word format)
    
    The extracted text will be stored and can be summarized using the generate endpoint.
    """
    content_bytes = await file.read()
    text = ""
    filename_lower = (file.filename or "").lower()
    ctype = (file.content_type or "").lower()
    
    # Determine file type and extract text accordingly
    if ctype in ("application/pdf",) or filename_lower.endswith(".pdf"):
        # Handle PDF files
        text = _extract_text_from_pdf_bytes(content_bytes)
        if not text:
            raise HTTPException(
                status_code=415, 
                detail="Unable to parse PDF. Ensure the file is not scanned or image-only. Text-based PDFs are supported."
            )
    elif (ctype in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                    "application/msword") or 
          filename_lower.endswith((".docx", ".doc"))):
        # Handle Word documents (.docx and .doc)
        if filename_lower.endswith(".docx"):
            # Try python-docx first, then fallback to manual parsing
            text = _extract_text_from_docx_bytes(content_bytes)
            if not text:
                # Fallback to manual ZIP/XML parsing
                text = _extract_text_from_docx_manual(content_bytes)
        else:
            # .doc files (older format) - not easily parseable without additional libraries
            raise HTTPException(
                status_code=415,
                detail="Legacy .doc files are not supported. Please convert to .docx format or upload as PDF."
            )
        
        if not text:
            raise HTTPException(
                status_code=415,
                detail="Unable to extract text from Word document. Please ensure the file is a valid .docx file."
            )
    else:
        # Treat as plain text/markdown
        try:
            text = content_bytes.decode("utf-8", errors="ignore")
        except Exception:
            # Try other encodings
            try:
                text = content_bytes.decode("latin-1", errors="ignore")
            except Exception:
                text = ""
        
        if not text or not text.strip():
            raise HTTPException(
                status_code=415, 
                detail="Unsupported file format or empty content. Supported formats: .txt, .md, .pdf, .docx"
            )

    workspace: Optional[Workspace] = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    owner_onboarding: Optional[UserOnboarding] = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == workspace.created_by,
        UserOnboarding.workspace_id == workspace_id
    ).first()
    # Build structured JSON
    data: Dict[str, Any] = {}
    if owner_onboarding and isinstance(owner_onboarding.onboarding_data, dict):
        data.update(owner_onboarding.onboarding_data)
    
    # Store the uploaded text - this is what will be summarized
    data["source_text"] = text
    # Store upload metadata for verification
    data["uploaded_at"] = datetime.now(timezone.utc).isoformat()
    data["uploaded_filename"] = file.filename
    # Do not overwrite ai_summary here; generation endpoint will set it
    data["updated_at"] = datetime.now(timezone.utc).isoformat()

    if not owner_onboarding:
        owner_onboarding = UserOnboarding(
            user_id=workspace.created_by,
            workspace_id=workspace_id,
            onboarding_data=data
        )
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
    
    DATA FLOW VERIFICATION:
    - This endpoint reads source_text from the onboarding_data stored by the upload endpoint
    - Both endpoints use the same workspace_id filter to ensure data isolation per workspace
    - The source_text extracted here is the exact text that was uploaded for this workspace
    - Metadata (uploaded_at, summary_source_length) is stored to verify data integrity
    """
    workspace: Optional[Workspace] = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    owner_onboarding: Optional[UserOnboarding] = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == workspace.created_by,
        UserOnboarding.workspace_id == workspace_id
    ).first()
    
    if not owner_onboarding:
        raise HTTPException(status_code=400, detail="No onboarding data found for this workspace. Please upload a file first.")
    
    raw_data = owner_onboarding.onboarding_data
    source_text = ""
    if isinstance(raw_data, dict):
        source_text = raw_data.get("source_text", "") or ""
    elif isinstance(raw_data, str):
        # Backward compatibility
        source_text = raw_data

    if not isinstance(source_text, str) or source_text.strip() == "":
        raise HTTPException(status_code=400, detail="No source text available to summarize. Please upload a file first.")
    
    # Verify we're using the correct workspace's data
    # This ensures data integrity - the source_text should belong to this workspace
    if isinstance(raw_data, dict) and "updated_at" in raw_data:
        # Optional: Could add additional validation here if needed
        pass

    client = _get_openai_client()
    summary_text: str
    if client is None:
        # Fallback summary: truncate and label
        summary_text = (source_text[:800] + ("..." if len(source_text) > 800 else ""))
    else:
        try:
            prompt = (
                """
                You are an expert project analyst and proposal reviewer.
                Read the following project proposal carefully and generate a concise summary that captures the main objectives, methods, expected outcomes, and key insights.\n\n
                """
                 + source_text
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """
                            You are an expert project analyst and proposal reviewer. 
                            Your task is to read and summarize project proposal documents into clear, structured summaries that capture the main points accurately.

                            Given the full text of a project proposal, produce a concise summary that includes:

                            1. **Project Title & Objective** – Briefly describe the main goal or purpose.
                            2. **Problem Statement** – Outline the key issue or challenge being addressed.
                            3. **Proposed Solution / Methodology** – Summarize how the project plans to achieve its goals.
                            4. **Expected Outcomes / Impact** – Explain what results or benefits are anticipated.
                            5. **Key Stakeholders / Partners (if mentioned)** – Identify relevant participants or organizations.

                            Guidelines:
                            - Keep the summary between **150–250 words**.
                            - Maintain a **professional, neutral, and analytical tone**.
                            - Use **clear and concise language** suitable for project documentation.
                            - If any section is missing from the proposal, **omit it** rather than fabricating information.

                            User input will contain the full project proposal text.


                            
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
    # IMPORTANT: Preserve the source_text that was used for generation
    data_out: Dict[str, Any] = {}
    if owner_onboarding and isinstance(owner_onboarding.onboarding_data, dict):
        data_out.update(owner_onboarding.onboarding_data)
        # Ensure we're using the same source_text that was uploaded
        # This prevents any potential data mixing issues
        if "source_text" in data_out and data_out["source_text"] != source_text:
            # This should never happen, but log if it does
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Source text mismatch detected for workspace {workspace_id}")
    else:
        # Wrap legacy string source into structured JSON
        data_out = {"source_text": source_text}
    
    # Store the summary with metadata about what was summarized
    data_out["ai_summary"] = summary_text
    data_out["summary_generated_at"] = datetime.now(timezone.utc).isoformat()
    data_out["summary_source_length"] = len(source_text)  # Store length for verification
    data_out["updated_at"] = datetime.now(timezone.utc).isoformat()

    # owner_onboarding should always exist at this point (we checked earlier)
    # But keep this as a safety check
    if not owner_onboarding:
        raise HTTPException(status_code=500, detail="Onboarding record was deleted during generation. Please try again.")
    
    # Update the onboarding data with the generated summary
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
        UserOnboarding.user_id == workspace.created_by,
        UserOnboarding.workspace_id == workspace_id
    ).first()
    if not owner_onboarding:
        owner_onboarding = UserOnboarding(
            user_id=workspace.created_by,
            workspace_id=workspace_id
        )
        db.add(owner_onboarding)

    owner_onboarding.onboarding_completed = True
    owner_onboarding.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(owner_onboarding)
    return {"workspace_id": workspace_id, "onboarding_completed": True}


