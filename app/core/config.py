"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Ensure .env is loaded early so BaseSettings reads environment variables correctly
load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./yodaai.db"
    NEON_DATABASE_URL: Optional[str] = None
    USE_LOCAL_DB: bool = False  # Set to False to use Neon Cloud (RECOMMENDED)
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Gemini
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Authentication
    SECRET_KEY: str = "test-secret-key-for-development"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours - enough for retrospective sessions
    
    # Firebase (optional)
    FIREBASE_PROJECT_ID: Optional[str] = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY: Optional[str] = os.getenv("FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL: Optional[str] = os.getenv("FIREBASE_CLIENT_EMAIL")
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = None  # Path to credentials.json or JSON content
    
    # Email Service Configuration
    
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = "noreply@taistatInfo"
    SMTP_FROM_NAME: Optional[str] = "YodaAI"
    
    # Application
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    APP_URL: str = "https://yoda-ai.vercel.app/"
    
    # Feature Flags
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_CALENDAR_INTEGRATION: bool = True
    ENABLE_AI_ANALYSIS: bool = True
    ENABLE_AUTOMATED_REMINDERS: bool = True
    
    # AI Service Configuration
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 500
    AI_MODEL: str = "gpt-4"
    AI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    AI_RAG_TOP_K: int = 8

    # AI Monitoring / Guardrails
    AI_TOKEN_SPIKE_THRESHOLD: int = 8000
    AI_MAX_OUTPUT_TOKENS: int = 2000

    # Chroma (optional retrieval settings)
    # If true, require Chroma Cloud credentials and do not fall back to local persistence.
    CHROMA_FORCE_CLOUD: bool = True
    CHROMA_API_KEY: Optional[str] = None
    CHROMA_TENANT: Optional[str] = None
    CHROMA_DATABASE: Optional[str] = "Novel"
    CHROMA_COLLECTION: Optional[str] = "summary_embeddings"
    # Dedicated collection for DA recommendations knowledge base (Disciplined Agile reference embeddings)
    CHROMA_DA_COLLECTION: Optional[str] = "da_recommendations"
    CHROMA_HOST: Optional[str] = None
    CHROMA_PORT: Optional[int] = None
    CHROMA_SSL: bool = True
    # Optional JSON string of extra headers for Chroma HttpClient, e.g. {"X-Chroma-Token":"..."}.
    CHROMA_HEADERS_JSON: Optional[str] = None
    CHROMA_PERSIST_DIR: str = "./.chroma"

    # Hugging Face Inference
    HUGGINGFACE_API_KEY: Optional[str] = None
    HF_TOKEN: Optional[str] = None
    HUGGINGFACE_MODEL: Optional[str] = None
    HUGGINGFACE_TEMPERATURE: float = 0.3
    HUGGINGFACE_MAX_TOKENS: int = 150
    HUGGINGFACE_ENABLE_POSTCORRECT: bool = False
    HUGGINGFACE_GRAMMAR_MODEL: Optional[str] = None
    
    class Config:
        env_file = ".env"


settings = Settings()
