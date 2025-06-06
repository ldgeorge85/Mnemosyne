"""
Base repository for database operations.

This module provides a base class for repositories to handle common
CRUD operations on database models.
"""
from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

# Type variable for the ORM model
ModelType = TypeVar("ModelType")

class BaseRepository:
    """
    Base repository for handling common database operations.
    
    This class provides common CRUD operations and serves as a base
    for more specific repository implementations.
    """
    
    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        """
        Initialize the base repository.
        
        Args:
            session: The database session to use for operations
            model_class: The SQLAlchemy model class this repository handles
        """
        self.session = session
        self.model = model_class
    
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """
        Retrieve an entity by its ID.
        
        Args:
            id: The unique identifier of the entity
            
        Returns:
            The entity instance if found, None otherwise
        """
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_all(self) -> List[ModelType]:
        """
        Retrieve all entities of the model type.
        
        Returns:
            List of all entities
        """
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create a new entity.
        
        Args:
            obj_in: Dictionary containing entity fields
            
        Returns:
            The newly created entity instance
        """
        obj = self.model(**obj_in)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def update(self, id: str, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """
        Update an existing entity.
        
        Args:
            id: The unique identifier of the entity to update
            obj_in: Dictionary containing fields to update
            
        Returns:
            The updated entity instance if found, None otherwise
        """
        stmt = update(self.model).where(self.model.id == id).values(**obj_in).returning(self.model)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalars().first()
    
    async def delete(self, id: str) -> bool:
        """
        Delete an entity by its ID.
        
        Args:
            id: The unique identifier of the entity to delete
            
        Returns:
            True if the entity was deleted, False otherwise
        """
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
