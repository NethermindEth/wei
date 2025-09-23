"""
Utility functions for agent nodes.

This module contains utility functions used by various agent nodes,
including tool wrappers and text extraction helpers.
"""

from typing import Dict, Any, List, Tuple, Optional
import logging
import re
from agent_state import AgentState, ClaimEvidence, Task
from agent_tools import SearchTool, IndexerTool, ReaderTool, RAGTool

# Configure logging
logger = logging.getLogger('agent_nodes.utils')

# Initialize tools
# Create instances of tool classes
try:
    # Create tool instances
    search_tool_instance = SearchTool()
    indexer_tool_instance = IndexerTool()
    reader_tool_instance = ReaderTool()
    rag_tool_instance = RAGTool()
    logger.info("All tool instances initialized successfully")
except Exception as e:
    logger.error(f"Error initializing tool instances: {str(e)}")
    # Create dummy instances for graceful failure
    class DummyTool:
        def __getattr__(self, name):
            def dummy_method(*args, **kwargs):
                logger.error(f"Tool not initialized properly, using dummy {name}")
                return {}
            return dummy_method
    
    search_tool_instance = DummyTool()
    indexer_tool_instance = DummyTool()
    reader_tool_instance = DummyTool()
    rag_tool_instance = DummyTool()

# Create wrapper functions with proper type hints and error handling
def search_web(query: str) -> List[Dict[str, Any]]:
    """Search the web for information related to the query.
    
    Args:
        query: The search query string
        
    Returns:
        List of search results with title, snippet, and URL
    """
    try:
        logger.info(f"Searching web for: {query}")
        results = search_tool_instance.search_web(query)
        logger.info(f"Found {len(results)} web search results")
        return results
    except Exception as e:
        logger.error(f"Error in search_web: {str(e)}")
        return []

def search_indexed(query: str, collection: str = "proposals", num_results: int = 5) -> List[Dict[str, Any]]:
    """Search indexed documents for information related to the query.
    
    Args:
        query: The search query string
        collection: The collection to search in ("proposals" or "governance")
        num_results: Maximum number of results to return
        
    Returns:
        List of indexed document results with title, content, and source
    """
    try:
        logger.info(f"Searching indexed documents for: {query} in collection {collection}")
        results = search_tool_instance.search_indexed(query, collection, num_results)
        logger.info(f"Found {len(results)} indexed document results")
        return results
    except Exception as e:
        logger.error(f"Error in search_indexed: {str(e)}")
        return []

def fetch_eip(eip_number: str) -> Dict[str, Any]:
    """Fetch information about an Ethereum Improvement Proposal.
    
    Args:
        eip_number: The EIP number to fetch
        
    Returns:
        Dictionary containing EIP details
    """
    try:
        logger.info(f"Fetching EIP: {eip_number}")
        result = indexer_tool_instance.fetch_eip(eip_number)
        logger.info(f"Successfully fetched EIP: {eip_number}")
        return result
    except Exception as e:
        logger.error(f"Error fetching EIP {eip_number}: {str(e)}")
        return {
            "eip": eip_number,
            "title": f"EIP-{eip_number} (Error)",
            "author": "Unknown",
            "status": "Unknown",
            "content": f"Error fetching EIP: {str(e)}",
            "url": f"https://eips.ethereum.org/EIPS/eip-{eip_number}"
        }

def fetch_bip(bip_number: str) -> Dict[str, Any]:
    """Fetch information about a Bitcoin Improvement Proposal.
    
    Args:
        bip_number: The BIP number to fetch
        
    Returns:
        Dictionary containing BIP details
    """
    try:
        logger.info(f"Fetching BIP: {bip_number}")
        result = indexer_tool_instance.fetch_bip(bip_number)
        logger.info(f"Successfully fetched BIP: {bip_number}")
        return result
    except Exception as e:
        logger.error(f"Error fetching BIP {bip_number}: {str(e)}")
        return {
            "bip": bip_number,
            "title": f"BIP-{bip_number} (Error)",
            "author": "Unknown",
            "status": "Unknown",
            "content": f"Error fetching BIP: {str(e)}",
            "url": f"https://github.com/bitcoin/bips/blob/master/bip-{bip_number}.mediawiki"
        }

def fetch_forum_post(forum_id: str, post_id: str = None) -> Dict[str, Any]:
    """Fetch a post from a forum API.
    
    Args:
        forum_id: The forum identifier (e.g., "ethereum", "bitcoin")
        post_id: The post identifier
        
    Returns:
        Dictionary containing forum post details
    """
    try:
        logger.info(f"Fetching forum post: {forum_id}/{post_id}")
        result = indexer_tool_instance.fetch_forum_post(forum_id, post_id)
        logger.info(f"Successfully fetched forum post: {forum_id}/{post_id}")
        return result
    except Exception as e:
        logger.error(f"Error fetching forum post {forum_id}/{post_id}: {str(e)}")
        return {
            "title": f"{forum_id.capitalize() if forum_id else 'Unknown'} Forum Post (Error)",
            "author": "Unknown",
            "content": f"Error fetching forum post: {str(e)}",
            "date": "",
            "votes": {"for": 0, "against": 0},
            "comments": 0
        }

