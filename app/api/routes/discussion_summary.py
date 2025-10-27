"""
Discussion and Summary Generation
AI-facilitated discussion on top-voted themes + Sprint summaries
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import os
import json
from openai import OpenAI

from app.database.database import get_db
from app.models.retrospective_new import (
    Retrospective, DiscussionTopic, DiscussionMessage, ThemeGroup,
    RetrospectiveParticipant, RetrospectiveResponse
)
from app.models.user import User
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/discussion", tags=["discussion-summary"])

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Pydantic Models
class DiscussionTopicResponse(BaseModel):
    id: int
    theme_title: str
    theme_description: str
    total_votes: int
    rank: int
    is_discussed: bool
    
    class Config:
        from_attributes = True


class DiscussionMessageResponse(BaseModel):
    id: int
    content: str
    message_type: str
    author_name: str = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SprintSummary(BaseModel):
    retrospective_id: int
    sprint_name: str
    summary: str
    key_achievements: List[str]
    main_challenges: List[str]
    action_items_count: int
    generated_at: datetime


# ============================================================================
# DISCUSSION ENDPOINTS
# ============================================================================

@router.get("/{retro_id}/topics", response_model=List[DiscussionTopicResponse])
async def get_discussion_topics(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get discussion topics (top-voted themes)
    """
    try:
        # Verify participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not a participant")
        
        # Get topics
        topics = db.query(DiscussionTopic, ThemeGroup).join(
            ThemeGroup, DiscussionTopic.theme_group_id == ThemeGroup.id
        ).filter(
            DiscussionTopic.retrospective_id == retro_id
        ).order_by(DiscussionTopic.rank).all()
        
        return [
            DiscussionTopicResponse(
                id=topic.id,
                theme_title=theme.title,
                theme_description=theme.description,
                total_votes=topic.total_votes,
                rank=topic.rank,
                is_discussed=topic.is_discussed
            )
            for topic, theme in topics
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get discussion topics error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch topics: {str(e)}")


@router.post("/{topic_id}/message")
async def send_discussion_message(
    topic_id: int,
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message in discussion and get AI facilitation
    """
    try:
        topic = db.query(DiscussionTopic).filter(DiscussionTopic.id == topic_id).first()
        
        if not topic:
            raise HTTPException(status_code=404, detail="Discussion topic not found")
        
        # Verify participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == topic.retrospective_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not a participant")
        
        # Save user message
        user_msg = DiscussionMessage(
            discussion_topic_id=topic_id,
            user_id=current_user.id,
            content=message,
            message_type='user'
        )
        db.add(user_msg)
        db.flush()
        
        # Get theme details for context
        theme = db.query(ThemeGroup).filter(ThemeGroup.id == topic.theme_group_id).first()
        
        # Get conversation history
        history = db.query(DiscussionMessage, User).outerjoin(
            User, DiscussionMessage.user_id == User.id
        ).filter(
            DiscussionMessage.discussion_topic_id == topic_id
        ).order_by(DiscussionMessage.created_at).all()
        
        # Build AI messages
        messages_for_ai = [
            {"role": "system", "content": f"""You are YodaAI, facilitating a team discussion on the theme: "{theme.title}". 
            
Description: {theme.description}
Votes received: {topic.total_votes}

Your role:
1. Keep discussion focused and productive
2. Ask thought-provoking questions
3. Encourage participation from everyone
4. Help identify concrete action items
5. Summarize key points periodically

Be conversational, supportive, and concise (max 2-3 sentences)."""}
        ]
        
        for msg, user in history:
            if msg.message_type == 'user' and user:
                messages_for_ai.append({"role": "user", "content": f"{user.full_name}: {msg.content}"})
            elif msg.message_type == 'ai_facilitator':
                messages_for_ai.append({"role": "assistant", "content": msg.content})
        
        # Get AI response
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages_for_ai,
                temperature=0.7,
                max_tokens=200
            )
            
            ai_content = response.choices[0].message.content
            
        except Exception as ai_error:
            print(f"OpenAI discussion error: {ai_error}")
            ai_content = "Thank you for sharing. What do others think about this?"
        
        # Save AI response
        ai_msg = DiscussionMessage(
            discussion_topic_id=topic_id,
            user_id=None,
            content=ai_content,
            message_type='ai_facilitator',
            ai_model='gpt-4'
        )
        db.add(ai_msg)
        db.commit()
        
        return {
            "message": ai_content,
            "type": "ai_facilitator"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Send discussion message error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/{topic_id}/messages", response_model=List[DiscussionMessageResponse])
async def get_discussion_messages(
    topic_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages for a discussion topic
    """
    try:
        topic = db.query(DiscussionTopic).filter(DiscussionTopic.id == topic_id).first()
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Verify participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == topic.retrospective_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not a participant")
        
        # Get messages
        messages = db.query(DiscussionMessage, User).outerjoin(
            User, DiscussionMessage.user_id == User.id
        ).filter(
            DiscussionMessage.discussion_topic_id == topic_id
        ).order_by(DiscussionMessage.created_at).all()
        
        return [
            DiscussionMessageResponse(
                id=msg.id,
                content=msg.content,
                message_type=msg.message_type,
                author_name=user.full_name if user else "YodaAI",
                created_at=msg.created_at
            )
            for msg, user in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get discussion messages error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")


# ============================================================================
# SUMMARY GENERATION
# ============================================================================

@router.post("/{retro_id}/generate-summary")
async def generate_summary(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI summary for retrospective (facilitator only)
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        if retro.facilitator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only facilitator can generate summary")
        
        # Gather all retrospective data
        responses = db.query(RetrospectiveResponse, User).join(
            User, RetrospectiveResponse.user_id == User.id
        ).filter(
            RetrospectiveResponse.retrospective_id == retro_id
        ).all()
        
        themes = db.query(ThemeGroup).filter(
            ThemeGroup.retrospective_id == retro_id
        ).all()
        
        # Build data for AI
        data_summary = {
            "sprint_name": retro.sprint_name,
            "participants": db.query(RetrospectiveParticipant).filter(
                RetrospectiveParticipant.retrospective_id == retro_id
            ).count(),
            "liked": [r.content for r, u in responses if r.category == 'liked'],
            "learned": [r.content for r, u in responses if r.category == 'learned'],
            "lacked": [r.content for r, u in responses if r.category == 'lacked'],
            "longed_for": [r.content for r, u in responses if r.category == 'longed_for'],
            "themes": [{"title": t.title, "description": t.description} for t in themes]
        }
        
        # Generate summary with OpenAI
        prompt = f"""Analyze this sprint retrospective and create a comprehensive summary.

Sprint: {retro.sprint_name or 'Unnamed Sprint'}
Participants: {data_summary['participants']}

LIKED (What went well):
{json.dumps(data_summary['liked'], indent=2)}

LEARNED (What we learned):
{json.dumps(data_summary['learned'], indent=2)}

LACKED (What was missing):
{json.dumps(data_summary['lacked'], indent=2)}

LONGED FOR (What we want):
{json.dumps(data_summary['longed_for'], indent=2)}

KEY THEMES:
{json.dumps(data_summary['themes'], indent=2)}

Create a summary with:
1. Overall sprint assessment (2-3 sentences)
2. Top 3 achievements
3. Top 3 challenges
4. Key recommendations

Return JSON:
{{
    "summary": "Overall assessment...",
    "achievements": ["Achievement 1", "Achievement 2", "Achievement 3"],
    "challenges": ["Challenge 1", "Challenge 2", "Challenge 3"],
    "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
}}
"""
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert agile coach analyzing retrospectives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            summary_data = json.loads(response.choices[0].message.content)
            
        except Exception as ai_error:
            print(f"OpenAI summary error: {ai_error}")
            summary_data = {
                "summary": "Summary generation failed. Please review the retrospective data manually.",
                "achievements": [],
                "challenges": [],
                "recommendations": []
            }
        
        # Save summary to retrospective
        retro.ai_summary = summary_data.get('summary', '')
        retro.ai_insights = summary_data
        db.commit()
        
        return {
            "summary": summary_data.get('summary', ''),
            "achievements": summary_data.get('achievements', []),
            "challenges": summary_data.get('challenges', []),
            "recommendations": summary_data.get('recommendations', []),
            "sprint_name": retro.sprint_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Generate summary error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.get("/{retro_id}/summary")
async def get_summary(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get retrospective summary
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        # Verify participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not a participant")
        
        if not retro.ai_summary:
            raise HTTPException(status_code=404, detail="Summary not yet generated")
        
        insights = retro.ai_insights or {}
        
        return {
            "summary": retro.ai_summary,
            "achievements": insights.get('achievements', []),
            "challenges": insights.get('challenges', []),
            "recommendations": insights.get('recommendations', []),
            "sprint_name": retro.sprint_name,
            "generated_at": retro.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get summary error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")

