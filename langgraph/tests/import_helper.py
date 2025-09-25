#!/usr/bin/env python3
"""
Import helper for test files.

This module adds the parent directory to the Python path so that modules from the parent
directory can be imported in test files. It also loads environment variables from the
parent directory's .env file.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
    print(f"Added {parent_dir} to Python path")

# Load environment variables from parent directory's .env file
env_file = Path(parent_dir) / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
    print(f"Loaded environment variables from {env_file}")
else:
    print(f"Warning: .env file not found at {env_file}")
    print("Environment variables may not be properly set.")
    print("Create a .env file in the parent directory with your API keys.")

