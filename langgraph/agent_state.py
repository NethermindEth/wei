from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage

class ProposalMetadata(TypedDict):
    """Metadata about the proposal being analyzed."""
    id: str
    title: str
    author: str
    date_submitted: str
    protocol: str
    category: str
    url: str

class ClaimEvidence(TypedDict):
    """A claim and its supporting evidence."""
    claim: str
    evidence: List[str]
    sources: List[str]
    confidence: float

class Task(TypedDict):
    """A task identified from the proposal analysis."""
    id: str
    description: str
    priority: float  # RICE score
    blockers: List[str]
    dependencies: List[str]
    evidence: List[str]

class ArgumentsDict(TypedDict):
    """Arguments for and against a proposal."""
    for_proposal: List[str]
    against: List[str]

class AgentState(TypedDict):
    """The state of the proposal analysis agent."""
    # Input
    proposal: str
    metadata: ProposalMetadata
    
    # Intermediate data
    messages: List[BaseMessage]
    search_results: List[Dict[str, Any]]
    indexed_data: List[Dict[str, Any]]
    extracted_quotes: List[Dict[str, str]]
    claims_evidence: List[ClaimEvidence]
    signals: Dict[str, Any]
    hypotheses: List[Dict[str, Any]]
    verified_claims: List[ClaimEvidence]
    rag_results: Optional[List[Dict[str, Any]]]
    arguments: ArgumentsDict  # Arguments for and against the proposal
    
    # Output
    tasks: List[Task]
    blockers: List[str]
    evidence_summary: str
    next_steps: List[str]
