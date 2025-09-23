#!/usr/bin/env python
# coding: utf-8

"""
Roadmap generator using Perplexity model via OpenRouter API.
This module provides functions to generate implementation roadmaps for proposals.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json

# Load environment variables
load_dotenv()

def generate_roadmap(proposal_text, metadata):
    """
    Generate an implementation roadmap for a proposal using Perplexity/Sonar-Pro model.
    
    Args:
        proposal_text: The text of the proposal
        metadata: Dictionary with proposal metadata
    
    Returns:
        A dictionary containing the roadmap information
    """
    print("Generating implementation roadmap using Perplexity/Sonar-Pro...")
    
    # Initialize the Perplexity model via OpenRouter
    roadmap_llm = ChatOpenAI(
        model="perplexity/sonar-pro",
        api_key=os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Create the system prompt
    system_prompt = """You are a Strategic Planning Agent specializing in blockchain governance proposals.
    Your task is to create a detailed implementation roadmap for the proposal provided.
    
    The roadmap should include:
    1. Key milestones and their dependencies
    2. Timeline estimates (in weeks/months)
    3. Resource requirements
    4. Risk assessment and mitigation strategies
    5. Success metrics and evaluation criteria
    
    Format your response as a structured JSON object with the following keys:
    - milestones: array of milestone objects with name, description, timeline, dependencies
    - resources: object describing required resources (technical, human, financial)
    - risks: array of risk objects with description, impact, probability, mitigation
    - metrics: array of success metrics with description and measurement method
    """
    
    # Create the human message with the proposal and metadata
    human_message = f"""
    Please analyze this proposal and create an implementation roadmap:
    
    PROPOSAL:
    {proposal_text}
    
    METADATA:
    - ID: {metadata.get('id', 'Unknown')}
    - Title: {metadata.get('title', 'Unknown')}
    - Author: {metadata.get('author', 'Unknown')}
    - Protocol: {metadata.get('protocol', 'Unknown')}
    - Category: {metadata.get('category', 'Unknown')}
    
    Provide a comprehensive implementation roadmap that would help stakeholders understand how to execute this proposal.
    """
    
    # Send the messages to the model
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_message)
    ]
    
    # Get the response
    start_time = __import__('time').time()
    response = roadmap_llm.invoke(messages)
    end_time = __import__('time').time()
    latency_ms = int((end_time - start_time) * 1000)
    
    print(f"Roadmap generated in {latency_ms} ms")
    
    # Try to parse the response as JSON
    try:
        # Extract JSON content from the response
        response_text = response.content
        
        # Look for JSON-like structure in the response
        if "```json" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_text = response_text.split("```")[1].strip()
        else:
            json_text = response_text
        
        # Parse the JSON
        roadmap_data = json.loads(json_text)
        return roadmap_data
    except Exception as e:
        print(f"Error parsing roadmap response as JSON: {e}")
        # Return the raw response if JSON parsing fails
        return {"raw_response": response.content}

def format_roadmap_for_display(roadmap_data):
    """
    Format the roadmap data for display in a notebook.
    
    Args:
        roadmap_data: The roadmap data dictionary
    
    Returns:
        A formatted string with HTML for display
    """
    if "raw_response" in roadmap_data:
        # If we couldn't parse as JSON, just return the raw response
        return f"<pre>{roadmap_data['raw_response']}</pre>"
    
    html = "<div style='max-width: 900px;'>"
    
    # Milestones section
    html += "<h3>Implementation Milestones</h3>"
    html += "<table style='width: 100%; border-collapse: collapse;'>"
    html += "<tr style='background-color: #f8f9fa;'>"
    html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Milestone</th>"
    html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Description</th>"
    html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Timeline</th>"
    html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Dependencies</th>"
    html += "</tr>"
    
    for milestone in roadmap_data.get("milestones", []):
        html += "<tr>"
        html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{milestone.get('name', '')}</td>"
        html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{milestone.get('description', '')}</td>"
        html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{milestone.get('timeline', '')}</td>"
        
        # Format dependencies as a list
        dependencies = milestone.get('dependencies', [])
        if dependencies:
            html += "<td style='padding: 8px; border: 1px solid #ddd;'><ul style='margin: 0; padding-left: 20px;'>"
            for dep in dependencies:
                html += f"<li>{dep}</li>"
            html += "</ul></td>"
        else:
            html += "<td style='padding: 8px; border: 1px solid #ddd;'>None</td>"
        
        html += "</tr>"
    
    html += "</table>"
    
    # Resources section
    html += "<h3>Required Resources</h3>"
    resources = roadmap_data.get("resources", {})
    html += "<table style='width: 100%; border-collapse: collapse;'>"
    
    for resource_type, description in resources.items():
        html += "<tr>"
        html += f"<td style='padding: 8px; border: 1px solid #ddd; width: 20%; font-weight: bold;'>{resource_type.title()}</td>"
        html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{description}</td>"
        html += "</tr>"
    
    html += "</table>"
    
    # Risks section
    html += "<h3>Risk Assessment</h3>"
    html += "<table style='width: 100%; border-collapse: collapse;'>"
    html += "<tr style='background-color: #f8f9fa;'>"
    html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Risk</th>"
    html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Impact</th>"
    html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Probability</th>"
    html += "<th style='padding: 8px; text-align: left; border: 1px solid #ddd;'>Mitigation</th>"
    html += "</tr>"
    
    for risk in roadmap_data.get("risks", []):
        html += "<tr>"
        html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{risk.get('description', '')}</td>"
        html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{risk.get('impact', '')}</td>"
        html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{risk.get('probability', '')}</td>"
        html += f"<td style='padding: 8px; border: 1px solid #ddd;'>{risk.get('mitigation', '')}</td>"
        html += "</tr>"
    
    html += "</table>"
    
    # Success metrics section
    html += "<h3>Success Metrics</h3>"
    html += "<ul>"
    
    for metric in roadmap_data.get("metrics", []):
        html += f"<li><strong>{metric.get('description', '')}</strong>: {metric.get('measurement', '')}</li>"
    
    html += "</ul>"
    html += "</div>"
    
    return html

if __name__ == "__main__":
    # Example usage
    example_proposal = """
    # EIP-1234: Ethereum Network Upgrade - Proof of Stake Transition
    
    ## Abstract
    This proposal outlines a comprehensive plan for transitioning the Ethereum network from Proof of Work (PoW) to Proof of Stake (PoS) consensus mechanism.
    
    ## Motivation
    The current PoW consensus mechanism has several limitations including high energy consumption and limited scalability.
    
    ## Specification
    The transition will occur in three phases:
    1. Beacon Chain Deployment
    2. The Merge
    3. Sharding Implementation
    """
    
    example_metadata = {
        "id": "EIP-1234",
        "title": "Ethereum Network Upgrade - Proof of Stake Transition",
        "author": "Vitalik Buterin",
        "protocol": "Ethereum",
        "category": "Core"
    }
    
    roadmap = generate_roadmap(example_proposal, example_metadata)
    print(json.dumps(roadmap, indent=2))
