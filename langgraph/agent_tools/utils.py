"""
Utility Functions

This module contains utility functions used by the agent tools.
"""

from typing import TypeVar, Dict, Any, Union

# Type variable for generic parameter extraction
T = TypeVar('T')

def extract_param(param: Union[Dict[str, T], T], key: str = None, default: T = None) -> T:
    """Extract a parameter value from various input formats.
    
    Args:
        param: The parameter which might be a dictionary or direct value
        key: The key to look for in the dictionary (if param is a dictionary)
        default: Default value to return if param is None
        
    Returns:
        The extracted parameter value
    """
    if param is None:
        return default
        
    if isinstance(param, dict):
        # Try to find the specified key
        if key and key in param:
            return param[key]
        # Try common keys
        if 'self' in param:
            return extract_param(param['self'], key, default)
        # For query parameters
        if 'query' in param:
            return param['query']
            
    return param
