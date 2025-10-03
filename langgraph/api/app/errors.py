"""
Error handling utilities for the application.
"""

from typing import Dict, Any, Optional, Type, Union
from fastapi import HTTPException, status
import logging

# Configure logging
logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base exception class for application errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class NotFoundError(AppError):
    """Exception raised when a resource is not found."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class AuthenticationError(AppError):
    """Exception raised for authentication errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(AppError):
    """Exception raised for authorization errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class ServiceError(AppError):
    """Exception raised for service-level errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ExternalServiceError(AppError):
    """Exception raised for errors in external services."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


class DatabaseError(AppError):
    """Exception raised for database errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


def handle_exception(
    exception: Exception, 
    operation: str, 
    error_message: Optional[str] = None
) -> None:
    """
    Handle exceptions by logging and raising appropriate HTTP exceptions.
    
    Args:
        exception: The exception to handle
        operation: The operation that was being performed
        error_message: Optional custom error message
    
    Raises:
        HTTPException: Appropriate HTTP exception based on the error type
    """
    # Log the exception
    logger.error(f"Error during {operation}: {str(exception)}")
    
    # Use provided error message or generate one
    message = error_message or f"Error during {operation}: {str(exception)}"
    
    # Handle application-specific errors
    if isinstance(exception, AppError):
        raise HTTPException(
            status_code=exception.status_code,
            detail=exception.message
        )
    
    # Handle other known exceptions
    if isinstance(exception, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Default to internal server error
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=message
    )


def format_response(
    data: Any = None, 
    message: str = "Success", 
    status_code: int = 200
) -> Dict[str, Any]:
    """
    Format a consistent API response.
    
    Args:
        data: The data to include in the response
        message: A message describing the response
        status_code: The HTTP status code
    
    Returns:
        A dictionary with status, message, data, and status_code
    """
    return {
        "status": "success" if status_code < 400 else "error",
        "message": message,
        "data": data,
        "status_code": status_code
    }
