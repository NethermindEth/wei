from typing import Dict, Any, List, Tuple, Optional
import os
import logging
import time
import re
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from agent_state import AgentState, ClaimEvidence, Task
import networkx as nx
from agent_tools import SearchTool, IndexerTool, ReaderTool, RAGTool

# Import Langfuse for tracing
from langfuse_setup import trace_llm_call

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_nodes.log')
    ]
)
logger = logging.getLogger('agent_nodes')

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Initialize tools
# Create instances of tool classes
try:
    search_tool_instance = SearchTool()
    indexer_tool_instance = IndexerTool()
    reader_tool_instance = ReaderTool()
    rag_tool_instance = RAGTool()
    logger.info("All tool instances initialized successfully")
except Exception as e:
    logger.error(f"Error initializing tool instances: {str(e)}")
    raise

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

def fetch_forum_post(forum_id: str, post_id: str) -> Dict[str, Any]:
    """Fetch a post from a forum API.
    
    Args:
        forum_id: The forum identifier (e.g., "ethereum", "bitcoin")
        post_id: The post identifier
        
    Returns:
        Dictionary containing forum post details
    """
    try:
        logger.info(f"Fetching forum post: {post_id} from forum {forum_id}")
        result = indexer_tool_instance.fetch_forum_post(forum_id, post_id)
        logger.info(f"Successfully fetched forum post: {post_id}")
        return result
    except Exception as e:
        logger.error(f"Error fetching forum post {post_id} from {forum_id}: {str(e)}")
        return {
            "id": post_id,
            "forum": forum_id,
            "title": "Forum Post (Error)",
            "author": "Unknown",
            "content": f"Error fetching forum post: {str(e)}",
            "date": "Unknown",
            "url": "",
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
        content_length = len(result.get("content", ""))
        logger.info(f"Successfully read document: {url} (content length: {content_length})")
        return result
    except Exception as e:
        logger.error(f"Error reading document {url}: {str(e)}")
        return {
            "content": f"Error reading document: {str(e)}",
            "metadata": {"source": url, "error": str(e)}
        }

def clip_quotes(content: str, keywords: Optional[List[str]] = None) -> List[Dict[str, str]]:
    """Extract quotes from content based on keywords.
    
    Args:
        content: The text content to extract quotes from
        keywords: List of keywords to search for in the content
        
    Returns:
        List of extracted quotes with their associated keywords
    """
    try:
        if keywords:
            logger.info(f"Clipping quotes with keywords: {keywords}")
        else:
            logger.info("Clipping quotes with default keywords")
        results = reader_tool_instance.clip_quotes(content, keywords)
        logger.info(f"Extracted {len(results)} quotes")
        return results
    except Exception as e:
        logger.error(f"Error clipping quotes: {str(e)}")
        return []

def rag_query(query: str, k: int = 3) -> List[Dict[str, Any]]:
    """Query the RAG system with a question.
    
    Args:
        query: The query string
        k: Number of results to return
        
    Returns:
        List of relevant documents with content, source, and score
    """
    try:
        logger.info(f"RAG query: {query} (k={k})")
        results = rag_tool_instance.rag_query(query, k)
        logger.info(f"RAG query returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error in RAG query: {str(e)}")
        return []

# Define LLM configuration parameters
LLM_CONFIG = {
    "analysis": {
        "model": "gpt-4o-mini",
        "temperature": 0.2,
        "max_tokens": 2000,
        "timeout": 60,
        "retry_attempts": 3
    },
    "roadmap": {
        "model": "perplexity/sonar-pro",
        "temperature": 0.3,
        "max_tokens": 2500,
        "timeout": 90,
        "retry_attempts": 3
    }
}

# Initialize LLMs with different configurations
try:
    # For analysis components, use OpenRouter API key
    analysis_llm = ChatOpenAI(
        model=LLM_CONFIG["analysis"]["model"],
        temperature=LLM_CONFIG["analysis"]["temperature"],
        max_tokens=LLM_CONFIG["analysis"]["max_tokens"],
        api_key=os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        timeout=LLM_CONFIG["analysis"]["timeout"],
        max_retries=LLM_CONFIG["analysis"]["retry_attempts"]
    )
    logger.info(f"Initialized analysis LLM with model: {LLM_CONFIG['analysis']['model']}")
    
    # For roadmap modeling, use Perplexity/Sonar-Pro
    roadmap_llm = ChatOpenAI(
        model=LLM_CONFIG["roadmap"]["model"],
        temperature=LLM_CONFIG["roadmap"]["temperature"],
        max_tokens=LLM_CONFIG["roadmap"]["max_tokens"],
        api_key=os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        timeout=LLM_CONFIG["roadmap"]["timeout"],
        max_retries=LLM_CONFIG["roadmap"]["retry_attempts"]
    )
    logger.info(f"Initialized roadmap LLM with model: {LLM_CONFIG['roadmap']['model']}")
    
except Exception as e:
    logger.error(f"Error initializing LLM models: {str(e)}")
    raise

def planning_agent(state: AgentState) -> AgentState:
    """Planning Agent: Creates a research plan based on the proposal.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with planning results
    """
    try:
        logger.info("==== PLANNING AGENT ====")
        logger.info("Creating a detailed research plan for the proposal...")
        
        # Validate required state fields
        if 'proposal' not in state:
            logger.error("Missing 'proposal' in state")
            raise ValueError("Missing 'proposal' in state")
        if 'metadata' not in state:
            logger.error("Missing 'metadata' in state")
            raise ValueError("Missing 'metadata' in state")
        
        # Extract metadata safely with defaults
        metadata = state['metadata']
        title = metadata.get('title', 'Untitled')
        protocol = metadata.get('protocol', 'Unknown')
        category = metadata.get('category', 'Unknown')
        author = metadata.get('author', 'Unknown')
        date_submitted = metadata.get('date_submitted', 'Unknown')
        
        system_prompt = """You are a Planning Agent for proposal analysis. 
        Your job is to create a detailed research plan based on the proposal and metadata provided.
        Identify key areas that need investigation, questions that need answers, and potential sources of information.
        """
        
        human_message = f"""
        Proposal: {state['proposal']}
        
        Metadata:
        - Title: {title}
        - Protocol: {protocol}
        - Category: {category}
        - Author: {author}
        - Date Submitted: {date_submitted}
        
        Create a detailed research plan for analyzing this proposal.
        """
        
        logger.info(f"Analyzing proposal: {title}")
        logger.info(f"Protocol: {protocol}")
        logger.info(f"Category: {category}")
        logger.info(f"Sending query to LLM ({LLM_CONFIG['analysis']['model']}) for planning...")
        
        # Start timing for latency measurement
        start_time = time.time()
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        # Use analysis_llm for planning
        try:
            response = analysis_llm.invoke(messages)
            
            # Calculate latency in milliseconds
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"LLM response received in {latency_ms}ms")
            
            # Trace the LLM call with Langfuse
            trace_llm_call(
                model_name=LLM_CONFIG['analysis']['model'],
                prompt=human_message,
                completion=response.content,
                latency_ms=latency_ms,
                metadata={
                    "agent": "planning_agent",
                    "proposal_title": title,
                    "protocol": protocol
                }
            )
            
            # Log a preview of the response
            response_preview = response.content[:500] + "..." if len(response.content) > 500 else response.content
            logger.info(f"Planning Agent Response Preview: {response_preview}")
            
            # Update state with planning results
            state["messages"] = state.get("messages", []) + [response]
            
        except Exception as e:
            logger.error(f"Error invoking LLM for planning: {str(e)}")
            # Create a fallback response
            from langchain_core.messages import AIMessage
            fallback_content = f"Error generating research plan: {str(e)}. Please proceed with basic analysis of the proposal."
            fallback_response = AIMessage(content=fallback_content)
            state["messages"] = state.get("messages", []) + [fallback_response]
            
        return state
        
    except Exception as e:
        logger.error(f"Error in planning_agent: {str(e)}")
        # Return state with minimal modifications to allow pipeline to continue
        if "messages" not in state:
            from langchain_core.messages import AIMessage
            state["messages"] = [AIMessage(content="Error in planning stage. Proceeding with default analysis plan.")]
        return state

