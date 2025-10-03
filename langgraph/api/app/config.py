"""Configuration module for the application."""

# Standard library imports
import logging
import os
from typing import Optional, List, Any, Dict
from types import SimpleNamespace

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create settings dictionary
settings_dict = {
    # API settings
    "API_V1_STR": "",
    "PROJECT_NAME": "Wei Agent API",
    "PORT": int(os.getenv("PORT", "8002")),
    
    # Security settings
    "SECRET_KEY": os.getenv("SECRET_KEY", "changeme"),
    "API_KEY_NAME": "X-API-Key",
    "ACCESS_TOKEN_EXPIRE_MINUTES": 60 * 24 * 8,  # 8 days
    
    # Logging
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "info"),
    
    # Debug mode
    "DEBUG": os.getenv("DEBUG", "False").lower() in ("true", "1", "t"),
}

# CORS settings
cors_origins_str = os.getenv("BACKEND_CORS_ORIGINS", "*")
if cors_origins_str == "*":
    settings_dict["BACKEND_CORS_ORIGINS"] = ["*"]
else:
    settings_dict["BACKEND_CORS_ORIGINS"] = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

# API Keys
api_keys_str = os.getenv("API_KEYS", "")
settings_dict["API_KEYS"] = [key.strip() for key in api_keys_str.split(",") if key.strip()]

# Database settings
settings_dict["DATABASE_HOST"] = os.getenv("DATABASE_HOST", "localhost")
settings_dict["DATABASE_PORT"] = os.getenv("DATABASE_PORT", "5432")
settings_dict["DATABASE_USER"] = os.getenv("DATABASE_USER", "postgres")
settings_dict["DATABASE_PASSWORD"] = os.getenv("DATABASE_PASSWORD", "postgres")
settings_dict["DATABASE_NAME"] = os.getenv("DATABASE_NAME", "wei_agent")
settings_dict["DATABASE_URL"] = os.getenv("DATABASE_URL", "")

# If DATABASE_URL is not provided, construct it
if not settings_dict["DATABASE_URL"]:
    settings_dict["DATABASE_URL"] = f"postgresql+asyncpg://{settings_dict['DATABASE_USER']}:{settings_dict['DATABASE_PASSWORD']}@{settings_dict['DATABASE_HOST']}:{settings_dict['DATABASE_PORT']}/{settings_dict['DATABASE_NAME']}"

# Database pool settings
settings_dict["DB_POOL_SIZE"] = int(os.getenv("DB_POOL_SIZE", "5"))
settings_dict["DB_MAX_OVERFLOW"] = int(os.getenv("DB_MAX_OVERFLOW", "10"))
settings_dict["DB_POOL_TIMEOUT"] = int(os.getenv("DB_POOL_TIMEOUT", "30"))
settings_dict["DB_POOL_RECYCLE"] = int(os.getenv("DB_POOL_RECYCLE", "1800"))
settings_dict["DB_ECHO_LOG"] = os.getenv("DB_ECHO_LOG", "False").lower() in ("true", "1", "t")

# Model settings
settings_dict["WEI_AGENT_AI_MODEL_PROVIDER"] = os.getenv("WEI_AGENT_AI_MODEL_PROVIDER", "openai")
settings_dict["WEI_AGENT_AI_MODEL_NAME"] = os.getenv("WEI_AGENT_AI_MODEL_NAME", "gpt-4o-mini")
settings_dict["WEI_AGENT_ROADMAP_MODEL_NAME"] = os.getenv("WEI_AGENT_ROADMAP_MODEL_NAME", "perplexity/sonar-pro")
settings_dict["WEI_AGENT_OPEN_ROUTER_API_KEY"] = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
settings_dict["WEI_AGENT_EXA_API_KEY"] = os.getenv("WEI_AGENT_EXA_API_KEY")

# Model parameters
settings_dict["WEI_AGENT_ANALYZING_TEMPERATURE"] = float(os.getenv("WEI_AGENT_ANALYZING_TEMPERATURE", "0.2"))
settings_dict["WEI_AGENT_ANALYZING_MAX_TOKENS"] = int(os.getenv("WEI_AGENT_ANALYZING_MAX_TOKENS", "2000"))
settings_dict["WEI_AGENT_MAX_TOKENS"] = int(os.getenv("WEI_AGENT_MAX_TOKENS", "400"))

# Langfuse settings
settings_dict["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY")
settings_dict["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY")
settings_dict["LANGFUSE_HOST"] = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
settings_dict["LANGFUSE_PROJECT"] = os.getenv("LANGFUSE_PROJECT", "default")

# Create settings object
settings = SimpleNamespace(**settings_dict)

# Log loaded settings
logger.info(f"Loaded settings with CORS origins: {settings.BACKEND_CORS_ORIGINS}")
logger.info(f"Loaded settings with API keys count: {len(settings.API_KEYS)}")
logger.info(f"Database URL: {settings.DATABASE_URL}")

def get_postgres_system_url() -> str:
    """Get the PostgreSQL system URL for database creation."""
    # Extract the base URL without the database name
    parts = str(settings.DATABASE_URL).split("/")
    base_url = "/".join(parts[:-1])
    
    # Return the URL with the postgres database
    return f"{base_url}/postgres"
