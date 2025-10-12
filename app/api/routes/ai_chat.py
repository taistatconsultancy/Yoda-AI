"""
AI chat routes for retrospective assistance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.ai_chat import ChatSession, ChatMessage
from app.schemas.ai_chat import (
    ChatSessionCreate, 
    ChatSessionResponse, 
    ChatMessageResponse, 
    ChatRequest
)
from app.services.ai_chat_service import AIChatService
from app.api.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new chat session"""
    service = AIChatService(db)
    session = service.create_chat_session(session_data, current_user.id)
    return ChatSessionResponse.from_orm(session)


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 100,
    retrospective_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's chat sessions"""
    service = AIChatService(db)
    sessions = service.get_user_sessions(
        current_user.id, 
        skip=skip, 
        limit=limit,
        retrospective_id=retrospective_id
    )
    return [ChatSessionResponse.from_orm(session) for session in sessions]


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific chat session"""
    service = AIChatService(db)
    session = service.get_chat_session(session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return ChatSessionResponse.from_orm(session)


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    session_id: str,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Send a message in a chat session"""
    service = AIChatService(db)
    
    # Verify session belongs to user
    session = service.get_chat_session(session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Send message and get AI response
    message = await service.send_message(session_id, chat_request.message, current_user.id)
    return ChatMessageResponse.from_orm(message)


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get messages from a chat session"""
    service = AIChatService(db)
    
    # Verify session belongs to user
    session = service.get_chat_session(session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = service.get_chat_messages(session_id, skip=skip, limit=limit)
    return [ChatMessageResponse.from_orm(message) for message in messages]


@router.post("/sessions/{session_id}/end")
async def end_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """End a chat session"""
    service = AIChatService(db)
    success = service.end_chat_session(session_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return {"message": "Chat session ended successfully"}


@router.post("/retrospective/{retrospective_id}/analyze")
async def analyze_retrospective(
    retrospective_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Analyze retrospective data and generate insights"""
    service = AIChatService(db)
    analysis = await service.analyze_retrospective(retrospective_id, current_user.id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retrospective not found"
        )
    return analysis
