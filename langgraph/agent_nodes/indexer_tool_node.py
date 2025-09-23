"""
Indexer Tool Node

This module contains the indexer tool node for the proposal analysis workflow.
The indexer tool is responsible for accessing canonical indexers like EIP GitHub,
BIPs, and Forum APIs to gather information about standards and proposals.
"""

import logging
import re
from typing import Dict, Any, List
from agent_state import AgentState
from .utils import fetch_eip, fetch_bip, fetch_forum_post

# Configure logging
logger = logging.getLogger('agent_nodes.indexer_tool_node')

def indexer_tool_node(state: AgentState) -> AgentState:
    """Tool Node: Access canonical indexers like EIP GitHub, BIPs, Forum API.
    
    This node analyzes the proposal and search results to identify references to
    standards (EIPs, BIPs) and forum posts, then fetches the relevant information.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with indexed data
    """
    try:
        logger.info("==== INDEXER TOOL NODE ====")
        logger.info("Accessing canonical indexers for relevant documents...")
        
        # Extract proposal text and search results
        proposal_text = state.get("proposal", "")
        search_results = state.get("search_results", [])
        indexed_results = state.get("indexed_results", [])
        
        # Combine all text for analysis
        all_text = proposal_text
        for result in search_results:
            all_text += " " + result.get("title", "") + " " + result.get("snippet", "")
        for result in indexed_results:
            all_text += " " + result.get("title", "") + " " + result.get("content", "")
        
        # Extract EIP references
        eip_references = set()
        eip_patterns = [
            r"EIP[- ]?(\d+)",
            r"Ethereum Improvement Proposal[- ]?(\d+)"
        ]
        
        for pattern in eip_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                eip_references.add(match.strip())
        
        # Extract BIP references
        bip_references = set()
        bip_patterns = [
            r"BIP[- ]?(\d+)",
            r"Bitcoin Improvement Proposal[- ]?(\d+)"
        ]
        
        for pattern in bip_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                bip_references.add(match.strip())
        
        # Extract forum post references
        forum_references = []
        forum_patterns = [
            r"(ethereum|bitcoin|aave|uniswap|compound|maker)\s+forum\s+post\s+[\"']?([^\"']+)[\"']?",
            r"(ethereum|bitcoin|aave|uniswap|compound|maker)\.org/forum/([^/\s]+)"
        ]
        
        for pattern in forum_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                forum_references.append((match[0], match[1]))
        
        # Fetch data from indexers
        indexed_data = []
        
        # Fetch EIP data
        for eip_number in eip_references:
            logger.info(f"Fetching EIP-{eip_number}")
            eip_data = fetch_eip(eip_number)
            indexed_data.append({
                "type": "eip",
                "id": eip_number,
                "data": eip_data
            })
        
        # Fetch BIP data
        for bip_number in bip_references:
            logger.info(f"Fetching BIP-{bip_number}")
            bip_data = fetch_bip(bip_number)
            indexed_data.append({
                "type": "bip",
                "id": bip_number,
                "data": bip_data
            })
        
        # Fetch forum post data
        for forum_id, post_id in forum_references:
            logger.info(f"Fetching forum post: {forum_id}/{post_id}")
            forum_data = fetch_forum_post(forum_id, post_id)
            indexed_data.append({
                "type": "forum_post",
                "id": f"{forum_id}/{post_id}",
                "data": forum_data
            })
        
        # Update the state with indexed data
        state["indexed_data"] = indexed_data
        
        logger.info(f"Fetched {len(indexed_data)} indexed documents")
        
        return state
    except Exception as e:
        logger.error(f"Error in indexer tool node: {str(e)}", exc_info=True)
        state["indexed_data"] = []
        return state
