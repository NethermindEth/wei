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
        
        # Prepare the prompt for the prioritizer agent
        system_prompt = """You are a governance proposal prioritizer agent. Your task is to:
1. Prioritize the findings from the proposal analysis
2. Identify key tasks that should be performed based on the analysis
3. Identify any blockers that prevent a complete evaluation
4. Determine the priority level for each task (high, medium, low)

Output a JSON object with:
- tasks: Array of task objects with description and priority
- blockers: Array of blocker descriptions
"""
        
        # Prepare analysis summary for the prompt
        claims_summary = "\n".join([
            f"Claim: {claim_obj.get('claim', '')} (Confidence: {claim_obj.get('confidence', 0.5)})"
            for claim_obj in claims_evidence[:5]  # Limit to 5 claims
        ])
        
        hypotheses_summary = "\n".join([
            f"Hypothesis ({hyp.get('type', 'implication')}): {hyp.get('hypothesis', '')}"
            for hyp in hypotheses[:5]  # Limit to 5 hypotheses
        ])
        
        signals_summary = "\n".join([
            f"Signal ({signal.get('type', '')}): {signal.get('description', '')}"
            for signal in signals[:5]  # Limit to 5 signals
        ])
        
        critique_summary = critique[:300] if critique else "No critique available"
        
        gaps_summary = "\n".join([f"- {gap}" for gap in gaps[:5]])
        
        rag_summary = ""
        for rag_item in rag_results[:3]:  # Limit to 3 RAG queries
            query = rag_item.get("query", "")
            results = rag_item.get("results", [])
            
            rag_summary += f"Query: {query}\n"
            for result in results[:1]:  # Limit to 1 result per query
                content = result.get("content", "")
                rag_summary += f"Result: {content[:100]}...\n"
        
        user_prompt = f"""Governance Proposal:
Title: {metadata.get('title', 'Untitled')}
Protocol: {metadata.get('protocol', 'Unknown')}
Category: {metadata.get('category', 'Unknown')}

Key Claims:
{claims_summary}

Hypotheses:
{hypotheses_summary}

Signals:
{signals_summary}

Critique:
{critique_summary}

Gaps:
{gaps_summary}

Additional Context from RAG:
{rag_summary}

Based on this analysis, prioritize the findings and generate tasks that should be performed.
Identify any blockers that prevent a complete evaluation of the proposal.
"""
        
        # Initialize the language model
        model = os.getenv("WEI_AGENT_PRIORITIZER_MODEL", "anthropic/claude-3-opus-20240229")
        temperature = float(os.getenv("WEI_AGENT_PRIORITIZER_TEMPERATURE", "0.3"))
        
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
        
        # Extract tasks and blockers from response
        response_text = response.content
        logger.debug(f"Prioritizer agent response: {response_text}")
        
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
        
        logger.info(f"Generated {len(formatted_tasks)} tasks and identified {len(blockers)} blockers")
        
        return state
    except Exception as e:
        logger.error(f"Error in prioritizer agent: {str(e)}", exc_info=True)
        state["tasks"] = [{"description": "Review the proposal for technical feasibility", "priority": "high"}]
        state["blockers"] = [f"Error in prioritizer agent: {str(e)}"]
        return state
