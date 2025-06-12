# Mnemosyne - AI Implementation Patterns

---

## Pattern: CrewAI-Based Agent Orchestration with DB-Backed Tracking
- Use CrewAI for sub-agent orchestration, task delegation, and hierarchical agent trees.
- Integrate with a custom AgentManager service for agent lifecycle, DB-backed orchestration, and API/tooling.
- Support recursive sub-agent creation and robust logging/monitoring.
- Persist all agent/task state, logs, and orchestration events in Postgres.
- Expose endpoints for agent definition, linking, tasking, monitoring, and log retrieval.

## Pattern: Cognee-Inspired Memory Reflection and Scoring
- Implement reflection and importance scoring for memories, inspired by Cognee.
- Organize memory hierarchically and link to agent/task logs.
- Integrate memory reflection and scoring with agent/task lifecycle events.

This document outlines standardized implementation patterns for AI assistants working on the Mnemosyne codebase. Following these patterns ensures consistency, maintainability, and high quality across the project.

## Code Organization

### Backend (Python/FastAPI)

#### Directory Structure
```
/backend
├── app
│   ├── api              # API routes organized by domain
│   │   ├── v1           # API version 1 endpoints
│   │   └── dependencies # Endpoint dependencies (auth, permissions)
│   ├── core             # Core application code
│   │   ├── config       # Configuration management
│   │   ├── security     # Security utilities
│   │   └── logging      # Logging configuration
│   ├── db               # Database models and operations
│   │   ├── migrations   # Alembic migrations
│   │   ├── models       # SQLAlchemy models
│   │   └── repositories # Data access layer
│   ├── services         # Business logic services
│   │   ├── memory       # Memory management services
│   │   ├── conversation # Conversation handling
│   │   └── tasks        # Task management services
│   └── utils            # Utility functions
├── tests                # Test suite
│   ├── unit             # Unit tests
│   ├── integration      # Integration tests
│   └── e2e              # End-to-end tests
```

#### Module Structure
- Each module should have a clear single responsibility
- Use `__init__.py` to expose public interfaces
- Keep implementation details private when possible
- Follow Python naming conventions: snake_case for variables/functions, PascalCase for classes

### Frontend (React/TypeScript)

#### Directory Structure
```
/frontend
├── public              # Static assets
├── src
│   ├── api            # API client and service interfaces
│   ├── components     # Reusable UI components
│   │   ├── common     # Shared components
│   │   ├── layout     # Layout components
│   │   └── domain     # Domain-specific components
│   ├── hooks          # Custom React hooks
│   ├── pages          # Page components
│   ├── stores         # Zustand stores
│   ├── styles         # Global styles and theming
│   ├── types          # TypeScript type definitions
│   └── utils          # Utility functions
├── tests              # Test suite
```

#### Component Structure
- Use functional components with hooks
- Organize props with TypeScript interfaces
- Separate business logic from presentation
- Follow component composition patterns
- Use named exports for components

## Coding Standards

### Python/FastAPI

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Document functions, classes, and modules with docstrings
- Use dependency injection for services
- Handle errors with appropriate exception classes and status codes
- Validate input data with Pydantic models
- Use async/await for IO-bound operations

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from app.services.memory import MemoryService
from app.api.dependencies.auth import get_current_user

router = APIRouter()

class MemoryCreate(BaseModel):
    """Schema for creating a new memory."""
    content: str
    tags: List[str]
    importance: Optional[int] = 1

class MemoryResponse(BaseModel):
    """Schema for memory response."""
    id: str
    content: str
    tags: List[str]
    importance: int
    created_at: str
    embedding_id: Optional[str] = None

@router.post("/memories/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory: MemoryCreate,
    memory_service: MemoryService = Depends(),
    user = Depends(get_current_user)
):
    """
    Create a new memory for the current user.
    
    Args:
        memory: The memory data to create
        memory_service: The memory service dependency
        user: The current authenticated user
        
    Returns:
        The created memory
        
    Raises:
        HTTPException: If there's an error creating the memory
    """
    try:
        result = await memory_service.create_memory(user.id, memory)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create memory: {str(e)}"
        )
```

### React/TypeScript

- Use TypeScript for all components and functions
- Follow ESLint and Prettier configurations
- Use functional components with hooks
- Use Chakra UI components for consistent styling
- Separate data fetching logic with custom hooks
- Use Zustand for state management
- Document component props with JSDoc comments

```tsx
import React from 'react';
import { Box, Heading, Text, Tag, Flex, useColorModeValue } from '@chakra-ui/react';

/**
 * Props for the MemoryCard component
 */
interface MemoryCardProps {
  /** Unique identifier for the memory */
  id: string;
  /** Main content of the memory */
  content: string;
  /** List of tags associated with the memory */
  tags: string[];
  /** Timestamp when the memory was created */
  createdAt: string;
  /** Optional importance score (1-5) */
  importance?: number;
  /** Handler for when the card is clicked */
  onClick?: (id: string) => void;
}

/**
 * Card component for displaying a single memory
 */
