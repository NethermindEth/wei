from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Clerk Configuration
    clerk_secret_key: str
    clerk_publishable_key: str

    # Server Configuration
    port: int = 8000
    host: str = "0.0.0.0"
    log_level: str = "info"

    # Service Authorization
    allowed_service_keys: str

    # CORS Configuration
    allowed_origins: str = "http://localhost:3000"

    @property
    def service_keys_list(self) -> List[str]:
        return [key.strip() for key in self.allowed_service_keys.split(",")]

    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


def get_settings() -> Settings:
    return Settings()

