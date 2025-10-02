#!/usr/bin/env python
"""
Fix the routes.py file to use the correct Path import.
"""

import os
import sys
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def fix_routes():
    """Fix the routes.py file to use the correct Path import."""
    file_path = 'app/api/routes.py'
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check if the file has the correct import
        if 'from fastapi import' in content and 'Path' not in content.split('from fastapi import')[1].split('\n')[0]:
            # Add Path to the fastapi import
            content = re.sub(
                r'from fastapi import ([^,\n]*)',
                r'from fastapi import \1, Path',
                content
            )
            
            # Remove any other Path imports
            content = re.sub(
                r'from pathlib import Path',
                r'# from pathlib import Path  # Commented out to avoid conflict with fastapi.Path',
                content
            )
            
            # Write the file back
            with open(file_path, 'w') as f:
                f.write(content)
                
            logger.info(f"Fixed Path import in {file_path}")
            return True
        else:
            logger.info(f"No Path import issues found in {file_path}")
            return True
    except Exception as e:
        logger.error(f"Error fixing {file_path}: {e}")
        return False

if __name__ == "__main__":
    fix_routes()
