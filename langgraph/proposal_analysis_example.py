#!/usr/bin/env python
# coding: utf-8

"""
# Proposal Analysis Agent Example

This script demonstrates how to use the Proposal Analysis Agent to analyze governance proposals.
It showcases the full workflow from proposal input to detailed analysis output, including
claim verification, risk assessment, and recommendation generation.

The example includes proper error handling, logging, and configuration management.
"""

# Disable LangChain tracing and LangSmith integration
import disable_langchain_tracing

# Standard library imports
import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('proposal_analysis_example.log')
    ]
)
logger = logging.getLogger('proposal_analysis_example')

# Try to import optional dependencies
try:
    from dotenv import load_dotenv
    # Load environment variables
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except ImportError:
    logger.warning("python-dotenv not installed. Environment variables may not be loaded correctly.")
    def load_dotenv():
        pass

# Try to import proposal analysis components
try:
    from proposal_analyzer import analyze_proposal, Config, check_api_keys
    from agent_state import AgentState, ProposalMetadata
    from agent_nodes import planning_agent, search_tool_node, indexer_tool_node
    import agent_tools
    analysis_available = True
    logger.info("Proposal analysis components imported successfully")
except ImportError as e:
    logger.error(f"Could not import proposal analysis components: {str(e)}")
    logger.warning("Running in demo mode with mock responses")
    analysis_available = False
    
    # Define a minimal Config class for demo mode
    class Config:
        """Minimal configuration for demo mode."""
        OPENROUTER_API_KEY = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
        EXA_API_KEY = os.getenv("WEI_AGENT_EXA_API_KEY")
        DEFAULT_MODEL = "anthropic/claude-3-opus-20240229"
        ANALYSIS_DEPTH = "comprehensive"

# Check API keys
if analysis_available:
    api_keys_available = check_api_keys()
    if not api_keys_available:
        logger.warning("Some required API keys are missing. The agent may fall back to mock responses.")
else:
    # Manual check in demo mode
    if not Config.OPENROUTER_API_KEY or not Config.EXA_API_KEY:
        logger.warning("Some required API keys are missing. The agent may fall back to mock responses.")

# Example Proposal
example_proposal = """
# EIP-1234: Ethereum Network Upgrade - Proof of Stake Transition

## Abstract
This proposal outlines a comprehensive plan for transitioning the Ethereum network from Proof of Work (PoW) to Proof of Stake (PoS) consensus mechanism. The transition aims to significantly reduce energy consumption, improve scalability, and enhance security of the network.

## Motivation
The current PoW consensus mechanism has several limitations:
1. High energy consumption and environmental impact
2. Limited scalability with increasing transaction volumes
3. Potential centralization due to mining hardware requirements

By transitioning to PoS, Ethereum can address these issues while maintaining decentralization and security.

## Specification
The transition will occur in three phases:

### Phase 1: Beacon Chain Deployment
- Launch a parallel PoS chain (Beacon Chain)
- Allow ETH holders to become validators by staking their ETH
- Minimum stake requirement: 32 ETH

### Phase 2: The Merge
- Merge the existing PoW chain with the Beacon Chain
- Transition block production to PoS validators
- Maintain backward compatibility for existing applications

### Phase 3: Sharding Implementation
- Implement sharding to improve scalability
- Split the network into 64 shard chains
- Enable parallel transaction processing

## Security Considerations
- Slashing mechanisms to penalize malicious validators
- Minimum stake requirements to prevent Sybil attacks
- Decentralization metrics will be continuously monitored

## Backward Compatibility
All existing applications will continue to function without modification after the transition.
"""

example_metadata = {
    "id": "EIP-1234",
    "title": "Ethereum Network Upgrade - Proof of Stake Transition",
    "author": "Vitalik Buterin",
    "date_submitted": "2022-03-15",
    "protocol": "Ethereum",
    "category": "Core",
    "url": "https://eips.ethereum.org/EIPS/eip-1234"
}