def read_document(url: str) -> Dict[str, Any]:
    """Read a document from a URL.
    
    Args:
        url: The URL of the document to read
        
    Returns:
        Dictionary containing document content and metadata
    """
    try:
        logger.info(f"Reading document: {url}")
        result = reader_tool_instance.read_document(url)
        logger.info(f"Successfully read document: {url}")
        return result
    except Exception as e:
        logger.error(f"Error reading document {url}: {str(e)}")
        return {
            "content": f"Error reading document: {str(e)}",
            "metadata": {
                "source": url,
                "title": "Error Reading Document",
                "type": "error"
            }
        }

def clip_quotes(content: str, keywords: List[str] = None) -> List[Dict[str, str]]:
    """Extract quotes from content based on keywords.
    
    Args:
        content: The text content to extract quotes from
        keywords: List of keywords to search for in the content
        
    Returns:
        List of dictionaries containing quotes and their associated keywords
    """
    try:
        logger.info(f"Clipping quotes with {len(keywords) if keywords else 'default'} keywords")
        
        # Simple implementation to avoid serialization issues
        if not keywords:
            keywords = ["governance", "proposal", "voting", "implementation"]
        
        quotes = []
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        for sentence in sentences:
            for keyword in keywords:
                if keyword.lower() in sentence.lower():
                    quotes.append({
                        "quote": sentence.strip(),
                        "keyword": keyword
                    })
                    break
        
        logger.info(f"Extracted {len(quotes)} quotes from content")
        return quotes
    except Exception as e:
        logger.error(f"Error clipping quotes: {str(e)}")
        return []

def rag_query(query: str, k: int = 3) -> List[Dict[str, Any]]:
    """Query the RAG system with a question.
    
    Args:
        query: The search query
        k: Number of results to return
        
    Returns:
        List of dictionaries containing content, source, and score
    """
    try:
        logger.info(f"RAG query: {query} (k={k})")
        result = rag_tool_instance.rag_query(query, k)
        logger.info(f"RAG query returned {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Error in RAG query: {str(e)}")
        return []

# Text extraction helpers
def extract_claims_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract claims from text.
    
    Args:
        text: The text to extract claims from
        
    Returns:
        List of dictionaries containing claims
    """
    claims = []
    
    # Simple pattern matching for claims
    claim_patterns = [
        r"(?:claim|statement|assertion):\s*(.*?)(?:\.|$)",
        r"(?:The proposal|It) (?:claims|states|asserts) that\s*(.*?)(?:\.|$)",
        r"(?:According to|As per) the proposal,\s*(.*?)(?:\.|$)"
    ]
    
    for pattern in claim_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if match.strip() and len(match.strip()) > 10:
                claims.append({
                    "claim": match.strip(),
                    "evidence": [],
                    "confidence": 0.5  # Default confidence
                })
    
    logger.info(f"Extracted {len(claims)} claims from text")
    return claims

def extract_tasks_from_text(text: str) -> List[Dict[str, str]]:
    """Extract tasks from text.
    
    Args:
        text: The text to extract tasks from
        
    Returns:
        List of dictionaries containing tasks
    """
    tasks = []
    
    # Simple pattern matching for tasks
    task_patterns = [
        r"(?:task|action item|to-do):\s*(.*?)(?:\.|$)",
        r"(?:need to|should|must|recommend to)\s*(.*?)(?:\.|$)"
    ]
    
    priority_keywords = {
        "high": ["urgent", "critical", "immediate", "essential", "high priority"],
        "medium": ["important", "significant", "moderate", "medium priority"],
        "low": ["minor", "optional", "nice to have", "low priority"]
    }
    
    for pattern in task_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if match.strip() and len(match.strip()) > 10:
                # Determine priority based on keywords
                priority = "medium"  # Default priority
                for p, keywords in priority_keywords.items():
                    if any(keyword in match.lower() for keyword in keywords):
                        priority = p
                        break
                
                tasks.append({
                    "description": match.strip(),
                    "priority": priority
                })
    
    logger.info(f"Extracted {len(tasks)} tasks from text")
    return tasks

def extract_blockers_from_text(text: str) -> List[str]:
    """Extract blockers from text.
    
    Args:
        text: The text to extract blockers from
        
    Returns:
        List of blocker strings
    """
    blockers = []
    
    # Simple pattern matching for blockers
    blocker_patterns = [
        r"(?:blocker|obstacle|challenge|issue|problem):\s*(.*?)(?:\.|$)",
        r"(?:blocked by|hindered by|limited by)\s*(.*?)(?:\.|$)"
    ]
    
    for pattern in blocker_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if match.strip() and len(match.strip()) > 10:
                blockers.append(match.strip())
    
    logger.info(f"Extracted {len(blockers)} blockers from text")
    return blockers

def extract_next_steps_from_text(text: str) -> List[str]:
    """Extract next steps from text.
    
    Args:
        text: The text to extract next steps from
        
    Returns:
        List of next step strings
    """
    next_steps = []
    
    # Simple pattern matching for next steps
    next_step_patterns = [
        r"(?:next step|next action|recommendation|suggested action):\s*(.*?)(?:\.|$)",
        r"(?:recommend|suggest) to\s*(.*?)(?:\.|$)"
    ]
    
    for pattern in next_step_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if match.strip() and len(match.strip()) > 10:
                next_steps.append(match.strip())
    
    logger.info(f"Extracted {len(next_steps)} next steps from text")
    return next_steps
