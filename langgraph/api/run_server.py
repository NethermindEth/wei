#!/usr/bin/env python
"""
Simple wrapper script to run the server.
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
PORT = int(os.getenv("PORT", "8004"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

def debug_import_issues():
    """Debug import issues."""
    try:
        logger.info("Importing app.main")
        import app.main
        logger.info("Successfully imported app.main")
        
        # Check for Path and Field usage
        import inspect
        import fastapi
        
        logger.info("Checking for Path and Field usage")
        for module_name, module in sys.modules.items():
            if module_name.startswith('app.'):
                for name, obj in inspect.getmembers(module):
                    if inspect.isfunction(obj) and 'Path(' in inspect.getsource(obj):
                        logger.warning(f"Found Path(...) in {module_name}.{name}")
                    if inspect.isclass(obj) and 'Field(' in inspect.getsource(obj):
                        logger.warning(f"Found Field(...) in {module_name}.{name}")
        
        return True
    except Exception as e:
        logger.critical(f"Error during debug: {e}")
        return False

if __name__ == "__main__":
    try:
        logger.info(f"Starting server on port {PORT} with log level {LOG_LEVEL}")
        
        # Debug import issues
        debug_import_issues()
        
        # Run the server directly with uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=PORT,
            log_level=LOG_LEVEL,
            reload=False,  # Disable reload to avoid issues
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical(f"Server failed to start: {e}")
        sys.exit(1)
