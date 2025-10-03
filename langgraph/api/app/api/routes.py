"""
API routes for the application.
"""

# Standard library imports
import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

# Local application imports
from app.auth import get_api_key
from app.config import settings
from app.db import get_session
from app.db.models import Analysis
from app.schemas import (
    AnalysisResponse, AnalyzeResponse, ArgumentsRequest, CacheEntry, CacheInvalidateRequest,
    CacheListResponse, CacheRefreshRequest, CacheStats, ChatRequest,
    ChatResponse, CustomEvaluationRequest, CustomEvaluationResponse, DeepResearchRequest, DeepResearchApiResponse,
    EvaluationResult, ProposalArguments, ProposalArgumentsResponse, ProposalRequest, RelatedProposalsResponse,
    RelatedProposal, RoadmapRequest, RoadmapResponse, RoadmapApiResponse
)
from app.services.langgraph.context import Context
from app.services.langgraph.graph import graph
from app.tracing import trace_function, trace_span
from app.utils import extract_json_from_markdown, try_extract_json_from_markdown

# Helper functions
def is_valid_argument(arg: str) -> bool:
    """Check if an argument is valid (not empty or placeholder)."""
    if not arg or not isinstance(arg, str):
        return False
    
    # Check if it's too short
    if len(arg.strip()) < 5:
        return False
    
    # Check for placeholder text
    placeholders = [
        "placeholder", "example", "insert", "argument here", 
        "to be added", "to be determined", "tbd", "n/a", "none"
    ]
    
    lower_arg = arg.lower()
    for placeholder in placeholders:
        if placeholder in lower_arg:
            return False
    
    return True


# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/health", summary="Health check endpoint")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/info", summary="Information about the API")
async def info():
    """Get information about the API."""
    return {
        "name": settings.PROJECT_NAME,
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }


@router.get("/test")
async def test_api_key(
    api_key: str = Depends(get_api_key),
):
    """Test API key authentication."""
    return {"message": "API key is valid"}


@router.post("/pre-filter", response_model=AnalyzeResponse)
@trace_function("analyze_proposal")
async def analyze_proposal(
    request: ProposalRequest,
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_session),
):
    """
    Analyze a proposal and return the analysis result.
    """
    logger.info(f"Analyzing proposal: {request.proposal_id or 'new'}")
    
    # Validate request
    if not request.proposal_text or len(request.proposal_text.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proposal description must be at least 10 characters long",
        )
    
    try:
        # Create context
        context = Context(
            model=f"{settings.WEI_AGENT_AI_MODEL_PROVIDER}/{settings.WEI_AGENT_AI_MODEL_NAME}",
            openrouter_api_key=settings.WEI_AGENT_OPEN_ROUTER_API_KEY,
            exa_api_key=settings.WEI_AGENT_EXA_API_KEY
        )
        
        # Set proposal text in context
        context.proposal_text = request.proposal_text
        
        # Run the graph
        from langgraph.runtime import Runtime
        runtime = Runtime(context=context)
        
        # Use the graph for analysis
        result = await graph.ainvoke({
            "task": "analyze_proposal",
            "proposal_text": request.proposal_text
        }, runtime=runtime)
        
        # Debug log the result
        logger.info(f"Graph result: {result}")
        
        # Extract the analysis result
        if "analysis_result" in result:
            analysis_data = result["analysis_result"]
            
            # Convert each evaluation category to EvaluationResult objects
            for key in ["goals_and_motivation", "measurable_outcomes", "budget", "technical_specifications", "language_quality"]:
                if key in analysis_data:
                    analysis_data[key] = EvaluationResult(
                        status=analysis_data[key].get("status", "n/a"),
                        justification=analysis_data[key].get("justification", ""),
                        suggestions=analysis_data[key].get("suggestions", [])
                    )
            
            # Return the response with dynamic fields
            return AnalyzeResponse(**analysis_data)
        else:
            # If no analysis result, return a default response
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to analyze proposal: no analysis result returned",
            )
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error analyzing proposal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze proposal: {str(e)}",
        )


