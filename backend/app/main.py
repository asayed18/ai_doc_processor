"""
FastAPI application factory and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import checklist, files, questions
from .core.config import settings
from .db.session import init_db


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Include routers
    app.include_router(files.router, prefix="/api/v1")
    app.include_router(questions.router, prefix="/api/v1")
    app.include_router(checklist.router, prefix="/api/v1")

    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": f"{settings.app_name} API",
            "version": settings.app_version,
            "environment": settings.environment,
        }

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    # Debug endpoint (only in development)
    if not settings.is_production:

        @app.get("/debug")
        async def debug_info():
            return {
                "message": "Debug Information",
                "environment": settings.environment,
                "is_production": settings.is_production,
                "allowed_cors_origins": settings.cors_origins,
                "api_version": settings.app_version,
            }

        @app.get("/debug/cors")
        async def debug_cors():
            return {
                "environment": settings.environment,
                "is_production": settings.is_production,
                "allowed_origins": settings.cors_origins,
                "cors_enabled": True,
            }

    return app


def setup_database():
    """Initialize database tables."""
    init_db()


# Create the app instance
app = create_app()


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    setup_database()


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    pass
