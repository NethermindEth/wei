"""
DeepAgent Subagents Module

This module defines custom subagents for specialized tasks in the proposal analysis workflow.
These subagents can be used with the deepagents package to handle specific aspects of proposal analysis.
"""

import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deepagent_subagents.log')
    ]
)
logger = logging.getLogger('deepagent_subagents')

# Argument generation subagent for creating balanced arguments
argument_subagent = {
    "name": "argument-agent",
    "description": "Used to generate balanced arguments for and against proposals",
    "prompt": """You are a specialized argument generation agent focused on governance proposals.
Your task is to create strong, balanced arguments both for and against proposals
to help stakeholders make informed decisions.

Use the generate_proposal_arguments tool to create initial arguments.
Refine these arguments based on the specific details of the proposal.
Ensure arguments are specific, substantive, and directly related to the proposal.

Generate at least 3-5 strong arguments on each side.
Avoid generic, placeholder, or repetitive arguments.
Each argument should be concise but substantive (1-3 sentences).
""",
    "tools": ["generate_proposal_arguments"]
}

# List of all subagents
deepagent_subagents = [
    argument_subagent
]
