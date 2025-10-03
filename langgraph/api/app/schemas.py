"""
Schema models for request/response data.
"""

# Standard library imports
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

# Third-party imports
from pydantic import BaseModel, Field

# Schema groups

#-----------------------------------------------------------------------------
# 1. Request models
#-----------------------------------------------------------------------------

# Deep Research models
class DeepResearchRequest(BaseModel):
    """Request model for deep research."""

    topic: str = Field(..., description="The protocol, community, subculture, or idea to research")


class DiscussionResource(BaseModel):
    """A single discussion resource/platform found during research."""

    name: str = Field(..., description="Official name of the community/resource")
    link: str = Field(..., description="Direct link to the hub")
    type: str = Field(..., description="Category of resource (docs, forum, Discord, GitHub, meetup, newsletter, etc.)")
    description: str = Field(..., description="Explanation of the role and value of this space")
    quality_of_discourse: str = Field(..., description="Assessment of discourse quality")


class DeepResearchResponse(BaseModel):
    """The structured response from the deep research AI model."""

    topic: str = Field(..., description="The research topic")
    resources: List[DiscussionResource] = Field(..., description="List of discovered resources/platforms")


class DeepResearchApiResponse(BaseModel):
    """Response for deep research API endpoints."""

    topic: str = Field(..., description="The research topic")
    resources: List[DiscussionResource] = Field(..., description="List of discovered resources/platforms")
    from_cache: bool = Field(..., description="Whether this result was served from cache")
    created_at: datetime = Field(..., description="When this result was created")
    expires_at: datetime = Field(..., description="When this result expires")


