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
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    # Gemini
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Authentication
    SECRET_KEY: str = "test-secret-key-for-development"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Firebase (optional)
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    
    # Auth0 (optional)
    AUTH0_DOMAIN: Optional[str] = None
    AUTH0_CLIENT_ID: Optional[str] = None
    AUTH0_CLIENT_SECRET: Optional[str] = None
    
    # Application
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Chroma (optional retrieval settings)
    CHROMA_API_KEY: Optional[str] = None
    CHROMA_TENANT: Optional[str] = None
    CHROMA_COLLECTION: Optional[str] = "thematic_embeddings"

    # Hugging Face Inference
    HUGGINGFACE_API_KEY: Optional[str] = None
    # HF_TOKEN is a common env name used by examples; include here so BaseSettings loads it from .env
    HF_TOKEN: Optional[str] = None
    HUGGINGFACE_MODEL: Optional[str] = None
    # Hugging Face generation tuning
    HUGGINGFACE_TEMPERATURE: float = 0.3
    HUGGINGFACE_MAX_TOKENS: int = 150
    # Optional post-generation grammar correction (uses HF model or same model)
    HUGGINGFACE_ENABLE_POSTCORRECT: bool = False
    HUGGINGFACE_GRAMMAR_MODEL: Optional[str] = None
    
    class Config:
        env_file = ".env"


settings = Settings()
