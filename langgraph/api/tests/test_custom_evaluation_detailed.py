"""
End-to-end tests for the custom evaluation feature.

These tests focus on verifying the detailed functionality of the custom evaluation
feature, including handling of various criteria formats and response structures.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from unittest.mock import AsyncMock

from tests.test_base import BaseTest


class TestCustomEvaluationDetailed(BaseTest):
    """Test detailed functionality of the custom evaluation feature."""
    
    @pytest.mark.e2e
    @pytest.mark.custom
    async def test_custom_evaluation_with_complex_criteria(self, async_client: AsyncClient, monkeypatch):
        """
        Test custom evaluation with complex nested criteria.
        """
        from app.services.langgraph.graph import graph
        
        # Define complex criteria
        complex_criteria = {
            "financial": {
                "treasury_impact": "The proposal should clearly state the financial impact on the treasury.",
                "roi": "The proposal should demonstrate a positive return on investment."
            },
            "technical": {
                "feasibility": "The proposal should be technically feasible with current resources.",
                "security": "The proposal should not introduce security vulnerabilities."
            },
            "governance": {
                "alignment": "The proposal should align with the community's stated values and mission.",
                "decentralization": "The proposal should promote decentralization."
            }
        }
        
        # Mock response with matching structure
        mock_response = {
            "summary": "The proposal meets most criteria but has some concerns.",
            "response_map": {
                "financial.treasury_impact": {
                    "status": "pass",
                    "justification": "The proposal clearly states it will use 10% of the treasury."
                },
                "financial.roi": {
                    "status": "fail",
                    "justification": "The proposal does not quantify the expected return.",
                    "suggestions": ["Add specific metrics for measuring success."]
                },
                "technical.feasibility": {
                    "status": "pass",
                    "justification": "The proposal uses existing technology and resources."
                },
                "technical.security": {
                    "status": "pass",
                    "justification": "No security concerns identified."
                },
                "governance.alignment": {
                    "status": "pass",
                    "justification": "The proposal aligns with the community's focus on developer support."
                },
                "governance.decentralization": {
                    "status": "fail",
                    "justification": "The proposal centralizes decision-making in a small committee.",
                    "suggestions": ["Add community voting mechanisms for fund allocation."]
                }
            }
        }
        
        # Mock the graph.ainvoke method
        async def mock_invoke(input_data, runtime):
            if input_data.get("task") == "custom_evaluate":
                return {"custom_evaluation": mock_response}
            return {}
        
        # Apply the mock
        monkeypatch.setattr(graph, "ainvoke", AsyncMock(side_effect=mock_invoke))
        
        # Create request data
        request_data = {
            "content": self.get_test_proposal()["content"],
            "custom_criteria": complex_criteria
        }
        
        # Send request for custom evaluation
        response = await async_client.post(
            "/api/v1/pre-filter/custom",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify that evaluation results were generated with the correct structure
        assert data["summary"] == "The proposal meets most criteria but has some concerns."
        assert len(data["response_map"]) == 6
        
        # Check specific criteria results
        assert data["response_map"]["financial.treasury_impact"]["status"] == "pass"
        assert data["response_map"]["financial.roi"]["status"] == "fail"
        assert "suggestions" in data["response_map"]["financial.roi"]
        assert data["response_map"]["governance.decentralization"]["status"] == "fail"
    
    @pytest.mark.e2e
    @pytest.mark.custom
    async def test_custom_evaluation_with_missing_fields(self, async_client: AsyncClient, monkeypatch):
        """
        Test that the API handles responses with missing fields gracefully.
        """
        from app.services.langgraph.graph import graph
        
        # Mock response with missing fields
        mock_response = {
            "summary": "Partial evaluation completed.",
            "response_map": {
                "criteria1": {
                    "status": "pass"
                    # Missing justification
                },
                "criteria2": {
                    # Missing status
                    "justification": "Some justification"
                },
                "criteria3": {
                    "status": "fail",
                    "justification": "Failed for some reason",
                    "suggestions": []  # Empty suggestions
                }
            }
        }
        
        # Mock the graph.ainvoke method
        async def mock_invoke(input_data, runtime):
            if input_data.get("task") == "custom_evaluate":
                return {"custom_evaluation": mock_response}
            return {}
        
        # Apply the mock
        monkeypatch.setattr(graph, "ainvoke", AsyncMock(side_effect=mock_invoke))
        
        # Create request data
        request_data = {
            "content": self.get_test_proposal()["content"],
            "custom_criteria": self.get_test_custom_criteria()
        }
        
        # Send request for custom evaluation
        response = await async_client.post(
            "/api/v1/pre-filter/custom",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # Check response - should still work despite missing fields
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify that the response has the expected structure
        assert data["summary"] == "Partial evaluation completed."
        assert "criteria1" in data["response_map"]
        assert "criteria2" in data["response_map"]
        assert "criteria3" in data["response_map"]
    
    @pytest.mark.e2e
    @pytest.mark.custom
    async def test_custom_evaluation_error_handling(self, async_client: AsyncClient, monkeypatch):
        """
        Test that the API handles errors in the evaluation process gracefully.
        """
        from app.services.langgraph.graph import graph
        
        # Mock the graph.ainvoke method to raise an exception
        async def mock_invoke(input_data, runtime):
            if input_data.get("task") == "custom_evaluate":
                raise ValueError("Simulated error in evaluation process")
            return {}
        
        # Apply the mock
        monkeypatch.setattr(graph, "ainvoke", AsyncMock(side_effect=mock_invoke))
        
        # Create request data
        request_data = {
            "content": self.get_test_proposal()["content"],
            "custom_criteria": self.get_test_custom_criteria()
        }
        
        # Send request for custom evaluation
        response = await async_client.post(
            "/api/v1/pre-filter/custom",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # Check response - should return an error
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        
        # Verify that the error message is included
        assert "detail" in data
        assert "Failed to evaluate proposal" in data["detail"]
