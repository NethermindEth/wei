"""
End-to-end tests for cache management endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.test_base import BaseTest


class TestCacheManagement(BaseTest):
    """Test cache management endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_cached_queries(self, async_client: AsyncClient):
        """Test listing cached queries."""
        # Send request to list cached queries
        response = await async_client.get(
            "/api/v1/cache",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the response has the expected structure
        assert "entries" in data
        assert "total" in data
        assert isinstance(data["entries"], list)
        assert isinstance(data["total"], int)
    
    @pytest.mark.asyncio
    async def test_get_cache_stats(self, async_client: AsyncClient):
        """Test getting cache statistics."""
        # Send request to get cache statistics
        response = await async_client.get(
            "/api/v1/cache/stats",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the response has the expected structure
        assert "total_entries" in data
        assert "hit_rate" in data
        assert "miss_rate" in data
        assert "size_bytes" in data
    
    @pytest.mark.asyncio
    async def test_invalidate_cache(self, async_client: AsyncClient):
        """Test invalidating cache entries."""
        # Create request data
        request_data = {
            "keys": ["test_key_1", "test_key_2"]
        }
        
        # Send request to invalidate cache entries
        response = await async_client.post(
            "/api/v1/cache/invalidate",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the response has the expected message
        assert "message" in data
        assert "Invalidated" in data["message"]
    
    @pytest.mark.asyncio
    async def test_refresh_cache(self, async_client: AsyncClient):
        """Test refreshing cache entries."""
        # Create request data
        request_data = {
            "keys": ["test_key_1", "test_key_2"]
        }
        
        # Send request to refresh cache entries
        response = await async_client.post(
            "/api/v1/cache/refresh",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the response has the expected message
        assert "message" in data
        assert "Refreshed" in data["message"]
    
    @pytest.mark.asyncio
    async def test_cleanup_cache(self, async_client: AsyncClient):
        """Test cleaning up cache."""
        # Send request to clean up cache
        response = await async_client.post(
            "/api/v1/cache/cleanup",
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that the response has the expected message
        assert "message" in data
        assert "Cache cleanup" in data["message"]
