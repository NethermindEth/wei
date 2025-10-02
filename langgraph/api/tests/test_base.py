"""
Base test class for end-to-end API tests.
"""

from typing import Dict, Any

# Import from conftest.py
from tests.conftest import TEST_API_KEY


class BaseTest:
    """Base test class for all API tests."""
    
    @staticmethod
    def get_auth_headers() -> Dict[str, str]:
        """Get authentication headers."""
        return {"X-API-Key": TEST_API_KEY}
    
    @staticmethod
    def get_test_proposal(proposal_id: str = "test-proposal-1") -> Dict[str, Any]:
        """Get a test proposal for testing."""
        return {
            "content": "This is a test proposal to increase the community treasury allocation for developer grants by 10%.",
            "proposal_id": proposal_id,
            "metadata": {"space": "test-space", "author": "test-author"}
        }
    
    @staticmethod
    def get_test_custom_criteria() -> Dict[str, Any]:
        """Get test custom criteria for evaluation."""
        return {
            "criteria1": "The proposal should clearly state the amount of funds requested.",
            "criteria2": "The proposal should explain how the funds will be used.",
            "criteria3": "The proposal should include a timeline for implementation."
        }