# Roadmap models
class RoadmapRequest(BaseModel):
    """Request model for roadmap generation."""

    subject: str = Field(..., description="The subject of the roadmap (e.g., protocol name)")
    kind: str = Field(..., description="The kind of subject (e.g., protocol, DAO, project)")
    scope: str = Field(..., description="The scope of the roadmap")
    from_date: Optional[str] = Field(None, description="Start date for research window (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, description="End date for research window (YYYY-MM-DD)")
    additional_context: Optional[str] = Field(None, description="Additional context for roadmap generation")


class RoadmapSource(BaseModel):
    """A source used in roadmap research."""

    id: str = Field(..., description="Unique identifier for the source")
    type: str = Field(..., description="Type of source (e.g., blog, whitepaper, website)")
    title: str = Field(..., description="Title of the source")
    url: str = Field(..., description="URL of the source")
    published_at: str = Field(..., description="Publication date of the source")
    retrieved_at: str = Field(..., description="Date when the source was retrieved")
    credibility: str = Field(..., description="Credibility assessment of the source")
    notes: str = Field("", description="Additional notes about the source")


class RoadmapDomain(BaseModel):
    """Domain information for the roadmap."""

    name: str = Field(..., description="Name of the subject")
    kind: str = Field(..., description="Kind of subject")
    scope: str = Field(..., description="Scope of the roadmap")
    as_of: str = Field(..., description="Date when the roadmap was generated")
    research_window: Dict[str, str] = Field(..., description="Research time window")


class RoadmapMetadata(BaseModel):
    """Metadata for the roadmap."""

    generator: str = Field(..., description="Name of the generator")
    generated_at: str = Field(..., description="Generation timestamp")
    notes: str = Field("", description="Additional notes")


class RoadmapResponseContent(BaseModel):
    """Content of the roadmap response."""

    schema_version: str = Field(..., description="Schema version")
    domain: RoadmapDomain = Field(..., description="Domain information")
    streams: List[str] = Field(default_factory=list, description="Development streams")
    fitness_functions: List[Dict[str, Any]] = Field(default_factory=list, description="Fitness functions")
    problems: List[Dict[str, Any]] = Field(default_factory=list, description="Problems identified")
    interventions: List[Dict[str, Any]] = Field(default_factory=list, description="Proposed interventions")
    proposals: List[Dict[str, Any]] = Field(default_factory=list, description="Proposals")
    links: List[Dict[str, Any]] = Field(default_factory=list, description="Links between elements")
    sources: List[RoadmapSource] = Field(default_factory=list, description="Sources used")
    metadata: RoadmapMetadata = Field(..., description="Metadata")


class RoadmapResponse(BaseModel):
    """Response model for roadmap generation."""

    id: str = Field(..., description="Unique identifier for the roadmap")
    request: RoadmapRequest = Field(..., description="Original request")
    response: RoadmapResponseContent = Field(..., description="Generated roadmap content")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: str = Field(..., description="Expiration timestamp")


class RoadmapApiResponse(BaseModel):
    """API response for roadmap generation."""

    result: RoadmapResponse = Field(..., description="Generated roadmap")
    cache_info: Optional[Dict[str, Any]] = Field(None, description="Cache information")

class ProposalRequest(BaseModel):
    """Request model for proposal analysis, matching Rust Proposal struct."""
    
    # Allow either content or description field for backward compatibility
    content: Optional[str] = Field(None, description="Description of the proposal (deprecated, use description)")
    description: Optional[str] = Field(None, description="Description of the proposal")
    proposal_id: Optional[str] = Field(None, description="Optional proposal ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    
    def __init__(self, **data):
        super().__init__(**data)
        # If description is not provided but content is, use content as description
        if not self.description and self.content:
            self.description = self.content
    
    # Validate that at least one of content or description is provided
    @property
    def proposal_text(self) -> str:
        """Get the proposal text from either description or content field."""
        return self.description or self.content or ""
    
    class Config:
        validate_assignment = True


class ArgumentsRequest(BaseModel):
    """Request model for generating proposal arguments."""
    
    # Allow either content or description field for backward compatibility
    content: Optional[str] = Field(None, description="Description of the proposal (deprecated, use description)")
    description: Optional[str] = Field(None, description="Description of the proposal")
    proposal_id: Optional[str] = Field(None, description="Optional proposal ID")
    max_arguments: Optional[int] = Field(5, description="Maximum number of arguments to generate per side")
    
    def __init__(self, **data):
        super().__init__(**data)
        # If description is not provided but content is, use content as description
        if not self.description and self.content:
            self.description = self.content
    
    # Validate that at least one of content or description is provided
    @property
    def proposal_text(self) -> str:
        """Get the proposal text from either description or content field."""
        return self.description or self.content or ""
    
    class Config:
        validate_assignment = True


class CustomEvaluationRequest(BaseModel):
    """Request model for custom proposal evaluation."""
    
    # Allow either content or description field for backward compatibility
    content: Optional[str] = Field(None, description="Description of the proposal to evaluate (deprecated, use description)")
    description: Optional[str] = Field(None, description="Description of the proposal to evaluate")
    custom_criteria: Union[Dict[str, Any], str] = Field(..., description="Custom evaluation criteria")
    
    def __init__(self, **data):
        super().__init__(**data)
        # If description is not provided but content is, use content as description
        if not self.description and self.content:
            self.description = self.content
        # If custom_criteria is a string, convert it to a dict
        if isinstance(self.custom_criteria, str):
            self.custom_criteria = {"general": self.custom_criteria}
    
    # Validate that at least one of content or description is provided
    @property
    def proposal_text(self) -> str:
        """Get the proposal text from either description or content field."""
        return self.description or self.content or ""
    
    class Config:
        validate_assignment = True


#-----------------------------------------------------------------------------
# 2. Shared models
#-----------------------------------------------------------------------------

class ProposalArguments(BaseModel):
    """Model for proposal arguments."""
    
    for_proposal: List[str] = Field(default_factory=list, description="Arguments supporting the proposal")
    against: List[str] = Field(default_factory=list, description="Arguments against the proposal")


class ProposalArgumentsResponse(BaseModel):
    """Response wrapper for proposal arguments to match Rust implementation."""
    
    arguments: ProposalArguments = Field(..., description="Arguments for and against the proposal")
    from_cache: bool = Field(False, description="Whether this response came from cache")


class EvaluationResult(BaseModel):
    """Model for evaluation results."""
    
    status: str = Field(..., description="Status of the evaluation (pass/fail/n/a)")
    justification: str = Field("", description="Justification for the evaluation")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")


class CustomEvaluationResponse(BaseModel):
    """Response model for custom proposal evaluation, matching Rust implementation exactly."""


class RelatedProposal(BaseModel):
    """Model for a related proposal."""
    
    id: str = Field(..., description="Unique identifier of the proposal")
    title: str = Field(..., description="Title of the proposal")
    score: float = Field(..., description="Relevance score")
    content: Optional[str] = Field(None, description="Proposal content")
    url: Optional[str] = Field(None, description="URL to the proposal")


# 5. Roadmap models
#-----------------------------------------------------------------------------

class RoadmapRequest(BaseModel):
    """Request model for roadmap generation."""

    subject: str = Field(..., description="The subject of the roadmap (e.g., protocol name)")
    kind: str = Field(..., description="The kind of subject (e.g., protocol, DAO, project)")
    scope: str = Field(..., description="The scope of the roadmap")
    from_date: Optional[str] = Field(None, description="Start date for research window (YYYY-MM-DD)")
    to_date: Optional[str] = Field(None, description="End date for research window (YYYY-MM-DD)")
    additional_context: Optional[str] = Field(None, description="Additional context for roadmap generation")


class RoadmapSource(BaseModel):
    """A source used in roadmap research."""

    id: str = Field(..., description="Unique identifier for the source")
    type: str = Field(..., description="Type of source (e.g., blog, whitepaper, website)")
    title: str = Field(..., description="Title of the source")
    url: str = Field(..., description="URL of the source")
    published_at: str = Field(..., description="Publication date of the source")
    retrieved_at: str = Field(..., description="Date when the source was retrieved")
    credibility: str = Field(..., description="Credibility assessment of the source")
    notes: str = Field("", description="Additional notes about the source")


class RoadmapDomain(BaseModel):
    """Domain information for the roadmap."""

    name: str = Field(..., description="Name of the subject")
    kind: str = Field(..., description="Kind of subject")
    scope: str = Field(..., description="Scope of the roadmap")
    as_of: str = Field(..., description="Date when the roadmap was generated")
    research_window: Dict[str, str] = Field(..., description="Research time window")


class RoadmapMetadata(BaseModel):
    """Metadata for the roadmap."""

    generator: str = Field(..., description="Name of the generator")
    generated_at: str = Field(..., description="Generation timestamp")
    notes: str = Field("", description="Additional notes")


class RoadmapResponseContent(BaseModel):
    """Content of the roadmap response."""

    schema_version: str = Field(..., description="Schema version")
    domain: RoadmapDomain = Field(..., description="Domain information")
    streams: List[str] = Field(default_factory=list, description="Development streams")
    fitness_functions: List[Dict[str, Any]] = Field(default_factory=list, description="Fitness functions")
    problems: List[Dict[str, Any]] = Field(default_factory=list, description="Problems identified")
    interventions: List[Dict[str, Any]] = Field(default_factory=list, description="Proposed interventions")
    proposals: List[Dict[str, Any]] = Field(default_factory=list, description="Proposals")
    links: List[Dict[str, Any]] = Field(default_factory=list, description="Links between elements")
    sources: List[RoadmapSource] = Field(default_factory=list, description="Sources used")
    metadata: RoadmapMetadata = Field(..., description="Metadata")


class RoadmapResponse(BaseModel):
    """Response model for roadmap generation."""

    id: str = Field(..., description="Unique identifier for the roadmap")
    request: RoadmapRequest = Field(..., description="Original request")
    response: RoadmapResponseContent = Field(..., description="Generated roadmap content")
    created_at: str = Field(..., description="Creation timestamp")
    expires_at: str = Field(..., description="Expiration timestamp")


class RoadmapApiResponse(BaseModel):
    """API response for roadmap generation."""

    result: RoadmapResponse = Field(..., description="Generated roadmap")
    cache_info: Optional[Dict[str, Any]] = Field(None, description="Cache information")


class RelatedProposalsResponse(BaseModel):
    """Response model for related proposals search."""
    
    related_proposals: List[RelatedProposal] = Field(default_factory=list, description="List of related proposals")
    query: str = Field(..., description="The query that was used for the search")
    from_cache: bool = Field(False, description="Whether this response came from cache")
    cache_key: Optional[str] = Field(None, description="Cache key used for this request")


#-----------------------------------------------------------------------------
# 4. Response models
#-----------------------------------------------------------------------------

class AnalysisResponse(BaseModel):
    """Response model for proposal analysis."""
    
    id: UUID = Field(None, description="Analysis ID")
    proposal_id: str = Field(None, description="Proposal ID")
    result: str = Field(None, description="Analysis result")
    confidence: float = Field(None, description="Confidence score")
    details: str = Field(None, description="Analysis details")
    created_at: datetime = Field(None, description="Creation timestamp")
    updated_at: datetime = Field(None, description="Last update timestamp")
    arguments: Optional[ProposalArguments] = Field(None, description="Proposal arguments")


class AnalyzeResponse(BaseModel):
    """Response for proposal analysis, matching Rust implementation exactly."""
    
    summary: str
    goals_and_motivation: Optional[EvaluationResult] = None
    measurable_outcomes: Optional[EvaluationResult] = None
    budget: Optional[EvaluationResult] = None
    technical_specifications: Optional[EvaluationResult] = None
    language_quality: Optional[EvaluationResult] = None
    
    # Allow additional fields for custom criteria
    class Config:
        extra = "allow"


class WebhookEventResponse(BaseModel):
    """Response model for webhook events."""
    
    id: UUID = Field(None, description="Event ID")
    event_type: str = Field(None, description="Event type")
    processed: bool = Field(None, description="Whether the event has been processed")
    created_at: datetime = Field(None, description="Creation timestamp")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")


class CacheStats(BaseModel):
    """Response model for cache statistics."""
    
    total_entries: int = Field(None, description="Total number of cache entries")
    hit_rate: float = Field(None, description="Cache hit rate")
    miss_rate: float = Field(None, description="Cache miss rate")
    size_bytes: int = Field(None, description="Cache size in bytes")


class CacheEntry(BaseModel):
    """Response model for cache entries."""
    
    key: str = Field(None, description="Cache key")
    created_at: datetime = Field(None, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    size_bytes: int = Field(None, description="Entry size in bytes")


class CacheListResponse(BaseModel):
    """Response model for listing cache entries."""
    
    entries: List[CacheEntry] = Field(None, description="List of cache entries")
    total: int = Field(None, description="Total number of entries")


class CacheInvalidateRequest(BaseModel):
    """Request model for invalidating cache entries."""
    
    keys: List[str] = Field(None, description="List of cache keys to invalidate")


class CacheRefreshRequest(BaseModel):
    """Request model for refreshing cache entries."""
    
    keys: List[str] = Field(None, description="List of cache keys to refresh")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    detail: str = Field(None, description="Error detail")


class ChatRequest(BaseModel):
    """Chat request model."""
    
    message: str = Field(None, description="User message")


class ChatResponse(BaseModel):
    """Chat response model."""
    
    response: str = Field(None, description="Agent response")
