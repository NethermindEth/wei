"""Define the configurable parameters for the agent."""
from __future__ import annotations
import os
from dataclasses import dataclass, field, fields
from typing import Annotated, Optional, Dict, Any, List

# Define a simple system prompt
SYSTEM_PROMPT = """You are an AI assistant that helps analyze governance proposals."""

@dataclass(kw_only=True)
class Context:
    """The context for the agent."""
    system_prompt: str = field(
        default=SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt to use for the agent's interactions. "
                        "This prompt sets the context and behavior for the agent."
        },
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="anthropic/claude-3-5-sonnet-20240620",
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
                        "Should be in the form: provider/model-name."
        },
    )

    max_search_results: int = field(
        default=10,
        metadata={
            "description": "The maximum number of search results to return for each search query."
        },
    )

    # Proposal analysis configuration
    enable_proposal_analysis: bool = field(
        default=True,
        metadata={
            "description": "Enable advanced proposal analysis features including evaluation reports and task generation."
        },
    )

    analysis_depth: str = field(
        default="comprehensive",
        metadata={
            "description": "Depth of proposal analysis: 'basic', 'standard', or 'comprehensive'."
        },
    )

    max_arguments: int = field(
        default=5,
        metadata={
            "description": "Maximum number of arguments to generate for each side of a proposal."
        },
    )

    max_tasks: int = field(
        default=8,
        metadata={
            "description": "Maximum number of tasks to generate from proposal analysis."
        },
    )

    max_blockers: int = field(
        default=5,
        metadata={
            "description": "Maximum number of blockers to identify in proposal analysis."
        },
    )

    enable_langfuse_tracing: bool = field(
        default=True,
        metadata={
            "description": "Enable Langfuse tracing for monitoring and debugging proposal analysis."
        },
    )

    openrouter_api_key: str = field(
        default="",
        metadata={
            "description": "OpenRouter API key for LLM calls in proposal analysis."
        },
    )

    exa_api_key: str = field(
        default="",
        metadata={
            "description": "Exa API key for web search functionality."
        },
    )

    langfuse_public_key: str = field(
        default="",
        metadata={
            "description": "Langfuse public key for tracing (optional)."
        },
    )

    langfuse_secret_key: str = field(
        default="",
        metadata={
            "description": "Langfuse secret key for tracing (optional)."
        },
    )
    
    # Additional fields for proposal text and custom criteria
    proposal_text: str = ""
    custom_criteria: Dict[str, Any] = None
    search_query: str = ""

    def __post_init__(self) -> None:
        """Fetch env vars for attributes that were not passed as args."""
        # First, load matching env names for direct fields (MODEL, OPENROUTER_API_KEY, etc.)
        for f in fields(self):
            if not f.init:
                continue
            if getattr(self, f.name) == f.default:
                setattr(self, f.name, os.environ.get(f.name.upper(), f.default))
        
        # Then, apply OpenRouter-specific overrides if provided
        provider = os.environ.get("WEI_AGENT_AI_MODEL_PROVIDER")
        name = os.environ.get("WEI_AGENT_AI_MODEL_NAME")
        if provider and name:
            self.model = f"{provider}/{name}"
        
        # Map OpenRouter API key into field if present
        or_key = os.environ.get("WEI_AGENT_OPEN_ROUTER_API_KEY")
        if or_key:
            self.openrouter_api_key = or_key
        
        # Map Exa API key into field if present
        exa_key = os.environ.get("WEI_AGENT_EXA_API_KEY")
        if exa_key:
            self.exa_api_key = exa_key
