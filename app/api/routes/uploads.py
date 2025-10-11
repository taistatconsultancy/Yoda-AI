"""
File upload routes for sprint summaries
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.sprint_summary import SprintSummary
from app.schemas.sprint_summary import SprintSummaryCreate, SprintSummaryResponse
from app.services.upload_service import UploadService
from app.api.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/sprint-summary", response_model=SprintSummaryResponse)
async def upload_sprint_summary(
    file: UploadFile = File(...),
    sprint_id: str = None,
    title: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload a sprint summary file"""
    
    # Validate file type
    if not file.filename.endswith(('.json', '.csv', '.txt')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JSON, CSV, and TXT files are allowed"
        )
    
    # Read file content
    content = await file.read()
    
    # Create upload service and process file
    upload_service = UploadService(db)
    
    try:
        sprint_summary = upload_service.process_sprint_summary(
            file_content=content,
            filename=file.filename,
            file_size=len(content),
            sprint_id=sprint_id,
            title=title or file.filename,
            uploaded_by=current_user.id
        )
        
        return SprintSummaryResponse.from_orm(sprint_summary)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/sprint-summaries")
async def get_sprint_summaries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's uploaded sprint summaries"""
    upload_service = UploadService(db)
    summaries = upload_service.get_user_sprint_summaries(current_user.id, skip=skip, limit=limit)
    return [SprintSummaryResponse.from_orm(s) for s in summaries]


@router.get("/sprint-summary/{summary_id}", response_model=SprintSummaryResponse)
async def get_sprint_summary(
    summary_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific sprint summary"""
    upload_service = UploadService(db)
    summary = upload_service.get_sprint_summary(summary_id, current_user.id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sprint summary not found"
        )
    return SprintSummaryResponse.from_orm(summary)
