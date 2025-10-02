"""
Middleware for the FastAPI application.
"""

# Standard library imports
import time
import uuid
from typing import Callable

# Third-party imports
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Local application imports
from app.tracing import trace_span, get_langfuse_client


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
