"""
Deep Adapter Module

This module provides an adapter to use the deepagents-based implementation
with the existing API. It ensures backward compatibility with code that
uses the original proposal_analyzer.py implementation.
"""

import logging
from typing import Dict, Any
from deep_proposal_analyzer import analyze_proposal as deep_analyze_proposal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deep_adapter.log')
    ]
)
logger = logging.getLogger('deep_adapter')

def analyze_proposal(proposal: str, metadata: Dict[str, Any], export_json: bool = False, json_path: str = None) -> Dict[str, Any]:
    """
    Adapter function to use the deepagents-based implementation with the existing API.
    
    This function has the same signature as the original analyze_proposal function
    but uses the deepagents-based implementation internally.
    
    Args:
        proposal: The proposal text to analyze
        metadata: Metadata about the proposal (title, protocol, category, author, etc.)
        export_json: Whether to export the results as JSON
        json_path: Path to save the JSON results (default: proposal_analysis_result.json)
        
    Returns:
        Dict[str, Any]: Analysis results in the same format as the original implementation
    """
    logger.info("Using deepagents-based implementation for proposal analysis")
    
    # Call the deepagents-based implementation
    result = deep_analyze_proposal(proposal, metadata, export_json, json_path)
    
    # The result is already in the correct format for backward compatibility
    return result
