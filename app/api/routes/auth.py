"""
Authentication routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.dependencies.auth import get_current_user
from app.schemas.auth import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def me(current_user = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)
