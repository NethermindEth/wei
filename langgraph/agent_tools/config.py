"""
Configuration Module

This module contains the configuration settings for API keys, URLs, and other parameters
used by the agent tools.
"""

import os
import logging
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger('agent_tools.config')

# Load environment variables
load_dotenv()
logger.debug("Environment variables loaded")

class Config:
    """Configuration class for API settings and cache parameters."""
    # API configuration
    EXA_API_KEY = os.getenv("WEI_AGENT_EXA_API_KEY")
    EXA_API_URL = "https://api.exa.ai/search"
    OPENROUTER_API_KEY = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
    
    # Cache TTL settings (in seconds)
    WEB_SEARCH_CACHE_TTL = 3600  # 1 hour
    INDEXED_SEARCH_CACHE_TTL = 7200  # 2 hours
    DOCUMENT_CACHE_TTL = 86400  # 24 hours
    
    # Default search parameters
    DEFAULT_SEARCH_RESULTS = 5
    DEFAULT_KEYWORDS = ["governance", "voting", "implementation", "security"]
