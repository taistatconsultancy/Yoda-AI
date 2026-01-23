"""
4Ls AI Chat with Dynamic Progress Tracking
Handles: Liked, Learned, Lacked, Longed For
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timezone
import os
import json

from app.database.database import get_db
from app.models.retrospective_new import (
    Retrospective, ChatSession, ChatMessage, RetrospectiveResponse,
    RetrospectiveParticipant
)
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.core.config import settings
from app.ai.openai_client import AIClient
from app.ai.features.fourls_chat import generate_fourls_reply

router = APIRouter(prefix="/api/v1/fourls-chat", tags=["4ls-chat"])


# Pydantic Models
class ChatMessageRequest(BaseModel):
    retrospective_id: int
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    content: str
    message_type: str
    created_at: datetime
    current_category: str = None
    
    class Config:
        from_attributes = True


class ProgressOverview(BaseModel):
    liked: bool = False
    learned: bool = False
    lacked: bool = False
    longed_for: bool = False
    all_completed: bool = False


class ChatSessionResponse(BaseModel):
    session_id: str
    retrospective_id: int
    current_category: str
    progress: ProgressOverview
    messages: List[ChatMessageResponse]
    
    class Config:
        from_attributes = True


# ============================================================================
# 4LS CHAT ENDPOINTS
# ============================================================================

class StartChatRequest(BaseModel):
    retrospective_id: int


@router.post("/start")
async def start_4ls_chat(
    retrospective_id: Optional[int] = None,
    start_data: Optional[StartChatRequest] = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new 4Ls chat session
    """
    try:
        # Accept retrospective_id from query or JSON body for compatibility
        retro_id = retrospective_id if retrospective_id is not None else (start_data.retrospective_id if start_data else None)
        if retro_id is None:
            raise HTTPException(status_code=422, detail="retrospective_id is required")

        # Verify retrospective exists and is at/after scheduled start
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")

        # Verify user is participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="You are not a participant in this retrospective")
        
        # Check if session already exists
        existing_session = db.query(ChatSession).filter(
            ChatSession.retrospective_id == retrospective_id,
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True,
            ChatSession.is_completed == False
        ).first()
        
        if existing_session:
            return {
                "session_id": existing_session.session_id,
                "message": "Resuming existing session"
            }
        
        # Deactivate any stale completed sessions that might still be marked active
        stale_sessions = db.query(ChatSession).filter(
            ChatSession.retrospective_id == retrospective_id,
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True,
            ChatSession.is_completed == True
        ).all()
        for stale in stale_sessions:
            stale.is_active = False
        
        # Create new session
        import secrets
        session_id = secrets.token_urlsafe(16)
        
        new_session = ChatSession(
            retrospective_id=retrospective_id,
            user_id=current_user.id,
            session_id=session_id,
            session_type='4ls_input',
            current_category='liked',
            is_active=True,
            is_completed=False
        )
        db.add(new_session)
        db.flush()
        
        # Add welcome message
        welcome_msg = ChatMessage(
            session_id=new_session.id,
            content=f"Welcome {current_user.full_name}! Let's start our retrospective. We'll go through 4 categories: What you Liked, Learned, Lacked, and Longed For. Let's begin with what you LIKED about this sprint. What went well?",
            message_type='assistant',
            current_category='liked',
            ai_model='gpt-4'
        )
        db.add(welcome_msg)
        db.commit()
        
        return {
            "session_id": session_id,
            "message": "4Ls chat session started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Start 4Ls chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start chat: {str(e)}")


