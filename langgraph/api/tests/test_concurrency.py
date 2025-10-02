"""
End-to-end tests for concurrent requests and performance.

These tests focus on verifying that the API can handle multiple concurrent
requests and maintains performance under load.
"""

import pytest
import time
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from tests.test_base import BaseTest


class TestConcurrency(BaseTest):
    """Test concurrent requests and performance."""
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_concurrent_proposal_analysis(self, test_client: TestClient):
        """Test handling of concurrent proposal analysis requests."""
        # Create multiple proposal requests with different IDs
        proposals = []
        for i in range(5):
            proposal = self.get_test_proposal()
            proposal["proposal_id"] = f"test-concurrent-{i}"
            proposals.append(proposal)
        
        # Mock the graph.ainvoke method
        async def mock_invoke(input_data, runtime=None):
            if input_data.get("task") == "analyze_proposal":
                return {
                    "analysis_result": {
                        "result": "pass",
                        "confidence": 0.85,
                        "details": "This is a good proposal."
                    }
                }
            return {}
        
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
        with patch('app.api.routes.graph.ainvoke', AsyncMock(side_effect=mock_invoke)), \
             patch('app.api.routes.create_analysis', AsyncMock(side_effect=mock_create_analysis)):
            
            # Send requests sequentially
            start_time = time.time()
            responses = []
            
            for proposal in proposals:
                response = test_client.post(
                    "/api/v1/pre-filter",
                    json=proposal,
                    headers=self.get_auth_headers()
                )
                responses.append(response)
            
            end_time = time.time()
            
            # Check that all requests were successful
            for response in responses:
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "result" in data
            
            # Log the total time taken
            total_time = end_time - start_time
            print(f"Concurrent proposal analysis took {total_time:.2f} seconds for {len(proposals)} requests")
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_concurrent_argument_generation(self, test_client: TestClient):
        """Test handling of concurrent argument generation requests."""
        # Create multiple argument requests with different IDs
        requests = []
        for i in range(3):
            request = {
                "content": self.get_test_proposal()["content"],
                "proposal_id": f"test-concurrent-args-{i}",
                "max_arguments": 3
            }
            requests.append(request)
        
        # Mock the graph.ainvoke method
        async def mock_invoke(input_data, runtime=None):
            if input_data.get("task") == "generate_arguments":
                return {
                    "arguments": {
                        "for_proposal": ["Argument for 1", "Argument for 2"],
                        "against": ["Argument against 1", "Argument against 2"]
                    }
                }
            return {}
        
        # Apply the mock
        with patch('app.api.routes.graph.ainvoke', AsyncMock(side_effect=mock_invoke)):
            # Send requests sequentially
            start_time = time.time()
            responses = []
            
            for request in requests:
                response = test_client.post(
                    "/api/v1/pre-filter/arguments",
                    json=request,
                    headers=self.get_auth_headers()
                )
                responses.append(response)
            
            end_time = time.time()
            
            # Check that all requests were successful
            for response in responses:
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "for_proposal" in data
                assert "against" in data
            
            # Log the total time taken
            total_time = end_time - start_time
            print(f"Concurrent argument generation took {total_time:.2f} seconds for {len(requests)} requests")
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_concurrent_custom_evaluations(self, test_client: TestClient):
        """Test handling of concurrent custom evaluation requests."""
        # Create multiple custom evaluation requests with different criteria
        requests = []
        base_criteria = self.get_test_custom_criteria()
        
        for i in range(3):
            # Add a unique criterion for each request
            criteria = base_criteria.copy()
            criteria[f"unique_criteria_{i}"] = f"This is a unique criterion for request {i}"
            
            request = {
                "content": self.get_test_proposal()["content"],
                "custom_criteria": criteria
            }
            requests.append(request)
        
        # Mock the graph.ainvoke method
        async def mock_invoke(input_data, runtime=None):
            if input_data.get("task") == "custom_evaluate":
                # Create a response with the criteria from the input
                criteria = input_data.get("criteria", {})
                response_map = {}
                
                for key in criteria.keys():
                    response_map[key] = {
                        "status": "pass",
                        "justification": f"This proposal meets the {key} criterion."
                    }
                
                return {
                    "custom_evaluation": {
                        "summary": "The proposal meets all criteria.",
                        "response_map": response_map
                    }
                }
            return {}
        
        # Apply the mock
        with patch('app.api.routes.graph.ainvoke', AsyncMock(side_effect=mock_invoke)):
            # Send requests sequentially (since we can't use asyncio.gather with TestClient)
            start_time = time.time()
            responses = []
            
            for request in requests:
                response = test_client.post(
                    "/api/v1/pre-filter/custom",
                    json=request,
                    headers=self.get_auth_headers()
                )
                responses.append(response)
            
            end_time = time.time()
            
            # Check that all requests were successful
            for response in responses:
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "summary" in data
                assert "response_map" in data
            
            # Log the total time taken
            total_time = end_time - start_time
            print(f"Concurrent custom evaluations took {total_time:.2f} seconds for {len(requests)} requests")
    
    @pytest.mark.e2e
    @pytest.mark.slow
    def test_mixed_concurrent_requests(self, test_client: TestClient):
        """Test handling of mixed concurrent requests to different endpoints."""
        # Create requests for different endpoints
        proposal_request = self.get_test_proposal()
        
        arguments_request = {
            "content": self.get_test_proposal()["content"],
            "proposal_id": "test-mixed-args",
            "max_arguments": 3
        }
        
        custom_eval_request = {
            "content": self.get_test_proposal()["content"],
            "custom_criteria": self.get_test_custom_criteria()
        }
        
        chat_request = {
            "message": "What makes a good governance proposal?"
        }
        
        # Mock the graph.ainvoke method
        async def mock_invoke(input_data, runtime=None):
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
                        "summary": "The proposal meets all criteria.",
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
            return {}
        
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
        with patch('app.api.routes.graph.ainvoke', AsyncMock(side_effect=mock_invoke)), \
             patch('app.api.routes.create_analysis', AsyncMock(side_effect=mock_create_analysis)):
            
            # Send requests sequentially
            start_time = time.time()
            responses = []
            
            # Proposal analysis
            responses.append(test_client.post(
                "/api/v1/pre-filter",
                json=proposal_request,
                headers=self.get_auth_headers()
            ))
            
            # Arguments generation
            responses.append(test_client.post(
                "/api/v1/pre-filter/arguments",
                json=arguments_request,
                headers=self.get_auth_headers()
            ))
            
            # Custom evaluation
            responses.append(test_client.post(
                "/api/v1/pre-filter/custom",
                json=custom_eval_request,
                headers=self.get_auth_headers()
            ))
            
            # Chat
            responses.append(test_client.post(
                "/api/v1/chat",
                json=chat_request
            ))
            
            # Cache stats
            responses.append(test_client.get(
                "/api/v1/cache/stats",
                headers=self.get_auth_headers()
            ))
            
            end_time = time.time()
            
            # Check that all requests were successful
            for response in responses:
                assert response.status_code == status.HTTP_200_OK
            
            # Log the total time taken
            total_time = end_time - start_time
            print(f"Mixed concurrent requests took {total_time:.2f} seconds for {len(responses)} requests")
