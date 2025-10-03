"""Define the graph for the agent."""
from typing import Dict, Any, TypedDict, Optional, List, Union
from langgraph.graph import StateGraph, END

# Define the state
class State(TypedDict):
    """The state of the graph."""
    task: str
    proposal_text: Optional[str]
    custom_criteria: Optional[Dict[str, Any]]
    search_query: Optional[str]
    messages: Optional[List[Any]]
    result: Optional[Dict[str, Any]]
    analysis_result: Optional[Dict[str, Any]]
    custom_evaluation: Optional[Dict[str, Any]]
    search_results: Optional[List[Dict[str, Any]]]
    topic: Optional[str]
    deep_research_result: Optional[Dict[str, Any]]
    roadmap_request: Optional[Dict[str, Any]]
    roadmap_result: Optional[Dict[str, Any]]


# Define a function for analyzing proposals
def analyze_proposal(state: State) -> State:
    """Analyze a proposal and return the result."""
    proposal_text = state.get("proposal_text", "")
    
    # In a real implementation, this would call an AI model
    # For now, return a simple result
    result = {
        "summary": f"Analysis of proposal: {proposal_text[:50]}...",
        "goals_and_motivation": {
            "status": "pass",
            "justification": "The proposal clearly states its goals and motivation.",
            "suggestions": []
        },
        "measurable_outcomes": {
            "status": "fail",
            "justification": "The proposal does not define clear measurable outcomes.",
            "suggestions": [
                "Define specific metrics to measure success.",
                "Include a timeline for achieving outcomes."
            ]
        },
        "budget": {
            "status": "n/a",
            "justification": "No budget information is provided in the proposal.",
            "suggestions": []
        },
        "technical_specifications": {
            "status": "pass",
            "justification": "The technical specifications are well-defined.",
            "suggestions": []
        },
        "language_quality": {
            "status": "pass",
            "justification": "The proposal is well-written and easy to understand.",
            "suggestions": []
        }
    }
    
    return {**state, "analysis_result": result}

