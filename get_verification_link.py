"""
Quick script to get verification link for a user
"""
import sys
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user import User
from app.models.email_verification import EmailVerificationToken
from app.core.config import settings

def get_verification_link(email: str):
    """Get verification link for a user"""
    db: Session = SessionLocal()
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return
        
        print(f"\n✅ User found: {user.full_name} ({user.email})")
        print(f"   Email verified: {user.email_verified}")
        
        # Find latest verification token
        token_record = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.used_at.is_(None)
        ).order_by(EmailVerificationToken.created_at.desc()).first()
        
        if not token_record:
            print(f"❌ No active verification token found for {email}")
            return
        
        # Generate verification link
        verification_link = f"{settings.APP_URL}/api/v1/user-auth/verify-email?token={token_record.token}"
        
        print(f"\n{'='*70}")
        print("EMAIL VERIFICATION LINK:")
        print(f"{'='*70}")
        print(f"\n{verification_link}\n")
        print(f"{'='*70}")
        print(f"\n✅ Copy this link and paste in your browser to verify {email}")
        print(f"   Token expires: {token_record.expires_at}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_verification_link.py <email>")
        print("Example: python get_verification_link.py marswriter649@gmail.com")
        sys.exit(1)
    
    email = sys.argv[1]
    get_verification_link(email)
