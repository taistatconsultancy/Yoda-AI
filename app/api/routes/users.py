"""
User lookup routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.database.database import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user


router = APIRouter()


class UserProfileUpdate(BaseModel):
    """User profile update request"""
    country_name: Optional[str] = None
    company_name: Optional[str] = None


@router.get("/lookup")
async def lookup_user(
    email: str = Query(..., description="Email address to lookup"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Look up an existing, verified, active user by email.
    Returns minimal public info if found; 404 otherwise.
    """
    # Normalize email
    normalized = email.strip().lower()

    user: Optional[User] = (
        db.query(User)
        .filter(User.email == normalized, User.email_verified.is_(True), User.is_active.is_(True))
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found or not verified")

    return {
        "id": user.id,
        "email": user.email,
        "displayName": user.full_name,
        "avatar": user.profile_picture_url,
        "email_verified": user.email_verified,
    }


@router.get("/me")
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get current user's profile information
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "country_name": current_user.country_name,
        "company_name": current_user.company_name,
        "email_verified": current_user.email_verified,
    }


@router.put("/me/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Update current user's profile (country and company)
    """
    if profile_data.country_name is not None:
        current_user.country_name = profile_data.country_name
    if profile_data.company_name is not None:
        current_user.company_name = profile_data.company_name
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "country_name": current_user.country_name,
        "company_name": current_user.company_name,
        "message": "Profile updated successfully"
    }