def search_tool_node(state: AgentState) -> AgentState:
    """Tool Node: Search web and indexed resources.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with search results
    """
    try:
        logger.info("==== SEARCH TOOL NODE ====")
        logger.info("Searching web and indexed resources for relevant information...")
        
        # Extract search queries from the planning agent's output
        if "messages" not in state or not state["messages"]:
            logger.warning("No messages found from planning agent. Using default planning output.")
            planning_output = "Research proposal impact and similar proposals."
        else:
            planning_output = state["messages"][-1].content
            logger.info("Extracting search queries from planning output")
            planning_excerpt = planning_output[:200] + "..." if len(planning_output) > 200 else planning_output
            logger.debug(f"Planning output excerpt: {planning_excerpt}")
        
        # Extract queries from the planning output
        # Look for specific keywords like "search for" or "investigate"
        planning_text = planning_output.lower()
        
        # Extract search queries from the planning output
        web_queries = []
        indexed_queries = []
        
        # Get metadata safely with defaults
        metadata = state.get('metadata', {})
        protocol = metadata.get('protocol', 'blockchain')
        category = metadata.get('category', 'governance')
        
        # Look for search instructions in the planning output
        search_keywords = ["search for", "research", "investigate", "find", "look up", "explore"]
        if any(keyword in planning_text for keyword in search_keywords):
            # Try to extract specific queries using regex
            import re
            search_patterns = [
                r"search\s+for\s+['\"]([^'\"]+)['\"]?",
                r"research\s+['\"]([^'\"]+)['\"]?",
                r"investigate\s+['\"]([^'\"]+)['\"]?",
                r"find\s+information\s+(?:about|on)\s+['\"]([^'\"]+)['\"]?"
            ]
            
            for pattern in search_patterns:
                matches = re.findall(pattern, planning_text)
                if matches:
                    web_queries.extend(matches)
            
            # If no specific queries found, use default queries based on metadata
            if not web_queries:
                logger.info("No specific search queries found. Using default queries based on metadata.")
                web_queries = [
                    f"{protocol} {category} proposal impact", 
                    f"{protocol} governance"
                ]
                indexed_queries = [
                    f"similar {protocol} proposals", 
                    f"{protocol} {category} precedents"
                ]
            else:
                # Generate indexed queries based on web queries
                indexed_queries = [f"{query} {protocol}" for query in web_queries[:2]]
        else:
            # Default queries based on the proposal metadata
            logger.info("No search instructions found. Using default queries based on metadata.")
            web_queries = [
                f"{protocol} {category} proposal impact", 
                f"{protocol} governance"
            ]
            indexed_queries = [
                f"similar {protocol} proposals", 
                f"{protocol} {category} precedents"
            ]
        
        logger.info("Executing search queries")
        
        # Search the web
        web_results = []
        for query in web_queries:
            logger.info(f"Searching web for: '{query}'")
            
            # Use our wrapper function instead of the tool method
            results = search_web(query)
            
            for result in results:
                logger.debug(f"Found: {result['title']}")
                logger.debug(f"URL: {result['url']}")
                snippet = result.get('snippet', '')[:100] + "..." if len(result.get('snippet', '')) > 100 else result.get('snippet', '')
                logger.debug(f"Snippet: {snippet}")
            
            web_results.extend(results)
        
        # Search indexed documents
        indexed_results = []
        for query in indexed_queries:
            logger.info(f"Searching indexed documents for: '{query}'")
            
            # Use our wrapper function instead of the tool method
            results = search_indexed(query)
            
            for result in results:
                logger.debug(f"Found: {result['title']}")
                logger.debug(f"URL: {result['source']}")
                content = result.get('content', '')[:100] + "..." if len(result.get('content', '')) > 100 else result.get('content', '')
                logger.debug(f"Content: {content}")
            
            indexed_results.extend(results)
        
        # Update state with search results
        state["search_results"] = web_results + indexed_results
        
        logger.info(f"Search complete. Found {len(web_results)} web results and {len(indexed_results)} indexed documents.")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in search_tool_node: {str(e)}")
        # Initialize search_results if not present to allow pipeline to continue
        if "search_results" not in state:
            state["search_results"] = []
        return state

def indexer_tool_node(state: AgentState) -> AgentState:
    """Tool Node: Access canonical indexers like EIP GitHub, BIPs, Forum API.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with indexed data
    """
    try:
        logger.info("==== INDEXER TOOL NODE ====")
        logger.info("Accessing canonical indexers for relevant documents...")
        
        # Determine which resources to fetch based on the proposal metadata
        indexed_data = []
        
        # Get metadata safely with defaults
        metadata = state.get('metadata', {})
        protocol = metadata.get('protocol', 'unknown').lower()
        title = metadata.get('title', '')
        
        logger.info(f"Processing protocol: {protocol}")
        
        # Fetch relevant EIP document if this is an Ethereum proposal
        if protocol == "ethereum":
            # Extract EIP number from the proposal title if available
            eip_number = None
            eip_match = re.search(r'EIP[- ]?([0-9]+)', title)
            if eip_match:
                eip_number = eip_match.group(1)
                logger.info(f"Found EIP number in title: EIP-{eip_number}")
            else:
                # Use a default EIP that's relevant to governance
                eip_number = "1559"  # A well-known EIP
                logger.info(f"No EIP number found in title. Using default: EIP-{eip_number}")
                
            logger.info(f"Fetching EIP document: {eip_number}")
            
            try:
                # Use our wrapper function instead of the tool method
                eip_doc = fetch_eip(eip_number)
                eip_doc["type"] = "eip"  # Add type for consistency
                indexed_data.append(eip_doc)
                
                logger.info(f"Retrieved EIP: {eip_doc['title']}")
                logger.debug(f"Author(s): {eip_doc['author']}")
                logger.debug(f"Status: {eip_doc['status']}")
                content_excerpt = eip_doc['content'][:100] + "..." if len(eip_doc['content']) > 100 else eip_doc['content']
                logger.debug(f"Content excerpt: {content_excerpt}")
            except Exception as e:
                logger.error(f"Error fetching EIP: {str(e)}")
        
        # Fetch relevant BIP document if this is a Bitcoin proposal
        elif protocol == "bitcoin":
            # Extract BIP number from the proposal title if available
            bip_match = re.search(r'BIP[- ]?([0-9]+)', title)
            if bip_match:
                bip_number = bip_match.group(1)
                logger.info(f"Found BIP number in title: BIP-{bip_number}")
            else:
                # Use a default BIP that's relevant to governance
                bip_number = "8"  # BIP-8 is about block activation
                logger.info(f"No BIP number found in title. Using default: BIP-{bip_number}")
                
            logger.info(f"Fetching BIP document: {bip_number}")
            
            try:
                # Use our wrapper function instead of the tool method
                bip_doc = fetch_bip(bip_number)
                bip_doc["type"] = "bip"  # Add type for consistency
                indexed_data.append(bip_doc)
                
                logger.info(f"Retrieved BIP: {bip_doc['title']}")
                logger.debug(f"Author(s): {bip_doc['author']}")
                logger.debug(f"Status: {bip_doc['status']}")
                content_excerpt = bip_doc['content'][:100] + "..." if len(bip_doc['content']) > 100 else bip_doc['content']
                logger.debug(f"Content excerpt: {content_excerpt}")
            except Exception as e:
                logger.error(f"Error fetching BIP: {str(e)}")
        
        # Fetch relevant forum posts for any protocol
        logger.info(f"Fetching governance forum post for {protocol}")
        try:
            # Use our wrapper function instead of the tool method
            forum_id = protocol
            post_id = "governance"  # Generic post ID for governance topics
            forum_post = fetch_forum_post(forum_id, post_id)
            forum_post["forum"] = forum_id
            forum_post["type"] = "forum_post"
            
            # Add default values for consistency with the previous implementation
            if "votes" not in forum_post:
                forum_post["votes"] = {"for": 0, "against": 0}
            if "comments" not in forum_post:
                forum_post["comments"] = 0
                
            indexed_data.append(forum_post)
            
            logger.info(f"Retrieved forum post: {forum_post['title']}")
            logger.debug(f"Author: {forum_post['author']}")
            logger.debug(f"Date: {forum_post['date']}")
            content_excerpt = forum_post['content'][:100] + "..." if len(forum_post['content']) > 100 else forum_post['content']
            logger.debug(f"Content excerpt: {content_excerpt}")
        except Exception as e:
            logger.error(f"Error fetching forum post: {str(e)}")
            logger.info("Will continue with other data sources")
        
        # Update state with indexed data
        state["indexed_data"] = indexed_data
        
        logger.info(f"Indexing complete. Retrieved {len(indexed_data)} relevant documents.")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in indexer_tool_node: {str(e)}")
        # Initialize indexed_data if not present to allow pipeline to continue
        if "indexed_data" not in state:
            state["indexed_data"] = []
        return state

def reader_tool_node(state: AgentState) -> AgentState:
    """Tool Node: Reader and Clip Quotes.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with extracted quotes
    """
    try:
        logger.info("==== READER TOOL NODE ====")
        logger.info("Reading documents and extracting relevant quotes...")
        
        extracted_quotes = []
        
        # Check if search_results exists
        if "search_results" not in state or not state["search_results"]:
            logger.warning("No search results found for reading.")
            state["extracted_quotes"] = []
            return state
        
        # Extract relevant keywords from the proposal based on metadata and content
        # Start with default keywords that are generally relevant
        keywords = ["governance", "voting", "implementation", "security"]
        
        # Add protocol-specific keywords
        metadata = state.get('metadata', {})
        if "protocol" in metadata:
            protocol_keyword = metadata["protocol"].lower()
            keywords.append(protocol_keyword)
            logger.debug(f"Added protocol keyword: {protocol_keyword}")
            
        if "category" in metadata:
            category_keyword = metadata["category"].lower()
            keywords.append(category_keyword)
            logger.debug(f"Added category keyword: {category_keyword}")
        
        # Try to extract additional keywords from the proposal text
        if "proposal" in state and state["proposal"]:
            # Use a simple approach to extract potential keywords
            proposal_text = state["proposal"].lower()
            potential_keywords = [
                "timelock", "dao", "treasury", "funds", "upgrade", "migration",
                "vote", "quorum", "threshold", "delegate", "community"
            ]
            
            for keyword in potential_keywords:
                if keyword in proposal_text and keyword not in keywords:
                    keywords.append(keyword)
                    logger.debug(f"Added proposal-derived keyword: {keyword}")
        
        # Remove duplicates and ensure all keywords are lowercase
        keywords = list(set([k.lower() for k in keywords]))
        
        logger.info(f"Using keywords for quote extraction: {keywords}")
        
        # Process search results
        logger.info("Processing search results for quote extraction")
        for i, result in enumerate(state["search_results"]):
            if "url" in result and result["url"].startswith("http"):
                try:
                    logger.info(f"Reading document {i+1}/{len(state['search_results'])}: {result['url']}")
                    
                    # Use our wrapper function instead of the tool method
                    document = read_document(result['url'])
                    
                    if document and "content" in document and document["content"]:
                        content_length = len(document['content'])
                        logger.info(f"Successfully read document: {result.get('title', 'Untitled')} ({content_length} chars)")
                        
                        # Use our wrapper function instead of the tool method
                        logger.debug(f"Clipping quotes with {len(keywords)} keywords")
                        quotes = clip_quotes(document['content'], keywords)
                        
                        logger.info(f"Found {len(quotes)} relevant quotes in document")
                        
                        for quote in quotes:
                            quote["source"] = result["url"]
                            quote["title"] = result.get("title", "Unknown")
                            extracted_quotes.append(quote)
                    else:
                        logger.warning(f"Could not extract content from {result['url']}")
                except Exception as e:
                    logger.error(f"Error reading document {result['url']}: {str(e)}")
                    # Use snippet as fallback if available
                    if "snippet" in result and result["snippet"]:
                        logger.info("Using snippet as fallback for quote extraction")
                        try:
                            # Use our wrapper function instead of the tool method
                            quotes = clip_quotes(result['snippet'], keywords)
                            for quote in quotes:
                                quote["source"] = result["url"]
                                quote["title"] = result.get("title", "Unknown")
                                quote["is_fallback"] = True  # Mark as fallback
                                extracted_quotes.append(quote)
                            logger.info(f"Found {len(quotes)} quotes in fallback snippet")
                        except Exception as snippet_error:
                            logger.error(f"Error processing snippet: {str(snippet_error)}")
        
        # Process indexed data
        if "indexed_data" in state and state["indexed_data"]:
            logger.info("Processing indexed data for quote extraction")
            for i, data in enumerate(state["indexed_data"]):
                if "content" in data and data["content"]:
                    try:
                        title = data.get('title', f"Indexed document {i+1}")
                        logger.info(f"Processing indexed document: {title}")
                        
                        # Use our wrapper function instead of the tool method
                        quotes = clip_quotes(data['content'], keywords)
                        
                        logger.info(f"Found {len(quotes)} relevant quotes in indexed document")
                        
                        for quote in quotes:
                            quote["source"] = data.get("url", data.get("id", "unknown"))
                            quote["title"] = title
                            quote["type"] = data.get("type", "indexed")
                            extracted_quotes.append(quote)
                    except Exception as e:
                        logger.error(f"Error processing indexed document: {str(e)}")
        
        # Deduplicate quotes by comparing content
        if extracted_quotes:
            unique_quotes = []
            quote_texts = set()
            
            for quote in extracted_quotes:
                quote_text = quote.get("quote", "")
                # Only add if we haven't seen this exact quote before
                if quote_text and quote_text not in quote_texts:
                    quote_texts.add(quote_text)
                    unique_quotes.append(quote)
            
            logger.info(f"Removed {len(extracted_quotes) - len(unique_quotes)} duplicate quotes")
            extracted_quotes = unique_quotes
        
        # Update state with extracted quotes
        state["extracted_quotes"] = extracted_quotes
        
        logger.info(f"Quote extraction complete. Found {len(extracted_quotes)} unique relevant quotes.")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in reader_tool_node: {str(e)}")
        # Initialize extracted_quotes if not present to allow pipeline to continue
        if "extracted_quotes" not in state:
            state["extracted_quotes"] = []
        return state

