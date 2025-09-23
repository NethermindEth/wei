"""
Hypothesizer Node

This module contains the hypothesizer node for the proposal analysis workflow.
This node generates hypotheses about the proposal based on the claims, evidence,
and detected signals.
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
logger = logging.getLogger('agent_nodes.hypothesizer')

def hypothesizer(state: AgentState) -> AgentState:
    """Agent Node: Generate hypotheses about the proposal.
    
    This node generates hypotheses about the proposal based on the claims,
    evidence, and detected signals. It identifies potential implications,
    risks, and benefits of the proposal.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with hypotheses
    """
    try:
        logger.info("==== HYPOTHESIZER NODE ====")
        logger.info("Generating hypotheses about the proposal...")
        
        # Extract claims, evidence, signals, and proposal text
        claims_evidence = state.get("claims_evidence", [])
        signals = state.get("signals", [])
        proposal_text = state.get("proposal", "")
        metadata = state.get("metadata", {})
        
        if not claims_evidence and not signals:
            logger.warning("No claims, evidence, or signals provided")
            state["hypotheses"] = []
            return state
        
        # Prepare the prompt for the hypothesizer
        system_prompt = """You are a governance proposal hypothesizer. Your task is to:
1. Generate hypotheses about the implications of the proposal
2. Identify potential risks and benefits
3. Consider second-order effects and unintended consequences
4. Assess the likelihood and impact of each hypothesis

Output a JSON array of hypothesis objects, each with:
- hypothesis: The hypothesis statement
- type: "risk", "benefit", or "implication"
- likelihood: Numeric likelihood score from 0.0 to 1.0
- impact: Numeric impact score from 0.0 to 1.0
- reasoning: Brief reasoning for the hypothesis
"""
        
        # Prepare claims and signals summary for the prompt
        claims_summary = "\n".join([
            f"Claim: {claim_obj.get('claim', '')} (Confidence: {claim_obj.get('confidence', 0.5)})"
            for claim_obj in claims_evidence[:10]  # Limit to 10 claims
        ])
        
        signals_summary = "\n".join([
            f"Signal: {signal.get('description', '')} (Severity: {signal.get('severity', 'medium')})"
            for signal in signals
        ])
        
        user_prompt = f"""Governance Proposal:
Title: {metadata.get('title', 'Untitled')}
Protocol: {metadata.get('protocol', 'Unknown')}
Category: {metadata.get('category', 'Unknown')}

Key Claims:
{claims_summary}

Detected Signals:
{signals_summary}

