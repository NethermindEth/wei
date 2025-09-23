"""
API Cache Module for Wei Agent System

This module provides caching functionality for API calls to reduce redundant requests
and improve performance. It implements a simple in-memory cache with TTL (time-to-live)
for cached items.
"""

import time
import hashlib
import json
import logging
from typing import Dict, Any, Optional, Tuple, Callable
from functools import wraps

# Configure logging
logger = logging.getLogger('api_cache')

# Global cache storage
# Structure: {cache_key: (timestamp, result)}
_CACHE: Dict[str, Tuple[float, Any]] = {}

# Default TTL in seconds (1 hour)
DEFAULT_TTL = 3600


def generate_cache_key(func_name: str, args: Tuple, kwargs: Dict[str, Any]) -> str:
    """
    Generate a unique cache key based on function name and arguments.
    
    Args:
        func_name: Name of the function being cached
        args: Positional arguments to the function
        kwargs: Keyword arguments to the function
        
    Returns:
        A unique string key for the cache
    """
    # Convert args and kwargs to a stable string representation
    args_str = json.dumps(args, sort_keys=True)
    kwargs_str = json.dumps(kwargs, sort_keys=True)
    
    # Create a hash of the function name and arguments
    key_data = f"{func_name}:{args_str}:{kwargs_str}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_api_call(ttl: int = DEFAULT_TTL):
    """
    Decorator to cache API call results.
    
    Args:
        ttl: Time-to-live for cached items in seconds
        
    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a unique key for this function call
            cache_key = generate_cache_key(func.__name__, args, kwargs)
            
            # Check if result is in cache and not expired
            if cache_key in _CACHE:
                timestamp, result = _CACHE[cache_key]
                if time.time() - timestamp < ttl:
                    logger.info(f"Cache hit for {func.__name__}")
                    return result
                else:
                    logger.info(f"Cache expired for {func.__name__}")
                    # Remove expired item
                    del _CACHE[cache_key]
            
            # Call the original function
            logger.info(f"Cache miss for {func.__name__}, calling API")
            result = func(*args, **kwargs)
            
            # Store result in cache
            _CACHE[cache_key] = (time.time(), result)
            
            return result
        return wrapper
    return decorator


def clear_cache() -> int:
    """
    Clear the entire cache.
    
    Returns:
        Number of items cleared from cache
    """
    count = len(_CACHE)
    _CACHE.clear()
    logger.info(f"Cleared {count} items from cache")
    return count


def get_cache_stats() -> Dict[str, Any]:
    """
    Get statistics about the current cache.
    
    Returns:
        Dictionary with cache statistics
    """
    current_time = time.time()
    total_items = len(_CACHE)
    expired_items = sum(1 for timestamp, _ in _CACHE.values() if current_time - timestamp >= DEFAULT_TTL)
    
    return {
        "total_items": total_items,
        "active_items": total_items - expired_items,
        "expired_items": expired_items,
        "cache_size_bytes": sum(len(json.dumps(result)) for _, result in _CACHE.values())
    }