def save_analysis_results(results: Dict[str, Any], output_path: str = "analysis_results.json") -> None:
    """
    Save analysis results to a JSON file.
    
    Args:
        results: The analysis results to save
        output_path: Path where to save the JSON file
        
    Returns:
        None
    """
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Analysis results saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save analysis results: {str(e)}")


def display_analysis_summary(results: Dict[str, Any]) -> None:
    """
    Display a summary of the analysis results in a structured format.
    
    Args:
        results: The analysis results to display
        
    Returns:
        None
    """
    logger.info("===== ANALYSIS SUMMARY =====")
    
    # Display basic information
    logger.info(f"Proposal: {results.get('metadata', {}).get('title', 'Unknown')}")
    logger.info(f"Protocol: {results.get('metadata', {}).get('protocol', 'Unknown')}")
    
    # Display tasks
    logger.info("\nKey Tasks:")
    for task in results.get('tasks', [])[:5]:  # Show top 5 tasks
        logger.info(f"- {task.get('description', 'Unknown')} (Priority: {task.get('priority', 'medium')})")
    
    # Display blockers
    if results.get('blockers'):
        logger.info("\nBlockers:")
        for blocker in results.get('blockers', []):
            logger.info(f"- {blocker}")
    
    # Display summary
    if 'summary' in results:
        logger.info("\nSummary:")
        logger.info(results['summary'])
    
    # Display recommendation
    if 'recommendation' in results:
        logger.info("\nRecommendation:")
        logger.info(results['recommendation'])
    
    # Display next steps
    if results.get('next_steps'):
        logger.info("\nNext Steps:")
        for step in results.get('next_steps', []):
            logger.info(f"- {step}")
            
    logger.info("===== END OF SUMMARY =====")


def run_mock_analysis() -> Dict[str, Any]:
    """
    Run a mock analysis when the actual analysis components are not available.
    
    Returns:
        Dict[str, Any]: Mock analysis results
    """
    logger.info("Running mock analysis with sample data")
    
    return {
        "metadata": example_metadata,
        "summary": "This proposal outlines a transition from Proof of Work to Proof of Stake for Ethereum.",
        "tasks": [
            {"description": "Review technical feasibility of PoS implementation", "priority": "high"},
            {"description": "Assess security implications of the transition", "priority": "high"},
            {"description": "Evaluate economic impact on validators and miners", "priority": "medium"},
            {"description": "Review backward compatibility measures", "priority": "medium"},
            {"description": "Analyze energy consumption reduction claims", "priority": "low"}
        ],
        "blockers": [],
        "evidence_summary": "The proposal provides a comprehensive plan for the PoW to PoS transition with clear phases and security considerations.",
        "next_steps": [
            "Conduct formal security audit of the proposed implementation",
            "Create educational resources for validators",
            "Develop monitoring tools for the transition period"
        ],
        "recommendation": "The proposal is technically sound and addresses key concerns. Recommended for implementation with minor adjustments to the timeline."
    }


def main() -> None:
    """
    Main function to run the proposal analysis example.
    """
    logger.info("Starting proposal analysis example")
    
    try:
        # Check if we can run the actual analysis
        if analysis_available and Config.OPENROUTER_API_KEY and Config.EXA_API_KEY:
            logger.info("Running full proposal analysis with actual components")
            
            # Set analysis parameters
            export_json = True
            json_path = "eip1234_analysis_results.json"
            
            # Run the analysis
            try:
                results = analyze_proposal(
                    proposal=example_proposal,
                    metadata=example_metadata,
                    export_json=export_json,
                    json_path=json_path
                )
                logger.info("Analysis completed successfully")
            except Exception as e:
                logger.error(f"Error during proposal analysis: {str(e)}", exc_info=True)
                logger.warning("Falling back to mock analysis")
                results = run_mock_analysis()
        else:
            # Run mock analysis if components or API keys are not available
            logger.warning("Required components or API keys not available")
            results = run_mock_analysis()
        
        # Display and save results
        display_analysis_summary(results)
        save_analysis_results(results)
        
    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}", exc_info=True)
        sys.exit(1)
    
    logger.info("Proposal analysis example completed")


# Run the example if this script is executed directly
if __name__ == "__main__":
    main()
