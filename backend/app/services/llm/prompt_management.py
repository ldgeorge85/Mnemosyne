"""
Prompt Engineering System

This module provides a flexible prompt management system for
creating, storing, retrieving, and versioning prompt templates.
"""
import os
import re
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from pydantic import BaseModel, Field, validator

from app.core.config import settings


# Set up module logger
logger = logging.getLogger(__name__)


class PromptTemplate(BaseModel):
    """
    A template for generating prompts with variable interpolation.
    
    Supports Jinja-style variable interpolation with {{variable_name}} syntax
    and optional default values with {{variable_name|default_value}}.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Name of the prompt template")
    description: str = Field(..., description="Description of the prompt's purpose")
    template: str = Field(..., description="The prompt template text with variables")
    version: str = Field(default="1.0.0", description="Semantic version of the template")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    @validator('version')
    def validate_version(cls, v):
        """Validate that version follows semantic versioning format."""
        pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(pattern, v):
            raise ValueError("Version must follow semantic versioning (e.g., 1.0.0)")
        return v
    
    def extract_variables(self) -> List[str]:
        """
        Extract variable names from the template.
        
        Returns:
            List of variable names
        """
        pattern = r'\{\{([^{}|]+)(?:\|[^{}]+)?\}\}'
        matches = re.findall(pattern, self.template)
        return [match.strip() for match in matches]
    
    def fill(self, variables: Dict[str, Any]) -> str:
        """
        Fill the template with provided variables.
        
        Args:
            variables: Dictionary mapping variable names to values
            
        Returns:
            Filled prompt with variables replaced by their values
            
        Raises:
            KeyError: If a required variable is missing
        """
        template = self.template
        
        # Find all variables in the template
        pattern = r'\{\{([^{}|]+)(?:\|([^{}]+))?\}\}'
        matches = re.finditer(pattern, template)
        
        # Keep track of missing variables
        missing = []
        
        # Replace variables with provided values or defaults
        for match in matches:
            var_name = match.group(1).strip()
            default_value = match.group(2).strip() if match.group(2) else None
            
            if var_name in variables:
                value = str(variables[var_name])
            elif default_value is not None:
                value = default_value
            else:
                # Add to missing variables
                missing.append(var_name)
                continue
                
            # Replace the variable with its value
            placeholder = match.group(0)
            template = template.replace(placeholder, value)
        
        # If any variables are missing, raise an error
        if missing:
            raise KeyError(f"Missing required variables: {', '.join(missing)}")
            
        return template
    
    def new_version(self, template: str, version: Optional[str] = None) -> "PromptTemplate":
        """
        Create a new version of this template.
        
        Args:
            template: New template text
            version: Semantic version (if None, increment patch number)
            
        Returns:
            New PromptTemplate instance
        """
        if version is None:
            # Increment patch version
            major, minor, patch = map(int, self.version.split('.'))
            version = f"{major}.{minor}.{patch + 1}"
            
        return PromptTemplate(
            id=str(uuid.uuid4()),
            name=self.name,
            description=self.description,
            template=template,
            version=version,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=self.tags.copy(),
            metadata=self.metadata.copy()
        )


class PromptLibrary:
    """
    Library for managing and storing prompt templates.
    
    This class provides methods for creating, retrieving, updating,
    and versioning prompt templates.
    """
    
    DEFAULT_STORAGE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '../../data/prompts'
    )
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the prompt library.
        
        Args:
            storage_path: Path to the directory where prompts are stored
        """
        self.storage_path = storage_path or self.DEFAULT_STORAGE_PATH
        self._ensure_storage_directory()
        self._templates: Dict[str, Dict[str, PromptTemplate]] = {}
        self._load_templates()
    
    def _ensure_storage_directory(self) -> None:
        """Ensure the storage directory exists."""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _get_template_path(self, template_name: str) -> str:
        """Get the path to the template file."""
        valid_name = re.sub(r'[^\w\-\.]', '_', template_name)
        return os.path.join(self.storage_path, f"{valid_name}.json")
    
    def _load_templates(self) -> None:
        """Load all templates from the storage directory."""
        self._templates = {}
        if not os.path.exists(self.storage_path):
            return
            
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.storage_path, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        
                    # Data is stored as a dict mapping version to template data
                    template_name = filename.replace('.json', '')
                    self._templates[template_name] = {}
                    
                    for version, template_data in data.items():
                        template = PromptTemplate(**template_data)
                        self._templates[template_name][version] = template
                        
                except Exception as e:
                    logger.error(f"Error loading template {filename}: {e}")
    
    def _save_template(self, template: PromptTemplate) -> None:
        """
        Save a template to the storage.
        
        Args:
            template: Template to save
        """
        # Create a valid filename
        template_name = re.sub(r'[^\w\-\.]', '_', template.name)
        filepath = os.path.join(self.storage_path, f"{template_name}.json")
        
        # Load existing data or create new data
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
            except Exception:
                data = {}
        else:
            data = {}
        
        # Add this template version
        data[template.version] = template.dict()
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        # Add to in-memory cache
        if template.name not in self._templates:
            self._templates[template.name] = {}
        self._templates[template.name][template.version] = template
    
    def create_template(
        self,
        name: str,
        description: str,
        template: str,
        version: str = "1.0.0",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PromptTemplate:
        """
        Create a new prompt template.
        
        Args:
            name: Name of the template
            description: Description of the template
            template: Template text with variables
            version: Semantic version
            tags: Tags for categorization
            metadata: Additional metadata
            
        Returns:
            Created PromptTemplate
        """
        # Create the template
        prompt = PromptTemplate(
            name=name,
            description=description,
            template=template,
            version=version,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Save the template
        self._save_template(prompt)
        
        return prompt
    
    def get_template(
        self,
        name: str,
        version: Optional[str] = None,
        latest: bool = True
    ) -> Optional[PromptTemplate]:
        """
        Get a prompt template by name and version.
        
        Args:
            name: Name of the template
            version: Specific version to retrieve
            latest: If True and version is None, get the latest version
            
        Returns:
            PromptTemplate if found, None otherwise
        """
        if name not in self._templates:
            return None
            
        if version:
            # Get specific version
            return self._templates[name].get(version)
        elif latest:
            # Get latest version
            versions = list(self._templates[name].keys())
            if not versions:
                return None
                
            # Sort versions semantically
            versions.sort(key=lambda v: [int(x) for x in v.split('.')])
            return self._templates[name][versions[-1]]
        else:
            # Return all versions
            return list(self._templates[name].values())
    
    def list_templates(self, tag: Optional[str] = None) -> List[PromptTemplate]:
        """
        List all available templates, optionally filtered by tag.
        
        Args:
            tag: Filter templates by tag
            
        Returns:
            List of templates (latest version of each)
        """
        result = []
        
        for name in self._templates:
            template = self.get_template(name, latest=True)
            if template and (tag is None or tag in template.tags):
                result.append(template)
                
        return result
    
    def update_template(
        self,
        name: str,
        template: str,
        version: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[PromptTemplate]:
        """
        Update an existing template or create a new version.
        
        Args:
            name: Name of the template
            template: New template text
            version: New version (if None, increment patch number)
            description: New description (if None, keep existing)
            tags: New tags (if None, keep existing)
            metadata: New metadata (if None, keep existing)
            
        Returns:
            Updated PromptTemplate if successful, None otherwise
        """
        existing = self.get_template(name, latest=True)
        if not existing:
            return None
            
        # Create a new version
        if version is None:
            # Increment patch version
            major, minor, patch = map(int, existing.version.split('.'))
            version = f"{major}.{minor}.{patch + 1}"
            
        # Create the updated template
        updated = PromptTemplate(
            id=str(uuid.uuid4()),
            name=name,
            description=description or existing.description,
            template=template,
            version=version,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            tags=tags or existing.tags.copy(),
            metadata=metadata or existing.metadata.copy()
        )
        
        # Save the template
        self._save_template(updated)
        
        return updated
    
    def delete_template(self, name: str, version: Optional[str] = None) -> bool:
        """
        Delete a template or specific version.
        
        Args:
            name: Name of the template
            version: Specific version to delete (if None, delete all versions)
            
        Returns:
            True if deleted, False otherwise
        """
        if name not in self._templates:
            return False
            
        filepath = self._get_template_path(name)
        
        if not os.path.exists(filepath):
            return False
            
        if version:
            # Delete specific version
            if version not in self._templates[name]:
                return False
                
            # Load current data
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            # Remove the specific version
            if version in data:
                del data[version]
                
            # If there are no more versions, delete the file
            if data:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                del self._templates[name][version]
            else:
                os.remove(filepath)
                del self._templates[name]
                
            return True
        else:
            # Delete all versions
            try:
                os.remove(filepath)
                del self._templates[name]
                return True
            except Exception as e:
                logger.error(f"Error deleting template {name}: {e}")
                return False


class SystemPromptTemplates:
    """
    Collection of system-level prompt templates.
    
    This class provides access to commonly used system prompts
    for various purposes.
    """
    
    @staticmethod
    def get_library() -> PromptLibrary:
        """Get the prompt library instance."""
        return PromptLibrary()
    
    @classmethod
    def initialize_default_templates(cls) -> None:
        """Initialize default system templates."""
        library = cls.get_library()
        
        # Add default templates
        if not library.get_template("conversation_starter"):
            library.create_template(
                name="conversation_starter",
                description="Initial system message for a new conversation",
                template=(
                    "You are Mnemosyne, an AI executive assistant designed to help with "
                    "{{user_name|the user}}'s tasks, scheduling, and information needs. "
                    "Your conversation style is {{conversation_style|professional}} and "
                    "your primary focus is on {{focus_area|being helpful and accurate}}."
                ),
                tags=["system", "conversation"]
            )
            
        if not library.get_template("memory_retrieval"):
            library.create_template(
                name="memory_retrieval",
                description="System prompt for memory retrieval",
                template=(
                    "Please retrieve relevant information from my memory about {{topic}}. "
                    "Focus on {{aspect|all aspects}} and include {{include_details|all relevant details}}. "
                    "{{additional_instructions|}"
                ),
                tags=["system", "memory"]
            )
            
        if not library.get_template("task_creation"):
            library.create_template(
                name="task_creation",
                description="System prompt for creating a new task",
                template=(
                    "Create a task with the following parameters:\n"
                    "Title: {{title}}\n"
                    "Description: {{description}}\n"
                    "Due date: {{due_date|none}}\n"
                    "Priority: {{priority|normal}}\n"
                    "Tags: {{tags|}}\n"
                ),
                tags=["system", "task"]
            )
    
    @classmethod
    def get_conversation_starter(
        cls, 
        user_name: Optional[str] = None,
        conversation_style: str = "professional",
        focus_area: Optional[str] = None
    ) -> str:
        """
        Get the conversation starter system message.
        
        Args:
            user_name: Name of the user
            conversation_style: Style of conversation
            focus_area: Primary focus area
            
        Returns:
            Filled prompt template
        """
        library = cls.get_library()
        template = library.get_template("conversation_starter")
        
        if not template:
            cls.initialize_default_templates()
            template = library.get_template("conversation_starter")
            
        variables = {
            "conversation_style": conversation_style
        }
        
        if user_name:
            variables["user_name"] = user_name
            
        if focus_area:
            variables["focus_area"] = focus_area
            
        return template.fill(variables)


# Initialize default templates on module import
SystemPromptTemplates.initialize_default_templates()
