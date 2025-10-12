"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.api.dependencies.auth import get_current_user
from app.schemas.auth import UserResponse, UserLogin, UserRegister
from app.models.user import User
from passlib.context import CryptContext
import secrets
import jwt
from datetime import datetime, timedelta
import os

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password"""
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not pwd_context.verify(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Create JWT token
    secret_key = os.getenv("SECRET_KEY", "your-secret-key")
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(token_data, secret_key, algorithm="HS256")
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "displayName": user.full_name or user.username,
        "photoURL": None,
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register new user with email and password"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = pwd_context.hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        provider="local",
        is_active=True,
        is_verified=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create JWT token
    secret_key = os.getenv("SECRET_KEY", "your-secret-key")
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(token_data, secret_key, algorithm="HS256")
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "displayName": user.full_name or user.username,
        "photoURL": None,
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def me(current_user = Depends(get_current_user)):
    return UserResponse.from_orm(current_user)
