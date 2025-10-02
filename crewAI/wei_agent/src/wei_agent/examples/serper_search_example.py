#!/usr/bin/env python
"""
Example script to demonstrate the SerperSearchTool functionality.
This script can be run directly to test the search tool.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the wei_agent package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Load environment variables from .env file
load_dotenv()

from wei_agent.tools import SerperSearchTool


def main():
    """
    Main function to demonstrate the SerperSearchTool.
    """
    # Check if SERPER_API_KEY is set
    if not os.environ.get("SERPER_API_KEY"):
        print("Error: SERPER_API_KEY environment variable not found.")
        print("Please set it in your .env file or export it in your shell.")
        return
    
    # Create an instance of the SerperSearchTool
    search_tool = SerperSearchTool()
    
    # Get search query from command line arguments or use a default
    query = sys.argv[1] if len(sys.argv) > 1 else "Ethereum EIP-4844"
    
    print(f"Searching for: {query}")
    print("-" * 50)
    
    # Execute the search
    results = search_tool._run(query)
    
    # Print the results
    print(results)


if __name__ == "__main__":
    main()
