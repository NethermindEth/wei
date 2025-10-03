"""
Tests for the API components.

This module contains tests for the API components, including:
- Repository pattern
- Service layer
- Dependency injection
- Error handling
"""

# Standard library imports
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

# Third-party imports
import pytest
from fastapi import FastAPI, Depends, status
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock, AsyncMock

# Local application imports
from app.main import app
from app.db.models import Analysis
from app.repositories.analysis_repository import (
    AnalysisRepository, AnalysisCreate, AnalysisUpdate
)
from app.services.analysis_service import AnalysisService
from app.schemas import AnalysisResponse, ProposalArguments
from app.test_utils import (
    MockRepository, MockService, create_test_client, 
    create_async_test_client, mock_dependency
)


class TestApiComponents:
    """Test the API components."""
    
    @pytest.fixture
    def test_client(self) -> TestClient:
        """Create a test client."""
        return create_test_client(app)
    
    @pytest.fixture
    async def async_client(self) -> AsyncClient:
        """Create an async test client."""
        async_client = await create_async_test_client(app)
        yield async_client
        await async_client.aclose()
    
    @pytest.fixture
    def mock_repository(self) -> MockRepository:
        """Create a mock repository."""
        return MockRepository(Analysis)
    
    @pytest.fixture
    def mock_create_analysis(self):
        """Mock the create_analysis function."""
        async def mock_create_analysis(db, proposal_id, result, confidence, details, arguments=None):
            # Create a mock Analysis object
            analysis = MagicMock()
            analysis.id = uuid.uuid4()
            analysis.proposal_id = proposal_id
            analysis.result = result
            analysis.confidence = confidence
            analysis.details = details
            analysis.arguments = arguments
            analysis.created_at = datetime.now()
            analysis.updated_at = datetime.now()
            return analysis
        return AsyncMock(side_effect=mock_create_analysis)
    
    @pytest.fixture
    def mock_graph_ainvoke(self):
        """Mock the graph.ainvoke method."""
        async def mock_ainvoke(input_data, runtime=None):
            task = input_data.get("task")
            if task == "analyze_proposal":
                return {
                    "analysis_result": {
                        "result": "pass",
                        "confidence": 0.85,
                        "details": "Test details"
                    },
                    "arguments": {
                        "for_proposal": ["Test supporting argument."],
                        "against": ["Test opposing argument."]
                    }
                }
            elif task == "generate_arguments":
                return {
                    "arguments": {
                        "for_proposal": ["Test supporting argument."],
                        "against": ["Test opposing argument."]
                    }
                }
            elif task == "custom_evaluate":
                return {
                    "custom_evaluation": {
                        "summary": "Test summary",
                        "response_map": {
                            "test_criterion": {
                                "status": "pass",
                                "justification": "Test justification",
                                "suggestions": ["Test suggestion"]
                            }
                        }
                    }
                }
            elif task == "search_related_proposals":
                return {
                    "search_results": [
                        {"id": "1", "title": "Test Proposal 1", "score": 0.95},
                        {"id": "2", "title": "Test Proposal 2", "score": 0.85}
                    ]
                }
            elif task == "chat":
                from langchain_core.messages import AIMessage
                return {
                    "messages": [AIMessage(content="Test response")]
                }
            return {}
        return AsyncMock(side_effect=mock_ainvoke)
    
    @pytest.fixture
    def mock_service(self, mock_repository) -> MockService:
        """Create a mock service."""
        service = AnalysisService(mock_repository)
        
        # Mock the to_response method
        async def mock_analyze_proposal(*args, **kwargs):
            return AnalysisResponse(
                id=uuid.uuid4(),
                proposal_id=kwargs.get("proposal_id", str(uuid.uuid4())),
                result="pass",
                confidence=0.85,
                details="Test details",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                arguments=ProposalArguments(
                    for_proposal=["Test supporting argument."],
                    against=["Test opposing argument."]
                )
            )
        
        # Mock service methods
        service.analyze_proposal = AsyncMock(side_effect=mock_analyze_proposal)
        service.get_proposal_arguments = AsyncMock(return_value=ProposalArguments(
            for_proposal=["Test supporting argument."],
            against=["Test opposing argument."]
        ))
        service.custom_evaluate_proposal = AsyncMock(return_value={
            "summary": "Test summary",
            "response_map": {
                "test_criterion": {
                    "status": "pass",
                    "justification": "Test justification",
                    "suggestions": ["Test suggestion"]
                }
            }
        })
        service.search_related_proposals = AsyncMock(return_value=[
            {"id": "1", "title": "Test Proposal 1", "score": 0.95},
            {"id": "2", "title": "Test Proposal 2", "score": 0.85}
        ])
        service.chat = AsyncMock(return_value="Test response")
        
        return service
    
    @pytest.fixture
    def auth_headers(self) -> Dict[str, str]:
        """Create authentication headers."""
        return {"X-API-Key": "test_api_key"}
    
    def test_api_key_authentication(self, test_client: TestClient, auth_headers: Dict[str, str]):
        """Test API key authentication."""
        # Test with valid API key
        response = test_client.get("/api/v1/test", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "API key is valid"}
        
        # Test with invalid API key
        response = test_client.get("/api/v1/test", headers={"X-API-Key": "invalid_key"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Test without API key
        response = test_client.get("/api/v1/test")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_analyze_proposal(
        self, 
        async_client: AsyncClient, 
        mock_service: AnalysisService,
        mock_graph_ainvoke,
        mock_create_analysis,
        auth_headers: Dict[str, str]
    ):
        """Test analyzing a proposal."""
        # Mock the get_analysis_service dependency
        mock_dependency(app, "get_analysis_service", mock_service)
        
        # Mock the create_analysis function
        with patch('app.api.routes.create_analysis', mock_create_analysis):
            # Mock the graph.ainvoke method
            with patch('app.api.routes.graph.ainvoke', mock_graph_ainvoke):
                # Create test data
                proposal_id = str(uuid.uuid4())
                proposal_text = "This is a test proposal to increase the community treasury allocation for developer grants by 10%."
                
                # Send request
                response = await async_client.post(
                    "/api/v1/pre-filter",
                    json={
                        "content": proposal_text,
                        "proposal_id": proposal_id
                    },
                    headers=auth_headers
                )
                
                # Check response
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "id" in data
                assert data["proposal_id"] == proposal_id
                assert data["result"] == "pass"
                assert data["confidence"] == 0.85
                assert data["details"] == "Test details"
                assert "created_at" in data
                assert "updated_at" in data
                assert "arguments" in data
                assert "for_proposal" in data["arguments"]
                assert "against" in data["arguments"]
    
    
    @pytest.mark.asyncio
    async def test_get_proposal_arguments(
        self, 
        async_client: AsyncClient, 
        mock_service: AnalysisService,
        mock_graph_ainvoke,
        mock_create_analysis,
        auth_headers: Dict[str, str]
    ):
        """Test generating arguments for a proposal."""
        # Mock the get_analysis_service dependency
        mock_dependency(app, "get_analysis_service", mock_service)
        
        # Mock the create_analysis function
        with patch('app.api.routes.create_analysis', mock_create_analysis):
            # Mock the graph.ainvoke method
            with patch('app.api.routes.graph.ainvoke', mock_graph_ainvoke):
                # Create test data
                proposal_id = str(uuid.uuid4())
                proposal_text = "This is a test proposal to increase the community treasury allocation for developer grants by 10%."
                
                # Send request
                response = await async_client.post(
                    "/api/v1/pre-filter/arguments",
                    json={
                        "content": proposal_text,
                        "proposal_id": proposal_id,
                        "max_arguments": 3
                    },
                    headers=auth_headers
                )
                
                # Check response
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "for_proposal" in data
                assert "against" in data
                assert len(data["for_proposal"]) > 0
                assert len(data["against"]) > 0
    
    @pytest.mark.asyncio
    async def test_custom_evaluate_proposal(
        self, 
        async_client: AsyncClient, 
        mock_service: AnalysisService,
        mock_graph_ainvoke,
        mock_create_analysis,
        auth_headers: Dict[str, str]
    ):
        """Test evaluating a proposal with custom criteria."""
        # Mock the get_analysis_service dependency
        mock_dependency(app, "get_analysis_service", mock_service)
        
        # Mock the create_analysis function
        with patch('app.api.routes.create_analysis', mock_create_analysis):
            # Mock the graph.ainvoke method
            with patch('app.api.routes.graph.ainvoke', mock_graph_ainvoke):
                # Create test data
                proposal_text = "This is a test proposal to increase the community treasury allocation for developer grants by 10%."
                custom_criteria = {
                    "criteria1": "The proposal should clearly state the amount of funds requested.",
                    "criteria2": "The proposal should explain how the funds will be used.",
                    "criteria3": "The proposal should include a timeline for implementation."
                }
                
                # Send request
                response = await async_client.post(
                    "/api/v1/pre-filter/custom",
                    json={
                        "content": proposal_text,
                        "custom_criteria": custom_criteria
                    },
                    headers=auth_headers
                )
                
                # Check response
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "summary" in data
                assert "response_map" in data
                assert isinstance(data["response_map"], dict)
                assert "test_criterion" in data["response_map"]
                assert data["response_map"]["test_criterion"]["status"] == "pass"
    
    @pytest.mark.asyncio
    async def test_search_related_proposals(
        self, 
        async_client: AsyncClient, 
        mock_service: AnalysisService,
        mock_graph_ainvoke,
        mock_create_analysis,
        auth_headers: Dict[str, str]
    ):
        """Test searching for related proposals."""
        # Mock the get_analysis_service dependency
        mock_dependency(app, "get_analysis_service", mock_service)
        
        # Mock the create_analysis function
        with patch('app.api.routes.create_analysis', mock_create_analysis):
            # Mock the graph.ainvoke method
            with patch('app.api.routes.graph.ainvoke', mock_graph_ainvoke):
                # Create test data
                search_query = "treasury allocation"
                
                # Send request
                response = await async_client.get(
                    f"/api/v1/related-proposals?query={search_query}",
                    headers=auth_headers
                )
                
                # Check response
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert isinstance(data, list)
                assert len(data) > 0
                assert "id" in data[0]
                assert "title" in data[0]
                assert "score" in data[0]
    @pytest.mark.asyncio
    async def test_chat(
        self, 
        async_client: AsyncClient, 
        mock_service: AnalysisService,
        mock_graph_ainvoke,
        mock_create_analysis
    ):
        """Test chatting with the agent."""
        # Mock the get_analysis_service dependency
        mock_dependency(app, "get_analysis_service", mock_service)
        
        # Mock the create_analysis function
        with patch('app.api.routes.create_analysis', mock_create_analysis):
            # Mock the graph.ainvoke method
            with patch('app.api.routes.graph.ainvoke', mock_graph_ainvoke):
                # Send request
                response = await async_client.post(
                    "/api/v1/chat",
                    json={"message": "Hello, agent!"}
                )
                
                # Check response
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "response" in data
                assert data["response"] == "Test response"
    
    @pytest.mark.asyncio
    async def test_error_handling(
        self, 
        async_client: AsyncClient, 
        mock_service: AnalysisService,
        auth_headers: Dict[str, str]
    ):
        """Test error handling."""
        # Mock the get_analysis_service dependency
        mock_dependency(app, "get_analysis_service", mock_service)
        
        # Test validation error
        response = await async_client.post(
            "/api/v1/pre-filter",
            json={
                "content": "",  # Empty content should fail validation
                "proposal_id": str(uuid.uuid4())
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test missing required field
        response = await async_client.post(
            "/api/v1/pre-filter",
            json={
                "proposal_id": str(uuid.uuid4())
                # Missing content field
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
