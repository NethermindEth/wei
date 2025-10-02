from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from config import Settings

logger = logging.getLogger(__name__)

security = HTTPBearer()


class ServiceAuthMiddleware:
    """Middleware to verify service-to-service authentication"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.allowed_keys = set(settings.service_keys_list)

    def verify_service_key(self, api_key: str) -> bool:
        """Verify if the provided API key is allowed"""
        return api_key in self.allowed_keys

    async def __call__(self, request: Request):
        """Validate service API key from request headers"""
        service_key = request.headers.get("X-Service-Key")

        if not service_key:
            logger.warning(f"Missing service key in request from {request.client.host}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Service key is required"
            )

        if not self.verify_service_key(service_key):
            logger.warning(f"Invalid service key attempted from {request.client.host}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid service key"
            )

        logger.debug(f"Service authenticated successfully from {request.client.host}")


def verify_service_auth(service_key: Optional[str] = None, settings: Settings = None) -> bool:
    """Dependency function to verify service authentication"""
    if not service_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Service key is required"
        )

    if settings and service_key not in settings.service_keys_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service key"
        )

    return True

