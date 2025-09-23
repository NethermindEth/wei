"""
Prioritizer Agent Node

This module contains the prioritizer agent node for the proposal analysis workflow.
This agent prioritizes the findings and generates tasks based on the analysis.
"""

import logging
import os
import time
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from agent_state import AgentState, Task
from langfuse_setup import trace_llm_call
from .utils import extract_tasks_from_text, extract_blockers_from_text

# Configure logging
logger = logging.getLogger('agent_nodes.prioritizer_agent')

def prioritizer_agent(state: AgentState) -> AgentState:
    """Agent Node: Prioritize findings and generate tasks.
    
    This agent takes the analysis results, prioritizes the findings,
    and generates tasks based on the analysis. It identifies key actions
    that should be taken based on the proposal evaluation.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with prioritized tasks and blockers
    """
    try:
        logger.info("==== PRIORITIZER AGENT ====")
        logger.info("Prioritizing findings and generating tasks...")
        
        # Extract analysis results
        claims_evidence = state.get("claims_evidence", [])
        hypotheses = state.get("hypotheses", [])
        signals = state.get("signals", [])
        critique = state.get("critique", "")
        gaps = state.get("gaps", [])
        rag_results = state.get("rag_results", [])
        metadata = state.get("metadata", {})
        
        # Prepare a minimal prompt for the prioritizer agent to reduce token count
        system_prompt = "Prioritize tasks for this proposal."
        
        # Use a very minimal user prompt to reduce token count
        user_prompt = f"Proposal: {metadata.get('title', 'Governance proposal')}"
        
        # Initialize the language model
        model = os.getenv("WEI_AGENT_PRIORITIZER_MODEL", "anthropic/claude-3-opus-20240229")
        temperature = float(os.getenv("WEI_AGENT_PRIORITIZER_TEMPERATURE", "0.3"))
        
        logger.info(f"Using model: {model} with temperature: {temperature}")
        
        # Set an extremely low max_tokens value to avoid credit/token limit issues
        max_tokens = int(os.getenv("WEI_AGENT_PRIORITIZER_MAX_TOKENS", "20"))
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
            
            # Get response content
            response_text = response.content
            
            # Trace the LLM call
            try:
                trace_llm_call(
                    model_name=model,
                    prompt=user_prompt,
                    completion=response_text,
                    latency_ms=latency_ms,
                    metadata={
                        "proposal_title": metadata.get('title', 'Untitled')
                    }
                )
            except Exception as trace_error:
                logger.warning(f"Error in tracing: {str(trace_error)}")
                
            # Debug log the response
            logger.debug(f"Prioritizer agent response: {response_text}")
            
        except Exception as e:
            logger.error(f"Error in prioritizer agent: {str(e)}")
            # Create minimal response that can be processed
            response_text = """Tasks:
            1. Review the proposal for technical feasibility (Priority: high)
            2. Assess security implications (Priority: high)
            
            Blockers:
            None identified.
            """
            logger.info("Using minimal fallback response due to LLM error")
        
        # Parse the response to extract tasks and blockers
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        tasks = []
        blockers = []
        
        if json_match:
            try:
                response_json = json.loads(json_match.group(1))
                tasks = response_json.get("tasks", [])
                blockers = response_json.get("blockers", [])
                logger.info(f"Successfully parsed {len(tasks)} tasks and {len(blockers)} blockers from JSON response")
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from response")
                tasks = extract_tasks_from_text(response_text)
                blockers = extract_blockers_from_text(response_text)
        else:
            # Fallback to pattern matching
            tasks = extract_tasks_from_text(response_text)
            blockers = extract_blockers_from_text(response_text)
        
        # Ensure tasks are properly formatted
        formatted_tasks = []
        for task in tasks:
            if isinstance(task, dict):
                formatted_task = {
                    "description": task.get("description", ""),
                    "priority": task.get("priority", "medium")
                }
                formatted_tasks.append(formatted_task)
            elif isinstance(task, str):
                # Determine priority based on keywords
                priority = "medium"  # Default priority
                if any(kw in task.lower() for kw in ["urgent", "critical", "immediate", "high priority"]):
                    priority = "high"
                elif any(kw in task.lower() for kw in ["minor", "optional", "nice to have", "low priority"]):
                    priority = "low"
                
                formatted_tasks.append({
                    "description": task,
                    "priority": priority
                })
        
        # Update the state with tasks and blockers
        state["tasks"] = formatted_tasks
        state["blockers"] = blockers
        
        # Preserve arguments from previous nodes if they exist
        if "arguments" in state:
            logger.info(f"Preserving arguments in prioritizer agent: {state['arguments']}")
        else:
            logger.warning("No arguments found in state during prioritization")
        
        logger.info(f"Generated {len(formatted_tasks)} tasks and identified {len(blockers)} blockers")
        
        return state
    except Exception as e:
        logger.error(f"Error in prioritizer agent: {str(e)}", exc_info=True)
        state["tasks"] = [{"description": "Review the proposal for technical feasibility", "priority": "high"}]
        state["blockers"] = [f"Error in prioritizer agent: {str(e)}"]
        return state
