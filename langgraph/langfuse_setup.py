"""Langfuse integration for the Wei Agent.
This module provides a simplified interface for tracing LLM calls and other operations.
"""
import os
import uuid
import logging
from typing import Dict, Any, List, Optional, TypeVar
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger('langfuse_setup')

# Type definitions for better type hinting
T = TypeVar('T')
Metadata = Dict[str, Any]
Span = Any  # Ideally would be langfuse.Span but avoiding direct import dependency

# Constants for environment variables
ENV_PUBLIC_KEY = "LANGFUSE_PUBLIC_KEY"
ENV_SECRET_KEY = "LANGFUSE_SECRET_KEY"
ENV_HOST = "LANGFUSE_HOST"
DEFAULT_HOST = "https://cloud.langfuse.com"

# Load environment variables
load_dotenv()

# Flag to indicate if Langfuse integration is available
langfuse_available = False
langfuse_client = None

# Initialize Langfuse client
try:
    # Try to import and initialize Langfuse
    from langfuse import Langfuse, get_client, observe
    
    # Get credentials from environment variables
    public_key = os.getenv(ENV_PUBLIC_KEY)
    secret_key = os.getenv(ENV_SECRET_KEY)
    host = os.getenv(ENV_HOST, DEFAULT_HOST)
    
    if public_key and secret_key:
        logger.info("Found Langfuse credentials in environment variables")
        # Mask credentials for security in logs
        masked_key = f"{public_key[:5]}...{public_key[-5:] if len(public_key) > 10 else ''}"
        logger.info(f"{ENV_PUBLIC_KEY}: {masked_key}")
        logger.info(f"{ENV_HOST}: {host}")
    else:
        logger.warning("Langfuse credentials not found in environment variables")
    
    if public_key and secret_key:
        # Create a Langfuse client
        langfuse_client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
        langfuse_available = True
        logger.info("Langfuse client initialized successfully")
        
        # Verify connection
        if langfuse_client.auth_check():
            logger.info("Langfuse client authenticated successfully")
        else:
            logger.warning("Langfuse client authentication failed")
            langfuse_available = False
    else:
        logger.warning(f"{ENV_PUBLIC_KEY} and {ENV_SECRET_KEY} must both be set")
        langfuse_client = None
except ImportError:
    logger.warning("Langfuse package not installed. Install with: pip install langfuse")
    langfuse_client = None
except Exception as e:
    logger.error(f"Error initializing Langfuse client: {e}")
    langfuse_client = None

def get_langfuse_client():
    """Get the Langfuse client.
    
    Returns:
        The Langfuse client if available, otherwise None.
    """
    if not langfuse_available:
        return None
        
    try:
        return get_client()
    except Exception as e:
        logger.warning(f"Error getting Langfuse client: {e}")
        return None


def validate_metadata(metadata: Optional[Metadata]) -> Metadata:
    """Validate and normalize metadata.
    
    Args:
        metadata: The metadata to validate
        
    Returns:
        A validated metadata dictionary
    """
    if metadata is None:
        return {}
        
    if not isinstance(metadata, dict):
        logger.warning(f"Invalid metadata type: {type(metadata)}, expected dict")
        return {}
        
    return metadata


def create_span(name: str, metadata: Optional[Metadata] = None) -> Optional[Span]:
    """Create a span with error handling.
    
    Args:
        name: The name of the span
        metadata: Optional metadata for the span
        
    Returns:
        A span object if successful, otherwise None
    """
    if not langfuse_available:
        logger.debug(f"Langfuse not available, skipping span creation for {name}")
        return None
    
    try:
        client = get_langfuse_client()
        if not client:
            logger.warning("Could not get Langfuse client")
            return None
            
        metadata = validate_metadata(metadata)
        span = client.start_span(name=name, metadata=metadata)
        logger.info(f"Created span: {name}")
        return span
    except Exception as e:
        logger.warning(f"Error creating span {name}: {e}")
        return None

# Define a decorator for observing functions with Langfuse
def observe_function(name=None, as_type=None):
    """Decorator for observing functions with Langfuse."""
    def decorator(func):
        if not langfuse_available:
            return func
        
        try:
            return observe(name=name, as_type=as_type)(func)
        except Exception as e:
            logger.warning(f"Error applying observe decorator: {e}")
            return func
    
    return decorator

