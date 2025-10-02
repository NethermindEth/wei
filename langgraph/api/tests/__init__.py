"""
Test package for the Wei Agent API.

This package contains end-to-end tests for the Wei Agent API routes.
The tests are designed to validate the functionality of the API without mocking
any dependencies, ensuring that the entire system works as expected in a
real-world scenario.

Test categories:
1. Authentication tests - Verify API key validation
2. Proposal analysis tests - Test proposal analysis endpoints
3. Argument generation tests - Test argument generation for proposals
4. Custom evaluation tests - Test custom evaluation of proposals
5. Related proposals tests - Test searching for related proposals
6. Cache management tests - Test cache-related endpoints
7. Chat functionality tests - Test the chat endpoint
8. Community and roadmap tests - Test community and roadmap endpoints
"""

# Import test fixtures for easy access
from tests.test_base import BaseTest
