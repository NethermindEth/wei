"""
Search Tool Module

This module contains the SearchTool class for searching the web and indexed resources.
"""

import logging
import requests
import json
from typing import List, Dict, Any, Union
from api_cache import cache_api_call
from .config import Config
from .utils import extract_param

# Configure logging
logger = logging.getLogger('agent_tools.search_tool')

class SearchTool:
    """Tool for searching the web and indexed resources using Exa API.
    
    This class provides methods to search both the general web and specific indexed
    collections using the Exa API. It handles parameter extraction, API communication,
    and result formatting with proper error handling and logging.
    
    Attributes:
        exa_api_key: API key for Exa service
        exa_api_url: URL endpoint for Exa API
    """
    
    def __init__(self):
        """Initialize the SearchTool with API credentials.
        
        Raises:
            ValueError: If the required API key is not found in environment variables
        """
        self.exa_api_key = Config.EXA_API_KEY
        self.exa_api_url = Config.EXA_API_URL
        
        if not self.exa_api_key:
            logger.error("EXA_API_KEY not found in environment variables")
            raise ValueError("EXA_API_KEY is required for SearchTool to function properly")
    
    @cache_api_call(ttl=Config.WEB_SEARCH_CACHE_TTL)
    def search_web(self, query: Union[str, Dict[str, Any]], num_results: int = None) -> List[Dict[str, str]]:
        """Search the web for information related to the query using Exa API.
        
        Args:
            query: The search query string or dictionary
            num_results: Maximum number of results to return (default: Config.DEFAULT_SEARCH_RESULTS)
            
        Returns:
            List of search results with title, snippet, and URL
            
        Example:
            >>> search_tool = SearchTool()
            >>> results = search_tool.search_web("Ethereum governance proposals")
            >>> print(len(results))
            5
        """
        # Extract parameters
        query_text = extract_param(query, default="")
        num_results = extract_param(num_results, default=Config.DEFAULT_SEARCH_RESULTS)
        
        if not query_text:
            logger.warning("Empty query provided to search_web")
            return []
        
        try:
            logger.info(f"Searching web for: '{query_text}'")
            
            # Prepare the request
            headers = {
                "x-api-key": self.exa_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "query": query_text,
                "num_results": num_results,
                "use_autoprompt": True,
                "type": "keyword"
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
                    "title": result.get("title", "Untitled"),
                    "url": result.get("url", ""),
                    "snippet": result.get("text", "")
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Found {len(formatted_results)} web search results")
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error in search_web: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in search_web: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in search_web: {str(e)}")
            return []
    
    @cache_api_call(ttl=Config.INDEXED_SEARCH_CACHE_TTL)
    def search_indexed(self, query: Union[str, Dict[str, Any]], collection: str = "proposals", num_results: int = None) -> List[Dict[str, Any]]:
        """Search indexed documents for information related to the query.
        
        Args:
            query: The search query string or dictionary
            collection: The collection to search in ("proposals" or "governance")
            num_results: Maximum number of results to return (default: Config.DEFAULT_SEARCH_RESULTS)
            
        Returns:
            List of indexed document results with title, content, and source
        """
        # Extract parameters
        query_text = extract_param(query, default="")
        num_results = extract_param(num_results, default=Config.DEFAULT_SEARCH_RESULTS)
        
        if not query_text:
            logger.warning("Empty query provided to search_indexed")
            return []
        
        try:
            logger.info(f"Searching indexed documents for: '{query_text}' in collection '{collection}'")
            
            # Prepare the request
            headers = {
                "x-api-key": self.exa_api_key,
                "Content-Type": "application/json"
            }
            
            # Adjust the search type based on the collection
            search_type = "semantic" if collection == "proposals" else "keyword"
            
            data = {
                "query": query_text,
                "num_results": num_results,
                "use_autoprompt": True,
                "type": search_type,
                "collection": collection
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
                    "title": result.get("title", "Untitled"),
                    "source": result.get("url", ""),
                    "content": result.get("text", "")
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Found {len(formatted_results)} indexed document results")
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error in search_indexed: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in search_indexed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in search_indexed: {str(e)}")
            return []
