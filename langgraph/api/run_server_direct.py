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

if __name__ == "__main__":
    try:
        # Hard-code the port to 8007
        port = 8007
        logger.info(f"Starting server on port {port}")
        
        # Run the server directly
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False,
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical(f"Server failed to start: {e}")
        sys.exit(1)
