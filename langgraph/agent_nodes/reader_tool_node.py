"""
Reader Tool Node

This module contains the reader tool node for the proposal analysis workflow.
The reader tool is responsible for reading documents and extracting relevant
information from them.
"""

import logging
from typing import Dict, Any, List
from agent_state import AgentState
from .utils import read_document, clip_quotes

# Configure logging
logger = logging.getLogger('agent_nodes.reader_tool_node')

def reader_tool_node(state: AgentState) -> AgentState:
    """Tool Node: Read documents and extract relevant information.
    
    This node takes search results and indexed data, reads the documents,
    and extracts relevant information using the reader tool.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with document content and extracted information
    """
    try:
        logger.info("==== READER TOOL NODE ====")
        logger.info("Reading documents and extracting relevant information...")
        
        # Extract search results and indexed data
        search_results = state.get("search_results", [])
        indexed_results = state.get("indexed_results", [])
        indexed_data = state.get("indexed_data", [])
        metadata = state.get("metadata", {})
        
        # Extract keywords from metadata and proposal
        keywords = [
            metadata.get("protocol", ""),
            metadata.get("category", ""),
            "governance",
            "proposal",
            "vote",
            "implementation",
            "security"
        ]
        keywords = [k for k in keywords if k]  # Remove empty strings
        
        # Read documents from search results
        documents = []
        for result in search_results:
            url = result.get("url")
            if not url:
                continue
                
            logger.info(f"Reading document: {url}")
            document = read_document(url)
            
            # Extract quotes using keywords
            content = document.get("content", "")
            if content:
                quotes = clip_quotes(content, keywords)
                document["quotes"] = quotes
                logger.info(f"Extracted {len(quotes)} quotes from document")
            
            documents.append({
                "type": "web",
                "url": url,
                "document": document
            })
            
            # Limit to prevent overwhelming results
            if len(documents) >= 10:
                logger.info("Reached maximum number of documents to read")
                break
        
        # Process indexed data (EIPs, BIPs, forum posts)
        for item in indexed_data:
            item_type = item.get("type")
            item_data = item.get("data", {})
            
            content = item_data.get("content", "")
            if content:
                quotes = clip_quotes(content, keywords)
                item_data["quotes"] = quotes
                logger.info(f"Extracted {len(quotes)} quotes from {item_type} document")
        
        # Update the state with documents and processed indexed data
        state["documents"] = documents
        state["indexed_data"] = indexed_data  # Update with quotes
        
        logger.info(f"Processed {len(documents)} documents and {len(indexed_data)} indexed items")
        
        return state
    except Exception as e:
        logger.error(f"Error in reader tool node: {str(e)}", exc_info=True)
        state["documents"] = []
        return state
