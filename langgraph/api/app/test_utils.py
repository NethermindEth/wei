"""
Test utilities for the application.

This module provides utilities for testing the application, including:
- Mock database session
- Mock repository
- Mock service
- Test client factory
"""

# Standard library imports
import asyncio
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, AsyncGenerator
import uuid

# Third-party imports
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import AsyncMock, MagicMock, patch

# Local application imports
from app.db.core import Base
from app.repositories.base import BaseRepository, ModelType
from app.services.base_service import BaseService
from app.config import settings

# Define type variables
T = TypeVar('T')
RepoType = TypeVar('RepoType')
ServiceType = TypeVar('ServiceType')
ModelType = TypeVar('ModelType')
ResponseSchemaType = TypeVar('ResponseSchemaType', bound=BaseModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class MockDBSession:
    """Mock database session for testing."""
    
    async def __aenter__(self):
        """Enter async context."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        pass
    
    async def commit(self):
        """Mock commit."""
        pass
    
    async def rollback(self):
        """Mock rollback."""
        pass
    
    async def close(self):
        """Mock close."""
        pass
    
    async def execute(self, *args, **kwargs):
        """Mock execute."""
        result = MagicMock()
        result.scalar_one = AsyncMock(return_value=0)
        result.scalar_one_or_none = AsyncMock(return_value=None)
        result.scalars = MagicMock(return_value=result)
        result.all = MagicMock(return_value=[])
        return result
    
    async def get(self, model, id):
        """Mock get."""
        return None
    
    def add(self, obj):
        """Mock add."""
        pass
    
    async def refresh(self, obj):
        """Mock refresh."""
        pass


class MockRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Mock repository for testing.
    
    This class provides a mock implementation of the BaseRepository interface.
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession = None):
        """
        Initialize the mock repository.
        
        Args:
            model: The model class
            db: The database session
        """
        self.model = model
        self.db = db or MockDBSession()
        self.items: Dict[Any, ModelType] = {}
    
    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Mock create operation.
        
        Args:
            obj_in: The data to create the record with
            
        Returns:
            A mock model instance
        """
        # Create a mock model instance
        item_id = uuid.uuid4()
        item = MagicMock()
        item.id = item_id
        
        # Add attributes from obj_in
        if isinstance(obj_in, dict):
            for key, value in obj_in.items():
                setattr(item, key, value)
        else:
            for key, value in obj_in.dict().items():
                setattr(item, key, value)
        
        # Add timestamps
        item.created_at = datetime.now()
        item.updated_at = datetime.now()
        
        # Store the item
        self.items[item_id] = item
        
        return item
    
    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Mock get_by_id operation.
        
        Args:
            id: The ID of the record to get
            
        Returns:
            The record if found, None otherwise
        """
        return self.items.get(id)
    
    async def get_by_id_or_404(self, id: Any) -> ModelType:
        """
        Mock get_by_id_or_404 operation.
        
        Args:
            id: The ID of the record to get
            
        Returns:
            The record if found
            
        Raises:
            HTTPException: If the record is not found
        """
        item = await self.get_by_id(id)
        if item is None:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with ID {id} not found"
            )
        return item
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Mock get_all operation.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column to order by
            filters: Dictionary of filters to apply
            
        Returns:
            List of records
        """
        items = list(self.items.values())
        
        # Apply filters if provided
        if filters:
            filtered_items = []
            for item in items:
                match = True
                for field, value in filters.items():
                    if hasattr(item, field) and getattr(item, field) != value:
                        match = False
                        break
                if match:
                    filtered_items.append(item)
            items = filtered_items
        
        # Apply pagination
        return items[skip:skip + limit]
    
    async def update(
        self, 
        id: Any, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Mock update operation.
        
        Args:
            id: The ID of the record to update
            obj_in: The data to update the record with
            
        Returns:
            The updated record
            
        Raises:
            HTTPException: If the record is not found
        """
        item = await self.get_by_id_or_404(id)
        
        # Update attributes from obj_in
        if isinstance(obj_in, dict):
            for key, value in obj_in.items():
                setattr(item, key, value)
        else:
            for key, value in obj_in.dict(exclude_unset=True).items():
                setattr(item, key, value)
        
        # Update timestamp
        item.updated_at = datetime.now()
        
        # Store the updated item
        self.items[id] = item
        
        return item
    
    async def delete(self, id: Any) -> bool:
        """
        Mock delete operation.
        
        Args:
            id: The ID of the record to delete
            
        Returns:
            True if the record was deleted, False otherwise
            
        Raises:
            HTTPException: If the record is not found
        """
        await self.get_by_id_or_404(id)
        
        # Remove the item
        if id in self.items:
            del self.items[id]
            return True
        return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Mock count operation.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            Number of records
        """
        items = await self.get_all(filters=filters)
        return len(items)
    
    async def exists(self, id: Any) -> bool:
        """
        Mock exists operation.
        
        Args:
            id: The ID of the record to check
            
        Returns:
            True if the record exists, False otherwise
        """
        return id in self.items


class MockService(Generic[RepoType, ModelType, ResponseSchemaType, CreateSchemaType, UpdateSchemaType]):
    """
    Mock service for testing.
    
    This class provides a mock implementation of the BaseService interface.
    """
    
    def __init__(self, repository: RepoType):
        """
        Initialize the mock service.
        
        Args:
            repository: The repository to use
        """
        self.repository = repository
    
    async def create(self, obj_in: CreateSchemaType) -> ResponseSchemaType:
        """
        Mock create operation.
        
        Args:
            obj_in: The data to create the record with
            
        Returns:
            The created record as a response schema
        """
        db_obj = await self.repository.create(obj_in)
        return self.to_response(db_obj)
    
    async def get_by_id(self, id: Any) -> ResponseSchemaType:
        """
        Mock get_by_id operation.
        
        Args:
            id: The ID of the record to get
            
        Returns:
            The record as a response schema
            
        Raises:
            HTTPException: If the record is not found
        """
        db_obj = await self.repository.get_by_id_or_404(id)
        return self.to_response(db_obj)
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        **filters
    ) -> List[ResponseSchemaType]:
        """
        Mock get_all operation.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Additional filters to apply
            
        Returns:
            List of records as response schemas
        """
        db_objs = await self.repository.get_all(skip=skip, limit=limit, filters=filters)
        return [self.to_response(db_obj) for db_obj in db_objs]
    
    async def update(self, id: Any, obj_in: UpdateSchemaType) -> ResponseSchemaType:
        """
        Mock update operation.
        
        Args:
            id: The ID of the record to update
            obj_in: The data to update the record with
            
        Returns:
            The updated record as a response schema
            
        Raises:
            HTTPException: If the record is not found
        """
        db_obj = await self.repository.update(id, obj_in)
        return self.to_response(db_obj)
    
    async def delete(self, id: Any) -> bool:
        """
        Mock delete operation.
        
        Args:
            id: The ID of the record to delete
            
        Returns:
            True if the record was deleted
            
        Raises:
            HTTPException: If the record is not found
        """
        return await self.repository.delete(id)
    
    async def count(self, **filters) -> int:
        """
        Mock count operation.
        
        Args:
            **filters: Filters to apply
            
        Returns:
            Number of records
        """
        return await self.repository.count(filters=filters)
    
    def to_response(self, db_obj: ModelType) -> ResponseSchemaType:
        """
        Convert a database object to a response schema.
        
        Args:
            db_obj: The database object to convert
            
        Returns:
            The response schema
        """
        # This is a mock implementation that should be overridden by subclasses
        response = MagicMock()
        
        # Copy attributes from db_obj
        for key in dir(db_obj):
            if not key.startswith('_') and not callable(getattr(db_obj, key)):
                setattr(response, key, getattr(db_obj, key))
        
        return response


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a test database session.
    
    Yields:
        A test database session
    """
    # Create an in-memory SQLite database for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    TestingSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Yield session
    async with TestingSessionLocal() as session:
        yield session
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def create_test_client(app: FastAPI) -> TestClient:
    """
    Create a test client for the FastAPI application.
    
    Args:
        app: The FastAPI application
        
    Returns:
        A test client
    """
    # Override dependencies
    async def override_get_db():
        async for session in get_test_db():
            yield session
    
    # Apply overrides
    app.dependency_overrides = {
        AsyncSession: override_get_db
    }
    
    # Create test client
    return TestClient(app)


async def create_async_test_client(app: FastAPI) -> AsyncClient:
    """
    Create an async test client for the FastAPI application.
    
    Args:
        app: The FastAPI application
        
    Returns:
        An async test client
    """
    # Override dependencies
    async def override_get_db():
        async for session in get_test_db():
            yield session
    
    # Apply overrides
    app.dependency_overrides = {
        AsyncSession: override_get_db
    }
    
    # Create async test client
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


def mock_dependency(app: FastAPI, dependency: Any, mock_value: Any) -> None:
    """
    Mock a dependency in the FastAPI application.
    
    Args:
        app: The FastAPI application
        dependency: The dependency to mock
        mock_value: The mock value to use
    """
    if app.dependency_overrides is None:
        app.dependency_overrides = {}
    
    app.dependency_overrides[dependency] = lambda: mock_value
