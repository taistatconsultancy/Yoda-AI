"""
YodaAI - Conversational 4Ls Retrospective Assistant
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import (
    retrospectives, teams, action_items, 
    ai_chat, ai_chat_openai, onboarding, scheduling, user_auth,
    workspaces, retrospectives_full, fourls_chat, grouping, voting, discussion_summary
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
app.include_router(workspaces.router)  # Has its own prefix
app.include_router(retrospectives_full.router)  # Has its own prefix
app.include_router(fourls_chat.router)  # Has its own prefix
app.include_router(grouping.router)  # Has its own prefix
app.include_router(voting.router)  # Has its own prefix
app.include_router(discussion_summary.router)  # Has its own prefix
app.include_router(action_items.router, prefix="/api/v1/action-items", tags=["action-items"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])
app.include_router(scheduling.router, prefix="/api/v1/scheduling", tags=["scheduling"])
app.include_router(retrospectives.router, prefix="/api/v1/retrospectives-old", tags=["retrospectives-old"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["teams"])
app.include_router(ai_chat.router, prefix="/api/v1/ai-chat", tags=["ai-chat"])
app.include_router(ai_chat_openai.router, prefix="/api/v1/ai-chat-openai", tags=["ai-chat-openai"])

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
