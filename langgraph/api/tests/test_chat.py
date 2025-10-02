"""
End-to-end tests for the chat endpoint.
"""

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.test_base import BaseTest


class TestChat(BaseTest):
    """Test chat functionality."""
    
    @pytest.mark.asyncio
    async def test_chat_basic_question(self, async_client: AsyncClient):
        """Test sending a basic question to the chat endpoint."""
        # Create request data
        request_data = {
            "message": "What is a governance proposal?"
        }
        
        # Send chat request
        response = await async_client.post(
            "/api/v1/chat",
            json=request_data
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that a response was returned
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_chat_proposal_specific_question(self, async_client: AsyncClient):
        """Test sending a proposal-specific question to the chat endpoint."""
        # Create request data
        request_data = {
            "message": "How would you evaluate a proposal that requests 100 ETH for a developer grant program?"
        }
        
        # Send chat request
        response = await async_client.post(
            "/api/v1/chat",
            json=request_data
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that a response was returned
        assert "response" in data
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
    
    @pytest.mark.asyncio
    async def test_chat_empty_message(self, async_client: AsyncClient):
        """Test sending an empty message to the chat endpoint."""
        # Create request data with empty message
        request_data = {
            "message": ""
        }
        
        # Send chat request
        response = await async_client.post(
            "/api/v1/chat",
            json=request_data
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that a response was returned
        assert "response" in data