@router.post("/pre-filter/arguments", response_model=ProposalArgumentsResponse)
@trace_function("get_proposal_arguments")
async def get_proposal_arguments(
    request: ArgumentsRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Generate arguments for and against a proposal.
    """
    logger.info(f"Generating arguments for proposal: {request.proposal_id or 'new'}")
    
    try:
        # Create context
        context = Context(
            model=f"{settings.WEI_AGENT_AI_MODEL_PROVIDER}/{settings.WEI_AGENT_AI_MODEL_NAME}",
            openrouter_api_key=settings.WEI_AGENT_OPEN_ROUTER_API_KEY,
            exa_api_key=settings.WEI_AGENT_EXA_API_KEY,
            max_arguments=request.max_arguments or 5
        )
        
        # Set proposal text in context
        context.proposal_text = request.proposal_text
        
        # Run the graph
        from langgraph.runtime import Runtime
        runtime = Runtime(context=context)
        
        # Use the graph for argument generation
        result = await graph.ainvoke(
            {"proposal_text": request.proposal_text, "task": "generate_arguments"}, 
            runtime=runtime
        )
        
        # Extract the arguments
        if "arguments" in result:
            arguments = result["arguments"]
            
            # If arguments is a string (possibly JSON in markdown), try to parse it
            if isinstance(arguments, str):
                success, parsed_result = extract_json_from_markdown(arguments)
                if success:
                    arguments = parsed_result
            
            # Check if arguments is a dictionary with the expected keys
            if isinstance(arguments, dict) and "for_proposal" in arguments and "against" in arguments:
                # Filter out placeholder arguments
                for_proposal = [arg for arg in arguments["for_proposal"] if is_valid_argument(arg)]
                against = [arg for arg in arguments["against"] if is_valid_argument(arg)]
                
                # Ensure we have at least one argument on each side
                if not for_proposal:
                    for_proposal = ["No supporting arguments were generated."]
                if not against:
                    against = ["No opposing arguments were generated."]
                
                # Create arguments object
                proposal_arguments = ProposalArguments(
                    for_proposal=for_proposal,
                    against=against
                )
                
                # Return wrapped response to match Rust implementation
                return ProposalArgumentsResponse(
                    arguments=proposal_arguments,
                    from_cache=False  # We're not implementing caching in this version
                )
        
        # Fallback to empty arguments if no valid arguments were found
        proposal_arguments = ProposalArguments(
            for_proposal=["No supporting arguments were generated."],
            against=["No opposing arguments were generated."]
        )
        
        # Return wrapped response
        return ProposalArgumentsResponse(
            arguments=proposal_arguments,
            from_cache=False
        )
    except Exception as e:
        # Log the error
        logger.error(f"Error generating arguments: {str(e)}")
        
        # Return fallback arguments
        proposal_arguments = ProposalArguments(
            for_proposal=["Error generating supporting arguments."],
            against=["Error generating opposing arguments."]
        )
        
        # Return wrapped response
        return ProposalArgumentsResponse(
            arguments=proposal_arguments,
            from_cache=False
        )


@router.post("/pre-filter/custom", response_model=CustomEvaluationResponse)
@trace_function("custom_evaluate_proposal")
async def custom_evaluate_proposal(
    request: CustomEvaluationRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Evaluate a proposal using custom criteria.
    """
    logger.info("Custom evaluating proposal")
    
    try:
        # Create context
        context = Context(
            model=f"{settings.WEI_AGENT_AI_MODEL_PROVIDER}/{settings.WEI_AGENT_AI_MODEL_NAME}",
            openrouter_api_key=settings.WEI_AGENT_OPEN_ROUTER_API_KEY,
            exa_api_key=settings.WEI_AGENT_EXA_API_KEY
        )
        
        # Set proposal text and custom criteria in context
        context.proposal_text = request.proposal_text
        context.custom_criteria = request.custom_criteria
        
        # Run the graph
        from langgraph.runtime import Runtime
        runtime = Runtime(context=context)
        
        # Use the graph for custom evaluation
        result = await graph.ainvoke(
            {
                "proposal_text": request.proposal_text, 
                "custom_criteria": request.custom_criteria,
                "task": "custom_evaluate"
            }, 
            runtime=runtime
        )
        
        # Extract the evaluation result
        if "custom_evaluation" in result:
            evaluation = result["custom_evaluation"]
            
            # If evaluation is a string (possibly JSON in markdown), try to parse it
            if isinstance(evaluation, str):
                success, parsed_result = extract_json_from_markdown(evaluation)
                if success and isinstance(parsed_result, dict):
                    evaluation = parsed_result
                else:
                    logger.warning(f"Failed to parse custom evaluation result: {parsed_result}")
                    evaluation = {}
            
            # Return the response in the correct format
            return CustomEvaluationResponse(
                summary=evaluation.get("summary", "No summary provided"),
                response_map=evaluation.get("response_map", {})
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to evaluate proposal: no evaluation result returned",
            )
    except Exception as e:
        logger.error(f"Error custom evaluating proposal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate proposal: {str(e)}",
        )


# Database operations

async def create_analysis(
    db: AsyncSession,
    proposal_id: str,
    result: str,
    confidence: float,
    details: str,
    arguments: Optional[Dict[str, List[str]]] = None,
    content: Optional[str] = None
) -> Analysis:
    """
    Create and save an analysis record in the database.
    """
    # Create analysis record
    analysis = Analysis(
        proposal_id=proposal_id,
        result=result,
        confidence=confidence,
        details=details,
    )
    
    # Add arguments if provided
    if arguments:
        analysis.arguments = arguments
    
    # Save to database
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    
    return analysis


async def get_analysis_by_id(db: AsyncSession, id: uuid.UUID) -> Analysis:
    """
    Get an analysis by ID from the database.
    """
    analysis = await db.get(Analysis, id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {id} not found",
        )
    
    return analysis


async def find_analysis_by_proposal_id(db: AsyncSession, proposal_id: str) -> Analysis:
    """
    Find an analysis by proposal ID in the database.
    """
    from sqlalchemy import select
    query = select(Analysis).where(Analysis.proposal_id == proposal_id).order_by(Analysis.created_at.desc())
    result = await db.execute(query)
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis for proposal {proposal_id} not found",
        )
    
    return analysis


