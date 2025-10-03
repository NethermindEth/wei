"""
Base repository module for database operations.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import uuid
from datetime import datetime

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from app.db.core import Base
from app.errors import NotFoundError, DatabaseError

# Define a generic type variable for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)
# Define a generic type variable for Pydantic schemas
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository class with default methods for CRUD operations.
    
    Attributes:
        model: The SQLAlchemy model class
        db: The database session
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize the repository with a model and database session.
        
        Args:
            model: The SQLAlchemy model class
            db: The database session
        """
        self.model = model
        self.db = db
    
    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Create a new record.
        
        Args:
            obj_in: The data to create the record with
            
        Returns:
            The created record
        """
        try:
            # Convert Pydantic model to dict if needed
            obj_data = obj_in.dict() if isinstance(obj_in, BaseModel) else obj_in
            
            # Create model instance
            db_obj = self.model(**obj_data)
            
            # Add to session and commit
            self.db.add(db_obj)
            await self.db.commit()
            await self.db.refresh(db_obj)
            
            return db_obj
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error creating {self.model.__name__}: {str(e)}")
    
    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Get a record by ID.
        
        Args:
            id: The ID of the record to get
            
        Returns:
            The record if found, None otherwise
        """
        try:
            query = select(self.model).where(self.model.id == id)
            result = await self.db.execute(query)
            return result.scalars().first()
        except Exception as e:
            raise DatabaseError(f"Error getting {self.model.__name__} by ID: {str(e)}")
    
    async def get_by_id_or_404(self, id: Any) -> ModelType:
        """
        Get a record by ID or raise a 404 error.
        
        Args:
            id: The ID of the record to get
            
        Returns:
            The record if found
            
        Raises:
            NotFoundError: If the record is not found
        """
        obj = await self.get_by_id(id)
        if obj is None:
            raise NotFoundError(f"{self.model.__name__} with ID {id} not found")
        return obj
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Get all records with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column to order by
            filters: Dictionary of filters to apply
            
        Returns:
            List of records
        """
        try:
            # Start with a base query
            query = select(self.model)
            
            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.where(getattr(self.model, field) == value)
            
            # Apply ordering if provided
            if order_by and hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            # Execute query
            result = await self.db.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseError(f"Error getting all {self.model.__name__}: {str(e)}")
    
    async def update(
        self, 
        id: Any, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update a record.
        
        Args:
            id: The ID of the record to update
            obj_in: The data to update the record with
            
        Returns:
            The updated record
            
        Raises:
            NotFoundError: If the record is not found
        """
        try:
            # Get the existing record
            db_obj = await self.get_by_id_or_404(id)
            
            # Convert Pydantic model to dict if needed
            update_data = obj_in.dict(exclude_unset=True) if isinstance(obj_in, BaseModel) else obj_in
            
            # Update the record
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            # Add updated_at timestamp if the model has it
            if hasattr(db_obj, "updated_at"):
                setattr(db_obj, "updated_at", datetime.now())
            
            # Commit changes
            await self.db.commit()
            await self.db.refresh(db_obj)
            
            return db_obj
        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error updating {self.model.__name__}: {str(e)}")
    
    async def delete(self, id: Any) -> bool:
        """
        Delete a record.
        
        Args:
            id: The ID of the record to delete
            
        Returns:
            True if the record was deleted, False otherwise
            
        Raises:
            NotFoundError: If the record is not found
        """
        try:
            # Get the existing record
            db_obj = await self.get_by_id_or_404(id)
            
            # Delete the record
            await self.db.delete(db_obj)
            await self.db.commit()
            
            return True
        except NotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            raise DatabaseError(f"Error deleting {self.model.__name__}: {str(e)}")
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filtering.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            Number of records
        """
        try:
            # Start with a base query
            query = select(func.count()).select_from(self.model)
            
            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        query = query.where(getattr(self.model, field) == value)
            
            # Execute query
            result = await self.db.execute(query)
            return result.scalar_one()
        except Exception as e:
            raise DatabaseError(f"Error counting {self.model.__name__}: {str(e)}")
    
    async def exists(self, id: Any) -> bool:
        """
        Check if a record exists.
        
        Args:
            id: The ID of the record to check
            
        Returns:
            True if the record exists, False otherwise
        """
        try:
            query = select(func.count()).select_from(self.model).where(self.model.id == id)
            result = await self.db.execute(query)
            return result.scalar_one() > 0
        except Exception as e:
            raise DatabaseError(f"Error checking if {self.model.__name__} exists: {str(e)}")
