"""
Langfuse Tracing Integration for the Wei Agent API

This module provides comprehensive tracing and monitoring capabilities
using Langfuse for the API server.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Union, Callable
from contextlib import contextmanager
from functools import wraps

from app.config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST, LANGFUSE_PROJECT

# Configure logging
logger = logging.getLogger('wei_api_tracing')

# Global variables for Langfuse integration
_langfuse_client = None
_langfuse_available = False


def initialize_langfuse() -> bool:
    """Initialize Langfuse client with environment variables.
    
    Returns:
        bool: True if Langfuse is successfully initialized, False otherwise
    """
    global _langfuse_client, _langfuse_available
    
    try:
        from langfuse import Langfuse
        
        # Get Langfuse configuration from config
        public_key = LANGFUSE_PUBLIC_KEY
        secret_key = LANGFUSE_SECRET_KEY
        host = LANGFUSE_HOST
        
        if not public_key or not secret_key:
            logger.warning("Langfuse credentials not found in environment variables")
            return False
        
        # Initialize Langfuse client
        _langfuse_client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
            project=LANGFUSE_PROJECT
        )
        
        # Test the connection
        if _langfuse_client.auth_check():
            _langfuse_available = True
            logger.info("Langfuse tracing initialized successfully")
            return True
        else:
            logger.warning("Langfuse authentication failed")
            return False
            
    except ImportError:
        logger.info("Langfuse not installed, tracing disabled")
        return False
    except Exception as e:
        logger.error(f"Error initializing Langfuse: {str(e)}")
        return False


def get_langfuse_client():
    """Get the Langfuse client instance.
    
    Returns:
        Langfuse: The Langfuse client instance, or None if not available
    """
    global _langfuse_client, _langfuse_available
    
    if not _langfuse_available and not _langfuse_client:
        initialize_langfuse()
    
    return _langfuse_client if _langfuse_available else None


@contextmanager
def trace_span(name: str, metadata: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None):
    """Context manager for tracing a span of code execution.
    
    Args:
        name: Name of the span
        metadata: Optional metadata to include with the span
        tags: Optional tags to include with the span
    """
    client = get_langfuse_client()
    span = None
    start_time = time.time()
    
    try:
        if client:
            span = client.span(
                name=name,
                metadata=metadata or {},
                tags=tags or []
            )
            span.start()
        
        yield span
        
    finally:
        if span:
            span.end()
        
        # Log execution time even if Langfuse is not available
        execution_time = time.time() - start_time
        logger.debug(f"Execution time for {name}: {execution_time:.2f}s")


def trace_function(name: str, metadata: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None):
    """Decorator for tracing a function execution.
    
    Args:
        name: Name of the trace
        metadata: Optional metadata to include with the trace
        tags: Optional tags to include with the trace
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with trace_span(name, metadata, tags) as span:
                try:
                    result = await func(*args, **kwargs)
                    if span:
                        span.update(status="success")
                    return result
                except Exception as e:
                    if span:
                        span.update(status="error", metadata={"error": str(e)})
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with trace_span(name, metadata, tags) as span:
                try:
                    result = func(*args, **kwargs)
                    if span:
                        span.update(status="success")
                    return result
                except Exception as e:
                    if span:
                        span.update(status="error", metadata={"error": str(e)})
                    raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def trace_json_parsing(content: str, result: Any, success: bool = True, error: Optional[str] = None):
    """
    Trace JSON parsing operations.
    
    Args:
        content: The content being parsed
        result: The parsed result or None if parsing failed
        success: Whether parsing was successful
        error: Error message if parsing failed
    """
    client = get_langfuse_client()
    if not client:
        return
    
    # Create observation
    observation = client.observation(
        name="json_parsing",
        input=content[:1000] if content else "",  # Limit input size
        output=str(result)[:1000] if result else "",  # Limit output size
        status="success" if success else "error",
        metadata={
            "content_length": len(content) if content else 0,
            "error": error or ""
        },
        tags=["json_parsing"]
    )
    
    # Submit observation
    observation.submit()


# Import asyncio at the end to avoid circular imports
import asyncio
