"""
User lookup routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user


router = APIRouter()


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


