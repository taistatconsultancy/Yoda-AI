"""
Voting System for Theme Groups
Each member gets 10 votes to allocate
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database.database import get_db
from app.models.retrospective_new import (
    Retrospective, ThemeGroup, VotingSession, VoteAllocation,
    RetrospectiveParticipant, DiscussionTopic
)
from app.models.user import User
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/voting", tags=["voting"])


# Pydantic Models
class VoteRequest(BaseModel):
    theme_group_id: int
    votes: int  # Number of votes to allocate


class BatchVoteRequest(BaseModel):
    """Bulk vote submission"""
    allocations: List[VoteRequest]  # List of theme_id and votes pairs


class ThemeVoteSummary(BaseModel):
    theme_id: int
    theme_title: str
    theme_description: str
    total_votes: int
    my_votes: int = 0
    rank: int = None


class VotingStatus(BaseModel):
    voting_session_id: int
    votes_per_member: int
    votes_used: int
    votes_remaining: int
    theme_votes: List[ThemeVoteSummary]
    can_vote: bool
    all_participants_voted: bool = False
    participants_who_voted: int = 0
    total_participants: int = 0


# ============================================================================
# VOTING ENDPOINTS
# ============================================================================

@router.post("/{retro_id}/start")
async def start_voting(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start voting session (facilitator only)
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        if retro.facilitator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only facilitator can start voting")
        
        # Check if voting already exists
        existing_session = db.query(VotingSession).filter(
            VotingSession.retrospective_id == retro_id,
            VotingSession.is_active == True
        ).first()
        
        if existing_session:
            return {"message": "Voting session already active", "session_id": existing_session.id}
        
        # Create voting session
        new_session = VotingSession(
            retrospective_id=retro_id,
            votes_per_member=10,
            min_votes_to_discuss=3,
            is_active=True
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return {
            "message": "Voting session started",
            "session_id": new_session.id,
            "votes_per_member": 10
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Start voting error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start voting: {str(e)}")


@router.get("/{retro_id}/status")
async def get_voting_status(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current voting status
    """
    try:
        # Verify participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not a participant")
        
        # Get voting session
        session = db.query(VotingSession).filter(
            VotingSession.retrospective_id == retro_id,
            VotingSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="No active voting session")
        
        # Calculate votes used by current user
        user_votes = db.query(func.sum(VoteAllocation.votes_allocated)).filter(
            VoteAllocation.voting_session_id == session.id,
            VoteAllocation.user_id == current_user.id
        ).scalar() or 0
        
        # Get all themes with votes
        themes = db.query(ThemeGroup).filter(
            ThemeGroup.retrospective_id == retro_id
        ).all()
        
        theme_summaries = []
        for theme in themes:
            # Total votes for this theme
            total_votes = db.query(func.sum(VoteAllocation.votes_allocated)).filter(
                VoteAllocation.voting_session_id == session.id,
                VoteAllocation.theme_group_id == theme.id
            ).scalar() or 0
            
            # My votes for this theme
            my_votes = db.query(VoteAllocation.votes_allocated).filter(
                VoteAllocation.voting_session_id == session.id,
                VoteAllocation.theme_group_id == theme.id,
                VoteAllocation.user_id == current_user.id
            ).scalar() or 0
            
            theme_summaries.append(ThemeVoteSummary(
                theme_id=theme.id,
                theme_title=theme.title,
                theme_description=theme.description,
                total_votes=total_votes,
                my_votes=my_votes
            ))
        
        # Sort by total votes and assign ranks
        theme_summaries.sort(key=lambda x: x.total_votes, reverse=True)
        for idx, theme in enumerate(theme_summaries, 1):
            theme.rank = idx
        
        # Get participant voting stats
        total_participants = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id
        ).count()
        
        participants_who_voted = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.completed_voting == True
        ).count()
        
        all_participants_voted = participants_who_voted >= total_participants
        
        return VotingStatus(
            voting_session_id=session.id,
            votes_per_member=session.votes_per_member,
            votes_used=user_votes,
            votes_remaining=session.votes_per_member - user_votes,
            theme_votes=theme_summaries,
            can_vote=user_votes < session.votes_per_member,
            all_participants_voted=all_participants_voted,
            participants_who_voted=participants_who_voted,
            total_participants=total_participants
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get voting status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch voting status: {str(e)}")


@router.post("/{retro_id}/vote")
async def cast_vote(
    retro_id: int,
    vote_req: VoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cast votes for a theme
    """
    try:
        # Get voting session
        session = db.query(VotingSession).filter(
            VotingSession.retrospective_id == retro_id,
            VotingSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="No active voting session")
        
        # Verify participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not a participant")
        
        # Verify theme exists
        theme = db.query(ThemeGroup).filter(
            ThemeGroup.id == vote_req.theme_group_id,
            ThemeGroup.retrospective_id == retro_id
        ).first()
        
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        
        # Calculate total votes used
        current_votes = db.query(func.sum(VoteAllocation.votes_allocated)).filter(
            VoteAllocation.voting_session_id == session.id,
            VoteAllocation.user_id == current_user.id
        ).scalar() or 0
        
        # Check if user has enough votes
        if current_votes + vote_req.votes > session.votes_per_member:
            remaining = session.votes_per_member - current_votes
            raise HTTPException(
                status_code=400, 
                detail=f"Not enough votes. You have {remaining} votes remaining"
            )
        
        if vote_req.votes < 0:
            raise HTTPException(status_code=400, detail="Votes must be positive")
        
        # Check if already voted for this theme
        existing_vote = db.query(VoteAllocation).filter(
            VoteAllocation.voting_session_id == session.id,
            VoteAllocation.theme_group_id == vote_req.theme_group_id,
            VoteAllocation.user_id == current_user.id
        ).first()
        
        if existing_vote:
            # Update existing vote
            existing_vote.votes_allocated += vote_req.votes
        else:
            # Create new vote allocation
            new_vote = VoteAllocation(
                voting_session_id=session.id,
                theme_group_id=vote_req.theme_group_id,
                user_id=current_user.id,
                votes_allocated=vote_req.votes
            )
            db.add(new_vote)
        
        db.commit()
        
        # Calculate new total
        new_total = current_votes + vote_req.votes
        
        return {
            "message": f"Allocated {vote_req.votes} votes to {theme.title}",
            "votes_used": new_total,
            "votes_remaining": session.votes_per_member - new_total
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Cast vote error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cast vote: {str(e)}")


@router.post("/{retro_id}/submit-votes")
async def submit_votes_batch(
    retro_id: int,
    batch_req: BatchVoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit all votes at once (batch)
    """
    try:
        # Get voting session
        session = db.query(VotingSession).filter(
            VotingSession.retrospective_id == retro_id,
            VotingSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="No active voting session")
        
        # Verify participant
        participant = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id,
            RetrospectiveParticipant.user_id == current_user.id
        ).first()
        
        if not participant:
            raise HTTPException(status_code=403, detail="Not a participant")
        
        # Calculate total votes to be allocated
        total_votes = sum(alloc.votes for alloc in batch_req.allocations)
        
        # Check if exceeds votes_per_member
        if total_votes > session.votes_per_member:
            raise HTTPException(
                status_code=400,
                detail=f"Total votes ({total_votes}) exceeds maximum ({session.votes_per_member})"
            )
        
        # Check for negative votes
        if any(alloc.votes < 0 for alloc in batch_req.allocations):
            raise HTTPException(status_code=400, detail="Votes must be non-negative")
        
        # Get all themes to verify they exist
        theme_ids = {alloc.theme_group_id for alloc in batch_req.allocations}
        themes = db.query(ThemeGroup).filter(
            ThemeGroup.id.in_(theme_ids),
            ThemeGroup.retrospective_id == retro_id
        ).all()
        
        if len(themes) != len(theme_ids):
            raise HTTPException(status_code=404, detail="Some themes not found")
        
        # Delete existing votes for this user in this session
        db.query(VoteAllocation).filter(
            VoteAllocation.voting_session_id == session.id,
            VoteAllocation.user_id == current_user.id
        ).delete()
        
        # Create new vote allocations
        for alloc in batch_req.allocations:
            new_vote = VoteAllocation(
                voting_session_id=session.id,
                theme_group_id=alloc.theme_group_id,
                user_id=current_user.id,
                votes_allocated=alloc.votes
            )
            db.add(new_vote)
        
        # Mark this participant as having completed voting
        if participant:
            participant.completed_voting = True
        
        db.commit()
        
        return {
            "message": f"Successfully submitted {total_votes} votes",
            "votes_allocated": total_votes,
            "votes_remaining": session.votes_per_member - total_votes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Submit votes batch error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit votes: {str(e)}")


@router.post("/{retro_id}/finalize")
async def finalize_voting(
    retro_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Finalize voting and create discussion topics (facilitator only)
    """
    try:
        retro = db.query(Retrospective).filter(Retrospective.id == retro_id).first()
        
        if not retro:
            raise HTTPException(status_code=404, detail="Retrospective not found")
        
        if retro.facilitator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only facilitator can finalize voting")
        
        session = db.query(VotingSession).filter(
            VotingSession.retrospective_id == retro_id,
            VotingSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="No active voting session")
        
        # End voting session
        session.is_active = False
        session.ended_at = datetime.utcnow()
        
        # Get top voted themes
        theme_votes = db.query(
            ThemeGroup,
            func.sum(VoteAllocation.votes_allocated).label('total_votes')
        ).join(
            VoteAllocation, ThemeGroup.id == VoteAllocation.theme_group_id
        ).filter(
            VoteAllocation.voting_session_id == session.id
        ).group_by(ThemeGroup.id).order_by(
            func.sum(VoteAllocation.votes_allocated).desc()
        ).all()
        
        # Create discussion topics for themes with minimum votes
        discussion_topics_created = []
        rank = 1
        
        for theme, total_votes in theme_votes:
            if total_votes >= session.min_votes_to_discuss:
                # Check if topic already exists
                existing_topic = db.query(DiscussionTopic).filter(
                    DiscussionTopic.retrospective_id == retro_id,
                    DiscussionTopic.theme_group_id == theme.id
                ).first()
                
                if not existing_topic:
                    topic = DiscussionTopic(
                        retrospective_id=retro_id,
                        theme_group_id=theme.id,
                        total_votes=total_votes,
                        rank=rank,
                        time_allocated_minutes=15,
                        is_discussed=False
                    )
                    db.add(topic)
                    discussion_topics_created.append(theme.title)
                    rank += 1
        
        # Mark voting as complete for all participants
        participants = db.query(RetrospectiveParticipant).filter(
            RetrospectiveParticipant.retrospective_id == retro_id
        ).all()
        
        for p in participants:
            p.completed_voting = True
        
        db.commit()
        
        return {
            "message": "Voting finalized",
            "discussion_topics_created": len(discussion_topics_created),
            "topics": discussion_topics_created
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Finalize voting error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to finalize voting: {str(e)}")
