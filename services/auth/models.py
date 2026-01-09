from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int


class UserMetadata(BaseModel):
    user_id: str = Field(..., description="Clerk user ID")
    email: Optional[str] = Field(None, description="Primary email address")
    username: Optional[str] = Field(None, description="Username")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")
    created_at: Optional[int] = Field(None, description="Account creation timestamp")
    updated_at: Optional[int] = Field(None, description="Last update timestamp")
    public_metadata: Optional[Dict[str, Any]] = Field(None, description="Public metadata")
    private_metadata: Optional[Dict[str, Any]] = Field(None, description="Private metadata")
    unsafe_metadata: Optional[Dict[str, Any]] = Field(None, description="Unsafe metadata")


class TokenVerificationResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    expires_at: Optional[int] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"