async def find_analyses_by_proposal_id(db: AsyncSession, proposal_id: str) -> List[Analysis]:
    """
    Find all analyses for a proposal in the database.
    """
    from sqlalchemy import select
    query = select(Analysis).where(Analysis.proposal_id == proposal_id).order_by(Analysis.created_at.desc())
    result = await db.execute(query)
    analyses = result.scalars().all()
    
    if not analyses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No analyses found for proposal {proposal_id}",
        )
    
    return analyses


@router.get("/pre-filter/{id}", response_model=AnalysisResponse)
@trace_function("get_analysis")
async def get_analysis(
    id: uuid.UUID = Path(...),
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_session),
):
    """
    Get an analysis by ID.
    """
    logger.info(f"Getting analysis: {id}")
    
    # Get the analysis from the database
    analysis = await get_analysis_by_id(db, id)
    
    # Convert to response model
    response = AnalysisResponse(
        id=analysis.id,
        proposal_id=analysis.proposal_id,
        result=analysis.result,
        confidence=analysis.confidence,
        details=analysis.details,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )
    
    # Add arguments if available
    if hasattr(analysis, 'arguments') and analysis.arguments:
        response.arguments = ProposalArguments(**analysis.arguments)
    
    return response


@router.get("/pre-filter/proposals/{id}", response_model=AnalysisResponse)
@trace_function("get_analysis_by_proposal_id")
async def get_analysis_by_proposal_id(
    id: str = Path(...),
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_session),
):
    """
    Get an analysis by proposal ID.
    """
    logger.info(f"Getting analysis for proposal: {id}")
    
    # Get the analysis from the database
    analysis = await find_analysis_by_proposal_id(db, id)
    
    # Convert to response model
    response = AnalysisResponse(
        id=analysis.id,
        proposal_id=analysis.proposal_id,
        result=analysis.result,
        confidence=analysis.confidence,
        details=analysis.details,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )
    
    # Add arguments if available
    if hasattr(analysis, 'arguments') and analysis.arguments:
        response.arguments = ProposalArguments(**analysis.arguments)
    
    return response