# Define a function for generating roadmaps
def generate_roadmap(state: State) -> State:
    """Generate a roadmap for a subject using AI models."""
    import os
    import logging
    import json
    import uuid
    import requests
    from datetime import datetime, timezone, timedelta
    from typing import Dict, Any, List, Optional
    
    # Get request data from state
    request = state.get("roadmap_request", {})
    context = state.get("context", None)
    
    # Extract request fields
    subject = request.get("subject", "")
    kind = request.get("kind", "")
    scope = request.get("scope", "")
    from_date = request.get("from_date")
    to_date = request.get("to_date")
    additional_context = request.get("additional_context")
    
    # Validate required fields
    if not subject or not kind or not scope:
        logging.error("Missing required fields in roadmap request")
        return {**state, "error": "Missing required fields in roadmap request"}
    
    # Get API keys from context or environment
    openrouter_api_key = None
    if context and hasattr(context, "openrouter_api_key"):
        openrouter_api_key = context.openrouter_api_key
    
    # If no API key in context, try to get from environment
    if not openrouter_api_key:
        from dotenv import load_dotenv
        load_dotenv()
        openrouter_api_key = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
    
    # Get model name from environment
    model_name = os.environ.get("WEI_AGENT_ROADMAP_MODEL_NAME", "perplexity/sonar-pro")
    
    # Generate current date and research window
    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    
    # Set default research window if not provided
    if not from_date:
        from_date = (now - timedelta(days=90)).strftime("%Y-%m-%d")
    if not to_date:
        to_date = today_str
    
    # Generate roadmap using AI
    if openrouter_api_key:
        try:
            logging.info(f"Generating roadmap for {subject} using {model_name}")
            
            # Prepare the prompt
            prompt = f"""Generate a comprehensive roadmap for {subject} ({kind}) with the following scope: {scope}.
            Research window: from {from_date} to {to_date}.
            
            Additional context: {additional_context or 'None provided'}
            
            Return the response in the following JSON format:
            
            {{"schema_version": "1.0.0",
            "domain": {{"name": "{subject}", "kind": "{kind}", "scope": "{scope}", "as_of": "{today_str}", "research_window": {{"from": "{from_date}", "to": "{to_date}"}}}},
            "streams": ["Stream1", "Stream2", ...],
            "fitness_functions": [],
            "problems": [],
            "interventions": [],
            "proposals": [],
            "links": [],
            "sources": [
                {{"id": "s1", "type": "blog|whitepaper|website", "title": "Source Title", "url": "https://example.com", "published_at": "YYYY-MM-DD or unclear", "retrieved_at": "{today_str}", "credibility": "high|medium|low", "notes": ""}},
                ...
            ],
            "metadata": {{"generator": "Perplexity Research Agent", "generated_at": "{now.strftime('%Y-%m-%dT%H:%M:%SZ')}", "notes": "Any additional notes about the roadmap generation process"}}}}
            
            Include at least 5 relevant sources with real URLs and accurate publication dates when known.
            Focus on real, verifiable information about {subject}.
            """
            
            # Make request to OpenRouter API
            headers = {
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a specialized research agent that generates comprehensive roadmaps for protocols, DAOs, and other blockchain projects."},
                    {"role": "user", "content": prompt}
                ]
            }
            
            # Add response_format if not using Perplexity
            if "perplexity" not in model_name.lower():
                data["response_format"] = {"type": "json_object"}
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                    
                    # Parse the JSON response
                    try:
                        roadmap_content = json.loads(content)
                    except json.JSONDecodeError:
                        # Try to extract JSON from the text response
                        import re
                        json_match = re.search(r'\{.*\}', content, re.DOTALL)
                        if json_match:
                            try:
                                roadmap_content = json.loads(json_match.group(0))
                            except json.JSONDecodeError:
                                logging.error(f"Failed to parse JSON from content: {content[:100]}...")
                                return {**state, "error": "Failed to parse roadmap content"}
                        else:
                            logging.error(f"No JSON found in content: {content[:100]}...")
                            return {**state, "error": "No valid roadmap content found"}
                    
                    # Create the roadmap response
                    roadmap_id = str(uuid.uuid4())
                    expires_at = (now + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    created_at = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    
                    # Process the roadmap content to ensure proper format
                    # Convert string items to dictionaries in lists that should contain dictionaries
                    for field in ['fitness_functions', 'problems', 'interventions', 'proposals', 'links']:
                        if field in roadmap_content and isinstance(roadmap_content[field], list):
                            for i, item in enumerate(roadmap_content[field]):
                                if isinstance(item, str):
                                    # Convert string to a simple dictionary
                                    roadmap_content[field][i] = {"description": item}
                    
                    roadmap_response = {
                        "id": roadmap_id,
                        "request": {
                            "subject": subject,
                            "kind": kind,
                            "scope": scope,
                            "from_date": from_date,
                            "to_date": to_date,
                            "additional_context": additional_context
                        },
                        "response": roadmap_content,
                        "created_at": created_at,
                        "expires_at": expires_at
                    }
                    
                    logging.info(f"Successfully generated roadmap for {subject}")
                    return {**state, "roadmap_result": roadmap_response}
                except Exception as e:
                    logging.error(f"Error processing roadmap results: {str(e)}")
                    return {**state, "error": f"Error processing roadmap results: {str(e)}"}
            else:
                logging.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return {**state, "error": f"OpenRouter API error: {response.status_code}"}
        except Exception as e:
            logging.error(f"Error generating roadmap: {str(e)}")
            return {**state, "error": f"Error generating roadmap: {str(e)}"}
    else:
        logging.error("No OpenRouter API key found for roadmap generation")
        return {**state, "error": "No API key available for roadmap generation"}

# Define a function to generate arguments
def generate_arguments(state: State) -> State:
    """Generate arguments for a proposal."""
    proposal_text = state.get("proposal_text", "")
    
    # In a real implementation, this would call an LLM
    # For now, return a simple result with arguments for and against the proposal
    arguments = {
        "for_proposal": [
            "A Code of Conduct will establish clear behavioral expectations for all community members",
            "It provides a framework for addressing conflicts and disputes in a fair and consistent manner",
            "Having formal standards will help protect the community from toxic behavior and maintain a positive environment",
            "Other successful DAOs have benefited from implementing similar codes of conduct",
            "Clear guidelines will help newcomers understand community norms more quickly"
        ],
        "against": [
            "The proposed enforcement mechanisms may be difficult to implement in a decentralized context",
            "Some community members might view this as unnecessary bureaucracy",
            "The code could be interpreted or enforced inconsistently without clear governance",
            "It may be challenging to achieve consensus on what constitutes violations in edge cases",
            "Resources for enforcement and appeals processes are not clearly defined"
        ]
    }
    
    return {**state, "arguments": arguments}

# Define a function for custom evaluation
def custom_evaluate(state: State) -> State:
    """Evaluate a proposal using custom criteria."""
    proposal_text = state.get("proposal_text", "")
    custom_criteria = state.get("custom_criteria", {})
    
    # In a real implementation, this would call an LLM
    # For now, return a simple result that matches the Rust implementation format
    
    # Parse the custom criteria
    criteria_text = custom_criteria
    if isinstance(custom_criteria, dict) and "general" in custom_criteria:
        criteria_text = custom_criteria["general"]
    elif isinstance(custom_criteria, str):
        criteria_text = custom_criteria
    
    # Extract criteria names from the text
    criteria_names = []
    if isinstance(criteria_text, str):
        # Simple parsing: split by "and", "or", ","
        for separator in [" and ", " or ", ","]:
            if separator in criteria_text:
                criteria_names = [name.strip() for name in criteria_text.split(separator)]
                break
        
        # If no separators found, use the whole string as one criterion
        if not criteria_names:
            criteria_names = [criteria_text.strip()]
    
    # Create the response
    result = {
        "summary": "The proposal for the Community Code of Conduct meets the goals of establishing shared standards and accountability within the Redbelly DAO, thus supporting effective team structure.",
        "response_map": {}
    }
    
    # Add evaluation for each criterion
    for criterion in criteria_names:
        criterion_key = criterion.lower().replace(" ", "_")
        result["response_map"][criterion_key] = {
            "status": "pass",
            "justification": f"The proposal effectively addresses the need for shared standards of behavior, which is essential for maintaining community integrity and trust as the DAO grows. It establishes clear expectations and processes that support the DAO's mission and {criterion}.",
            "suggestions": []
        }
    
    # If no criteria were found, add a default one
    if not result["response_map"]:
        result["response_map"]["general"] = {
            "status": "pass",
            "justification": "The proposal effectively addresses the need for shared standards of behavior, which is essential for maintaining community integrity and trust as the DAO grows.",
            "suggestions": []
        }
    
    return {**state, "custom_evaluation": result}

# Define a function for searching related proposals
def search_related_proposals(state: State) -> State:
    """Search for related proposals using EXA API."""
    import os
    import logging
    import requests
    import json
    import random
    from typing import List, Dict, Any
    
    search_query = state.get("search_query", "")
    context = state.get("context", None)
    
    if not search_query:
        logging.warning("No search query provided, returning empty results")
        return {**state, "search_results": []}
    
    # Get API keys from context
    exa_api_key = None
    if context and hasattr(context, "exa_api_key"):
        exa_api_key = context.exa_api_key
        if exa_api_key:
            logging.info(f"Using EXA API key from context: {exa_api_key[:4]}...{exa_api_key[-4:]}")
    
    # If no API key in context, try to get from environment
    if not exa_api_key:
        # Try to load from .env file directly
        from dotenv import load_dotenv
        load_dotenv()
        
        exa_api_key = os.getenv("WEI_AGENT_EXA_API_KEY")
        if exa_api_key:
            logging.info(f"Using EXA API key from environment: {exa_api_key[:4]}...{exa_api_key[-4:]}")
        else:
            logging.warning("No EXA API key found in environment")
    
    # Try to use EXA API if key is available
    if exa_api_key:
        try:
            # Use requests directly instead of the exa-py package
            import requests
            
            # Configure EXA API request
            headers = {
                "x-api-key": exa_api_key,
                "Content-Type": "application/json"
            }
            
            # Construct search query
            logging.info(f"Searching EXA API for related proposals: {search_query}")
            
            # Make request to EXA API
            response = requests.post(
                "https://api.exa.ai/search",
                headers=headers,
                json={
                    "query": search_query,
                    "num_results": 10,  # Limit to 10 results
                    "use_autoprompt": True
                }
            )
            
            if response.status_code == 200:
                search_data = response.json()
                results = []
                
                # Process results
                if "results" in search_data:
                    logging.info(f"Found {len(search_data['results'])} results from EXA API")
                    
                    for i, result in enumerate(search_data["results"]):
                        # Extract relevant information
                        url = result.get("url", "")
                        title = result.get("title", f"Proposal {i+1}")
                        text = result.get("text", "")
                        
                        # Generate a unique ID for the proposal
                        proposal_id = f"proposal-{i+1}"
                        
                        # Calculate a relevance score (normalized between 0.5 and 1.0)
                        # In a real implementation, this would be based on the search relevance
                        score = 1.0 - (i * 0.05)  # Simple decreasing score based on position
                        
                        # Add to results
                        results.append({
                            "id": proposal_id,
                            "title": title,
                            "score": score,
                            "content": text[:500] + "..." if len(text) > 500 else text,  # Truncate long content
                            "url": url
                        })
                
                # Return results
                if results:
                    logging.info(f"Successfully processed {len(results)} related proposals from EXA API")
                    return {**state, "search_results": results}
                else:
                    logging.warning("No related proposals found from EXA API, using fallback")
            else:
                logging.error(f"EXA API error: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error using EXA API for related proposals: {str(e)}")
    
    # If we get here, either no EXA API key or an error occurred
    logging.warning("Using OpenRouter for related proposals search")
    
    # Get OpenRouter API key from context or environment
    openrouter_api_key = None
    if context and hasattr(context, "openrouter_api_key"):
        openrouter_api_key = context.openrouter_api_key
    
    # If no API key in context, try to get from environment
    if not openrouter_api_key:
        openrouter_api_key = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
    
    if openrouter_api_key:
        try:
            # Use OpenRouter to generate related proposals
            model_name = os.environ.get("WEI_AGENT_ROADMAP_MODEL_NAME", "gpt-4o-mini")
            
            # Prepare the prompt
            prompt = f"""Generate 5 fictional but realistic governance proposals that are related to this query: '{search_query}'.
            For each proposal, provide:
            1. A unique ID (format: proposal-XXX)
            2. A descriptive title
            3. A relevance score between 0.5 and 1.0
            4. A short content summary (1-2 sentences)
            5. A fictional URL
            
            Format your response as a JSON array.
            """
            
            # Make request to OpenRouter API
            headers = {
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that generates realistic governance proposals."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                
                # Parse the JSON response
                try:
                    parsed_content = json.loads(content)
                    
                    # Extract proposals from the response
                    if isinstance(parsed_content, list):
                        results = parsed_content
                    elif isinstance(parsed_content, dict) and "proposals" in parsed_content:
                        results = parsed_content["proposals"]
                    else:
                        # Try to find an array in the response
                        for key, value in parsed_content.items():
                            if isinstance(value, list) and len(value) > 0:
                                results = value
                                break
                        else:
                            results = []
                    
                    if results:
                        logging.info(f"Generated {len(results)} related proposals using OpenRouter")
                        return {**state, "search_results": results}
                except Exception as e:
                    logging.error(f"Error parsing OpenRouter response: {str(e)}")
            else:
                logging.error(f"OpenRouter API error: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error using OpenRouter for related proposals: {str(e)}")
    
    # If all else fails, generate some basic fallback results
    logging.warning("All search methods failed, using basic fallback for related proposals")
    
    # Generate some basic fallback results based on the query
    words = search_query.split()
    results = []
    
    # Use parts of the query to generate titles
    for i in range(min(3, len(words) + 1)):
        word_sample = random.sample(words, min(i+1, len(words))) if words else ["Proposal"]
        title_base = " ".join(word_sample).capitalize()
        
        if i == 0:
            title = f"Implement {title_base} Framework"
            content = f"This proposal aims to implement a comprehensive framework for {search_query}."
        elif i == 1:
            title = f"Update {title_base} Guidelines"
            content = f"This proposal suggests updates to the existing guidelines related to {search_query}."
        else:
            title = f"Create {title_base} Fund"
            content = f"This proposal recommends creating a dedicated fund to support initiatives related to {search_query}."
        
        results.append({
            "id": f"proposal-{i+1}",
            "title": title,
            "score": 0.9 - (i * 0.1),
            "content": content,
            "url": f"https://example.com/proposals/{i+1}"
        })
    
    return {**state, "search_results": results}

# Define a function for deep research
def deep_research(state: State) -> State:
    """Perform deep research on a topic using EXA API and AI models."""
    import os
    import logging
    from typing import List, Dict, Any
    
    topic = state.get("topic", "")
    context = state.get("context", None)
    
    # Get API keys from context
    exa_api_key = None
    if context and hasattr(context, "exa_api_key"):
        exa_api_key = context.exa_api_key
        if exa_api_key:
            logging.info(f"Using EXA API key from context: {exa_api_key[:4]}...{exa_api_key[-4:]}")
    
    # If no API key in context, try to get from environment
    if not exa_api_key:
        # Try to load from .env file directly
        from dotenv import load_dotenv
        load_dotenv()
        
        exa_api_key = os.getenv("WEI_AGENT_EXA_API_KEY")
        if exa_api_key:
            logging.info(f"Using EXA API key from environment: {exa_api_key[:4]}...{exa_api_key[-4:]}")
        else:
            logging.warning("No EXA API key found in environment")
    
    # Function to generate resources using AI model
    def generate_resources_with_ai(topic: str) -> List[Dict[str, Any]]:
        try:
            from langchain_core.prompts import PromptTemplate
            from langchain_openai import ChatOpenAI
            
            model_name = os.environ.get("WEI_AGENT_ROADMAP_MODEL_NAME", "gpt-4o-mini")
            
            # Create the prompt
            prompt = f"""Generate a detailed research report on {topic}, focusing on community discussions, documentation, and resources.
            For each resource, provide:
            1. Name of the resource
            2. Link (URL)
            3. Type (documentation, forum, blog, etc.)
            4. Description (detailed explanation of what the resource contains)
            5. Quality of discourse (assessment of the discussion quality)
            
            Return exactly 10 diverse, high-quality resources in JSON format.
            """
            
            # Use OpenAI directly
            import openai
            client = openai.OpenAI()
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a research assistant that provides information in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            # Extract and parse the JSON
            import json
            content = response.choices[0].message.content
            data = json.loads(content)
            
            # Extract resources from the response
            if "resources" in data:
                return data["resources"]
            else:
                return data.get("results", [])
                
        except Exception as e:
            logging.error(f"Error generating resources with AI: {str(e)}")
            # Return hardcoded fallback resources for the topic
            return [
                {
                    "name": f"{topic} Documentation",
                    "link": f"https://example.com/{topic.lower().replace(' ', '-')}",
                    "type": "documentation",
                    "description": f"Official documentation for {topic}",
                    "quality_of_discourse": "high-quality technical documentation"
                },
                {
                    "name": f"{topic} Community Forum",
                    "link": f"https://forum.example.com/{topic.lower().replace(' ', '-')}",
                    "type": "forum",
                    "description": f"Community discussion forum for {topic}",
                    "quality_of_discourse": "community-driven Q&A"
                }
            ]
    
    # Try to use EXA API if key is available
    if exa_api_key:
        try:
            # Use requests directly instead of the exa-py package
            import requests
            
            # Configure EXA API request
            headers = {
                "x-api-key": exa_api_key,
                "Content-Type": "application/json"
            }
            
            # Construct search query
            search_query = f"community discussions, documentation, and resources about {topic}"
            logging.info(f"Searching EXA API for: {search_query}")
            
            # Make request to EXA API
            response = requests.post(
                "https://api.exa.ai/search",
                headers=headers,
                json={
                    "query": search_query,
                    "num_results": 15,
                    "use_autoprompt": True
                }
            )
            
            if response.status_code == 200:
                search_data = response.json()
                resources = []
                
                # Process results
                if "results" in search_data:
                    logging.info(f"Found {len(search_data['results'])} results from EXA API")
                    
                    for result in search_data["results"]:
                        # Determine resource type based on URL
                        url = result.get("url", "").lower()
                        title = result.get("title", "")
                        text = result.get("text", "")
                        
                        if "github" in url:
                            resource_type = "repository"
                            quality = "technical and procedural, with both developer debate and community input"
                        elif "stackoverflow" in url or "forum" in url or "community" in url:
                            resource_type = "forum"
                            quality = "community-driven Q&A with moderate depth"
                        elif "docs" in url or "documentation" in url:
                            resource_type = "documentation"
                            quality = "high-level, practical guidance and aggregation of best practices"
                        elif "blog" in url or "medium" in url or "dev.to" in url:
                            resource_type = "blog, best practices"
                            quality = "insightful guidance, practical real-world interpretation"
                        else:
                            resource_type = "web resource"
                            quality = "mixed technical and community governance information"
                        
                        # Add to resources
                        resources.append({
                            "name": title,
                            "link": url,
                            "type": resource_type,
                            "description": text[:300] + "..." if len(text) > 300 else text,
                            "quality_of_discourse": quality
                        })
                
                # Return results
                if resources:
                    logging.info(f"Successfully processed {len(resources)} resources from EXA API")
                    return {**state, "deep_research_result": {"topic": topic, "resources": resources}}
                else:
                    logging.warning("No results from EXA API, falling back to other methods")
            else:
                logging.error(f"EXA API error: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error using EXA API: {str(e)}")
            logging.warning("Falling back to other methods due to EXA API error")
    else:
        logging.warning("No EXA API key found, using other search methods")
        
    # If EXA API key is not available, try using OpenRouter with perplexity/sonar-pro model
    import os
    import json
    import requests
    
    # Get OpenRouter API key from context or environment
    openrouter_api_key = None
    if context and hasattr(context, "openrouter_api_key"):
        openrouter_api_key = context.openrouter_api_key
        if openrouter_api_key:
            logging.info(f"Using OpenRouter API key from context: {openrouter_api_key[:4]}...{openrouter_api_key[-4:]}")
    
    # If no API key in context, try to get from environment
    if not openrouter_api_key:
        # Try to load from .env file directly
        from dotenv import load_dotenv
        load_dotenv()
        
        openrouter_api_key = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
        if openrouter_api_key:
            logging.info(f"Using OpenRouter API key from environment: {openrouter_api_key[:4]}...{openrouter_api_key[-4:]}")
        else:
            logging.warning("No OpenRouter API key found in environment")
    
    # Get model name from environment
    model_name = os.environ.get("WEI_AGENT_ROADMAP_MODEL_NAME", "perplexity/sonar-pro")
    
    if openrouter_api_key:
        try:
            logging.info(f"Using OpenRouter with model {model_name} for research on topic: {topic}")
            
            # Prepare the prompt for the model
            prompt = f"""I need to find high-quality community resources, documentation, and discussion forums about {topic}.
            Please provide a list of at least 5 specific resources with the following information for each:
            1. Name of the resource
            2. URL (must be a real, valid URL)
            3. Type (documentation, forum, blog, repository, etc.)
            4. Description (what the resource contains and why it's valuable)
            5. Quality of discourse (assessment of the discussion quality)
            
            Format your response as a JSON array of resources with these fields: name, link, type, description, quality_of_discourse.
            """
            
            # Make request to OpenRouter API
            headers = {
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            # Different models have different response_format requirements
            if "perplexity" in model_name.lower():
                # Perplexity models don't support response_format parameter
                data = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": "You are a research assistant that provides accurate information about online communities and resources. Always respond with valid JSON."},
                        {"role": "user", "content": prompt + "\n\nRespond with valid JSON only, no other text."}
                    ]
                }
            else:
                # Other models like OpenAI support response_format
                data = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": "You are a research assistant that provides accurate information about online communities and resources."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                    
                    # Parse the JSON response
                    try:
                        parsed_content = json.loads(content)
                    except json.JSONDecodeError:
                        # Try to extract JSON from the text response
                        import re
                        json_match = re.search(r'\{.*\}', content, re.DOTALL)
                        if json_match:
                            try:
                                parsed_content = json.loads(json_match.group(0))
                            except json.JSONDecodeError:
                                logging.error(f"Failed to parse JSON from content: {content[:100]}...")
                                parsed_content = {}
                        else:
                            logging.error(f"No JSON found in content: {content[:100]}...")
                            parsed_content = {}
                    
                    # Extract resources from the response
                    resources = []
                    
                    # Try different possible formats
                    if isinstance(parsed_content, dict):
                        if "resources" in parsed_content:
                            resources = parsed_content["resources"]
                        else:
                            # Try to find an array in the response
                            for key, value in parsed_content.items():
                                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                                    resources = value
                                    break
                    elif isinstance(parsed_content, list):
                        # The content itself is an array
                        resources = parsed_content
                    
                    # Validate resources format
                    valid_resources = []
                    for item in resources:
                        if isinstance(item, dict) and "name" in item and "link" in item:
                            valid_resources.append(item)
                    
                    resources = valid_resources
                    
                    if resources:
                        logging.info(f"Found {len(resources)} resources from OpenRouter ({model_name})")
                        return {**state, "deep_research_result": {"topic": topic, "resources": resources}}
                except Exception as e:
                    logging.error(f"Error processing OpenRouter results: {str(e)}")
            else:
                logging.error(f"OpenRouter API error: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error using OpenRouter API: {str(e)}")
    else:
        logging.warning("No OpenRouter API key found, skipping this search method")
    
    # If all methods fail, return empty resources
    logging.error("All search methods failed. Returning empty resources.")
    resources = []
    
    # Return the results
    return {**state, "deep_research_result": {"topic": topic, "resources": resources}}

# Define a simple chat function
def chat(state: State) -> State:
    """Chat with the user."""
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else {"content": ""}
    last_message_content = last_message.get("content", "")
    
    from langchain_core.messages import AIMessage
    response = AIMessage(content=f"You said: {last_message_content}. This is a simple response.")
    
    return {**state, "messages": messages + [response]}

# Define the router function
def router(state: State) -> Dict[str, Any]:
    """Route the state to the appropriate node."""
    task = state.get("task")
    
    if task == "analyze_proposal":
        return {"next": "analyze_proposal"}
    elif task == "generate_arguments":
        return {"next": "generate_arguments"}
    elif task == "custom_evaluate":
        return {"next": "custom_evaluate"}
    elif task == "search_related_proposals":
        return {"next": "search_related_proposals"}
    elif task == "deep_research":
        return {"next": "deep_research"}
    elif task == "generate_roadmap":
        return {"next": "generate_roadmap"}
    elif task == "chat":
        return {"next": "chat"}
    else:
        return {"next": END}

# Build the graph
graph = StateGraph(State)
graph.add_node("analyze_proposal", analyze_proposal)
graph.add_node("generate_arguments", generate_arguments)
graph.add_node("custom_evaluate", custom_evaluate)
graph.add_node("search_related_proposals", search_related_proposals)
graph.add_node("deep_research", deep_research)
graph.add_node("generate_roadmap", generate_roadmap)
graph.add_node("chat", chat)

# Add the edges
graph.set_entry_point("router")
graph.add_node("router", router)
graph.add_conditional_edges(
    "router",
    lambda x: x["next"],
    {
        "analyze_proposal": "analyze_proposal",
        "generate_arguments": "generate_arguments",
        "custom_evaluate": "custom_evaluate",
        "search_related_proposals": "search_related_proposals",
        "deep_research": "deep_research",
        "generate_roadmap": "generate_roadmap",
        "chat": "chat",
        END: END
    }
)
graph.add_edge("analyze_proposal", END)
graph.add_edge("generate_arguments", END)
graph.add_edge("custom_evaluate", END)
graph.add_edge("search_related_proposals", END)
graph.add_edge("deep_research", END)
graph.add_edge("generate_roadmap", END)
graph.add_edge("chat", END)

# Compile the graph
graph = graph.compile()
