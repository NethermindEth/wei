"""
End-to-end tests for authentication.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from tests.test_base import BaseTest


class TestAuthentication(BaseTest):
    """Test authentication functionality."""
    
    def test_valid_api_key(self, test_client: TestClient):
        """Test that a valid API key is accepted."""
        response = test_client.get(
            "/api/v1/test",
            headers=self.get_auth_headers()
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "API key is valid"}
    
    def test_invalid_api_key(self, test_client: TestClient):
        """Test that an invalid API key is rejected."""
        response = test_client.get(
            "/api/v1/test",
            headers={"X-API-Key": "invalid_key"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in response.json()["detail"]
    
    def test_missing_api_key(self, test_client: TestClient):
        """Test that a missing API key is rejected."""
        response = test_client.get("/api/v1/test")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid API key" in response.json()["detail"]
