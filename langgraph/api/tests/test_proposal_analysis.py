"""
End-to-end tests for proposal analysis endpoints.
"""

import uuid
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from fastapi import status, Depends
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.models import Analysis
from app.db import get_session
from app.api.routes import create_analysis, get_analysis_by_id, find_analysis_by_proposal_id, find_analyses_by_proposal_id
from tests.test_base import BaseTest


class TestProposalAnalysis(BaseTest):
    """Test proposal analysis endpoints."""
    
    def test_analyze_proposal(self, test_client: TestClient):
        """Test analyzing a proposal."""
        # Create a unique proposal ID for this test
        unique_proposal_id = f"test-proposal-{uuid.uuid4()}"
        test_proposal = self.get_test_proposal(unique_proposal_id)
        analysis_id = uuid.uuid4()
        
        # Create a mock analysis object
        mock_analysis = MagicMock()
        mock_analysis.id = analysis_id
        mock_analysis.proposal_id = unique_proposal_id
        mock_analysis.result = "pass"
        mock_analysis.confidence = 0.85
        mock_analysis.details = "Test details"
        mock_analysis.created_at = datetime.now()
        mock_analysis.updated_at = datetime.now()
        
        # Mock the graph.ainvoke method
        with patch('app.api.routes.graph.ainvoke') as mock_ainvoke, \
             patch('app.api.routes.create_analysis', return_value=mock_analysis) as mock_create_analysis:
            
            # Set up the mock response from the graph
            mock_ainvoke.return_value = {
                "analysis_result": {
                    "result": "pass",
                    "confidence": 0.85,
                    "details": "Test details"
                }
            }
            
            # Set up the mock create_analysis function
            mock_create_analysis.return_value = mock_analysis
            
            # Send a proposal for analysis
            response = test_client.post(
                "/api/v1/pre-filter",
                json=test_proposal,
                headers=self.get_auth_headers()
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "id" in data
            assert data["proposal_id"] == unique_proposal_id
            assert data["result"] == "pass"
            assert data["confidence"] == 0.85
            assert data["details"] == "Test details"
            assert "created_at" in data
            assert "updated_at" in data
    
    def test_get_analysis_by_id(self, test_client: TestClient):
        """Test getting an analysis by ID."""
        # Create a unique analysis ID for this test
        analysis_id = uuid.uuid4()
        unique_proposal_id = f"test-proposal-{uuid.uuid4()}"
        
        # Create a mock analysis object
        mock_analysis = MagicMock()
        mock_analysis.id = analysis_id
        mock_analysis.proposal_id = unique_proposal_id
        mock_analysis.result = "pass"
        mock_analysis.confidence = 0.85
        mock_analysis.details = "Test details"
        mock_analysis.created_at = datetime.now()
        mock_analysis.updated_at = datetime.now()
        
        # Mock the get_analysis_by_id function
        with patch('app.api.routes.get_analysis_by_id', return_value=mock_analysis) as mock_get_analysis:
            # Set up the mock response
            mock_get_analysis.return_value = mock_analysis
            
            # Get the analysis by ID
            response = test_client.get(
                f"/api/v1/pre-filter/{analysis_id}",
                headers=self.get_auth_headers()
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == str(analysis_id)
            assert data["proposal_id"] == unique_proposal_id
            assert data["result"] == "pass"
            assert data["confidence"] == 0.85
            assert data["details"] == "Test details"
    
    def test_get_analysis_by_proposal_id(self, test_client: TestClient):
        """Test getting an analysis by proposal ID."""
        # Create a unique proposal ID for this test
        unique_proposal_id = f"test-proposal-{uuid.uuid4()}"
        analysis_id = uuid.uuid4()
        
        # Create a mock analysis object
        mock_analysis = MagicMock()
        mock_analysis.id = analysis_id
        mock_analysis.proposal_id = unique_proposal_id
        mock_analysis.result = "pass"
        mock_analysis.confidence = 0.85
        mock_analysis.details = "Test details"
        mock_analysis.created_at = datetime.now()
        mock_analysis.updated_at = datetime.now()
        
        # Mock the find_analysis_by_proposal_id function
        with patch('app.api.routes.find_analysis_by_proposal_id', return_value=mock_analysis) as mock_find_analysis:
            # Set up the mock response
            mock_find_analysis.return_value = mock_analysis
            
            # Get the analysis by proposal ID
            response = test_client.get(
                f"/api/v1/pre-filter/proposals/{unique_proposal_id}",
                headers=self.get_auth_headers()
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == str(analysis_id)
            assert data["proposal_id"] == unique_proposal_id
            assert data["result"] == "pass"
            assert data["confidence"] == 0.85
            assert data["details"] == "Test details"
    
    def test_get_proposal_analyses(self, test_client: TestClient):
        """Test getting all analyses for a proposal."""
        # Create a unique proposal ID for this test
        unique_proposal_id = f"test-proposal-{uuid.uuid4()}"
        analysis_id = uuid.uuid4()
        
        # Create a mock analysis object
        mock_analysis = MagicMock()
        mock_analysis.id = analysis_id
        mock_analysis.proposal_id = unique_proposal_id
        mock_analysis.result = "pass"
        mock_analysis.confidence = 0.85
        mock_analysis.details = "Test details"
        mock_analysis.created_at = datetime.now()
        mock_analysis.updated_at = datetime.now()
        
        # Mock the find_analyses_by_proposal_id function
        with patch('app.api.routes.find_analyses_by_proposal_id', return_value=[mock_analysis]) as mock_find_analyses:
            # Set up the mock response
            mock_find_analyses.return_value = [mock_analysis]
            
            # Get all analyses for the proposal
            response = test_client.get(
                f"/api/v1/pre-filter/proposal/{unique_proposal_id}",
                headers=self.get_auth_headers()
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 1
            assert data[0]["id"] == str(analysis_id)
            assert data[0]["proposal_id"] == unique_proposal_id
            assert data[0]["result"] == "pass"
            assert data[0]["confidence"] == 0.85
            assert data[0]["details"] == "Test details"
    
    def test_nonexistent_analysis(self, test_client: TestClient):
        """Test getting a nonexistent analysis."""
        # Generate a random UUID
        random_id = uuid.uuid4()
        
        # Mock the get_analysis_by_id function to raise a 404 error
        with patch('app.api.routes.get_analysis_by_id') as mock_get_analysis:
            # Set up the mock to raise an HTTPException
            from fastapi import HTTPException
            mock_get_analysis.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis with ID {random_id} not found"
            )
            
            # Try to get a nonexistent analysis
            response = test_client.get(
                f"/api/v1/pre-filter/{random_id}",
                headers=self.get_auth_headers()
            )
            
            # Check response
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "not found" in response.json()["detail"]
