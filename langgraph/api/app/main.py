"""
Main application module.

This module initializes the FastAPI application with middleware, routes, and exception handlers.
"""

# Standard library imports
import logging
import os
from typing import Dict, Any, Callable
from datetime import datetime

# Third-party imports
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time

# Local application imports
from app.api.routes import router as api_router
from app.config import settings
from app.errors import AppError
from app.db.core import init_db
from app.middleware import add_middleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        The configured FastAPI application
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="API for Wei Agent, a proposal analysis tool",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        debug=settings.DEBUG
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    add_middleware(app)
    
    # Add exception handlers
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(exc)},
        )
    
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Handle application errors."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "extra": exc.details},
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    
    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Initialize the application on startup."""
        logger.info("Starting up application")
        
        # Skip database initialization in testing mode
        if os.environ.get("TESTING") == "True":
            logger.info("TESTING environment detected. Skipping database initialization.")
            return
        
        # Initialize database
        try:
            await init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up resources on shutdown."""
        logger.info("Shutting down application")
    
    # Add API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Add health and info endpoints directly to the app
    @app.get("/health", summary="Health check endpoint")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat()
        }
    
    @app.get("/info", summary="Information about the API")
    async def info():
        """Get information about the API."""
        return {
            "name": settings.PROJECT_NAME,
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "version": "1.0.0"
        }
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    """Run the application with uvicorn when executed directly."""
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
