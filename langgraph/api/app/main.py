"""
Main module for the application.
"""

# Standard library imports
import logging
import os
import time

# Third-party imports
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.sql import text

# Local application imports
from app.api import router
from app.db import init_db
from app.middleware import TracingMiddleware
from app.tracing import initialize_langfuse

# Configure logging
log_level_name = os.getenv("LOG_LEVEL", "info").upper()
log_level = getattr(logging, log_level_name, logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# API settings
API_V1_STR = "/api/v1"
PROJECT_NAME = "Wei Agent API"

# Create FastAPI app
app = FastAPI(
    title=PROJECT_NAME,
    openapi_url=f"{API_V1_STR}/openapi.json",
)

# Process CORS origins
cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "*")
if cors_origins:
    if cors_origins == "*":
        allow_origins = ["*"]
    else:
        allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
else:
    allow_origins = ["*"]

logger.info(f"Configuring CORS with origins: {allow_origins}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tracing middleware
app.add_middleware(TracingMiddleware)

# Add middleware to check initialization status
@app.middleware("http")
async def check_initialization_middleware(request: Request, call_next):
    if not _initialization_complete and not request.url.path == "/health":
        return JSONResponse(
            status_code=503,
            content={"detail": "Service is starting up. Please try again later."},
        )
    return await call_next(request)

# Include API router
app.include_router(router, prefix=API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": f"{PROJECT_NAME} is running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    status = "ok" if _initialization_complete else "initializing"
    
    return {
        "status": status,
        "initialization_complete": _initialization_complete,
        "timestamp": time.time()
    }


@app.get("/info")
async def info():
    """Get information about the application."""
    import os
    
    return {
        "name": PROJECT_NAME,
        "environment": {
            "WEI_AGENT_OPEN_ROUTER_API_KEY": "Set" if os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY") else "Not set",
            "WEI_AGENT_AI_MODEL_PROVIDER": os.getenv("WEI_AGENT_AI_MODEL_PROVIDER", "Not set"),
            "WEI_AGENT_AI_MODEL_NAME": os.getenv("WEI_AGENT_AI_MODEL_NAME", "Not set"),
            "WEI_AGENT_EXA_API_KEY": "Set" if os.getenv("WEI_AGENT_EXA_API_KEY") else "Not set",
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# Flag to track initialization status
_initialization_complete = False

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    global _initialization_complete
    import os
    logger.info("Starting up application")
    
    # Skip database initialization if TESTING is set
    if os.getenv("TESTING") == "True":
        logger.info("TESTING environment detected. Skipping database initialization.")
        _initialization_complete = True
        return
    
    try:
        # Initialize database - this is critical, so we raise an exception if it fails
        await init_db()
        logger.info("Database initialization complete")
        
        # Check if tables exist and run migrations if needed
        from app.db import get_session, Base
        from app.db.models import Analysis, WebhookEvent
        
        # Get a database session
        session_gen = get_session()
        session = await session_gen.__anext__()
        
        try:
            # Check if the tables exist by querying the database directly
            tables_exist = False
            try:
                # Try to query the analyses table
                async with session.begin():
                    query = text("SELECT 1 FROM analyses LIMIT 1")
                    await session.execute(query)
                tables_exist = True
                logger.info("Tables exist. Skipping migrations.")
            except Exception as e:
                # If the query fails, the table doesn't exist
                tables_exist = False
                logger.info(f"Tables don't exist: {e}. Will run migrations.")
            
            if not tables_exist:
                logger.info("Tables do not exist. Running migrations...")
                
                # Run migrations using the SQL script
                import os
                migration_file = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    '..',
                    'migrations',
                    '001_initial_schema.sql'
                )
                
                if os.path.exists(migration_file):
                    with open(migration_file, 'r') as f:
                        migration_sql = f.read()
                    
                    # Execute the migration SQL
                    async with session.begin():
                        # Create extension for UUID generation
                        await session.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
                        
                        # Execute the migration SQL
                        statements = migration_sql.split(';')
                        for statement in statements:
                            if statement.strip():
                                await session.execute(text(statement))
                    
                    logger.info("Migration completed successfully")
                else:
                    logger.error(f"Migration file not found: {migration_file}")
            else:
                logger.info("Tables already exist. Skipping migrations.")
        finally:
            # Close the session
            await session.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Exit the application if database initialization fails
        logger.critical("Cannot start application without database connection")
        # We don't call sys.exit here because it would be caught by uvicorn
        # Instead, we'll raise an exception that will be propagated to the server
        raise RuntimeError(f"Database initialization failed: {e}")
    
    try:
        # Initialize Langfuse tracing - this is optional
        if initialize_langfuse():
            logger.info("Langfuse tracing initialized")
        else:
            logger.info("Langfuse tracing not available")
    except Exception as e:
        logger.error(f"Langfuse initialization failed: {e}")
    
    # Mark initialization as complete
    _initialization_complete = True
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down application")
