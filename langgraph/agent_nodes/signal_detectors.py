"""
Signal Detectors Node

This module contains the signal detectors node for the proposal analysis workflow.
This node analyzes the claims, evidence, and graph analysis to detect signals
that may indicate issues or opportunities in the proposal.
"""

import logging
import re
from typing import Dict, Any, List
from agent_state import AgentState

# Configure logging
logger = logging.getLogger('agent_nodes.signal_detectors')

def signal_detectors(state: AgentState) -> AgentState:
    """Tool Node: Detect signals in the proposal analysis.
    
    This node analyzes the claims, evidence, and graph analysis to detect
    signals that may indicate issues or opportunities in the proposal.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with detected signals
    """
    try:
        logger.info("==== SIGNAL DETECTORS NODE ====")
        logger.info("Detecting signals in proposal analysis...")
        
        # Extract claims, evidence, and graph analysis
        claims_evidence = state.get("claims_evidence", [])
        graph_analysis = state.get("graph_analysis", {})
        proposal_text = state.get("proposal", "")
        metadata = state.get("metadata", {})
        
        if not claims_evidence:
            logger.warning("No claims and evidence provided")
            state["signals"] = []
            return state
        
        # Initialize signals list
        signals = []
        
        # 1. Detect claims with low confidence or insufficient evidence
        for claim_obj in claims_evidence:
            claim = claim_obj.get("claim", "")
            confidence = claim_obj.get("confidence", 0.5)
            evidence_list = claim_obj.get("evidence", [])
            
            if confidence < 0.3:
                signals.append({
                    "type": "low_confidence_claim",
                    "severity": "high",
                    "description": f"Low confidence claim: {claim}",
                    "confidence": confidence
                })
            
            if len(evidence_list) < 2:
                signals.append({
                    "type": "insufficient_evidence",
                    "severity": "medium",
                    "description": f"Insufficient evidence for claim: {claim}",
                    "evidence_count": len(evidence_list)
                })
        
        # 2. Detect contradictions in claims
        claim_texts = [claim_obj.get("claim", "") for claim_obj in claims_evidence]
        for i, claim1 in enumerate(claim_texts):
            for j, claim2 in enumerate(claim_texts):
                if i < j:  # Avoid comparing a claim with itself or duplicate comparisons
                    # Simple contradiction detection based on negation
                    if ("not " in claim1 and claim1.replace("not ", "") in claim2) or \
                       ("not " in claim2 and claim2.replace("not ", "") in claim1):
                        signals.append({
                            "type": "contradicting_claims",
                            "severity": "high",
                            "description": f"Contradicting claims detected",
                            "claim1": claim1,
                            "claim2": claim2
                        })
        
        # 3. Detect security concerns
        security_keywords = ["security", "vulnerability", "exploit", "attack", "risk", "threat"]
        for claim_obj in claims_evidence:
            claim = claim_obj.get("claim", "").lower()
            if any(keyword in claim for keyword in security_keywords):
                signals.append({
                    "type": "security_concern",
                    "severity": "high",
                    "description": f"Security concern detected: {claim_obj.get('claim', '')}",
                    "confidence": claim_obj.get("confidence", 0.5)
                })
        
        # 4. Detect implementation complexity
        complexity_keywords = ["complex", "complicated", "difficult", "challenging", "hard to implement"]
        for claim_obj in claims_evidence:
            claim = claim_obj.get("claim", "").lower()
            if any(keyword in claim for keyword in complexity_keywords):
                signals.append({
                    "type": "implementation_complexity",
                    "severity": "medium",
                    "description": f"Implementation complexity detected: {claim_obj.get('claim', '')}",
                    "confidence": claim_obj.get("confidence", 0.5)
                })
        
        # 5. Detect governance implications
        governance_keywords = ["governance", "voting", "decision", "consensus", "stakeholder"]
        for claim_obj in claims_evidence:
            claim = claim_obj.get("claim", "").lower()
            if any(keyword in claim for keyword in governance_keywords):
                signals.append({
                    "type": "governance_implication",
                    "severity": "medium",
                    "description": f"Governance implication detected: {claim_obj.get('claim', '')}",
                    "confidence": claim_obj.get("confidence", 0.5)
                })
        
        # 6. Detect economic implications
        economic_keywords = ["economic", "incentive", "cost", "benefit", "value", "token", "price"]
        for claim_obj in claims_evidence:
            claim = claim_obj.get("claim", "").lower()
            if any(keyword in claim for keyword in economic_keywords):
                signals.append({
                    "type": "economic_implication",
                    "severity": "medium",
                    "description": f"Economic implication detected: {claim_obj.get('claim', '')}",
                    "confidence": claim_obj.get("confidence", 0.5)
                })
        
        # 7. Detect overall confidence signal based on graph analysis
        overall_confidence = graph_analysis.get("overall_confidence", 0.5)
        if overall_confidence < 0.4:
            signals.append({
                "type": "low_overall_confidence",
                "severity": "high",
                "description": "Low overall confidence in proposal claims",
                "confidence": overall_confidence
            })
        elif overall_confidence > 0.8:
            signals.append({
                "type": "high_overall_confidence",
                "severity": "low",
                "description": "High overall confidence in proposal claims",
                "confidence": overall_confidence
            })
        
        # Update the state with detected signals
        state["signals"] = signals
        
        logger.info(f"Detected {len(signals)} signals in proposal analysis")
        
        return state
    except Exception as e:
        logger.error(f"Error in signal detectors node: {str(e)}", exc_info=True)
        state["signals"] = []
        return state
