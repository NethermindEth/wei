"""
Database initialization script.
"""

import asyncio
import logging
from app.db import init_db
from app.config import settings

# Configure logging
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Initialize the database."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialization complete.")


if __name__ == "__main__":
    asyncio.run(main())
