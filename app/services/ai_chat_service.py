"""
AI chat service for managing chat sessions and AI interactions
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from app.models.ai_chat import ChatSession, ChatMessage
from app.models.retrospective import Retrospective, RetrospectiveResponse
from app.schemas.ai_chat import ChatSessionCreate, ChatRequest
from app.services.enhanced_ai_service import EnhancedAIService
from app.services.firebase_service import FirebaseService


class AIChatService:
    """Service for AI chat management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = EnhancedAIService()
        # Initialize Firestore helper for chat-only storage
        try:
            self.firebase = FirebaseService()
        except Exception:
            self.firebase = None
    
    def create_chat_session(self, session_data: ChatSessionCreate, user_id: int) -> ChatSession:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        # If Firestore is enabled, create session there (chat-only migration)
        if getattr(self, "firebase", None) and self.firebase.enabled:
            session_doc = {
                "session_id": session_id,
                "retrospective_id": session_data.retrospective_id,
                "user_id": user_id,
                "session_type": session_data.session_type,
                "current_step": session_data.current_step,
                "context": session_data.context or {},
                "is_active": True,
                "created_at": datetime.utcnow().isoformat()
            }
            created = self.firebase.create_chat_session(session_id, session_doc)
            # Save a welcome message in Firestore
            welcome = {
                "content": self._get_welcome_message(session_data.session_type, session_data.current_step),
                "message_type": "ai",
                "ai_model": "system",
                "ai_confidence": 100,
                "created_at": datetime.utcnow().isoformat()
            }
            self.firebase.save_message(session_id, welcome)

            # Return a lightweight ChatSession-like object
            cs = ChatSession(
                session_id=session_id,
                retrospective_id=session_data.retrospective_id,
                user_id=user_id,
                session_type=session_data.session_type,
                current_step=session_data.current_step,
                context=session_data.context
            )
            return cs

        # Fallback to SQLAlchemy
        chat_session = ChatSession(
            session_id=session_id,
            retrospective_id=session_data.retrospective_id,
            user_id=user_id,
            session_type=session_data.session_type,
            current_step=session_data.current_step,
            context=session_data.context
        )

        self.db.add(chat_session)
        self.db.commit()
        self.db.refresh(chat_session)

        # Add welcome message
        welcome_message = ChatMessage(
            session_id=chat_session.id,
            content=self._get_welcome_message(session_data.session_type, session_data.current_step),
            message_type="ai",
            ai_model="gpt-4",
            ai_confidence=100
        )

        self.db.add(welcome_message)
        self.db.commit()

        return chat_session
    
    def _has_project_context(self, user_id: int, retrospective_id: Optional[int] = None) -> bool:
        """Check if user has project context (team membership or uploaded documents)"""
        # Check if user is part of any team
        from app.models.team import Team, TeamMember
        team_membership = self.db.query(TeamMember).filter(
            TeamMember.user_id == user_id
        ).first()
        
        if team_membership:
            return True
        
        # Check if user has uploaded documents
        from app.models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if user and hasattr(user, 'uploaded_documents') and user.uploaded_documents:
            return True
        
        # For demo purposes, allow if user has any retrospective
        if retrospective_id:
            retrospective = self.db.query(Retrospective).filter(
                Retrospective.id == retrospective_id
            ).first()
            if retrospective:
                return True
        
        return False
    
    def _get_project_context(self, user_id: int, retrospective_id: Optional[int] = None) -> Optional[str]:
        """Get project context for the user"""
        try:
            # Get team information
            from app.models.team import Team, TeamMember
            team_membership = self.db.query(TeamMember).filter(
                TeamMember.user_id == user_id
            ).first()
            
            if team_membership:
                team = self.db.query(Team).filter(Team.id == team_membership.team_id).first()
                if team:
                    return f"Team: {team.name}, Role: {team_membership.role}"
            
            # Get retrospective context
            if retrospective_id:
                retrospective = self.db.query(Retrospective).filter(
                    Retrospective.id == retrospective_id
                ).first()
                if retrospective:
                    return f"Retrospective: {retrospective.title or 'Sprint Retrospective'}"
            
            return None
        except Exception as e:
            print(f"Error getting project context: {e}")
            return None
    
    def _get_uploaded_documents(self, user_id: int) -> Optional[str]:
        """Get uploaded documents content for the user"""
        try:
            from app.models.user import User
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and hasattr(user, 'uploaded_documents') and user.uploaded_documents:
                # In a real implementation, you would read the actual document content
                # For now, return a placeholder
                return f"User has uploaded {len(user.uploaded_documents)} documents"
            return None
        except Exception as e:
            print(f"Error getting uploaded documents: {e}")
            return None
    
    def get_user_sessions(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        retrospective_id: Optional[int] = None
    ) -> List[ChatSession]:
        """Get user's chat sessions"""
        # If Firestore enabled, get sessions from there
        if getattr(self, "firebase", None) and self.firebase.enabled:
            sessions = self.firebase.get_sessions_for_user(user_id)
            # Convert to ChatSession objects minimally
            result = []
            for s in sessions[skip: skip + limit]:
                cs = ChatSession(
                    session_id=s.get("session_id") or s.get("id"),
                    retrospective_id=s.get("retrospective_id"),
                    user_id=s.get("user_id"),
                    session_type=s.get("session_type"),
                    current_step=s.get("current_step"),
                    context=s.get("context")
                )
                result.append(cs)
            return result

        query = self.db.query(ChatSession).filter(ChatSession.user_id == user_id)
        
        if retrospective_id:
            query = query.filter(ChatSession.retrospective_id == retrospective_id)
        
        return query.offset(skip).limit(limit).all()
    
    def get_chat_session(self, session_id: str, user_id: int) -> Optional[ChatSession]:
        """Get a specific chat session"""
        # Check Firestore first
        if getattr(self, "firebase", None) and self.firebase.enabled:
            s = self.firebase.get_session(session_id)
            if not s:
                return None
            # Ensure user matches
            if s.get("user_id") != user_id:
                return None
            return ChatSession(
                session_id=s.get("session_id") or s.get("id"),
                retrospective_id=s.get("retrospective_id"),
                user_id=s.get("user_id"),
                session_type=s.get("session_type"),
                current_step=s.get("current_step"),
                context=s.get("context")
            )

        return self.db.query(ChatSession).filter(
            and_(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            )
        ).first()
    
    def get_chat_messages(self, session_id: str, skip: int = 0, limit: int = 100) -> List[ChatMessage]:
        """Get messages from a chat session"""
        # If Firestore enabled, fetch messages from Firestore
        if getattr(self, "firebase", None) and self.firebase.enabled:
            msgs = self.firebase.get_messages(session_id, limit=limit)
            result = []
            for m in msgs[skip: skip + limit]:
                cm = ChatMessage(
                    session_id=0,
                    content=m.get("content"),
                    message_type=m.get("message_type"),
                    ai_model=m.get("ai_model"),
                    ai_confidence=m.get("ai_confidence"),
                    ai_metadata=m.get("ai_metadata"),
                    follow_up_questions=m.get("follow_up_questions")
                )
                result.append(cm)
            return result

        session = self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            return []
        
        return self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).offset(skip).limit(limit).all()
    
    async def send_message(self, session_id: str, message_content: str, user_id: int) -> ChatMessage:
        """Send a message and get AI response"""
        session = self.get_chat_session(session_id, user_id)
        if not session:
            raise ValueError("Chat session not found")
        
        # Check if user has project context or is part of a team
        if not self._has_project_context(user_id, session.retrospective_id):
            # Return a message asking user to upload project or join team
            context_message = ChatMessage(
                session_id=session.id,
                content="Hi there! I'd love to help with your retrospective! To provide the most relevant insights, please upload project documents or ensure you're part of a team. You can do this through the onboarding section or team management. This will help me understand your project context better!",
                message_type="ai",
                ai_model="system",
                ai_confidence=100,
                ai_metadata={"type": "context_required"}
            )
            self.db.add(context_message)
            self.db.commit()
            self.db.refresh(context_message)
            return context_message
        
        # Save user message (Firestore preferred)
        if getattr(self, "firebase", None) and self.firebase.enabled:
            user_msg = {
                "content": message_content,
                "message_type": "user",
                "created_at": datetime.utcnow().isoformat()
            }
            self.firebase.save_message(session.session_id, user_msg)
        else:
            user_message = ChatMessage(
                session_id=session.id,
                content=message_content,
                message_type="user"
            )
            self.db.add(user_message)
            self.db.commit()
            self.db.refresh(user_message)
        
        # Get chat history for context
        chat_history = self._get_chat_history(session.id)
        
        # Get project context and uploaded documents
        project_context = self._get_project_context(user_id, session.retrospective_id)
        uploaded_documents = self._get_uploaded_documents(user_id)
        
        # Generate AI response using enhanced service
        ai_response = await self.ai_service.generate_retrospective_response(
            user_message=message_content,
            current_step=session.current_step or "liked",
            chat_history=chat_history,
            project_context=project_context,
            uploaded_documents=uploaded_documents
        )
        
        # Save AI response (Firestore preferred)
        ai_msg_payload = {
            "content": ai_response["response"],
            "message_type": "ai",
            "ai_model": ai_response["metadata"].get("model", "gpt-4"),
            "ai_confidence": ai_response["confidence"],
            "ai_metadata": ai_response["metadata"],
            "follow_up_questions": ai_response["follow_up_questions"],
            "created_at": datetime.utcnow().isoformat()
        }

        if getattr(self, "firebase", None) and self.firebase.enabled:
            self.firebase.save_message(session.session_id, ai_msg_payload)
            # Update session context in Firestore if needed
            if ai_response["follow_up_questions"]:
                self.firebase.update_chat_session(session.session_id, {"context.last_follow_up_questions": ai_response["follow_up_questions"]})
            # Return a lightweight ChatMessage-like object
            ai_msg = ChatMessage(
                session_id=0,
                content=ai_response["response"],
                message_type="ai",
                ai_model=ai_response["metadata"].get("model", "gpt-4"),
                ai_confidence=ai_response["confidence"],
                ai_metadata=ai_response["metadata"],
                follow_up_questions=ai_response["follow_up_questions"]
            )
            return ai_msg

        # SQLAlchemy path
        ai_message = ChatMessage(
            session_id=session.id,
            content=ai_response["response"],
            message_type="ai",
            ai_model=ai_response["metadata"].get("model", "gpt-4"),
            ai_confidence=ai_response["confidence"],
            ai_metadata=ai_response["metadata"],
            follow_up_questions=ai_response["follow_up_questions"]
        )
        
        self.db.add(ai_message)
        
        # Update session context if needed
        if ai_response["follow_up_questions"]:
            if not session.context:
                session.context = {}
            session.context["last_follow_up_questions"] = ai_response["follow_up_questions"]
        
        self.db.commit()
        self.db.refresh(ai_message)
        
        return ai_message
    
    def end_chat_session(self, session_id: str, user_id: int) -> bool:
        """End a chat session"""
        # If Firestore enabled, update the session doc
        if getattr(self, "firebase", None) and self.firebase.enabled:
            s = self.firebase.get_session(session_id)
            if not s or s.get("user_id") != user_id:
                return False
            return self.firebase.update_chat_session(session_id, {"is_active": False, "ended_at": datetime.utcnow().isoformat()})

        session = self.get_chat_session(session_id, user_id)
        if not session:
            return False
        
        session.is_active = False
        session.ended_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    async def analyze_retrospective(self, retrospective_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Analyze retrospective data and generate insights"""
        # Get retrospective
        retrospective = self.db.query(Retrospective).filter(
            and_(
                Retrospective.id == retrospective_id,
                Retrospective.created_by == user_id
            )
        ).first()
        
        if not retrospective:
            return None
        
        # Get all responses
        responses = self.db.query(RetrospectiveResponse).filter(
            RetrospectiveResponse.retrospective_id == retrospective_id
        ).all()
        
        # Convert to format expected by AI service
        response_data = []
        for response in responses:
            response_data.append({
                "liked": response.liked,
                "learned": response.learned,
                "lacked": response.lacked,
                "longed_for": response.longed_for
            })
        
        # Analyze with AI
        analysis = await self.ai_service.analyze_retrospective_patterns(response_data)
        
        # Generate action items
        action_items = await self.ai_service.generate_action_items({
            "liked": [r.liked for r in responses if r.liked],
            "learned": [r.learned for r in responses if r.learned],
            "lacked": [r.lacked for r in responses if r.lacked],
            "longed_for": [r.longed_for for r in responses if r.longed_for]
        })
        
        return {
            "retrospective_id": retrospective_id,
            "analysis": analysis,
            "suggested_action_items": action_items,
            "response_count": len(responses)
        }
    
    def _get_chat_history(self, session_id: int) -> List[Dict]:
        """Get chat history for a session"""
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
        
        return [
            {
                "type": msg.message_type,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    
    def _get_welcome_message(self, session_type: str, current_step: Optional[str]) -> str:
        """Get appropriate welcome message based on session type"""
        if session_type == "retrospective":
            if current_step == "liked":
                return "Hi there! Welcome to your retrospective! I'm YodaAI, your AI assistant. Let's start with what you **Liked** about this sprint. What went well that you'd like to continue? 💚"
            elif current_step == "learned":
                return "Great! Now let's talk about what you **Learned** during this sprint. What new insights or knowledge did you gain? 🎓"
            elif current_step == "lacked":
                return "Now let's discuss what **Lacked** or didn't go well. What challenges did you face? ⚠️"
            elif current_step == "longed_for":
                return "Finally, what do you **Long For**? What would you like to see happen differently in future sprints? ⭐"
            else:
                return "Hi there! Welcome to your retrospective! I'm YodaAI, your AI assistant. I'll guide you through the 4Ls framework to help your team reflect and improve. Let's begin! 🚀"
        else:
            return "Hello! I'm YodaAI, your AI assistant for agile retrospectives. How can I help you today? 🤖"
