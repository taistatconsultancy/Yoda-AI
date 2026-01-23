"""
Workspace Documents Routes

Owns project document uploads intended for workspace-scoped RAG.
"""

from typing import Any, Dict, Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database.database import get_db
from app.api.dependencies.permissions import get_workspace_membership
from app.models.workspace import Workspace
from app.models.onboarding import UserOnboarding
from app.core.config import settings
from app.ai.openai_client import AIClient
from app.ai.rag.chroma_store import ChromaStore
from app.ai.utils import hash_text

# Reuse extractors from onboarding (keeps behavior consistent for now)
from app.api.routes.onboarding import _extract_text_from_pdf_bytes, _extract_text_from_docx_bytes, _extract_text_from_docx_manual  # noqa: F401


router = APIRouter(prefix="/api/v1", tags=["workspace-documents"])


@router.post("/workspaces/{workspace_id}/documents/upload")
async def upload_workspace_document(
    workspace_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
):
    # Enforce privileged roles (Scrum Master or Project Manager)
    role = (membership.role or '').strip().lower()
    if role not in ('scrum master', 'project manager'):
        raise HTTPException(status_code=403, detail="Requires Scrum Master or Project Manager privileges")

    workspace: Optional[Workspace] = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    content_bytes = await file.read()
    filename_lower = (file.filename or "").lower()
    ctype = (file.content_type or "").lower()

    # Extract text
    if ctype in ("application/pdf",) or filename_lower.endswith(".pdf"):
        text = _extract_text_from_pdf_bytes(content_bytes)
        if not text:
            raise HTTPException(status_code=415, detail="Unable to parse PDF. Ensure it's text-based (not scanned).")
    elif (ctype in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword")
          or filename_lower.endswith((".docx", ".doc"))):
        if filename_lower.endswith(".docx"):
            text = _extract_text_from_docx_bytes(content_bytes) or _extract_text_from_docx_manual(content_bytes)
        else:
            raise HTTPException(status_code=415, detail="Legacy .doc files are not supported. Please convert to .docx.")
        if not text:
            raise HTTPException(status_code=415, detail="Unable to extract text from Word document.")
    else:
        try:
            text = content_bytes.decode("utf-8", errors="ignore")
        except Exception:
            text = content_bytes.decode("latin-1", errors="ignore")
        if not text or not text.strip():
            raise HTTPException(status_code=415, detail="Unsupported or empty document. Use .txt, .md, .pdf, .docx")

    uploaded_at = datetime.now(timezone.utc).isoformat()
    doc_hash = hash_text(text)
    doc_id = f"{workspace_id}:{(file.filename or 'document')}:{doc_hash}"

    # Keep a canonical list of document metadata in user_onboarding for now (owner record).
    owner_onboarding: Optional[UserOnboarding] = db.query(UserOnboarding).filter(
        UserOnboarding.user_id == workspace.created_by,
        UserOnboarding.workspace_id == workspace_id
    ).first()
    data: Dict[str, Any] = {}
    if owner_onboarding and isinstance(owner_onboarding.onboarding_data, dict):
        data.update(owner_onboarding.onboarding_data)

    docs = data.get("documents")
    if not isinstance(docs, list):
        docs = []
    docs.append({
        "doc_id": doc_id,
        "doc_hash": doc_hash,
        "filename": file.filename,
        "uploaded_at": uploaded_at,
        "bytes": len(content_bytes),
    })
    data["documents"] = docs
    data["updated_at"] = uploaded_at

    if not owner_onboarding:
        owner_onboarding = UserOnboarding(user_id=workspace.created_by, workspace_id=workspace_id, onboarding_data=data)
        db.add(owner_onboarding)
    else:
        owner_onboarding.onboarding_data = data
    db.commit()

    # Background index into Chroma (workspace-scoped)
    def _index_doc(wid: int, did: str, dhash: str, fname: str, uploaded_at_iso: str, txt: str) -> None:
        try:
            ai = AIClient()
            store = ChromaStore()
            store.upsert_text_document(
                ai=ai,
                source="onboarding",
                doc_id=did,
                text=txt,
                embedding_model=getattr(settings, "AI_EMBEDDING_MODEL", "text-embedding-3-small"),
                extra_metadata={"workspace_id": wid, "filename": fname, "uploaded_at": uploaded_at_iso, "doc_hash": dhash},
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Workspace document indexing failed: {e}")
            return

    background_tasks.add_task(_index_doc, workspace_id, doc_id, doc_hash, (file.filename or ""), uploaded_at, text)

    return {"workspace_id": workspace_id, "doc_id": doc_id, "doc_hash": doc_hash, "filename": file.filename, "saved": True}


@router.get("/workspaces/{workspace_id}/documents")
def list_workspace_documents(
    workspace_id: int,
    membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
):
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
    data = owner_onboarding.onboarding_data if owner_onboarding and isinstance(owner_onboarding.onboarding_data, dict) else {}
    docs = data.get("documents") if isinstance(data, dict) else []
    if not isinstance(docs, list):
        docs = []
    return {"workspace_id": workspace_id, "documents": docs}

