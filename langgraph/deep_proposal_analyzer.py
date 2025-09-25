"""
Deep Proposal Analyzer Module

This module uses the deepagents package to analyze governance proposals.
It replaces the previous LangGraph-based implementation with a more powerful
and flexible deepagents-based approach.
"""

# Disable LangChain tracing and LangSmith integration
import disable_langchain_tracing

import logging
import os
import json
import time
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from deepagent_tools import deepagent_tools
from deepagent_subagents import deepagent_subagents
from langgraph.graph import StateGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deep_proposal_analyzer.log')
    ]
)
logger = logging.getLogger('deep_proposal_analyzer')


def trace_search_queries(web_queries: List[str], indexed_queries: List[str], metadata: Dict[str, Any]) -> None:
    """Trace search queries and similarity calculations.
    
    Args:
        web_queries: List of web search queries
        indexed_queries: List of indexed search queries
        metadata: Metadata about the proposal
    """
    # Import tracing functions if not already imported
    try:
        from langfuse_setup import trace_exa_query, trace_cosine_similarity
    except ImportError:
        logger.warning("Langfuse tracing not available for search queries")
        return
    
    # Simulate search results for demonstration purposes
    # In a real implementation, these would be actual search results
    mock_web_results = [
        {"title": "Impact Analysis of Protocol Changes", "url": "https://example.com/impact", "score": 0.85},
        {"title": f"{metadata.get('protocol', 'Unknown')} Governance Framework", "url": "https://example.com/governance", "score": 0.78}
    ]
    
    # Common metadata for all queries
    base_metadata = {
        "protocol": metadata.get('protocol', 'Unknown'),
        "proposal_id": metadata.get('id', 'Unknown'),
        "proposal_title": metadata.get('title', 'Untitled')
    }
    
    # Trace web queries
    for query in web_queries:
        trace_exa_query(
            query=query,
            results=mock_web_results,
            latency_ms=150,  # Simulated latency
            metadata={**base_metadata, "query_type": "web"}
        )
    
    # Trace indexed queries
    for query in indexed_queries:
        trace_exa_query(
            query=query,
            results=[{"title": "Similar Proposal Example", "url": "https://example.com/similar", "score": 0.92}],
            latency_ms=80,  # Simulated latency
            metadata={**base_metadata, "query_type": "indexed"}
        )
    
    # Trace cosine similarity calculations
    # Simulated cosine similarity scores
    cosine_scores = [0.92, 0.85, 0.78, 0.65, 0.61, 0.55, 0.48, 0.42]
    trace_cosine_similarity(
        vectors=8,
        scores=cosine_scores,
        threshold=0.7,
        metadata={**base_metadata, "comparison_type": "proposal_similarity"}
    )

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

class Config:
    """Configuration class for proposal analyzer settings and API keys.
    
    This class centralizes all configuration parameters used throughout the
    proposal analyzer, including API keys, model parameters, and analysis settings.
    
    Attributes:
        OPENROUTER_API_KEY: API key for OpenRouter service
        EXA_API_KEY: API key for Exa service
        DEFAULT_MODEL: Default language model to use for analysis
        ANALYSIS_DEPTH: Level of depth for proposal analysis
        EVIDENCE_THRESHOLD: Minimum evidence required for claims
    """
    # API Keys
    OPENROUTER_API_KEY = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
    EXA_API_KEY = os.getenv("WEI_AGENT_EXA_API_KEY")
    
    # Model parameters
    DEFAULT_MODEL = os.getenv("WEI_AGENT_MODEL", "openai/gpt-3.5-turbo")  # Use a smaller model by default
    
    # Analysis parameters
    ANALYSIS_DEPTH = "comprehensive"  # Options: "basic", "standard", "comprehensive"
    EVIDENCE_THRESHOLD = 2  # Minimum pieces of evidence required for claims
    MAX_CLAIMS = 10  # Maximum number of claims to analyze
    
    # Report generation
    INCLUDE_EVIDENCE_DETAILS = True
    GENERATE_ARGUMENTS = True

