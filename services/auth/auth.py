from typing import Optional
from clerk_backend_api import Clerk, AuthenticateRequestOptions
from fastapi import HTTPException, status
import httpx
import logging

from config import Settings
from models import UserMetadata, TokenVerificationResponse

logger = logging.getLogger(__name__)


class ClerkAuthService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.clerk = Clerk(bearer_auth=settings.clerk_secret_key)

    async def verify_token(self, token: str) -> TokenVerificationResponse:
        """Verify Clerk JWT token using the Clerk SDK's authenticate_request method"""
        try:
            # Create a mock httpx.Request with the Authorization header
            # The SDK's authenticate_request method expects an httpx.Request object
            request = httpx.Request(
                method="GET",
                url="http://localhost",  # URL doesn't matter for token verification
                headers={"Authorization": f"Bearer {token}"}
            )

            # Use the SDK's built-in token verification
            request_state = self.clerk.authenticate_request(
                request,
                AuthenticateRequestOptions()
            )

            if not request_state.is_signed_in:
                # Token verification failed
                error_message = request_state.reason or "Token verification failed"
                logger.warning(f"Token verification failed: {error_message}")
                return TokenVerificationResponse(
                    valid=False,
                    error=error_message
                )

            # Token is valid, extract claims from the decoded payload
            payload = request_state.payload

            return TokenVerificationResponse(
                valid=True,
                user_id=payload.get("sub") if payload else None,
                session_id=payload.get("sid") if payload else None,
                expires_at=payload.get("exp") if payload else None
            )

        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return TokenVerificationResponse(
                valid=False,
                error=f"Token verification error: {str(e)}"
            )

    async def get_user_metadata(self, user_id: str) -> UserMetadata:
        """Retrieve user metadata from Clerk using the SDK"""
        try:
            user = self.clerk.users.get(user_id=user_id)

            # Extract primary email address
            email = None
            if user.email_addresses:
                primary_email = next(
                    (e for e in user.email_addresses if e.id == user.primary_email_address_id),
                    None
                )
                if primary_email:
                    email = primary_email.email_address
                elif user.email_addresses:
                    email = user.email_addresses[0].email_address

            return UserMetadata(
                user_id=user.id,
                email=email,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                profile_image_url=user.profile_image_url,
                created_at=user.created_at,
                updated_at=user.updated_at,
                public_metadata=user.public_metadata,
                private_metadata=user.private_metadata,
                unsafe_metadata=user.unsafe_metadata
            )

        except Exception as e:
            logger.error(f"Failed to fetch user metadata for {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {str(e)}"
            )

    async def get_current_user_metadata(self, token: str) -> UserMetadata:
        """Get user metadata for the user associated with the provided JWT token"""
        verification_result = await self.verify_token(token)

        if not verification_result.valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=verification_result.error or "Invalid token"
            )

        if not verification_result.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain user_id"
            )

        return await self.get_user_metadata(verification_result.user_id)
