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
from app.api.routes import auth, retrospectives, uploads
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
# Firebase-only: keep /auth router for potential status endpoints, but no local login/register
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(retrospectives.router, prefix="/api/v1/retrospectives", tags=["retrospectives"])
app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])

# Mount static UI under /ui
app.mount("/ui", StaticFiles(directory="app/ui", html=True), name="ui")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to YodaAI - Conversational 4Ls Retrospective Assistant",
        "version": "1.0.0",
        "status": "running"
    }


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
