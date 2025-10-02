from fastapi import FastAPI, Depends, Header, HTTPException, status, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from typing import Optional
import logging
from datetime import datetime
import uvicorn

from config import get_settings, Settings
from auth import ClerkAuthService
from middleware import ServiceAuthMiddleware, verify_service_auth
from models import (
    UserMetadata,
    TokenVerificationResponse,
    HealthResponse,
    ErrorResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Security schemes for Swagger UI
bearer_scheme = HTTPBearer(
    scheme_name="Bearer Token",
    description="Enter your Clerk JWT token"
)
service_key_scheme = APIKeyHeader(
    name="X-Service-Key",
    scheme_name="Service Key",
    description="Enter your service API key"
)

# Initialize FastAPI app
app = FastAPI(
    title="Wei Auth Service",
    description="Authentication service for Wei using Clerk",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get settings
settings = get_settings()

# Initialize services
auth_service = ClerkAuthService(settings)
service_auth = ServiceAuthMiddleware(settings)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint (no auth required)
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"]
)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat()
    )


# Verify JWT token
@app.post(
    "/verify-token",
    response_model=TokenVerificationResponse,
    tags=["Authentication"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"}
    }
)
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    service_key: str = Security(service_key_scheme)
):
    """
    Verify a Clerk JWT token.

    Click the "Authorize" button (🔒) above to add your credentials:
    - Bearer Token: Your Clerk JWT token (without 'Bearer ' prefix)
    - X-Service-Key: Your service API key
    """
    # Verify service authentication
    if service_key not in settings.service_keys_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service key"
        )

    # Token is already extracted by HTTPBearer
    token = credentials.credentials
    return await auth_service.verify_token(token)


# Get current user metadata from JWT
# NOTE: This route MUST come before /users/{user_id} to avoid "me" being treated as a user_id
@app.get(
    "/users/me",
    response_model=UserMetadata,
    tags=["Users"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    service_key: str = Security(service_key_scheme)
):
    """
    Get current user metadata from JWT token.

    Click the "Authorize" button (🔒) above to add your credentials:
    - Bearer Token: Your Clerk JWT token (without 'Bearer ' prefix)
    - X-Service-Key: Your service API key
    """
    # Verify service authentication
    if service_key not in settings.service_keys_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service key"
        )

    # Token is already extracted by HTTPBearer
    token = credentials.credentials
    return await auth_service.get_current_user_metadata(token)


# Get user metadata by user ID
@app.get(
    "/users/{user_id}",
    response_model=UserMetadata,
    tags=["Users"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "User not found"}
    }
)
async def get_user(
    user_id: str,
    service_key: str = Security(service_key_scheme)
):
    """
    Get user metadata by Clerk user ID.

    Click the "Authorize" button (🔒) above to add your service API key.
    """
    # Verify service authentication
    if service_key not in settings.service_keys_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service key"
        )
    
    return await auth_service.get_user_metadata(user_id)


# Batch get users
@app.post(
    "/users/batch",
    response_model=list[UserMetadata],
    tags=["Users"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"}
    }
)
async def get_users_batch(
    user_ids: list[str],
    service_key: str = Security(service_key_scheme)
):
    """
    Get metadata for multiple users by their Clerk user IDs.

    Click the "Authorize" button (🔒) above to add your service API key.
    """
    # Verify service authentication
    if service_key not in settings.service_keys_list:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service key"
        )

    results = []
    for user_id in user_ids:
        try:
            user_metadata = await auth_service.get_user_metadata(user_id)
            results.append(user_metadata)
        except HTTPException as e:
            logger.warning(f"Failed to fetch user {user_id}: {e.detail}")
            continue
    
    return results


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=True
    )

