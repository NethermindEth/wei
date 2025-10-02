"""
End-to-end tests for community and roadmap endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.test_base import BaseTest


class TestCommunityRoadmap(BaseTest):
    """Test community and roadmap endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_community_analysis(self, async_client: AsyncClient):
        """Test getting community analysis."""
        # Send request to get community analysis
        response = await async_client.get(
            "/api/v1/community",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the response has the expected message
        assert "message" in data
        assert "Community analysis" in data["message"]
    
    @pytest.mark.asyncio
    async def test_analyze_community(self, async_client: AsyncClient):
        """Test analyzing community."""
        # Send request to analyze community
        response = await async_client.post(
            "/api/v1/community",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the response has the expected message
        assert "message" in data
        assert "Community analysis" in data["message"]
    
    @pytest.mark.asyncio
    async def test_get_cached_roadmap(self, async_client: AsyncClient):
        """Test getting cached roadmap."""
        # Send request to get cached roadmap
        response = await async_client.get(
            "/api/v1/roadmap",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the response has the expected message
        assert "message" in data
        assert "Roadmap" in data["message"]
    
    @pytest.mark.asyncio
    async def test_generate_roadmap(self, async_client: AsyncClient):
        """Test generating roadmap."""
        # Send request to generate roadmap
        response = await async_client.post(
            "/api/v1/roadmap",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the response has the expected message
        assert "message" in data
        assert "Roadmap" in data["message"]