export const MemoryCard: React.FC<MemoryCardProps> = ({
  id,
  content,
  tags,
  createdAt,
  importance = 1,
  onClick,
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const handleClick = () => {
    if (onClick) {
      onClick(id);
    }
  };
  
  return (
    <Box
      p={4}
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      bg={bgColor}
      boxShadow="sm"
      onClick={handleClick}
      cursor={onClick ? 'pointer' : 'default'}
      transition="all 0.2s"
      _hover={{ boxShadow: onClick ? 'md' : 'sm' }}
    >
      <Heading size="md" mb={2} noOfLines={2}>
        {content.split(' ').slice(0, 5).join(' ')}...
      </Heading>
      <Text noOfLines={3} mb={3}>
        {content}
      </Text>
      <Flex justify="space-between" align="center">
        <Flex gap={2} flexWrap="wrap">
          {tags.map((tag) => (
            <Tag key={tag} size="sm">
              {tag}
            </Tag>
          ))}
        </Flex>
        <Text fontSize="sm" color="gray.500">
          {new Date(createdAt).toLocaleDateString()}
        </Text>
      </Flex>
    </Box>
  );
};
```

## Database Patterns

### Schema Design

- Use meaningful table and column names
- Define explicit primary keys
- Use foreign keys to enforce referential integrity
- Include audit columns (created_at, updated_at)
- Use appropriate data types and constraints
- Implement soft deletes where appropriate

### Migrations

- Create migrations for all schema changes
- Include both up and down migration functions
- Document the purpose of each migration
- Test migrations in development before applying to production
- Never modify existing migrations after they've been applied

```python
"""create memories table

Revision ID: a1b2c3d4e5f6
Revises: 
Create Date: 2025-05-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'memories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', ARRAY(sa.String()), nullable=False),
        sa.Column('importance', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('embedding_id', UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['embedding_id'], ['embeddings.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_memories_user_id', 'memories', ['user_id'])
    op.create_index('idx_memories_embedding_id', 'memories', ['embedding_id'])
    op.create_index('idx_memories_tags', 'memories', ['tags'], postgresql_using='gin')


def downgrade():
    op.drop_index('idx_memories_tags')
    op.drop_index('idx_memories_embedding_id')
    op.drop_index('idx_memories_user_id')
    op.drop_table('memories')
```

## Testing Patterns

### Backend Testing

- Write unit tests for all services and utilities
- Write integration tests for API endpoints
- Use pytest fixtures for test dependencies
- Mock external services
- Use factories for test data
- Aim for at least 80% test coverage

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app
from app.services.memory import MemoryService

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_memory_service():
    with patch("app.api.dependencies.get_memory_service") as mock:
        service = MagicMock(spec=MemoryService)
        mock.return_value = service
        yield service

def test_create_memory(client, mock_memory_service):
    # Setup
    mock_memory_service.create_memory.return_value = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "content": "Test memory",
        "tags": ["test", "memory"],
        "importance": 1,
        "created_at": "2025-05-28T12:00:00Z",
        "embedding_id": None
    }
    
    # Exercise
    response = client.post(
        "/api/v1/memories/",
        json={
            "content": "Test memory",
            "tags": ["test", "memory"],
            "importance": 1
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Verify
    assert response.status_code == 201
    assert response.json()["content"] == "Test memory"
    mock_memory_service.create_memory.assert_called_once()
```

### Frontend Testing

- Write unit tests for components
- Write integration tests for pages
- Test custom hooks
- Mock API calls
- Use React Testing Library for component testing
- Test for accessibility

```tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryCard } from './MemoryCard';

describe('MemoryCard', () => {
  const defaultProps = {
    id: '123',
    content: 'This is a test memory for unit testing',
    tags: ['test', 'memory'],
    createdAt: '2025-05-28T12:00:00Z',
    importance: 3
  };

  it('renders the memory content', () => {
    render(<MemoryCard {...defaultProps} />);
    expect(screen.getByText(/This is a test memory/i)).toBeInTheDocument();
  });

  it('displays all tags', () => {
    render(<MemoryCard {...defaultProps} />);
    expect(screen.getByText('test')).toBeInTheDocument();
    expect(screen.getByText('memory')).toBeInTheDocument();
  });

  it('calls onClick handler when clicked', () => {
    const handleClick = jest.fn();
    render(<MemoryCard {...defaultProps} onClick={handleClick} />);
    
    fireEvent.click(screen.getByText(/This is a test memory/i));
    
    expect(handleClick).toHaveBeenCalledWith('123');
  });

  it('formats the date correctly', () => {
    render(<MemoryCard {...defaultProps} />);
    // This will depend on locale settings in the test environment
    expect(screen.getByText(/5\/28\/2025/)).toBeInTheDocument();
  });
});
```

## Documentation Patterns

### Code Documentation

- Document all public functions, classes, and interfaces
- Use docstrings in Python (Google style)
- Use JSDoc comments in TypeScript
- Include parameters, return values, and exceptions
- Explain complex algorithms or business logic
- Update documentation when code changes

### API Documentation

- Use OpenAPI/Swagger for API documentation
- Document all endpoints, parameters, and responses
- Include example requests and responses
- Document authentication requirements
- Document error responses

## Error Handling

### Backend Error Handling

- Use appropriate HTTP status codes
- Return consistent error response structure
- Log errors with context
- Handle expected exceptions gracefully
- Implement global exception handlers

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

app = FastAPI()

class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the exception here
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
```

### Frontend Error Handling

- Implement error boundaries
- Handle API errors consistently
- Show user-friendly error messages
- Log errors to the console or error tracking service
- Provide retry or recovery options when possible

```tsx
import React, { useState } from 'react';
import { 
  Alert, 
  AlertIcon, 
  AlertTitle, 
  AlertDescription,
  Button,
  Box
} from '@chakra-ui/react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log the error to an error reporting service
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert
          status="error"
          variant="subtle"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          textAlign="center"
          height="200px"
          borderRadius="md"
        >
          <AlertIcon boxSize="40px" mr={0} />
          <AlertTitle mt={4} mb={1} fontSize="lg">
            Something went wrong
          </AlertTitle>
          <AlertDescription maxWidth="sm">
            {this.state.error?.message || 'An unexpected error occurred'}
          </AlertDescription>
          <Button 
            mt={4}
            colorScheme="red"
            onClick={() => this.setState({ hasError: false, error: null })}
          >
            Try again
          </Button>
        </Alert>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

## State Management

### Backend State Management

- Use the database as the source of truth
- Implement caching for performance
- Use Redis for distributed state
- Implement proper locking for concurrent operations
- Consider using event-driven architecture for complex state transitions

### Frontend State Management

- Use Zustand for global state management
- Keep component state local when possible
- Use React Query for server state
- Implement proper loading and error states
- Use optimistic updates for better UX

```tsx
import create from 'zustand';
import { persist } from 'zustand/middleware';

interface Memory {
  id: string;
  content: string;
  tags: string[];
  importance: number;
  createdAt: string;
}

interface MemoryState {
  memories: Memory[];
  selectedMemoryId: string | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setMemories: (memories: Memory[]) => void;
  addMemory: (memory: Memory) => void;
  updateMemory: (id: string, updates: Partial<Memory>) => void;
  deleteMemory: (id: string) => void;
  selectMemory: (id: string | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
}

const useMemoryStore = create<MemoryState>()(
  persist(
    (set) => ({
      memories: [],
      selectedMemoryId: null,
      isLoading: false,
      error: null,
      
      setMemories: (memories) => set({ memories }),
      
      addMemory: (memory) => set((state) => ({ 
        memories: [...state.memories, memory] 
      })),
      
      updateMemory: (id, updates) => set((state) => ({
        memories: state.memories.map((memory) => 
          memory.id === id ? { ...memory, ...updates } : memory
        )
      })),
      
      deleteMemory: (id) => set((state) => ({
        memories: state.memories.filter((memory) => memory.id !== id),
        selectedMemoryId: state.selectedMemoryId === id ? null : state.selectedMemoryId
      })),
      
      selectMemory: (id) => set({ selectedMemoryId: id }),
      
      setLoading: (isLoading) => set({ isLoading }),
      
      setError: (error) => set({ error })
    }),
    {
      name: 'memory-storage',
      partialize: (state) => ({ memories: state.memories }),
    }
  )
);

export default useMemoryStore;
```

## Security Patterns

### Authentication and Authorization

- Use JWT for authentication
- Implement proper token validation
- Use RBAC for authorization
- Validate permissions for all operations
- Implement proper session management

### Data Security

- Encrypt sensitive data at rest
- Use HTTPS for all connections
- Implement proper input validation
- Prevent common security vulnerabilities (OWASP Top 10)
- Implement proper logging (without sensitive data)

## Performance Patterns

### Backend Performance

- Use database indexes appropriately
- Implement caching for frequently accessed data
- Use pagination for large result sets
- Optimize database queries
- Use async/await for IO-bound operations

### Frontend Performance

- Use code splitting
- Implement lazy loading
- Optimize bundle size
- Implement proper memoization
- Use virtualization for long lists

## Accessibility Patterns

- Use semantic HTML
- Implement proper ARIA attributes
- Ensure keyboard navigation
- Maintain sufficient color contrast
- Test with screen readers

## Best Practices for AI Assistant Implementation

### Iterative Development

1. Start with the core structure
2. Implement basic functionality
3. Add tests
4. Refine and optimize
5. Document

### When to Request Human Feedback

- Architectural decisions
- Security-critical components
- Business logic clarifications
- Performance optimizations
- User experience questions

### Providing Context in Commits

- Reference task IDs in commit messages
- Explain the purpose of changes
- Note any potential issues or alternatives considered
- Mention related tasks or dependencies

### Code Review Preparation

- Self-review code before submitting
- Include comprehensive test coverage
- Document any non-obvious decisions
- Highlight areas that may need special attention
