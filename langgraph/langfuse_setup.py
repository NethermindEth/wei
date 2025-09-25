"""Langfuse integration for the Wei Agent.
This module provides a simplified interface for tracing LLM calls.
"""
import os
import uuid
import time
import logging
import functools
from dotenv import load_dotenv
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger('langfuse_setup')

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
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    if public_key and secret_key:
        logger.info("Found Langfuse credentials in environment variables")
        logger.info(f"LANGFUSE_PUBLIC_KEY: {public_key[:5]}...{public_key[-5:] if len(public_key) > 10 else ''}")
        logger.info(f"LANGFUSE_HOST: {host}")
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
        logger.warning("Langfuse API keys not found in environment variables")
        langfuse_client = None
except ImportError:
    logger.warning("Langfuse package not installed. Install with: pip install langfuse")
    langfuse_client = None
except Exception as e:
    logger.error(f"Error initializing Langfuse client: {e}")
    langfuse_client = None

def get_langfuse_client():
    """Get the Langfuse client."""
    if langfuse_available:
        try:
            return get_client()
        except Exception as e:
            logger.warning(f"Error getting Langfuse client: {e}")
            return None
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


def trace_llm_call_with_context(model_name, prompt, completion, latency_ms, metadata=None):
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
        
        # Create a trace using a context manager
        with langfuse.start_as_current_span(name="llm_process", metadata={
            "model": model_name,
            "latency_ms": latency_ms,
            **(metadata or {})
        }) as span:
            # Update the span with additional information
            span.update(metadata={
                "prompt_length": len(prompt),
                "completion_length": len(completion),
                "token_ratio": len(completion.split()) / len(prompt.split()) if len(prompt.split()) > 0 else 0,
                "processing_time_per_token": latency_ms / len(completion.split()) if len(completion.split()) > 0 else 0
            })
            
            # Create a nested generation for the LLM call
            with langfuse.start_as_current_generation(
                name="llm_generation",
                model=model_name,
                input=prompt,
                output=completion,
                metadata={
                    "latency_ms": latency_ms,
                    "input_tokens": len(prompt.split()),
                    "output_tokens": len(completion.split()),
                    **(metadata or {})
                }
            ) as generation:
                # Update the generation with additional information
                generation.update(metadata={
                    "completion_tokens": len(completion.split()),
                    "prompt_tokens": len(prompt.split()),
                    "total_tokens": len(prompt.split()) + len(completion.split())
                })
            
            # Score the current span
            langfuse.score_current_span(
                name="quality",
                value=min(1.0, len(completion) / 500)  # Example quality metric
            )
        
        # Flush to ensure data is sent to Langfuse
        langfuse.flush()
        logger.info("Langfuse data flushed")
        
        return trace_id
    except Exception as e:
        logger.warning(f"Error tracing with Langfuse: {e}")
        return None


def trace_exa_query(query, results, latency_ms, metadata=None):
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
    
    if not langfuse_available:
        logger.debug("Langfuse not available")
        return None
    
    try:
        # Get the Langfuse client
        langfuse = get_langfuse_client()
        if not langfuse:
            logger.warning("Could not get Langfuse client")
            return None
        
        # Create a span for the Exa query
        with langfuse.start_as_current_span(name="exa_query", metadata={
            "query": query,
            "latency_ms": latency_ms,
            "num_results": len(results) if isinstance(results, list) else 1,
            **(metadata or {})
        }) as span:
            # Add detailed information about each result
            if isinstance(results, list) and len(results) > 0:
                for i, result in enumerate(results[:5]):  # Limit to first 5 results to avoid too much data
                    result_metadata = {}
                    if isinstance(result, dict):
                        if "title" in result:
                            result_metadata[f"result_{i}_title"] = result["title"]
                        if "url" in result:
                            result_metadata[f"result_{i}_url"] = result["url"]
                        if "score" in result:
                            result_metadata[f"result_{i}_score"] = result["score"]
                        if "relevance_score" in result:
                            result_metadata[f"result_{i}_relevance"] = result["relevance_score"]
                    
                    if result_metadata:
                        span.update(metadata=result_metadata)
            
            # Score the span based on number of results
            if isinstance(results, list):
                quality_score = min(1.0, len(results) / 10)  # Example quality metric
                langfuse.score_current_span(name="result_quality", value=quality_score)
        
        # Flush to ensure data is sent to Langfuse
        langfuse.flush()
        logger.info("Exa query trace flushed")
        
        return span.id
    except Exception as e:
        logger.warning(f"Error tracing Exa query with Langfuse: {e}")
        return None


def trace_cosine_similarity(vectors, scores, threshold=0.7, metadata=None):
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
    
    if not langfuse_available:
        logger.debug("Langfuse not available")
        return None
    
    try:
        # Get the Langfuse client
        langfuse = get_langfuse_client()
        if not langfuse:
            logger.warning("Could not get Langfuse client")
            return None
        
        # Calculate statistics
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        above_threshold = sum(1 for score in scores if score >= threshold)
        
        # Create a span for the cosine similarity calculation
        with langfuse.start_as_current_span(name="cosine_similarity", metadata={
            "num_vectors": vectors,
            "num_comparisons": len(scores),
            "threshold": threshold,
            "avg_score": avg_score,
            "max_score": max_score,
            "min_score": min_score,
            "above_threshold": above_threshold,
            "above_threshold_percent": (above_threshold / len(scores)) * 100 if scores else 0,
            **(metadata or {})
        }) as span:
            # Add top 5 scores
            if scores:
                top_scores = sorted(scores, reverse=True)[:5]
                for i, score in enumerate(top_scores):
                    span.update(metadata={f"top_score_{i+1}": score})
            
            # Score the span based on average similarity
            langfuse.score_current_span(name="similarity_quality", value=min(1.0, avg_score))
        
        # Flush to ensure data is sent to Langfuse
        langfuse.flush()
        logger.info("Cosine similarity trace flushed")
        
        return span.id
    except Exception as e:
        logger.warning(f"Error tracing cosine similarity with Langfuse: {e}")
        return None
