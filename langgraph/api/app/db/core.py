"""
Core database module

This module contains the core database types and functions.
"""

# Standard library imports
import asyncio
import logging
import os
from typing import Optional, Tuple

# Third-party imports
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import text

# Local application imports
from app.config import (
    DATABASE_URL, DATABASE_NAME, DB_ECHO_LOG,
    DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT, DB_POOL_RECYCLE,
    get_postgres_system_url
)

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy base class for models
Base = declarative_base()

# Database connection pool
engine = None
async_session_maker = None


async def init_db_pool():
    """Initialize the database connection pool."""
    global engine, async_session_maker
    
    if engine is not None:
        return
    
    logger.info("Initializing database connection pool")
    
    # Create async engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=DB_ECHO_LOG,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=DB_POOL_RECYCLE,
    )
    
    # Create session maker
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


async def get_session() -> AsyncSession:
    """Get a database session."""
    if async_session_maker is None:
        await init_db_pool()
    
    async with async_session_maker() as session:
        yield session


async def ensure_database_exists() -> Tuple[bool, str]:
    """
    Ensure the database exists, creating it if necessary.
    
    Returns:
        Tuple[bool, str]: (was_created, database_name)
    """
    db_name = DATABASE_NAME
    postgres_url = get_postgres_system_url()
    
    # Connect to postgres system database
    system_engine = create_async_engine(
        postgres_url,
        isolation_level="AUTOCOMMIT",
    )
    
    try:
        # Check if database exists
        async with system_engine.connect() as conn:
            result = await conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            )
            exists = result.scalar() is not None
            
            # Create database if it doesn't exist
            if not exists:
                logger.info(f"Creating database: {db_name}")
                await conn.execute(text(f"CREATE DATABASE {db_name}"))
                return True, db_name
            
            logger.info(f"Database {db_name} already exists")
            return False, db_name
    finally:
        await system_engine.dispose()


async def run_migrations():
    """Run database migrations."""
    from alembic.config import Config
    from alembic import command
    import os
    
    # Get the directory of the current file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Create Alembic configuration
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
    
    # Run migrations
    logger.info("Running database migrations")
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations completed")


async def init_db():
    """Initialize the database with automatic creation and run migrations."""
    # Ensure database exists
    created, db_name = await ensure_database_exists()
    
    # Initialize connection pool
    await init_db_pool()
    
    # Run migrations if database was created
    if created:
        await run_migrations()
    
    return engine
