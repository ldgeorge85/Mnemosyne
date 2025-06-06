"""
Prompt Templates API endpoints.

This module provides API endpoints for managing prompt templates,
including creating, retrieving, updating, and deleting templates.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.services.llm.prompt_management import PromptLibrary, PromptTemplate


router = APIRouter()


class PromptTemplateCreate(BaseModel):
    """Schema for creating a prompt template."""
    name: str = Field(..., description="Name of the prompt template")
    description: str = Field(..., description="Description of the prompt's purpose")
    template: str = Field(..., description="The prompt template text with variables")
    version: str = Field("1.0.0", description="Semantic version of the template")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PromptTemplateUpdate(BaseModel):
    """Schema for updating a prompt template."""
    template: str = Field(..., description="The prompt template text with variables")
    version: Optional[str] = Field(None, description="Semantic version of the template")
    description: Optional[str] = Field(None, description="Description of the prompt's purpose")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PromptTemplateResponse(BaseModel):
    """Schema for a prompt template response."""
    id: str
    name: str
    description: str
    template: str
    version: str
    created_at: str
    updated_at: str
    tags: List[str]
    metadata: Dict[str, Any]
    variables: List[str]
    
    @classmethod
    def from_model(cls, template: PromptTemplate) -> "PromptTemplateResponse":
        """Convert a PromptTemplate to a PromptTemplateResponse."""
        return cls(
            id=template.id,
            name=template.name,
            description=template.description,
            template=template.template,
            version=template.version,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat(),
            tags=template.tags,
            metadata=template.metadata,
            variables=template.extract_variables()
        )


class PromptFillRequest(BaseModel):
    """Schema for filling a prompt template with variables."""
    variables: Dict[str, Any] = Field(..., description="Variables to fill the template with")


@router.post("/", response_model=PromptTemplateResponse)
async def create_template(
    data: PromptTemplateCreate,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> PromptTemplateResponse:
    """
    Create a new prompt template.
    
    Args:
        data: Template creation data
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Created prompt template
    """
    library = PromptLibrary()
    
    # Check if template with this name already exists
    if library.get_template(data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Prompt template with name '{data.name}' already exists"
        )
    
    template = library.create_template(
        name=data.name,
        description=data.description,
        template=data.template,
        version=data.version,
        tags=data.tags,
        metadata=data.metadata
    )
    
    return PromptTemplateResponse.from_model(template)


@router.get("/", response_model=List[PromptTemplateResponse])
async def list_templates(
    tag: Optional[str] = None,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[PromptTemplateResponse]:
    """
    List all prompt templates, optionally filtered by tag.
    
    Args:
        tag: Filter templates by tag
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        List of prompt templates
    """
    library = PromptLibrary()
    templates = library.list_templates(tag=tag)
    return [PromptTemplateResponse.from_model(t) for t in templates]


@router.get("/{name}", response_model=PromptTemplateResponse)
async def get_template(
    name: str,
    version: Optional[str] = None,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> PromptTemplateResponse:
    """
    Get a prompt template by name and version.
    
    Args:
        name: Name of the template
        version: Specific version to retrieve
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Prompt template
    """
    library = PromptLibrary()
    template = library.get_template(name, version=version)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template '{name}' not found"
        )
    
    return PromptTemplateResponse.from_model(template)


@router.put("/{name}", response_model=PromptTemplateResponse)
async def update_template(
    name: str,
    data: PromptTemplateUpdate,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> PromptTemplateResponse:
    """
    Update a prompt template or create a new version.
    
    Args:
        name: Name of the template
        data: Template update data
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Updated prompt template
    """
    library = PromptLibrary()
    
    # Check if template exists
    if not library.get_template(name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template '{name}' not found"
        )
    
    template = library.update_template(
        name=name,
        template=data.template,
        version=data.version,
        description=data.description,
        tags=data.tags,
        metadata=data.metadata
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update prompt template '{name}'"
        )
    
    return PromptTemplateResponse.from_model(template)


@router.delete("/{name}")
async def delete_template(
    name: str,
    version: Optional[str] = None,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete a prompt template or specific version.
    
    Args:
        name: Name of the template
        version: Specific version to delete
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Success message
    """
    library = PromptLibrary()
    
    # Check if template exists
    if not library.get_template(name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template '{name}' not found"
        )
    
    result = library.delete_template(name, version=version)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete prompt template '{name}'"
        )
    
    return {
        "message": f"Prompt template '{name}'{' version ' + version if version else ''} deleted successfully"
    }


@router.post("/{name}/fill", response_model=Dict[str, str])
async def fill_template(
    name: str,
    data: PromptFillRequest,
    version: Optional[str] = None,
    db = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Fill a prompt template with variables.
    
    Args:
        name: Name of the template
        data: Variables to fill the template with
        version: Specific version to use
        db: Database session
        current_user_id: ID of the authenticated user
        
    Returns:
        Filled prompt
    """
    library = PromptLibrary()
    template = library.get_template(name, version=version)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt template '{name}' not found"
        )
    
    try:
        filled = template.fill(data.variables)
        return {"prompt": filled}
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
