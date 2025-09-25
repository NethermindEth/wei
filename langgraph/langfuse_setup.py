"""Langfuse integration for the Wei Agent.
This module provides a simplified interface for tracing LLM calls and other operations.
"""
import os
import uuid
import logging
from typing import Dict, Any, List, Optional, TypeVar, Callable, Union
from dotenv import load_dotenv

# Import utilities from utils.py
from utils import Metadata

# Configure logging
logger = logging.getLogger('langfuse_setup')

# Type definitions for better type hinting
T = TypeVar('T')
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


def trace_operation(
    operation_type: str,
    name: str,
    input_data: Any,
    output_data: Any,
    latency_ms: float,
    metadata: Optional[Metadata] = None,
    metrics_calculator: Optional[Callable] = None
) -> Optional[str]:
    """Generic function to trace any operation with Langfuse.
    
    Args:
        operation_type: Type of operation (llm, query, similarity, etc.)
        name: Name of the span
        input_data: Input data for the operation
        output_data: Output data from the operation
        latency_ms: Latency in milliseconds
        metadata: Additional metadata
        metrics_calculator: Optional function to calculate additional metrics
        
    Returns:
        Span ID if successful, None otherwise
    """
    logger.info(f"{operation_type.title()} Operation: {name}")
    logger.info(f"Latency: {latency_ms} ms")
    
    if not langfuse_available:
        logger.debug("Langfuse not available")
        return None
    
    try:
        langfuse = get_langfuse_client()
        if not langfuse:
            return None
        
        # Prepare base metadata
        base_metadata = validate_metadata(metadata)
        base_metadata.update({
            "operation_type": operation_type,
            "latency_ms": latency_ms,
        })
        
        # Calculate additional metrics if provided
        if metrics_calculator:
            metrics = metrics_calculator(input_data, output_data, latency_ms)
            base_metadata.update(metrics)
        
        # Create span
        with langfuse.start_as_current_span(name=name, metadata=base_metadata) as span:
            # Score the span if metrics are available
            if "quality_score" in base_metadata:
                langfuse.score_current_span(
                    name="quality", 
                    value=base_metadata["quality_score"]
                )
        
        langfuse.flush()
        logger.info(f"{operation_type.title()} trace flushed")
        
        return span.id
    except Exception as e:
        logger.warning(f"Error tracing {operation_type} with Langfuse: {e}")
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
    quality_score = min(1.0, len(completion) / 500)  # Example quality metric
    
    return {
        "prompt_length": len(prompt),
        "completion_length": len(completion),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "token_ratio": token_ratio,
        "processing_time_per_token": processing_time_per_token,
        "quality_score": quality_score
    }


def llm_metrics_calculator(prompt: str, completion: str, latency_ms: float) -> Dict[str, Any]:
    """Calculate metrics for LLM calls.
    
    Args:
        prompt: The prompt text
        completion: The completion text
        latency_ms: Processing latency in milliseconds
        
    Returns:
        Dictionary of calculated metrics
    """
    return calculate_token_metrics(prompt, completion, latency_ms)


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
    # Prepare base metadata
    base_metadata = validate_metadata(metadata)
    base_metadata["model"] = model_name
    
    # Use the generic trace_operation function
    return trace_operation(
        operation_type="llm",
        name="llm_process",
        input_data=prompt,
        output_data=completion,
        latency_ms=latency_ms,
        metadata=base_metadata,
        metrics_calculator=llm_metrics_calculator
    )


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


def exa_metrics_calculator(query: str, results: List[Dict[str, Any]], latency_ms: float) -> Dict[str, Any]:
    """Calculate metrics for Exa API queries.
    
    Args:
        query: The query sent to Exa API
        results: The results received from Exa API
        latency_ms: The latency of the query in milliseconds
        
    Returns:
        Dictionary of calculated metrics
    """
    # Extract basic metrics
    metrics = {
        "query": query,
        "num_results": len(results) if isinstance(results, list) else 1,
    }
    
    # Calculate quality score based on number of results
    if isinstance(results, list) and results:
        metrics["quality_score"] = min(1.0, len(results) / 10)  # Example quality metric
    
    # Extract result metadata
    result_metadata = extract_result_metadata(results)
    metrics.update(result_metadata)
    
    return metrics


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
    # Use the generic trace_operation function
    return trace_operation(
        operation_type="search",
        name="exa_query",
        input_data=query,
        output_data=results,
        latency_ms=latency_ms,
        metadata=metadata,
        metrics_calculator=exa_metrics_calculator
    )


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


def similarity_metrics_calculator(vectors: int, scores: List[float], latency_ms: float, threshold: float = 0.7) -> Dict[str, Any]:
    """Calculate metrics for cosine similarity calculations.
    
    Args:
        vectors: The number of vectors compared
        scores: The similarity scores
        latency_ms: The latency of the calculation in milliseconds
        threshold: The similarity threshold used
        
    Returns:
        Dictionary of calculated metrics
    """
    # Calculate statistics
    stats = calculate_similarity_stats(scores, threshold)
    
    # Add basic metrics
    metrics = {
        "num_vectors": vectors,
        "threshold": threshold,
        **stats
    }
    
    # Add top 5 scores if available
    if scores:
        top_scores = sorted(scores, reverse=True)[:5]
        for i, score in enumerate(top_scores):
            metrics[f"top_score_{i+1}"] = score
    
    # Add quality score based on average similarity
    metrics["quality_score"] = min(1.0, stats["avg_score"])
    
    return metrics


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
    # Prepare base metadata with threshold
    base_metadata = validate_metadata(metadata)
    base_metadata["threshold"] = threshold
    
    # Use the generic trace_operation function
    return trace_operation(
        operation_type="similarity",
        name="cosine_similarity",
        input_data=vectors,
        output_data=scores,
        latency_ms=0,  # No latency measurement for this operation
        metadata=base_metadata,
        metrics_calculator=lambda v, s, l: similarity_metrics_calculator(v, s, l, threshold)
    )
