#!/usr/bin/env python
"""
Fix Path parameters in routes.py.
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

def fix_path_params():
    """Fix Path parameters in routes.py."""
    file_path = 'app/api/routes.py'
    try:
        # Read the file
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace Path(None) with Path(...)
        content = re.sub(r'Path\(None\)', 'Path(...)', content)
        
        # Write the file back
        with open(file_path, 'w') as f:
            f.write(content)
            
        logger.info(f"Fixed Path parameters in {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error fixing {file_path}: {e}")
        return False

if __name__ == "__main__":
    fix_path_params()
