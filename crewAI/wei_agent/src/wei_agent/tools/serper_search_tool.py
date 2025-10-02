import os
import json
import http.client
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class SerperSearchInput(BaseModel):
    """Input schema for SerperSearchTool."""
    query: str = Field(..., description="The search query to look up on the internet.")


class SerperSearchTool(BaseTool):
    name: str = "Internet Search"
    description: str = (
        "A tool that searches the internet for current information using the Serper API. "
        "Use this tool when you need to find up-to-date information about topics, "
        "news, events, or any other information that might be available online."
    )
    args_schema: Type[BaseModel] = SerperSearchInput

    def _run(self, query: str) -> str:
        """
        Execute a search query using the Serper API.
        
        Args:
            query: The search query string
            
        Returns:
            The search results as a formatted string
        """
        try:
            # Get API key from environment variables
            api_key = os.environ.get("SERPER_API_KEY")
            if not api_key:
                return "Error: SERPER_API_KEY environment variable not found."
            
            # Set up the connection to Serper API
            conn = http.client.HTTPSConnection("google.serper.dev")
            
            # Prepare the payload
            payload = json.dumps({
                "q": query
            })
            
            # Set headers with API key
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            
            # Make the request
            conn.request("POST", "/search", payload, headers)
            
            # Get the response
            response = conn.getresponse()
            data = response.read()
            
            # Parse the JSON response
            search_results = json.loads(data.decode("utf-8"))
            
            # Format the results
            formatted_results = self._format_results(search_results)
            
            return formatted_results
            
        except Exception as e:
            return f"Error performing search: {str(e)}"
    
    def _format_results(self, results: dict) -> str:
        """
        Format the search results into a readable string.
        
        Args:
            results: The JSON response from Serper API
            
        Returns:
            A formatted string with search results
        """
        formatted_output = "Search Results:\n\n"
        
        # Add organic results if available
        if "organic" in results:
            formatted_output += "Organic Results:\n"
            for i, result in enumerate(results["organic"][:5], 1):  # Limit to top 5 results
                formatted_output += f"{i}. {result.get('title', 'No Title')}\n"
                formatted_output += f"   URL: {result.get('link', 'No Link')}\n"
                formatted_output += f"   Snippet: {result.get('snippet', 'No Snippet')}\n\n"
        
        # Add knowledge graph if available
        if "knowledgeGraph" in results:
            kg = results["knowledgeGraph"]
            formatted_output += "Knowledge Graph:\n"
            formatted_output += f"Title: {kg.get('title', 'No Title')}\n"
            formatted_output += f"Type: {kg.get('type', 'No Type')}\n"
            if "description" in kg:
                formatted_output += f"Description: {kg.get('description')}\n"
            formatted_output += "\n"
        
        # Add related searches if available
        if "relatedSearches" in results:
            formatted_output += "Related Searches:\n"
            for i, search in enumerate(results["relatedSearches"][:5], 1):  # Limit to top 5
                formatted_output += f"{i}. {search.get('query', '')}\n"
        
        return formatted_output
