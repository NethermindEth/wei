"""
Base service module for business logic.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
import logging

from pydantic import BaseModel

from app.errors import ServiceError, NotFoundError

# Configure logging
logger = logging.getLogger(__name__)

# Define a generic type variable for repositories
RepoType = TypeVar("RepoType")
# Define a generic type variable for models
ModelType = TypeVar("ModelType")
# Define a generic type variable for response schemas
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)
# Define a generic type variable for create schemas
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# Define a generic type variable for update schemas
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[RepoType, ModelType, ResponseSchemaType, CreateSchemaType, UpdateSchemaType]):
    """
    Base service class with default methods for business logic.
    
    Attributes:
        repository: The repository instance
    """
    
    def __init__(self, repository: RepoType):
        """
        Initialize the service with a repository.
        
        Args:
            repository: The repository to use for data access
        """
        self.repository = repository
    
    async def create(self, obj_in: CreateSchemaType) -> ResponseSchemaType:
        """
        Create a new record.
        
        Args:
            obj_in: The data to create the record with
            
        Returns:
            The created record as a response schema
        """
        try:
            # Create the record using the repository
            db_obj = await self.repository.create(obj_in)
            
            # Convert to response schema and return
            return self.to_response(db_obj)
        except Exception as e:
            logger.error(f"Error creating record: {str(e)}")
            raise ServiceError(f"Error creating record: {str(e)}")
    
    async def get_by_id(self, id: Any) -> ResponseSchemaType:
        """
        Get a record by ID.
        
        Args:
            id: The ID of the record to get
            
        Returns:
            The record as a response schema
            
        Raises:
            NotFoundError: If the record is not found
        """
        try:
            # Get the record using the repository
            db_obj = await self.repository.get_by_id(id)
            
            # Raise error if not found
            if db_obj is None:
                raise NotFoundError(f"Record with ID {id} not found")
            
            # Convert to response schema and return
            return self.to_response(db_obj)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting record by ID: {str(e)}")
            raise ServiceError(f"Error getting record by ID: {str(e)}")
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        **filters
    ) -> List[ResponseSchemaType]:
        """
        Get all records with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Additional filters to apply
            
        Returns:
            List of records as response schemas
        """
        try:
            # Get all records using the repository
            db_objs = await self.repository.get_all(skip=skip, limit=limit, filters=filters)
            
            # Convert to response schemas and return
            return [self.to_response(db_obj) for db_obj in db_objs]
        except Exception as e:
            logger.error(f"Error getting all records: {str(e)}")
            raise ServiceError(f"Error getting all records: {str(e)}")
    
    async def update(self, id: Any, obj_in: UpdateSchemaType) -> ResponseSchemaType:
        """
        Update a record.
        
        Args:
            id: The ID of the record to update
            obj_in: The data to update the record with
            
        Returns:
            The updated record as a response schema
            
        Raises:
            NotFoundError: If the record is not found
        """
        try:
            # Update the record using the repository
            db_obj = await self.repository.update(id, obj_in)
            
            # Convert to response schema and return
            return self.to_response(db_obj)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating record: {str(e)}")
            raise ServiceError(f"Error updating record: {str(e)}")
    
    async def delete(self, id: Any) -> bool:
        """
        Delete a record.
        
        Args:
            id: The ID of the record to delete
            
        Returns:
            True if the record was deleted
            
        Raises:
            NotFoundError: If the record is not found
        """
        try:
            # Delete the record using the repository
            return await self.repository.delete(id)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting record: {str(e)}")
            raise ServiceError(f"Error deleting record: {str(e)}")
    
    async def count(self, **filters) -> int:
        """
        Count records with filtering.
        
        Args:
            **filters: Filters to apply
            
        Returns:
            Number of records
        """
        try:
            # Count records using the repository
            return await self.repository.count(filters=filters)
        except Exception as e:
            logger.error(f"Error counting records: {str(e)}")
            raise ServiceError(f"Error counting records: {str(e)}")
    
    def to_response(self, db_obj: ModelType) -> ResponseSchemaType:
        """
        Convert a database object to a response schema.
        
        Args:
            db_obj: The database object to convert
            
        Returns:
            The response schema
            
        Raises:
            NotImplementedError: If the method is not implemented by a subclass
        """
        raise NotImplementedError("Subclasses must implement to_response method")
