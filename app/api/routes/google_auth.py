from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.firebase_auth import verify_firebase_token
from app.database.database import SessionLocal
from app.models.user import User
from datetime import datetime
from jose import jwt
from app.core.config import settings

router = APIRouter()


class GoogleTokenRequest(BaseModel):
    id_token: str


def create_jwt_token(user_id: int, email: str):
    """Create JWT token for our API"""
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow().timestamp() + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/google")
async def google_signin(request: GoogleTokenRequest):
    """
    Sign in with Google Firebase ID token.
    Creates user in database if doesn't exist.
    """
    db = SessionLocal()
    
    try:
        # 1. Verify Firebase ID token
        decoded_token = verify_firebase_token(request.id_token)
        
        # 2. Extract user info
        firebase_uid = decoded_token['uid']
        email = decoded_token['email']
        display_name = decoded_token.get('name', email.split('@')[0])
        picture_url = decoded_token.get('picture')
        email_verified = decoded_token.get('email_verified', False)
        
        # 3. Check if user exists in database
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # 4. Create new user
            # Generate username from email
            username = email.split('@')[0]
            
            # Ensure unique username
            existing_username = db.query(User).filter(User.username == username).first()
            counter = 1
            while existing_username:
                username = f"{email.split('@')[0]}_{counter}"
                existing_username = db.query(User).filter(User.username == username).first()
                counter += 1
            
            # Create user
            user = User(
                email=email,
                username=username,
                full_name=display_name,
                profile_picture_url=picture_url,
                google_id=firebase_uid,
                email_verified=email_verified,
                email_verified_at=datetime.utcnow() if email_verified else None,
                is_active=True
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            print(f"✅ Created new user from Google: {email}")
        else:
            # 5. Update existing user
            user.google_id = firebase_uid
            user.email_verified = email_verified or user.email_verified
            if email_verified and not user.email_verified_at:
                user.email_verified_at = datetime.utcnow()
            user.profile_picture_url = picture_url or user.profile_picture_url
            user.last_login_at = datetime.utcnow()
            
            db.commit()
            
            print(f"✅ Updated existing user from Google: {email}")
        
        # 6. Create JWT token for our API
        access_token = create_jwt_token(user.id, user.email)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "profile_picture_url": user.profile_picture_url,
                "country_name": user.country_name,
                "company_name": user.company_name
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Google sign-in error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=401, detail="Invalid Google token")
    finally:
        db.close()