def analyzing_agent(state: AgentState) -> AgentState:
    """Analyzing Agent / Extractor: Extract claims and evidence from the quotes.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with extracted claims and evidence
    """
    try:
        logger.info("==== ANALYZING AGENT ====")
        logger.info("Analyzing quotes and extracting claims with evidence...")
        
        system_prompt = """You are an Analyzing Agent for proposal analysis.
        Your job is to extract claims and their supporting evidence from the provided quotes.
        For each claim, provide the evidence that supports it and rate your confidence in the claim.
        Structure your response clearly with sections for each claim, including:
        - Claim: [The claim statement]
        - Evidence: [List of supporting evidence]
        - Sources: [Sources of the evidence]
        - Confidence: [A number between 0.0 and 1.0]
        """
        
        # Prepare quotes for analysis
        if "extracted_quotes" not in state or not state["extracted_quotes"]:
            logger.warning("No extracted quotes found for analysis. Using default quotes.")
            # Create default quotes
            state["extracted_quotes"] = [
                {"quote": "The proposal addresses governance structures.", "source": "default_source", "keyword": "governance", "title": "Default Document"},
                {"quote": "Implementation details are provided in the proposal.", "source": "default_source", "keyword": "implementation", "title": "Default Document"}
            ]
        
        # Format quotes for the LLM with more context
        formatted_quotes = []
        for q in state["extracted_quotes"]:
            quote_text = q.get('quote', '')
            source = q.get('source', 'unknown')
            title = q.get('title', 'Untitled')
            keyword = q.get('keyword', '')
            formatted_quotes.append(f"Quote: {quote_text}\nSource: {source} ({title})\nKeyword: {keyword}")
        
        quotes_text = "\n\n".join(formatted_quotes)
        
        # Get proposal safely
        proposal = state.get('proposal', 'No proposal text available')
        
        human_message = f"""
        Proposal: {proposal}
        
        Extracted Quotes:
        {quotes_text}
        
        Extract claims and their supporting evidence from these quotes.
        For each claim, provide:
        1. The claim itself
        2. Supporting evidence
        3. Sources of the evidence
        4. Your confidence in the claim (0.0 to 1.0)
        
        Format your response with clear sections for each claim:
        
        Claim 1: [claim statement]
        Evidence: [list evidence points]
        Sources: [list sources]
        Confidence: [number between 0.0 and 1.0]
        
        Claim 2: [claim statement]
        ...
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        # Use analysis_llm for analyzing quotes and extracting claims
        logger.info(f"Sending request to LLM ({LLM_CONFIG['analysis']['model']}) for claim extraction")
        
        # Start timing for latency measurement
        start_time = time.time()
        
        try:
            response = analysis_llm.invoke(messages)
            
            # Calculate latency in milliseconds
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"LLM response received in {latency_ms}ms")
            
            # Parse the LLM response to extract structured claims and evidence
            response_text = response.content
            logger.debug(f"Response preview: {response_text[:200]}...")
            
            # Initialize claims_evidence list
            claims_evidence = []
            
            # Try to extract structured claims from the response
            # Look for patterns like "Claim:" or "Claim 1:" followed by evidence
            claim_pattern = r'\n\s*(?:Claim\s*\d*:|CLAIM\s*\d*:)'
            claim_blocks = re.split(claim_pattern, response_text)
            
            logger.info(f"Found {len(claim_blocks)} potential claim blocks in response")
            
            # Process each claim block (skip the first one if it's just an introduction)
            for i, block in enumerate(claim_blocks):
                if i == 0 and not re.search(r'evidence|confidence|source', block.lower()):
                    logger.debug("Skipping introduction block")
                    continue  # Skip introduction text
                    
                if not block.strip():
                    logger.debug(f"Skipping empty block {i}")
                    continue  # Skip empty blocks
                
                logger.debug(f"Processing claim block {i}")
                    
                # Initialize claim data
                claim_data = {
                    "claim": "",
                    "evidence": [],
                    "sources": [],
                    "confidence": 0.5  # Default confidence
                }
                
                # Extract claim text
                claim_match = re.search(r'^[^\n]+', block.strip())
                if claim_match:
                    claim_data["claim"] = claim_match.group(0).strip()
                    logger.debug(f"Extracted claim: {claim_data['claim'][:50]}...")
                
                # Extract evidence
                evidence_pattern = r'(?:Evidence|EVIDENCE|Supporting Evidence)[^\n]*:(.+?)(?:(?:Source|SOURCE|Confidence|CONFIDENCE)[^\n]*:|$)'
                evidence_section = re.search(evidence_pattern, block, re.DOTALL)
                if evidence_section:
                    evidence_text = evidence_section.group(1).strip()
                    # Split evidence items by numbered lists, bullet points, or new lines
                    evidence_items = re.split(r'\n\s*[-*]|\n\s*\d+\.', evidence_text)
                    for item in evidence_items:
                        if item.strip():
                            claim_data["evidence"].append(item.strip())
                    logger.debug(f"Extracted {len(claim_data['evidence'])} evidence items")
                
                # Extract sources
                sources_pattern = r'(?:Source|SOURCE|Sources|SOURCES)[^\n]*:(.+?)(?:(?:Confidence|CONFIDENCE)[^\n]*:|$)'
                sources_section = re.search(sources_pattern, block, re.DOTALL)
                if sources_section:
                    sources_text = sources_section.group(1).strip()
                    # Split sources by commas, numbered lists, bullet points, or new lines
                    sources_items = re.split(r',|\n\s*[-*]|\n\s*\d+\.', sources_text)
                    for item in sources_items:
                        if item.strip():
                            claim_data["sources"].append(item.strip())
                    logger.debug(f"Extracted {len(claim_data['sources'])} sources")
                
                # Extract confidence
                confidence_pattern = r'(?:Confidence|CONFIDENCE)[^\n]*:\s*([\d.]+)'
                confidence_match = re.search(confidence_pattern, block)
                if confidence_match:
                    try:
                        confidence = float(confidence_match.group(1))
                        # Ensure confidence is between 0 and 1
                        claim_data["confidence"] = max(0.0, min(1.0, confidence))
                        logger.debug(f"Extracted confidence: {claim_data['confidence']}")
                    except ValueError as e:
                        logger.warning(f"Error parsing confidence value: {str(e)}")
                        # Keep default confidence
                
                # Add the claim to our list if it has a claim text
                if claim_data["claim"]:
                    claims_evidence.append(claim_data)
                    logger.debug(f"Added claim to list: {claim_data['claim'][:30]}...")
            
            # If we couldn't extract structured claims, create at least one from the overall response
            if not claims_evidence:
                logger.warning("Could not extract structured claims. Creating a general claim from the response.")
                claims_evidence = [{
                    "claim": "Analysis of the proposal based on provided quotes",
                    "evidence": [response_text[:500]],  # Use the first part of the response as evidence
                    "sources": ["LLM analysis"],
                    "confidence": 0.5
                }]
                
            logger.info(f"Successfully extracted {len(claims_evidence)} claims with evidence")
            for i, claim in enumerate(claims_evidence):
                logger.info(f"Claim {i+1}: {claim['claim'][:50]}... (Confidence: {claim['confidence']})")
                logger.debug(f"Evidence items: {len(claim['evidence'])}")
                logger.debug(f"Sources: {', '.join(claim['sources'][:3])}{'...' if len(claim['sources']) > 3 else ''}")
            
            # Update state with claims and evidence
            state["claims_evidence"] = claims_evidence
            state["messages"] = state.get("messages", []) + [response]
            
        except Exception as e:
            logger.error(f"Error invoking LLM for claim extraction: {str(e)}")
            # Create a fallback response and claim
            from langchain_core.messages import AIMessage
            fallback_content = f"Error extracting claims: {str(e)}. Please proceed with basic analysis of the proposal."
            fallback_response = AIMessage(content=fallback_content)
            
            # Create a fallback claim
            state["claims_evidence"] = [{
                "claim": "Analysis of the proposal (error in processing)",
                "evidence": ["Error occurred during claim extraction"],
                "sources": ["System fallback"],
                "confidence": 0.5
            }]
            state["messages"] = state.get("messages", []) + [fallback_response]
        
        return state
        
    except Exception as e:
        logger.error(f"Error in analyzing_agent: {str(e)}")
        # Initialize claims_evidence if not present to allow pipeline to continue
        if "claims_evidence" not in state:
            state["claims_evidence"] = [{
                "claim": "Error in analysis",
                "evidence": [f"An error occurred: {str(e)}"],
                "sources": ["Error handler"],
                "confidence": 0.5
            }]
        return state

def claim_evidence_graph_store(state: AgentState) -> AgentState:
    """Claim-Evidence Graph store: Store claims and evidence in a graph.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with claim-evidence graph
    """
    try:
        logger.info("==== CLAIM-EVIDENCE GRAPH STORE ====")
        logger.info("Creating graph representation of claims and evidence...")
        
        # Create a directed graph
        G = nx.DiGraph()
        
        # Check if claims_evidence exists in the state
        if "claims_evidence" not in state or not state["claims_evidence"]:
            logger.warning("No claims_evidence found for graph creation. Creating a default claim.")
            # Initialize empty claims_evidence to prevent errors
            state["claims_evidence"] = [
                {
                    "claim": "Default claim",
                    "evidence": ["No specific evidence available"],
                    "sources": ["No specific source"],
                    "confidence": 0.5
                }
            ]
        
        # Add nodes and edges for claims and evidence
        claim_count = 0
        evidence_count = 0
        
        for claim_evidence in state["claims_evidence"]:
            # Get claim safely
            claim = claim_evidence.get("claim", f"Unnamed claim {claim_count}")
            confidence = claim_evidence.get("confidence", 0.5)
            
            # Add claim node
            G.add_node(claim, type="claim", confidence=confidence)
            claim_count += 1
            logger.debug(f"Added claim node: {claim[:50]}... (confidence: {confidence})")
            
            # Get evidence and sources safely
            evidence_list = claim_evidence.get("evidence", [])
            sources_list = claim_evidence.get("sources", [])
            
            # Add evidence nodes and edges
            for i, evidence in enumerate(evidence_list):
                evidence_id = f"{claim[:20]}_{i}".replace(" ", "_")  # Create a more reliable ID
                
                # Get source safely
                source = sources_list[i] if i < len(sources_list) else "unknown"
                
                # Add evidence node
                G.add_node(
                    evidence_id, 
                    type="evidence", 
                    content=evidence, 
                    source=source
                )
                
                # Add edge from evidence to claim
                G.add_edge(evidence_id, claim, type="supports")
                
                evidence_count += 1
                logger.debug(f"Added evidence node {i+1} for claim: {claim[:30]}...")
        
        # Store the graph in the state
        state["claim_evidence_graph"] = G
        
        # Log graph statistics
        logger.info(f"Graph creation complete. Created graph with {claim_count} claims and {evidence_count} evidence nodes.")
        logger.info(f"Graph has {len(G.nodes)} nodes and {len(G.edges)} edges.")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in claim_evidence_graph_store: {str(e)}")
        # Create a minimal graph to allow pipeline to continue
        G = nx.DiGraph()
        G.add_node("error_claim", type="claim", confidence=0.0)
        G.add_node("error_evidence", type="evidence", content=f"Error: {str(e)}", source="error")
        G.add_edge("error_evidence", "error_claim", type="supports")
        
        state["claim_evidence_graph"] = G
        return state

def signal_detectors(state: AgentState) -> AgentState:
    """Signal Detectors: Detect bursts, bottlenecks in the claim-evidence graph.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with detected signals
    """
    try:
        logger.info("==== SIGNAL DETECTORS ====")
        logger.info("Detecting patterns and anomalies in the claim-evidence graph...")
        
        # Check if claim_evidence_graph exists in the state
        if "claim_evidence_graph" not in state or state["claim_evidence_graph"] is None:
            # If not, create a new graph from claims_evidence
            logger.warning("claim_evidence_graph not found in state. Creating a new one.")
            
            # Create a directed graph
            G = nx.DiGraph()
            
            # Add nodes and edges for claims and evidence if claims_evidence exists
            if "claims_evidence" in state and state["claims_evidence"]:
                logger.info("Building graph from claims_evidence data")
                claim_count = 0
                evidence_count = 0
                
                for claim_evidence in state["claims_evidence"]:
                    # Get claim safely
                    claim = claim_evidence.get("claim", f"Unnamed claim {claim_count}")
                    confidence = claim_evidence.get("confidence", 0.5)
                    
                    # Add claim node
                    G.add_node(claim, type="claim", confidence=confidence)
                    claim_count += 1
                    
                    # Get evidence and sources safely
                    evidence_list = claim_evidence.get("evidence", [])
                    sources_list = claim_evidence.get("sources", [])
                    
                    # Add evidence nodes and edges
                    for i, evidence in enumerate(evidence_list):
                        evidence_id = f"{claim[:20]}_{i}".replace(" ", "_")  # Create a more reliable ID
                        
                        # Get source safely
                        source = sources_list[i] if i < len(sources_list) else "unknown"
                        
                        # Add evidence node
                        G.add_node(
                            evidence_id, 
                            type="evidence", 
                            content=evidence, 
                            source=source
                        )
                        
                        # Add edge from evidence to claim
                        G.add_edge(evidence_id, claim, type="supports")
                        evidence_count += 1
                
                logger.info(f"Created graph with {claim_count} claims and {evidence_count} evidence nodes")
            else:
                logger.warning("No claims_evidence data found. Creating an empty graph.")
            
            # Store the graph in the state
            state["claim_evidence_graph"] = G
        else:
            # Use the existing graph
            G = state["claim_evidence_graph"]
            logger.info(f"Using existing graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
        
        # Initialize signals dictionary
        signals = {}
        
        # Detect claims with high confidence but little evidence
        logger.info("Detecting high confidence claims with insufficient evidence")
        high_confidence_low_evidence_count = 0
        
        for node in G.nodes():
            if G.nodes[node].get("type") == "claim":
                confidence = G.nodes[node].get("confidence", 0)
                evidence_count = sum(1 for pred in G.predecessors(node) if G.nodes[pred].get("type") == "evidence")
                
                if confidence > 0.8 and evidence_count < 2:
                    signals[node] = {
                        "type": "high_confidence_low_evidence",
                        "confidence": confidence,
                        "evidence_count": evidence_count
                    }
                    high_confidence_low_evidence_count += 1
                    logger.debug(f"Detected high confidence ({confidence}) claim with low evidence ({evidence_count}): {node[:50]}...")
        
        # Detect bottlenecks (claims that depend on a single piece of evidence)
        logger.info("Detecting bottleneck claims (dependent on single evidence)")
        bottleneck_count = 0
        
        for node in G.nodes():
            if G.nodes[node].get("type") == "claim":
                predecessors = list(G.predecessors(node))
                if len(predecessors) == 1:
                    # Only mark as bottleneck if not already marked as high confidence/low evidence
                    if node not in signals:
                        evidence_content = G.nodes[predecessors[0]].get("content", "")
                        evidence_preview = evidence_content[:50] + "..." if len(evidence_content) > 50 else evidence_content
                        
                        signals[node] = {
                            "type": "bottleneck",
                            "single_evidence": evidence_content
                        }
                        bottleneck_count += 1
                        logger.debug(f"Detected bottleneck claim: {node[:50]}... with single evidence: {evidence_preview}")
        
        # Detect contradictory evidence (not implemented in original code, adding as enhancement)
        # This would require semantic analysis, which is beyond the scope of this function
        # But we can add a placeholder for future implementation
        
        # Update state with signals
        state["signals"] = signals
        
        logger.info(f"Signal detection complete. Found {high_confidence_low_evidence_count} high confidence/low evidence claims and {bottleneck_count} bottleneck claims.")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in signal_detectors: {str(e)}")
        # Initialize signals if not present to allow pipeline to continue
        state["signals"] = {}
        return state

def hypothesizer(state: AgentState) -> AgentState:
    """Hypothesizer: Generate hypotheses about problems and candidate tasks.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with hypotheses and candidate tasks
    """
    try:
        logger.info("==== HYPOTHESIZER ====")
        logger.info("Generating hypotheses about problems and candidate tasks...")
        
        system_prompt = """You are a Hypothesizer for proposal analysis.
        Your job is to generate hypotheses about problems in the proposal and candidate tasks to address them.
        Use the claims, evidence, and signals to inform your hypotheses.
        
        Structure your response with clear sections for each hypothesis/problem:
        
        Hypothesis 1: [problem statement]
        Severity: [Low/Medium/High/Critical]
        Confidence: [number between 0.0 and 1.0]
        Tasks:
        - [task 1]
        - [task 2]
        - [task 3]
        
        Hypothesis 2: [problem statement]
        ...
        """
        
        # Prepare claims, evidence, and signals for the hypothesizer
        # Handle missing claims_evidence safely
        if "claims_evidence" not in state or not state["claims_evidence"]:
            logger.warning("No claims_evidence found for hypothesis generation")
            claims_text = "No claims found."
        else:
            # Format claims with confidence for better context
            formatted_claims = []
            for i, c in enumerate(state["claims_evidence"]):
                claim = c.get('claim', f"Unnamed claim {i+1}")
                confidence = c.get('confidence', 0.5)
                evidence_count = len(c.get('evidence', []))
                formatted_claims.append(f"Claim {i+1}: {claim} (Confidence: {confidence}, Evidence: {evidence_count} items)")
            
            claims_text = "\n".join(formatted_claims)
            logger.info(f"Prepared {len(formatted_claims)} claims for hypothesis generation")
        
        # Handle missing signals safely
        if "signals" not in state or not state["signals"]:
            logger.warning("No signals found for hypothesis generation")
            signals_text = "No signals detected."
        else:
            # Format signals with more context
            formatted_signals = []
            for claim, signal_info in state["signals"].items():
                signal_type = signal_info.get('type', 'unknown')
                claim_preview = claim[:50] + "..." if len(claim) > 50 else claim
                
                if signal_type == "high_confidence_low_evidence":
                    confidence = signal_info.get('confidence', 0)
                    evidence_count = signal_info.get('evidence_count', 0)
                    formatted_signals.append(f"Signal: {signal_type} for claim '{claim_preview}' (Confidence: {confidence}, Evidence: {evidence_count})")
                elif signal_type == "bottleneck":
                    evidence = signal_info.get('single_evidence', '')
                    evidence_preview = evidence[:50] + "..." if len(evidence) > 50 else evidence
                    formatted_signals.append(f"Signal: {signal_type} for claim '{claim_preview}' (Single evidence: '{evidence_preview}')")
                else:
                    formatted_signals.append(f"Signal: {signal_type} for claim '{claim_preview}'")
            
            signals_text = "\n".join(formatted_signals)
            logger.info(f"Prepared {len(formatted_signals)} signals for hypothesis generation")
        
        # Get proposal safely
        proposal = state.get('proposal', 'No proposal text available')
        
        human_message = f"""
        Proposal: {proposal}
        
        Claims and Evidence:
        {claims_text}
        
        Signals Detected:
        {signals_text}
        
        Generate hypotheses about problems in the proposal and candidate tasks to address them.
        For each hypothesis, provide:
        1. The problem statement
        2. Severity (Low, Medium, High, or Critical)
        3. Your confidence in the hypothesis (0.0 to 1.0)
        4. A list of candidate tasks to address the problem
        
        Format your response with clear sections for each hypothesis as shown in the system prompt.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        # Use roadmap_llm for generating hypotheses and roadmap tasks
        logger.info(f"Sending request to LLM ({LLM_CONFIG['roadmap']['model']}) for hypothesis generation")
        
        # Start timing for latency measurement
        start_time = time.time()
        
        try:
            response = roadmap_llm.invoke(messages)
            
            # Calculate latency in milliseconds
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"LLM response received in {latency_ms}ms")
            
            # Parse the LLM response to extract structured hypotheses
            response_text = response.content
            logger.debug(f"Response preview: {response_text[:200]}...")
            
            # Initialize hypotheses list
            hypotheses = []
            
            # Try to extract structured hypotheses from the response
            # Find all hypothesis/problem blocks in the text
            hypothesis_pattern = r'\n\s*(?:Problem|PROBLEM|Hypothesis|HYPOTHESIS)\s*\d*:'
            problem_blocks = re.split(hypothesis_pattern, response_text)
            
            logger.info(f"Found {len(problem_blocks)} potential hypothesis blocks in response")
            
            # Process each problem block (skip the first one if it's just an introduction)
            for i, block in enumerate(problem_blocks):
                if i == 0 and not re.search(r'severity|confidence|task', block.lower()):
                    logger.debug("Skipping introduction block")
                    continue  # Skip introduction text
                    
                if not block.strip():
                    logger.debug(f"Skipping empty block {i}")
                    continue  # Skip empty blocks
                
                logger.debug(f"Processing hypothesis block {i}")
                    
                # Initialize hypothesis data
                hypothesis_data = {
                    "problem": "",
                    "severity": "Medium",  # Default severity
                    "confidence": 0.7,  # Default confidence
                    "candidate_tasks": []
                }
                
                # Extract problem statement
                problem_match = re.search(r'^[^\n]+', block.strip())
                if problem_match:
                    hypothesis_data["problem"] = problem_match.group(0).strip()
                    logger.debug(f"Extracted problem: {hypothesis_data['problem'][:50]}...")
                
                # Extract severity
                severity_pattern = r'(?:Severity|SEVERITY)[^\n]*:\s*(Low|Medium|High|Critical)'
                severity_match = re.search(severity_pattern, block, re.IGNORECASE)
                if severity_match:
                    hypothesis_data["severity"] = severity_match.group(1).capitalize()
                    logger.debug(f"Extracted severity: {hypothesis_data['severity']}")
                
                # Extract confidence
                confidence_pattern = r'(?:Confidence|CONFIDENCE)[^\n]*:\s*([\d.]+)'
                confidence_match = re.search(confidence_pattern, block)
                if confidence_match:
                    try:
                        confidence = float(confidence_match.group(1))
                        # Ensure confidence is between 0 and 1
                        hypothesis_data["confidence"] = max(0.0, min(1.0, confidence))
                        logger.debug(f"Extracted confidence: {hypothesis_data['confidence']}")
                    except ValueError as e:
                        logger.warning(f"Error parsing confidence value: {str(e)}")
                        # Keep default confidence
                
                # Extract candidate tasks
                tasks_pattern = r'(?:Tasks|TASKS|Candidate Tasks|CANDIDATE TASKS)[^\n]*:(.+?)(?:(?:\n\s*(?:Severity|SEVERITY|Confidence|CONFIDENCE))|$)'
                tasks_section = re.search(tasks_pattern, block, re.DOTALL)
                if tasks_section:
                    tasks_text = tasks_section.group(1).strip()
                    # Split tasks by numbered lists, bullet points, or new lines
                    task_items = re.split(r'\n\s*[-*]|\n\s*\d+\.', tasks_text)
                    for item in task_items:
                        if item.strip():
                            hypothesis_data["candidate_tasks"].append(item.strip())
                    logger.debug(f"Extracted {len(hypothesis_data['candidate_tasks'])} candidate tasks")
                
                # Add the hypothesis to our list if it has a problem statement and at least one task
                if hypothesis_data["problem"] and hypothesis_data["candidate_tasks"]:
                    hypotheses.append(hypothesis_data)
                    logger.debug(f"Added hypothesis to list: {hypothesis_data['problem'][:30]}...")
            
            # If we couldn't extract structured hypotheses, create at least one from the overall response
            if not hypotheses:
                logger.warning("Could not extract structured hypotheses. Creating a general hypothesis from the response.")
                
                # Try to find any tasks mentioned in the text
                task_pattern = r'(?:task|action|step|research)[^\n.]*:[^\n.]*'
                task_matches = re.findall(task_pattern, response_text, re.IGNORECASE)
                
                if task_matches:
                    candidate_tasks = [match.strip() for match in task_matches]
                    logger.info(f"Found {len(candidate_tasks)} tasks in unstructured response")
                else:
                    candidate_tasks = ["Analyze the proposal in more detail"]
                    logger.info("No tasks found in unstructured response, using default task")
                
                hypotheses = [{
                    "problem": "Further analysis required based on provided information",
                    "severity": "Medium",
                    "confidence": 0.7,
                    "candidate_tasks": candidate_tasks
                }]
            
            logger.info(f"Successfully extracted {len(hypotheses)} hypotheses with {sum(len(h['candidate_tasks']) for h in hypotheses)} total tasks")
            for i, hypothesis in enumerate(hypotheses):
                logger.info(f"Hypothesis {i+1}: {hypothesis['problem'][:50]}... (Severity: {hypothesis['severity']}, Confidence: {hypothesis['confidence']})")
                logger.debug(f"Tasks: {len(hypothesis['candidate_tasks'])}")
                for j, task in enumerate(hypothesis['candidate_tasks'][:3]):
                    logger.debug(f"  - {task[:50]}...")
                if len(hypothesis['candidate_tasks']) > 3:
                    logger.debug(f"  - ... and {len(hypothesis['candidate_tasks']) - 3} more tasks")
            
            # Update state with hypotheses and response
            state["hypotheses"] = hypotheses
            state["messages"] = state.get("messages", []) + [response]
            
        except Exception as e:
            logger.error(f"Error invoking LLM for hypothesis generation: {str(e)}")
            # Create a fallback response and hypothesis
            from langchain_core.messages import AIMessage
            fallback_content = f"Error generating hypotheses: {str(e)}. Please proceed with basic analysis of the proposal."
            fallback_response = AIMessage(content=fallback_content)
            
            # Create a fallback hypothesis
            state["hypotheses"] = [{
                "problem": "Analysis required (error in processing)",
                "severity": "Medium",
                "confidence": 0.7,
                "candidate_tasks": ["Review the proposal thoroughly", "Gather additional information"]
            }]
            state["messages"] = state.get("messages", []) + [fallback_response]
        
        return state
        
    except Exception as e:
        logger.error(f"Error in hypothesizer: {str(e)}")
        # Initialize hypotheses if not present to allow pipeline to continue
        if "hypotheses" not in state:
            state["hypotheses"] = [{
                "problem": "Error in hypothesis generation",
                "severity": "Medium",
                "confidence": 0.5,
                "candidate_tasks": ["Review the proposal", f"Address error: {str(e)}"]
            }]
        return state

