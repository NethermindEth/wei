"""
Search Tool Node

This module contains the search tool node for the proposal analysis workflow.
The search tool is responsible for searching the web and indexed resources
for information related to the proposal.
"""

import logging
from typing import Dict, Any, List
from agent_state import AgentState
from .utils import search_web, search_indexed

# Configure logging
logger = logging.getLogger('agent_nodes.search_tool_node')

def search_tool_node(state: AgentState) -> AgentState:
    """Tool Node: Search the web and indexed resources for information.
    
    This node takes search queries from the state and performs web searches
    and indexed searches to gather information related to the proposal.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with search results
    """
    try:
        logger.info("==== SEARCH TOOL NODE ====")
        logger.info("Searching for information related to the proposal...")
        
        # Extract search queries from state
        search_queries = state.get("search_queries", [])
        metadata = state.get("metadata", {})
        
        if not search_queries:
            logger.warning("No search queries provided")
            state["search_results"] = []
            return state
        
        # Perform web searches for each query
        all_web_results = []
        for query in search_queries:
            # Enhance query with metadata
            enhanced_query = f"{query} {metadata.get('protocol', '')} {metadata.get('category', '')}"
            logger.info(f"Searching web for: {enhanced_query}")
            
            web_results = search_web(enhanced_query)
            all_web_results.extend(web_results)
            
            # Limit to prevent overwhelming results
            if len(all_web_results) >= 20:
                logger.info("Reached maximum number of web search results")
                break
        
        # Perform indexed searches for governance-related queries
        all_indexed_results = []
        governance_queries = [q for q in search_queries if any(kw in q.lower() for kw in ["governance", "proposal", "vote", "dao"])]
        
        for query in governance_queries:
            # Search in proposals collection
            logger.info(f"Searching indexed documents for: {query} in proposals collection")
            proposal_results = search_indexed(query, collection="proposals")
            all_indexed_results.extend(proposal_results)
            
            # Search in governance collection
            logger.info(f"Searching indexed documents for: {query} in governance collection")
            governance_results = search_indexed(query, collection="governance")
            all_indexed_results.extend(governance_results)
            
            # Limit to prevent overwhelming results
            if len(all_indexed_results) >= 20:
                logger.info("Reached maximum number of indexed search results")
                break
        
        # Update the state with search results
        state["search_results"] = all_web_results
        state["indexed_results"] = all_indexed_results
        
        logger.info(f"Found {len(all_web_results)} web search results and {len(all_indexed_results)} indexed results")
        
        return state
    except Exception as e:
        logger.error(f"Error in search tool node: {str(e)}", exc_info=True)
        state["search_results"] = []
        state["indexed_results"] = []
        return state
