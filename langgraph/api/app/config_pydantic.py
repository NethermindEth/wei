"""
Configuration module using Pydantic BaseSettings.
"""

# Standard library imports
import logging
from typing import List, Optional

# Third-party imports
from pydantic import BaseSettings, Field, PostgresDsn, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API settings
    api_v1_str: str = "/api/v1"
    project_name: str = "Wei Agent API"
    port: int = Field(8002, env="PORT")
    
    # CORS settings
    backend_cors_origins: List[str] = Field(["*"], env="BACKEND_CORS_ORIGINS")
    
    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and v != "":
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return ["*"]
    
    # Security settings
    secret_key: str = Field("changeme", env="SECRET_KEY")
    api_keys: List[str] = Field([], env="API_KEYS")
    api_key_name: str = "X-API-Key"
    access_token_expire_minutes: int = 60 * 24 * 8  # 8 days
    
    @validator("api_keys", pre=True)
    def assemble_api_keys(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and v != "":
            return [key.strip() for key in v.split(",") if key.strip()]
        return []
    
    # Database settings
    database_host: str = Field("localhost", env="DATABASE_HOST")
    database_port: str = Field("5432", env="DATABASE_PORT")
    database_user: str = Field("postgres", env="DATABASE_USER")
    database_password: str = Field("postgres", env="DATABASE_PASSWORD")
    database_name: str = Field("wei_agent", env="DATABASE_NAME")
    database_url: Optional[PostgresDsn] = Field(None, env="DATABASE_URL")
    
    @validator("database_url", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if v:
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("database_user"),
            password=values.get("database_password"),
            host=values.get("database_host"),
            port=values.get("database_port"),
            path=f"/{values.get('database_name')}",
        )
    
    # Database pool settings
    db_pool_size: int = Field(5, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(10, env="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(30, env="DB_POOL_TIMEOUT")
    db_pool_recycle: int = Field(1800, env="DB_POOL_RECYCLE")
    db_echo_log: bool = Field(False, env="DB_ECHO_LOG")
    
    # Model settings
    wei_agent_ai_model_provider: str = Field("openai", env="WEI_AGENT_AI_MODEL_PROVIDER")
    wei_agent_ai_model_name: str = Field("gpt-4o-mini", env="WEI_AGENT_AI_MODEL_NAME")
    wei_agent_roadmap_model_name: str = Field("perplexity/sonar-pro", env="WEI_AGENT_ROADMAP_MODEL_NAME")
    wei_agent_open_router_api_key: Optional[str] = Field(None, env="WEI_AGENT_OPEN_ROUTER_API_KEY")
    wei_agent_exa_api_key: Optional[str] = Field(None, env="WEI_AGENT_EXA_API_KEY")
    
    # Model parameters
    wei_agent_analyzing_temperature: float = Field(0.2, env="WEI_AGENT_ANALYZING_TEMPERATURE")
    wei_agent_analyzing_max_tokens: int = Field(2000, env="WEI_AGENT_ANALYZING_MAX_TOKENS")
    wei_agent_max_tokens: int = Field(400, env="WEI_AGENT_MAX_TOKENS")
    
    # Langfuse settings
    langfuse_public_key: Optional[str] = Field(None, env="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: Optional[str] = Field(None, env="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field("https://cloud.langfuse.com", env="LANGFUSE_HOST")
    langfuse_project: str = Field("default", env="LANGFUSE_PROJECT")
    
    # Logging
    log_level: str = Field("info", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Log loaded settings
logger.info(f"Loaded settings with CORS origins: {settings.backend_cors_origins}")
logger.info(f"Loaded settings with API keys count: {len(settings.api_keys)}")
logger.info(f"Database URL: {settings.database_url}")


def get_postgres_system_url() -> str:
    """Get the PostgreSQL system URL for database creation."""
    # Extract the base URL without the database name
    parts = str(settings.database_url).split("/")
    base_url = "/".join(parts[:-1])
    
    # Return the URL with the postgres database
    return f"{base_url}/postgres"
