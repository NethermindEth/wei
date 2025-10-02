"""
Authentication module for the application.
"""

# Standard library imports
import logging

# Third-party imports
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from starlette.requests import Request

# Local application imports
from app.config import API_KEYS, API_KEY_NAME

# Configure logging
logger = logging.getLogger(__name__)

# API key header
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
    request: Request,
    api_key: str = Security(api_key_header),
) -> str:
    """
    Validate API key from header against a list of valid API keys.
    
    Args:
        request: The request object
        api_key: The API key from the header
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If the API key is invalid
    """
    # Skip API key validation if no API keys are configured
    if not API_KEYS:
        logger.warning("No API keys configured, allowing all requests")
        return "no_api_key_required"
    
    # Check if the API key is in the list of valid keys
    if api_key not in API_KEYS:
        key_prefix = api_key[:5] if api_key else "None"
        logger.warning(f"Invalid API key attempt: {key_prefix}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    key_prefix = api_key[:5] if api_key else "None"
    logger.debug(f"Valid API key used: {key_prefix}")
    
    
    return api_key
