# Deepagent-based Proposal Analysis with Modern Langfuse Tracing

## Overview
This PR implements a proposal analysis system using the deepagent package, with modern Langfuse tracing for observability. The implementation focuses on generating high-quality arguments for and against governance proposals, identifying tasks and blockers, and providing comprehensive evaluation reports.

## Key Components

### 1. Deep Proposal Analyzer:
- Main component that orchestrates the analysis process
- Generates evaluation reports with structured categories
- Identifies tasks, blockers, and next steps
- Produces balanced arguments for and against proposals

### 2. Deepagent Tools:
- Custom tools for proposal analysis, including argument generation
- Configurable model parameters via environment variables
- Robust error handling and fallback mechanisms

### 3. Modern Langfuse Tracing:
- Context managers with `start_as_current_span` and `start_as_current_generation`
- Decorator-based tracing with `@observe_function`
- Hierarchical spans for better trace visualization
- Detailed metadata for comprehensive observability

### 4. Testing:
- Comprehensive tests for the deep analyzer
- Specific tests for argument generation
- Test utilities for consistent evaluation

## Benefits
- **High-Quality Arguments**: Generates nuanced and balanced arguments for and against proposals
- **Structured Evaluation**: Provides comprehensive evaluation reports with clear categories
- **Robust Error Handling**: Includes fallback mechanisms for parsing and generation
- **Detailed Observability**: Comprehensive tracing for monitoring and debugging
- **Configurable**: Flexible configuration via environment variables

## Next Steps
- Add more specialized analysis tools
- Enhance argument generation with more context
- Expand test coverage for edge cases
