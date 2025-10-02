#!/usr/bin/env python
"""
Direct fix for the NoneType issue.
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

def fix_files():
    """Fix all files with potential issues."""
    # Files to check and fix
    files_to_fix = []
    
    # Walk through the app directory
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                files_to_fix.append(os.path.join(root, file))
    
    # Check each file
    for file_path in files_to_fix:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if the file needs fixing
            if '...' in content:
                logger.info(f"Found ellipsis in {file_path}, applying fixes")
                
                # Replace all instances of ... with None
                content = content.replace('...', 'None')
                
                # Write the file back
                with open(file_path, 'w') as f:
                    f.write(content)
                
                logger.info(f"Fixed ellipsis in {file_path}")
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")

if __name__ == "__main__":
    fix_files()
