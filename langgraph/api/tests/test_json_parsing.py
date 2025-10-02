"""
End-to-end tests for JSON parsing functionality in the API.

These tests focus on the JSON parsing capabilities that are critical for
handling AI model responses in various formats.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
import json

from tests.test_base import BaseTest


class TestJsonParsing(BaseTest):
    """Test JSON parsing functionality in real API scenarios."""
    
    @pytest.mark.e2e
    @pytest.mark.custom
    @pytest.mark.parametrize("json_format", [
        # Standard JSON in code block
        """```json
        {
            "summary": "Test summary",
            "response_map": {
                "criteria1": {
                    "status": "pass",
                    "justification": "Test justification"
                }
            }
        }
        ```""",
        
        # JSON without language marker
        """```
        {
            "summary": "Test summary",
            "response_map": {
                "criteria1": {
                    "status": "pass",
                    "justification": "Test justification"
                }
            }
        }
        ```""",
        
        # JSON with uppercase marker
        """```JSON
        {
            "summary": "Test summary",
            "response_map": {
                "criteria1": {
                    "status": "pass",
                    "justification": "Test justification"
                }
            }
        }
        ```""",
        
        # JSON with alternative markers
        """~~~json
        {
            "summary": "Test summary",
            "response_map": {
                "criteria1": {
                    "status": "pass",
                    "justification": "Test justification"
                }
            }
        }
        ~~~""",
        
        # Plain JSON without markers
        """{
            "summary": "Test summary",
            "response_map": {
                "criteria1": {
                    "status": "pass",
                    "justification": "Test justification"
                }
            }
        }""",
        
        # JSON with surrounding text
        """Here's the evaluation result:
        
        {
            "summary": "Test summary",
            "response_map": {
                "criteria1": {
                    "status": "pass",
                    "justification": "Test justification"
                }
            }
        }
        
        I hope this helps!"""
    ])
    def test_json_parsing_in_custom_evaluation(self, test_client: TestClient, monkeypatch, json_format):
        """
        Test that the API can correctly parse JSON in various formats during custom evaluation.
        
        This test mocks the LangGraph response to return different JSON formats and verifies
        that the API correctly extracts and processes the JSON regardless of format.
        """
        from app.services.langgraph.graph import graph
        from unittest.mock import AsyncMock
        
        # Mock the graph.ainvoke method to return our test JSON
        mock_result = {"custom_evaluation": json_format}
        mock_invoke = AsyncMock(return_value=mock_result)
        monkeypatch.setattr(graph, "ainvoke", mock_invoke)
        
        # Create request data
        request_data = {
            "content": self.get_test_proposal()["content"],
            "custom_criteria": self.get_test_custom_criteria()
        }
        
        # Send request for custom evaluation
        response = test_client.post(
            "/api/v1/pre-filter/custom",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify that JSON was correctly parsed
        assert data["summary"] == "Test summary"
        assert "criteria1" in data["response_map"]
        assert data["response_map"]["criteria1"]["status"] == "pass"
        assert data["response_map"]["criteria1"]["justification"] == "Test justification"
    
    @pytest.mark.e2e
    @pytest.mark.arguments
    @pytest.mark.parametrize("json_format", [
        # Standard JSON in code block
        """```json
        {
            "for_proposal": ["Argument for 1", "Argument for 2"],
            "against": ["Argument against 1", "Argument against 2"]
        }
        ```""",
        
        # Plain JSON without markers
        """{
            "for_proposal": ["Argument for 1", "Argument for 2"],
            "against": ["Argument against 1", "Argument against 2"]
        }""",
        
        # JSON with surrounding text
        """Here are the arguments:
        
        {
            "for_proposal": ["Argument for 1", "Argument for 2"],
            "against": ["Argument against 1", "Argument against 2"]
        }
        
        Hope this helps!"""
    ])
    def test_json_parsing_in_arguments(self, test_client: TestClient, monkeypatch, json_format):
        """
        Test that the API can correctly parse JSON in various formats during argument generation.
        
        This test mocks the LangGraph response to return different JSON formats and verifies
        that the API correctly extracts and processes the arguments JSON regardless of format.
        """
        from app.services.langgraph.graph import graph
        from unittest.mock import AsyncMock
        
        # Mock the graph.ainvoke method to return our test JSON
        mock_result = {"arguments": json_format}
        mock_invoke = AsyncMock(return_value=mock_result)
        monkeypatch.setattr(graph, "ainvoke", mock_invoke)
        
        # Create request data
        request_data = {
            "content": self.get_test_proposal()["content"],
            "proposal_id": "test-proposal-args",
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
        
        # Verify that JSON was correctly parsed
        assert "for_proposal" in data
        assert "against" in data
        assert len(data["for_proposal"]) == 2
        assert len(data["against"]) == 2
        assert data["for_proposal"][0] == "Argument for 1"
        assert data["against"][0] == "Argument against 1"
    
    @pytest.mark.e2e
    @pytest.mark.arguments
    def test_filtering_placeholder_arguments(self, test_client: TestClient, monkeypatch):
        """
        Test that the API correctly filters out placeholder arguments.
        """
        from app.services.langgraph.graph import graph
        from unittest.mock import AsyncMock
        
        # JSON with placeholder arguments that should be filtered
        json_with_placeholders = """{
            "for_proposal": ["Real argument for", "Placeholder argument", "PLACEHOLDER: This should be removed"],
            "against": ["Real argument against", "placeholder: Another one to remove", "Valid point"]
        }"""
        
        # Mock the graph.ainvoke method to return our test JSON
        mock_result = {"arguments": json_with_placeholders}
        mock_invoke = AsyncMock(return_value=mock_result)
        monkeypatch.setattr(graph, "ainvoke", mock_invoke)
        
        # Create request data
        request_data = {
            "content": self.get_test_proposal()["content"],
            "proposal_id": "test-proposal-filter",
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
        
        # Verify that placeholder arguments were filtered out
        assert len(data["for_proposal"]) == 1
        assert len(data["against"]) == 2
        assert "Real argument for" in data["for_proposal"]
        assert "Placeholder argument" not in data["for_proposal"]
        assert "PLACEHOLDER: This should be removed" not in data["for_proposal"]
        assert "placeholder: Another one to remove" not in data["against"]
