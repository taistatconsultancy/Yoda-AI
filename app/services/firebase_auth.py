"""
Firebase authentication: initialize Admin SDK and verify ID tokens.
"""

from typing import Optional, Dict, Any
import os
import json

import firebase_admin
from firebase_admin import auth as fb_auth, credentials

from app.core.config import settings


_app_initialized = False


def _ensure_initialized() -> None:
    global _app_initialized
    if _app_initialized:
        return

    # Initialize using service account JSON path or JSON content
    # Try multiple methods: credentials.json file, env vars, or application default
    try:
        cred: credentials.Base = None
        
        # Method 1: Try credentials.json file in project root
        if os.path.exists("credentials.json"):
            try:
                with open("credentials.json", "r") as f:
                    cred_info = json.load(f)
                    cred = credentials.Certificate(cred_info)
                    print("✅ Firebase initialized from credentials.json")
                    firebase_admin.initialize_app(cred)
                    _app_initialized = True
                    return
            except Exception as e:
                print(f"Warning: Could not load credentials.json: {e}")
        
        # Method 2: Try environment variables
        if settings.FIREBASE_PRIVATE_KEY and settings.FIREBASE_CLIENT_EMAIL and settings.FIREBASE_PROJECT_ID:
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": "dummy",
                "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": "dummy",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}",
            })
            print("✅ Firebase initialized from environment variables")
            firebase_admin.initialize_app(cred)
            _app_initialized = True
            return
        
        # Method 3: Application default credentials (for GCP environments)
        cred = credentials.ApplicationDefault()
        print("✅ Firebase initialized using application default credentials")
        firebase_admin.initialize_app(cred)
        _app_initialized = True
        
    except Exception as e:
        # Fallback to default app if already initialized elsewhere
        if not firebase_admin._apps:
            print(f"⚠️ Warning: Firebase initialization failed: {e}")
            print("⚠️ Firebase features will be unavailable - Google Sign-In disabled")
            _app_initialized = True  # Mark as initialized to prevent retries
            return
        _app_initialized = True


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """Verify a Firebase ID token and return the decoded payload."""
    _ensure_initialized()
    
    # Check if Firebase is actually available
    if not firebase_admin._apps:
        raise Exception("Firebase is not configured. Please set up Firebase credentials or use email/password authentication.")
    
    # Add 60 seconds clock skew tolerance to handle time sync issues
    decoded = fb_auth.verify_id_token(id_token, clock_skew_seconds=60)
    return decoded


