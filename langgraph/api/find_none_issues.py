#!/usr/bin/env python
"""
Script to find NoneType issues in the codebase.
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

def find_none_issues():
    """Find potential NoneType issues in the codebase."""
    # Files to check
    files_to_check = []
    
    # Walk through the app directory
    for root, dirs, files in os.walk('app'):
        for file in files:
            if file.endswith('.py'):
                files_to_check.append(os.path.join(root, file))
    
    # Patterns to look for
    patterns = [
        r'Path\(.*\)',
        r'Field\(.*\)',
        r'Query\(.*\)',
        r'None.*os\.PathLike',
        r'\.\.\.', # Ellipsis
    ]
    
    # Check each file
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    logger.info(f"Found potential issue in {file_path}: {matches}")
        except Exception as e:
            logger.error(f"Error checking {file_path}: {e}")

if __name__ == "__main__":
    find_none_issues()
