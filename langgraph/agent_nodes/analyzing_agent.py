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
        
        # Prepare the prompt for the analyzing agent
        system_prompt = """You are a governance proposal analyzing agent. Your task is to:
1. Identify key claims made in the proposal
2. Match evidence to these claims (supporting or contradicting)
3. Assess the confidence level for each claim based on evidence

Output a JSON array of claim-evidence objects, each with:
- claim: The claim statement
- evidence: Array of evidence objects with text, source, and relation (supporting/contradicting)
- confidence: Numeric confidence score from 0.0 to 1.0
"""
        
        # Prepare evidence summary for the prompt
        evidence_summary = "\n\n".join([
            f"Evidence {i+1} from {e['source']}:\n{e['text']}"
            for i, e in enumerate(evidence_texts[:20])  # Limit to 20 pieces of evidence
        ])
        
        user_prompt = f"""Governance Proposal:
Title: {metadata.get('title', 'Untitled')}
Protocol: {metadata.get('protocol', 'Unknown')}
Category: {metadata.get('category', 'Unknown')}

Proposal Text:
{proposal_text[:3000]}  # Limit to first 3000 chars

Evidence:
{evidence_summary}

Analyze this proposal to identify key claims and match them with supporting or contradicting evidence.
"""
        
        # Initialize the language model
        model = os.getenv("WEI_AGENT_ANALYZING_MODEL", "anthropic/claude-3-opus-20240229")
        temperature = float(os.getenv("WEI_AGENT_ANALYZING_TEMPERATURE", "0.2"))
        
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
        
        # Extract claims and evidence from response
        response_text = response.content
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
