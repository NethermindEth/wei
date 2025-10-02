"""
Server entry point.
"""

import os
import sys
import uvicorn
import dotenv
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
dotenv.load_dotenv()

# Get environment variables with defaults
PORT = int(os.getenv("PORT", "8007"))  # Use port 8007 by default
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

async def check_postgres():
    """Check if PostgreSQL is running and accessible."""
    try:
        # Try to connect to PostgreSQL
        import asyncpg
        
        try:
            conn = await asyncpg.connect(
                host=os.getenv("DATABASE_HOST", "localhost"),
                port=int(os.getenv("DATABASE_PORT", "5432")),
                user=os.getenv("DATABASE_USER", "postgres"),
                password=os.getenv("DATABASE_PASSWORD", "postgres"),
                database="postgres"  # Connect to default database
            )
            await conn.close()
            logger.info("Successfully connected to PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    except ImportError:
        logger.error("asyncpg not installed")
        return False
    except Exception as e:
        logger.error(f"Error checking PostgreSQL: {e}")
        return False

async def main():
    """Main entry point for the server."""
    # Check if PostgreSQL is running
    if not await check_postgres():
        logger.critical("PostgreSQL is not running or not accessible")
        logger.critical("Cannot start application without database connection")
        sys.exit(1)
    
    logger.info(f"Starting server on port {PORT} with log level {LOG_LEVEL}")
    
    # Run the server
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=PORT,
        log_level=LOG_LEVEL,
        reload=False,  # Disable reload to avoid issues
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        # Run the main function
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical(f"Server failed to start: {e}")
        sys.exit(1)
