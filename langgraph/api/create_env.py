#!/usr/bin/env python
"""
Script to create a basic .env file for development.
"""

import os
import secrets

# Define the path to the .env file
env_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

# Define the content of the .env file
env_content = f"""# API SERVER CONFIGURATION
PORT=8000

# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=wei_agent

# API Authentication
API_KEYS=dev_key,test_key
SECRET_KEY={secrets.token_urlsafe(32)}

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:3000,*nethermind.io,*nethermind-org.vercel.app

# AI MODEL CONFIGURATION
WEI_AGENT_AI_MODEL_PROVIDER=openai
WEI_AGENT_AI_MODEL_NAME=gpt-4o-mini
WEI_AGENT_ROADMAP_MODEL_NAME=perplexity/sonar-pro

# Langfuse Configuration
LANGFUSE_PROJECT=default

# Logging
LOG_LEVEL=info
"""

# Write the content to the .env file
with open(env_file_path, "w") as f:
    f.write(env_content)

print(f"Created .env file at {env_file_path}")
print("You can now run the server with: python server.py")
print("Note: You'll need to add your API keys (WEI_AGENT_OPEN_ROUTER_API_KEY, etc.) to the .env file.")