@observe_function(name="llm_call", as_type="generation")
def trace_llm_call(model_name, prompt, completion, latency_ms, metadata=None, parent=None):
    """
    Trace an LLM call with Langfuse using the @observe decorator.
    
    This function provides a simplified interface for tracing LLM calls,
    with fallback to console logging if Langfuse is not available.
    
    Args:
        model_name: The name of the LLM model used
        prompt: The prompt sent to the LLM
        completion: The completion received from the LLM
        latency_ms: The latency of the LLM call in milliseconds
        metadata: Additional metadata to include in the trace
        parent: Parent trace or span (optional)
        
    Returns:
        str: The trace ID or a dummy ID if Langfuse is not available
    """
    # Always log basic information to console
    logger.info(f"LLM Call: {model_name}")
    logger.info(f"Latency: {latency_ms} ms")
    
    if metadata:
        logger.debug(f"Metadata: {metadata}")
    
    # Return the completion (the @observe decorator will handle the tracing)
    return completion


def calculate_token_metrics(prompt: str, completion: str, latency_ms: float) -> Dict[str, float]:
    """Calculate metrics related to tokens and processing time.
    
    Args:
        prompt: The prompt text
        completion: The completion text
        latency_ms: Processing latency in milliseconds
        
    Returns:
        Dictionary of calculated metrics
    """
    prompt_tokens = len(prompt.split())
    completion_tokens = len(completion.split())
    total_tokens = prompt_tokens + completion_tokens
    
    # Calculate ratios and rates with safeguards against division by zero
    token_ratio = completion_tokens / prompt_tokens if prompt_tokens > 0 else 0
    processing_time_per_token = latency_ms / completion_tokens if completion_tokens > 0 else 0
    
    return {
        "prompt_length": len(prompt),
        "completion_length": len(completion),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "token_ratio": token_ratio,
        "processing_time_per_token": processing_time_per_token
    }


def trace_llm_call_with_context(model_name: str, prompt: str, completion: str, latency_ms: float, metadata: Optional[Metadata] = None) -> Optional[str]:
    """
    Trace an LLM call with Langfuse using context managers.
    
    This function provides a simplified interface for tracing LLM calls using context managers,
    with fallback to console logging if Langfuse is not available.
    
    Args:
        model_name: The name of the LLM model used
        prompt: The prompt sent to the LLM
        completion: The completion received from the LLM
        latency_ms: The latency of the LLM call in milliseconds
        metadata: Additional metadata to include in the trace
        
    Returns:
        str: The trace ID or None if Langfuse is not available
    """
    # Always log basic information to console
    logger.info(f"LLM Call: {model_name}")
    logger.info(f"Latency: {latency_ms} ms")
    
    if not langfuse_available:
        logger.debug("Langfuse not available")
        return None
    
    try:
        # Get the Langfuse client
        langfuse = get_langfuse_client()
        if not langfuse:
            logger.warning("Could not get Langfuse client")
            return None
        
        # Create a trace ID
        trace_id = str(uuid.uuid4())
        
        # Calculate token metrics
        token_metrics = calculate_token_metrics(prompt, completion, latency_ms)
        
        # Prepare base metadata
        base_metadata = validate_metadata(metadata)
        base_metadata["model"] = model_name
        base_metadata["latency_ms"] = latency_ms
        
        # Create a trace using a context manager
        with langfuse.start_as_current_span(name="llm_process", metadata=base_metadata) as span:
            # Update the span with token metrics
            span.update(metadata=token_metrics)
            
            # Create a nested generation for the LLM call
            with langfuse.start_as_current_generation(
                name="llm_generation",
                model=model_name,
                input=prompt,
                output=completion,
                metadata={**base_metadata, **token_metrics}
            ) as generation:
                pass  # The generation is automatically tracked
            
            # Score the current span based on completion quality
            quality_score = min(1.0, len(completion) / 500)  # Example quality metric
            langfuse.score_current_span(name="quality", value=quality_score)
        
        # Flush to ensure data is sent to Langfuse
        langfuse.flush()
        logger.info("Langfuse data flushed")
        
        return trace_id
    except Exception as e:
        logger.warning(f"Error tracing with Langfuse: {e}")
        return None


def extract_result_metadata(results: List[Dict[str, Any]], max_results: int = 5) -> Dict[str, Any]:
    """Extract metadata from search results.
    
    Args:
        results: List of search results
        max_results: Maximum number of results to process
        
    Returns:
        Dictionary of extracted metadata
    """
    result_metadata = {}
    
    if not isinstance(results, list) or not results:
        return result_metadata
    
    # Process only up to max_results to avoid excessive data
    for i, result in enumerate(results[:max_results]):
        if not isinstance(result, dict):
            continue
            
        # Extract common fields from result
        for field in ["title", "url", "score", "relevance_score"]:
            if field in result:
                result_metadata[f"result_{i}_{field}"] = result[field]
    
    return result_metadata


