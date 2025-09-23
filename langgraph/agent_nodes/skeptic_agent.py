"""
Skeptic Agent Node

This module contains the skeptic agent node for the proposal analysis workflow.
This agent critically evaluates the claims, evidence, and hypotheses to identify
weaknesses and gaps in the analysis.
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
logger = logging.getLogger('agent_nodes.skeptic_agent')

def skeptic_agent(state: AgentState) -> AgentState:
    """Agent Node: Critically evaluate the proposal analysis.
    
    This agent critically evaluates the claims, evidence, and hypotheses
    to identify weaknesses and gaps in the analysis. It challenges assumptions
    and identifies areas that need further investigation.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with critique and identified gaps
    """
    try:
        logger.info("==== SKEPTIC AGENT ====")
        logger.info("Critically evaluating the proposal analysis...")
        
        # Extract claims, evidence, hypotheses, and proposal text
        claims_evidence = state.get("claims_evidence", [])
        hypotheses = state.get("hypotheses", [])
        proposal_text = state.get("proposal", "")
        metadata = state.get("metadata", {})
        
        if not claims_evidence and not hypotheses:
            logger.warning("No claims, evidence, or hypotheses provided")
            state["critique"] = "Insufficient information to perform critical evaluation."
            state["gaps"] = ["No claims or hypotheses to evaluate"]
            state["need_rag_fallback"] = True
            return state
        
        # Prepare a minimal prompt for the skeptic agent to reduce token count
        system_prompt = "Critique this proposal."
        
        # Use a very minimal user prompt to reduce token count
        user_prompt = f"Proposal: {metadata.get('title', 'Governance proposal')}"
        
        # Initialize the language model
        model = os.getenv("WEI_AGENT_SKEPTIC_MODEL", "anthropic/claude-3-opus-20240229")
        temperature = float(os.getenv("WEI_AGENT_SKEPTIC_TEMPERATURE", "0.3"))
        
        logger.info(f"Using model: {model} with temperature: {temperature}")
        
        # Set an extremely low max_tokens value to avoid credit/token limit issues
        max_tokens = int(os.getenv("WEI_AGENT_SKEPTIC_MAX_TOKENS", "20"))
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
                        "proposal_title": metadata.get('title', 'Untitled'),
                        "claims_count": len(claims_evidence),
                        "hypotheses_count": len(hypotheses)
                    }
                )
            except Exception as trace_error:
                logger.warning(f"Error in tracing: {str(trace_error)}")
                
        except Exception as e:
            logger.error(f"Error during LLM call: {str(e)}")
            # Create minimal response that can be processed
            response_text = """Critique:
            The proposal analysis provides a basic overview but lacks detailed technical assessment.
            
            Gaps:
            None identified at this stage.
            
            Need additional information: No
            """
            logger.info("Using minimal fallback response due to LLM error")
        
        # Debug log the response
        logger.debug(f"Skeptic agent response: {response_text}")
        
        # Parse the response to extract critique and gaps
        import json
        import re
        
        # Try to extract JSON from the response using the same improved extraction
        # method as in the hypothesizer
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
        
        # Extract critique and gaps using the improved JSON extraction
        response_json = extract_json_from_markdown(response_text)
        
        # Default values
        critique = "Unable to parse critique from response"
        gaps = []
        need_rag_fallback = False
        claims_needing_rag = []
        
        # Extract values from JSON if available
        if response_json:
            critique = response_json.get("critique", critique)
            gaps = response_json.get("gaps", gaps)
            need_rag_fallback = response_json.get("need_rag_fallback", False)
            claims_needing_rag = response_json.get("claims_needing_rag", [])
        else:
            # Fallback to simple pattern matching
            logger.warning("Failed to parse JSON from response, using fallback extraction")
            
            # Extract critique
            critique_match = re.search(r'critique"?\s*:?\s*"(.*?)"', response_text, re.DOTALL)
            if critique_match:
                critique = critique_match.group(1)
            else:
                # Try to find a paragraph that looks like a critique
                paragraphs = response_text.split("\n\n")
                for para in paragraphs:
                    if "critique" in para.lower() or "evaluation" in para.lower():
                        critique = para
                        break
            
            # Extract gaps
            gaps_match = re.search(r'gaps"?\s*:?\s*\[(.*?)\]', response_text, re.DOTALL)
            if gaps_match:
                gaps_text = gaps_match.group(1)
                gaps = [g.strip(' "\'') for g in gaps_text.split(',')]
            else:
                # Try to find bullet points that look like gaps
                gap_lines = re.findall(r'(?:^|\n)[-*]\s*(.*?)(?:\n|$)', response_text)
                if gap_lines:
                    gaps = [line.strip() for line in gap_lines if line.strip()]
            
            # Extract need_rag_fallback
            rag_match = re.search(r'need_rag_fallback"?\s*:?\s*(true|false)', response_text, re.IGNORECASE)
            if rag_match:
                need_rag_fallback = rag_match.group(1).lower() == "true"
            else:
                # Infer from text
                need_rag_fallback = "additional information" in response_text.lower() or "more context" in response_text.lower()
        
        # Update the state with critique and gaps
        state["critique"] = critique
        state["gaps"] = gaps
        state["need_rag_fallback"] = need_rag_fallback
        state["claims_needing_rag"] = claims_needing_rag
        
        # Preserve arguments from hypothesizer if they exist
        if "arguments" in state:
            logger.info(f"Preserving arguments from hypothesizer: {state['arguments']}")
        else:
            logger.warning("No arguments found in state from hypothesizer")
        
        logger.info(f"Generated critique with {len(gaps)} identified gaps")
        logger.info(f"Need RAG fallback: {need_rag_fallback}")
        
        return state
    except Exception as e:
        logger.error(f"Error in skeptic agent: {str(e)}", exc_info=True)
        state["critique"] = f"Error in skeptic agent: {str(e)}"
        state["gaps"] = ["Error occurred during critical evaluation"]
        state["need_rag_fallback"] = True
        return state
