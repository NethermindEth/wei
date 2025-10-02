"""
Configuration module for the application.
"""

import os
import logging
from typing import Optional, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# API settings
API_V1_STR = "/api/v1"
PROJECT_NAME = "Wei Agent API"
PORT = int(os.getenv("PORT", "8002"))

# CORS settings
cors_origins_str = os.getenv("BACKEND_CORS_ORIGINS", "*")
if cors_origins_str == "*":
    BACKEND_CORS_ORIGINS = ["*"]
else:
    BACKEND_CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
api_keys_str = os.getenv("API_KEYS", "")
API_KEYS = [key.strip() for key in api_keys_str.split(",") if key.strip()]
API_KEY_NAME = "X-API-Key"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 8 days

# Database settings
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")
DATABASE_NAME = os.getenv("DATABASE_NAME", "wei_agent")
DATABASE_URL = os.getenv("DATABASE_URL", "")

# If DATABASE_URL is not provided, construct it
if not DATABASE_URL:
    DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Database pool settings
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))
DB_ECHO_LOG = os.getenv("DB_ECHO_LOG", "False").lower() in ("true", "1", "t")

# Model settings
WEI_AGENT_AI_MODEL_PROVIDER = os.getenv("WEI_AGENT_AI_MODEL_PROVIDER", "openai")
WEI_AGENT_AI_MODEL_NAME = os.getenv("WEI_AGENT_AI_MODEL_NAME", "gpt-4o-mini")
WEI_AGENT_ROADMAP_MODEL_NAME = os.getenv("WEI_AGENT_ROADMAP_MODEL_NAME", "perplexity/sonar-pro")
WEI_AGENT_OPEN_ROUTER_API_KEY = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
WEI_AGENT_EXA_API_KEY = os.getenv("WEI_AGENT_EXA_API_KEY")

# Model parameters
WEI_AGENT_ANALYZING_TEMPERATURE = float(os.getenv("WEI_AGENT_ANALYZING_TEMPERATURE", "0.2"))
WEI_AGENT_ANALYZING_MAX_TOKENS = int(os.getenv("WEI_AGENT_ANALYZING_MAX_TOKENS", "2000"))
WEI_AGENT_MAX_TOKENS = int(os.getenv("WEI_AGENT_MAX_TOKENS", "400"))

# Langfuse settings
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
LANGFUSE_PROJECT = os.getenv("LANGFUSE_PROJECT", "default")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# Log loaded settings
logger.info(f"Loaded settings with CORS origins: {BACKEND_CORS_ORIGINS}")
logger.info(f"Loaded settings with API keys count: {len(API_KEYS)}")
logger.info(f"Database URL: {DATABASE_URL}")

def get_postgres_system_url() -> str:
    """Get the PostgreSQL system URL for database creation."""
    # Extract the base URL without the database name
    parts = DATABASE_URL.split("/")
    base_url = "/".join(parts[:-1])
    
    # Return the URL with the postgres database
    return f"{base_url}/postgres"
