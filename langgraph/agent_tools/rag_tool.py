"""
RAG Tool Module

This module contains the RAGTool class for Retrieval-Augmented Generation operations.
"""

import logging
import requests
import json
from typing import Dict, Any, List
from api_cache import cache_api_call
from .config import Config

# Configure logging
logger = logging.getLogger('agent_tools.rag_tool')

class RAGTool:
    """Tool for Retrieval-Augmented Generation operations."""
    
    def __init__(self):
        """Initialize the RAGTool with API credentials.
        
        Raises:
            ValueError: If the required API key is not found in environment variables
        """
        self.exa_api_key = Config.EXA_API_KEY
        self.exa_api_url = Config.EXA_API_URL
        
        if not self.exa_api_key:
            logger.error("EXA_API_KEY not found in environment variables")
            raise ValueError("EXA_API_KEY is required for RAGTool to function properly")
    
    @cache_api_call(ttl=Config.WEB_SEARCH_CACHE_TTL)
    def rag_query(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Query the RAG system with a question.
        
        Args:
            query: The query string
            k: Number of results to return
            
        Returns:
            List of relevant documents with content, source, and score
        """
        try:
            logger.info(f"RAG query: {query} (k={k})")
            
            # Prepare the request
            headers = {
                "x-api-key": self.exa_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "query": query,
                "num_results": k,
                "use_autoprompt": True,
                "type": "semantic"
            }
            
            # Make the API call
            response = requests.post(
                self.exa_api_url,
                headers=headers,
                data=json.dumps(data)
            )
            
            # Check for successful response
            response.raise_for_status()
            results = response.json().get("results", [])
            
            # Format the results
            formatted_results = []
            for result in results:
                formatted_result = {
                    "content": result.get("text", ""),
                    "source": result.get("url", ""),
                    "score": result.get("score", 0.0),
                    "title": result.get("title", "Untitled")
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"RAG query returned {len(formatted_results)} results")
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error in rag_query: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in rag_query: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in rag_query: {str(e)}")
            return []