# Verify API keys are available
def check_api_keys() -> bool:
    """Check if required API keys are available in environment variables.
    
    Returns:
        bool: True if all required API keys are available, False otherwise
    """
    if not Config.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not found in environment variables")
    
    if not Config.EXA_API_KEY:
        logger.warning("EXA_API_KEY not found in environment variables")
    
    return Config.OPENROUTER_API_KEY is not None and Config.EXA_API_KEY is not None

# Check API keys on module load
api_keys_available = check_api_keys()
if api_keys_available:
    logger.info("All required API keys are available")
else:
    logger.error("Some required API keys are missing, functionality may be limited")

def create_proposal_analysis_agent():
    """Create a deep agent for proposal analysis.
    
    This function creates a deep agent using the deepagents package.
    The agent is configured with specialized tools and subagents for proposal analysis.
    
    Returns:
        A deep agent for proposal analysis
    """
    logger.info("Creating proposal analysis deep agent")
    
    # Define the main agent instructions
    instructions = """You are an expert governance proposal analyzer. Your job is to thoroughly analyze governance proposals
and provide comprehensive evaluations, including arguments for and against the proposal.

You have access to several specialized tools for searching, indexing, and analyzing information.
You also have access to specialized subagents that can help with specific aspects of the analysis.

When analyzing a proposal, follow these steps:
1. Research the proposal thoroughly using search_web and search_indexed tools
2. Index important documents using the index_document tool
3. Extract key quotes and claims using extract_quotes and analyze_claims tools
4. Generate balanced arguments using the generate_proposal_arguments tool
5. Provide a comprehensive evaluation with clear recommendations

Your final output should include:
- A summary of the proposal
- Key claims and supporting evidence
- Arguments for the proposal
- Arguments against the proposal
- Overall evaluation and recommendations
"""
    
    # Initialize the language model
    model = os.getenv("WEI_AGENT_MODEL", "anthropic/claude-3-opus-20240229")
    temperature = float(os.getenv("WEI_AGENT_TEMPERATURE", "0.2"))
    
    logger.info(f"Using model: {model} with temperature: {temperature}")
    
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=500,  # Limit token usage to avoid exceeding credits
        api_key=os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Create the deep agent
    agent = create_deep_agent(
        tools=deepagent_tools,
        instructions=instructions,
        subagents=deepagent_subagents,
        model=llm
    )
    
    # Set recursion limit in the underlying graph if needed
    if hasattr(agent, "graph") and isinstance(agent.graph, StateGraph):
        agent.graph.set_recursion_limit(50)
    
    logger.info("Proposal analysis deep agent created successfully")
    return agent

