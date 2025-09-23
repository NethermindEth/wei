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
        
        # Prepare the prompt for the planning agent
        system_prompt = """You are a governance proposal analysis planning agent. Your task is to:
1. Understand the governance proposal
2. Determine what information is needed to analyze it
3. Generate specific search queries to gather this information
4. Create an analysis plan

Output a JSON object with:
- search_queries: List of specific search queries to gather information
- analysis_plan: Step-by-step plan for analyzing the proposal
"""
        
        user_prompt = f"""Governance Proposal:
Title: {metadata.get('title', 'Untitled')}
Protocol: {metadata.get('protocol', 'Unknown')}
Category: {metadata.get('category', 'Unknown')}
Author: {metadata.get('author', 'Unknown')}

Proposal Text:
{proposal_text[:2000]}  # Limit to first 2000 chars for planning

Based on this proposal, determine what information is needed to analyze it and generate specific search queries.
"""
        
        # Initialize the language model
        model = os.getenv("WEI_AGENT_PLANNING_MODEL", "anthropic/claude-3-opus-20240229")
        temperature = float(os.getenv("WEI_AGENT_PLANNING_TEMPERATURE", "0.2"))
        
        logger.info(f"Using model: {model} with temperature: {temperature}")
        
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
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
        
        # Call the LLM
        response = llm.invoke(messages)
        
        # Calculate latency in milliseconds
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Trace the LLM call
        trace_llm_call(
            model_name=model,
            prompt=user_prompt,
            completion=response.content,
            latency_ms=latency_ms,
            metadata={
                "proposal_title": metadata.get('title', 'Untitled'),
                "protocol": metadata.get('protocol', 'Unknown')
            }
        )
        
        # Extract search queries and analysis plan from response
        response_text = response.content
        logger.debug(f"Planning agent response: {response_text}")
        
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
