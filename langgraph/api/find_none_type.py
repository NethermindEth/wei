#!/usr/bin/env python
"""
Find NoneType issues in the codebase.
"""

import os
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def find_none_type():
    """Find NoneType issues in the codebase."""
    try:
        # Try to import app.main
        import app.main
        logger.info("Successfully imported app.main")
    except Exception as e:
        logger.error(f"Failed to import app.main: {e}")
        traceback.print_exc()
        
        # Try to import individual modules
        modules = [
            'app.config',
            'app.auth',
            'app.api',
            'app.api.routes',
            'app.schemas',
            'app.db',
            'app.tracing',
            'app.middleware'
        ]
        
        for module_name in modules:
            try:
                __import__(module_name)
                logger.info(f"Successfully imported {module_name}")
            except Exception as e:
                logger.error(f"Failed to import {module_name}: {e}")
                traceback.print_exc()

if __name__ == "__main__":
    find_none_type()
