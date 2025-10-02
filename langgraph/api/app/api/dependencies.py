"""
Dependencies for the API routes.
"""

# Standard library imports
from typing import AsyncGenerator

# Third-party imports
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from app.db import get_session
from app.repositories.analysis_repository import AnalysisRepository
from app.services.analysis_service import AnalysisService


async def get_analysis_repository(
    db: AsyncSession = Depends(get_session)
) -> AsyncGenerator[AnalysisRepository, None]:
    """
    Get an AnalysisRepository instance.
    
    Args:
        db: The database session
        
    Yields:
        An AnalysisRepository instance
    """
    repo = AnalysisRepository(db)
    yield repo


async def get_analysis_service(
    repository: AnalysisRepository = Depends(get_analysis_repository)
) -> AsyncGenerator[AnalysisService, None]:
    """
    Get an AnalysisService instance.
    
    Args:
        repository: The AnalysisRepository to use
        
    Yields:
        An AnalysisService instance
    """
    service = AnalysisService(repository)
    yield service
