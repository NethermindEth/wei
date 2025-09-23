"""Langfuse integration for the Wei Agent.
This module provides a simplified interface for tracing LLM calls.
"""
import os
import uuid
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flag to indicate if Langfuse integration is available
langfuse_available = False

# Initialize Langfuse client
try:
    # Try to import and initialize Langfuse
    from langfuse import Langfuse
    
    # Check if environment variables are set
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    if public_key and secret_key:
        # Create a Langfuse client
        langfuse_client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
        langfuse_available = True
        print("Langfuse client initialized successfully")
    else:
        print("Langfuse API keys not found in environment variables")
        langfuse_client = None
except ImportError:
    print("Langfuse package not installed. Install with: pip install langfuse")
    langfuse_client = None
except Exception as e:
    print(f"Error initializing Langfuse client: {e}")
    langfuse_client = None

def trace_llm_call(model_name, prompt, completion, latency_ms, metadata=None):
    """
    Log LLM call information to the console.
    
    This function provides a simplified interface for logging LLM calls,
    without depending on external services.
    
    Args:
        model_name: The name of the LLM model used
        prompt: The prompt sent to the LLM
        completion: The completion received from the LLM
        latency_ms: The latency of the LLM call in milliseconds
        metadata: Additional metadata to include in the trace
    """
    # Always log basic information to console
    print(f"LLM Call: {model_name}")
    print(f"Latency: {latency_ms} ms")
    
    if metadata:
        print(f"Metadata: {metadata}")
    
    # Generate a trace ID for reference
    trace_id = str(uuid.uuid4())
    print(f"Trace ID: {trace_id}")
    
    # Return the trace ID for reference
    return trace_id