@router.get("/pre-filter/proposal/{proposal_id}", response_model=List[AnalysisResponse])
@trace_function("get_proposal_analyses")
async def get_proposal_analyses(
    proposal_id: str = Path(...),
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_session),
):
    """
    Get all analyses for a proposal.
    """
    logger.info(f"Getting all analyses for proposal: {proposal_id}")
    
    # Get analyses from the database
    analyses = await find_analyses_by_proposal_id(db, proposal_id)
    
    # Convert to response models
    result = []
    for analysis in analyses:
        response = AnalysisResponse(
            id=analysis.id,
            proposal_id=analysis.proposal_id,
            result=analysis.result,
            confidence=analysis.confidence,
            details=analysis.details,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at,
        )
        
        # Add arguments if available
        if hasattr(analysis, 'arguments') and analysis.arguments:
            response.arguments = ProposalArguments(**analysis.arguments)
        
        result.append(response)
    
    return result


@router.get("/related-proposals", response_model=RelatedProposalsResponse)
async def search_related_proposals(
    query: str = Query(..., description="The search query"),
    limit: int = Query(5, description="Maximum number of results to return", ge=1, le=10),
    api_key: str = Depends(get_api_key),
):
    """
    Search for related proposals.
    """
    logger.info(f"Searching for related proposals: {query} (limit: {limit})")
    
    try:
        # Create cache key
        cache_key = f"related-proposals:{query}:{limit}"
        logger.info(f"Would check cache for key: {cache_key}")
        
        # Simulate cache check
        cached_result = None  # In a real implementation, this would be the cached result
        
        if cached_result:
            logger.info(f"Cache hit for query: {query}")
            # Return cached result
            return cached_result
        else:
            logger.info(f"Cache miss for query: {query}, performing fresh search")
            
            # Create context with API keys
            from dotenv import load_dotenv
            load_dotenv()
            
            # Get API keys directly from environment
            exa_api_key = os.getenv("WEI_AGENT_EXA_API_KEY")
            openrouter_api_key = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
            model_provider = os.getenv("WEI_AGENT_AI_MODEL_PROVIDER", "openai")
            model_name = os.getenv("WEI_AGENT_AI_MODEL_NAME", "gpt-4o-mini")
            
            # Log the API keys for debugging (mask them for security)
            if exa_api_key:
                masked_exa = exa_api_key[:4] + "*" * (len(exa_api_key) - 8) + exa_api_key[-4:]
                logger.info(f"Found EXA API key: {masked_exa}")
            if openrouter_api_key:
                masked_or = openrouter_api_key[:4] + "*" * (len(openrouter_api_key) - 8) + openrouter_api_key[-4:]
                logger.info(f"Found OpenRouter API key: {masked_or}")
            
            context = Context(
                model=f"{model_provider}/{model_name}",
                openrouter_api_key=openrouter_api_key,
                exa_api_key=exa_api_key
            )
            
            # Run the graph
            from langgraph.runtime import Runtime
            runtime = Runtime(context=context)
            
            # Use the graph for search
            result = await graph.ainvoke(
                {"search_query": query, "task": "search_related_proposals"}, 
                runtime=runtime
            )
            
            # Get search results
            search_results = result.get("search_results", [])
            
            # Limit the results
            search_results = search_results[:limit]
            
            # Convert to RelatedProposal objects
            related_proposals = []
            for item in search_results:
                related_proposals.append(
                    RelatedProposal(
                        id=item.get("id", ""),
                        title=item.get("title", ""),
                        score=item.get("score", 0.0),
                        content=item.get("content"),
                        url=item.get("url")
                    )
                )
            
            # Create the response
            now = datetime.now(timezone.utc)  # Use UTC time to match Rust implementation
            response = RelatedProposalsResponse(
                related_proposals=related_proposals,
                query=query,
                from_cache=False,  # Always false since we're not implementing caching
                cache_key=cache_key
            )
            
            # In a real implementation, we would store this in a cache
            # For now, just log that we would cache it
            logger.info(f"Would cache result with key: {cache_key}")
            
            return response
    except Exception as e:
        logger.error(f"Error searching for related proposals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search for related proposals: {str(e)}",
        )


