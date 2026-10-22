"""PrePilot AI — FastAPI application entry point."""

import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .config import settings
from .database import init_db, SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PrePilot AI",
    description="AI-powered placement preparation platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routes
from .routes import auth, resume, interview, coding, planner, chat, dashboard, admin

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(interview.router)
app.include_router(coding.router)
app.include_router(planner.router)
app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(admin.router)

# Determine frontend directory
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@app.on_event("startup")
def on_startup():
    """Initialize database and seed data on startup."""
    logger.info("Starting PrePilot AI...")

    # Create uploads directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Initialize database
    init_db()
    logger.info("Database tables created")

    # Seed demo data
    if settings.SEED_DEMO_DATA:
        from .seed import seed_data
        db = SessionLocal()
        try:
            seed_data(db)
        finally:
            db.close()

    logger.info("PrePilot AI started successfully!")


# Serve frontend static files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    # Catch-all for SPA routing — serve index.html for any non-API route
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept API routes or docs
        if full_path.startswith(("api/", "docs", "redoc", "openapi")):
            return
        # Check if it's a static file
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Otherwise serve index.html for SPA routing
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "app": "PrePilot AI",
            "version": "1.0.0",
            "docs": "/docs",
            "frontend": "Frontend directory not found. Place frontend files in /frontend/",
        }
