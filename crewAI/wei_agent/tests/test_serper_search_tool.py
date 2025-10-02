import os
import unittest
from unittest.mock import patch, MagicMock
import json
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

from wei_agent.tools.serper_search_tool import SerperSearchTool


class TestSerperSearchTool(unittest.TestCase):
    """Test cases for the SerperSearchTool."""

    def setUp(self):
        """Set up test environment."""
        self.tool = SerperSearchTool()
        
        # Sample response data
        self.sample_response = {
            "organic": [
                {
                    "title": "Test Result 1",
                    "link": "https://example.com/1",
                    "snippet": "This is a test snippet 1."
                },
                {
                    "title": "Test Result 2",
                    "link": "https://example.com/2",
                    "snippet": "This is a test snippet 2."
                }
            ],
            "knowledgeGraph": {
                "title": "Test Knowledge",
                "type": "Test Type",
                "description": "Test description."
            },
            "relatedSearches": [
                {"query": "related query 1"},
                {"query": "related query 2"}
            ]
        }

    @patch('os.environ.get')
    def test_missing_api_key(self, mock_env_get):
        """Test behavior when API key is missing."""
        mock_env_get.return_value = None
        result = self.tool._run("test query")
        self.assertIn("Error: SERPER_API_KEY environment variable not found", result)

    @patch('os.environ.get')
    @patch('http.client.HTTPSConnection')
    def test_successful_search(self, mock_connection, mock_env_get):
        """Test successful search with mocked response."""
        # Mock environment variable
        mock_env_get.return_value = "fake_api_key"
        
        # Mock HTTP connection
        mock_conn = MagicMock()
        mock_connection.return_value = mock_conn
        
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(self.sample_response).encode('utf-8')
        mock_conn.getresponse.return_value = mock_response
        
        # Execute search
        result = self.tool._run("test query")
        
        # Verify results
        self.assertIn("Organic Results:", result)
        self.assertIn("Test Result 1", result)
        self.assertIn("Test Result 2", result)
        self.assertIn("Knowledge Graph:", result)
        self.assertIn("Test Knowledge", result)
        self.assertIn("Related Searches:", result)
        
        # Verify API call
        mock_conn.request.assert_called_once()
        args, kwargs = mock_conn.request.call_args
        self.assertEqual(args[0], "POST")
        self.assertEqual(args[1], "/search")
        self.assertIn("test query", args[2])
        self.assertEqual(kwargs, {})

    @patch('os.environ.get')
    @patch('http.client.HTTPSConnection')
    def test_exception_handling(self, mock_connection, mock_env_get):
        """Test exception handling during search."""
        # Mock environment variable
        mock_env_get.return_value = "fake_api_key"
        
        # Mock HTTP connection to raise exception
        mock_conn = MagicMock()
        mock_connection.return_value = mock_conn
        mock_conn.request.side_effect = Exception("Test exception")
        
        # Execute search
        result = self.tool._run("test query")
        
        # Verify error message
        self.assertIn("Error performing search:", result)
        self.assertIn("Test exception", result)


if __name__ == '__main__':
    unittest.main()