@router.get("/community")
async def get_community_analysis(
    topic: str,
    api_key: str = Depends(get_api_key),
):
    """
    Get cached community analysis results.
    """
    logger.info(f"Getting community analysis for topic: {topic}")
    
    try:
        # In a real implementation, this would check a cache
        # For now, just call the analyze_community endpoint with a note that we would check cache
        cache_key = f"community:{topic}"
        logger.info(f"Would check cache for key: {cache_key}")
        
        # Simulate cache check
        cached_result = None  # In a real implementation, this would be the cached result
        
        if cached_result:
            logger.info(f"Cache hit for topic: {topic}")
            # Return cached result
            return cached_result
        else:
            logger.info(f"Cache miss for topic: {topic}, performing fresh analysis")
            # Perform fresh analysis
            request = DeepResearchRequest(topic=topic)
            return await analyze_community(request, api_key)
    except Exception as e:
        logger.error(f"Error getting community analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get community analysis: {str(e)}",
        )


@router.post("/community", response_model=DeepResearchApiResponse)
async def analyze_community(
    request: DeepResearchRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Analyze community discourse for a protocol/topic.
    """
    logger.info(f"Analyzing community for topic: {request.topic}")
    
    try:
        # Create context with all necessary API keys
        import os
        from dotenv import load_dotenv
        
        # Load environment variables from .env file
        load_dotenv()
        
        # Get API keys directly from environment
        exa_api_key = os.getenv("WEI_AGENT_EXA_API_KEY")
        openrouter_api_key = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
        model_provider = os.getenv("WEI_AGENT_AI_MODEL_PROVIDER", "openai")
        model_name = os.getenv("WEI_AGENT_AI_MODEL_NAME", "gpt-4o-mini")
        
        # Log the API keys for debugging (mask them for security)
        if exa_api_key:
            masked_exa = exa_api_key[:4] + "*" * (len(exa_api_key) - 8) + exa_api_key[-4:]
            logger.info(f"Found EXA API key: {masked_exa}")
        if openrouter_api_key:
            masked_or = openrouter_api_key[:4] + "*" * (len(openrouter_api_key) - 8) + openrouter_api_key[-4:]
            logger.info(f"Found OpenRouter API key: {masked_or}")
        
        context = Context(
            model=f"{model_provider}/{model_name}",
            openrouter_api_key=openrouter_api_key,
            exa_api_key=exa_api_key
        )
        
        # Set topic in context
        context.topic = request.topic
        
        # Log API key status for debugging
        if context.exa_api_key:
            logger.info("EXA API key is set and will be used for research")
        else:
            logger.warning("EXA API key is not set, will fall back to other search methods")
        
        # Run the graph
        from langgraph.runtime import Runtime
        runtime = Runtime(context=context)
        
        # Use the graph for deep research
        result = await graph.ainvoke({
            "task": "deep_research",
            "topic": request.topic
        }, runtime=runtime)
        
        # Extract the deep research result
        if "deep_research_result" in result:
            research_data = result["deep_research_result"]
            
            # Create the response
            now = datetime.now(timezone.utc)  # Use UTC time to match Rust implementation
            expires_at = now + timedelta(hours=24)  # Cache for 24 hours
            
            # Check if we should cache this result
            should_cache = len(research_data.get("resources", [])) > 0
            cache_key = None
            
            if should_cache:
                # In a real implementation, we would store this in a cache
                # For now, just log that we would cache it
                cache_key = f"community:{research_data['topic']}"
                logger.info(f"Would cache result with key: {cache_key}")
            
            return DeepResearchApiResponse(
                topic=research_data["topic"],
                resources=research_data["resources"],
                from_cache=False,  # Always false since we're not implementing caching
                created_at=now,
                expires_at=expires_at
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to analyze community: no research result returned",
            )
    except Exception as e:
        logger.error(f"Error analyzing community: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze community: {str(e)}",
        )


@router.get("/roadmap")
async def get_cached_roadmap(
    subject: str = Query(..., description="Subject of the roadmap"),
    api_key: str = Depends(get_api_key),
):
    """
    Get cached roadmap.
    """
    logger.info(f"Getting cached roadmap for subject: {subject}")
    
    try:
        # Create cache key
        cache_key = f"roadmap:{subject}"
        logger.info(f"Would check cache for key: {cache_key}")
        
        # Simulate cache check
        cached_result = None  # In a real implementation, this would be the cached result
        
        if cached_result:
            logger.info(f"Cache hit for subject: {subject}")
            # Return cached result
            return cached_result
        else:
            logger.info(f"Cache miss for subject: {subject}, need to generate new roadmap")
            # Return a 404 if not found in cache
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No cached roadmap found for subject: {subject}",
            )
    except Exception as e:
        logger.error(f"Error getting cached roadmap: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cached roadmap: {str(e)}",
        )


@router.post("/roadmap", response_model=RoadmapApiResponse)
async def generate_roadmap(
    request: RoadmapRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Generate roadmap.
    """
    logger.info(f"Generating roadmap for subject: {request.subject}")
    
    try:
        # Validate required fields
        if not request.subject or not request.subject.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subject cannot be empty",
            )
        
        if not request.kind or not request.kind.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kind cannot be empty",
            )
        
        if not request.scope or not request.scope.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scope cannot be empty",
            )
        
        # Validate date formats if provided
        if request.from_date:
            try:
                datetime.strptime(request.from_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="From date must be in YYYY-MM-DD format",
                )
        
        if request.to_date:
            try:
                datetime.strptime(request.to_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="To date must be in YYYY-MM-DD format",
                )
        
        # Validate date range if both dates are provided
        if request.from_date and request.to_date and request.from_date > request.to_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="From date must be before or equal to To date",
            )
        
        # Create context with API keys
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get API keys directly from environment
        openrouter_api_key = os.getenv("WEI_AGENT_OPEN_ROUTER_API_KEY")
        model_provider = os.getenv("WEI_AGENT_AI_MODEL_PROVIDER", "openai")
        model_name = os.getenv("WEI_AGENT_ROADMAP_MODEL_NAME", "perplexity/sonar-pro")
        
        # Log the API keys for debugging (mask them for security)
        if openrouter_api_key:
            masked_or = openrouter_api_key[:4] + "*" * (len(openrouter_api_key) - 8) + openrouter_api_key[-4:]
            logger.info(f"Found OpenRouter API key: {masked_or}")
        
        context = Context(
            model=f"{model_provider}/{model_name}",
            openrouter_api_key=openrouter_api_key
        )
        
        # Run the graph
        from langgraph.runtime import Runtime
        runtime = Runtime(context=context)
        
        # Convert request to dict for the graph
        roadmap_request = {
            "subject": request.subject,
            "kind": request.kind,
            "scope": request.scope,
            "from_date": request.from_date,
            "to_date": request.to_date,
            "additional_context": request.additional_context
        }
        
        # Use the graph for roadmap generation
        result = await graph.ainvoke(
            {"roadmap_request": roadmap_request, "task": "generate_roadmap"}, 
            runtime=runtime
        )
        
        # Check for errors
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"],
            )
        
        # Get roadmap result
        roadmap_result = result.get("roadmap_result")
        if not roadmap_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate roadmap: no result returned",
            )
        
        # Process the response to ensure it matches the expected format
        try:
            # Return the response
            return RoadmapApiResponse(
                result=roadmap_result,
                cache_info=None  # No cache info for fresh generation
            )
        except Exception as e:
            # If there's an error with the response format, return a raw JSON response
            logger.error(f"Error formatting roadmap response: {str(e)}")
            return {
                "result": roadmap_result,
                "cache_info": None
            }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate roadmap: {str(e)}",
        )


