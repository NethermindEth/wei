"""
Run script for the FastAPI application.

This script starts the FastAPI application with uvicorn.
"""

import os
import logging
import uvicorn

from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Wei Agent API")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.PORT,
        help="Port to bind the server to"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=settings.LOG_LEVEL.lower(),
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level"
    )
    return parser.parse_args()


def main():
    """Run the application."""
    args = parse_args()
    
    # Log startup information
    logger.info(f"Starting Wei Agent API on {args.host}:{args.port}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Workers: {args.workers}")
    logger.info(f"Auto-reload: {args.reload}")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
