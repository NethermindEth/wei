"""DeepAgent Tools Module

This module defines custom tools for use with the deepagents package.
These tools are designed to work with the DeepAgent system for proposal analysis.
"""

import logging
import os
from typing import Dict, Any, List
from deepagents.tools import tool

# Import utilities
from utils import extract_json, measure_execution_time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deepagent_tools.log')
    ]
)
logger = logging.getLogger('deepagent_tools')

@tool
def generate_proposal_arguments(proposal_text: str, metadata: Dict[str, str] = None) -> Dict[str, List[str]]:
    """Generate arguments for and against a proposal using an LLM.
    
    Args:
        proposal_text: The text of the proposal
        metadata: Optional metadata about the proposal
        
    Returns:
        Dictionary with "for_proposal" and "against" lists of arguments
    """
    import json
    import time
    import requests
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    
    logger.info(f"DeepAgent calling generate_proposal_arguments with actual LLM call")
    
    # Initialize metadata if not provided
    if metadata is None:
        metadata = {}
    
    # Extract metadata fields with defaults
    protocol = metadata.get('protocol', 'the protocol')
    category = metadata.get('category', 'governance')
    title = metadata.get('title', 'the proposal')
    
    try:
        # Import Langfuse for tracing
        try:
            from langfuse_setup import trace_llm_call_with_context, get_langfuse_client
            logger.info("Using Langfuse to trace LLM call")
            
            # Get the Langfuse client
            langfuse = get_langfuse_client()
            use_langfuse = langfuse is not None
            
            if use_langfuse:
                logger.info("Langfuse client initialized successfully")
            else:
                logger.info("Langfuse client not available")
        except ImportError:
            logger.warning("Langfuse not available for tracing")
            use_langfuse = False
        
        # Initialize the language model with configurable parameters
        model_name = os.getenv("WEI_AGENT_MODEL", "openai/gpt-3.5-turbo")
        temperature = float(os.getenv("WEI_AGENT_ANALYZING_TEMPERATURE", "0.2"))
        max_tokens = int(os.getenv("WEI_AGENT_MAX_TOKENS", "400"))
        logger.info(f"Using model {model_name} with temperature: {temperature}, max_tokens: {max_tokens}")
        
        # Check for OpenRouter API key
        api_key = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
        
        # If no API key found, try to read from .env file directly
        if not api_key:
            try:
                # Try to find API key in .env file
                env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
                if os.path.exists(env_path):
                    with open(env_path, 'r') as f:
                        for line in f:
                            if line.startswith('WEI_AGENT_OPEN_ROUTER_API_KEY='):
                                api_key = line.strip().split('=', 1)[1].strip('"\'')
                                break
            except Exception as e:
                logger.error(f"Error reading .env file: {str(e)}")
        
        if not api_key:
            logger.error("No OpenRouter API key found. Please set WEI_AGENT_OPEN_ROUTER_API_KEY in your environment variables or .env file.")
            raise ValueError("OpenRouter API key not found")
        
        logger.info(f"Using model: {model_name} with temperature: {temperature}")
        
        # Create the prompt
        prompt = f"""You are an expert governance analyst. Analyze this proposal and generate balanced arguments.

### Proposal Title: {title}
### Protocol: {protocol}
### Category: {category}

### Proposal Text:
{proposal_text}

### Task:
Generate 3-5 strong, specific arguments FOR this proposal and 3-5 strong, specific arguments AGAINST this proposal.
Base your arguments on the actual content of the proposal. Be specific and substantive.
Avoid generic arguments that could apply to any proposal.

Format your response as a JSON object with two arrays: 'for_proposal' and 'against'.
Example format:
{{
  "for_proposal": ["Argument 1", "Argument 2", "Argument 3"],
  "against": ["Argument 1", "Argument 2", "Argument 3"]
}}

JSON response:
"""
        
        start_time = time.time()
        
        # Make the LLM call using OpenRouter API directly for better control
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Error from OpenRouter API: {response.status_code} - {response.text}")
            raise Exception(f"OpenRouter API error: {response.status_code}")
        
        response_data = response.json()
        completion = response_data["choices"][0]["message"]["content"]
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        logger.info(f"LLM call completed in {latency_ms:.2f} ms")
        
        # Trace the LLM call with Langfuse if available
        if use_langfuse:
            try:
                # Get the Langfuse client
                langfuse = get_langfuse_client()
                if langfuse:
                    # Create a trace using context managers
                    with langfuse.start_as_current_span(name="generate_proposal_arguments", metadata={
                        "proposal_title": title,
                        "protocol": protocol,
                        "category": category
                    }) as span:
                        # Update the span with additional information
                        span.update(metadata={
                            "latency_ms": latency_ms,
                            "status": "success"
                        })
                        
                        # Create a nested generation for the LLM call
                        with langfuse.start_as_current_generation(
                            name="llm_generation",
                            model=model_name,
                            input=prompt,
                            output=completion,
                            metadata={
                                "temperature": temperature,
                                "max_tokens": max_tokens,
                                "latency_ms": latency_ms
                            }
                        ) as generation:
                            # Update the generation with additional information
                            generation.update(metadata={
                                "completion_tokens": len(completion.split())
                            })
                        
                        # Score the current span
                        langfuse.score_current_span(
                            name="quality",
                            value=min(1.0, len(completion) / 500)  # Example quality metric
                        )
                    
                    # Flush to ensure data is sent to Langfuse
                    langfuse.flush()
                    logger.info("LLM call traced with Langfuse using context managers")
                else:
                    logger.warning("Could not get Langfuse client for tracing")
            except Exception as e:
                logger.error(f"Error tracing LLM call with Langfuse: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Parse the JSON response
        try:
            arguments = extract_json_from_completion(completion)
            
            # Validate the structure
            validate_arguments_structure(arguments)
            
            # Ensure we have at least some arguments
            arguments = ensure_minimum_arguments(arguments, title, protocol)
            
            logger.info(f"Successfully parsed arguments: {len(arguments['for_proposal'])} for, {len(arguments['against'])} against")
            return arguments
            
        except Exception as json_err:
            logger.error(f"Error parsing JSON response: {str(json_err)}")
            logger.error(f"Raw completion: {completion}")
            
            # Fall back to extracting arguments from text
            return extract_arguments_from_text(completion, title, protocol)
    
    except Exception as e:
        logger.error(f"Error generating arguments with LLM: {str(e)}")
        return {
            "for_proposal": [f"The {title} proposal aims to improve {protocol}."],
            "against": [f"The implementation of {title} may present technical challenges."]
        }

@measure_execution_time
def extract_json_from_completion(completion: str) -> Dict[str, Any]:
    """Extract JSON from LLM completion using the utility function.
    
    Args:
        completion: The raw completion from the LLM
        
    Returns:
        Extracted JSON as a dictionary
        
    Raises:
        ValueError: If JSON cannot be extracted
    """
    try:
        # Use the utility function from utils.py
        return extract_json(completion)
    except ValueError as e:
        logger.error(f"Error extracting JSON: {e}")
        raise ValueError(f"Could not extract valid JSON from completion: {e}")


def validate_arguments_structure(arguments: Dict[str, Any]) -> None:
    """Validate the structure of the arguments dictionary.
    
    Args:
        arguments: The arguments dictionary to validate
        
    Raises:
        ValueError: If the structure is invalid
    """
    if not isinstance(arguments, dict):
        raise ValueError("Response is not a dictionary")
    
    if "for_proposal" not in arguments or "against" not in arguments:
        raise ValueError("Response missing required keys")
    
    if not isinstance(arguments["for_proposal"], list) or not isinstance(arguments["against"], list):
        raise ValueError("Arguments must be lists")


def ensure_minimum_arguments(arguments: Dict[str, List[str]], title: str, protocol: str) -> Dict[str, List[str]]:
    """Ensure there are at least some arguments in each category.
    
    Args:
        arguments: The arguments dictionary
        title: The proposal title
        protocol: The protocol name
        
    Returns:
        Updated arguments dictionary with fallback arguments if needed
    """
    result = arguments.copy()
    
    # Ensure we have at least some arguments for the proposal
    if not result.get("for_proposal"):
        result["for_proposal"] = [f"The {title} proposal aims to improve {protocol}."]
    
    # Ensure we have at least some arguments against the proposal
    if not result.get("against"):
        result["against"] = [f"The implementation of {title} may present technical challenges."]
    
    return result


@measure_execution_time
def extract_arguments_from_text(completion: str, title: str, protocol: str) -> Dict[str, List[str]]:
    """Extract arguments from text when JSON parsing fails.
    
    Args:
        completion: The raw completion from the LLM
        title: The proposal title
        protocol: The protocol name
        
    Returns:
        Dictionary with for_proposal and against arguments
    """
    import re
    
    for_arguments = []
    against_arguments = []
    
    logger.info(f"Attempting to extract arguments from raw text of length {len(completion)}")
    
    # Try multiple patterns for extracting arguments for the proposal
    for_patterns = [
        r'(?:Arguments? for|FOR)[:\s]+(.*?)(?:Arguments? against|AGAINST|$)',
        r'"for_proposal"\s*:\s*\[([^\]]+)\]',
        r'for_proposal[:\s]+(.*?)(?:against|$)'
    ]
    
    for pattern in for_patterns:
        for_section = re.search(pattern, completion, re.DOTALL | re.IGNORECASE)
        if for_section:
            for_text = for_section.group(1).strip()
            # Try different item patterns
            item_patterns = [
                r'(?:\d+\.|-|\*)\s*(.*?)(?=(?:\d+\.|-|\*)|$)',
                r'"([^"]+)"',  # Quoted items
                r'([^,\n]+)'  # Comma or newline separated
            ]
            
            for item_pattern in item_patterns:
                for_args = re.findall(item_pattern, for_text, re.DOTALL)
                if for_args:
                    for_arguments = [arg.strip().rstrip(',"').lstrip('"') for arg in for_args if arg.strip()]
                    if for_arguments:
                        break
            
            if for_arguments:  # If we found arguments, stop trying patterns
                break
    
    # Try multiple patterns for extracting arguments against the proposal
    against_patterns = [
        r'(?:Arguments? against|AGAINST)[:\s]+(.*?)(?:$)',
        r'"against"\s*:\s*\[([^\]]+)\]',
        r'against[:\s]+(.*?)(?:$)'
    ]
    
    for pattern in against_patterns:
        against_section = re.search(pattern, completion, re.DOTALL | re.IGNORECASE)
        if against_section:
            against_text = against_section.group(1).strip()
            # Try different item patterns
            item_patterns = [
                r'(?:\d+\.|-|\*)\s*(.*?)(?=(?:\d+\.|-|\*)|$)',
                r'"([^"]+)"',  # Quoted items
                r'([^,\n]+)'  # Comma or newline separated
            ]
            
            for item_pattern in item_patterns:
                against_args = re.findall(item_pattern, against_text, re.DOTALL)
                if against_args:
                    against_arguments = [arg.strip().rstrip(',"').lstrip('"') for arg in against_args if arg.strip()]
                    if against_arguments:
                        break
            
            if against_arguments:  # If we found arguments, stop trying patterns
                break
    
    # Clean up arguments - remove any that are too short or contain only punctuation
    for_arguments = [arg for arg in for_arguments if len(arg) > 10 and not all(c in '.,;:!?-"' for c in arg)]
    against_arguments = [arg for arg in against_arguments if len(arg) > 10 and not all(c in '.,;:!?-"' for c in arg)]
    
    # Ensure we have at least some arguments
    if not for_arguments:
        for_arguments = [f"The {title} proposal aims to improve {protocol}."]
    
    if not against_arguments:
        against_arguments = [f"The implementation of {title} may present technical challenges."]
    
    logger.info(f"Extracted {len(for_arguments)} arguments for and {len(against_arguments)} arguments against")
    
    return {
        "for_proposal": for_arguments[:5],  # Limit to 5 most relevant
        "against": against_arguments[:5]  # Limit to 5 most relevant
    }


# List of all tools available for deepagents
deepagent_tools = [generate_proposal_arguments]
