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
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    
    # Email Service Configuration
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = "noreply@yodaai.com"
    SMTP_FROM_NAME: Optional[str] = "YodaAI"
    
    # Application
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    APP_URL: str = "http://localhost:8000"
    
    # Feature Flags
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    ENABLE_CALENDAR_INTEGRATION: bool = False
    ENABLE_AI_ANALYSIS: bool = True
    ENABLE_AUTOMATED_REMINDERS: bool = False
    
    # AI Service Configuration
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 500
    AI_MODEL: str = "gpt-4"

    # Chroma (optional retrieval settings)
    CHROMA_API_KEY: Optional[str] = None
    CHROMA_TENANT: Optional[str] = None
    CHROMA_COLLECTION: Optional[str] = "thematic_embeddings"

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
