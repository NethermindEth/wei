"""Middleware for the FastAPI application."""

# Standard library imports
import time
import uuid
import logging
from typing import Callable, Dict, Any

# Third-party imports
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Local application imports
from app.tracing import trace_span, get_langfuse_client

# Configure logging
logger = logging.getLogger(__name__)


class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware for tracing HTTP requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and trace it.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next middleware or route handler
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Extract path and method for tracing
        path = request.url.path
        method = request.method
        
        # Create trace metadata
        metadata = {
            "request_id": request_id,
            "path": path,
            "method": method,
            "query_params": str(request.query_params),
        }
        
        # Create trace tags
        tags = [f"method:{method}", f"path:{path}"]
        
        # Process the request with tracing
        with trace_span(f"http_request_{method}", metadata=metadata, tags=tags) as span:
            try:
                # Process the request
                response = await call_next(request)
                
                # Update span with response information
                if span:
                    span.update(
                        status="success",
                        metadata={
                            **metadata,
                            "status_code": response.status_code,
                            "duration_ms": round((time.time() - start_time) * 1000),
                        }
                    )
                
                # Add tracing headers to response
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Response-Time"] = str(round((time.time() - start_time) * 1000))
                
                return response
            except Exception as e:
                # Update span with error information
                if span:
                    span.update(
                        status="error",
                        metadata={
                            **metadata,
                            "error": str(e),
                            "duration_ms": round((time.time() - start_time) * 1000),
                        }
                    )
                raise


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request information and performance metrics.
    
    This middleware logs information about each request, including:
    - HTTP method
    - URL path
    - Client IP
    - Status code
    - Response time
    - User agent
    """
    
    def __init__(self, app: ASGIApp):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log information.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next middleware or route handler
        """
        # Record start time
        start_time = time.time()
        
        # Get request information
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = (time.time() - start_time) * 1000
            
            # Log request information
            logger.info(
                f"Request: {method} {path} | "
                f"Client: {client_ip} | "
                f"Status: {response.status_code} | "
                f"Time: {process_time:.2f}ms | "
                f"User-Agent: {user_agent}"
            )
            
            # Add custom headers for debugging
            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
            
            return response
        except Exception as e:
            # Log error
            logger.error(f"Error processing request {method} {path}: {str(e)}")
            raise


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests.
    
    This middleware limits the number of requests that can be made by a client
    within a specified time window.
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        limit: int = 100, 
        window: int = 60, 
        exclude_paths: list = None
    ):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
            limit: Maximum number of requests allowed per window
            window: Time window in seconds
            exclude_paths: List of paths to exclude from rate limiting
        """
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.exclude_paths = exclude_paths or []
        self.clients: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and apply rate limiting.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next middleware or route handler
        """
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get current time
        current_time = time.time()
        
        # Initialize client data if not exists
        if client_ip not in self.clients:
            self.clients[client_ip] = {
                "count": 0,
                "window_start": current_time
            }
        
        # Reset count if window has passed
        if current_time - self.clients[client_ip]["window_start"] > self.window:
            self.clients[client_ip] = {
                "count": 0,
                "window_start": current_time
            }
        
        # Increment request count
        self.clients[client_ip]["count"] += 1
        
        # Check if rate limit exceeded
        if self.clients[client_ip]["count"] > self.limit:
            # Return 429 Too Many Requests
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Process the request
        return await call_next(request)


def add_middleware(app: FastAPI) -> None:
    """
    Add middleware to the FastAPI application.
    
    Args:
        app: The FastAPI application
    """
    # Add tracing middleware
    app.add_middleware(TracingMiddleware)
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add rate limiting middleware
    app.add_middleware(
        RateLimitingMiddleware,
        limit=100,
        window=60,
        exclude_paths=["/api/docs", "/api/redoc", "/api/openapi.json"]
    )
