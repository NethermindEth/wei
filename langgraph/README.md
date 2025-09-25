# Wei Notebook: Deep Proposal Analysis System

## Overview

Wei Notebook is an advanced proposal analysis system designed to evaluate governance proposals for blockchain protocols. This implementation uses the deepagent package to provide a more powerful and flexible analysis approach.

## System Architecture

The system is built around the deepagent package, which provides a flexible framework for creating powerful AI agents:

1. **Deep Proposal Analyzer**: The main component that orchestrates the analysis process
2. **Deepagent Tools**: Custom tools for proposal analysis, including argument generation
3. **Deepagent Subagents**: Specialized subagents for different aspects of analysis
4. **Langfuse Tracing**: Modern tracing implementation for observability


## Key Files and Components

### Core Components

- **deep_proposal_analyzer.py**: The main analyzer that orchestrates the analysis process
- **deepagent_tools.py**: Implements custom tools for proposal analysis, including argument generation
- **deepagent_subagents.py**: Contains specialized subagents for different aspects of analysis
- **deep_adapter.py**: Adapter for integrating with the deepagent package

### Support Components

- **disable_langchain_tracing.py**: Disables LangChain tracing for cleaner output
- **langfuse_setup.py**: Provides modern tracing functionality for LLM calls

### Testing

- **tests/test_deep_analyzer.py**: Tests for the deep proposal analyzer
- **tests/test_argument_generation.py**: Tests for the argument generation functionality

## Setting Up the Environment

### Prerequisites

- Python 3.9+
- Required API keys:
  - OpenRouter API key (for LLM access)
  - Exa API key (for search and retrieval)

### Environment Variables

Create a `.env` file with the following variables:

```
# API Keys
WEI_AGENT_OPEN_ROUTER_API_KEY=your_openrouter_api_key
WEI_AGENT_EXA_API_KEY=your_exa_api_key

# Model Configuration
WEI_AGENT_MODEL=anthropic/claude-3-opus-20240229
WEI_AGENT_PLANNING_MODEL=anthropic/claude-3-opus-20240229
WEI_AGENT_ANALYZING_MODEL=anthropic/claude-3-opus-20240229
WEI_AGENT_ANALYZING_TEMPERATURE=0.2
WEI_AGENT_ANALYZING_MAX_TOKENS=2000

# Langfuse Configuration (Optional, for tracing)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com
```

You can also copy the `.env.example` file and fill in your API keys.

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Using the System

### Basic Usage

```python
from deep_proposal_analyzer import analyze_proposal

# Define your proposal text
proposal_text = """
# Proposal Title

## Abstract
Proposal details...

## Motivation
...
"""

# Define metadata
metadata = {
    "id": "PROP-123",
    "title": "Your Proposal Title",
    "author": "Author Name",
    "date_submitted": "2025-09-22",
    "protocol": "Ethereum",  # or Bitcoin, Aave, etc.
    "category": "Core",      # or Governance, DeFi, etc.
    "url": "https://example.com/proposal"
}

# Run the analysis
result = analyze_proposal(proposal_text, metadata)

# Access the results
tasks = result["tasks"]
blockers = result["blockers"]
evaluation_report = result["evaluation_report"]
arguments = result["arguments"]  # Contains "for_proposal" and "against" lists
```

### Understanding the Results

The analysis result contains several key components:

1. **Tasks**: Prioritized tasks identified from the proposal
2. **Blockers**: Potential issues that might block implementation
3. **Evidence Summary**: A summary of the evidence found
4. **Next Steps**: Recommended next actions
5. **Evaluation Report**: A comprehensive evaluation including:
   - Goals and motivation assessment
   - Measurable outcomes evaluation
   - Budget analysis
   - Technical specifications review
   - Language quality assessment
   - Arguments for and against the proposal

## Workflow Details

### 1. Planning Phase

The Planning Agent creates a detailed research plan based on the proposal text and metadata. It identifies key areas to investigate and questions to answer.

```python
# Example planning agent output
"""
Research Plan:
1. Investigate technical feasibility
2. Assess economic implications
3. Evaluate governance impact
4. Research similar proposals
"""
```

### 2. Research Phase

The Search Tool, Indexer Tool, and Reader Tool work together to gather relevant information:

- Search Tool queries the web for relevant content
- Indexer Tool accesses canonical sources like EIPs and forum posts
- Reader Tool extracts content and clips relevant quotes

### 3. Analysis Phase

The Analyzing Agent extracts claims and evidence from the gathered information, which are organized into a claim-evidence graph.

```python
# Example claim-evidence structure
{
    "claim": "The proposal improves scalability",
    "evidence": ["Benchmark shows 10x throughput", "Similar approach succeeded in other protocols"],
    "sources": ["research_paper", "protocol_blog"],
    "confidence": 0.85
}
```

### 4. Evaluation Phase

