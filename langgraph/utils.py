"""
Common utilities for the Wei analyzer system.

This module provides shared utility functions used across the Wei analyzer system,
helping to reduce code duplication and improve maintainability.
"""
import re
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union, TypeVar, Callable

# Type definitions for better type hinting
T = TypeVar('T')
Metadata = Dict[str, Any]

# Configure logging
logger = logging.getLogger('wei_utils')

def setup_logging(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """Set up logging with consistent configuration.
    
    Args:
        name: Name for the logger
        log_file: Optional log file path
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger
    """
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    return logging.getLogger(name)

def extract_json(text: str) -> Dict[str, Any]:
    """Extract JSON from text with multiple fallback strategies.
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Extracted JSON as dictionary
        
    Raises:
        ValueError: If JSON cannot be extracted
    """
    # Try different extraction strategies in order of preference
    extraction_strategies = [
        # Strategy 1: Extract JSON between code block markers
        lambda t: re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', t, re.IGNORECASE),
        
        # Strategy 2: Extract any JSON-like structure with braces
        lambda t: re.search(r'\{[\s\S]*?\}', t),
        
        # Strategy 3: Try to parse the whole text as JSON
        lambda t: t if t.strip().startswith('{') and t.strip().endswith('}') else None
    ]
    
    for strategy in extraction_strategies:
        try:
            result = strategy(text)
            if result:
                if isinstance(result, re.Match):
                    json_str = result.group(1) if len(result.groups()) > 0 else result.group(0)
                else:
                    json_str = result
                return json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            continue
    
    # If all strategies fail, raise an error
    raise ValueError("Could not extract valid JSON from text")

def safe_get(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely get a nested value from a dictionary using dot notation.
    
    Args:
        data: Dictionary to get value from
        path: Path to value using dot notation (e.g., "a.b.c")
        default: Default value if path doesn't exist
        
    Returns:
        Value at path or default
    """
    if not data or not isinstance(data, dict):
        return default
        
    keys = path.split('.')
    result = data
    
    for key in keys:
        if isinstance(result, dict) and key in result:
            result = result[key]
        else:
            return default
    
    return result

def extract_section_with_patterns(content: str, patterns: List[str], min_length: int = 30) -> str:
    """Extract a section from content using a list of regex patterns.
    
    Args:
        content: The text content to search in
        patterns: List of regex patterns to try
        min_length: Minimum acceptable length for the extracted section
        
    Returns:
        The extracted section or empty string if not found
    """
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            section = match.group(1).strip()
            if len(section) >= min_length:
                return section
    return ""

def determine_section_status(content: str, section_text: str, keywords: List[str]) -> Dict[str, Any]:
    """Determine the status of a section based on content and keywords.
    
    Args:
        content: The full proposal content
        section_text: The extracted section text
        keywords: Keywords to check for in the content
        
    Returns:
        Dictionary with status, justification, and suggestions
    """
    has_keywords = any(keyword in content.lower() for keyword in keywords)
    status = "pass" if section_text or has_keywords else "fail"
    
    justification = section_text[:200] + "..." if len(section_text) > 200 else section_text
    if not justification and has_keywords:
        justification = f"The proposal includes {keywords[0]} considerations"
    
    suggestions = []
    if status == "fail":
        suggestions = [f"Clearly articulate the {keywords[0]} of the proposal"]
    
    return {
        "status": status,
        "justification": justification,
        "suggestions": suggestions
    }

def measure_execution_time(func: Callable) -> Callable:
    """Decorator to measure execution time of a function.
    
    Args:
        func: Function to measure
        
    Returns:
        Wrapped function that measures execution time
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        logger.info(f"Function {func.__name__} executed in {execution_time:.2f} ms")
        return result
    return wrapper
