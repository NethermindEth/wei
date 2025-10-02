"""
End-to-end tests for the integration between the API and the LangGraph runtime.

These tests focus on verifying that the API correctly integrates with the
LangGraph runtime for various tasks.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from tests.test_base import BaseTest


class TestLangGraphIntegration(BaseTest):
    """Test integration between the API and the LangGraph runtime."""
    
    @pytest.mark.e2e
    def test_graph_initialization(self, test_client: TestClient):
        """Test that the LangGraph is correctly initialized."""
        # Import the graph to check if it's initialized
        from app.services.langgraph.graph import graph
        
        # The graph should be initialized and have nodes
        assert graph is not None
        
        # Send a simple request to trigger graph usage
        response = test_client.post(
            "/api/v1/chat",
            json={"message": "Hello"},
        )
        
        # Check that the request was successful
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.e2e
    def test_context_creation(self, test_client: TestClient, monkeypatch):
        """Test that the Context is correctly created with the right parameters."""
        from app.services.langgraph.context import Context
        from app.services.langgraph.graph import graph
        
        # Create a mock Context class to capture initialization parameters
        original_init = Context.__init__
        context_params = {}
        
        def mock_init(self, *args, **kwargs):
            nonlocal context_params
            context_params = kwargs
            original_init(self, *args, **kwargs)
        
        # Mock the graph.ainvoke method
        async def mock_ainvoke(input_data, runtime=None):
            return {
                "analysis_result": {
                    "result": "pass",
                    "confidence": 0.85,
                    "details": "Test details"
                }
            }
            
        # Mock the create_analysis function
        from uuid import uuid4
        from datetime import datetime
        
        mock_analysis = MagicMock()
        mock_analysis.id = uuid4()
        mock_analysis.proposal_id = "test-proposal-1"
        mock_analysis.result = "pass"
        mock_analysis.confidence = 0.85
        mock_analysis.details = "Test details"
        mock_analysis.created_at = datetime.now()
        mock_analysis.updated_at = datetime.now()
        
        async def mock_create_analysis(*args, **kwargs):
            return mock_analysis
        
        # Apply the mocks
        monkeypatch.setattr(Context, "__init__", mock_init)
        monkeypatch.setattr(graph, "ainvoke", AsyncMock(side_effect=mock_ainvoke))
        monkeypatch.setattr('app.api.routes.create_analysis', AsyncMock(side_effect=mock_create_analysis))
        
        # Send a request to trigger Context creation
        response = test_client.post(
            "/api/v1/pre-filter",
            json=self.get_test_proposal(),
            headers=self.get_auth_headers()
        )
        
        # Check that the request was successful
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the Context was created with the right parameters
        assert "model" in context_params
        assert "openrouter_api_key" in context_params
        assert "exa_api_key" in context_params
    
    @pytest.mark.skip(reason="Runtime creation causes event loop issues in tests")
    @pytest.mark.e2e
    def test_runtime_creation(self, test_client: TestClient, monkeypatch):
        """Test that the Runtime is correctly created with the right context."""
        from app.services.langgraph.graph import graph
        
        # Mock the graph.ainvoke method
        async def mock_ainvoke(input_data, runtime=None):
            # Check if runtime has a context
            assert runtime is not None
            assert hasattr(runtime, 'context')
            
            return {
                "analysis_result": {
                    "result": "pass",
                    "confidence": 0.85,
                    "details": "Test details"
                }
            }
        
        # Apply the mock
        monkeypatch.setattr(graph, "ainvoke", AsyncMock(side_effect=mock_ainvoke))
        
        # Send a request to trigger Runtime creation
        response = test_client.post(
            "/api/v1/pre-filter",
            json=self.get_test_proposal(),
            headers=self.get_auth_headers()
        )
        
        # Check that the request was successful
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.e2e
    def test_graph_invocation_parameters(self, test_client: TestClient, monkeypatch):
        """Test that the graph is invoked with the right parameters for different tasks."""
        from app.services.langgraph.graph import graph
        
        # Create a mock for the graph.ainvoke method
        invoke_params = {}
        
        async def mock_ainvoke(input_data, runtime=None):
            nonlocal invoke_params
            invoke_params = input_data
            
            # Return appropriate mock results based on the task
            if input_data.get("task") == "analyze_proposal":
                return {
                    "analysis_result": {
                        "result": "pass",
                        "confidence": 0.85,
                        "details": "This is a good proposal."
                    }
                }
            elif input_data.get("task") == "generate_arguments":
                return {
                    "arguments": {
                        "for_proposal": ["Argument for"],
                        "against": ["Argument against"]
                    }
                }
            elif input_data.get("task") == "custom_evaluate":
                return {
                    "custom_evaluation": {
                        "summary": "Test summary",
                        "response_map": {
                            "criteria1": {
                                "status": "pass",
                                "justification": "Test justification"
                            }
                        }
                    }
                }
            elif input_data.get("task") == "chat":
                return {
                    "messages": ["Test response"]
                }
            else:
                return {}
        
        # Apply the mock
        monkeypatch.setattr(graph, "ainvoke", AsyncMock(side_effect=mock_ainvoke))
        
        # Test proposal analysis
        test_client.post(
            "/api/v1/pre-filter",
            json=self.get_test_proposal(),
            headers=self.get_auth_headers()
        )
        assert invoke_params.get("task") == "analyze_proposal"
        assert "proposal_text" in invoke_params
        
        # Test argument generation
        test_client.post(
            "/api/v1/pre-filter/arguments",
            json={
                "content": self.get_test_proposal()["content"],
                "proposal_id": "test-args",
                "max_arguments": 3
            },
            headers=self.get_auth_headers()
        )
        assert invoke_params.get("task") == "generate_arguments"
        assert "proposal_text" in invoke_params
        
        # Test custom evaluation
        test_client.post(
            "/api/v1/pre-filter/custom",
            json={
                "content": self.get_test_proposal()["content"],
                "custom_criteria": self.get_test_custom_criteria()
            },
            headers=self.get_auth_headers()
        )
        assert invoke_params.get("task") == "custom_evaluate"
        assert "proposal_text" in invoke_params
        assert "custom_criteria" in invoke_params
        
        # Test chat
        test_client.post(
            "/api/v1/chat",
            json={"message": "Hello"}
        )
        assert invoke_params.get("task") == "chat"
        assert "messages" in invoke_params
    
    @pytest.mark.e2e
    def test_model_configuration(self, test_client: TestClient, monkeypatch):
        """Test that the model is correctly configured from environment variables."""
        from app.config import (
            WEI_AGENT_AI_MODEL_PROVIDER,
            WEI_AGENT_AI_MODEL_NAME
        )
        from app.services.langgraph.graph import graph
        
        # The model configuration should be available
        assert WEI_AGENT_AI_MODEL_PROVIDER is not None
        assert WEI_AGENT_AI_MODEL_NAME is not None
        
        # Mock the graph.ainvoke method
        async def mock_ainvoke(input_data, runtime=None):
            return {"messages": ["I am using " + WEI_AGENT_AI_MODEL_NAME]}
        
        # Apply the mock
        monkeypatch.setattr(graph, "ainvoke", AsyncMock(side_effect=mock_ainvoke))
        
        # Send a request to use the model
        response = test_client.post(
            "/api/v1/chat",
            json={"message": "What model are you using?"}
        )
        
        # Check that the request was successful
        assert response.status_code == status.HTTP_200_OK
