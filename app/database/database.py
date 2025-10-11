"""
Database configuration and connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
database_url = settings.NEON_DATABASE_URL or settings.DATABASE_URL

# Neon requires SSL; enable when using Neon URL
connect_args = {}
if settings.NEON_DATABASE_URL:
    connect_args["sslmode"] = "require"

engine = create_engine(
    database_url,
    echo=settings.DEBUG,
    connect_args=connect_args
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


async def init_db():
    """Initialize database tables"""
    # Import all models here to ensure they are registered
    from app.models import user, retrospective, sprint_summary
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
