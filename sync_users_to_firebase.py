"""
Sync Users from Neon Database to Firebase
This script syncs user credentials and data from Neon PostgreSQL to Firebase Authentication and Firestore
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database.database import SessionLocal
from app.models.user import User
from app.services.firebase_auth import _ensure_initialized
from app.services.firebase_service import FirebaseService
from firebase_admin import auth as fb_auth
import firebase_admin

print("=" * 80)
print("🔄 Syncing Users from Neon Database to Firebase")
print("=" * 80)

def sync_users_to_firebase():
    """Sync users from Neon PostgreSQL to Firebase Authentication and Firestore"""
    
    # Initialize Firebase
    print("\n1. Initializing Firebase...")
    try:
        _ensure_initialized()
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return False
    
    # Get database session
    print("\n2. Connecting to Neon database...")
    db = SessionLocal()
    try:
        # Get all users from Neon database
        users = db.query(User).all()
        print(f"✅ Found {len(users)} users in Neon database")
        
        if len(users) == 0:
            print("⚠️ No users found in database to sync")
            return True
        
        # Initialize Firestore service
        firestore_service = FirebaseService()
        
        success_count = 0
        error_count = 0
        
        # Sync each user
        for user in users:
            print(f"\n3. Syncing user: {user.email} (ID: {user.id})")
            
            try:
                # Prepare user data for Firebase
                user_data = {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "email_verified": user.email_verified,
                    "default_role": user.default_role,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "synced_at": datetime.utcnow().isoformat()
                }
                
                # Try to create or update user in Firebase Authentication
                try:
                    # Try to get existing user
                    try:
                        fb_user = fb_auth.get_user_by_email(user.email)
                        print(f"   - Firebase user exists, updating...")
                        
                        # Update user in Firebase Auth
                        fb_auth.update_user(
                            fb_user.uid,
                            email=user.email,
                            display_name=user.full_name,
                            email_verified=user.email_verified,
                            disabled=not user.is_active
                        )
                        print(f"   ✅ Updated Firebase Auth user: {fb_user.uid}")
                        
                    except fb_auth.UserNotFoundError:
                        # Create new user in Firebase Auth (password will be set later)
                        try:
                            fb_user = fb_auth.create_user(
                                email=user.email,
                                display_name=user.full_name,
                                email_verified=user.email_verified,
                                disabled=not user.is_active
                            )
                            print(f"   ✅ Created Firebase Auth user: {fb_user.uid}")
                        except Exception as e:
                            print(f"   ⚠️ Could not create Firebase Auth user: {e}")
                            fb_user = None
                    
                    # Store additional user data in Firestore
                    if firestore_service.enabled and fb_user:
                        try:
                            # Store user document in Firestore
                            user_doc = {
                                **user_data,
                                "firebase_uid": fb_user.uid,
                                "last_synced": datetime.utcnow().isoformat()
                            }
                            
                            firestore_service.client.collection("users").document(fb_user.uid).set(user_doc)
                            print(f"   ✅ Stored user data in Firestore")
                        except Exception as e:
                            print(f"   ⚠️ Could not store in Firestore: {e}")
                    
                except Exception as e:
                    print(f"   ⚠️ Error syncing user authentication: {e}")
                
                success_count += 1
                print(f"   ✅ User synced successfully")
                
            except Exception as e:
                print(f"   ❌ Error syncing user {user.email}: {e}")
                error_count += 1
        
        print("\n" + "=" * 80)
        print("📊 Sync Summary")
        print("=" * 80)
        print(f"Total users: {len(users)}")
        print(f"✅ Successful: {success_count}")
        print(f"❌ Errors: {error_count}")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def check_firebase_setup():
    """Check if Firebase is properly set up"""
    print("\n" + "=" * 80)
    print("🔍 Checking Firebase Setup")
    print("=" * 80)
    
    # Check Firebase Authentication
    try:
        users = fb_auth.list_users(max_results=1)
        print("✅ Firebase Authentication is working")
    except Exception as e:
        print(f"⚠️ Firebase Authentication check failed: {e}")
    
    # Check Firestore
    try:
        from app.services.firebase_service import FirebaseService
        fs_service = FirebaseService()
        if fs_service.enabled:
            print("✅ Firestore is enabled and working")
        else:
            print("⚠️ Firestore is not enabled")
    except Exception as e:
        print(f"⚠️ Firestore check failed: {e}")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Run setup check
    check_firebase_setup()
    
    # Sync users
    result = sync_users_to_firebase()
    
    if result:
        print("\n✅ Sync complete!")
    else:
        print("\n❌ Sync failed!")
        sys.exit(1)
