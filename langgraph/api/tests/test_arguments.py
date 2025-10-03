"""
End-to-end tests for proposal argument generation endpoints.
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.test_base import BaseTest


class TestArgumentGeneration(BaseTest):
    """Test argument generation endpoints."""
    
    @pytest.mark.asyncio
    async def test_generate_arguments(self, async_client: AsyncClient):
        """Test generating arguments for a proposal."""
        # Create request data
        request_data = {
            "description": self.get_test_proposal()["description"],
            "proposal_id": "test-proposal-args",
            "max_arguments": 3
        }
        
        # Send request to generate arguments
        response = await async_client.post(
            "/api/v1/pre-filter/arguments",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that arguments were generated
        assert "arguments" in data
        assert "from_cache" in data
        arguments = data["arguments"]
        assert "for_proposal" in arguments
        assert "against" in arguments
        assert isinstance(arguments["for_proposal"], list)
        assert isinstance(arguments["against"], list)
        
        # Check that we have at least one argument on each side
        assert len(arguments["for_proposal"]) >= 1
        assert len(arguments["against"]) >= 1
    
    @pytest.mark.asyncio
    async def test_generate_arguments_with_empty_content(self, async_client: AsyncClient):
        """Test generating arguments with empty content."""
        # Create request data with empty description
        request_data = {
            "description": "",
            "proposal_id": "test-proposal-empty",
            "max_arguments": 3
        }
        
        # Send request to generate arguments
        response = await async_client.post(
            "/api/v1/pre-filter/arguments",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # Check response - should still work but might have fallback messages
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that arguments structure is present
        assert "arguments" in data
        assert "from_cache" in data
        arguments = data["arguments"]
        assert "for_proposal" in arguments
        assert "against" in arguments
        assert isinstance(arguments["for_proposal"], list)
        assert isinstance(arguments["against"], list)
    
    @pytest.mark.asyncio
    async def test_generate_arguments_with_max_arguments(self, async_client: AsyncClient):
        """Test generating arguments with maximum number specified."""
        # Create request data with max_arguments set to 1
        request_data = {
            "description": self.get_test_proposal()["description"],
            "proposal_id": "test-proposal-max-args",
            "max_arguments": 1
        }
        
        # Send request to generate arguments
        response = await async_client.post(
            "/api/v1/pre-filter/arguments",
            json=request_data,
            headers=self.get_auth_headers()
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that arguments were generated
        assert "arguments" in data
        assert "from_cache" in data
        arguments = data["arguments"]
        assert "for_proposal" in arguments
        assert "against" in arguments
        assert isinstance(arguments["for_proposal"], list)
        assert isinstance(arguments["against"], list)
        
        # Check that we have at most max_arguments on each side
        # Note: We can't guarantee exactly 1 because the implementation might have fallbacks
        assert len(arguments["for_proposal"]) <= 1
        assert len(arguments["against"]) <= 1
