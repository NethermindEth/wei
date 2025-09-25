#!/bin/bash

# Script to run tests with Langfuse tracing enabled
# This script sets the necessary environment variables and runs the tests

# Check if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
else
    echo "No .env file found, using environment variables from command line"
fi

# Check if Langfuse API keys are set
if [ -z "$LANGFUSE_PUBLIC_KEY" ] || [ -z "$LANGFUSE_SECRET_KEY" ]; then
    echo "Error: Langfuse API keys not set"
    echo "Please set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables"
    exit 1
fi

# Check if OpenRouter API key is set
if [ -z "$WEI_AGENT_OPEN_ROUTER_API_KEY" ]; then
    echo "Error: OpenRouter API key not set"
    echo "Please set WEI_AGENT_OPEN_ROUTER_API_KEY environment variable"
    exit 1
fi

# Print configuration
echo "=== Configuration ==="
echo "LANGFUSE_PUBLIC_KEY: ${LANGFUSE_PUBLIC_KEY:0:5}...${LANGFUSE_PUBLIC_KEY: -5}"
echo "LANGFUSE_SECRET_KEY: ${LANGFUSE_SECRET_KEY:0:5}...${LANGFUSE_SECRET_KEY: -5}"
echo "LANGFUSE_HOST: $LANGFUSE_HOST"
echo "WEI_AGENT_MODEL: $WEI_AGENT_MODEL"
echo "WEI_AGENT_ANALYZING_TEMPERATURE: $WEI_AGENT_ANALYZING_TEMPERATURE"
echo "WEI_AGENT_ANALYZING_MAX_TOKENS: $WEI_AGENT_ANALYZING_MAX_TOKENS"
echo "===================="

# Run the tests
echo "Running tests with Langfuse tracing enabled..."
python tests/test_deep_analyzer.py

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "Tests passed!"
    echo "Check Langfuse dashboard at $LANGFUSE_HOST to see the traces"
else
    echo "Tests failed!"
fi