Signal Detectors identify important signals, the Hypothesizer generates hypotheses, and the Skeptic Agent critically evaluates them. When needed, the RAG Fallback provides additional context.

### 5. Prioritization Phase

The Prioritizer Agent identifies and prioritizes tasks, and the Strategy Agent develops a strategic roadmap for implementation.

### 6. Roadmap Generation with Perplexity

The system uses Perplexity's Sonar-Pro model (via OpenRouter API) to generate detailed implementation roadmaps. This provides:

- Milestone planning with dependencies and timelines
- Resource requirement analysis
- Risk assessment and mitigation strategies
- Success metrics and evaluation criteria

## Advanced Usage

### Customizing the Analysis

You can customize the analysis by modifying the agent prompts in `agent_nodes.py` or by adjusting the workflow in `proposal_analyzer.py`.

### Tracing LLM Calls with Langfuse

The system uses Langfuse for comprehensive tracing and observability. Tracing is implemented through `langfuse_setup.py` and provides:

#### Modern Tracing Features
- Context managers with `with langfuse.start_as_current_span(...)` syntax
- Decorator-based tracing with `@observe_function`
- Automatic span and trace management
- Nested spans and generations for complex workflows
- Score tracking for quality metrics

#### Comprehensive Observability
- Model name, prompt, and completion tracking
- Latency measurements and token usage statistics
- Rich metadata for context and debugging
- Hierarchical spans showing the full execution flow
- Parent-child relationships between operations

#### Setting Up Langfuse

1. Sign up for a Langfuse account at [langfuse.com](https://langfuse.com)
2. Get your public and secret keys from the Langfuse dashboard
3. Add them to your `.env` file:
   ```
   LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
   LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```
4. The system will automatically use Langfuse for tracing if the keys are available

#### Using Traces in Development

When debugging, you can use the Langfuse dashboard to:
- View the full execution flow of your analysis
- Identify bottlenecks in the workflow
- Debug errors in specific components
- Monitor LLM usage and performance

### Adding Visualizations to the Notebook

The repository includes two visualization files:
- `workflow_visualization.png` - Shows the complete workflow of the system
- `roadmap_visualization.png` - Shows the implementation roadmap

To include these visualizations in your Jupyter notebook:

```python
# Add these cells to your notebook
from IPython.display import Image, display, Markdown

# Display workflow visualization
display(Markdown("## Workflow Visualization"))
display(Image(filename="workflow_visualization.png"))

# Display roadmap visualization
display(Markdown("## Implementation Roadmap"))
display(Image(filename="roadmap_visualization.png"))
```

You can also generate these visualizations programmatically using the `workflow_visualization.py` script:

```python
from workflow_visualization import visualize_workflow, create_roadmap_visualization

# Generate and display the workflow visualization
workflow_plt = visualize_workflow()
workflow_plt.show()

# Generate and display the roadmap visualization
roadmap_plt = create_roadmap_visualization()
roadmap_plt.show()
```

### Using the Perplexity-Powered Roadmap Generator

The repository includes a roadmap generator that uses Perplexity's Sonar-Pro model via OpenRouter API:

```python
# Add these cells to your notebook
from roadmap_generator import generate_roadmap, format_roadmap_for_display
from IPython.display import HTML

# Generate the roadmap using Perplexity/Sonar-Pro
roadmap_data = generate_roadmap(proposal_text, metadata)

# Format and display the roadmap
roadmap_html = format_roadmap_for_display(roadmap_data)
display(HTML(roadmap_html))
```

This will generate a detailed implementation roadmap with milestones, resources, risks, and success metrics.

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure your `.env` file contains the required API keys
2. **Import Errors**: Make sure all dependencies are installed
3. **LLM Errors**: Check your OpenRouter API key and quota

### Debugging

#### Using Langfuse for Debugging

The Langfuse dashboard provides powerful debugging capabilities:

1. **Trace Explorer**: View all traces with filtering and search
2. **Trace Details**: Examine the full execution flow of each analysis
3. **Span Inspection**: Dive into specific operations to see inputs, outputs, and errors
4. **LLM Call Analysis**: Review prompts, completions, and performance metrics

#### Local Debugging

If Langfuse is not configured, the system falls back to local logging:

- Use the trace IDs from LLM calls to track the flow of information
- Check the log files for detailed execution information
- Set the logging level to DEBUG for more verbose output

## Extending the System

### Adding New Agents

1. Define a new agent function in `agent_nodes.py`
2. Update the workflow in `proposal_analyzer.py` to include your agent
3. Update the state definition in `agent_state.py` if needed

### Adding New Tools

1. Implement your tool in `agent_tools.py`
2. Initialize it in `agent_nodes.py`
3. Use it in the appropriate agent function

## Conclusion

The Wei Notebook proposal analysis system provides a powerful framework for analyzing governance proposals. By combining multiple specialized agents with external knowledge sources, it delivers comprehensive and structured evaluations to help stakeholders make informed decisions.

For more information, refer to the code documentation in each file.
