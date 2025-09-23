"""
RAG Fallback Node

This module contains the RAG fallback node for the proposal analysis workflow.
This node uses Retrieval-Augmented Generation to gather additional information
when the skeptic agent identifies gaps in the analysis.
"""

import logging
from typing import Dict, Any, List
from agent_state import AgentState
from .utils import rag_query

# Configure logging
logger = logging.getLogger('agent_nodes.rag_fallback')

def rag_fallback(state: AgentState) -> AgentState:
    """Tool Node: Use RAG to gather additional information.
    
    This node uses Retrieval-Augmented Generation to gather additional information
    when the skeptic agent identifies gaps in the analysis. It queries the RAG system
    with specific questions based on the identified gaps.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with additional information from RAG
    """
    try:
        logger.info("==== RAG FALLBACK NODE ====")
        logger.info("Using RAG to gather additional information...")
        
        # Extract gaps and claims needing RAG
        gaps = state.get("gaps", [])
        claims_needing_rag = state.get("claims_needing_rag", [])
        critique = state.get("critique", "")
        metadata = state.get("metadata", {})
        
        if not gaps and not claims_needing_rag:
            logger.warning("No gaps or claims identified for RAG fallback")
            state["rag_results"] = []
            return state
        
        # Generate queries based on gaps and claims
        queries = []
        
        # Add queries for gaps
        for gap in gaps:
            # Convert gap to a question
            if not gap.endswith("?"):
                gap_query = f"What information is available about {gap} in the context of {metadata.get('protocol', '')} governance?"
            else:
                gap_query = gap
            
            queries.append(gap_query)
        
        # Add queries for claims needing RAG
        for claim in claims_needing_rag:
            claim_query = f"Is there evidence supporting or contradicting the claim: '{claim}' in {metadata.get('protocol', '')}?"
            queries.append(claim_query)
        
        # Add a general query based on the critique
        if critique:
            general_query = f"What additional context is needed to address this critique: '{critique[:100]}...' for {metadata.get('title', 'this proposal')}?"
            queries.append(general_query)
        
        # Deduplicate and limit queries
        unique_queries = list(set(queries))
        limited_queries = unique_queries[:5]  # Limit to 5 queries
        
        # Execute RAG queries
        rag_results = []
        for query in limited_queries:
            logger.info(f"Executing RAG query: {query}")
            results = rag_query(query, k=3)  # Get top 3 results for each query
            
            if results:
                rag_results.append({
                    "query": query,
                    "results": results
                })
        
        # Update the state with RAG results
        state["rag_results"] = rag_results
        
        # Update evidence summary with RAG results
        evidence_summary = state.get("evidence_summary", "")
        rag_summary = "\n\nAdditional context from RAG:\n"
        
        for rag_item in rag_results:
            query = rag_item.get("query", "")
            results = rag_item.get("results", [])
            
            rag_summary += f"- Query: {query}\n"
            for result in results:
                content = result.get("content", "")
                source = result.get("source", "Unknown")
                rag_summary += f"  - From {source}: {content[:100]}...\n"
        
        state["evidence_summary"] = evidence_summary + rag_summary
        
        # Preserve arguments from previous nodes if they exist
        if "arguments" in state:
            logger.info(f"Preserving arguments in RAG fallback: {state['arguments']}")
        else:
            logger.warning("No arguments found in state during RAG fallback")
        
        logger.info(f"Executed {len(limited_queries)} RAG queries with {sum(len(item.get('results', [])) for item in rag_results)} total results")
        
        return state
    except Exception as e:
        logger.error(f"Error in RAG fallback node: {str(e)}", exc_info=True)
        state["rag_results"] = []
        return state
