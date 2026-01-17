"""
YodaAI - Conversational 4Ls Retrospective Assistant
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import (
    action_items, scheduling, user_auth, users,
    workspaces, retrospectives_full, fourls_chat, grouping, voting, discussion_summary, 
    google_auth, workspace_invitations, onboarding
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    try:
        logger.info("Starting YodaAI application...")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Debug mode: {settings.DEBUG}")
        
        # Import here to avoid errors if database fails
        from app.database.database import init_db
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Startup error: {e}", exc_info=True)
        # Don't fail completely - let app start and handle DB errors at runtime
        logger.warning("⚠️ Continuing without full database initialization")
    
    yield
    
    # Shutdown
    logger.info("Shutting down YodaAI application")


# Create FastAPI application
app = FastAPI(
    title="YodaAI - Conversational 4Ls Retrospective Assistant",
    description="AI-powered retrospective assistant for agile teams",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(user_auth.router, prefix="/api/v1/user-auth", tags=["authentication"])
app.include_router(google_auth.router, prefix="/api/v1/user-auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(workspaces.router)  # Has its own prefix
app.include_router(workspace_invitations.router)
app.include_router(workspace_invitations.token_router)
app.include_router(retrospectives_full.router)  # Has its own prefix
app.include_router(onboarding.router)  # /api/v1/workspaces/{id}/onboarding

# Add redirect for old retrospective paths
@app.get("/retrospectives/{retro_id}")
async def redirect_retrospective(retro_id: int):
    """Redirect old retrospective paths to new API format"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/yodaai-app?retro_id={retro_id}", status_code=301)

# Handle old retrospective.html with code path (for backward compatibility)
@app.get("/ui/retrospective.html/{code}")
async def redirect_retrospective_by_code(code: str):
    """Handle old retrospective.html/{code} URLs - redirect to clean URL"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/retrospective/{code}", status_code=301)

app.include_router(fourls_chat.router)  # Has its own prefix
app.include_router(grouping.router)  # Has its own prefix
app.include_router(voting.router)  # Has its own prefix
app.include_router(discussion_summary.router)  # Has its own prefix
app.include_router(action_items.router, prefix="/api/v1/action-items", tags=["action-items"])
app.include_router(scheduling.router, prefix="/api/v1/scheduling", tags=["scheduling"])

# Serve yodaai-app.html at /yodaai-app (clean URL without /ui and .html)
@app.get("/yodaai-app")
async def serve_yodaai_app():
    """Serve the main YodaAI application"""
    file_path = os.path.join("app/ui", "yodaai-app.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Application file not found")

# Serve retrospective.html at /retrospective (clean URL without /ui and .html)
@app.get("/retrospective")
async def serve_retrospective():
    """Serve the retrospective application"""
    file_path = os.path.join("app/ui", "retrospective.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Retrospective file not found")

# Handle retrospective with code path (e.g., /retrospective/{code})
@app.get("/retrospective/{code}")
async def serve_retrospective_with_code(code: str):
    """Serve the retrospective application with a specific code"""
    file_path = os.path.join("app/ui", "retrospective.html")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Retrospective file not found")

# Mount static UI under /ui (for backward compatibility and static assets)
app.mount("/ui", StaticFiles(directory="app/ui", html=True), name="ui")


@app.get("/")
async def root():
    """Root endpoint - redirects to main app"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/yodaai-app")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "yodaai"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