Generate hypotheses about the implications, risks, and benefits of this proposal.
Consider both direct effects and potential second-order or unintended consequences.
"""
        
        # Initialize the language model
        model = os.getenv("WEI_AGENT_HYPOTHESIZER_MODEL", "anthropic/claude-3-opus-20240229")
        temperature = float(os.getenv("WEI_AGENT_HYPOTHESIZER_TEMPERATURE", "0.7"))
        
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
                "claims_count": len(claims_evidence),
                "signals_count": len(signals)
            }
        )
        
        # Extract hypotheses from response
        response_text = response.content
        logger.debug(f"Hypothesizer response: {response_text}")
        
        # Parse the response to extract hypotheses
        import json
        import re
        
        # Try to extract JSON from the response using improved JSON extraction
        # This implementation is inspired by the improvements mentioned in the memory
        # about enhanced JSON parsing functionality
        def extract_json_from_markdown(text):
            # Try with code block markers (multiple types)
            patterns = [
                r'```(?:json)?\s*([\s\S]*?)\s*```',  # Standard markdown
                r'```JSON\s*([\s\S]*?)\s*```',       # Uppercase JSON
                r'~~~(?:json)?\s*([\s\S]*?)\s*~~~',  # Alternative markers
                r"'''(?:json)?\s*([\s\S]*?)\s*'''",  # Single quote alternative
            ]
            
            for pattern in patterns:
                json_match = re.search(pattern, text)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        continue
            
            # Try to find JSON-like content without markers
            try:
                # Look for array pattern
                array_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
                if array_match:
                    return json.loads(array_match.group(0))
                
                # Look for object pattern
                object_match = re.search(r'\{\s*".*\}\s*', text, re.DOTALL)
                if object_match:
                    return json.loads(object_match.group(0))
            except json.JSONDecodeError:
                pass
            
            # Final fallback: try to parse the entire text
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return None
        
        # Extract hypotheses using the improved JSON extraction
        hypotheses = extract_json_from_markdown(response_text)
        
        # Fallback to simple pattern matching if JSON extraction fails
        if not hypotheses:
            logger.warning("Failed to parse JSON from response, using fallback extraction")
            
            # Simple pattern matching for hypotheses
            hypothesis_pattern = r'(?:Hypothesis|Risk|Benefit|Implication):\s*(.*?)(?:\n|$)'
            matches = re.findall(hypothesis_pattern, response_text, re.IGNORECASE)
            
            hypotheses = []
            for i, match in enumerate(matches):
                hypothesis_text = match.strip()
                if hypothesis_text:
                    # Determine type based on keywords
                    hypothesis_type = "implication"
                    if "risk" in hypothesis_text.lower():
                        hypothesis_type = "risk"
                    elif "benefit" in hypothesis_text.lower():
                        hypothesis_type = "benefit"
                    
                    hypotheses.append({
                        "hypothesis": hypothesis_text,
                        "type": hypothesis_type,
                        "likelihood": 0.5,  # Default values
                        "impact": 0.5,
                        "reasoning": "Extracted from text response"
                    })
        
        # Ensure hypotheses is a list
        if not isinstance(hypotheses, list):
            if isinstance(hypotheses, dict):
                # If it's a dict, it might be a wrapper object
                if "hypotheses" in hypotheses:
                    hypotheses = hypotheses["hypotheses"]
                else:
                    # Convert single dict to list
                    hypotheses = [hypotheses]
            else:
                # Fallback to empty list
                hypotheses = []
        
        # Ensure each hypothesis has the required fields
        formatted_hypotheses = []
        for hyp in hypotheses:
            if isinstance(hyp, dict):
                formatted_hyp = {
                    "hypothesis": hyp.get("hypothesis", ""),
                    "type": hyp.get("type", "implication"),
                    "likelihood": hyp.get("likelihood", 0.5),
                    "impact": hyp.get("impact", 0.5),
                    "reasoning": hyp.get("reasoning", "")
                }
                formatted_hypotheses.append(formatted_hyp)
        
        # Update the state with hypotheses
        state["hypotheses"] = formatted_hypotheses
        
        # Generate arguments for and against the proposal
        # This is inspired by the memory about proposal argument generation
        for_arguments = []
        against_arguments = []
        
        for hyp in formatted_hypotheses:
            hyp_type = hyp.get("type", "")
            hyp_text = hyp.get("hypothesis", "")
            
            if hyp_type == "benefit":
                for_arguments.append(hyp_text)
            elif hyp_type == "risk":
                against_arguments.append(hyp_text)
            elif hyp_type == "implication":
                # Determine if implication is positive or negative
                impact = hyp.get("impact", 0.5)
                likelihood = hyp.get("likelihood", 0.5)
                
                if impact > 0.6 and likelihood > 0.5:
                    for_arguments.append(hyp_text)
                elif impact < 0.4 and likelihood > 0.5:
                    against_arguments.append(hyp_text)
        
        # Ensure we have at least some arguments on each side
        if not for_arguments:
            for_arguments = ["The proposal may have benefits that are not immediately apparent"]
        if not against_arguments:
            against_arguments = ["The proposal may have risks that require further investigation"]
        
        # Add arguments to state
        state["arguments"] = {
            "for_proposal": for_arguments,
            "against": against_arguments
        }
        
        logger.info(f"Generated {len(formatted_hypotheses)} hypotheses")
        logger.info(f"Generated {len(for_arguments)} arguments for and {len(against_arguments)} arguments against the proposal")
        
        return state
    except Exception as e:
        logger.error(f"Error in hypothesizer node: {str(e)}", exc_info=True)
        state["hypotheses"] = []
        state["arguments"] = {
            "for_proposal": ["Unable to generate arguments for the proposal due to an error"],
            "against": ["Unable to generate arguments against the proposal due to an error"]
        }
        return state
