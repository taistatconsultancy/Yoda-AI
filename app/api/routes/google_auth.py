"""
Google OAuth authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
import httpx
import os
import jwt
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/google")
async def google_auth(token: str, db: Session = Depends(get_db)):
    """Authenticate with Google OAuth token"""
    try:
        # Verify Google token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v1/userinfo?access_token={token}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            google_user = response.json()
            
        # Check if user exists
        user = db.query(User).filter(User.email == google_user["email"]).first()
        
        if not user:
            # Create new user
            user = User(
                email=google_user["email"],
                username=google_user["email"].split("@")[0],
                full_name=google_user.get("name"),
                provider="google",
                provider_id=google_user["id"],
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
        jwt_token = jwt.encode(token_data, secret_key, algorithm="HS256")
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "displayName": user.full_name or user.username,
            "photoURL": google_user.get("picture"),
            "access_token": jwt_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {str(e)}"
        )