# Cache management routes

@router.get("/cache", response_model=CacheListResponse)
async def list_cached_queries(
    api_key: str = Depends(get_api_key),
):
    """
    List cached queries.
    """
    logger.info("Listing cached queries")
    
    # This is a placeholder - implement actual cache listing logic
    return CacheListResponse(
        entries=[
            CacheEntry(
                key="example_key",
                created_at=datetime.now(),
                expires_at=datetime.now(),
                size_bytes=1024,
            )
        ],
        total=1,
    )


@router.get("/cache/stats", response_model=CacheStats)
async def get_cache_stats(
    api_key: str = Depends(get_api_key),
):
    """
    Get cache statistics.
    """
    logger.info("Getting cache statistics")
    
    # This is a placeholder - implement actual cache stats logic
    return CacheStats(
        total_entries=10,
        hit_rate=0.75,
        miss_rate=0.25,
        size_bytes=10240,
    )


@router.post("/cache/invalidate")
async def invalidate_cache(
    request: CacheInvalidateRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Invalidate cache entries.
    """
    logger.info(f"Invalidating cache entries: {request.keys}")
    
    # This is a placeholder - implement actual cache invalidation logic
    return {"message": f"Invalidated {len(request.keys)} cache entries"}


@router.post("/cache/refresh")
async def refresh_cache(
    request: CacheRefreshRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Refresh cache entries.
    """
    logger.info(f"Refreshing cache entries: {request.keys}")
    
    # This is a placeholder - implement actual cache refresh logic
    return {"message": f"Refreshed {len(request.keys)} cache entries"}


@router.post("/cache/cleanup")
async def cleanup_cache(
    api_key: str = Depends(get_api_key),
):
    """
    Clean up cache.
    """
    logger.info("Cleaning up cache")
    
    # This is a placeholder - implement actual cache cleanup logic
    return {"message": "Cache cleanup initiated"}


@router.post("/chat", response_model=ChatResponse)
@trace_function("chat")
async def chat(
    request: ChatRequest,
):
    """
    Chat with the Wei Agent.
    """
    try:
        # Create context
        context = Context(
            model=f"{settings.WEI_AGENT_AI_MODEL_PROVIDER}/{settings.WEI_AGENT_AI_MODEL_NAME}",
            openrouter_api_key=settings.WEI_AGENT_OPEN_ROUTER_API_KEY,
            exa_api_key=settings.WEI_AGENT_EXA_API_KEY
        )
        
        # Create messages
        messages = [HumanMessage(content=request.message)]
        
        # Run the graph
        from langgraph.runtime import Runtime
        runtime = Runtime(context=context)
        
        # Use the graph
        result = await graph.ainvoke({
            "task": "chat",
            "messages": messages
        }, runtime=runtime)
        
        # Extract the response
        if "messages" in result and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            if isinstance(last_message, AIMessage):
                response = last_message.content
            else:
                response = str(last_message)
        else:
            response = "No response from the agent"
        
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}",
        )
