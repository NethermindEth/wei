"""
Indexer Tool Module

This module contains the IndexerTool class for accessing canonical indexers like EIP GitHub, BIPs, and Forum API.
"""

import logging
import requests
import json
import re
from typing import Dict, Any
from api_cache import cache_api_call
from .config import Config

# Configure logging
logger = logging.getLogger('agent_tools.indexer_tool')

class IndexerTool:
    """Tool for accessing canonical indexers like EIP GitHub, BIPs, Forum API using Exa API."""
    
    def __init__(self):
        """Initialize the IndexerTool with API credentials.
        
        Raises:
            ValueError: If the required API key is not found in environment variables
        """
        self.exa_api_key = Config.EXA_API_KEY
        self.exa_api_url = Config.EXA_API_URL
        
        if not self.exa_api_key:
            logger.error("EXA_API_KEY not found in environment variables")
            raise ValueError("EXA_API_KEY is required for IndexerTool to function properly")
    
    @cache_api_call(ttl=Config.DOCUMENT_CACHE_TTL)
    def fetch_eip(self, eip_number: str) -> Dict[str, Any]:
        """Fetch information about an Ethereum Improvement Proposal.
        
        Args:
            eip_number: The EIP number to fetch
            
        Returns:
            Dictionary containing EIP details
        """
        try:
            logger.info(f"Fetching EIP: {eip_number}")
            
            # Construct the URL for the EIP
            eip_url = f"https://eips.ethereum.org/EIPS/eip-{eip_number}"
            
            # Prepare the request
            headers = {
                "x-api-key": self.exa_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "url": eip_url,
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
            
            # Extract metadata from the content
            title_match = re.search(r"Title:\s*(.+?)(?:\n|$)", content)
            author_match = re.search(r"Author:\s*(.+?)(?:\n|$)", content)
            status_match = re.search(r"Status:\s*(.+?)(?:\n|$)", content)
            
            title = f"EIP-{eip_number}: {title_match.group(1).strip()}" if title_match else f"EIP-{eip_number}"
            author = author_match.group(1).strip() if author_match else "Unknown"
            status = status_match.group(1).strip() if status_match else "Unknown"
            
            # Format the result
            formatted_result = {
                "eip": eip_number,
                "title": title,
                "author": author,
                "status": status,
                "content": content,
                "url": eip_url
            }
            
            logger.info(f"Successfully fetched EIP-{eip_number}: {title}")
            return formatted_result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error in fetch_eip: {str(e)}")
            return {
                "eip": eip_number,
                "title": f"EIP-{eip_number} (Error)",
                "author": "Unknown",
                "status": "Unknown",
                "content": f"Error fetching EIP: {str(e)}",
                "url": f"https://eips.ethereum.org/EIPS/eip-{eip_number}"
            }
        except Exception as e:
            logger.error(f"Unexpected error in fetch_eip: {str(e)}")
            return {
                "eip": eip_number,
                "title": f"EIP-{eip_number} (Error)",
                "author": "Unknown",
                "status": "Unknown",
                "content": f"Error fetching EIP: {str(e)}",
                "url": f"https://eips.ethereum.org/EIPS/eip-{eip_number}"
            }
    
    @cache_api_call(ttl=Config.DOCUMENT_CACHE_TTL)
    def fetch_bip(self, bip_number: str) -> Dict[str, Any]:
        """Fetch information about a Bitcoin Improvement Proposal.
        
        Args:
            bip_number: The BIP number to fetch
            
        Returns:
            Dictionary containing BIP details
        """
        try:
            logger.info(f"Fetching BIP: {bip_number}")
            
            # Construct the URL for the BIP
            bip_url = f"https://github.com/bitcoin/bips/blob/master/bip-{bip_number}.mediawiki"
            
            # Prepare the request
            headers = {
                "x-api-key": self.exa_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "url": bip_url,
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
            
            # Extract metadata from the content
            title_match = re.search(r"Title:\s*(.+?)(?:\n|$)", content)
            author_match = re.search(r"Author:\s*(.+?)(?:\n|$)", content)
            status_match = re.search(r"Status:\s*(.+?)(?:\n|$)", content)
            
            title = f"BIP-{bip_number}: {title_match.group(1).strip()}" if title_match else f"BIP-{bip_number}"
            author = author_match.group(1).strip() if author_match else "Unknown"
            status = status_match.group(1).strip() if status_match else "Unknown"
            
            # Format the result
            formatted_result = {
                "bip": bip_number,
                "title": title,
                "author": author,
                "status": status,
                "content": content,
                "url": bip_url
            }
            
            logger.info(f"Successfully fetched BIP-{bip_number}: {title}")
            return formatted_result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error in fetch_bip: {str(e)}")
            return {
                "bip": bip_number,
                "title": f"BIP-{bip_number} (Error)",
                "author": "Unknown",
                "status": "Unknown",
                "content": f"Error fetching BIP: {str(e)}",
                "url": f"https://github.com/bitcoin/bips/blob/master/bip-{bip_number}.mediawiki"
            }
        except Exception as e:
            logger.error(f"Unexpected error in fetch_bip: {str(e)}")
            return {
                "bip": bip_number,
                "title": f"BIP-{bip_number} (Error)",
                "author": "Unknown",
                "status": "Unknown",
                "content": f"Error fetching BIP: {str(e)}",
                "url": f"https://github.com/bitcoin/bips/blob/master/bip-{bip_number}.mediawiki"
            }
    
    @cache_api_call(ttl=Config.DOCUMENT_CACHE_TTL)
    def fetch_forum_post(self, forum_id: str, post_id: str) -> Dict[str, Any]:
        """Fetch a post from a forum API.
        
        Args:
            forum_id: The forum identifier (e.g., "ethereum", "bitcoin")
            post_id: The post identifier
            
        Returns:
            Dictionary containing forum post details
        """
        try:
            logger.info(f"Fetching forum post: {post_id} from forum {forum_id}")
            
            # Construct the URL for the forum post
            # This is a simplified example; in reality, you would need to map forum_id to actual forum URLs
            forum_url = f"https://forum.{forum_id}.org/t/{post_id}"
            
            # Prepare the request
            headers = {
                "x-api-key": self.exa_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "url": forum_url,
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
            title = result.get("title", f"Forum Post {post_id}")
            
            # Format the result
            formatted_result = {
                "id": post_id,
                "forum": forum_id,
                "title": title,
                "author": "Unknown",  # Would need additional parsing to extract author
                "content": content,
                "date": "Unknown",    # Would need additional parsing to extract date
                "url": forum_url,
                "votes": {"for": 0, "against": 0},  # Placeholder values
                "comments": 0         # Placeholder value
            }
            
            logger.info(f"Successfully fetched forum post: {title}")
            return formatted_result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error in fetch_forum_post: {str(e)}")
            return {
                "id": post_id,
                "forum": forum_id,
                "title": "Forum Post (Error)",
                "author": "Unknown",
                "content": f"Error fetching forum post: {str(e)}",
                "date": "",
                "votes": {"for": 0, "against": 0},
                "comments": 0
            }
        except Exception as e:
            logger.error(f"Unexpected error in fetch_forum_post: {str(e)}")
            return {
                "id": post_id,
                "forum": forum_id,
                "title": "Forum Post (Error)",
                "author": "Unknown",
                "content": f"Error fetching forum post: {str(e)}",
                "date": "",
                "votes": {"for": 0, "against": 0},
                "comments": 0
            }
