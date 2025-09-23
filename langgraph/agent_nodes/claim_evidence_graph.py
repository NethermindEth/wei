"""
Claim Evidence Graph Node

This module contains the claim evidence graph node for the proposal analysis workflow.
This node builds a graph representation of claims and evidence to identify
relationships and patterns.
"""

import logging
import networkx as nx
from typing import Dict, Any, List
from agent_state import AgentState, ClaimEvidence

# Configure logging
logger = logging.getLogger('agent_nodes.claim_evidence_graph')

def claim_evidence_graph_store(state: AgentState) -> AgentState:
    """Tool Node: Build and analyze a graph of claims and evidence.
    
    This node takes the claims and evidence identified by the analyzing agent
    and builds a graph representation to identify relationships and patterns.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with claim-evidence graph analysis
    """
    try:
        logger.info("==== CLAIM EVIDENCE GRAPH NODE ====")
        logger.info("Building and analyzing claim-evidence graph...")
        
        # Extract claims and evidence
        claims_evidence = state.get("claims_evidence", [])
        
        if not claims_evidence:
            logger.warning("No claims and evidence provided")
            state["graph_analysis"] = "No claims and evidence to analyze."
            return state
        
        # Create a graph
        G = nx.DiGraph()
        
        # Add claims as nodes
        for i, claim_obj in enumerate(claims_evidence):
            claim = claim_obj.get("claim", "")
            confidence = claim_obj.get("confidence", 0.5)
            
            # Add claim node
            G.add_node(f"claim_{i}", type="claim", text=claim, confidence=confidence)
            
            # Add evidence nodes and edges
            evidence_list = claim_obj.get("evidence", [])
            for j, evidence in enumerate(evidence_list):
                evidence_text = evidence.get("text", "")
                evidence_source = evidence.get("source", "Unknown")
                evidence_relation = evidence.get("relation", "supporting")
                
                # Add evidence node
                evidence_id = f"evidence_{i}_{j}"
                G.add_node(evidence_id, type="evidence", text=evidence_text, source=evidence_source)
                
                # Add edge from evidence to claim
                G.add_edge(evidence_id, f"claim_{i}", relation=evidence_relation)
        
        # Analyze the graph
        # 1. Identify claims with the most supporting evidence
        claim_support = {}
        for node in G.nodes():
            if node.startswith("claim_"):
                supporting_evidence = [
                    pred for pred in G.predecessors(node)
                    if G.edges[pred, node]["relation"] == "supporting"
                ]
                contradicting_evidence = [
                    pred for pred in G.predecessors(node)
                    if G.edges[pred, node]["relation"] == "contradicting"
                ]
                
                claim_support[node] = {
                    "supporting": len(supporting_evidence),
                    "contradicting": len(contradicting_evidence),
                    "net_support": len(supporting_evidence) - len(contradicting_evidence)
                }
        
        # 2. Identify evidence that supports multiple claims
        evidence_connections = {}
        for node in G.nodes():
            if node.startswith("evidence_"):
                connected_claims = list(G.successors(node))
                evidence_connections[node] = {
                    "connected_claims": len(connected_claims),
                    "claim_ids": connected_claims
                }
        
        # 3. Calculate overall confidence based on evidence
        overall_confidence = sum(
            G.nodes[node]["confidence"] for node in G.nodes() if node.startswith("claim_")
        ) / max(1, sum(1 for node in G.nodes() if node.startswith("claim_")))
        
        # Generate graph analysis summary
        graph_analysis = {
            "claim_count": sum(1 for node in G.nodes() if node.startswith("claim_")),
            "evidence_count": sum(1 for node in G.nodes() if node.startswith("evidence_")),
            "strongest_claims": sorted(
                [
                    {
                        "claim": G.nodes[node]["text"],
                        "net_support": claim_support[node]["net_support"],
                        "supporting": claim_support[node]["supporting"],
                        "contradicting": claim_support[node]["contradicting"]
                    }
                    for node in claim_support
                ],
                key=lambda x: x["net_support"],
                reverse=True
            )[:3],  # Top 3 strongest claims
            "overall_confidence": overall_confidence
        }
        
        # Update the state with graph analysis
        state["graph_analysis"] = graph_analysis
        
        logger.info(f"Built graph with {graph_analysis['claim_count']} claims and {graph_analysis['evidence_count']} evidence nodes")
        logger.info(f"Overall confidence: {overall_confidence:.2f}")
        
        return state
    except Exception as e:
        logger.error(f"Error in claim evidence graph node: {str(e)}", exc_info=True)
        state["graph_analysis"] = f"Error in claim evidence graph analysis: {str(e)}"
        return state
