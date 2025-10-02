"""
API routes for the application.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_api_key
from app.db import get_session
from app.db.models import Analysis, WebhookEvent
from app.utils import extract_json_from_markdown, try_extract_json_from_markdown
from app.schemas import (
    AnalysisResponse, ArgumentsRequest, CacheEntry, CacheInvalidateRequest,
    CacheListResponse, CacheRefreshRequest, CacheStats, ChatRequest,
    ChatResponse, CustomEvaluationRequest, CustomEvaluationResponse,
    ProposalArguments, ProposalRequest, WebhookEventResponse
)


async def create_analysis(
    db: AsyncSession,
    proposal_id: str,
    result: str,
    confidence: float,
    details: str,
    arguments: Optional[Dict[str, List[str]]] = None
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

# Import the graph
import sys
import os
import asyncio

# Import from local services
from app.services.langgraph.graph import graph
from app.services.langgraph.context import Context
from langchain_core.messages import HumanMessage, AIMessage

# Import config and tracing
from app.config import (
    WEI_AGENT_AI_MODEL_PROVIDER, WEI_AGENT_AI_MODEL_NAME,
    WEI_AGENT_OPEN_ROUTER_API_KEY, WEI_AGENT_EXA_API_KEY
)
from app.tracing import trace_function, trace_span

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/test")
async def test_api_key(
    api_key: str = Depends(get_api_key),
):
    """Test API key authentication."""
    return {"message": "API key is valid"}


@router.post("/pre-filter", response_model=AnalysisResponse)
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
    
    try:
        # Create context
        context = Context(
            model=f"{WEI_AGENT_AI_MODEL_PROVIDER}/{WEI_AGENT_AI_MODEL_NAME}",
            openrouter_api_key=WEI_AGENT_OPEN_ROUTER_API_KEY,
            exa_api_key=WEI_AGENT_EXA_API_KEY
        )
        
        # Set proposal text in context
        context.proposal_text = request.content
        
        # Run the graph
        from langgraph.runtime import Runtime
        runtime = Runtime(context=context)
        
        # Use the graph for analysis
        result = await graph.ainvoke({
            "task": "analyze_proposal",
            "proposal_text": request.content
        }, runtime=runtime)
        
        # Extract the analysis result
        if "analysis_result" in result:
            analysis_data = result["analysis_result"]
            
            # Extract arguments if available
            arguments = result.get("arguments")
            
            # Create and save analysis record
            analysis = await create_analysis(
                db,
                proposal_id=request.proposal_id or str(uuid.uuid4()),
                result=analysis_data.get("result", "unknown"),
                confidence=float(analysis_data.get("confidence", 0.5)),
                details=analysis_data.get("details", "No details provided"),
                arguments=arguments
            )
            
            # Return response
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
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to analyze proposal: no analysis result returned",
            )
    except Exception as e:
        logger.error(f"Error analyzing proposal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze proposal: {str(e)}",
        )


@router.post("/pre-filter/arguments", response_model=ProposalArguments)
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
            model=f"{WEI_AGENT_AI_MODEL_PROVIDER}/{WEI_AGENT_AI_MODEL_NAME}",
            openrouter_api_key=WEI_AGENT_OPEN_ROUTER_API_KEY,
            exa_api_key=WEI_AGENT_EXA_API_KEY,
            max_arguments=request.max_arguments or 5
        )
        
        # Set proposal text in context
        context.proposal_text = request.content
        
        # Run the graph
        from langgraph.runtime import Runtime
        runtime = Runtime(context=context)
        
        # Use the graph for argument generation
        result = await graph.ainvoke(
            {"proposal_text": request.content, "task": "generate_arguments"}, 
            runtime=runtime
        )
        
        # Extract the arguments
        if "arguments" in result:
            arguments = result["arguments"]
            
            # If arguments is a string (possibly JSON in markdown), try to parse it
            if isinstance(arguments, str):
                success, parsed_result = extract_json_from_markdown(arguments)
                if success and isinstance(parsed_result, dict):
                    arguments = parsed_result
                else:
                    logger.warning(f"Failed to parse arguments result: {parsed_result}")
                    arguments = {}
            
            # Extract and clean up arguments
            for_proposal = arguments.get("for_proposal", [])
            against = arguments.get("against", [])
            
            # Filter out placeholder or empty arguments
            if isinstance(for_proposal, list):
                for_proposal = [arg for arg in for_proposal if arg and not arg.lower().startswith("placeholder")]
            else:
                for_proposal = []
                
            if isinstance(against, list):
                against = [arg for arg in against if arg and not arg.lower().startswith("placeholder")]
            else:
                against = []
            
            # Ensure minimum arguments per side with fallback messages
            if not for_proposal:
                for_proposal = ["No supporting arguments were generated."]
                
            if not against:
                against = ["No opposing arguments were generated."]
            
            return ProposalArguments(
                for_proposal=for_proposal,
                against=against,
            )
        else:
            # Fallback to empty arguments with explanatory messages
            return ProposalArguments(
                for_proposal=["No supporting arguments were generated."],
                against=["No opposing arguments were generated."]
            )
    except Exception as e:
        logger.error(f"Error generating arguments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate arguments: {str(e)}",
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
            model=f"{WEI_AGENT_AI_MODEL_PROVIDER}/{WEI_AGENT_AI_MODEL_NAME}",
            openrouter_api_key=WEI_AGENT_OPEN_ROUTER_API_KEY,
            exa_api_key=WEI_AGENT_EXA_API_KEY
        )
        
        # Set proposal text and custom criteria in context
        context.proposal_text = request.content
        context.custom_criteria = request.custom_criteria
        
        # Run the graph
        from langgraph.runtime import Runtime
        runtime = Runtime(context=context)
        
        # Use the graph for custom evaluation
        result = await graph.ainvoke(
            {
                "proposal_text": request.content, 
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
            
            return CustomEvaluationResponse(
                summary=evaluation.get("summary", "No summary provided"),
                response_map=evaluation.get("response_map", {}),
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


@router.get("/related-proposals")
async def search_related_proposals(
    query: str = Query(None),
    api_key: str = Depends(get_api_key),
):
    """
    Search for related proposals.
    """
    logger.info(f"Searching for related proposals: {query}")
    
    try:
        # Create context
        context = Context(
            model=f"{WEI_AGENT_AI_MODEL_PROVIDER}/{WEI_AGENT_AI_MODEL_NAME}",
            openrouter_api_key=WEI_AGENT_OPEN_ROUTER_API_KEY,
            exa_api_key=WEI_AGENT_EXA_API_KEY
        )
        
        # Run the graph
        from langgraph.runtime import Runtime
        runtime = Runtime(context=context)
        
        # Use the graph for search
        result = await graph.ainvoke(
            {"search_query": query, "task": "search_related_proposals"}, 
            runtime=runtime
        )
        
        # Return the search results
        return result.get("search_results", [])
    except Exception as e:
        logger.error(f"Error searching for related proposals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search for related proposals: {str(e)}",
        )


@router.get("/community")
async def get_community_analysis(
    api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_session),
):
    """
    Get community analysis.
    """
    logger.info("Getting community analysis")
    
    # This is a placeholder - implement actual community analysis logic
    return {"message": "Community analysis endpoint"}


@router.post("/community")
async def analyze_community(
    api_key: str = Depends(get_api_key),
):
    """
    Analyze community.
    """
    logger.info("Analyzing community")
    
    # This is a placeholder - implement actual community analysis logic
    return {"message": "Community analysis initiated"}


@router.get("/roadmap")
async def get_cached_roadmap(
    api_key: str = Depends(get_api_key),
):
    """
    Get cached roadmap.
    """
    logger.info("Getting cached roadmap")
    
    # This is a placeholder - implement actual roadmap retrieval logic
    return {"message": "Roadmap endpoint"}


@router.post("/roadmap")
async def generate_roadmap(
    api_key: str = Depends(get_api_key),
):
    """
    Generate roadmap.
    """
    logger.info("Generating roadmap")
    
    # This is a placeholder - implement actual roadmap generation logic
    return {"message": "Roadmap generation initiated"}


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
            model=f"{WEI_AGENT_AI_MODEL_PROVIDER}/{WEI_AGENT_AI_MODEL_NAME}",
            openrouter_api_key=WEI_AGENT_OPEN_ROUTER_API_KEY,
            exa_api_key=WEI_AGENT_EXA_API_KEY
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
