"""
End-to-end tests for custom evaluation endpoints.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from tests.test_base import BaseTest


class TestCustomEvaluation(BaseTest):
    """Test custom evaluation endpoints."""
    
    @pytest.mark.e2e
    def test_custom_evaluate_proposal(self, test_client: TestClient):
        """Test custom evaluation of a proposal."""
        # Create request data
        request_data = {
            "content": self.get_test_proposal()["content"],
            "custom_criteria": self.get_test_custom_criteria()
        }
        
        # Mock the graph.ainvoke method
        async def mock_invoke(input_data, runtime=None):
            if input_data.get("task") == "custom_evaluate":
                return {
                    "custom_evaluation": {
                        "summary": "The proposal meets most criteria.",
                        "response_map": {
                            "clarity": {
                                "status": "pass",
                                "justification": "The proposal is clearly written."
                            },
                            "feasibility": {
                                "status": "pass",
                                "justification": "The proposal is feasible."
                            }
                        }
                    }
                }
            return {}
        
        # Apply the mock
        with patch('app.api.routes.graph.ainvoke', AsyncMock(side_effect=mock_invoke)):
            # Send request for custom evaluation
            response = test_client.post(
                "/api/v1/pre-filter/custom",
                json=request_data,
                headers=self.get_auth_headers()
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Check that evaluation results were generated
            assert "summary" in data
            assert "response_map" in data
            assert isinstance(data["response_map"], dict)
            
            # Check that criteria were evaluated
            assert "clarity" in data["response_map"]
            assert "feasibility" in data["response_map"]
            criterion_result = data["response_map"]["clarity"]
            assert "status" in criterion_result
            assert "justification" in criterion_result
    
    @pytest.mark.e2e
    def test_custom_evaluate_with_empty_criteria(self, test_client: TestClient):
        """Test custom evaluation with empty criteria."""
        # Create request data with empty criteria
        request_data = {
            "content": self.get_test_proposal()["content"],
            "custom_criteria": {}
        }
        
        # Mock the graph.ainvoke method
        async def mock_invoke(input_data, runtime=None):
            if input_data.get("task") == "custom_evaluate":
                return {
                    "custom_evaluation": {
                        "summary": "No criteria provided for evaluation.",
                        "response_map": {}
                    }
                }
            return {}
        
        # Apply the mock
        with patch('app.api.routes.graph.ainvoke', AsyncMock(side_effect=mock_invoke)):
            # Send request for custom evaluation
            response = test_client.post(
                "/api/v1/pre-filter/custom",
                json=request_data,
                headers=self.get_auth_headers()
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Check that evaluation structure is present
            assert "summary" in data
            assert "response_map" in data
    
    @pytest.mark.e2e
    def test_custom_evaluate_with_complex_criteria(self, test_client: TestClient):
        """Test custom evaluation with complex criteria."""
        # Create request data with complex criteria
        complex_criteria = {
            "financial_impact": "The proposal should clearly state the financial impact on the treasury.",
            "technical_feasibility": "The proposal should be technically feasible with current resources.",
            "community_benefit": "The proposal should benefit the broader community, not just a small group.",
            "alignment_with_values": "The proposal should align with the community's stated values and mission."
        }
        
        request_data = {
            "content": self.get_test_proposal()["content"],
            "custom_criteria": complex_criteria
        }
        
        # Mock the graph.ainvoke method
        async def mock_invoke(input_data, runtime=None):
            if input_data.get("task") == "custom_evaluate":
                response_map = {}
                for key in complex_criteria.keys():
                    response_map[key] = {
                        "status": "pass",
                        "justification": f"The proposal meets the {key} criterion."
                    }
                
                return {
                    "custom_evaluation": {
                        "summary": "The proposal meets all complex criteria.",
                        "response_map": response_map
                    }
                }
            return {}
        
        # Apply the mock
        with patch('app.api.routes.graph.ainvoke', AsyncMock(side_effect=mock_invoke)):
            # Send request for custom evaluation
            response = test_client.post(
                "/api/v1/pre-filter/custom",
                json=request_data,
                headers=self.get_auth_headers()
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Check that evaluation results were generated
            assert "summary" in data
            assert "response_map" in data
            
            # Check that all criteria were evaluated
            for criterion_key in complex_criteria.keys():
                assert criterion_key in data["response_map"]
