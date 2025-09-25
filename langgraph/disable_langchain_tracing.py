"""
Script to disable LangChain tracing and LangSmith integration, but keep Langfuse tracing enabled.
This script sets environment variables to disable various tracing mechanisms.
"""
import os
from typing import Dict, List

# Constants for LangChain environment variables
LANGCHAIN_ENV_VARS = {
    "LANGCHAIN_TRACING_V2": "false",
    "LANGCHAIN_ENDPOINT": "",
    "LANGCHAIN_API_KEY": "",
    "LANGCHAIN_PROJECT": ""
}

# Constants for LangSmith environment variables
LANGSMITH_ENV_VARS = {
    "LANGSMITH_TRACING": "false",
    "LANGSMITH_API_KEY": "",
    "LANGSMITH_ENDPOINT": "",
    "LANGSMITH_PROJECT": ""
}


def disable_tracing_systems(env_vars_dict: Dict[str, str]) -> None:
    """Disable a tracing system by setting its environment variables.
    
    Args:
        env_vars_dict: Dictionary of environment variables to set
    """
    for key, value in env_vars_dict.items():
        os.environ[key] = value


# Disable LangChain tracing
disable_tracing_systems(LANGCHAIN_ENV_VARS)

# Disable LangSmith tracing
disable_tracing_systems(LANGSMITH_ENV_VARS)

# Note: Langfuse tracing is kept enabled
# Langfuse credentials should be set in the .env file

print("LangChain tracing and LangSmith integration have been disabled.")
print("Langfuse tracing remains enabled if credentials are provided in the .env file.")

