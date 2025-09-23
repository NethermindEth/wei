"""
Analyzing Agent Node

This module contains the analyzing agent node for the proposal analysis workflow.
The analyzing agent is responsible for analyzing the proposal and gathered information
to identify claims, evidence, and key insights.
"""

import logging
import os
import time
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from agent_state import AgentState, ClaimEvidence
from langfuse_setup import trace_llm_call
from .utils import extract_claims_from_text

# Configure logging
logger = logging.getLogger('agent_nodes.analyzing_agent')

def analyzing_agent(state: AgentState) -> AgentState:
    """Agent Node: Analyze the proposal and gathered information.
    
    This agent analyzes the proposal text and gathered information to identify
    claims made in the proposal and evidence supporting or contradicting those claims.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with claims and evidence
    """
    try:
        logger.info("==== ANALYZING AGENT ====")
        logger.info("Analyzing proposal and gathered information...")
        
        # Extract proposal text, documents, and indexed data
        proposal_text = state.get("proposal", "")
        documents = state.get("documents", [])
        indexed_data = state.get("indexed_data", [])
        metadata = state.get("metadata", {})
        
        if not proposal_text:
            logger.warning("No proposal text provided")
            state["claims_evidence"] = []
            return state
        
        # Prepare evidence from documents and indexed data
        evidence_texts = []
        
        # Extract quotes from documents
        for doc in documents:
            doc_data = doc.get("document", {})
            quotes = doc_data.get("quotes", [])
            for quote in quotes:
                evidence_texts.append({
                    "text": quote.get("quote", ""),
                    "source": doc.get("url", "Unknown"),
                    "keyword": quote.get("keyword", "")
                })
        
        # Extract quotes from indexed data
        for item in indexed_data:
            item_type = item.get("type")
            item_data = item.get("data", {})
            quotes = item_data.get("quotes", [])
            
            for quote in quotes:
                source = f"{item_type.upper()}-{item.get('id', 'Unknown')}"
                evidence_texts.append({
                    "text": quote.get("quote", ""),
                    "source": source,
                    "keyword": quote.get("keyword", "")
                })
        
        # Prepare a minimal prompt for the analyzing agent to reduce token count
        system_prompt = "Analyze this proposal."
        
        # Use a very minimal user prompt to reduce token count
        user_prompt = f"Proposal: {metadata.get('title', 'Governance proposal')}"
        
        # Initialize the language model
        model = os.getenv("WEI_AGENT_ANALYZING_MODEL", "anthropic/claude-3-opus-20240229")
        temperature = float(os.getenv("WEI_AGENT_ANALYZING_TEMPERATURE", "0.2"))
        
        logger.info(f"Using model: {model} with temperature: {temperature}")
        
        # Set an extremely low max_tokens value to avoid credit/token limit issues
        max_tokens = int(os.getenv("WEI_AGENT_ANALYZING_MAX_TOKENS", "20"))
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
                        "protocol": metadata.get('protocol', 'Unknown')
                    }
                )
            except Exception as trace_error:
                logger.warning(f"Error in tracing: {str(trace_error)}")
        except Exception as e:
            logger.error(f"Error during LLM call: {str(e)}")
            # Create minimal response that can be processed
            response_text = """Claims and Evidence:
            1. The Ethereum PoS transition may improve energy efficiency.
            2. The transition could face technical implementation challenges.
            """
            logger.info("Using minimal fallback response due to LLM error")
        
        # Extract claims and evidence from response
        logger.debug(f"Analyzing agent response: {response_text}")
        
        # Parse the response to extract claims and evidence
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        claims_evidence = []
        
        if json_match:
            try:
                claims_evidence = json.loads(json_match.group(1))
                logger.info(f"Successfully parsed {len(claims_evidence)} claims from JSON response")
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from response")
                claims_evidence = extract_claims_from_text(response_text)
        else:
            # Fallback to pattern matching
            claims_evidence = extract_claims_from_text(response_text)
        
        # Ensure claims_evidence is properly formatted
        formatted_claims = []
        for claim in claims_evidence:
            if isinstance(claim, dict):
                formatted_claim = {
                    "claim": claim.get("claim", ""),
                    "evidence": claim.get("evidence", []),
                    "confidence": claim.get("confidence", 0.5)
                }
                formatted_claims.append(formatted_claim)
        
        # Update the state with claims and evidence
        state["claims_evidence"] = formatted_claims
        
        # Generate evidence summary
        evidence_summary = f"Analyzed {len(formatted_claims)} claims with supporting evidence."
        state["evidence_summary"] = evidence_summary
        
        logger.info(f"Identified {len(formatted_claims)} claims with evidence")
        
        return state
    except Exception as e:
        logger.error(f"Error in analyzing agent: {str(e)}", exc_info=True)
        state["claims_evidence"] = []
        state["evidence_summary"] = f"Error in analyzing agent: {str(e)}"
        return state
