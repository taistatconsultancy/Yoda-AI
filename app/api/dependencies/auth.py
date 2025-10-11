"""
Authentication dependency for FastAPI routes
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import get_db
from app.models.user import User
from app.services.firebase_auth import verify_firebase_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Resolve the current authenticated user from a Bearer token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Firebase-only verification
    decoded = verify_firebase_token(token)
    email: Optional[str] = decoded.get("email")
    if email is None:
        raise credentials_exception
    # Upsert user record based on Firebase UID/email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            username=decoded.get("uid") or email.split("@")[0],
            full_name=decoded.get("name"),
            provider="firebase",
            provider_id=decoded.get("uid"),
            is_verified=decoded.get("email_verified", False),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    if user is None:
        raise credentials_exception
    return user


