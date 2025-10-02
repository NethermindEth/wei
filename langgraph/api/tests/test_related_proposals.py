"""
End-to-end tests for related proposals search endpoint.
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.test_base import BaseTest


class TestRelatedProposals(BaseTest):
    """Test related proposals search endpoint."""
    
    @pytest.mark.asyncio
    async def test_search_related_proposals(self, async_client: AsyncClient):
        """Test searching for related proposals."""
        # Send search request
        query = "treasury allocation"
        response = await async_client.get(
            f"/api/v1/related-proposals?query={query}",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that search results were returned
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_search_with_empty_query(self, async_client: AsyncClient):
        """Test searching with an empty query."""
        # Send search request with empty query
        response = await async_client.get(
            "/api/v1/related-proposals",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that search results were returned
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_search_with_specific_query(self, async_client: AsyncClient):
        """Test searching with a specific query."""
        # Send search request with specific query
        query = "developer grants funding"
        response = await async_client.get(
            f"/api/v1/related-proposals?query={query}",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that search results were returned
        assert isinstance(data, list)
