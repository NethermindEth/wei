"""
End-to-end tests for the integration between proposal analysis and arguments.

These tests focus on verifying that the arguments feature works correctly
when integrated with the proposal analysis endpoints.
"""

import pytest
import uuid
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from tests.test_base import BaseTest


class TestArgumentsIntegration(BaseTest):
    """Test integration between proposal analysis and arguments."""
    
    @pytest.mark.e2e
    @pytest.mark.arguments
    def test_arguments_in_analysis_response(self, test_client: TestClient):
        """
        Test that the analysis response can include arguments when available.
        
        This test verifies that the AnalysisResponse can include the optional
        arguments field of type ProposalArguments as described in the memory.
        """
        from app.services.langgraph.graph import graph
        
        # Mock the graph.ainvoke method to return analysis with arguments
        async def mock_invoke(input_data, runtime=None):
            if input_data.get("task") == "analyze_proposal":
                return {
                    "analysis_result": {
                        "result": "pass",
                        "confidence": 0.85,
                        "details": "This is a good proposal."
                    },
                    "arguments": {
                        "for_proposal": [
                            "Increases developer engagement",
                            "Promotes innovation in the ecosystem"
                        ],
                        "against": [
                            "Reduces treasury reserves",
                            "May not have sufficient oversight"
                        ]
                    }
                }
            return {}
            
        # Create a mock analysis object with arguments field
        mock_analysis = MagicMock()
        mock_analysis.id = uuid.uuid4()
        mock_analysis.proposal_id = self.get_test_proposal().get('proposal_id', 'test-proposal-1')
        mock_analysis.result = "pass"
        mock_analysis.confidence = 0.85
        mock_analysis.details = "This is a good proposal."
        mock_analysis.created_at = datetime.now()
        mock_analysis.updated_at = datetime.now()
        mock_analysis.arguments = {
            "for_proposal": [
                "Increases developer engagement",
                "Promotes innovation in the ecosystem"
            ],
            "against": [
                "Reduces treasury reserves",
                "May not have sufficient oversight"
            ]
        }
        
        # Mock the create_analysis function
        async def mock_create_analysis(*args, **kwargs):
            return mock_analysis
        
        # Apply the mocks
        with patch('app.api.routes.graph.ainvoke', AsyncMock(side_effect=mock_invoke)), \
             patch('app.api.routes.create_analysis', AsyncMock(side_effect=mock_create_analysis)):
                
            # No need for mock_session anymore since we're mocking create_analysis directly
            
            # Send a proposal for analysis
            response = test_client.post(
                "/api/v1/pre-filter",
                json=self.get_test_proposal(),
                headers=self.get_auth_headers()
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify that the response includes arguments
            assert "arguments" in data
            assert "for_proposal" in data["arguments"]
            assert "against" in data["arguments"]
            assert len(data["arguments"]["for_proposal"]) == 2
            assert len(data["arguments"]["against"]) == 2
    
    @pytest.mark.e2e
    @pytest.mark.arguments
    def test_arguments_fallback_messages(self, test_client: TestClient):
        """
        Test that fallback messages are provided when no arguments are available.
        """
        from app.services.langgraph.graph import graph
        
        # Mock the graph.ainvoke method to return empty arguments
        async def mock_invoke(input_data, runtime=None):
            if input_data.get("task") == "generate_arguments":
                return {
                    "arguments": {
                        "for_proposal": [],
                        "against": []
                    }
                }
            return {}
        
        # Apply the mock
        with patch('app.api.routes.graph.ainvoke', AsyncMock(side_effect=mock_invoke)):
            # Create request data
            request_data = {
                "content": self.get_test_proposal()["content"],
                "proposal_id": "test-proposal-fallback",
                "max_arguments": 3
            }
            
            # Send request to generate arguments
            response = test_client.post(
                "/api/v1/pre-filter/arguments",
                json=request_data,
                headers=self.get_auth_headers()
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify that fallback messages are provided
            assert len(data["for_proposal"]) == 1
            assert len(data["against"]) == 1
            assert data["for_proposal"][0] == "No supporting arguments were generated."
            assert data["against"][0] == "No opposing arguments were generated."
    
    @pytest.mark.e2e
    @pytest.mark.arguments
    def test_arguments_with_malformed_response(self, test_client: TestClient):
        """
        Test that the API handles malformed responses gracefully.
        """
        from app.services.langgraph.graph import graph
        
        # Mock the graph.ainvoke method to return malformed arguments
        async def mock_invoke(input_data, runtime=None):
            if input_data.get("task") == "generate_arguments":
                return {
                    "arguments": "This is not valid JSON but a string instead"
                }
            return {}
        
        # Apply the mock
        with patch('app.api.routes.graph.ainvoke', AsyncMock(side_effect=mock_invoke)):
            # Create request data
            request_data = {
                "content": self.get_test_proposal()["content"],
                "proposal_id": "test-proposal-malformed",
                "max_arguments": 3
            }
            
            # Send request to generate arguments
            response = test_client.post(
                "/api/v1/pre-filter/arguments",
                json=request_data,
                headers=self.get_auth_headers()
            )
            
            # Check response - should still work with fallback messages
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify that fallback messages are provided
            assert "for_proposal" in data
            assert "against" in data
