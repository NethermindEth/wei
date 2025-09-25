"""
Test script for the argument generation tool.

This script tests the argument generation tool directly without using the full deep agent.
"""

import logging
import json
import os
import sys

# Import helper to add parent directory to path
import import_helper

# Now we can import modules from the parent directory
try:
    from deepagent_tools import generate_proposal_arguments
except ImportError as e:
    print(f"Error importing deepagent_tools: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_argument_generation.log')
    ]
)
logger = logging.getLogger('test_argument_generation')

def main():
    """Run a test of the argument generation tool."""
    logger.info("Testing argument generation tool...")
    
    # Example proposal text
    example_proposal = """
    EIP-1559: Fee Market Change for ETH 1.0 Chain
    
    Simple Summary:
    A transaction pricing mechanism that includes fixed-per-block network fee that is burned and dynamically expands/contracts block sizes to deal with transient congestion.
    
    Abstract:
    There is a base fee per gas in protocol, which can move up or down by a maximum of 1/8 in each block. The base fee per gas is burned. Transactions specify the maximum fee per gas they are willing to give to miners to incentivize them to include their transaction (aka: priority fee). Transactions also specify the maximum fee per gas they are willing to pay total (aka: max fee), which covers both the priority fee and the block's network fee per gas (aka: base fee).
    
    The algorithm results in a gas target of 15M gas, with a base fee that adjusts to market conditions and that gets burned instead of paid to the miner. Miners only receive the priority fee.
    
    Motivation:
    The current fee market for Ethereum is a first-price auction, where users submit transactions with bids ("gasprices") and miners choose transactions with the highest bids. This leads to inefficiencies:
    
    1. Needlessly high fees: users need to bid more than necessary to ensure their transactions are included
    2. Slow inclusion: users sometimes wait for many blocks to avoid overpaying
    3. Poor user experience: users need to manually adjust gasprices
    
    Technical Specification:
    At the beginning of a block, the protocol calculates a "base fee" per gas based on the size of the previous block. The base fee increases when the previous block is larger than the target size, and decreases when the previous block is smaller than the target size. The base fee is burned.
    
    Users submit transactions with a "max fee" per gas they are willing to pay, and a "priority fee" per gas they are willing to pay to miners. The transaction will be included if the max fee is greater than the sum of the base fee and the priority fee. The user is refunded the difference between the max fee and the sum of the base fee and priority fee.
    """
    
    # Example metadata
    example_metadata = {
        "title": "EIP-1559: Fee Market Change for ETH 1.0 Chain",
        "protocol": "Ethereum",
        "category": "Core",
        "author": "Vitalik Buterin"
    }
    
    # Generate arguments
    logger.info("Generating arguments...")
    # Access the original function from the decorated tool
    arguments = generate_proposal_arguments.func(example_proposal, example_metadata)
    
    # Print the arguments
    print("\nArguments For:")
    for arg in arguments["for_proposal"]:
        print(f"- {arg}")
    
    print("\nArguments Against:")
    for arg in arguments["against"]:
        print(f"- {arg}")
    
    # Print the full result
    logger.info("Printing full result...")
    print("\nFull Result:")
    print(json.dumps(arguments, indent=2))
    
    logger.info("Test complete.")

if __name__ == "__main__":
    main()