@router.get("/link/by-retro/{retrospective_id}")
async def get_or_create_session_link(
    retrospective_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return a session link for the given retrospective, creating a session if needed."""
    # Verify retrospective exists and is at/after scheduled start
    retro = db.query(Retrospective).filter(Retrospective.id == retrospective_id).first()
    if not retro:
        raise HTTPException(status_code=404, detail="Retrospective not found")

    # Verify user is participant
    participant = db.query(RetrospectiveParticipant).filter(
        RetrospectiveParticipant.retrospective_id == retrospective_id,
        RetrospectiveParticipant.user_id == current_user.id
    ).first()
    if not participant:
        raise HTTPException(status_code=403, detail="You are not a participant in this retrospective")

    # Find existing active session
    session = db.query(ChatSession).filter(
        ChatSession.retrospective_id == retrospective_id,
        ChatSession.user_id == current_user.id,
        ChatSession.is_active == True
    ).first()

    if not session:
        import secrets
        session_id_str = secrets.token_urlsafe(16)
        session = ChatSession(
            retrospective_id=retrospective_id,
            user_id=current_user.id,
            session_id=session_id_str,
            session_type='4ls_input',
            current_category='liked',
            is_active=True,
            is_completed=False
        )
        db.add(session)
        db.flush()

        welcome_msg = ChatMessage(
            session_id=session.id,
            content=f"Welcome {current_user.full_name}! Let's start our retrospective with what you LIKED.",
            message_type='assistant',
            current_category='liked',
            ai_model='gpt-4'
        )
        db.add(welcome_msg)
        db.commit()

    # Return URL to retrospective with code instead of yodaai-app
    url = f"{settings.APP_URL}/retrospective/{retro.code}"
    return {"session_id": session.session_id, "url": url, "code": retro.code}


@router.get("/email-link/{retrospective_id}/{user_id}")
async def get_email_session_link(
    retrospective_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Public endpoint for email links - creates session and returns direct chat URL."""
    # Verify retrospective exists and is at/after scheduled start
    retro = db.query(Retrospective).filter(Retrospective.id == retrospective_id).first()
    if not retro:
        raise HTTPException(status_code=404, detail="Retrospective not found")

    # Verify user exists and is participant
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    participant = db.query(RetrospectiveParticipant).filter(
        RetrospectiveParticipant.retrospective_id == retrospective_id,
        RetrospectiveParticipant.user_id == user_id
    ).first()
    if not participant:
        raise HTTPException(status_code=403, detail="User is not a participant in this retrospective")

    # Find or create session
    session = db.query(ChatSession).filter(
        ChatSession.retrospective_id == retrospective_id,
        ChatSession.user_id == user_id,
        ChatSession.is_active == True
    ).first()

    if not session:
        import secrets
        session_id_str = secrets.token_urlsafe(16)
        session = ChatSession(
            retrospective_id=retrospective_id,
            user_id=user_id,
            session_id=session_id_str,
            session_type='4ls_input',
            current_category='liked',
            is_active=True,
            is_completed=False
        )
        db.add(session)
        db.flush()

        welcome_msg = ChatMessage(
            session_id=session.id,
            content=f"Welcome {user.full_name}! Let's start our retrospective with what you LIKED.",
            message_type='assistant',
            current_category='liked',
            ai_model='gpt-4'
        )
        db.add(welcome_msg)
        db.commit()

    # Return direct URL to retrospective with code instead of yodaai-app
    chat_url = f"{settings.APP_URL}/retrospective/{retro.code}"
    return {"redirect_url": chat_url}


@router.get("/{session_id}")
async def get_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat session with messages and progress
    """
    try:
        # Get session
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get messages
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at).all()
        
        # Calculate progress
        categories_completed = session.categories_completed or {
            "liked": False,
            "learned": False,
            "lacked": False,
            "longed_for": False
        }
        
        all_completed = all([
            categories_completed.get('liked', False),
            categories_completed.get('learned', False),
            categories_completed.get('lacked', False),
            categories_completed.get('longed_for', False)
        ])
        progress = ProgressOverview(
            liked=categories_completed.get('liked', False),
            learned=categories_completed.get('learned', False),
            lacked=categories_completed.get('lacked', False),
            longed_for=categories_completed.get('longed_for', False),
            all_completed=all_completed
        )
        
        message_responses = [
            ChatMessageResponse(
                id=msg.id,
                content=msg.content,
                message_type=msg.message_type,
                created_at=msg.created_at,
                current_category=msg.current_category
            )
            for msg in messages
        ]
        
        return ChatSessionResponse(
            session_id=session.session_id,
            retrospective_id=session.retrospective_id,
            current_category=session.current_category,
            progress=progress,
            messages=message_responses
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get chat session error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch session: {str(e)}")


class MessageRequest(BaseModel):
    message: str


@router.post("/{session_id}/message")
async def send_message(
    session_id: str,
    message_data: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message in the chat and get AI response
    """
    try:
        # Get session
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.is_completed:
            raise HTTPException(status_code=400, detail="Session already completed")
        
        # Save user message
        user_msg = ChatMessage(
            session_id=session.id,
            content=message_data.message,
            message_type='user',
            current_category=session.current_category
        )
        db.add(user_msg)
        db.flush()
        
        # Extract and save response
        response_content = message_data.message
        
        # Save as retrospective response
        retro_response = RetrospectiveResponse(
            retrospective_id=session.retrospective_id,
            user_id=current_user.id,
            chat_session_id=session.id,
            category=session.current_category,
            content=response_content
        )
        db.add(retro_response)
        
        # Get AI response using OpenAI
        conversation_history = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at).all()
        
        conversation_messages = []
        for msg in conversation_history:
            role = "assistant" if msg.message_type == "assistant" else "user"
            conversation_messages.append({"role": role, "content": msg.content})
        
        # Call AI layer (OpenAI wrapped + token logging)
        try:
            ai = AIClient()
            ai_content, usage = generate_fourls_reply(
                ai=ai,
                current_category=session.current_category,
                conversation_messages=conversation_messages,
                endpoint_name="fourls_chat.message",
            )
            tokens_used = usage.get("total_tokens") or 0
        except Exception as ai_error:
            print(f"AI API error: {ai_error}")
            ai_content = "Thank you for sharing! Tell me more about that."
            tokens_used = 0
        
        # Post-process to enforce at most one question per reply
        if ai_content and ai_content.count('?') > 1:
            first_q_idx = ai_content.find('?')
            if first_q_idx != -1:
                ai_content = ai_content[:first_q_idx + 1]

        # Check if AI wants to move to next category (heuristic)
        move_to_next = any(phrase in ai_content.lower() for phrase in [
            "move on", "next category", "let's talk about", "now let's",
            "what did you learn", "what you learned", "learned about",
            "what did you lack", "what you lacked", "lacked in",
            "what did you long", "what you longed", "longed for",
            "explore the", "move to", "transition to", "shift to"
        ])

        # Enforce at least two user responses in the current category before moving
        user_responses_in_current = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id,
            ChatMessage.message_type == 'user',
            ChatMessage.current_category == session.current_category
        ).count()
        if user_responses_in_current < 2:
            move_to_next = False
        
        new_category = session.current_category
        categories_completed = session.categories_completed or {
            "liked": False, "learned": False, "lacked": False, "longed_for": False
        }
        
        if move_to_next:
            categories_completed[session.current_category] = True
            
            category_order = ['liked', 'learned', 'lacked', 'longed_for']
            current_index = category_order.index(session.current_category)
            
            if current_index < len(category_order) - 1:
                new_category = category_order[current_index + 1]
            else:
                # All categories covered; keep session open but mark participant progress
                participant = db.query(RetrospectiveParticipant).filter(
                    RetrospectiveParticipant.retrospective_id == session.retrospective_id,
                    RetrospectiveParticipant.user_id == current_user.id
                ).first()
                if participant:
                    participant.completed_input = True
        
        # Update session
        session.current_category = new_category
        session.categories_completed = categories_completed
        session.last_activity_at = datetime.now(timezone.utc)
        
        # Save AI message
        ai_msg = ChatMessage(
            session_id=session.id,
            content=ai_content,
            message_type='assistant',
            current_category=new_category,
            ai_model='gpt-4',
            ai_tokens_used=tokens_used
        )
        db.add(ai_msg)
        db.commit()
        
        # Calculate progress
        all_completed = all([
            categories_completed.get('liked', False),
            categories_completed.get('learned', False),
            categories_completed.get('lacked', False),
            categories_completed.get('longed_for', False)
        ])
        progress = ProgressOverview(
            liked=categories_completed.get('liked', False),
            learned=categories_completed.get('learned', False),
            lacked=categories_completed.get('lacked', False),
            longed_for=categories_completed.get('longed_for', False),
            all_completed=all_completed
        )
        
        return {
            "message": ai_content,
            "current_category": new_category,
            "progress": progress,
            "is_completed": all_completed
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Send message error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.post("/{session_id}/complete")
async def complete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark session as completed
    """
    try:
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.is_completed = True
        session.completed_at = datetime.now(timezone.utc)
        session.is_active = False
        
        # Mark participant as having completed input
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == session.retrospective_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if participant:
            participant.completed_input = True
        
        db.commit()
        
        return {"message": "Session completed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Complete session error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")

