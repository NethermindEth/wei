"""
End-to-end tests for the API documentation.

These tests focus on verifying that the API documentation is correctly
generated and accessible.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
import json

from tests.test_base import BaseTest


class TestApiDocs(BaseTest):
    """Test API documentation."""
    
    @pytest.mark.e2e
    @pytest.mark.docs
    def test_openapi_schema(self, test_client: TestClient):
        """Test that the OpenAPI schema is accessible."""
        # Send request to get the OpenAPI schema
        response = test_client.get("/api/openapi.json")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the schema has the expected structure
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert "components" in data
        
        # Check that the API title is correct
        assert "title" in data["info"]
        assert "Wei Agent API" in data["info"]["title"]
        
        # Check that the API has the expected paths
        assert "/api/v1/pre-filter" in data["paths"]
        assert "/api/v1/pre-filter/arguments" in data["paths"]
        assert "/api/v1/pre-filter/custom" in data["paths"]
        assert "/api/v1/chat" in data["paths"]
    
    @pytest.mark.e2e
    @pytest.mark.docs
    def test_swagger_ui(self, test_client: TestClient):
        """Test that the Swagger UI is accessible."""
        # Send request to get the Swagger UI
        response = test_client.get("/api/docs")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        content = response.text
        
        # Check that the response contains Swagger UI elements
        assert "swagger-ui" in content.lower()
        assert "openapi.json" in content
    
    @pytest.mark.e2e
    @pytest.mark.docs
    def test_redoc(self, test_client: TestClient):
        """Test that the ReDoc UI is accessible."""
        # Send request to get the ReDoc UI
        response = test_client.get("/api/redoc")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        content = response.text
        
        # Check that the response contains ReDoc elements
        assert "redoc" in content.lower()
        assert "openapi.json" in content
    
    @pytest.mark.e2e
    @pytest.mark.docs
    def test_schema_models(self, test_client: TestClient):
        """Test that the schema includes all expected models."""
        # Send request to get the OpenAPI schema
        response = test_client.get("/api/openapi.json")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the schema includes all expected models
        schemas = data["components"]["schemas"]
        expected_models = [
            "AnalysisResponse",
            "ProposalRequest",
            "ArgumentsRequest",
            "ProposalArguments",
            "CustomEvaluationRequest",
            "CustomEvaluationResponse",
            "ChatRequest",
            "ChatResponse"
        ]
        
        for model in expected_models:
            assert model in schemas
            
        # Check that the ProposalArguments model has the expected properties
        proposal_args = schemas.get("ProposalArguments", {})
        assert "properties" in proposal_args
        assert "for_proposal" in proposal_args["properties"]
        assert "against" in proposal_args["properties"]
