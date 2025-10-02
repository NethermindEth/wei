#!/usr/bin/env python
"""
Minimal server for testing.
"""

import os
import sys
import uvicorn
import dotenv
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
dotenv.load_dotenv()

# Get environment variables with defaults
PORT = int(os.getenv("PORT", "8005"))  # Use port 8005 by default
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()

# API settings
API_V1_STR = "/api/v1"
PROJECT_NAME = "Wei Agent API"

# CORS settings
cors_origins_str = os.getenv("BACKEND_CORS_ORIGINS", "*")
if cors_origins_str == "*":
    BACKEND_CORS_ORIGINS = ["*"]
else:
    BACKEND_CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

# Security settings
api_keys_str = os.getenv("API_KEYS", "")
API_KEYS = [key.strip() for key in api_keys_str.split(",") if key.strip()]
API_KEY_NAME = "X-API-Key"

# Create FastAPI app
app = FastAPI(
    title=PROJECT_NAME,
    openapi_url=f"{API_V1_STR}/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key header
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    """
    Validate API key from header against a list of valid API keys.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
        )
    
    # Check if the API key is in the list of valid keys
    if api_key not in API_KEYS:
        logger.warning(f"Invalid API key attempt: {api_key[:5]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    
    logger.debug(f"Valid API key used: {api_key[:5]}...")
    return api_key

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": f"{PROJECT_NAME} is running"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/info")
async def info():
    """Information endpoint."""
    return {
        "name": PROJECT_NAME,
        "version": "0.1.0",
        "api_version": "v1",
        "cors_origins": BACKEND_CORS_ORIGINS,
        "api_keys_count": len(API_KEYS),
    }

@app.get("/api/v1/test", dependencies=[Depends(get_api_key)])
async def test_api_key():
    """Test API key authentication."""
    return {"message": "API key is valid"}

if __name__ == "__main__":
    try:
        # Hard-code the port to 8005 to avoid any issues
        port = 8005
        logger.info(f"Starting minimal server on port {port} with log level {LOG_LEVEL}")
        
        # Run the server
        uvicorn.run(
            "minimal_server:app",
            host="0.0.0.0",
            port=port,
            log_level=LOG_LEVEL,
            reload=False,
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.critical(f"Server failed to start: {e}")
        sys.exit(1)