def skeptic_agent(state: AgentState) -> AgentState:
    """Skeptic / Cross-checker: Verify evidence and determine if RAG fallback is needed.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with verification results and RAG fallback flag
    """
    try:
        logger.info("==== SKEPTIC AGENT ====")
        logger.info("Critically evaluating claims and evidence...")
        
        system_prompt = """You are a Skeptic Agent for proposal analysis.
        Your job is to critically evaluate the claims and evidence, looking for weaknesses or gaps.
        Verify each claim has at least 3 pieces of corroborating evidence.
        Identify potential biases, logical fallacies, or unsupported assumptions in the claims.
        
        Structure your response with clear sections for each claim evaluation:
        
        Claim: [claim text]
        Evidence Strength: [Strong/Moderate/Weak]
        Gaps: [identify any gaps in evidence]
        Potential Biases: [identify any potential biases]
        Recommendation: [recommend if more evidence is needed]
        """
        
        # Prepare claims and evidence for verification
        if "claims_evidence" not in state or not state["claims_evidence"]:
            logger.warning("No claims or evidence found for verification")
            claims_evidence_text = "No claims or evidence found."
            # Initialize empty claims_evidence to prevent errors
            state["claims_evidence"] = []
        else:
            # Format claims and evidence for better context
            formatted_claims = []
            for i, c in enumerate(state["claims_evidence"]):
                claim = c.get('claim', f"Unnamed claim {i+1}")
                evidence_list = c.get('evidence', [])
                sources_list = c.get('sources', [])
                confidence = c.get('confidence', 0.5)
                
                # Format evidence items
                evidence_items = []
                for j, evidence in enumerate(evidence_list):
                    source = sources_list[j] if j < len(sources_list) else "unknown"
                    evidence_items.append(f"Evidence {j+1}: {evidence} (Source: {source})")
                
                evidence_text = "\n".join(evidence_items) if evidence_items else "No evidence provided."
                
                formatted_claims.append(f"Claim {i+1}: {claim}\nConfidence: {confidence}\n{evidence_text}")
            
            claims_evidence_text = "\n\n".join(formatted_claims)
            logger.info(f"Prepared {len(formatted_claims)} claims for verification")
        
        # Get proposal safely
        proposal = state.get('proposal', 'No proposal text available')
        
        human_message = f"""
        Proposal: {proposal}
        
        Claims and Evidence to Verify:
        {claims_evidence_text}
        
        Critically evaluate each claim and its evidence.
        For each claim:
        1. Assess the strength and quality of the evidence
        2. Identify any gaps or weaknesses in the evidence
        3. Note if the claim needs more evidence (less than 3 corroborations)
        4. Identify any potential biases or logical fallacies
        
        Format your response with clear sections for each claim as shown in the system prompt.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        # Use analysis_llm for critical evaluation and verification
        logger.info(f"Sending request to LLM ({LLM_CONFIG['analysis']['model']}) for claim verification")
        
        # Start timing for latency measurement
        start_time = time.time()
        
        try:
            response = analysis_llm.invoke(messages)
            
            # Calculate latency in milliseconds
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"LLM response received in {latency_ms}ms")
            
            # Store the response in messages
            state["messages"] = state.get("messages", []) + [response]
            
            # Log a preview of the response
            response_preview = response.content[:200] + "..." if len(response.content) > 200 else response.content
            logger.debug(f"Response preview: {response_preview}")
            
        except Exception as e:
            logger.error(f"Error invoking LLM for claim verification: {str(e)}")
            # Create a fallback response
            from langchain_core.messages import AIMessage
            fallback_content = f"Error verifying claims: {str(e)}. Proceeding with automated verification."
            fallback_response = AIMessage(content=fallback_content)
            state["messages"] = state.get("messages", []) + [fallback_response]
        
        # Determine which claims need RAG fallback based on evidence count
        # This is a simple heuristic that doesn't depend on the LLM response
        claims_needing_rag = []
        verified_claims = []
        
        logger.info("Determining which claims need additional evidence via RAG")
        
        for claim_evidence in state["claims_evidence"]:
            claim = claim_evidence.get("claim", "")
            evidence_count = len(claim_evidence.get("evidence", []))
            confidence = claim_evidence.get("confidence", 0.5)
            
            # Claims with high confidence but little evidence are prime candidates for RAG
            if evidence_count < 3:
                claims_needing_rag.append(claim)
                logger.info(f"Claim needs RAG: '{claim[:50]}...' (evidence count: {evidence_count})")
            else:
                verified_claims.append(claim_evidence)
                logger.info(f"Claim verified: '{claim[:50]}...' (evidence count: {evidence_count})")
        
        # Update state with verification results
        state["verified_claims"] = verified_claims
        state["claims_needing_rag"] = claims_needing_rag
        
        # Determine if RAG fallback is needed
        need_rag = len(claims_needing_rag) > 0
        state["need_rag_fallback"] = need_rag
        
        logger.info(f"Verification complete. Found {len(verified_claims)} verified claims and {len(claims_needing_rag)} claims needing RAG.")
        logger.info(f"RAG fallback needed: {need_rag}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in skeptic_agent: {str(e)}")
        # Initialize verification results to allow pipeline to continue
        if "verified_claims" not in state:
            state["verified_claims"] = []
        if "claims_needing_rag" not in state:
            state["claims_needing_rag"] = [c.get("claim", "") for c in state.get("claims_evidence", [])][:1]
        state["need_rag_fallback"] = True
        return state

def rag_fallback(state: AgentState) -> AgentState:
    """RAG Fallback: Use RAG over internal archive for claims needing more evidence.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with additional evidence from RAG
    """
    try:
        # Check if RAG fallback is needed
        if not state.get("need_rag_fallback", False):
            logger.info("RAG fallback not needed. Skipping.")
            return state
        
        logger.info("==== RAG FALLBACK ====")
        logger.info("Using RAG over internal archive for claims needing more evidence...")
        
        rag_results = []
        
        # Check if claims_needing_rag exists
        if "claims_needing_rag" not in state or not state["claims_needing_rag"]:
            logger.warning("No claims needing RAG fallback found.")
            state["rag_results"] = []
            return state
        
        claims_needing_rag = state['claims_needing_rag']
        logger.info(f"Found {len(claims_needing_rag)} claims needing additional evidence")
        
        # Process each claim that needs more evidence
        for i, claim in enumerate(claims_needing_rag):
            claim_preview = claim[:50] + "..." if len(claim) > 50 else claim
            logger.info(f"Processing claim {i+1}/{len(claims_needing_rag)}: {claim_preview}")
            
            try:
                # Use our wrapper function instead of the tool method
                logger.info(f"Executing RAG query for claim {i+1}")
                results = rag_query(claim)
                
                if results:
                    logger.info(f"Found {len(results)} relevant documents for claim {i+1}")
                    
                    # Log details about the results
                    for j, result in enumerate(results):
                        score = result.get('score', 'N/A')
                        source = result.get('source', 'Unknown')
                        content = result.get('content', '')
                        content_preview = content[:100] + "..." if len(content) > 100 else content
                        
                        logger.debug(f"  Result {j+1}: Score {score}")
                        logger.debug(f"  Source: {source}")
                        logger.debug(f"  Content excerpt: {content_preview}")
                    
                    # Store the results for this claim
                    rag_results.append({
                        "claim": claim,
                        "results": results
                    })
                else:
                    logger.warning(f"No relevant documents found for claim {i+1}")
            except Exception as e:
                logger.error(f"Error in RAG query for claim {i+1}: {str(e)}")
        
        # Update state with RAG results
        state["rag_results"] = rag_results
        logger.info(f"Retrieved additional evidence for {len(rag_results)} claims")
        
        # Update verified claims with new evidence from RAG
        if "claims_evidence" in state and state["claims_evidence"]:
            newly_verified_claims = 0
            total_new_evidence = 0
            
            for rag_result in rag_results:
                claim_text = rag_result["claim"]
                new_evidence = [result["content"] for result in rag_result["results"]]
                new_sources = [result["source"] for result in rag_result["results"]]
                
                # Find the original claim
                for claim_evidence in state["claims_evidence"]:
                    if claim_evidence["claim"] == claim_text:
                        claim_preview = claim_text[:50] + "..." if len(claim_text) > 50 else claim_text
                        logger.info(f"Adding {len(new_evidence)} pieces of evidence to claim: {claim_preview}")
                        
                        # Add new evidence and sources
                        claim_evidence["evidence"].extend(new_evidence)
                        claim_evidence["sources"].extend(new_sources)
                        total_new_evidence += len(new_evidence)
                        
                        # If we now have enough evidence, add to verified claims
                        if len(claim_evidence["evidence"]) >= 3:
                            if "verified_claims" not in state:
                                state["verified_claims"] = []
                            
                            # Check if this claim is already in verified_claims
                            already_verified = False
                            for vc in state["verified_claims"]:
                                if vc["claim"] == claim_text:
                                    already_verified = True
                                    break
                            
                            if not already_verified:
                                state["verified_claims"].append(claim_evidence)
                                newly_verified_claims += 1
                                logger.info(f"Claim now has sufficient evidence and has been verified")
            
            logger.info(f"RAG fallback complete. Added {total_new_evidence} pieces of evidence to {len(rag_results)} claims.")
            logger.info(f"Newly verified claims: {newly_verified_claims}")
        else:
            logger.warning("No claims_evidence found in state to update with RAG results")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in rag_fallback: {str(e)}")
        # Initialize rag_results if not present to allow pipeline to continue
        if "rag_results" not in state:
            state["rag_results"] = []
        return state

def prioritizer_agent(state: AgentState) -> AgentState:
    """Prioritizer: Use MCDA/RICE to prioritize tasks.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with prioritized tasks
    """
    try:
        logger.info("==== PRIORITIZER AGENT ====")
        logger.info("Prioritizing tasks using RICE framework...")
        
        system_prompt = """You are a Prioritizer Agent for proposal analysis.
        Your job is to prioritize tasks using the RICE framework:
        - Reach: How many users will this impact?
        - Impact: How much will it impact each user?
        - Confidence: How confident are we in the estimates?
        - Effort: How much effort will it take?
        
        Structure your response with clear sections for each task:
        
        Task: [task description]
        Reach (1-10): [score]
        Impact (1-10): [score]
        Confidence (0.0-1.0): [score]
        Effort (1-10): [score]
        RICE Score: [calculated score]
        Priority: [High/Medium/Low]
        Blockers: [list any blockers]
        Dependencies: [list any dependencies]
        """
        
        # Initialize tasks list
        tasks = []
        
        # Check if hypotheses exists
        if "hypotheses" not in state or not state["hypotheses"]:
            logger.warning("No hypotheses found for prioritization. Using default tasks.")
            # Create default tasks if no hypotheses are available
            tasks = [
                {
                    "id": "task_1",
                    "description": "Research proposal background and context",
                    "problem": "Insufficient context"
                },
                {
                    "id": "task_2",
                    "description": "Analyze proposal impact and implications",
                    "problem": "Impact analysis needed"
                }
            ]
        else:
            # Extract tasks from hypotheses
            logger.info(f"Extracting tasks from {len(state['hypotheses'])} hypotheses")
            for hypothesis in state["hypotheses"]:
                problem = hypothesis.get("problem", "Unknown problem")
                candidate_tasks = hypothesis.get("candidate_tasks", [])
                
                for task_desc in candidate_tasks:
                    task_id = f"task_{len(tasks) + 1}"
                    tasks.append({
                        "id": task_id,
                        "description": task_desc,
                        "problem": problem
                    })
                    logger.debug(f"Added task {task_id}: {task_desc[:50]}...")
        
        logger.info(f"Prepared {len(tasks)} tasks for prioritization")
        
        # Format tasks for the LLM
        tasks_text = "\n".join([f"Task {task['id']}: {task['description']} (Problem: {task['problem']})" for task in tasks])
        
        # Get proposal safely
        proposal = state.get('proposal', 'No proposal text available')
        
        human_message = f"""
        Proposal: {proposal}
        
        Tasks to Prioritize:
        {tasks_text}
        
        Prioritize these tasks using the RICE framework.
        For each task, provide:
        1. Reach score (1-10): How many users will this impact?
        2. Impact score (1-10): How much will it impact each user?
        3. Confidence score (0.0-1.0): How confident are we in the estimates?
        4. Effort score (1-10): How much effort will it take?
        5. RICE score: (Reach * Impact * Confidence) / Effort
        6. Priority level (High/Medium/Low)
        7. Any blockers or dependencies
        
        Format your response with clear sections for each task as shown in the system prompt.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        # Use analysis_llm for prioritization
        logger.info(f"Sending request to LLM ({LLM_CONFIG['analysis']['model']}) for task prioritization")
        
        # Start timing for latency measurement
        start_time = time.time()
        
        try:
            response = analysis_llm.invoke(messages)
            
            # Calculate latency in milliseconds
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"LLM response received in {latency_ms}ms")
            
            # Parse the LLM response to extract structured prioritized tasks
            response_text = response.content
            logger.debug(f"Response preview: {response_text[:200]}...")
            
            # Initialize prioritized_tasks list
            prioritized_tasks = []
            
            # Try to extract structured tasks from the response
            # Find all task blocks in the text
            task_pattern = r'\n\s*(?:Task|TASK)\s*\d*:'
            task_blocks = re.split(task_pattern, response_text)
            
            logger.info(f"Found {len(task_blocks)} potential task blocks in response")
            
            # Process each task block (skip the first one if it's just an introduction)
            for i, block in enumerate(task_blocks):
                if i == 0 and not re.search(r'rice|priority|score|reach|impact|confidence|effort', block.lower()):
                    logger.debug("Skipping introduction block")
                    continue  # Skip introduction text
                    
                if not block.strip():
                    logger.debug(f"Skipping empty block {i}")
                    continue  # Skip empty blocks
                
                logger.debug(f"Processing task block {i}")
                    
                # Get the task ID
                task_id = f"task_{i}"
                
                # Initialize task data
                task_data = {
                    "id": task_id,
                    "description": "",
                    "priority": 5.0,  # Default priority
                    "rice_breakdown": {
                        "reach": 5,
                        "impact": 5,
                        "confidence": 0.5,
                        "effort": 5
                    },
                    "blockers": [],
                    "dependencies": [],
                    "estimated_completion_time": "3-5 days",  # Default
                    "required_skills": [],
                    "evidence": []
                }
                
                # Extract task description
                desc_match = re.search(r'^[^\n]+', block.strip())
                if desc_match:
                    task_data["description"] = desc_match.group(0).strip()
                    logger.debug(f"Extracted description: {task_data['description'][:50]}...")
                
                # Extract RICE score / priority
                priority_match = re.search(r'(?:RICE score|Priority|Score)[^\n]*:\s*([\d.]+)', block, re.IGNORECASE)
                if priority_match:
                    try:
                        task_data["priority"] = float(priority_match.group(1))
                        logger.debug(f"Extracted priority: {task_data['priority']}")
                    except ValueError as e:
                        logger.warning(f"Error parsing priority value: {str(e)}")
                        # Keep default priority
                
                # Extract RICE breakdown
                reach_match = re.search(r'Reach[^\n]*:\s*([\d.]+)', block, re.IGNORECASE)
                if reach_match:
                    try:
                        task_data["rice_breakdown"]["reach"] = int(float(reach_match.group(1)))
                        logger.debug(f"Extracted reach: {task_data['rice_breakdown']['reach']}")
                    except ValueError as e:
                        logger.warning(f"Error parsing reach value: {str(e)}")
                        # Keep default value
                        
                impact_match = re.search(r'Impact[^\n]*:\s*([\d.]+)', block, re.IGNORECASE)
                if impact_match:
                    try:
                        task_data["rice_breakdown"]["impact"] = int(float(impact_match.group(1)))
                        logger.debug(f"Extracted impact: {task_data['rice_breakdown']['impact']}")
                    except ValueError as e:
                        logger.warning(f"Error parsing impact value: {str(e)}")
                        # Keep default value
                        
                confidence_match = re.search(r'Confidence[^\n]*:\s*([\d.]+)', block, re.IGNORECASE)
                if confidence_match:
                    try:
                        task_data["rice_breakdown"]["confidence"] = float(confidence_match.group(1))
                        logger.debug(f"Extracted confidence: {task_data['rice_breakdown']['confidence']}")
                    except ValueError as e:
                        logger.warning(f"Error parsing confidence value: {str(e)}")
                        # Keep default value
                        
                effort_match = re.search(r'Effort[^\n]*:\s*([\d.]+)', block, re.IGNORECASE)
                if effort_match:
                    try:
                        task_data["rice_breakdown"]["effort"] = int(float(effort_match.group(1)))
                        logger.debug(f"Extracted effort: {task_data['rice_breakdown']['effort']}")
                    except ValueError as e:
                        logger.warning(f"Error parsing effort value: {str(e)}")
                        # Keep default value
                
                # Extract blockers
                blockers_pattern = r'(?:Blockers|BLOCKERS)[^\n]*:(.+?)(?:(?:Dependencies|DEPENDENCIES|Required Skills|REQUIRED SKILLS|Evidence|EVIDENCE)[^\n]*:|$)'
                blockers_section = re.search(blockers_pattern, block, re.DOTALL)
                if blockers_section:
                    blockers_text = blockers_section.group(1).strip()
                    # Split blockers by commas, bullet points, or new lines
                    blocker_items = re.split(r',|\n\s*[-*]|\n\s*\d+\.', blockers_text)
                    for item in blocker_items:
                        if item.strip() and item.strip().lower() not in ["none", "n/a"]:
                            task_data["blockers"].append(item.strip())
                    logger.debug(f"Extracted {len(task_data['blockers'])} blockers")
                
                # Extract dependencies
                dependencies_pattern = r'(?:Dependencies|DEPENDENCIES)[^\n]*:(.+?)(?:(?:Required Skills|REQUIRED SKILLS|Evidence|EVIDENCE|Blockers|BLOCKERS)[^\n]*:|$)'
                dependencies_section = re.search(dependencies_pattern, block, re.DOTALL)
                if dependencies_section:
                    dependencies_text = dependencies_section.group(1).strip()
                    # Split dependencies by commas, bullet points, or new lines
                    dependency_items = re.split(r',|\n\s*[-*]|\n\s*\d+\.', dependencies_text)
                    for item in dependency_items:
                        if item.strip() and item.strip().lower() not in ["none", "n/a"]:
                            task_data["dependencies"].append(item.strip())
                    logger.debug(f"Extracted {len(task_data['dependencies'])} dependencies")
                
                # Add the task to our list if it has a description
                if task_data["description"]:
                    prioritized_tasks.append(task_data)
                    logger.debug(f"Added task to list: {task_data['description'][:30]}...")
            
            # If we couldn't extract structured tasks, create at least one from the overall response
            if not prioritized_tasks:
                logger.warning("Could not extract structured tasks. Creating a general task from the response.")
                prioritized_tasks = [{
                    "id": "task_1",
                    "description": "Analyze the proposal based on LLM recommendations",
                    "priority": 7.5,
                    "rice_breakdown": {"reach": 7, "impact": 7, "confidence": 0.7, "effort": 5},
                    "blockers": [],
                    "dependencies": [],
                    "estimated_completion_time": "3-5 days",
                    "required_skills": ["Analysis", "Research"],
                    "evidence": ["Based on LLM analysis"]
                }]
            
            logger.info(f"Successfully extracted {len(prioritized_tasks)} prioritized tasks")
            for i, task in enumerate(prioritized_tasks):
                logger.info(f"Task {i+1}: {task['description'][:50]}... (Priority: {task['priority']})")
                rice = task['rice_breakdown']
                logger.debug(f"RICE breakdown: R={rice['reach']}, I={rice['impact']}, C={rice['confidence']}, E={rice['effort']}")
                if task['blockers']:
                    logger.debug(f"Blockers: {', '.join(task['blockers'][:3])}{'...' if len(task['blockers']) > 3 else ''}")
                if task['dependencies']:
                    logger.debug(f"Dependencies: {', '.join(task['dependencies'][:3])}{'...' if len(task['dependencies']) > 3 else ''}")
            
            # Update state with prioritized tasks and response
            state["tasks"] = prioritized_tasks
            state["messages"] = state.get("messages", []) + [response]
            
        except Exception as e:
            logger.error(f"Error invoking LLM for task prioritization: {str(e)}")
            # Create a fallback response and tasks
            from langchain_core.messages import AIMessage
            fallback_content = f"Error prioritizing tasks: {str(e)}. Please proceed with basic task prioritization."
            fallback_response = AIMessage(content=fallback_content)
            
            # Create fallback tasks from the original tasks list
            prioritized_tasks = []
            for i, task in enumerate(tasks):
                prioritized_tasks.append({
                    "id": task["id"],
                    "description": task["description"],
                    "priority": 5.0,  # Default medium priority
                    "rice_breakdown": {"reach": 5, "impact": 5, "confidence": 0.5, "effort": 5},
                    "blockers": [],
                    "dependencies": [],
                    "estimated_completion_time": "3-5 days",
                    "required_skills": ["Analysis", "Research"],
                    "evidence": ["Fallback prioritization due to error"]
                })
            
            # Update state with fallback tasks and response
            state["tasks"] = prioritized_tasks
            state["messages"] = state.get("messages", []) + [fallback_response]
        
        return state
        
    except Exception as e:
        logger.error(f"Error in prioritizer_agent: {str(e)}")
        # Initialize tasks if not present to allow pipeline to continue
        if "tasks" not in state:
            state["tasks"] = [{
                "id": "task_1",
                "description": "Analyze the proposal (error in prioritization)",
                "priority": 5.0,
                "rice_breakdown": {"reach": 5, "impact": 5, "confidence": 0.5, "effort": 5},
                "blockers": [],
                "dependencies": [],
                "estimated_completion_time": "3-5 days",
                "required_skills": ["Analysis", "Research"],
                "evidence": [f"Error occurred: {str(e)}"]
            }]
        return state

