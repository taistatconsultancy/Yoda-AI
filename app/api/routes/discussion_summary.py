"""
Discussion and Summary Generation
AI-facilitated discussion on top-voted themes + Sprint summaries
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List
from pydantic import BaseModel
from datetime import datetime
import os
import json
from openai import OpenAI

from app.database.database import get_db
from app.models.retrospective_new import (
    Retrospective, DiscussionTopic, DiscussionMessage, ThemeGroup,
    RetrospectiveParticipant, RetrospectiveResponse, DARecommendation,
    VotingSession, VoteAllocation
)
from app.models.action_item import ActionItem
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/discussion", tags=["discussion-summary"])


def get_openai_client():
    """Get OpenAI client with API key from settings"""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


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


class MessageRequest(BaseModel):
    message: str


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
    message_req: MessageRequest,
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
        
        # Check if this is the first message (discussion hasn't started yet)
        if not topic.discussion_started_at:
            topic.discussion_started_at = datetime.utcnow()
            topic.is_discussed = True
        
        # Save user message
        user_msg = DiscussionMessage(
            discussion_topic_id=topic_id,
            user_id=current_user.id,
            content=message_req.message,
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
            openai_client = get_openai_client()
            response = openai_client.chat.completions.create(
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


@router.post("/{retro_id}/chat")
async def general_discussion_chat(
    retro_id: int,
    message_req: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    General discussion chat for asking questions about themes and DA recommendations
    """
    try:
        # Verify participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not a participant")
        
        # Get topics and DA recommendations for context
        topics = db.query(DiscussionTopic, ThemeGroup).join(
            ThemeGroup, DiscussionTopic.theme_group_id == ThemeGroup.id
        ).filter(
            DiscussionTopic.retrospective_id == retro_id
        ).order_by(DiscussionTopic.total_votes.desc()).limit(5).all()
        
        # Get DA recommendations
        da_rec = db.query(DARecommendation).filter(
            DARecommendation.retrospective_id == retro_id
        ).first()
        
        # Build context
        themes_context = "\n".join([
            f"- {theme.title}: {theme.description} ({topic.total_votes} votes)"
            for topic, theme in topics
        ])
        
        da_context = da_rec.content if da_rec else "No DA recommendations generated yet."
        
        # Build AI prompt with context
        system_prompt = f"""You are YodaAI, helping teams understand their retrospective themes and Disciplined Agile recommendations.

Top Discussion Themes:
{themes_context}

Disciplined Agile Recommendations:
{da_context}

Your role:
1. Help clarify themes and their implications
2. Explain how DA recommendations apply to their situation
3. Suggest concrete implementation steps
4. Answer questions about agile practices

Be conversational, practical, and focused on action. Keep responses concise (2-3 sentences max)."""
        
        # Get AI response
        try:
            openai_client = get_openai_client()
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_req.message}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            ai_content = response.choices[0].message.content
            
        except Exception as ai_error:
            print(f"OpenAI general chat error: {ai_error}")
            ai_content = "Thank you for your question. Could you please rephrase it or ask about specific themes?"
        
        return {
            "message": ai_content,
            "type": "ai_assistant"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"General discussion chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


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
            print(f"Generating summary for retrospective {retro_id}")
            print(f"Data summary: {json.dumps(data_summary, indent=2)}")
            
            openai_client = get_openai_client()
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert agile coach analyzing retrospectives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            print(f"OpenAI response received")
            content = response.choices[0].message.content
            print(f"Response content: {content[:200]}...")
            
            summary_data = json.loads(content)
            
        except Exception as ai_error:
            import traceback
            print(f"OpenAI summary error: {ai_error}")
            print(f"Traceback: {traceback.format_exc()}")
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
        
        # Get voting tallies for all themes
        voting_results = []
        voting_session = db.query(VotingSession).filter(
            VotingSession.retrospective_id == retro_id
        ).order_by(VotingSession.created_at.desc()).first()
        
        if voting_session:
            themes = db.query(ThemeGroup).filter(
                ThemeGroup.retrospective_id == retro_id
            ).all()
            
            for theme in themes:
                total_votes = db.query(func.sum(VoteAllocation.votes_allocated)).filter(
                    VoteAllocation.voting_session_id == voting_session.id,
                    VoteAllocation.theme_group_id == theme.id
                ).scalar() or 0
                
                voting_results.append({
                    "theme_title": theme.title,
                    "theme_description": theme.description,
                    "total_votes": total_votes,
                    "category": theme.primary_category
                })
            
            # Sort by votes
            voting_results.sort(key=lambda x: x['total_votes'], reverse=True)
        
        return {
            "summary": retro.ai_summary,
            "achievements": insights.get('achievements', []),
            "challenges": insights.get('challenges', []),
            "recommendations": insights.get('recommendations', []),
            "sprint_name": retro.sprint_name,
            "generated_at": retro.updated_at,
            "voting_results": voting_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get summary error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch summary: {str(e)}")


# ============================================================================
# DA BROWSER RECOMMENDATIONS
# ============================================================================

@router.get("/{retro_id}/da-recommendations")
async def get_da_recommendations(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate DA Browser recommendations based on discussion topics
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
        
        # Get top themes for discussion
        topics = db.query(DiscussionTopic, ThemeGroup).join(
            ThemeGroup, DiscussionTopic.theme_group_id == ThemeGroup.id
        ).filter(
            DiscussionTopic.retrospective_id == retro_id
        ).order_by(DiscussionTopic.total_votes.desc()).limit(5).all()
        
        # Read disciplined_agile_scrape.md
        da_guide = ""
        try:
            da_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "disciplined_agile_scrape.md")
            with open(da_path, 'r', encoding='utf-8') as f:
                da_guide = f.read()[:5000]  # Limit to first 5000 chars
        except Exception as e:
            print(f"Could not read DA guide: {e}")
        
        # Build prompt for AI
        themes_text = "\n".join([
            f"- {theme.title}: {theme.description} (Votes: {topic.total_votes})"
            for topic, theme in topics
        ])
        
        prompt = f"""Based on the following themes from a team retrospective, provide specific Disciplined Agile recommendations.

Key Themes Discussed:
{themes_text}

Disciplined Agile Framework Overview:
{da_guide[:2000]}

Generate a concise 1-page summary with:
1. Specific DA practices that address these themes
2. Recommended workflow improvements
3. Tools and techniques to implement

IMPORTANT: Format your response using clear bullet points (- or •) for each recommendation. Use markdown-style formatting:
- **Category Name**: Description or header
  - Sub-point 1
  - Sub-point 2

Keep each bullet point concise and actionable. Structure the output in an organized, easy-to-read format."""
        
        # Check if DA recommendations already exist in database
        existing_da_rec = db.query(DARecommendation).filter(
            DARecommendation.retrospective_id == retro_id
        ).first()
        
        if existing_da_rec:
            return {
                "content": existing_da_rec.content
            }
        
        try:
            openai_client = get_openai_client()
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Disciplined Agile expert providing actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            recommendations = response.choices[0].message.content
            
            # Store DA recommendations in database
            da_rec = DARecommendation(
                retrospective_id=retro_id,
                content=recommendations,
                ai_model="gpt-4"
            )
            db.add(da_rec)
            db.commit()
            
        except Exception as ai_error:
            print(f"OpenAI DA recommendations error: {ai_error}")
            recommendations = "No specific recommendations available at this time. Please review the Disciplined Agile framework for guidance."
        
        return {
            "content": recommendations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get DA recommendations error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")


# ============================================================================
# PDF DOWNLOAD
# ============================================================================

@router.get("/{retro_id}/summary/pdf")
async def download_summary_pdf(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate and download summary as PDF
    """
    from fastapi.responses import Response
    
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
        
        # Get participants for listing
        participant_rows = db.query(RetrospectiveParticipant, User).join(
            User, RetrospectiveParticipant.user_id == User.id
        ).filter(
            RetrospectiveParticipant.retrospective_id == retro_id
        ).order_by(
            func.lower(func.coalesce(User.full_name, User.email, ''))
        ).all()
        
        # Get action items associated with this retrospective
        priority_order = case(
            [
                (ActionItem.priority == 'critical', 4),
                (ActionItem.priority == 'high', 3),
                (ActionItem.priority == 'medium', 2),
                (ActionItem.priority == 'low', 1),
            ],
            else_=0
        )
        
        action_items = db.query(ActionItem).filter(
            ActionItem.retrospective_id == retro_id
        ).order_by(
            ActionItem.status,
            priority_order.desc(),
            ActionItem.due_date.is_(None),
            ActionItem.due_date.asc()
        ).all()
        
        # Get DA recommendations and top themes
        da_rec = db.query(DARecommendation).filter(
            DARecommendation.retrospective_id == retro_id
        ).first()
        
        # Get top discussion topics
        topics = db.query(DiscussionTopic, ThemeGroup).join(
            ThemeGroup, DiscussionTopic.theme_group_id == ThemeGroup.id
        ).filter(
            DiscussionTopic.retrospective_id == retro_id
        ).order_by(DiscussionTopic.total_votes.desc()).limit(5).all()
        
        insights = retro.ai_insights or {}
        
        # Generate PDF using reportlab
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
            from reportlab.lib.units import inch
            import io
            from xml.sax.saxutils import escape as xml_escape
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=72)
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=20,
                alignment=1,  # Center alignment
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=12,
                spaceBefore=12,
            )
            subheading_style = ParagraphStyle(
                'SubHeading',
                parent=styles['Heading3'],
                fontSize=14,
                textColor=colors.HexColor('#4a5568'),
                spaceAfter=8,
            )
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
            )
            
            # Title
            elements.append(Paragraph(f"Retrospective Summary", title_style))
            elements.append(Paragraph(f"{retro.title or 'Team Retrospective'}", styles['Title']))
            if retro.sprint_name:
                elements.append(Paragraph(f"Sprint: {retro.sprint_name}", styles['Normal']))
            if retro.actual_start_time:
                elements.append(Paragraph(
                    f"Date: {retro.actual_start_time.strftime('%B %d, %Y')}", 
                    styles['Normal']
                ))
            elements.append(Spacer(1, 0.3*inch))
            
            # Top Themes for Discussion
            if topics:
                elements.append(Paragraph("Top Themes Discussed", heading_style))
                for i, (topic, theme) in enumerate(topics, 1):
                    elements.append(Paragraph(
                        f"{i}. {theme.title} ({topic.total_votes} votes)",
                        subheading_style
                    ))
                    if theme.description:
                        elements.append(Paragraph(theme.description, normal_style))
                    elements.append(Spacer(1, 0.1*inch))
                elements.append(Spacer(1, 0.2*inch))
            
            if participant_rows:
                elements.append(Paragraph("Participants", heading_style))
                participant_table_data = [["Name", "Email", "Voting Complete"]]
                for rp, user in participant_rows:
                    name = xml_escape(user.full_name or user.email or f"User {user.id}")
                    email = xml_escape(user.email or "—")
                    voting_complete = "Yes" if rp.completed_voting else "No"
                    participant_table_data.append([
                        Paragraph(name, normal_style),
                        Paragraph(email, normal_style),
                        Paragraph(voting_complete, normal_style)
                    ])
                participant_table = Table(
                    participant_table_data,
                    colWidths=[2.8*inch, 2.4*inch, 1.0*inch]
                )
                participant_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cbd5f5')),
                ]))
                elements.append(participant_table)
                elements.append(Spacer(1, 0.3*inch))
            
            elements.append(Paragraph("Action Items", heading_style))
            if action_items:
                action_table_data = [["Title", "Owner", "Status", "Due Date", "Progress"]]
                for item in action_items:
                    title_text = xml_escape(item.title or "Untitled action item")
                    assignee = "Unassigned"
                    if item.assignee:
                        assignee = item.assignee.full_name or item.assignee.email or f"User {item.assignee.id}"
                    assignee = xml_escape(assignee)
                    status_text = xml_escape((item.status or "pending").replace('_', ' ').title())
                    due_text = item.due_date.strftime('%b %d, %Y') if item.due_date else "—"
                    progress_text = f"{item.progress_percentage or 0}%"
                    action_table_data.append([
                        Paragraph(f"<b>{title_text}</b>", normal_style),
                        Paragraph(assignee, normal_style),
                        Paragraph(status_text, normal_style),
                        Paragraph(xml_escape(due_text), normal_style),
                        Paragraph(progress_text, normal_style)
                    ])
                action_table = Table(
                    action_table_data,
                    colWidths=[2.8*inch, 1.5*inch, 1.0*inch, 1.0*inch, 0.7*inch]
                )
                action_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4c51bf')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#edf2ff')]),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#d0d7f9')),
                ]))
                elements.append(action_table)
            else:
                elements.append(Paragraph("No action items were captured for this retrospective.", normal_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # Overall Assessment
            if retro.ai_summary:
                elements.append(PageBreak())
                elements.append(Paragraph("Overall Assessment", heading_style))
                elements.append(Paragraph(retro.ai_summary, normal_style))
                elements.append(Spacer(1, 0.3*inch))
            
            # Achievements
            achievements = insights.get('achievements', [])
            if achievements:
                elements.append(Paragraph("Key Achievements", heading_style))
                for achievement in achievements:
                    elements.append(Paragraph(f"✓ {achievement}", normal_style))
                elements.append(Spacer(1, 0.3*inch))
            
            # Challenges
            challenges = insights.get('challenges', [])
            if challenges:
                elements.append(Paragraph("Main Challenges", heading_style))
                for challenge in challenges:
                    elements.append(Paragraph(f"⚠ {challenge}", normal_style))
                elements.append(Spacer(1, 0.3*inch))
            
            # Disciplined Agile Recommendations (format bullets + bold)
            if da_rec and da_rec.content:
                elements.append(PageBreak())
                elements.append(Paragraph("Disciplined Agile Recommendations", heading_style))
                try:
                    import re
                    raw = da_rec.content or ""
                    # Convert **bold** to <b> for reportlab Paragraph
                    raw = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", raw)
                    # Split into lines and bullets
                    lines = [l.strip() for l in raw.splitlines() if l.strip()]
                    bullet_lines = []
                    for line in lines:
                        m = re.match(r"^[-•]\s*(.*)$", line)
                        if m:
                            bullet_lines.append(m.group(1))
                        else:
                            # Further split on ' - ' to extract sub-bullets
                            parts = [p.strip() for p in re.split(r"\s-\s", line) if p.strip()]
                            if len(parts) > 1:
                                bullet_lines.extend(parts)
                            else:
                                bullet_lines.append(line)
                    for blt in bullet_lines:
                        elements.append(Paragraph(f"• {blt}", normal_style))
                except Exception:
                    # Fallback to raw paragraph
                    elements.append(Paragraph(da_rec.content, normal_style))
                elements.append(Spacer(1, 0.3*inch))
            
            # Recommendations (if in insights)
            recommendations = insights.get('recommendations', [])
            if recommendations:
                elements.append(Paragraph("AI Suggested Action Ideas", heading_style))
                for recommendation in recommendations:
                    elements.append(Paragraph(f"→ {recommendation}", normal_style))
                elements.append(Spacer(1, 0.3*inch))
            
            # Build PDF
            doc.build(elements)
            
            # Get the value of the BytesIO buffer
            pdf = buffer.getvalue()
            buffer.close()
            
            # Return PDF
            return Response(
                content=pdf,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=retrospective_summary_{retro.code or retro_id}.pdf"
                }
            )
            
        except ImportError:
            raise HTTPException(
                status_code=500, 
                detail="PDF generation requires reportlab. Install with: pip install reportlab"
            )
        except Exception as pdf_error:
            print(f"PDF generation error: {pdf_error}")
            raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(pdf_error)}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Download summary PDF error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download PDF: {str(e)}")
