"""
Schema models for request/response data.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field


class ProposalRequest(BaseModel):
    """Request model for proposal analysis."""
    
    content: str = Field(None, description="The proposal content to analyze")
    proposal_id: Optional[str] = Field(None, description="Optional proposal ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class ArgumentsRequest(BaseModel):
    """Request model for generating proposal arguments."""
    
    content: str = Field(None, description="The proposal content to analyze")
    proposal_id: Optional[str] = Field(None, description="Optional proposal ID")
    max_arguments: Optional[int] = Field(5, description="Maximum number of arguments to generate per side")


class CustomEvaluationRequest(BaseModel):
    """Request model for custom proposal evaluation."""
    
    content: str = Field(None, description="The proposal content to evaluate")
    custom_criteria: Dict[str, Any] = Field(None, description="Custom evaluation criteria")


class ProposalArguments(BaseModel):
    """Model for proposal arguments."""
    
    for_proposal: List[str] = Field(default_factory=list, description="Arguments supporting the proposal")
    against: List[str] = Field(default_factory=list, description="Arguments against the proposal")


class EvaluationResult(BaseModel):
    """Model for evaluation results."""
    
    status: str = Field(None, description="Status of the evaluation (pass/fail)")
    justification: str = Field(None, description="Justification for the evaluation")
    suggestions: Optional[List[str]] = Field(None, description="Suggestions for improvement")


class CustomEvaluationResponse(BaseModel):
    """Response model for custom proposal evaluation."""
    
    summary: str = Field(None, description="Summary of the evaluation")
    response_map: Dict[str, EvaluationResult] = Field(None, description="Map of criteria to evaluation results")


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
