"""
Simple Firestore helper for chat sessions and messages.
"""
from typing import Optional, List, Dict, Any
import os
import json

from app.core.config import settings

try:
    from google.oauth2 import service_account
    from google.cloud import firestore
except Exception:
    service_account = None
    firestore = None


class FirebaseService:
    """Simple Firestore helper for chat sessions and messages."""

    def __init__(self):
        project = settings.FIREBASE_PROJECT_ID or os.getenv("FIREBASE_PROJECT_ID")
        client_email = settings.FIREBASE_CLIENT_EMAIL or os.getenv("FIREBASE_CLIENT_EMAIL")
        private_key = settings.FIREBASE_PRIVATE_KEY or os.getenv("FIREBASE_PRIVATE_KEY")
        service_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON") or None

        self.enabled = False
        self.client = None

        if not firestore or not service_account:
            print("Warning: google-cloud-firestore or google-auth not installed; Firestore unavailable.")
            return

        if service_json:
            try:
                info = json.loads(service_json)
                if "private_key" in info and isinstance(info["private_key"], str):
                    info["private_key"] = info["private_key"].replace("\\n", "\n")
                creds = service_account.Credentials.from_service_account_info(info)
                self.client = firestore.Client(project=info.get("project_id"), credentials=creds)
                self.enabled = True
                return
            except Exception as e:
                print(f"Warning: invalid FIREBASE_SERVICE_ACCOUNT_JSON: {e}")

        if project and client_email and private_key:
            try:
                private_key = private_key.replace("\\n", "\n")
                info = {
                    "type": "service_account",
                    "project_id": project,
                    "client_email": client_email,
                    "private_key": private_key,
                }
                creds = service_account.Credentials.from_service_account_info(info)
                self.client = firestore.Client(project=project, credentials=creds)
                self.enabled = True
            except Exception as e:
                print(f"Warning: Failed to init Firestore: {e}")
        else:
            print("Firestore not configured (missing FIREBASE_PROJECT_ID / FIREBASE_CLIENT_EMAIL / FIREBASE_PRIVATE_KEY)")

    def create_chat_session(self, session_id: str, session_data: Dict[str, Any]) -> Optional[str]:
        if not self.enabled:
            return None
        try:
            doc_ref = self.client.collection("chat_sessions").document(session_id)
            doc_ref.set(session_data)
            return session_id
        except Exception as e:
            print(f"Firestore create_chat_session error: {e}")
            return None

    def save_message(self, session_id: str, message: Dict[str, Any]) -> Optional[str]:
        if not self.enabled:
            return None
        try:
            col_ref = self.client.collection("chat_sessions").document(session_id).collection("messages")
            doc = col_ref.add(message)
            return doc[0].id
        except Exception as e:
            print(f"Firestore save_message error: {e}")
            return None

    def get_sessions_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            q = self.client.collection("chat_sessions").where("user_id", "==", user_id).stream()
            return [{**doc.to_dict(), "id": doc.id} for doc in q]
        except Exception as e:
            print(f"Firestore get_sessions_for_user error: {e}")
            return []

    def get_messages(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        try:
            q = self.client.collection("chat_sessions").document(session_id).collection("messages").order_by("created_at").limit(limit).stream()
            return [{**doc.to_dict(), "id": doc.id} for doc in q]
        except Exception as e:
            print(f"Firestore get_messages error: {e}")
            return []

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        try:
            doc = self.client.collection("chat_sessions").document(session_id).get()
            if not doc.exists:
                return None
            return {**doc.to_dict(), "id": doc.id}
        except Exception as e:
            print(f"Firestore get_session error: {e}")
            return None

    def update_chat_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        if not self.enabled:
            return False
        try:
            doc_ref = self.client.collection("chat_sessions").document(session_id)
            doc_ref.update(updates)
            return True
        except Exception as e:
            print(f"Firestore update_chat_session error: {e}")
            return False
