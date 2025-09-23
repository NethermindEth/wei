"""Agent Nodes Module

This module re-exports all agent nodes and utility functions from the agent_nodes package.
It serves as a backward-compatible interface for existing code that imports from this module.

Note: This file is maintained for backward compatibility. New code should import directly
from the agent_nodes package.
"""

import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_nodes.log')
    ]
)
logger = logging.getLogger('agent_nodes')

# Import all node functions from the agent_nodes package
from agent_nodes import (
    # Agent nodes
    planning_agent,
    search_tool_node,
    indexer_tool_node,
    reader_tool_node,
    analyzing_agent,
    claim_evidence_graph_store,
    signal_detectors,
    hypothesizer,
    skeptic_agent,
    rag_fallback,
    prioritizer_agent,
    strategy_agent,
    
    # Utility functions
    search_web,
    search_indexed,
    fetch_eip,
    fetch_bip,
    fetch_forum_post,
    read_document,
    clip_quotes,
    rag_query,
    extract_claims_from_text,
    extract_tasks_from_text,
    extract_blockers_from_text,
    extract_next_steps_from_text
)

logger.info("Agent nodes imported successfully from package")
