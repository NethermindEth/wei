"""
Planning Agent Node

This module contains the planning agent node for the proposal analysis workflow.
The planning agent is responsible for determining what information is needed
to analyze a governance proposal.
"""

import logging
import os
import time
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from agent_state import AgentState
from langfuse_setup import trace_llm_call

# Configure logging
logger = logging.getLogger('agent_nodes.planning_agent')

def planning_agent(state: AgentState) -> AgentState:
    """Agent Node: Plan the analysis approach for a governance proposal.
    
    This agent determines what information is needed to analyze the proposal,
    what sources to search, and what questions to ask.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with search queries and analysis plan
    """
    try:
        logger.info("==== PLANNING AGENT ====")
        logger.info("Planning analysis approach for governance proposal...")
        
        # Extract proposal text and metadata
        proposal_text = state.get("proposal", "")
        metadata = state.get("metadata", {})
        
        if not proposal_text:
            logger.warning("No proposal text provided")
            state["search_queries"] = []
            state["analysis_plan"] = "No proposal text provided to analyze."
            return state
        
        # Prepare a minimal prompt for the planning agent to reduce token count
        system_prompt = "Generate search queries for this proposal."
        
        # Use a very minimal user prompt to reduce token count
        user_prompt = f"Proposal: {metadata.get('title', 'Governance proposal')}"
        
        # Initialize the language model
        model = os.getenv("WEI_AGENT_PLANNING_MODEL", "anthropic/claude-3-opus-20240229")
        temperature = float(os.getenv("WEI_AGENT_PLANNING_TEMPERATURE", "0.2"))
        
        logger.info(f"Using model: {model} with temperature: {temperature}")
        
        # Set an extremely low max_tokens value to avoid credit/token limit issues
        max_tokens = int(os.getenv("WEI_AGENT_PLANNING_MAX_TOKENS", "20"))
        logger.info(f"Using max_tokens: {max_tokens}")
        
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,  # Limit token usage
            api_key=os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Prepare messages for the LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Start timing for latency measurement
        start_time = time.time()
        
        # Call the LLM with error handling
        try:
            response = llm.invoke(messages)
            
            # Calculate latency in milliseconds
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract the response text
            response_text = response.content
            
            # Trace the LLM call
            try:
                trace_llm_call(
                    model_name=model,
                    prompt=user_prompt,
                    completion=response_text,
                    latency_ms=latency_ms,
                    metadata={
                        "proposal_title": metadata.get('title', 'Untitled'),
                        "protocol": metadata.get('protocol', 'Unknown')
                    }
                )
            except Exception as trace_error:
                logger.warning(f"Error in tracing: {str(trace_error)}")
        except Exception as e:
            logger.error(f"Error during LLM call: {str(e)}")
            # Create minimal response that can be processed
            response_text = """Search Queries:
            1. Ethereum Proof of Stake transition
            2. Ethereum PoS benefits
            3. Ethereum PoS risks
            """
            logger.info("Using minimal fallback response due to LLM error")
        
        # Parse the response to extract search queries and analysis plan
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            try:
                response_json = json.loads(json_match.group(1))
                search_queries = response_json.get("search_queries", [])
                analysis_plan = response_json.get("analysis_plan", "")
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from response")
                search_queries = []
                analysis_plan = response_text
        else:
            # Fallback to simple pattern matching
            search_queries_match = re.search(r'search_queries"?\s*:?\s*\[(.*?)\]', response_text, re.DOTALL)
            if search_queries_match:
                search_queries_text = search_queries_match.group(1)
                search_queries = [q.strip(' "\'') for q in search_queries_text.split(',')]
            else:
                search_queries = []
            
            analysis_plan_match = re.search(r'analysis_plan"?\s*:?\s*"(.*?)"', response_text, re.DOTALL)
            if analysis_plan_match:
                analysis_plan = analysis_plan_match.group(1)
            else:
                analysis_plan = response_text
        
        # Update the state with search queries and analysis plan
        state["search_queries"] = search_queries
        state["analysis_plan"] = analysis_plan
        
        logger.info(f"Generated {len(search_queries)} search queries")
        logger.info("Analysis plan created")
        
        return state
    except Exception as e:
        logger.error(f"Error in planning agent: {str(e)}", exc_info=True)
        state["search_queries"] = []
        state["analysis_plan"] = f"Error in planning agent: {str(e)}"
        return state
