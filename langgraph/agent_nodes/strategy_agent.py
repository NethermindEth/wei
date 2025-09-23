"""
Strategy Agent Node

This module contains the strategy agent node for the proposal analysis workflow.
This agent generates a strategic recommendation based on the entire analysis.
"""

import logging
import os
import time
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from agent_state import AgentState
from langfuse_setup import trace_llm_call
from .utils import extract_next_steps_from_text

# Configure logging
logger = logging.getLogger('agent_nodes.strategy_agent')

def strategy_agent(state: AgentState) -> AgentState:
    """Agent Node: Generate strategic recommendation.
    
    This agent takes the entire analysis and generates a strategic recommendation
    for the proposal. It provides a summary of the analysis, a recommendation,
    and next steps.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with strategic recommendation and next steps
    """
    try:
        logger.info("==== STRATEGY AGENT ====")
        logger.info("Generating strategic recommendation...")
        
        # Extract analysis results
        claims_evidence = state.get("claims_evidence", [])
        hypotheses = state.get("hypotheses", [])
        signals = state.get("signals", [])
        critique = state.get("critique", "")
        tasks = state.get("tasks", [])
        blockers = state.get("blockers", [])
        arguments = state.get("arguments", {"for_proposal": [], "against": []})
        metadata = state.get("metadata", {})
        
        # Prepare the prompt for the strategy agent
        system_prompt = """You are a governance proposal strategy agent. Your task is to:
1. Synthesize the entire analysis of the proposal
2. Generate a strategic recommendation based on the analysis
3. Provide a summary of the key points from the analysis
4. Outline specific next steps for stakeholders

Output a JSON object with:
- summary: Overall summary of the analysis
- recommendation: Strategic recommendation for the proposal
- next_steps: Array of specific next steps for stakeholders
"""
        
        # Prepare analysis summary for the prompt
        tasks_summary = "\n".join([
            f"Task ({task.get('priority', 'medium')}): {task.get('description', '')}"
            for task in tasks[:5]  # Limit to 5 tasks
        ])
        
        blockers_summary = "\n".join([f"- {blocker}" for blocker in blockers[:3]])
        
        for_arguments = "\n".join([f"- {arg}" for arg in arguments.get("for_proposal", [])[:3]])
        against_arguments = "\n".join([f"- {arg}" for arg in arguments.get("against", [])[:3]])
        
        user_prompt = f"""Governance Proposal:
Title: {metadata.get('title', 'Untitled')}
Protocol: {metadata.get('protocol', 'Unknown')}
Category: {metadata.get('category', 'Unknown')}

Key Tasks:
{tasks_summary}

Blockers:
{blockers_summary}

Arguments For:
{for_arguments}

Arguments Against:
{against_arguments}

Critique:
{critique[:300] if critique else "No critique available"}

Based on this analysis, generate a strategic recommendation for this proposal.
Provide a summary of the key points and outline specific next steps for stakeholders.
"""
        
        # Initialize the language model
        model = os.getenv("WEI_AGENT_STRATEGY_MODEL", "anthropic/claude-3-opus-20240229")
        temperature = float(os.getenv("WEI_AGENT_STRATEGY_TEMPERATURE", "0.3"))
        
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
                "proposal_title": metadata.get('title', 'Untitled')
            }
        )
        
        # Extract strategy from response
        response_text = response.content
        logger.debug(f"Strategy agent response: {response_text}")
        
        # Parse the response to extract strategy
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        summary = ""
        recommendation = ""
        next_steps = []
        
        if json_match:
            try:
                response_json = json.loads(json_match.group(1))
                summary = response_json.get("summary", "")
                recommendation = response_json.get("recommendation", "")
                next_steps = response_json.get("next_steps", [])
                logger.info(f"Successfully parsed strategy from JSON response")
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from response")
                # Fallback to pattern matching
                summary_match = re.search(r'summary"?\s*:?\s*"(.*?)"', response_text, re.DOTALL)
                if summary_match:
                    summary = summary_match.group(1)
                
                recommendation_match = re.search(r'recommendation"?\s*:?\s*"(.*?)"', response_text, re.DOTALL)
                if recommendation_match:
                    recommendation = recommendation_match.group(1)
                
                next_steps = extract_next_steps_from_text(response_text)
        else:
            # Fallback to pattern matching
            paragraphs = response_text.split("\n\n")
            
            # Try to find summary and recommendation in paragraphs
            for para in paragraphs:
                if "summary" in para.lower() or "overview" in para.lower():
                    summary = para
                elif "recommend" in para.lower() or "strategy" in para.lower():
                    recommendation = para
            
            # Extract next steps
            next_steps = extract_next_steps_from_text(response_text)
        
        # If we still don't have a summary or recommendation, use the first and second paragraphs
        if not summary and len(paragraphs) > 0:
            summary = paragraphs[0]
        
        if not recommendation and len(paragraphs) > 1:
            recommendation = paragraphs[1]
        
        # Ensure we have at least one next step
        if not next_steps:
            next_steps = ["Review the proposal in more detail", "Consult with subject matter experts"]
        
        # Update the state with strategy
        state["summary"] = summary
        state["recommendation"] = recommendation
        state["next_steps"] = next_steps
        
        logger.info(f"Generated strategic recommendation with {len(next_steps)} next steps")
        
        return state
    except Exception as e:
        logger.error(f"Error in strategy agent: {str(e)}", exc_info=True)
        state["summary"] = f"Error in strategy agent: {str(e)}"
        state["recommendation"] = "Unable to generate recommendation due to an error"
        state["next_steps"] = ["Review the proposal manually", "Investigate the error in the strategy agent"]
        return state
