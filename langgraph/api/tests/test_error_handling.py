"""
End-to-end tests for error handling across all API routes.

These tests focus on verifying that the API handles errors gracefully
and returns appropriate error responses for various edge cases.
"""

import pytest
import uuid
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from tests.test_base import BaseTest


class TestErrorHandling(BaseTest):
    """Test error handling across all API routes."""
    
    @pytest.mark.e2e
    def test_invalid_proposal_content(self, test_client: TestClient):
        """Test handling of invalid proposal content."""
        # Create request with empty content
        request_data = {
            "content": "",
            "proposal_id": "test-empty-proposal"
        }
        
        # Send request for analysis
        response = test_client.post(
            "/api/v1/pre-filter",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # API should return an error for empty content
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.e2e
    def test_missing_required_fields(self, test_client: TestClient):
        """Test handling of missing required fields in requests."""
        # Create request missing the required content field
        request_data = {
            "proposal_id": "test-missing-content"
        }
        
        # Send request for analysis
        response = test_client.post(
            "/api/v1/pre-filter",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # API returns a bad request error for missing content
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.e2e
    def test_invalid_uuid_format(self, test_client: TestClient):
        """Test handling of invalid UUID format in path parameters."""
        # Send request with invalid UUID format
        response = test_client.get(
            "/api/v1/pre-filter/not-a-uuid",
            headers=self.get_auth_headers()
        )
        
        # Should return a validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.e2e
    def test_database_connection_error(self, test_client: TestClient):
        """Test handling of database connection errors."""
        # Mock the create_analysis function to raise an exception
        with patch('app.api.routes.create_analysis', side_effect=Exception("Database connection error")):
            # Send request for analysis
            response = test_client.post(
                "/api/v1/pre-filter",
                json=self.get_test_proposal(),
                headers=self.get_auth_headers()
            )
            
            # Should return a server error
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
    
    @pytest.mark.e2e
    def test_ai_model_error(self, test_client: TestClient):
        """Test handling of AI model errors."""
        # Mock the graph.ainvoke method to raise an exception
        with patch('app.api.routes.graph.ainvoke', side_effect=Exception("AI model error")):
            # Send request for analysis
            response = test_client.post(
                "/api/v1/pre-filter",
                json=self.get_test_proposal(),
                headers=self.get_auth_headers()
            )
            
            # Should return a server error
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "Failed to analyze proposal" in data["detail"]
    
    @pytest.mark.e2e
    def test_missing_analysis_result(self, test_client: TestClient):
        """Test handling of missing analysis result in AI response."""
        # Mock the graph.ainvoke method to return a response without analysis_result
        with patch('app.api.routes.graph.ainvoke', return_value={"some_other_key": "value"}):
            # Send request for analysis
            response = test_client.post(
                "/api/v1/pre-filter",
                json=self.get_test_proposal(),
                headers=self.get_auth_headers()
            )
            
            # Should return a server error
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "detail" in data
            assert "no analysis result returned" in data["detail"]
    
    @pytest.mark.e2e
    def test_invalid_custom_criteria_format(self, test_client: TestClient):
        """Test handling of invalid custom criteria format."""
        # Create request with invalid custom criteria format
        request_data = {
            "content": self.get_test_proposal()["content"],
            "custom_criteria": "This should be a dictionary, not a string"
        }
        
        # Send request for custom evaluation
        response = test_client.post(
            "/api/v1/pre-filter/custom",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # Should return a validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.e2e
    def test_very_large_proposal(self, test_client: TestClient):
        """Test handling of very large proposal content."""
        # Create request with very large content
        large_content = "A" * 100000  # 100KB of text
        request_data = {
            "content": large_content,
            "proposal_id": "test-large-proposal"
        }
        
        # Send request for analysis
        response = test_client.post(
            "/api/v1/pre-filter",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # API should either handle it or return an appropriate error
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, status.HTTP_500_INTERNAL_SERVER_ERROR]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "result" in data
