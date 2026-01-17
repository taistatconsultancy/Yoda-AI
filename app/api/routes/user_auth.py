"""
User authentication routes - Email/Password authentication with database storage
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database.database import get_db
from app.models.user import User
from app.models.email_verification import EmailVerificationToken
from app.services.email_service import email_service
from pydantic import BaseModel, EmailStr
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from datetime import timezone
from app.core.config import settings
from typing import Optional
import secrets

router = APIRouter()


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    full_name: str  # Required: first and last name


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response"""
    id: int
    email: str
    username: str
    full_name: str
    email_verified: bool
    default_role: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str
    user: UserResponse


class RegistrationResponse(BaseModel):
    """Registration response when email verification is required"""
    message: str
    email: str
    requires_verification: bool = True


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    try:
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=RegistrationResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password
    Stores user in Neon database
    Returns success response indicating email verification is required
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create username from email
        username = user_data.email.split('@')[0]
        
        # Check if username exists, make it unique
        base_username = username
        counter = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user (not verified yet)
        new_user = User(
            email=user_data.email,
            username=username,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            email_verified=False,  # Requires email verification
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate verification token
        from app.services.email_service import EmailService
        from app.models.email_verification import EmailVerificationToken
        
        email_service = EmailService()
        verification_token = email_service.generate_verification_token()
        
        # Create verification token record
        token_record = EmailVerificationToken(
            user_id=new_user.id,
            token=verification_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=1)  # 24 hours
        )
        db.add(token_record)
        db.commit()
        
        # Generate verification link
        base_url = settings.APP_URL
        verification_link = f"{base_url}/api/v1/user-auth/verify-email?token={verification_token}"
        
        # Send verification email
        email_sent = email_service.send_verification_email(
            to_email=new_user.email,
            verification_link=verification_link,
            full_name=new_user.full_name
        )
        
        if email_sent:
            print(f"✅ Verification email sent to: {new_user.email}")
        else:
            print(f"⚠️ Failed to send verification email. Token: {verification_link}")
            print(f"Verification link (check console): {verification_link}")
        
        # Return success response indicating email verification required
        return RegistrationResponse(
            message="Registration successful! Please check your email to verify your account before logging in.",
            email=new_user.email,
            requires_verification=True
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    Authenticates against Neon database
    """
    try:
        # Find user
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=401, 
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=400,
                detail="Account is inactive"
            )
        
        # Check email verification
        if not user.email_verified:
            raise HTTPException(
                status_code=403,
                detail="Please verify your email address before logging in. Check your inbox for the verification email."
            )
        
        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                email_verified=user.email_verified,
                default_role=user.default_role,
                country_name=user.country_name,
                company_name=user.company_name
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post("/demo-login", response_model=TokenResponse)
async def demo_login(db: Session = Depends(get_db)):
    """
    Create or login as demo user
    """
    # Check if demo user exists
    demo_user = db.query(User).filter(User.email == "demo@yodaai.com").first()
    
    if not demo_user:
        # Create demo user
        demo_user = User(
            email="demo@yodaai.com",
            username="demo_user",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
            email_verified=True,  # Auto-verify demo user
            is_active=True,
            default_role="facilitator",
            last_login_at=func.now()
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(demo_user.id), "email": demo_user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=demo_user.id,
            email=demo_user.email,
            username=demo_user.username,
            full_name=demo_user.full_name,
            email_verified=demo_user.email_verified,
            default_role=demo_user.default_role,
            country_name=demo_user.country_name,
            company_name=demo_user.company_name
        )
    )


@router.get("/verify-email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify user email address using token from email
    """
    try:
        # Find verification token
        token_record = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.token == token,
            EmailVerificationToken.used_at.is_(None)
        ).first()
        
        if not token_record:
            raise HTTPException(status_code=400, detail="Invalid or already used verification token")
        
        # Check if expired - use timezone-aware datetime
        now = datetime.now(timezone.utc)
        if token_record.expires_at < now:
            raise HTTPException(status_code=400, detail="Verification token has expired")
        
        # Mark token as used
        token_record.used_at = now
        
        # Update user email_verified status
        user = db.query(User).filter(User.id == token_record.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.email_verified = True
        user.email_verified_at = now
        
        # Commit changes
        db.commit()
        
        # Return HTML page with success message
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email Verified - YodaAI</title>
            <style>
                body {{ font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
                .container {{ background: white; padding: 40px; border-radius: 15px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.2); max-width: 500px; }}
                .icon {{ font-size: 64px; margin-bottom: 20px; }}
                h1 {{ color: #667eea; margin-bottom: 10px; }}
                p {{ color: #666; font-size: 16px; line-height: 1.6; }}
                .button {{ display: inline-block; margin-top: 20px; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .button:hover {{ background: #5568d3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">✅</div>
                <h1>Email Verified Successfully!</h1>
                <p>Your email address has been verified. You can now access all features of YodaAI!</p>
                <p><strong>Welcome to YodaAI, {user.full_name}!</strong></p>
                <a href="{settings.APP_URL}/yodaai-app" class="button">Go to YodaAI App</a>
            </div>
        </body>
        </html>
        """
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Verification error: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.get("/verify-token")
async def verify_token(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify JWT token and return user info
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            email_verified=user.email_verified,
            default_role=user.default_role,
            country_name=user.country_name,
            company_name=user.company_name
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

