"""
Test Firebase connection
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("🔥 Testing Firebase Connection")
print("=" * 60)

# Test Firebase Admin SDK
print("\n1. Testing Firebase Admin SDK initialization...")
try:
    from app.services.firebase_auth import _ensure_initialized, verify_firebase_token
    _ensure_initialized()
    print("✅ Firebase Admin SDK initialized successfully!")
except Exception as e:
    print(f"❌ Firebase Admin SDK initialization failed: {e}")
    sys.exit(1)

# Test Firestore
print("\n2. Testing Firestore connection...")
try:
    from app.services.firebase_service import FirebaseService
    firebase_service = FirebaseService()
    
    if firebase_service.enabled:
        print("✅ Firestore connection successful!")
        
        # Test write to Firestore
        print("\n3. Testing Firestore write operation...")
        test_session_id = "test_session_123"
        test_data = {
            "user_id": 999,
            "retrospective_id": 1,
            "session_id": test_session_id,
            "session_type": "test",
            "created_at": "2025-01-01T00:00:00Z"
        }
        
        result = firebase_service.create_chat_session(test_session_id, test_data)
        if result:
            print(f"✅ Test data written to Firestore: {result}")
            
            # Test read from Firestore
            print("\n4. Testing Firestore read operation...")
            session = firebase_service.get_session(test_session_id)
            if session:
                print(f"✅ Test data read from Firestore: {session}")
                print(f"   - User ID: {session.get('user_id')}")
                print(f"   - Session Type: {session.get('session_type')}")
            else:
                print("⚠️ Could not read test data from Firestore")
        else:
            print("⚠️ Could not write test data to Firestore")
    else:
        print("⚠️ Firestore is not enabled (check credentials)")
        
except Exception as e:
    print(f"❌ Firestore connection failed: {e}")
    import traceback
    traceback.print_exc()

# Test Database connection
print("\n5. Testing Neon Database connection...")
try:
    from app.database.database import engine, test_connection
    from sqlalchemy import text
    
    result = test_connection()
    if result:
        print("✅ Neon Database connection successful!")
        
        # Test query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM users"))
            count = result.fetchone()[0]
            print(f"   - Users table exists with {count} record(s)")
    else:
        print("❌ Neon Database connection failed")
except Exception as e:
    print(f"❌ Neon Database connection error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ Firebase connection test complete!")
print("=" * 60)
