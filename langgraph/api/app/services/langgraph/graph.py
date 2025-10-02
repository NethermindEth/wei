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

# Define a simple analyze function
def analyze_proposal(state: State) -> State:
    """Analyze a proposal."""
    proposal_text = state.get("proposal_text", "")
    
    # In a real implementation, this would call an LLM
    # For now, return a simple result
    result = {
        "id": "analysis-123",
        "proposal_id": "proposal-123",
        "result": "PASS",
        "confidence": 0.85,
        "details": f"Analysis of: {proposal_text[:50]}...",
        "created_at": "2025-09-30T12:00:00Z",
        "updated_at": "2025-09-30T12:00:00Z",
    }
    
    return {**state, "result": result}

# Define a function to generate arguments
def generate_arguments(state: State) -> State:
    """Generate arguments for a proposal."""
    proposal_text = state.get("proposal_text", "")
    
    # In a real implementation, this would call an LLM
    # For now, return a simple result
    result = {
        "id": "analysis-123",
        "proposal_id": "proposal-123",
        "result": "PASS",
        "confidence": 0.85,
        "details": f"Analysis of: {proposal_text[:50]}...",
        "created_at": "2025-09-30T12:00:00Z",
        "updated_at": "2025-09-30T12:00:00Z",
        "arguments": {
            "for_proposal": [
                "This proposal improves governance efficiency",
                "It addresses a critical security vulnerability",
                "The implementation is straightforward"
            ],
            "against": [
                "The timing could be better",
                "There are potential side effects",
                "More testing may be needed"
            ]
        }
    }
    
    return {**state, "result": result}

# Define a function for custom evaluation
def custom_evaluate(state: State) -> State:
    """Evaluate a proposal using custom criteria."""
    proposal_text = state.get("proposal_text", "")
    custom_criteria = state.get("custom_criteria", {})
    
    # In a real implementation, this would call an LLM
    # For now, return a simple result
    criteria_results = {}
    for key, value in custom_criteria.items():
        criteria_results[key] = {
            "status": "pass" if len(key) % 2 == 0 else "fail",
            "justification": f"Evaluation of criterion '{key}' for proposal: {proposal_text[:30]}...",
            "suggestions": ["Suggestion 1", "Suggestion 2"]
        }
    
    result = {
        "summary": f"Custom evaluation of proposal: {proposal_text[:50]}...",
        "response_map": criteria_results
    }
    
    return {**state, "result": result}

# Define a function for searching related proposals
def search_related_proposals(state: State) -> State:
    """Search for related proposals."""
    search_query = state.get("search_query", "")
    
    # In a real implementation, this would call a search service
    # For now, return a simple result
    result = [
        {
            "id": "proposal-123",
            "title": f"Related proposal 1 for: {search_query}",
            "similarity_score": 0.85
        },
        {
            "id": "proposal-456",
            "title": f"Related proposal 2 for: {search_query}",
            "similarity_score": 0.72
        }
    ]
    
    return {**state, "result": result}

# Define a function for chat
def chat(state: State) -> State:
    """Chat with the agent."""
    messages = state.get("messages", [])
    
    # In a real implementation, this would call an LLM
    # For now, return a simple response
    from langchain_core.messages import AIMessage
    
    # Get the last message content
    last_message_content = messages[-1].content if messages else "No message"
    
    # Create a response
    response = AIMessage(content=f"You said: {last_message_content}. This is a simple response.")
    
    return {**state, "messages": messages + [response]}

# Define the router function
def router(state: State) -> str:
    """Route the state to the appropriate node."""
    task = state.get("task")
    
    if task == "analyze_proposal":
        return "analyze_proposal"
    elif task == "generate_arguments":
        return "generate_arguments"
    elif task == "custom_evaluate":
        return "custom_evaluate"
    elif task == "search_related_proposals":
        return "search_related_proposals"
    elif task == "chat":
        return "chat"
    else:
        return END

# Build the graph
graph = StateGraph(State)
graph.add_node("analyze_proposal", analyze_proposal)
graph.add_node("generate_arguments", generate_arguments)
graph.add_node("custom_evaluate", custom_evaluate)
graph.add_node("search_related_proposals", search_related_proposals)
graph.add_node("chat", chat)

# Add the edges
graph.set_entry_point("router")
graph.add_node("router", router)
graph.add_edge("router", "analyze_proposal")
graph.add_edge("router", "generate_arguments")
graph.add_edge("router", "custom_evaluate")
graph.add_edge("router", "search_related_proposals")
graph.add_edge("router", "chat")
graph.add_edge("analyze_proposal", END)
graph.add_edge("generate_arguments", END)
graph.add_edge("custom_evaluate", END)
graph.add_edge("search_related_proposals", END)
graph.add_edge("chat", END)

# Compile the graph
graph = graph.compile()
