#!/usr/bin/env python
"""
Run the server directly with uvicorn.
"""

import os
import sys
import uvicorn
import dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
dotenv.load_dotenv()

# Get environment variables with defaults
PORT = int(os.getenv("PORT", "8006"))  # Use port 8006 to avoid conflicts
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

if __name__ == "__main__":
    try:
        # Hard-code the port to 8006
        port = 8006
        logger.info(f"Starting server on port {port} with log level {LOG_LEVEL}")
        
        # Run the server directly
        uvicorn.run(
            "minimal_server:app",
            host="0.0.0.0",
            port=port,  # Use the hard-coded port
            log_level=LOG_LEVEL,
            reload=False,
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical(f"Server failed to start: {e}")
        sys.exit(1)
