"""
End-to-end tests for API endpoints.
"""

import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from tests.test_base import BaseTest


class TestApiEndpoints(BaseTest):
    """Test API endpoints without database access."""
    
    def test_test_endpoint(self, test_client: TestClient):
        """Test the test endpoint."""
        response = test_client.get(
            "/api/v1/test",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "API key is valid"}
    
    def test_invalid_api_key(self, test_client: TestClient):
        """Test with an invalid API key."""
        response = test_client.get(
            "/api/v1/test",
            headers={"X-API-Key": "invalid-key"}
        )
        
        # Check response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in response.json()["detail"]
    
    def test_missing_api_key(self, test_client: TestClient):
        """Test with a missing API key."""
        response = test_client.get(
            "/api/v1/test"
        )
        
        # Check response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in response.json()["detail"]
