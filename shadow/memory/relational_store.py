"""
Relational Store Implementation for the Shadow platform.

This module provides relational storage functionality for the Shadow AI system,
supporting structured data and relationships between entities.
"""

import logging
import uuid
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

from memory.memory_base import MemoryItem, MemorySystem

# Configure logging
logger = logging.getLogger("shadow.memory.relational")


class RelationalItem(MemoryItem):
    """
    Extended memory item for relational data storage.
    
    Provides structured data representation and relationship tracking.
    """
    
    def __init__(
        self,
        content: str,
        entity_type: str,
        properties: Dict[str, Any] = None,
        relationships: Dict[str, List[str]] = None,
        metadata: Dict[str, Any] = None,
        item_id: Optional[str] = None
    ):
        """
        Initialize a relational item.
        
        Args:
            content: The item content/description
            entity_type: Type of entity (e.g., 'person', 'concept', 'event')
            properties: Entity properties as key-value pairs
            relationships: Entity relationships as {relation_type: [related_entity_ids]}
            metadata: Optional metadata for the item
            item_id: Optional ID for the item
        """
        metadata = metadata or {}
        metadata["entity_type"] = entity_type
        
        # Store relationships and properties separately
        self.properties = properties or {}
        self.relationships = relationships or {}
        
        super().__init__(content, metadata, item_id)
    
    @property
    def entity_type(self) -> str:
        """Get the entity type."""
        return self.metadata.get("entity_type", "generic")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the relational item to a dictionary.
        
        Returns:
            Dict representation of the relational item
        """
        result = super().to_dict()
        result["properties"] = self.properties
        result["relationships"] = self.relationships
        return result
    
    def add_relationship(self, relation_type: str, target_id: str) -> None:
        """
        Add a relationship to another entity.
        
        Args:
            relation_type: Type of the relationship
            target_id: ID of the target entity
        """
        if relation_type not in self.relationships:
            self.relationships[relation_type] = []
        
        if target_id not in self.relationships[relation_type]:
            self.relationships[relation_type].append(target_id)
    
    def remove_relationship(self, relation_type: str, target_id: str) -> bool:
        """
        Remove a relationship to another entity.
        
        Args:
            relation_type: Type of the relationship
            target_id: ID of the target entity
            
        Returns:
            True if the relationship was removed, False otherwise
        """
        if relation_type in self.relationships and target_id in self.relationships[relation_type]:
            self.relationships[relation_type].remove(target_id)
            return True
        return False


class InMemoryRelationalStore(MemorySystem):
    """
    In-memory implementation of a relational data store.
    
    This provides a simple relational storage system using in-memory dictionaries,
    suitable for development and testing.
    """
    
    def __init__(self):
        """Initialize the in-memory relational store."""
        super().__init__("InMemoryRelational")
        self.entities: Dict[str, RelationalItem] = {}
    
    def store(self, item: Union[RelationalItem, MemoryItem]) -> str:
        """
        Store a relational item.
        
        Args:
            item: The relational item to store
            
        Returns:
            ID of the stored item
        """
        # Convert to RelationalItem if necessary
        if not isinstance(item, RelationalItem):
            entity_type = item.metadata.get("entity_type", "generic")
            item = RelationalItem(
                item.content, entity_type, 
                properties={}, relationships={}, 
                metadata=item.metadata, item_id=item.item_id
            )
        
        # Generate an ID if one isn't provided
        if item.item_id is None:
            item.item_id = str(uuid.uuid4())
        
        # Store the entity
        self.entities[item.item_id] = item
        logger.info(f"Stored relational entity with ID {item.item_id} and type '{item.entity_type}'")
        return item.item_id
    
    def retrieve(self, item_id: str) -> Optional[RelationalItem]:
        """
        Retrieve a relational item by ID.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            The retrieved item or None if not found
        """
        return self.entities.get(item_id)
    
    def get_all(self) -> List[RelationalItem]:
        """
        Get all stored relational entities.
        
        Returns:
            List of all relational items
        """
        return list(self.entities.values())
    
    def delete(self, item_id: str) -> bool:
        """
        Delete a relational item.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            True if the item was deleted, False otherwise
        """
        if item_id in self.entities:
            # First, remove all relationships to this entity
            for entity in self.entities.values():
                for relation_type in list(entity.relationships.keys()):
                    if item_id in entity.relationships[relation_type]:
                        entity.relationships[relation_type].remove(item_id)
            
            # Then delete the entity
            del self.entities[item_id]
            logger.info(f"Deleted relational entity with ID {item_id}")
            return True
        
        logger.warning(f"Attempted to delete non-existent relational entity with ID {item_id}")
        return False
    
    def clear(self) -> bool:
        """
        Clear all relational items.
        
        Returns:
            True if the items were cleared, False otherwise
        """
        self.entities.clear()
        logger.info("Cleared all relational entities")
        return True
    
    def query_by_type(self, entity_type: str) -> List[RelationalItem]:
        """
        Query entities by type.
        
        Args:
            entity_type: Type of entities to retrieve
            
        Returns:
            List of entities of the specified type
        """
        return [entity for entity in self.entities.values() if entity.entity_type == entity_type]
    
    def query_by_property(self, property_name: str, property_value: Any) -> List[RelationalItem]:
        """
        Query entities by property.
        
        Args:
            property_name: Name of the property to match
            property_value: Value of the property to match
            
        Returns:
            List of entities with the specified property value
        """
        return [
            entity for entity in self.entities.values()
            if property_name in entity.properties and entity.properties[property_name] == property_value
        ]
    
    def query_by_relationship(self, relation_type: str, target_id: Optional[str] = None) -> List[RelationalItem]:
        """
        Query entities by relationship.
        
        Args:
            relation_type: Type of relationship to match
            target_id: Optional target entity ID to match
            
        Returns:
            List of entities with the specified relationship
        """
        if target_id:
            return [
                entity for entity in self.entities.values()
                if (relation_type in entity.relationships and 
                    target_id in entity.relationships[relation_type])
            ]
        else:
            return [
                entity for entity in self.entities.values()
                if relation_type in entity.relationships and entity.relationships[relation_type]
            ]


class SQLiteRelationalStore(MemorySystem):
    """
    SQLite implementation of a relational data store.
    
    This provides persistent storage of relational data using SQLite,
    suitable for more robust applications.
    """
    
    def __init__(self, db_path: str = "shadow_memory.db"):
        """
        Initialize the SQLite relational store.
        
        Args:
            db_path: Path to SQLite database file
        """
        super().__init__("SQLiteRelational")
        self.db_path = db_path
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the database tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create entities table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create properties table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                entity_id TEXT NOT NULL,
                property_name TEXT NOT NULL,
                property_value TEXT,
                PRIMARY KEY (entity_id, property_name),
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
            ''')
            
            # Create relationships table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                source_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                PRIMARY KEY (source_id, relation_type, target_id),
                FOREIGN KEY (source_id) REFERENCES entities(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES entities(id) ON DELETE CASCADE
            )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Initialized SQLite database for relational store")
        
        except Exception as e:
            logger.error(f"Error initializing SQLite database: {str(e)}")
    
    def store(self, item: Union[RelationalItem, MemoryItem]) -> str:
        """
        Store a relational item in the database.
        
        Args:
            item: The relational item to store
            
        Returns:
            ID of the stored item
        """
        # Convert to RelationalItem if necessary
        if not isinstance(item, RelationalItem):
            entity_type = item.metadata.get("entity_type", "generic")
            item = RelationalItem(
                item.content, entity_type, 
                properties={}, relationships={}, 
                metadata=item.metadata, item_id=item.item_id
            )
        
        # Generate an ID if one isn't provided
        if item.item_id is None:
            item.item_id = str(uuid.uuid4())
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store entity
            cursor.execute(
                "INSERT OR REPLACE INTO entities (id, entity_type, content, metadata) VALUES (?, ?, ?, ?)",
                (
                    item.item_id,
                    item.entity_type,
                    item.content,
                    json.dumps(item.metadata)
                )
            )
            
            # Store properties
            for prop_name, prop_value in item.properties.items():
                cursor.execute(
                    "INSERT OR REPLACE INTO properties (entity_id, property_name, property_value) VALUES (?, ?, ?)",
                    (
                        item.item_id,
                        prop_name,
                        json.dumps(prop_value)
                    )
                )
            
            # Store relationships
            for relation_type, target_ids in item.relationships.items():
                for target_id in target_ids:
                    cursor.execute(
                        "INSERT OR REPLACE INTO relationships (source_id, relation_type, target_id) VALUES (?, ?, ?)",
                        (
                            item.item_id,
                            relation_type,
                            target_id
                        )
                    )
            
            conn.commit()
            conn.close()
            logger.info(f"Stored relational entity with ID {item.item_id} in SQLite database")
            return item.item_id
        
        except Exception as e:
            logger.error(f"Error storing relational entity in SQLite database: {str(e)}")
            return item.item_id
    
    def retrieve(self, item_id: str) -> Optional[RelationalItem]:
        """
        Retrieve a relational item by ID from the database.
        
        Args:
            item_id: ID of the item to retrieve
            
        Returns:
            The retrieved item or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get entity
            cursor.execute(
                "SELECT id, entity_type, content, metadata FROM entities WHERE id = ?",
                (item_id,)
            )
            entity_row = cursor.fetchone()
            
            if not entity_row:
                conn.close()
                return None
            
            # Parse entity data
            entity_id, entity_type, content, metadata_json = entity_row
            metadata = json.loads(metadata_json) if metadata_json else {}
            
            # Get properties
            properties = {}
            cursor.execute(
                "SELECT property_name, property_value FROM properties WHERE entity_id = ?",
                (item_id,)
            )
            for prop_row in cursor.fetchall():
                prop_name, prop_value_json = prop_row
                properties[prop_name] = json.loads(prop_value_json) if prop_value_json else None
            
            # Get relationships
            relationships = {}
            cursor.execute(
                "SELECT relation_type, target_id FROM relationships WHERE source_id = ?",
                (item_id,)
            )
            for rel_row in cursor.fetchall():
                relation_type, target_id = rel_row
                if relation_type not in relationships:
                    relationships[relation_type] = []
                relationships[relation_type].append(target_id)
            
            conn.close()
            
            # Create and return entity
            return RelationalItem(
                content=content,
                entity_type=entity_type,
                properties=properties,
                relationships=relationships,
                metadata=metadata,
                item_id=entity_id
            )
        
        except Exception as e:
            logger.error(f"Error retrieving relational entity from SQLite database: {str(e)}")
            return None
    
    def delete(self, item_id: str) -> bool:
        """
        Delete a relational item from the database.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            True if the item was deleted, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if entity exists
            cursor.execute("SELECT id FROM entities WHERE id = ?", (item_id,))
            if not cursor.fetchone():
                conn.close()
                return False
            
            # Delete entity (cascade will delete properties and relationships)
            cursor.execute("DELETE FROM entities WHERE id = ?", (item_id,))
            
            conn.commit()
            conn.close()
            logger.info(f"Deleted relational entity with ID {item_id} from SQLite database")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting relational entity from SQLite database: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all relational items from the database.
        
        Returns:
            True if the items were cleared, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear all tables
            cursor.execute("DELETE FROM relationships")
            cursor.execute("DELETE FROM properties")
            cursor.execute("DELETE FROM entities")
            
            conn.commit()
            conn.close()
            logger.info("Cleared all relational entities from SQLite database")
            return True
        
        except Exception as e:
            logger.error(f"Error clearing relational entities from SQLite database: {str(e)}")
            return False
    
    def query_by_type(self, entity_type: str) -> List[RelationalItem]:
        """
        Query entities by type from the database.
        
        Args:
            entity_type: Type of entities to retrieve
            
        Returns:
            List of entities of the specified type
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get entities by type
            cursor.execute(
                "SELECT id FROM entities WHERE entity_type = ?",
                (entity_type,)
            )
            entity_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Retrieve each entity
            return [self.retrieve(entity_id) for entity_id in entity_ids if entity_id]
        
        except Exception as e:
            logger.error(f"Error querying entities by type from SQLite database: {str(e)}")
            return []
    
    def query_by_property(self, property_name: str, property_value: Any) -> List[RelationalItem]:
        """
        Query entities by property from the database.
        
        Args:
            property_name: Name of the property to match
            property_value: Value of the property to match
            
        Returns:
            List of entities with the specified property value
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get entities by property
            cursor.execute(
                "SELECT entity_id FROM properties WHERE property_name = ? AND property_value = ?",
                (property_name, json.dumps(property_value))
            )
            entity_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Retrieve each entity
            return [self.retrieve(entity_id) for entity_id in entity_ids if entity_id]
        
        except Exception as e:
            logger.error(f"Error querying entities by property from SQLite database: {str(e)}")
            return []
    
    def query_by_relationship(self, relation_type: str, target_id: Optional[str] = None) -> List[RelationalItem]:
        """
        Query entities by relationship from the database.
        
        Args:
            relation_type: Type of relationship to match
            target_id: Optional target entity ID to match
            
        Returns:
            List of entities with the specified relationship
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get entities by relationship
            if target_id:
                cursor.execute(
                    "SELECT source_id FROM relationships WHERE relation_type = ? AND target_id = ?",
                    (relation_type, target_id)
                )
            else:
                cursor.execute(
                    "SELECT source_id FROM relationships WHERE relation_type = ?",
                    (relation_type,)
                )
            
            entity_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # Retrieve each entity
            return [self.retrieve(entity_id) for entity_id in entity_ids if entity_id]
        
        except Exception as e:
            logger.error(f"Error querying entities by relationship from SQLite database: {str(e)}")
            return []
