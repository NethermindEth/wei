from typing import List, Dict, Any, Optional, Union, TypeVar, Generic, Callable, cast, overload
import requests
import json
import re
import os
import logging
from dotenv import load_dotenv
from api_cache import cache_api_call

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_tools.log')
    ]
)
logger = logging.getLogger('agent_tools')

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")


class Config:
    """Configuration class for API settings and cache parameters."""
    # API configuration
    EXA_API_KEY = os.getenv("WEI_AGENT_EXA_API_KEY")
    EXA_API_URL = "https://api.exa.ai/search"
    OPENROUTER_API_KEY = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
    
    # Cache TTL settings (in seconds)
    WEB_SEARCH_CACHE_TTL = 3600  # 1 hour
    INDEXED_SEARCH_CACHE_TTL = 7200  # 2 hours
    DOCUMENT_CACHE_TTL = 86400  # 24 hours
    
    # Default search parameters
    DEFAULT_SEARCH_RESULTS = 5
    DEFAULT_KEYWORDS = ["governance", "voting", "implementation", "security"]


# Type variable for generic parameter extraction
T = TypeVar('T')


def extract_param(param: Union[Dict[str, T], T], key: str = None, default: T = None) -> T:
    """Extract a parameter value from various input formats.
    
    Args:
        param: The parameter which might be a dictionary or direct value
        key: The key to look for in the dictionary (if param is a dictionary)
        default: Default value to return if param is None
        
    Returns:
        The extracted parameter value
    """
    if param is None:
        return default
        
    if isinstance(param, dict):
        # Try to find the specified key
        if key and key in param:
            return param[key]
        # Try common keys
        if 'self' in param:
            return extract_param(param['self'], key, default)
        # For query parameters
        if 'query' in param:
            return param['query']
            
    return param

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
            logger.warning("Empty search query provided")
            return []
        
        logger.info(f"Searching web for: {query_text}")
        
        headers = self._get_headers()
        payload = self._create_search_payload(query_text, num_results)
        
        return self._execute_search(payload, headers, "web search")
    
    @cache_api_call(ttl=Config.INDEXED_SEARCH_CACHE_TTL)
    def search_indexed(self, query: Union[str, Dict[str, Any]], 
                       collection: str = "proposals", 
                       num_results: int = None) -> List[Dict[str, str]]:
        """Search indexed documents for information related to the query.
        
        Args:
            query: The search query string or dictionary
            collection: The collection to search in ("proposals" or "governance")
            num_results: Maximum number of results to return
            
        Returns:
            List of indexed document results with title, content, and source
            
        Example:
            >>> search_tool = SearchTool()
            >>> results = search_tool.search_indexed("EIP-1559", collection="proposals")
            >>> print(results[0]["title"])
            'EIP-1559: Fee market change for ETH 1.0 chain'
        """
        # Extract parameters
        query_text = extract_param(query, default="")
        collection = extract_param(collection, default="proposals")
        num_results = extract_param(num_results, default=Config.DEFAULT_SEARCH_RESULTS)
        
        if not query_text:
            logger.warning("Empty search query provided")
            return []
        
        logger.info(f"Searching indexed documents for: {query_text} in collection: {collection}")
        
        # Determine site filters based on collection
        site_filters = self._get_site_filters(collection)
        
        headers = self._get_headers()
        payload = self._create_search_payload(query_text, num_results, site_filters)
        
        return self._execute_search(payload, headers, "indexed search", include_full_content=True)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for API requests.
        
        Returns:
            Dictionary containing request headers
        """
        return {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json"
        }
    
    def _create_search_payload(self, query: str, num_results: int, 
                              site_filters: List[str] = None) -> Dict[str, Any]:
        """Create the payload for search API requests.
        
        Args:
            query: The search query
            num_results: Maximum number of results to return
            site_filters: Optional list of sites to filter results
            
        Returns:
            Dictionary containing the search payload
        """
        payload = {
            "query": query,
            "numResults": num_results,
            "useAutoprompt": True
        }
        
        if site_filters:
            payload["filters"] = {"site": site_filters}
            
        return payload
    
    def _get_site_filters(self, collection: str) -> List[str]:
        """Get site filters based on collection type.
        
        Args:
            collection: The collection type ("proposals" or "governance")
            
        Returns:
            List of site filters
        """
        if collection.lower() == "proposals":
            return ["ethereum.org", "forum.ethereum.org", "eips.ethereum.org"]
        elif collection.lower() == "governance":
            return ["governance.aave.com", "gov.uniswap.org", "forum.ethereum.org"]
        return []
    
    def _execute_search(self, payload: Dict[str, Any], headers: Dict[str, str], 
                        search_type: str, include_full_content: bool = False) -> List[Dict[str, str]]:
        """Execute a search request and process the results.
        
        Args:
            payload: The search payload
            headers: The request headers
            search_type: Type of search for logging purposes
            include_full_content: Whether to include full content in results
            
        Returns:
            List of formatted search results
        """
        try:
            logger.debug(f"Making API request to {self.exa_api_url} for {search_type}")
            response = requests.post(self.exa_api_url, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])
            
            if not results:
                logger.warning(f"No results found for {search_type}")
                return []
            
            logger.info(f"Found {len(results)} results for {search_type}")
            
            # Format results based on search type
            if include_full_content:
                formatted_results = [{
                    "title": result.get("title", "No title"),
                    "content": result.get("text", ""),
                    "source": result.get("url", "")
                } for result in results]
            else:
                formatted_results = [{
                    "title": result.get("title", "No title"),
                    "snippet": result.get("text", "")[:500],  # Limit snippet length
                    "url": result.get("url", "")
                } for result in results]
            
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error in {search_type}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error in {search_type}: {str(e)}")
            return []

class IndexerTool:
    """Tool for accessing canonical indexers like EIP GitHub, BIPs, Forum API using Exa API."""
    
    def __init__(self):
        """Initialize the IndexerTool with API credentials.
        
        Raises:
            ValueError: If the required API key is not found in environment variables
        """
        self.exa_api_key = Config.EXA_API_KEY
        self.exa_api_url = Config.EXA_API_URL
        self.github_api_url = "https://api.github.com"
        self.forum_api_url = "https://forum-api.example.com"  # Placeholder URL
        
        if not self.exa_api_key:
            logger.error("EXA_API_KEY not found in environment variables")
            raise ValueError("EXA_API_KEY is required for IndexerTool to function properly")
            
        logger.info("IndexerTool initialized successfully")
    
    @cache_api_call(ttl=Config.DOCUMENT_CACHE_TTL)
    def fetch_eip(self, eip_number: Union[int, str, Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch information about an Ethereum Improvement Proposal using Exa API.
        
        Args:
            eip_number: The EIP number to fetch
            
        Returns:
            Dictionary containing EIP details
        """
        if not eip_number:
            logger.error("No EIP number provided")
            return {
                "eip": "unknown",
                "title": "Unknown EIP",
                "author": "Unknown",
                "status": "Unknown",
                "content": "Error: No EIP number provided",
                "url": "https://eips.ethereum.org/EIPS/"
            }
        
        logger.info(f"Fetching EIP-{eip_number} information")
        
        # Use Exa API to search for the EIP
        headers = {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": f"EIP-{eip_number} ethereum improvement proposal",
            "numResults": 1,
            "useAutoprompt": True,
            "filters": {
                "site": ["ethereum.org", "github.com/ethereum/EIPs"]
            }
        }
        
        try:
            logger.debug(f"Making API request to {self.exa_api_url} for EIP-{eip_number}")
            response = requests.post(self.exa_api_url, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])
            
            if not results:
                logger.warning(f"No information found for EIP-{eip_number}")
                return {
                    "eip": eip_number,
                    "title": f"EIP-{eip_number} (Not Found)",
                    "author": "Unknown",
                    "status": "Unknown",
                    "content": f"No information found for EIP-{eip_number}",
                    "url": f"https://eips.ethereum.org/EIPS/eip-{eip_number}"
                }
            
            result = results[0]
            logger.info(f"Found information for EIP-{eip_number}")
            
            # Extract author and status from the content if possible
            content = result.get("text", "")
            author = "Unknown"
            status = "Unknown"
            
            # Try to extract author
            author_match = re.search(r'Author:\s*([^\n]+)', content)
            if author_match:
                author = author_match.group(1).strip()
                logger.debug(f"Extracted author: {author}")
            
            # Try to extract status
            status_match = re.search(r'Status:\s*([^\n]+)', content)
            if status_match:
                status = status_match.group(1).strip()
                logger.debug(f"Extracted status: {status}")
            
            eip_data = {
                "eip": eip_number,
                "title": result.get("title", f"EIP-{eip_number}"),
                "author": author,
                "status": status,
                "content": content,
                "url": result.get("url", f"https://eips.ethereum.org/EIPS/eip-{eip_number}")
            }
            
            return eip_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching EIP-{eip_number}: {str(e)}")
            return self._create_error_response("eip", eip_number, str(e))
        except Exception as e:
            logger.error(f"Error fetching EIP-{eip_number}: {str(e)}")
            return self._create_error_response("eip", eip_number, str(e))
    
    def _fetch_document(self, query: str, site_filters: List[str], 
                       document_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a document using Exa API.
        
        Args:
            query: The search query
            site_filters: List of sites to filter results
            document_id: Document identifier for logging
            
        Returns:
            Dictionary containing the document data or None if not found
            
        Raises:
            requests.exceptions.RequestException: If there's an error with the API request
        """
        headers = {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "numResults": 1,
            "useAutoprompt": True,
            "filters": {
                "site": site_filters
            }
        }
        
        logger.debug(f"Making API request to {self.exa_api_url} for {document_id}")
        response = requests.post(self.exa_api_url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        if not results:
            logger.warning(f"No results found for {document_id}")
            return None
            
        logger.info(f"Found information for {document_id}")
        return results[0]
    
    def _extract_document_metadata(self, content: str, document_type: str) -> Dict[str, str]:
        """Extract metadata from document content using regex patterns.
        
        Args:
            content: The document content
            document_type: Type of document ("eip", "bip", etc.)
            
        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {}
        
        # Extract author
        author_match = re.search(r"Author[s]?:\s*([^\n]+)", content)
        if author_match:
            metadata["author"] = author_match.group(1).strip()
            logger.debug(f"Extracted author: {metadata['author']}")
        
        # Extract status
        status_match = re.search(r"Status:\s*([^\n]+)", content)
        if status_match:
            metadata["status"] = status_match.group(1).strip()
            logger.debug(f"Extracted status: {metadata['status']}")
        
        return metadata
    
    def _create_not_found_response(self, doc_type: str, doc_id: Any) -> Dict[str, Any]:
        """Create a response for when a document is not found.
        
        Args:
            doc_type: Document type ("eip", "bip", etc.)
            doc_id: Document identifier
            
        Returns:
            Dictionary containing not found response
        """
        if doc_type == "eip":
            return {
                "eip": doc_id,
                "title": f"EIP-{doc_id} (Not Found)",
                "author": "Unknown",
                "status": "Unknown",
                "content": f"No information found for EIP-{doc_id}",
                "url": f"https://eips.ethereum.org/EIPS/eip-{doc_id}"
            }
        elif doc_type == "bip":
            return {
                "bip": doc_id,
                "title": f"BIP-{doc_id} (Not Found)",
                "author": "Unknown",
                "status": "Unknown",
                "content": f"No information found for BIP-{doc_id}",
                "url": f"https://github.com/bitcoin/bips/blob/master/bip-{doc_id}.mediawiki"
            }
        else:
            return {
                "id": doc_id,
                "title": f"Document (Not Found)",
                "content": f"No information found for document {doc_id}"
            }
    
    def _create_error_response(self, doc_type: str, doc_id: Any, error_msg: str = "") -> Dict[str, Any]:
        """Create a response for when an error occurs.
        
        Args:
            doc_type: Document type ("eip", "bip", etc.)
            doc_id: Document identifier
            error_msg: Error message
            
        Returns:
            Dictionary containing error response
        """
        if doc_type == "eip":
            return {
                "eip": doc_id,
                "title": f"EIP-{doc_id} (Error)",
                "author": "Unknown",
                "status": "Unknown",
                "content": f"Error fetching EIP: {error_msg}",
                "url": f"https://eips.ethereum.org/EIPS/eip-{doc_id}"
            }
        elif doc_type == "bip":
            return {
                "bip": doc_id,
                "title": f"BIP-{doc_id} (Error)",
                "author": "Unknown",
                "status": "Unknown",
                "content": f"Error fetching BIP: {error_msg}",
                "url": f"https://github.com/bitcoin/bips/blob/master/bip-{doc_id}.mediawiki"
            }
        else:
            return {
                "id": doc_id,
                "title": f"Document (Error)",
                "content": f"Error fetching document: {error_msg}"
            }
    
    @cache_api_call(ttl=Config.DOCUMENT_CACHE_TTL)
    def fetch_bip(self, bip_number: Union[int, str, Dict[str, Any]]) -> Dict[str, Any]:
        """Fetch information about a Bitcoin Improvement Proposal using Exa API.
        
        Args:
            bip_number: The BIP number to fetch
            
        Returns:
            Dictionary containing BIP details including title, author, status, content, and URL
            
        Example:
            >>> indexer_tool = IndexerTool()
            >>> bip_info = indexer_tool.fetch_bip(2)
            >>> print(bip_info["title"])
            'BIP 2: Title'
        """
        # Extract parameter
        bip_number = extract_param(bip_number, key="bip_number")
        
        if not bip_number:
            logger.warning("No BIP number provided")
            return self._create_error_response("bip", "No BIP number provided")
        
        logger.info(f"Fetching BIP-{bip_number} information")
        
        # Construct a specific query to find the BIP
        query = f"BIP-{bip_number} bitcoin improvement proposal full text"
        site_filters = ["github.com/bitcoin/bips"]
        
        try:
            # Fetch document using generic method
            result = self._fetch_document(query, site_filters, f"BIP-{bip_number}")
            
            if not result:
                return self._create_not_found_response("bip", bip_number)
            
            # Extract metadata using regex patterns
            content = result.get("text", "")
            metadata = self._extract_document_metadata(content, document_type="bip")
            
            # Create response
            bip_data = {
                "bip": bip_number,
                "title": result.get("title", f"BIP-{bip_number}"),
                "author": metadata.get("author", "Unknown"),
                "status": metadata.get("status", "Unknown"),
                "content": content,
                "url": result.get("url", f"https://github.com/bitcoin/bips/blob/master/bip-{bip_number}.mediawiki")
            }
            
            return bip_data
            
        except Exception as e:
            logger.error(f"Error fetching BIP-{bip_number}: {str(e)}")
            return self._create_error_response("bip", bip_number, str(e))
    
    @cache_api_call(ttl=Config.DOCUMENT_CACHE_TTL)
    def fetch_forum_post(self, forum_id=None, post_id=None) -> Dict[str, Any]:
        """Fetch a post from a forum API using Exa API.
        
        Args:
            forum_id: The forum identifier (e.g., "ethereum", "bitcoin")
            post_id: The post identifier
            
        Returns:
            Dictionary containing forum post details including title, author, content, date, and votes
            
        Example:
            >>> indexer_tool = IndexerTool()
            >>> post_info = indexer_tool.fetch_forum_post("ethereum", "governance")
            >>> print(post_info["title"])
            'Ethereum Governance Discussion'
        """
        # Extract parameters with defaults
        forum_id = extract_param(forum_id, default=None)
        post_id = extract_param(post_id, default="governance")
        
        # Handle combined forum_id/post_id format (e.g., "ethereum/governance")
        if isinstance(forum_id, str) and '/' in forum_id:
            parts = forum_id.split('/')
            forum_id = parts[0]
            post_id = parts[1] if len(parts) > 1 else post_id
        
        # If we still don't have a forum_id, return a default response
        if not forum_id:
            logger.warning("No forum_id provided for fetching forum post")
            return self._create_forum_error_response(None, post_id, "No forum_id provided")
        
        logger.info(f"Fetching forum post: {post_id} from forum {forum_id}")
        
        # Get site filters based on forum_id
        site_filters = self._get_forum_site_filters(forum_id)
        
        # Construct a query based on forum_id and post_id
        query = f"{forum_id} forum {post_id} governance proposal"
        
        try:
            # Fetch document using generic method
            result = self._fetch_document(query, site_filters, f"Forum {forum_id}/{post_id}")
            
            if not result:
                return self._create_forum_not_found_response(forum_id, post_id)
            
            # Extract metadata from content
            content = result.get("text", "")
            metadata = self._extract_forum_metadata(content)
            
            forum_data = {
                "title": result.get("title", f"{forum_id.capitalize()} Forum Post"),
                "author": metadata.get("author", "Unknown"),
                "content": content,
                "date": metadata.get("date", ""),
                "url": result.get("url", ""),
                "votes": metadata.get("votes", {"for": 0, "against": 0}),
                "comments": metadata.get("comments", 0)
            }
            
            return forum_data
            
        except Exception as e:
            logger.error(f"Error fetching forum post {forum_id}/{post_id}: {str(e)}")
            return self._create_forum_error_response(forum_id, post_id, str(e))
    
    def _get_forum_site_filters(self, forum_id: str) -> List[str]:
        """Get site filters based on forum type.
        
        Args:
            forum_id: The forum identifier
            
        Returns:
            List of site filters
        """
        forum_id = forum_id.lower()
        if forum_id == "ethereum":
            return ["forum.ethereum.org", "ethereum.org"]
        elif forum_id == "bitcoin":
            return ["bitcointalk.org", "bitcoin.org"]
        elif forum_id == "aave":
            return ["governance.aave.com"]
        elif forum_id == "uniswap":
            return ["gov.uniswap.org"]
        else:
            # Default case - try to guess the domain
            return [f"{forum_id}.org", f"forum.{forum_id}.org", f"gov.{forum_id}.org"]
    
    def _extract_forum_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from forum post content.
        
        Args:
            content: The forum post content
            
        Returns:
            Dictionary containing extracted metadata
        """
        metadata = {}
        
        # Try to extract author
        author_match = re.search(r'(?:Author|Posted by|From):\s*([^\n,]+)', content)
        if author_match:
            metadata["author"] = author_match.group(1).strip()
            logger.debug(f"Extracted author: {metadata['author']}")
        
        # Try to extract date
        date_match = re.search(r'(?:Date|Posted on|Time):\s*([^\n]+)', content)
        if date_match:
            metadata["date"] = date_match.group(1).strip()
            logger.debug(f"Extracted date: {metadata['date']}")
        
        # Try to extract vote counts
        votes = {"for": 0, "against": 0}
        votes_match = re.search(r'(?:Votes|Poll):[^\n]*?(\d+)[^\n]*?for[^\n]*?(\d+)[^\n]*?against', content, re.IGNORECASE)
        if votes_match:
            try:
                votes["for"] = int(votes_match.group(1))
                votes["against"] = int(votes_match.group(2))
                logger.debug(f"Extracted votes: {votes['for']} for, {votes['against']} against")
            except (ValueError, IndexError) as e:
                logger.debug(f"Error parsing vote counts: {str(e)}")
        metadata["votes"] = votes
        
        # Try to extract comment count
        comments_match = re.search(r'(\d+)\s*(?:comments|replies)', content, re.IGNORECASE)
        if comments_match:
            try:
                metadata["comments"] = int(comments_match.group(1))
                logger.debug(f"Extracted comment count: {metadata['comments']}")
            except (ValueError, IndexError) as e:
                logger.debug(f"Error parsing comment count: {str(e)}")
        else:
            metadata["comments"] = 0
            
        return metadata
    
    def _create_forum_not_found_response(self, forum_id: str, post_id: str) -> Dict[str, Any]:
        """Create a response for when a forum post is not found.
        
        Args:
            forum_id: The forum identifier
            post_id: The post identifier
            
        Returns:
            Dictionary containing not found response
        """
        return {
            "title": f"{forum_id.capitalize() if forum_id else 'Unknown'} Forum Post Not Found",
            "author": "Unknown",
            "content": f"No forum post found for {forum_id}/{post_id}",
            "date": "",
            "votes": {"for": 0, "against": 0},
            "comments": 0
        }
    
    def _create_forum_error_response(self, forum_id: str, post_id: str, error_msg: str) -> Dict[str, Any]:
        """Create a response for when an error occurs fetching a forum post.
        
        Args:
            forum_id: The forum identifier
            post_id: The post identifier
            error_msg: Error message
            
        Returns:
            Dictionary containing error response
        """
        return {
            "title": f"{forum_id.capitalize() if forum_id else 'Unknown'} Forum Post (Error)",
            "author": "Unknown",
            "content": f"Error fetching forum post: {error_msg}",
            "date": "",
            "votes": {"for": 0, "against": 0},
            "comments": 0
        }
    

class ReaderTool:
    """Tool for reading documents and clipping quotes from web content.
    
    This class provides methods to fetch and process documents from the web,
    including specialized handling for PDFs and regular web pages. It also
    offers functionality to extract relevant quotes from documents based on
    specified keywords.
    
    Attributes:
        exa_api_key: API key for Exa service
        exa_api_url: URL endpoint for Exa API
    """
    
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
    def read_document(self, url: Union[str, Dict[str, Any], None] = None) -> Dict[str, Any]:
        """Read a document from a URL.
        
        Args:
            url: The URL of the document to read
            
        Returns:
            Dictionary containing document content and metadata
            
        Example:
            >>> reader_tool = ReaderTool()
            >>> doc = reader_tool.read_document("https://ethereum.org/en/whitepaper/")
            >>> print(doc["metadata"]["title"])
            'Ethereum Whitepaper'
        """
        # Extract URL parameter
        url_str = extract_param(url, key="url", default=None)
        
        if not url_str:
            logger.warning("No URL provided for reading document")
            return self._create_document_error_response("No URL provided for reading document.")
        
        # Ensure url is a string and properly formatted
        url_str = str(url_str).strip()
        
        logger.info(f"Reading document: {url_str}")
        
        if not url_str.startswith('http'):
            logger.warning(f"Invalid URL format: {url_str}")
            return self._create_document_error_response(
                "Invalid URL format. URL must start with http or https.",
                url=url_str
            )
        
        try:
            # Determine document type and use appropriate handler
            if self._is_pdf_url(url_str):
                return self._read_pdf_document(url_str)
            else:
                return self._read_web_document(url_str)
                
        except Exception as e:
            logger.error(f"Error reading document: {str(e)}")
            return self._create_document_error_response(f"Error reading document: {str(e)}", url=url_str)
    
    def _is_pdf_url(self, url: str) -> bool:
        """Check if the URL points to a PDF document.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL appears to be a PDF, False otherwise
        """
        return url.lower().endswith('.pdf') or '/pdf/' in url.lower() or 'type=pdf' in url.lower()
    
    def _read_pdf_document(self, url: str) -> Dict[str, Any]:
        """Read a PDF document from a URL.
        
        Args:
            url: The URL of the PDF document
            
        Returns:
            Dictionary containing the document content and metadata
            
        Raises:
            Exception: If there's an error reading the PDF
        """
        logger.info(f"Reading PDF document: {url}")
        
        # Use requests to download the PDF content
        response = requests.get(url)
        response.raise_for_status()
        
        # Save to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        try:
            # Try to use PyPDF2 for PDF parsing
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(temp_path)
                content = ""
                
                # Extract text from each page
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        content += f"Page {i+1}:\n{page_text}\n\n"
                    else:
                        content += f"Page {i+1}: [No extractable text]\n\n"
                
                logger.info(f"Successfully extracted text from PDF: {url} ({len(reader.pages)} pages)")
                
                # Create document metadata
                title = url.split("/")[-1]
                if title.lower().endswith('.pdf'):
                    title = title[:-4]  # Remove .pdf extension
                
                return {
                    "content": content,
                    "metadata": {
                        "source": url,
                        "title": title,
                        "type": "pdf",
                        "pages": len(reader.pages)
                    }
                }
                
            except ImportError:
                logger.warning("PyPDF2 not installed, falling back to Exa API")
                return self._read_web_document(url)
                
        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            raise
        finally:
            # Always clean up the temporary file
            import os
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _read_web_document(self, url: str) -> Dict[str, Any]:
        """Read a web document from a URL using Exa API.
        
        Args:
            url: The URL of the web document
            
        Returns:
            Dictionary containing the document content and metadata
            
        Raises:
            Exception: If there's an error reading the document
        """
        logger.info(f"Reading web document: {url}")
        
        headers = {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json"
        }
        
        # Extract the domain for filtering
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        logger.debug(f"Making Exa API request for URL: {url} (domain: {domain})")
        
        payload = {
            "query": url,  # Use the URL itself as the query
            "numResults": 1,
            "useAutoprompt": False,  # Disable autoprompt for exact URL matching
            "filters": {
                "site": [domain]
            }
        }
        
        response = requests.post(self.exa_api_url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        if not results:
            logger.warning(f"No content found for URL: {url}")
            return self._create_document_error_response(f"No content found for URL: {url}", url=url)
            
        result = results[0]
        logger.info(f"Successfully retrieved content for URL: {url}")
        
        return {
            "content": result.get("text", ""),
            "metadata": {
                "source": url,
                "title": result.get("title", ""),
                "published_date": result.get("publishedDate", ""),
                "type": "web"
            }
        }
    
    def _create_document_error_response(self, error_message: str, url: str = "unknown") -> Dict[str, Any]:
        """Create an error response for document reading failures.
        
        Args:
            error_message: The error message
            url: The URL that was being accessed
            
        Returns:
            Dictionary containing error information
        """
        return {
            "content": error_message,
            "metadata": {
                "source": url,
                "title": "Error Reading Document",
                "type": "error"
            }
        }
    
    @cache_api_call(ttl=Config.DOCUMENT_CACHE_TTL)
    def clip_quotes(self, content: Union[str, Dict[str, Any]], keywords: Union[List[str], str, None] = None) -> List[Dict[str, str]]:
        """Extract quotes from content based on keywords.
        
        Args:
            content: The text content to extract quotes from, or a dictionary containing content
            keywords: List of keywords to search for in the content
            
        Returns:
            List of dictionaries containing quotes and their associated keywords
            
        Example:
            >>> reader_tool = ReaderTool()
            >>> doc = reader_tool.read_document("https://ethereum.org/en/whitepaper/")
            >>> quotes = reader_tool.clip_quotes(doc["content"], ["blockchain", "consensus"])
            >>> print(len(quotes))
            5
        """
        # Extract parameters
        content_text = extract_param(content, key="content", default="")
        keywords_list = extract_param(keywords, default=Config.DEFAULT_KEYWORDS)
        
        # Convert single keyword to list if needed
        if isinstance(keywords_list, str):
            keywords_list = [keywords_list]
            logger.debug(f"Converted single keyword to list: {keywords_list}")
        
        logger.info(f"Clipping quotes with {len(keywords_list)} keywords: {keywords_list}")
        
        if not content_text or not isinstance(content_text, str):
            logger.warning(f"Invalid content provided: {type(content_text)}")
            return []
        
        quotes = []
        for keyword in keywords_list:
            # Find sentences containing the keyword using improved regex pattern
            pattern = f"[^.!?]*{re.escape(keyword)}[^.!?]*[.!?]"
            matches = re.findall(pattern, content_text, re.IGNORECASE)
            
            logger.debug(f"Found {len(matches)} matches for keyword '{keyword}'")
            
            for match in matches:
                quote = match.strip()
                if len(quote) > 10:  # Only include substantial quotes
                    quotes.append({
                        "quote": quote,
                        "keyword": keyword
                    })
        
        logger.info(f"Extracted {len(quotes)} total quotes from content")
        return quotes


class RAGTool:
    """Tool for RAG (Retrieval-Augmented Generation) over internal archive.
    
    This class provides methods to perform Retrieval-Augmented Generation (RAG)
    using external APIs. It combines search capabilities with language model
    integration to provide context-aware responses.
    
    Attributes:
        openai_api_key: API key for OpenRouter service
        exa_api_key: API key for Exa service
        exa_api_url: URL endpoint for Exa API
        client: OpenAI client configured for OpenRouter
    """
    
    def __init__(self):
        """Initialize the RAGTool with API credentials.
        
        Raises:
            ValueError: If required API keys are not found in environment variables
        """
        self.openai_api_key = Config.OPENROUTER_API_KEY
        self.exa_api_key = Config.EXA_API_KEY
        self.exa_api_url = Config.EXA_API_URL
        
        if not self.openai_api_key:
            logger.error("OPENROUTER_API_KEY not found in environment variables")
            raise ValueError("OPENROUTER_API_KEY is required for RAGTool to function properly")
            
        if not self.exa_api_key:
            logger.error("EXA_API_KEY not found in environment variables")
            raise ValueError("EXA_API_KEY is required for RAGTool to function properly")
        
        # Initialize OpenAI client with OpenRouter API
        from openai import OpenAI
        self.client = OpenAI(
            api_key=self.openai_api_key,
            base_url=Config.OPENROUTER_API_URL
        )
        logger.info("RAGTool initialized successfully")
    
    @cache_api_call(ttl=Config.INDEXED_SEARCH_CACHE_TTL)
    def _rag_query_impl(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Query the RAG system with a question.
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of dictionaries containing content, source, and score
        """
        logger.info(f"RAG query: {query} (k={k})")
        
        # First, use Exa to search for relevant content
        headers = {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "numResults": k,
            "useAutoprompt": True
        }
        
        try:
            # Get relevant documents from Exa
            logger.debug(f"Making API request to {self.exa_api_url} for RAG query")
            response = requests.post(self.exa_api_url, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json().get("results", [])
            
            if not results:
                logger.warning(f"No results found for RAG query: {query}")
                return []
            
            logger.info(f"Found {len(results)} results for RAG query")
            
            # Format the results
            formatted_results = []
            for i, result in enumerate(results):
                # Calculate a mock score based on position (better ranking = higher score)
                score = 1.0 - (i * 0.05)  # Simple decay function
                
                formatted_results.append({
                    "content": result.get("text", ""),
                    "source": result.get("url", f"source_{i}"),
                    "score": score
                })
            
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error in RAG query: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            return []
    
    @cache_api_call(ttl=Config.INDEXED_SEARCH_CACHE_TTL)
    def rag_query(self, query: Union[str, Dict[str, Any]], k: int = 3) -> List[Dict[str, Any]]:
        """Wrapper for rag_query that handles different input types
        
        Args:
            query: The search query or a dictionary containing the query
            k: Number of results to return or a dictionary containing k
            
        Returns:
            List of dictionaries containing content, source, and score
        """
        # Handle the case where query is a dictionary
        if isinstance(query, dict):
            if 'query' in query:
                query_text = query['query']
                logger.debug(f"Extracted query from dictionary: {query_text}")
                if isinstance(k, dict) and 'k' in k:
                    k = k['k']
                    logger.debug(f"Extracted k from dictionary: {k}")
                return self._rag_query_impl(query_text, k)
            elif 'self' in query:
                query_text = query['self']
                logger.debug(f"Extracted query from 'self' field: {query_text}")
                if isinstance(k, dict) and 'k' in k:
                    k = k['k']
                    logger.debug(f"Extracted k from dictionary: {k}")
                return self._rag_query_impl(query_text, k)
        
        # Handle the case where k is a dictionary
        if isinstance(k, dict) and 'k' in k:
            k = k['k']
            logger.debug(f"Extracted k from dictionary: {k}")
        
        return self._rag_query_impl(query, k)
