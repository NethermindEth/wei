"""
Repository for Analysis model operations.
"""

# Standard library imports
import uuid
from typing import List, Optional, Dict

# Third-party imports
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from app.db.models import Analysis


class AnalysisRepository:
    """Repository for Analysis model operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the repository with a database session.
        
        Args:
            db: The database session to use for operations
        """
        self.db = db
    
    async def create(
        self,
        proposal_id: str,
        result: str,
        confidence: float,
        details: str,
        arguments: Optional[Dict[str, List[str]]] = None
    ) -> Analysis:
        """
        Create and save an analysis record in the database.
        
        Args:
            proposal_id: The ID of the proposal being analyzed
            result: The analysis result (e.g., "pass", "fail")
            confidence: The confidence score (0-1)
            details: Detailed explanation of the analysis
            arguments: Optional arguments for and against the proposal
            
        Returns:
            The created Analysis object
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
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        
        return analysis
    
    async def get_by_id(self, id: uuid.UUID) -> Optional[Analysis]:
        """
        Get an analysis by ID from the database.
        
        Args:
            id: The ID of the analysis to retrieve
            
        Returns:
            The Analysis object if found, None otherwise
        """
        return await self.db.get(Analysis, id)
    
    async def find_by_proposal_id(self, proposal_id: str) -> Optional[Analysis]:
        """
        Find an analysis by proposal ID in the database.
        
        Args:
            proposal_id: The ID of the proposal to find analyses for
            
        Returns:
            The most recent Analysis object if found, None otherwise
        """
        query = select(Analysis).where(Analysis.proposal_id == proposal_id).order_by(Analysis.created_at.desc())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def find_all_by_proposal_id(self, proposal_id: str) -> List[Analysis]:
        """
        Find all analyses for a proposal in the database.
        
        Args:
            proposal_id: The ID of the proposal to find analyses for
            
        Returns:
            A list of Analysis objects
        """
        query = select(Analysis).where(Analysis.proposal_id == proposal_id).order_by(Analysis.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
        
    async def find_all(self, 
                       limit: int = 100, 
                       offset: int = 0, 
                       result_filter: Optional[str] = None,
                       min_confidence: Optional[float] = None,
                       max_confidence: Optional[float] = None,
                       proposal_id: Optional[str] = None) -> List[Analysis]:
        """
        Find all analyses with pagination and filtering.
        
        Args:
            limit: Maximum number of analyses to return
            offset: Number of analyses to skip
            result_filter: Optional filter for the result field
            min_confidence: Optional minimum confidence score
            max_confidence: Optional maximum confidence score
            proposal_id: Optional proposal ID filter
            
        Returns:
            A list of Analysis objects
        """
        # Start with a base query
        query = select(Analysis)
        
        # Apply filters if provided
        if result_filter:
            query = query.where(Analysis.result == result_filter)
            
        if min_confidence is not None:
            query = query.where(Analysis.confidence >= min_confidence)
            
        if max_confidence is not None:
            query = query.where(Analysis.confidence <= max_confidence)
            
        if proposal_id:
            query = query.where(Analysis.proposal_id == proposal_id)
        
        # Apply pagination and ordering
        query = query.order_by(Analysis.created_at.desc()).limit(limit).offset(offset)
        
        # Execute query
        result = await self.db.execute(query)
        return list(result.scalars().all())
        
    async def count(self,
                    result_filter: Optional[str] = None,
                    min_confidence: Optional[float] = None,
                    max_confidence: Optional[float] = None,
                    proposal_id: Optional[str] = None) -> int:
        """
        Count analyses with filtering.
        
        Args:
            result_filter: Optional filter for the result field
            min_confidence: Optional minimum confidence score
            max_confidence: Optional maximum confidence score
            proposal_id: Optional proposal ID filter
            
        Returns:
            The count of matching analyses
        """
        from sqlalchemy import func
        
        # Start with a base query
        query = select(func.count()).select_from(Analysis)
        
        # Apply filters if provided
        if result_filter:
            query = query.where(Analysis.result == result_filter)
            
        if min_confidence is not None:
            query = query.where(Analysis.confidence >= min_confidence)
            
        if max_confidence is not None:
            query = query.where(Analysis.confidence <= max_confidence)
            
        if proposal_id:
            query = query.where(Analysis.proposal_id == proposal_id)
        
        # Execute query
        result = await self.db.execute(query)
        return result.scalar_one()
