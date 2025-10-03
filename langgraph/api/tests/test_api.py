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
        async def mock_create_analysis(db, proposal_id, result, confidence, details, arguments=None, content=None):
            # Create a mock Analysis object
            analysis = MagicMock()
            analysis.id = uuid.uuid4()
            analysis.proposal_id = proposal_id
            analysis.result = result
            analysis.confidence = confidence
            analysis.details = details
            analysis.arguments = arguments
            analysis.content = content
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
                        "description": proposal_text,
                        "proposal_id": proposal_id
                    },
                    headers=auth_headers
                )
                
                # Check response
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "structured_response" in data
                structured_response = data["structured_response"]
                assert "id" in structured_response
                assert structured_response["proposal_id"] == proposal_id
                assert structured_response["result"] == "pass"
                assert structured_response["confidence"] == 0.85
                assert structured_response["details"] == "Test details"
                assert "created_at" in structured_response
                assert "updated_at" in structured_response
                assert "arguments" in structured_response
                assert "for_proposal" in structured_response["arguments"]
                assert "against" in structured_response["arguments"]
    
    
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
                        "description": proposal_text,
                        "proposal_id": proposal_id,
                        "max_arguments": 3
                    },
                    headers=auth_headers
                )
                
                # Check response
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "arguments" in data
                assert "from_cache" in data
                arguments = data["arguments"]
                assert "for_proposal" in arguments
                assert "against" in arguments
                assert len(arguments["for_proposal"]) > 0
                assert len(arguments["against"]) > 0
    
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
                        "description": proposal_text,
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
                assert "related_proposals" in data
                assert "query" in data
                assert "from_cache" in data
                related_proposals = data["related_proposals"]
                assert isinstance(related_proposals, list)
                assert len(related_proposals) > 0
                assert "id" in related_proposals[0]
                assert "title" in related_proposals[0]
                assert "score" in related_proposals[0]
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
                "description": "",  # Empty description should fail validation
                "proposal_id": str(uuid.uuid4())
            },
            headers=auth_headers
        )
        # Pydantic will validate that the field exists, but our custom validation in the route
        # will check if it's empty, so we need to make sure it passes Pydantic validation first
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test missing required field
        response = await async_client.post(
            "/api/v1/pre-filter",
            json={
                "proposal_id": str(uuid.uuid4())
                # Missing description field
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Pydantic validation error