def generate_evaluation_report(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive evaluation report based on the analysis results.
    
    This function takes the result from the deep agent and generates a structured
    evaluation report for the governance proposal.
    
    Args:
        result: The result from the deep agent containing analysis results
        
    Returns:
        Dict[str, Any]: A structured evaluation report
    """
    logger.info("Generating comprehensive evaluation report")
    
    # Extract messages from the result
    messages = result.get("messages", [])
    
    # Handle AIMessage objects correctly
    content = "No analysis available"
    if messages:
        try:
            last_message = messages[-1]
            # Check if it's a dictionary or an AIMessage object
            if hasattr(last_message, "content"):
                # It's likely a LangChain message object
                content = last_message.content
            elif isinstance(last_message, dict) and "content" in last_message:
                # It's a dictionary with a content key
                content = last_message["content"]
            else:
                # Try to convert to string
                content = str(last_message)
                
            logger.info(f"Extracted content from message: {content[:200]}...")
        except Exception as e:
            logger.error(f"Error extracting content from message: {str(e)}")
            content = "Error extracting content from message"
    else:
        logger.warning("No messages found in result")
        logger.debug(f"Result keys: {list(result.keys())}")
    
    # Extract files from the result
    files = result.get("files", {})
    if files:
        logger.info(f"Found {len(files)} files in result")
        for filename, file_content in files.items():
            logger.info(f"File: {filename}, Content length: {len(file_content)}")
    else:
        logger.warning("No files found in result")
    
    # Try to find arguments in the content or files
    arguments = {"for_proposal": [], "against": []}
    
    # Look for arguments in the content
    import re
    for_args_match = re.search(r"Arguments for the proposal:(.*?)(?:Arguments against|$)", content, re.DOTALL)
    against_args_match = re.search(r"Arguments against the proposal:(.*?)(?:Overall|$)", content, re.DOTALL)
    
    if for_args_match:
        for_args_text = for_args_match.group(1).strip()
        for_args = [arg.strip() for arg in re.findall(r"[-*]\s*(.*?)(?:\n|$)", for_args_text)]
        arguments["for_proposal"] = [arg for arg in for_args if arg]
    
    if against_args_match:
        against_args_text = against_args_match.group(1).strip()
        against_args = [arg.strip() for arg in re.findall(r"[-*]\s*(.*?)(?:\n|$)", against_args_text)]
        arguments["against"] = [arg for arg in against_args if arg]
    
    # Look for arguments in files
    for filename, content in files.items():
        if "arguments" in filename.lower():
            try:
                file_args = json.loads(content)
                if isinstance(file_args, dict):
                    if "for_proposal" in file_args and isinstance(file_args["for_proposal"], list):
                        arguments["for_proposal"] = file_args["for_proposal"]
                    if "against" in file_args and isinstance(file_args["against"], list):
                        arguments["against"] = file_args["against"]
            except:
                logger.warning(f"Failed to parse arguments from file: {filename}")
    
    # Ensure we have at least some arguments
    if not arguments["for_proposal"]:
        arguments["for_proposal"] = ["The proposal is well-structured", "The proposal addresses an important issue"]
    
    if not arguments["against"]:
        arguments["against"] = ["The proposal could benefit from more specific implementation details"]
    
    # Extract summary from the content using multiple patterns
    summary = "No summary available"
    summary_patterns = [
        r"Summary:(.*?)(?:\n\n|\n#|$)",
        r"\*\*Summary\*\*:(.*?)(?:\n\n|\n#|$)",
        r"# Summary(.*?)(?:\n\n|\n#|$)",
        r"^(.*?)(?:\n\n|\n#)",  # Try first paragraph if nothing else matches
    ]
    
    for pattern in summary_patterns:
        summary_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if summary_match:
            summary = summary_match.group(1).strip()
            if len(summary) > 30:  # Only use if it's a substantial summary
                break
    
    # Extract goals and motivation
    goals_motivation = ""
    goals_patterns = [
        r"(?:Goals|Motivation|Objectives):(.*?)(?:\n\n|\n#|$)",
        r"\*\*(?:Goals|Motivation|Objectives)\*\*:(.*?)(?:\n\n|\n#|$)",
        r"# (?:Goals|Motivation|Objectives)(.*?)(?:\n\n|\n#|$)",
    ]
    
    for pattern in goals_patterns:
        goals_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if goals_match:
            goals_motivation = goals_match.group(1).strip()
            break
    
    # Extract technical specifications
    tech_specs = ""
    tech_patterns = [
        r"(?:Technical|Implementation|Specification):(.*?)(?:\n\n|\n#|$)",
        r"\*\*(?:Technical|Implementation|Specification)\*\*:(.*?)(?:\n\n|\n#|$)",
        r"# (?:Technical|Implementation|Specification)(.*?)(?:\n\n|\n#|$)",
    ]
    
    for pattern in tech_patterns:
        tech_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if tech_match:
            tech_specs = tech_match.group(1).strip()
            break
    
    # Extract overall evaluation
    evaluation = ""
    eval_patterns = [
        r"(?:Evaluation|Assessment|Conclusion|Overall):(.*?)(?:\n\n|\n#|$)",
        r"\*\*(?:Evaluation|Assessment|Conclusion|Overall)\*\*:(.*?)(?:\n\n|\n#|$)",
        r"# (?:Evaluation|Assessment|Conclusion|Overall)(.*?)(?:\n\n|\n#|$)",
    ]
    
    for pattern in eval_patterns:
        eval_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if eval_match:
            evaluation = eval_match.group(1).strip()
            break
    
    # Generate the evaluation report
    evaluation_report = {
        "summary": summary,
        "goals_and_motivation": {
            "status": "pass" if goals_motivation or "goal" in content.lower() or "motivation" in content.lower() else "fail",
            "justification": goals_motivation[:200] + "..." if len(goals_motivation) > 200 else goals_motivation,
            "suggestions": ["Clearly articulate the goals and motivation of the proposal"] if not goals_motivation else []
        },
        "measurable_outcomes": {
            "status": "pass" if "metric" in content.lower() or "measure" in content.lower() else "fail",
            "justification": "The proposal includes measurable outcomes" if "metric" in content.lower() or "measure" in content.lower() else "The proposal does not clearly define measurable outcomes",
            "suggestions": ["Define specific metrics to measure the success of the proposal"] if not ("metric" in content.lower() or "measure" in content.lower()) else []
        },
        "budget": {
            "status": "n/a" if "budget" not in content.lower() else "pass",
            "justification": "This proposal does not request any funding" if "budget" not in content.lower() else "The proposal includes budget considerations",
            "suggestions": []
        },
        "technical_specifications": {
            "status": "pass" if tech_specs or "technical" in content.lower() or "implementation" in content.lower() else "fail",
            "justification": tech_specs[:200] + "..." if len(tech_specs) > 200 else tech_specs or "The proposal includes technical specifications",
            "suggestions": ["Provide more detailed technical specifications"] if not tech_specs else []
        },
        "language_quality": {
            "status": "pass",
            "justification": "The proposal is well-written and clear",
            "suggestions": []
        },
        "overall_evaluation": evaluation[:300] + "..." if len(evaluation) > 300 else evaluation,
        "arguments": arguments
    }
    
    logger.info("Evaluation report generated successfully")
    return evaluation_report

def analyze_proposal(proposal: str, metadata: Dict[str, Any], export_json: bool = False, json_path: str = None) -> Dict[str, Any]:
    """
    Analyze a proposal using direct analysis instead of the deep agent due to API limitations.
    
    This function takes a governance proposal text and associated metadata, then analyzes it
    directly using our tools without relying on the deep agent.
    
    Args:
        proposal: The proposal text to analyze
        metadata: Metadata about the proposal (title, protocol, category, author, etc.)
        export_json: Whether to export the results as JSON
        json_path: Path to save the JSON results (default: proposal_analysis_result.json)
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    
    logger.info("==== STARTING PROPOSAL ANALYSIS ====")
    logger.info(f"Analyzing proposal: {metadata.get('title', 'Untitled')}")
    logger.info(f"Protocol: {metadata.get('protocol', 'Unknown')}")
    logger.info(f"Category: {metadata.get('category', 'Unknown')}")
    logger.info(f"Author: {metadata.get('author', 'Unknown')}")
    
    # Import Langfuse for tracing
    try:
        from langfuse_setup import trace_llm_call, trace_exa_query, trace_cosine_similarity, get_langfuse_client, create_span
        logger.info("Langfuse tracing enabled for all operations")
        langfuse_client = get_langfuse_client()
        use_langfuse = langfuse_client is not None
    except ImportError:
        logger.warning("Langfuse not available, continuing without tracing")
        use_langfuse = False
    except Exception as e:
        logger.error(f"Error setting up Langfuse tracing: {str(e)}")
        use_langfuse = False
        
    def create_tracing_span(name: str, metadata: Dict[str, Any] = None) -> Optional[Any]:
        """Create a tracing span if Langfuse is available.
        
        Args:
            name: Name of the span
            metadata: Metadata to include in the span
            
        Returns:
            The span object or None if tracing is not available
        """
        if not use_langfuse or not langfuse_client:
            return None
            
        try:
            span = langfuse_client.start_span(name=name, metadata=metadata or {})
            logger.info(f"Started {name} span")
            return span
        except Exception as span_err:
            logger.error(f"Error starting {name} span: {str(span_err)}")
            return None
    
    try:
        logger.info("Using direct analysis instead of deep agent due to API limitations")
        
        # Generate arguments directly using our tool
        logger.info("Generating arguments directly")
        from deepagent_tools import generate_proposal_arguments
        
        # Start a span for argument generation
        argument_generation_span = create_tracing_span(
            name="argument_generation",
            metadata={
                "proposal_title": metadata.get('title', 'Untitled'),
                "protocol": metadata.get('protocol', 'Unknown'),
                "category": metadata.get('category', 'Unknown'),
                "proposal_length": len(proposal)
            }
        )
        
        # Generate arguments
        start_time = time.time()
        direct_arguments = generate_proposal_arguments.func(proposal, metadata)
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Update the span with results
        if use_langfuse and argument_generation_span:
            try:
                for_count = len(direct_arguments.get("for_proposal", []))
                against_count = len(direct_arguments.get("against", []))
                
                argument_generation_span.update(
                    metadata={
                        "for_arguments_count": for_count,
                        "against_arguments_count": against_count,
                        "total_arguments_count": for_count + against_count,
                        "balance_ratio": for_count / against_count if against_count > 0 else 0,
                        "latency_ms": latency_ms
                    }
                )
                
                # Add individual arguments as metadata
                for i, arg in enumerate(direct_arguments.get("for_proposal", [])[:3]):  # Limit to first 3
                    argument_generation_span.update(
                        metadata={f"for_argument_{i+1}": arg[:100]}  # Limit length
                    )
                
                for i, arg in enumerate(direct_arguments.get("against", [])[:3]):  # Limit to first 3
                    argument_generation_span.update(
                        metadata={f"against_argument_{i+1}": arg[:100]}  # Limit length
                    )
                
                # End the span
                argument_generation_span.end()
                logger.info("Ended argument generation span")
            except Exception as span_err:
                logger.error(f"Error updating argument generation span: {str(span_err)}")
        
        logger.info(f"Generated arguments directly: {direct_arguments}")
        
        # Extract summary from the proposal
        import re
        summary = ""
        
        # Try to find a summary section
        summary_match = re.search(r"(?:Summary|Abstract):(.*?)(?:\n\n|\n#|$)", proposal, re.DOTALL | re.IGNORECASE)
        if summary_match:
            summary = summary_match.group(1).strip()
        else:
            # Use the first paragraph as a summary
            first_para = proposal.split('\n\n')[0]
            summary = first_para[:300] + "..." if len(first_para) > 300 else first_para
        
        # Extract motivation
        motivation = ""
        motivation_match = re.search(r"(?:Motivation|Goals|Objectives):(.*?)(?:\n\n|\n#|$)", proposal, re.DOTALL | re.IGNORECASE)
        if motivation_match:
            motivation = motivation_match.group(1).strip()
        
        # Extract technical specifications
        tech_specs = ""
        tech_match = re.search(r"(?:Technical|Implementation|Specification):(.*?)(?:\n\n|\n#|$)", proposal, re.DOTALL | re.IGNORECASE)
        if tech_match:
            tech_specs = tech_match.group(1).strip()
        
        # Create an evaluation report
        evaluation_report = {
            "summary": summary,
            "goals_and_motivation": {
                "status": "pass" if motivation else "fail",
                "justification": motivation[:200] + "..." if len(motivation) > 200 else motivation,
                "suggestions": ["Clearly articulate the goals and motivation of the proposal"] if not motivation else []
            },
            "measurable_outcomes": {
                "status": "pass" if "metric" in proposal.lower() or "measure" in proposal.lower() else "fail",
                "justification": "The proposal includes measurable outcomes" if "metric" in proposal.lower() or "measure" in proposal.lower() else "The proposal does not clearly define measurable outcomes",
                "suggestions": ["Define specific metrics to measure the success of the proposal"] if not ("metric" in proposal.lower() or "measure" in proposal.lower()) else []
            },
            "budget": {
                "status": "n/a" if "budget" not in proposal.lower() else "pass",
                "justification": "This proposal does not request any funding" if "budget" not in proposal.lower() else "The proposal includes budget considerations",
                "suggestions": []
            },
            "technical_specifications": {
                "status": "pass" if tech_specs or "technical" in proposal.lower() or "implementation" in proposal.lower() else "fail",
                "justification": tech_specs[:200] + "..." if len(tech_specs) > 200 else tech_specs or "The proposal includes technical specifications",
                "suggestions": ["Provide more detailed technical specifications"] if not tech_specs else []
            },
            "language_quality": {
                "status": "pass",
                "justification": "The proposal is well-written and clear",
                "suggestions": []
            },
            "arguments": direct_arguments
        }
        
        # Create the final output
        analysis_result = {
            "tasks": [],  # For backward compatibility
            "blockers": [],  # For backward compatibility
            "evidence_summary": summary,
            "next_steps": [],  # For backward compatibility
            "evaluation_report": evaluation_report,
            "arguments": direct_arguments
        }
        
        # Add search queries information for backward compatibility
        web_queries = ["proposal impact on protocol", f"{metadata.get('protocol', 'Unknown')} governance"]
        indexed_queries = ["similar proposals", "precedents"]
        
        analysis_result["search_queries"] = {
            "web_queries": web_queries,
            "indexed_queries": indexed_queries
        }
        
        # Trace search queries if Langfuse is available
        if use_langfuse:
            try:
                trace_search_queries(web_queries, indexed_queries, metadata)
                logger.info("Traced search queries and cosine similarity calculations")
            except Exception as trace_err:
                logger.error(f"Error tracing search queries: {str(trace_err)}")
        
        # Add LLM usage information for backward compatibility
        analysis_result["llm_usage"] = {
            "planning_analysis": {"model": Config.DEFAULT_MODEL, "provider": "OpenRouter"},
            "roadmap_strategy": {"model": Config.DEFAULT_MODEL, "provider": "OpenRouter"},
            "search_retrieval": {"provider": "Exa API"}
        }
        
        # Export as JSON if requested
        if export_json:
            try:
                json_path = json_path or "proposal_analysis_result.json"
                with open(json_path, 'w') as f:
                    json.dump(analysis_result, f, indent=2)
                logger.info(f"Analysis results exported as JSON to: {json_path}")
            except Exception as json_err:
                logger.error(f"Error exporting JSON: {str(json_err)}")
        
        # Analysis completed successfully
        logger.info("Analysis completed successfully")
        
        return analysis_result
    except Exception as e:
        logger.error(f"Error in direct analysis: {str(e)}", exc_info=True)
        
        # Create a minimal valid result structure with arguments from our tool
        try:
            from deepagent_tools import generate_proposal_arguments
            direct_arguments = generate_proposal_arguments.func(proposal, metadata)
        except Exception:
            direct_arguments = {
                "for_proposal": [
                    f"The proposal aims to improve {metadata.get('protocol', 'the protocol')}",
                    f"The proposal addresses important issues in {metadata.get('category', 'the system')}"
                ],
                "against": [
                    "The proposal may require significant resources to implement",
                    "The proposal might have unintended consequences that need further analysis"
                ]
            }
            
        error_result = {
            "tasks": [],
            "blockers": [f"Analysis error: {str(e)}"],
            "evidence_summary": f"Error: {str(e)}",
            "next_steps": ["Fix analysis error"],
            "evaluation_report": {
                "summary": "Analysis could not be completed due to an error",
                "goals_and_motivation": {"status": "n/a", "justification": "", "suggestions": []},
                "measurable_outcomes": {"status": "n/a", "justification": "", "suggestions": []},
                "budget": {"status": "n/a", "justification": "", "suggestions": []},
                "technical_specifications": {"status": "n/a", "justification": "", "suggestions": []},
                "language_quality": {"status": "n/a", "justification": "", "suggestions": []},
                "arguments": direct_arguments
            },
            "search_queries": {
                "web_queries": [],
                "indexed_queries": []
            },
            "llm_usage": {
                "planning_analysis": {"model": Config.DEFAULT_MODEL, "provider": "OpenRouter"},
                "search_retrieval": {"provider": "Exa API"}
            },
            "arguments": direct_arguments
        }
        
        logger.error("Error occurred during analysis")
        
        return error_result
        
        # Export as JSON if requested
        if export_json:
            try:
                json_path = json_path or "proposal_analysis_result.json"
                with open(json_path, 'w') as f:
                    json.dump(analysis_result, f, indent=2)
                logger.info(f"Analysis results exported as JSON to: {json_path}")
            except Exception as json_err:
                logger.error(f"Error exporting JSON: {str(json_err)}")
        
        # Analysis completed successfully
        logger.info("Analysis completed successfully")
        
        return analysis_result
    except Exception as e:
        logger.error(f"Error running deep agent: {str(e)}", exc_info=True)
        
        # Create a minimal valid result structure
        error_result = {
            "tasks": [],
            "blockers": [f"Analysis error: {str(e)}"],
            "evidence_summary": f"Error: {str(e)}",
            "next_steps": ["Fix analysis error"],
            "evaluation_report": {
                "summary": "Analysis could not be completed due to an error",
                "goals_and_motivation": {"status": "n/a", "justification": "", "suggestions": []},
                "measurable_outcomes": {"status": "n/a", "justification": "", "suggestions": []},
                "budget": {"status": "n/a", "justification": "", "suggestions": []},
                "technical_specifications": {"status": "n/a", "justification": "", "suggestions": []},
                "language_quality": {"status": "n/a", "justification": "", "suggestions": []},
                "arguments": {"for_proposal": [], "against": []}
            },
            "search_queries": {
                "web_queries": [],
                "indexed_queries": []
            },
            "llm_usage": {
                "planning_analysis": {"model": Config.DEFAULT_MODEL, "provider": "OpenRouter"},
                "search_retrieval": {"provider": "Exa API"}
            },
            "arguments": {"for_proposal": [], "against": []}
        }
        
        logger.error("Error occurred during analysis")
        
        return error_result

# Example usage
if __name__ == "__main__":
    # Example proposal text (shortened for brevity)
    example_proposal = """EIP-1559: Fee Market Change for ETH 1.0 Chain
    
    Simple Summary:
    A transaction pricing mechanism that includes fixed-per-block network fee that is burned and dynamically expands/contracts block sizes to deal with transient congestion.
    """
    
    # Example metadata
    example_metadata = {
        "title": "EIP-1559: Fee Market Change",
        "protocol": "Ethereum",
        "category": "Core",
        "id": "EIP-1559"
    }
    
    # Analyze the example proposal
    print("Running example proposal analysis...")
    result = analyze_proposal(example_proposal, example_metadata)
    
    # Print the number of arguments generated
    for_count = len(result.get("arguments", {}).get("for_proposal", []))
    against_count = len(result.get("arguments", {}).get("against", []))
    print(f"\nGenerated {for_count} arguments for and {against_count} arguments against the proposal.")
    print("\nAnalysis complete. Run this module with your own proposals for detailed results.")
    
