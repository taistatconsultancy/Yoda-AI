"""
Firebase authentication: initialize Admin SDK and verify ID tokens.
"""

from typing import Optional, Dict, Any

import firebase_admin
from firebase_admin import auth as fb_auth, credentials

from app.core.config import settings


_app_initialized = False


def _ensure_initialized() -> None:
    global _app_initialized
    if _app_initialized:
        return

    # Initialize using service account JSON path or JSON content
    # Prefer GOOGLE_APPLICATION_CREDENTIALS path if set via env, otherwise
    # use credential.json in project root if present.
    try:
        cred: credentials.Base
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
        else:
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        _app_initialized = True
    except Exception:
        # Fallback to default app if already initialized elsewhere
        if not firebase_admin._apps:
            raise
        _app_initialized = True


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """Verify a Firebase ID token and return the decoded payload."""
    _ensure_initialized()
    decoded = fb_auth.verify_id_token(id_token)
    return decoded


