"""
Database configuration and connection management
Supports both SQLite (local development) and PostgreSQL (Neon Cloud production)
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Determine which database URL to use
# Prefer NEON_DATABASE_URL if available, otherwise use SQLite
if settings.NEON_DATABASE_URL and not getattr(settings, 'USE_LOCAL_DB', False):
    database_url = settings.NEON_DATABASE_URL
    logger.info("✅ Using NEON Cloud PostgreSQL database")
else:
    database_url = settings.DATABASE_URL
    logger.info("⚠️ Using LOCAL SQLite database")

# Configure connection arguments based on database type
connect_args = {}
engine_kwargs = {
    "echo": settings.DEBUG,
}

# Check if using Neon/PostgreSQL
is_postgres = database_url.startswith("postgresql")

if is_postgres:
    # PostgreSQL/Neon specific configuration
    logger.info("Configuring PostgreSQL/Neon database connection")
    # Neon requires SSL
    if "sslmode" not in database_url:
        database_url += "?sslmode=require" if "?" not in database_url else "&sslmode=require"
    
    # Use connection pooling for PostgreSQL
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,  # Verify connections before using
        "pool_recycle": 3600,   # Recycle connections after 1 hour
    })
else:
    # SQLite specific configuration
    logger.info("Configuring SQLite database connection")
    connect_args = {"check_same_thread": False}
    # SQLite doesn't support connection pooling well
    engine_kwargs["poolclass"] = NullPool

# Create database engine
engine = create_engine(
    database_url,
    connect_args=connect_args,
    **engine_kwargs
)

# Enable foreign key constraints for SQLite
if not is_postgres:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


async def init_db():
    """Initialize database tables"""
    try:
        logger.info("Checking database connection...")
        
        # Import all models here to ensure they are registered
        from app.models import (
            User,
            EmailVerificationToken,
            Workspace,
            WorkspaceMember,
            WorkspaceInvitation,
            Retrospective,
            RetrospectiveParticipant,
            ChatSession,
            ChatMessage,
            RetrospectiveResponse,
            ThemeGroup,
            VotingSession,
            VoteAllocation,
            DiscussionTopic,
            DiscussionMessage,
            ActionItem,
            UserOnboarding,
            ScheduledRetrospective,
            TeamPreparation,
            AutomatedReminder
        )
        
        # Only try to create tables if not using Neon (which may not have permissions)
        # For Neon, tables should already exist
        try:
            Base.metadata.create_all(bind=engine, checkfirst=True)
            logger.info("Database tables verified")
        except Exception as create_error:
            logger.warning(f"Could not create tables (may already exist): {create_error}")
            logger.info("Assuming tables already exist in database")
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
