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
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import (
    action_items, scheduling, user_auth, users,
    workspaces, retrospectives_full, fourls_chat, grouping, voting, discussion_summary, 
    google_auth, workspace_invitations
)
from app.database.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


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

# Add redirect for old retrospective paths
@app.get("/retrospectives/{retro_id}")
async def redirect_retrospective(retro_id: int):
    """Redirect old retrospective paths to new API format"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/ui/yodaai-app.html?retro_id={retro_id}", status_code=301)

# Handle retrospective.html with code path
@app.get("/ui/retrospective.html/{code}")
async def redirect_retrospective_by_code(code: str):
    """Handle retrospective.html/{code} URLs"""
    # Serve the retrospective.html file and let JavaScript handle the code
    file_path = os.path.join("app/ui", "retrospective.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

app.include_router(fourls_chat.router)  # Has its own prefix
app.include_router(grouping.router)  # Has its own prefix
app.include_router(voting.router)  # Has its own prefix
app.include_router(discussion_summary.router)  # Has its own prefix
app.include_router(action_items.router, prefix="/api/v1/action-items", tags=["action-items"])
app.include_router(scheduling.router, prefix="/api/v1/scheduling", tags=["scheduling"])

# Mount static UI under /ui
app.mount("/ui", StaticFiles(directory="app/ui", html=True), name="ui")


@app.get("/")
async def root():
    """Root endpoint - redirects to main app"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/ui/yodaai-app.html")


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