def strategy_agent(state: AgentState) -> AgentState:
    """Strategy Agent: Create plans and stepwise instructions.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with strategic plan
    """
    try:
        logger.info("==== STRATEGY AGENT ====")
        logger.info("Creating strategic plan based on prioritized tasks...")
        
        system_prompt = """You are a Strategy Agent for proposal analysis.
        Your job is to create a strategic plan based on the prioritized tasks.
        Provide step-by-step instructions for executing each task.
        
        Structure your response with clear sections for each task:
        
        Task: [task description]
        Priority: [priority level]
        Strategic Approach:
        1. [step 1]
        2. [step 2]
        3. [step 3]
        Expected Outcome: [what to expect]
        """
        
        # Prepare tasks for strategy planning
        if "tasks" not in state or not state["tasks"]:
            logger.warning("No prioritized tasks found for strategy planning. Using default tasks.")
            # Create default tasks if no prioritized tasks are available
            state["tasks"] = [
                {
                    "id": "task_1",
                    "description": "Research proposal background and context",
                    "priority": 8.0,
                    "blockers": [],
                    "dependencies": [],
                    "evidence": ["No specific evidence available"]
                },
                {
                    "id": "task_2",
                    "description": "Analyze proposal impact and implications",
                    "priority": 7.5,
                    "blockers": [],
                    "dependencies": [],
                    "evidence": ["No specific evidence available"]
                }
            ]
        
        # Format tasks for the LLM
        tasks_text = "\n\n".join([
            f"Task {task['id']}: {task['description']} (Priority: {task['priority']})\nBlockers: {', '.join(task['blockers']) if task.get('blockers') else 'None'}\nDependencies: {', '.join(task['dependencies']) if task.get('dependencies') else 'None'}"
            for task in state["tasks"]
        ])
        
        # Get proposal safely
        proposal = state.get('proposal', 'No proposal text available')
        
        human_message = f"""
        Proposal: {proposal}
        
        Prioritized Tasks:
        {tasks_text}
        
        Create a strategic plan with step-by-step instructions for executing these tasks.
        For each task, provide:
        1. A strategic approach with 3-5 concrete steps
        2. Expected outcomes
        3. Any specific techniques or methodologies to use
        4. How to handle potential blockers
        
        Format your response with clear sections for each task as shown in the system prompt.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        # Use roadmap_llm for strategic planning
        logger.info(f"Sending request to LLM ({LLM_CONFIG['roadmap']['model']}) for strategic planning")
        
        # Start timing for latency measurement
        start_time = time.time()
        
        try:
            response = roadmap_llm.invoke(messages)
            
            # Calculate latency in milliseconds
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"LLM response received in {latency_ms}ms")
            
            # Extract next steps from the response
            response_text = response.content
            logger.debug(f"Response preview: {response_text[:200]}...")
            
            # In a real implementation, we would parse the response more carefully
            # For now, we'll just extract some basic next steps
            next_steps = []
            
            # Try to extract steps using regex
            step_pattern = r'\d+\.\s+([^\n]+)'
            step_matches = re.findall(step_pattern, response_text)
            
            if step_matches:
                next_steps = [f"{i+1}. {step}" for i, step in enumerate(step_matches[:8])]
                logger.info(f"Extracted {len(next_steps)} next steps from response")
            else:
                # Fallback to simple line extraction
                lines = response_text.split('\n')
                potential_steps = [line for line in lines if re.match(r'^\d+\.\s+', line)]
                if potential_steps:
                    next_steps = potential_steps[:8]
                    logger.info(f"Extracted {len(next_steps)} next steps using fallback method")
                else:
                    # Create default steps if extraction fails
                    next_steps = [
                        "1. Begin research on similar proposals focusing on security outcomes",
                        "2. Conduct technical simulation of potential attack vectors",
                        "3. Analyze historical governance data from the past 24 months",
                        "4. Consult with security experts for formal assessment",
                        "5. Synthesize findings into a comprehensive report"
                    ]
                    logger.warning("Could not extract steps from response. Using default steps.")
            
            # Log the extracted steps
            for step in next_steps:
                logger.info(f"Step: {step}")
            
            # Update state with next steps and response
            state["next_steps"] = next_steps
            state["messages"] = state.get("messages", []) + [response]
            
        except Exception as e:
            logger.error(f"Error invoking LLM for strategic planning: {str(e)}")
            # Create a fallback response and next steps
            from langchain_core.messages import AIMessage
            fallback_content = f"Error creating strategic plan: {str(e)}. Please proceed with basic strategy."
            fallback_response = AIMessage(content=fallback_content)
            
            # Create default next steps
            state["next_steps"] = [
                "1. Research proposal background and context",
                "2. Analyze proposal impact and implications",
                "3. Identify potential risks and mitigations",
                "4. Prepare summary report with recommendations"
            ]
            state["messages"] = state.get("messages", []) + [fallback_response]
        
        return state
        
    except Exception as e:
        logger.error(f"Error in strategy_agent: {str(e)}")
        # Initialize next_steps if not present to allow pipeline to continue
        if "next_steps" not in state:
            state["next_steps"] = [
                "1. Research proposal background and context",
                "2. Analyze proposal impact and implications",
                "3. Identify potential risks and mitigations",
                "4. Prepare summary report with recommendations"
            ]
        return state

def summarizer_agent(state: AgentState) -> AgentState:
    """Summarizer Agent: Create a final summary of the analysis.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with final summary
    """
    try:
        logger.info("==== SUMMARIZER AGENT ====")
        logger.info("Creating final summary of the analysis...")
        
        system_prompt = """You are a Summarizer Agent for proposal analysis.
        Your job is to create a final summary of the analysis based on the claims, evidence, and strategic plan.
        Provide a concise summary that highlights the key findings, recommendations, and next steps.
        """
        
        # Prepare data for summarization
        claims_evidence = state.get("claims_evidence", [])
        tasks = state.get("tasks", [])
        next_steps = state.get("next_steps", [])
        
        # Format claims and evidence for the LLM
        claims_text = "\n\n".join([
            f"Claim: {c.get('claim', 'Unknown claim')}\nConfidence: {c.get('confidence', 0.5)}\nEvidence: {', '.join(c.get('evidence', ['No evidence'])[:3])}{'...' if len(c.get('evidence', [])) > 3 else ''}"
            for c in claims_evidence[:5]  # Limit to top 5 claims
        ]) if claims_evidence else "No claims or evidence available."
        
        # Format tasks and next steps
        tasks_text = "\n".join([f"- {task.get('description', 'Unknown task')} (Priority: {task.get('priority', 'Unknown')})" 
                              for task in tasks[:5]]) if tasks else "No tasks available."
        
        steps_text = "\n".join([f"{step}" for step in next_steps[:5]]) if next_steps else "No next steps available."
        
        # Get proposal safely
        proposal = state.get('proposal', 'No proposal text available')
        
        human_message = f"""
        Proposal: {proposal}
        
        Claims and Evidence:
        {claims_text}
        
        Prioritized Tasks:
        {tasks_text}
        
        Next Steps:
        {steps_text}
        
        Create a concise summary of the analysis that includes:
        1. Key findings about the proposal
        2. Main recommendations
        3. Critical next steps
        4. Any important caveats or limitations
        
        Format your response as a professional executive summary.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        # Use analysis_llm for summarization
        logger.info(f"Sending request to LLM ({LLM_CONFIG['analysis']['model']}) for final summarization")
        
        # Start timing for latency measurement
        start_time = time.time()
        
        try:
            response = analysis_llm.invoke(messages)
            
            # Calculate latency in milliseconds
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"LLM response received in {latency_ms}ms")
            
            # Update state with summary and response
            state["summary"] = response.content
            state["messages"] = state.get("messages", []) + [response]
            
            # Log a preview of the summary
            summary_preview = response.content[:200] + "..." if len(response.content) > 200 else response.content
            logger.info(f"Summary preview: {summary_preview}")
            
        except Exception as e:
            logger.error(f"Error invoking LLM for summarization: {str(e)}")
            # Create a fallback summary
            from langchain_core.messages import AIMessage
            fallback_content = f"Error creating summary: {str(e)}. Please review the analysis details directly."
            fallback_response = AIMessage(content=fallback_content)
            
            # Create a basic summary from available data
            basic_summary = """Executive Summary:
            
            Based on the available analysis, the proposal requires further investigation before a final recommendation can be made.
            Key areas of concern include potential security implications and impact on stakeholder participation.
            
            Next steps should focus on gathering additional evidence, consulting with domain experts, and conducting a thorough risk assessment.
            
            This summary was generated as a fallback due to an error in the summarization process.
            """
            
            state["summary"] = basic_summary
            state["messages"] = state.get("messages", []) + [fallback_response]
        
        return state
        
    except Exception as e:
        logger.error(f"Error in summarizer_agent: {str(e)}")
        # Initialize summary if not present to allow pipeline to continue
        if "summary" not in state:
            state["summary"] = f"Error in summarization: {str(e)}. Please review the detailed analysis instead."
        return state
