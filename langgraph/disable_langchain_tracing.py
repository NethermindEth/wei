"""
Script to disable LangChain tracing and LangSmith integration, but keep Langfuse tracing enabled.
This script sets environment variables to disable various tracing mechanisms.
"""
import os

# Set environment variables to disable LangChain tracing
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""
os.environ["LANGCHAIN_PROJECT"] = ""

# Disable LangSmith tracing
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGSMITH_API_KEY"] = ""
os.environ["LANGSMITH_ENDPOINT"] = ""
os.environ["LANGSMITH_PROJECT"] = ""

# Note: Langfuse tracing is kept enabled
# Langfuse credentials should be set in the .env file

print("LangChain tracing and LangSmith integration have been disabled. Langfuse tracing remains enabled if credentials are provided.")
