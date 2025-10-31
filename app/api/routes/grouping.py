"""
AI-Powered Theme Grouping
Groups retrospective responses into themes using OpenAI
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
    Retrospective, RetrospectiveResponse, ThemeGroup, RetrospectiveParticipant
)
from app.models.user import User
from app.models.workspace import WorkspaceMember
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/grouping", tags=["grouping"])

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def can_edit_grouping(db: Session, current_user: User, retro: Retrospective) -> bool:
    """Check if user can edit grouping - facilitator, Scrum Master, or Project Manager"""
    # Check if user is facilitator
    if retro.facilitator_id == current_user.id:
        return True
    
    # Check workspace role
    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == retro.workspace_id,
        WorkspaceMember.user_id == current_user.id,
        WorkspaceMember.is_active == True
    ).first()
    
    if membership and membership.role in ['Scrum Master', 'Project Manager']:
        return True
    
    return False


# Pydantic Models
class ResponseWithAuthor(BaseModel):
    id: int
    content: str
    category: str
    author_name: str
    author_id: int
    theme_group_id: int = None
    
    class Config:
        from_attributes = True


class ThemeGroupResponse(BaseModel):
    id: int
    title: str
    description: str
    primary_category: str
    response_count: int
    responses: List[ResponseWithAuthor]
    ai_generated: bool
    
    class Config:
        from_attributes = True


class GroupingResult(BaseModel):
    theme_groups: List[ThemeGroupResponse]
    ungrouped_responses: List[ResponseWithAuthor]
    total_responses: int
    total_groups: int


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_fallback_grouping(responses):
    """
    Create a simple category-based grouping when AI fails
    """
    category_map = {
        'liked': 'Things We Liked',
        'learned': 'Things We Learned',
        'lacked': 'Things We Lacked',
        'longed_for': 'Things We Longed For'
    }
    
    category_desc = {
        'liked': 'Positive aspects and successes from the sprint',
        'learned': 'New knowledge and skills gained',
        'lacked': 'Areas where we fell short or needed improvement',
        'longed_for': 'Desires and wishes for future sprints'
    }
    
    themes = []
    response_groups = {}
    
    # Group responses by category
    for resp, user in responses:
        cat = resp.category
        if cat not in response_groups:
            response_groups[cat] = []
        response_groups[cat].append(resp.id)
    
    # Create theme for each category that has responses
    for category, response_ids in response_groups.items():
        themes.append({
            'title': category_map.get(category, category.title()),
            'description': category_desc.get(category, f'Responses in the {category} category'),
            'primary_category': category,
            'response_ids': response_ids
        })
    
    return themes


# ============================================================================
# GROUPING ENDPOINTS
# ============================================================================

@router.post("/{retro_id}/generate")
async def generate_ai_grouping(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered theme grouping for retrospective responses
    """
    try:
        # Verify user is facilitator or participant
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant and retro.facilitator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all responses
        responses = db.query(RetrospectiveResponse, User).join(
            User, RetrospectiveResponse.user_id == User.id
        ).filter(
            RetrospectiveResponse.retrospective_id == retro_id
        ).all()
        
        if not responses:
            raise HTTPException(status_code=400, detail="No responses to group yet. Please complete the 4Ls input phase first.")
        
        # Prepare data for OpenAI
        responses_text = []
        for resp, user in responses:
            responses_text.append({
                "id": resp.id,
                "category": resp.category,
                "content": resp.content,
                "author": user.full_name
            })
        
        # Create prompt for OpenAI
        prompt = f"""You are analyzing retrospective responses from a team. Group these responses into meaningful themes.

Responses:
{json.dumps(responses_text, indent=2)}

Please:
1. Identify 3-7 main themes across all responses
2. Group related responses together
3. Create a clear, concise title for each theme (max 6 words)
4. Write a 1-2 sentence description for each theme
5. Assign a primary category (liked, learned, lacked, longed_for) to each theme

IMPORTANT: Return ONLY a valid JSON array, nothing else. Use this exact structure:
[
    {{
        "title": "Theme title",
        "description": "Brief description",
        "primary_category": "liked",
        "response_ids": [1, 2, 3]
    }}
]

Only include response IDs that actually belong to each theme. Some responses may not fit any theme (leave them ungrouped).
Do not include any explanatory text before or after the JSON.
"""
        
        try:
            # Call OpenAI (using gpt-4 without json_object mode since it's not supported)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing team retrospectives and identifying patterns and themes. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
            
            # Clean the response - remove markdown code blocks if present
            ai_response = ai_response.strip()
            if ai_response.startswith('```'):
                # Remove markdown code blocks
                lines = ai_response.split('\n')
                ai_response = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            
            grouping_data = json.loads(ai_response)
            
            # Handle both direct array and object with 'themes' key
            themes = grouping_data if isinstance(grouping_data, list) else grouping_data.get('themes', [])
            
        except json.JSONDecodeError as json_error:
            print(f"JSON parsing error: {json_error}")
            print(f"AI Response was: {ai_response}")
            # Create a simple fallback grouping by category
            print("Using fallback: grouping by category")
            themes = create_fallback_grouping(responses)
        except Exception as ai_error:
            print(f"OpenAI grouping error: {ai_error}")
            # Create a simple fallback grouping by category
            print("Using fallback: grouping by category")
            themes = create_fallback_grouping(responses)
        
        # Clear existing theme groups for this retro
        existing_groups = db.query(ThemeGroup).filter(
            ThemeGroup.retrospective_id == retro_id
        ).all()
        for group in existing_groups:
            db.delete(group)
        db.flush()
        
        # Create theme groups
        created_groups = []
        for theme_data in themes:
            new_group = ThemeGroup(
                retrospective_id=retro_id,
                title=theme_data['title'],
                description=theme_data.get('description', ''),
                primary_category=theme_data.get('primary_category', 'liked'),
                ai_generated=True,
                ai_confidence=0.85,
                display_order=len(created_groups)
            )
            db.add(new_group)
            db.flush()
            
            # Assign responses to this group
            response_ids = theme_data.get('response_ids', [])
            for resp_id in response_ids:
                resp = db.query(RetrospectiveResponse).filter(
                    RetrospectiveResponse.id == resp_id
                ).first()
                if resp:
                    resp.theme_group_id = new_group.id
            
            created_groups.append(new_group)
        
        db.commit()
        
        return {
            "message": f"Created {len(created_groups)} theme groups",
            "groups_created": len(created_groups),
            "responses_processed": len(responses)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Generate grouping error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate grouping: {str(e)}")


@router.get("/{retro_id}")
async def get_grouping_results(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get grouping results with theme groups and ungrouped responses
    """
    try:
        # Verify access
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not participant and retro.facilitator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all theme groups
        theme_groups = db.query(ThemeGroup).filter(
            ThemeGroup.retrospective_id == retro_id
        ).order_by(ThemeGroup.display_order).all()
        
        theme_group_responses = []
        for group in theme_groups:
            # Get responses for this group
            group_responses = db.query(RetrospectiveResponse, User).join(
                User, RetrospectiveResponse.user_id == User.id
            ).filter(
                RetrospectiveResponse.theme_group_id == group.id
            ).all()
            
            responses_list = [
                ResponseWithAuthor(
                    id=resp.id,
                    content=resp.content,
                    category=resp.category,
                    author_name=user.full_name,
                    author_id=user.id,
                    theme_group_id=group.id
                )
                for resp, user in group_responses
            ]
            
            theme_group_responses.append(ThemeGroupResponse(
                id=group.id,
                title=group.title,
                description=group.description,
                primary_category=group.primary_category,
                response_count=len(responses_list),
                responses=responses_list,
                ai_generated=group.ai_generated
            ))
        
        # Get ungrouped responses
        ungrouped = db.query(RetrospectiveResponse, User).join(
            User, RetrospectiveResponse.user_id == User.id
        ).filter(
            RetrospectiveResponse.retrospective_id == retro_id,
            RetrospectiveResponse.theme_group_id.is_(None)
        ).all()
        
        ungrouped_list = [
            ResponseWithAuthor(
                id=resp.id,
                content=resp.content,
                category=resp.category,
                author_name=user.full_name,
                author_id=user.id,
                theme_group_id=None
            )
            for resp, user in ungrouped
        ]
        
        total_responses = db.query(RetrospectiveResponse).filter(
            RetrospectiveResponse.retrospective_id == retro_id
        ).count()
        
        return GroupingResult(
            theme_groups=theme_group_responses,
            ungrouped_responses=ungrouped_list,
            total_responses=total_responses,
            total_groups=len(theme_groups)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get grouping error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch grouping: {str(e)}")


@router.delete("/theme/{theme_id}")
async def delete_theme_group(
    theme_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a theme group (facilitator only)
    """
    try:
        theme = db.query(ThemeGroup).filter(ThemeGroup.id == theme_id).first()
        
        if not theme:
            raise HTTPException(status_code=404, detail="Theme group not found")
        
        retro = db.query(Retrospective).filter(
            Retrospective.id == theme.retrospective_id
        ).first()
        
        if not can_edit_grouping(db, current_user, retro):
            raise HTTPException(status_code=403, detail="Only facilitator, Scrum Master, or Project Manager can delete themes")
        
        # Ungroup all responses in this theme
        responses = db.query(RetrospectiveResponse).filter(
            RetrospectiveResponse.theme_group_id == theme_id
        ).all()
        
        for resp in responses:
            resp.theme_group_id = None
        
        # Delete theme
        db.delete(theme)
        db.commit()
        
        return {"message": "Theme group deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Delete theme error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete theme: {str(e)}")


@router.post("/response/{response_id}/move/{theme_id}")
async def move_response_to_theme(
    response_id: int,
    theme_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Move a response to a different theme group
    """
    try:
        response = db.query(RetrospectiveResponse).filter(
            RetrospectiveResponse.id == response_id
        ).first()
        
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        
        theme = db.query(ThemeGroup).filter(ThemeGroup.id == theme_id).first()
        
        if not theme:
            raise HTTPException(status_code=404, detail="Theme group not found")
        
        retro = db.query(Retrospective).filter(
            Retrospective.id == response.retrospective_id
        ).first()
        
        if not can_edit_grouping(db, current_user, retro):
            raise HTTPException(status_code=403, detail="Only facilitator, Scrum Master, or Project Manager can move responses")
        
        response.theme_group_id = theme_id
        db.commit()
        
        return {"message": "Response moved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Move response error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to move response: {str(e)}")


@router.post("/{retro_id}/themes")
async def create_theme(
    retro_id: int,
    theme_data: dict,  # {category, title, description}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new theme manually (facilitator only)
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        if not can_edit_grouping(db, current_user, retro):
            raise HTTPException(status_code=403, detail="Only facilitator, Scrum Master, or Project Manager can create themes")
        
        # Get max display_order for this retrospective
        max_order = db.query(ThemeGroup.display_order).filter(
            ThemeGroup.retrospective_id == retro_id
        ).order_by(ThemeGroup.display_order.desc()).first()
        
        new_order = (max_order[0] + 1) if max_order else 0
        
        new_theme = ThemeGroup(
            retrospective_id=retro_id,
            title=theme_data.get('title'),
            description=theme_data.get('description', ''),
            primary_category=theme_data.get('category', 'liked'),
            display_order=new_order,
            ai_generated=False
        )
        
        db.add(new_theme)
        db.commit()
        db.refresh(new_theme)
        
        return ThemeGroupResponse(
            id=new_theme.id,
            title=new_theme.title,
            description=new_theme.description,
            primary_category=new_theme.primary_category,
            response_count=0,
            responses=[],
            ai_generated=new_theme.ai_generated
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Create theme error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create theme: {str(e)}")


@router.put("/theme/{theme_id}")
async def update_theme(
    theme_id: int,
    theme_data: dict,  # {title, description}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a theme (facilitator only)
    """
    try:
        theme = db.query(ThemeGroup).filter(ThemeGroup.id == theme_id).first()
        
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        
        retro = db.query(Retrospective).filter(Retrospective.id == theme.retrospective_id).first()
        
        if not can_edit_grouping(db, current_user, retro):
            raise HTTPException(status_code=403, detail="Only facilitator, Scrum Master, or Project Manager can update themes")
        
        if 'title' in theme_data:
            theme.title = theme_data['title']
        if 'description' in theme_data:
            theme.description = theme_data['description']
        
        db.commit()
        db.refresh(theme)
        
        return {"message": "Theme updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Update theme error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update theme: {str(e)}")


@router.post("/{retro_id}/themes/reorder")
async def reorder_themes(
    retro_id: int,
    order_data: dict,  # {category, theme_ids: [1,2,3]}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update theme display order (facilitator only)
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        if not can_edit_grouping(db, current_user, retro):
            raise HTTPException(status_code=403, detail="Only facilitator, Scrum Master, or Project Manager can reorder themes")
        
        theme_ids = order_data.get('theme_ids', [])
        category = order_data.get('category', 'liked')
        
        # Update display orders
        for index, theme_id in enumerate(theme_ids):
            theme = db.query(ThemeGroup).filter(
                ThemeGroup.id == theme_id,
                ThemeGroup.retrospective_id == retro_id,
                ThemeGroup.primary_category == category
            ).first()
            
            if theme:
                theme.display_order = index
        
        db.commit()
        
        return {"message": "Themes reordered successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Reorder themes error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reorder themes: {str(e)}")