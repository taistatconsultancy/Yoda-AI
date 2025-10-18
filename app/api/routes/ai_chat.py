"""
AI chat routes for retrospective assistance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import asyncio
import json
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
from app.services.enhanced_ai_service import EnhancedAIService
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.api.dependencies.auth import get_current_user

router = APIRouter()


class ProxyRequest(BaseModel):
    message: str
    current_step: Optional[str] = None
    chat_history: Optional[list] = None
    project_context: Optional[str] = None


@router.post("/proxy")
async def proxy_chat(request: ProxyRequest):
    """Lightweight, unauthenticated proxy endpoint that returns an LLM reply for the frontend.

    Note: This endpoint is intentionally simple for development/demo usage. In production you
    should protect it with authentication/quotas and validate inputs carefully.
    """
    try:
        ai_service = EnhancedAIService()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI service unavailable: {e}")

    try:
        resp = await ai_service.generate_retrospective_response(
            user_message=request.message,
            current_step=request.current_step or "liked",
            chat_history=request.chat_history or [],
            project_context=request.project_context
        )

        return {
            "response": resp.get("response", ""),
            "metadata": resp.get("metadata", {}),
            "follow_up_questions": resp.get("follow_up_questions", [])
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating AI response: {e}")


@router.post("/proxy/stream")
async def proxy_chat_stream(request: ProxyRequest):
    """Stream the AI reply as a typing effect using Server-Sent Events (SSE).

    This endpoint returns 'text/event-stream' SSE where each event's data is a
    small chunk of the final AI response. The frontend can consume this with
    EventSource and append the chunks to render a typing animation.
    """
    try:
        ai_service = EnhancedAIService()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI service unavailable: {e}")

    try:
        resp = await ai_service.generate_retrospective_response(
            user_message=request.message,
            current_step=request.current_step or "liked",
            chat_history=request.chat_history or [],
            project_context=request.project_context
        )

        text = resp.get("response", "") or ""

        # Choose chunk size for streaming. 1 = letter-by-letter, >1 groups letters.
        chunk_size = 4

        async def event_stream():
            # Stream the response in small chunks as SSE 'data' messages
            for i in range(0, len(text), chunk_size):
                chunk = text[i : i + chunk_size]
                # SSE data frame
                yield f"data: {chunk}\n\n"
                # Small pause to simulate typing
                await asyncio.sleep(0.03)

            # Signal end of stream with a final event
            yield "event: end\ndata: \n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating AI response: {e}")


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
