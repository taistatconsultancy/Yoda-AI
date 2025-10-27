"""
4Ls AI Chat with Dynamic Progress Tracking
Handles: Liked, Learned, Lacked, Longed For
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import os
import json
from openai import OpenAI

from app.database.database import get_db
from app.models.retrospective_new import (
    Retrospective, ChatSession, ChatMessage, RetrospectiveResponse,
    RetrospectiveParticipant
)
from app.models.user import User
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/fourls-chat", tags=["4ls-chat"])

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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

@router.post("/start")
async def start_4ls_chat(
    retrospective_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new 4Ls chat session
    """
    try:
        # Verify user is participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retrospective_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="You are not a participant in this retrospective")
        
        # Check if session already exists
        existing_session = db.query(ChatSession).filter(
            ChatSession.retrospective_id == retrospective_id,
            ChatSession.user_id == current_user.id,
            ChatSession.is_active == True
        ).first()
        
        if existing_session:
            # Return existing session
            return {
                "session_id": existing_session.session_id,
                "message": "Resuming existing session"
            }
        
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
        
        progress = ProgressOverview(
            liked=categories_completed.get('liked', False),
            learned=categories_completed.get('learned', False),
            lacked=categories_completed.get('lacked', False),
            longed_for=categories_completed.get('longed_for', False),
            all_completed=session.is_completed
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
        
        messages_for_ai = [
            {"role": "system", "content": f"""You are YodaAI, a facilitator for agile retrospectives. You are currently guiding a team member through the 4Ls: Liked, Learned, Lacked, Longed For. 
            
Current category: {session.current_category.upper()}

Your role:
1. Acknowledge their response
2. Ask ONE follow-up question if needed for clarity (keep it brief)
3. After 1-2 responses in a category, thank them and EXPLICITLY transition to the next category using phrases like:
   - "Now let's move to what you LEARNED"
   - "Let's talk about what you LACKED"
   - "Now, what did you LONG FOR"
4. Categories order: liked → learned → lacked → longed_for

Be conversational, encouraging, and concise. Always use the category name when transitioning."""}
        ]
        
        for msg in conversation_history:
            role = "assistant" if msg.message_type == "assistant" else "user"
            messages_for_ai.append({"role": role, "content": msg.content})
        
        # Call OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages_for_ai,
                temperature=0.7,
                max_tokens=300
            )
            
            ai_content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
        except Exception as ai_error:
            print(f"OpenAI API error: {ai_error}")
            # Fallback response
            ai_content = "Thank you for sharing! Tell me more about that."
            tokens_used = 0
        
        # Check if AI wants to move to next category (improved heuristic)
        move_to_next = any(phrase in ai_content.lower() for phrase in [
            "move on", "next category", "let's talk about", "now let's",
            "what did you learn", "what you learned", "learned about",
            "what did you lack", "what you lacked", "lacked in",
            "what did you long", "what you longed", "longed for",
            "explore the", "move to", "transition to", "shift to"
        ])
        
        new_category = session.current_category
        categories_completed = session.categories_completed or {
            "liked": False, "learned": False, "lacked": False, "longed_for": False
        }
        
        if move_to_next:
            # Mark current category as complete
            categories_completed[session.current_category] = True
            
            # Move to next category
            category_order = ['liked', 'learned', 'lacked', 'longed_for']
            current_index = category_order.index(session.current_category)
            
            if current_index < len(category_order) - 1:
                new_category = category_order[current_index + 1]
            else:
                # All categories done
                session.is_completed = True
                participant = db.query(RetrospectiveParticipant).filter(
                    RetrospectiveParticipant.retrospective_id == session.retrospective_id,
                    RetrospectiveParticipant.user_id == current_user.id
                ).first()
                if participant:
                    participant.completed_input = True
        
        # Update session
        session.current_category = new_category
        session.categories_completed = categories_completed
        session.last_activity_at = datetime.utcnow()
        
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
        progress = ProgressOverview(
            liked=categories_completed.get('liked', False),
            learned=categories_completed.get('learned', False),
            lacked=categories_completed.get('lacked', False),
            longed_for=categories_completed.get('longed_for', False),
            all_completed=session.is_completed
        )
        
        return {
            "message": ai_content,
            "current_category": new_category,
            "progress": progress,
            "is_completed": session.is_completed
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
        session.completed_at = datetime.utcnow()
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

