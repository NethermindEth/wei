"""Agent Tools Module

This module re-exports all tool classes from the agent_tools package.
It serves as a backward-compatible interface for existing code that imports from this module.

Note: This file is maintained for backward compatibility. New code should import directly
from the agent_tools package.
"""

import logging
from typing import Dict, Any, List, Optional, Union, TypeVar

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_tools.log')
    ]
)
logger = logging.getLogger('agent_tools')

# Import all tool classes and utilities from the agent_tools package
from agent_tools import (
    # Tool classes
    SearchTool,
    IndexerTool,
    ReaderTool,
    RAGTool,
    
    # Configuration
    Config,
    
    # Utility functions
    extract_param
)

logger.info("Agent tools imported successfully from package")
