# Wei Proposal Analyzer with DeepAgents

This directory contains a refactored implementation of the Wei Proposal Analyzer using the [deepagents](https://github.com/langchain-ai/deepagents) package from LangChain AI.

## Overview

The original implementation used a custom LangGraph-based workflow for proposal analysis. This refactored version leverages the deepagents package, which provides a more powerful and flexible framework for building complex agent systems.

Key improvements:
- More sophisticated planning capabilities
- Better context management
- Built-in file system for persistent state
- Specialized subagents for different aspects of analysis
- Improved error handling and fallback mechanisms

## Files

### DeepAgents Implementation
- `deep_proposal_analyzer.py`: Main implementation using deepagents
- `deepagent_tools.py`: Tools adapted from the original implementation for use with deepagents
- `deepagent_subagents.py`: Custom subagents for specialized tasks
- `deep_adapter.py`: Adapter for backward compatibility with the original API
- `test_deep_analyzer.py`: Test script for the deepagents implementation
- `test_argument_generation.py`: Test script for the argument generation tool

### Simple Implementation (Fallback)
- `simple_proposal_analyzer.py`: Simplified implementation that doesn't rely on external APIs
- `simple_adapter.py`: Adapter for the simple implementation
- `test_simple_analyzer.py`: Test script for the simple implementation

## Usage

The new implementation can be used in the same way as the original:

```python
from deep_adapter import analyze_proposal

# Example proposal text
example_proposal = """
EIP-1559: Fee Market Change for ETH 1.0 Chain

Simple Summary:
A transaction pricing mechanism that includes fixed-per-block network fee that is burned and dynamically expands/contracts block sizes to deal with transient congestion.
"""

# Example metadata
example_metadata = {
    "title": "EIP-1559: Fee Market Change for ETH 1.0 Chain",
    "protocol": "Ethereum",
    "category": "Core",
    "author": "Vitalik Buterin",
    "date_submitted": "2019-04-13",
    "id": "EIP-1559",
    "url": "https://eips.ethereum.org/EIPS/eip-1559"
}

# Analyze the example proposal
result = analyze_proposal(example_proposal, example_metadata)
```

## Dependencies

The refactored implementation requires the following dependencies:

```
langgraph>=0.0.8
langchain>=0.0.335
langchain-openai>=0.0.2
langchain-community>=0.0.13
langchain-chroma>=0.0.1
networkx>=3.1
python-dotenv>=1.0.0
chromadb>=0.4.18
openai>=1.3.0
requests>=2.31.0
numpy>=1.24.0
pandas>=2.0.0
langfuse>=2.0.0
deepagents>=0.0.1
```

## Configuration

Configuration is managed through environment variables:

- `WEI_AGENT_OPEN_ROUTER_API_KEY`: API key for OpenRouter service
- `WEI_AGENT_EXA_API_KEY`: API key for Exa service
- `WEI_AGENT_MODEL`: Default language model to use (default: "anthropic/claude-3-opus-20240229")
- `WEI_AGENT_TEMPERATURE`: Temperature setting for the model (default: 0.2)

## Architecture

The refactored implementation uses the following components:

1. **Deep Agent**: The main agent that coordinates the analysis process
2. **Tools**: Specialized functions for searching, indexing, and analyzing information
3. **Subagents**: Specialized agents for different aspects of the analysis:
   - Research Subagent: Gathers information about proposals
   - Analysis Subagent: Analyzes claims and evidence
   - Argument Subagent: Generates balanced arguments
   - Strategy Subagent: Develops strategic recommendations

## Benefits of DeepAgents

The deepagents package provides several benefits over the custom LangGraph implementation:

1. **Planning Tool**: Built-in planning capabilities to break down complex tasks
2. **Persistent State**: Memory between tool calls beyond conversation history
3. **Sub-agents**: Specialized agents for specific tasks with context quarantine
4. **Virtual File System**: Mock file system for persistent state without conflicts
5. **Detailed System Prompt**: Leverages proven patterns for effective agent behavior

## Backward Compatibility

The `deep_adapter.py` module ensures backward compatibility with code that uses the original implementation. It provides the same API but uses the deepagents-based implementation internally.

## Fallback Mechanism

The implementation includes a fallback mechanism to handle cases where the deepagents implementation cannot be used (e.g., due to API limitations or credit restrictions):

1. **Simple Implementation**: The `simple_proposal_analyzer.py` module provides a simplified implementation that doesn't rely on external APIs. It uses pattern matching and heuristics to extract information from the proposal text and generate arguments.

2. **Automatic Fallback**: If the deepagents implementation encounters an error (e.g., API credit limitations), it will automatically fall back to generating arguments directly using the `generate_proposal_arguments` function.

3. **Manual Fallback**: You can also manually use the simple implementation by importing from `simple_adapter` instead of `deep_adapter`:

```python
# Use the simple implementation directly
from simple_adapter import analyze_proposal

# Analyze the example proposal
result = analyze_proposal(example_proposal, example_metadata)
```

The simple implementation provides the same output structure as the deepagents implementation, ensuring consistent behavior regardless of which implementation is used.
