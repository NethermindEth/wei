"""
JSON parsing utilities for the Wei Agent API.

This module provides robust JSON parsing functions that can handle various formats
of JSON data, including those embedded in markdown code blocks or plain text.
"""

import json
import logging
import re
from typing import Any, Dict, Optional, Tuple, Union

from app.tracing import trace_json_parsing

# Configure logging
logger = logging.getLogger(__name__)


def extract_json_from_markdown(content: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
    """
    Extract JSON from markdown content, handling various formats.
    
    This function tries multiple strategies to extract valid JSON:
    1. Look for JSON in code blocks with various markers
    2. Try to parse the entire content as JSON
    3. Look for JSON-like content within surrounding text
    
    Args:
        content: The markdown content that may contain JSON
        
    Returns:
        Tuple of (success, result) where result is either the parsed JSON or an error message
    """
    if not content:
        error_msg = "Empty content provided"
        trace_json_parsing("", None, False, error_msg)
        return False, error_msg
    
    # Strategy 1: Try to extract JSON from code blocks with various markers
    code_block_patterns = [
        r"```(?:json|JSON)?\s*([\s\S]*?)\s*```",  # Standard markdown code blocks
        r"~~~(?:json|JSON)?\s*([\s\S]*?)\s*~~~",  # Alternative code block marker
        r"'''(?:json|JSON)?\s*([\s\S]*?)\s*'''",  # Another alternative marker
    ]
    
    for pattern in code_block_patterns:
        matches = re.findall(pattern, content)
        if matches:
            for match in matches:
                try:
                    result = json.loads(match)
                    trace_json_parsing(match, result, True)
                    return True, result
                except json.JSONDecodeError:
                    continue
    
    # Strategy 2: Try to parse the entire content as JSON
    try:
        result = json.loads(content)
        trace_json_parsing(content, result, True)
        return True, result
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Look for JSON-like content (text between { and })
    try:
        # Find the first { and the last }
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            json_content = content[start_idx:end_idx + 1]
            result = json.loads(json_content)
            trace_json_parsing(json_content, result, True)
            return True, result
    except json.JSONDecodeError:
        pass
    
    # If all strategies fail, return an error
    error_msg = "Failed to extract valid JSON from content"
    trace_json_parsing(content, None, False, error_msg)
    return False, error_msg


def try_extract_json_from_markdown(content: str) -> Dict[str, Any]:
    """
    Try to extract JSON from markdown content, returning an empty dict on failure.
    
    Args:
        content: The markdown content that may contain JSON
        
    Returns:
        The parsed JSON as a dict, or an empty dict if parsing fails
    """
    success, result = extract_json_from_markdown(content)
    if success and isinstance(result, dict):
        return result
    
    logger.warning(f"JSON extraction failed: {result if not success else 'Invalid result type'}")
    return {}