def trace_exa_query(query: str, results: List[Dict[str, Any]], latency_ms: float, metadata: Optional[Metadata] = None) -> Optional[str]:
    """
    Trace an Exa API query with Langfuse.
    
    Args:
        query: The query sent to Exa API
        results: The results received from Exa API
        latency_ms: The latency of the query in milliseconds
        metadata: Additional metadata to include in the trace
        
    Returns:
        str: The span ID or None if Langfuse is not available
    """
    logger.info(f"Exa Query: {query}")
    logger.info(f"Latency: {latency_ms} ms")
    
    # Early return if Langfuse is not available
    if not langfuse_available:
        logger.debug("Langfuse not available")
        return None
    
    try:
        # Get the Langfuse client
        langfuse = get_langfuse_client()
        if not langfuse:
            return None
        
        # Prepare base metadata
        base_metadata = validate_metadata(metadata)
        base_metadata.update({
            "query": query,
            "latency_ms": latency_ms,
            "num_results": len(results) if isinstance(results, list) else 1,
        })
        
        # Create a span for the Exa query
        with langfuse.start_as_current_span(name="exa_query", metadata=base_metadata) as span:
            # Extract and add result metadata
            result_metadata = extract_result_metadata(results)
            if result_metadata:
                span.update(metadata=result_metadata)
            
            # Score the span based on number of results
            if isinstance(results, list) and results:
                quality_score = min(1.0, len(results) / 10)  # Example quality metric
                langfuse.score_current_span(name="result_quality", value=quality_score)
        
        # Flush to ensure data is sent to Langfuse
        langfuse.flush()
        logger.info("Exa query trace flushed")
        
        return span.id
    except Exception as e:
        logger.warning(f"Error tracing Exa query with Langfuse: {e}")
        return None


def calculate_similarity_stats(scores: List[float], threshold: float = 0.7) -> Dict[str, float]:
    """Calculate statistics for similarity scores.
    
    Args:
        scores: List of similarity scores
        threshold: Threshold for considering a score as high
        
    Returns:
        Dictionary of calculated statistics
    """
    if not scores:
        return {
            "avg_score": 0.0,
            "max_score": 0.0,
            "min_score": 0.0,
            "above_threshold": 0,
            "above_threshold_percent": 0.0,
            "num_comparisons": 0
        }
    
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    above_threshold = sum(1 for score in scores if score >= threshold)
    above_threshold_percent = (above_threshold / len(scores)) * 100
    
    return {
        "avg_score": avg_score,
        "max_score": max_score,
        "min_score": min_score,
        "above_threshold": above_threshold,
        "above_threshold_percent": above_threshold_percent,
        "num_comparisons": len(scores)
    }


def trace_cosine_similarity(vectors: int, scores: List[float], threshold: float = 0.7, metadata: Optional[Metadata] = None) -> Optional[str]:
    """
    Trace cosine similarity calculations with Langfuse.
    
    Args:
        vectors: The number of vectors compared
        scores: The similarity scores
        threshold: The similarity threshold used
        metadata: Additional metadata to include in the trace
        
    Returns:
        str: The span ID or None if Langfuse is not available
    """
    logger.info(f"Cosine Similarity: {len(scores)} comparisons")
    
    # Early return if Langfuse is not available
    if not langfuse_available:
        logger.debug("Langfuse not available")
        return None
    
    try:
        # Get the Langfuse client
        langfuse = get_langfuse_client()
        if not langfuse:
            return None
        
        # Calculate statistics
        stats = calculate_similarity_stats(scores, threshold)
        
        # Prepare base metadata
        base_metadata = validate_metadata(metadata)
        base_metadata.update({
            "num_vectors": vectors,
            "threshold": threshold,
            **stats
        })
        
        # Create a span for the cosine similarity calculation
        with langfuse.start_as_current_span(name="cosine_similarity", metadata=base_metadata) as span:
            # Add top 5 scores if available
            if scores:
                top_scores = sorted(scores, reverse=True)[:5]
                top_scores_metadata = {f"top_score_{i+1}": score for i, score in enumerate(top_scores)}
                span.update(metadata=top_scores_metadata)
            
            # Score the span based on average similarity
            avg_score = stats["avg_score"]
            langfuse.score_current_span(name="similarity_quality", value=min(1.0, avg_score))
        
        # Flush to ensure data is sent to Langfuse
        langfuse.flush()
        logger.info("Cosine similarity trace flushed")
        
        return span.id
    except Exception as e:
        logger.warning(f"Error tracing cosine similarity with Langfuse: {e}")
        return None
