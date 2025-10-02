#!/usr/bin/env python
"""
Script to run tests for the Wei Agent API.
"""

import os
import sys
import pytest


def main():
    """Run the tests."""
    # Add the current directory to the path so that the app module can be imported
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Run the tests
    sys.exit(pytest.main(["-v"]))


if __name__ == "__main__":
    main()
