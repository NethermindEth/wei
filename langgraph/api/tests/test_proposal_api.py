"""
Tests for proposal analysis API endpoints.
"""

import uuid
import pytest
from unittest.mock import patch
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient

from tests.test_base import BaseTest


class TestProposalApi(BaseTest):
    """Test proposal analysis API endpoints."""
    
    def test_api_key_validation(self, test_client: TestClient):
        """Test API key validation."""
        # Create a test proposal
        test_proposal = self.get_test_proposal()
        
        # Test with valid API key
        response = test_client.post(
            "/api/v1/pre-filter",
            json=test_proposal,
            headers=self.get_auth_headers()
        )
        assert response.status_code != status.HTTP_401_UNAUTHORIZED
        
        # Test with invalid API key
        response = test_client.post(
            "/api/v1/pre-filter",
            json=test_proposal,
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test with missing API key
        response = test_client.post(
            "/api/v1/pre-filter",
            json=test_proposal
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_proposal_validation(self, test_client: TestClient):
        """Test proposal validation."""
        # Test with invalid JSON format
        response = test_client.post(
            "/api/v1/pre-filter",
            data="This is not valid JSON",
            headers=self.get_auth_headers()
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_health_endpoint(self, test_client: TestClient):
        """Test the health endpoint."""
        response = test_client.get("/health")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        
    def test_info_endpoint(self, test_client: TestClient):
        """Test the info endpoint."""
        response = test_client.get("/info")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "environment" in data
    
    def test_api_docs_endpoints(self, test_client: TestClient):
        """Test API documentation endpoints."""
        # Test OpenAPI schema endpoint
        response = test_client.get("/api/v1/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        schema = response.json()
        assert "paths" in schema
        assert "/api/v1/pre-filter" in schema["paths"]
        
        # Test Swagger UI endpoint
        response = test_client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        assert "swagger" in response.text.lower()
        
        # Test ReDoc endpoint
        response = test_client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
        assert "redoc" in response.text.lower()
