"""
Reader Tool Module

This module contains the ReaderTool class for reading documents and extracting quotes.
"""

import logging
import requests
import json
import re
from typing import Dict, Any, List, Optional
from api_cache import cache_api_call
from .config import Config

# Configure logging
logger = logging.getLogger('agent_tools.reader_tool')

class ReaderTool:
    """Tool for reading documents and extracting quotes."""
    
    def __init__(self):
        """Initialize the ReaderTool with API credentials.
        
        Raises:
            ValueError: If the required API key is not found in environment variables
        """
        self.exa_api_key = Config.EXA_API_KEY
        self.exa_api_url = Config.EXA_API_URL
        
        if not self.exa_api_key:
            logger.error("EXA_API_KEY not found in environment variables")
            raise ValueError("EXA_API_KEY is required for ReaderTool to function properly")
    
    @cache_api_call(ttl=Config.DOCUMENT_CACHE_TTL)
    def read_document(self, url: str) -> Dict[str, Any]:
        """Read a document from a URL.
        
        Args:
            url: The URL of the document to read
            
        Returns:
            Dictionary containing document content and metadata
        """
        try:
            logger.info(f"Reading document: {url}")
            
            # Prepare the request
            headers = {
                "x-api-key": self.exa_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "url": url,
                "include_raw_html": False
            }
            
            # Make the API call
            response = requests.post(
                f"{self.exa_api_url}/document",
                headers=headers,
                data=json.dumps(data)
            )
            
            # Check for successful response
            response.raise_for_status()
            result = response.json()
            
            # Extract relevant information
            content = result.get("text", "")
            title = result.get("title", "Untitled Document")
            
            # Format the result
            formatted_result = {
                "content": content,
                "metadata": {
                    "source": url,
                    "title": title,
                    "type": "web_document"
                }
            }
            
            content_length = len(content)
            logger.info(f"Successfully read document: {title} ({content_length} chars)")
            return formatted_result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error in read_document: {str(e)}")
            return {
                "content": f"Error reading document: {str(e)}",
                "metadata": {
                    "source": url,
                    "title": "Error Reading Document",
                    "type": "error"
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error in read_document: {str(e)}")
            return {
                "content": f"Error reading document: {str(e)}",
                "metadata": {
                    "source": url,
                    "title": "Error Reading Document",
                    "type": "error"
                }
            }
    
    def clip_quotes(self, content: str, keywords: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """Extract quotes from content based on keywords.
        
        Args:
            content: The text content to extract quotes from
            keywords: List of keywords to search for in the content
            
        Returns:
            List of dictionaries containing quotes and their associated keywords
        """
        try:
            if not keywords:
                keywords = Config.DEFAULT_KEYWORDS
                
            logger.info(f"Clipping quotes with {len(keywords)} keywords")
            
            # Simple implementation to avoid serialization issues
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
