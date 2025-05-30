# Mnemosyne - Development Guidelines

## Overview

This document outlines the development standards, workflows, and best practices for contributing to the Mnemosyne project. Adhering to these guidelines ensures code quality, maintainability, and a consistent development experience across the team.

## Code Style Guide

### Python (Backend)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use [Black](https://github.com/psf/black) for code formatting with a line length of 88 characters
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Use type hints for all function parameters and return values
- Document all modules, classes, and functions using docstrings (Google style)

Example:

```python
from typing import Dict, List, Optional

def process_data(input_data: Dict[str, any], options: Optional[List[str]] = None) -> Dict[str, any]:
    """
    Process the input data according to specified options.

    Args:
        input_data: The dictionary containing input data to process
        options: Optional list of processing options

    Returns:
        Processed data as a dictionary

    Raises:
        ValueError: If input_data is empty or invalid
    """
    if not input_data:
        raise ValueError("Input data cannot be empty")
    
    # Processing logic here
    result = {
        "processed": True,
        "data": input_data
    }
    
    return result
```

### TypeScript/JavaScript (Frontend)

- Use ESLint with the project's `.eslintrc.js` configuration
- Use Prettier for code formatting with a line length of 100 characters
- Use TypeScript for all new code
- Prefer functional components with hooks over class components
- Follow React best practices for component structure and props
- Use JSDoc comments for complex functions and components

Example:

```typescript
import React, { useState, useEffect } from 'react';
import { User } from '../types';

interface UserProfileProps {
  /** The user ID to display */
  userId: string;
  /** Callback when profile is updated */
  onProfileUpdate?: (user: User) => void;
}

/**
 * Displays a user profile with editable fields
 * 
 * @param props - Component properties
 * @returns User profile component
 */
export const UserProfile: React.FC<UserProfileProps> = ({ userId, onProfileUpdate }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  useEffect(() => {
    // Fetch user data
    const fetchUser = async () => {
      setIsLoading(true);
      try {
        // API call here
        const userData = await api.getUser(userId);
        setUser(userData);
      } catch (error) {
        console.error('Error fetching user:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchUser();
  }, [userId]);
  
  // Component rendering logic
  
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
};
```

### CSS/SCSS

- Use the Chakra UI theming system for styling components
- Create custom themes in the `src/styles` directory
- Use responsive design principles for all components
- Use semantic classnames following BEM naming convention for custom CSS

### SQL

- Use uppercase for SQL keywords (SELECT, INSERT, etc.)
- Use singular names for tables
- Use snake_case for column names
- Always include primary keys and timestamps (created_at, updated_at)
- Use foreign key constraints for relationships
- Document complex queries with comments

## Git Workflow

### Branch Naming Convention

- `feature/<issue-number>-<short-description>` for new features
- `bugfix/<issue-number>-<short-description>` for bug fixes
- `hotfix/<issue-number>-<short-description>` for critical fixes
- `chore/<issue-number>-<short-description>` for maintenance tasks
- `docs/<issue-number>-<short-description>` for documentation updates

Example: `feature/42-add-conversation-search`

### Commit Message Convention

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Changes that do not affect code meaning (white-space, formatting, etc.)
- `refactor`: Code changes that neither fix a bug nor add a feature
- `perf`: Code changes that improve performance
- `test`: Adding or correcting tests
- `chore`: Changes to the build process or auxiliary tools

Example:
```
feat(conversation): add search functionality

Implement search by title and content within conversations.
Includes API endpoints and frontend components.

Closes #42
```

### Pull Request Process

1. **Create a new branch** from `main` following the branch naming convention
2. **Develop** your feature, bug fix, or other contribution
3. **Write tests** to verify your changes
4. **Run the linter** to ensure code quality
5. **Commit your changes** following the commit message convention
6. **Push your branch** to the repository
7. **Create a pull request** against the `main` branch
8. **Fill out the PR template** with all required information
9. **Request reviews** from appropriate team members
10. **Address review feedback** and update the PR as needed
11. **Merge the PR** once it's approved and CI passes
12. **Delete the branch** after merging

### PR Template

```markdown
## Description
[Provide a brief description of the changes in this PR]

## Related Issue
[Reference the issue this PR addresses, e.g., "Closes #42"]

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update

## How Has This Been Tested?
[Describe the tests you ran to verify your changes]

## Checklist:
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

## Code Review Process

### Review Guidelines

1. **Be respectful and constructive** in all comments
2. **Focus on the code, not the person**
3. **Be specific** about what needs to be changed and why
4. **Provide examples** when suggesting alternative approaches
5. **Consider the context** of the PR and the project's constraints
6. **Don't nitpick** on minor style issues that can be handled by linters
7. **Approve with suggestions** for minor changes that don't need another review

### Review Checklist

- Does the code follow the project's style guide?
- Is the code maintainable and easy to understand?
- Are there appropriate tests for the changes?
- Is the documentation updated to reflect the changes?
- Does the code handle edge cases and errors appropriately?
- Are there any security concerns with the implementation?
- Is the code performant and scalable?
- Does the code introduce any technical debt?
- Are there any unnecessary dependencies added?

## Testing Guidelines

### Backend Testing

- Use `pytest` for all tests
- Organize tests in a structure that mirrors the production code
- Write unit tests for individual functions and methods
- Write integration tests for API endpoints
- Use fixtures to set up test data
- Mock external dependencies when appropriate
- Aim for at least 80% test coverage

Example:

```python
import pytest
from app.services.memory import MemoryService

@pytest.fixture
def memory_service():
    # Setup memory service with test dependencies
    return MemoryService(db_session=mock_db_session)

def test_create_memory(memory_service):
    # Given
    memory_data = {"content": "Test memory", "importance": 5}
    
    # When
    result = memory_service.create_memory(user_id="test-user", data=memory_data)
    
    # Then
    assert result.content == "Test memory"
    assert result.importance == 5
    assert result.user_id == "test-user"
```

### Frontend Testing

- Use Jest and React Testing Library for component tests
- Write unit tests for utility functions and hooks
- Write integration tests for components that interact with state or APIs
- Use mock service workers (MSW) to mock API calls
- Test user interactions and UI behaviors
- Test accessibility compliance

Example:

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ConversationList } from './ConversationList';
import { mockConversations } from '../test/mocks';

// Mock the store
jest.mock('../stores/conversationStore', () => ({
  useConversationStore: () => ({
    conversations: mockConversations,
    fetchConversations: jest.fn(),
    isLoading: false
  })
}));

describe('ConversationList', () => {
  it('renders all conversations', () => {
    render(<ConversationList />);
    
    expect(screen.getByText(mockConversations[0].title)).toBeInTheDocument();
    expect(screen.getByText(mockConversations[1].title)).toBeInTheDocument();
  });
  
  it('navigates to conversation detail when clicked', async () => {
    const mockNavigate = jest.fn();
    
    // Mock react-router
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate
    }));
    
    render(<ConversationList />);
    
    fireEvent.click(screen.getByText(mockConversations[0].title));
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(`/conversations/${mockConversations[0].id}`);
    });
  });
});
```

## Continuous Integration/Continuous Deployment (CI/CD)

### CI Checks

All PRs must pass the following CI checks before merging:

1. **Linting**: ESLint for frontend, Flake8 for backend
2. **Type checking**: TypeScript type checking for frontend, Mypy for backend
3. **Unit tests**: Jest for frontend, Pytest for backend
4. **Integration tests**: End-to-end tests with Cypress
5. **Build verification**: Ensure the application builds successfully
6. **Security scanning**: Check for vulnerabilities in dependencies

### CD Pipeline

The deployment process follows these steps:

1. **Build**: Create Docker images for all services
2. **Test**: Run smoke tests on the built images
3. **Stage**: Deploy to staging environment
4. **Verify**: Run integration tests against staging
5. **Approve**: Manual approval for production deployment
6. **Deploy**: Deploy to production environment
7. **Monitor**: Watch for any issues post-deployment

## Environment Setup

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/organization/mnemosyne.git
   cd mnemosyne
   ```

2. **Start the development environment**:
   ```bash
   ./manage.sh start-dev
   ```

3. **Access the applications**:
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - Swagger UI: http://localhost:8000/docs
   - Redis Commander: http://localhost:8081
   - PGAdmin: http://localhost:5050

### Docker-based Development

All development should happen inside Docker containers to ensure consistency across environments:

1. **Install prerequisites**:
   - Docker
   - Docker Compose
   - Git

2. **Environment variables**:
   - Copy `.env.example` to `.env` and update as needed
   - Never commit `.env` files to version control

3. **IDE integration**:
   - VS Code: Use the provided `.vscode` settings for Docker integration
   - Use the Remote - Containers extension for developing inside containers

## Documentation Standards

### Code Documentation

- Use docstrings for all public modules, classes, and functions
- Keep documentation close to the code it describes
- Update documentation when changing code behavior
- Document complex algorithms and business logic with comments

### Project Documentation

- Keep documentation in the `docs` directory
- Use Markdown for all documentation files
- Include diagrams when appropriate (as SVG or PNG)
- Update the `source_of_truth.md` file when adding or modifying project files

### API Documentation

- Document all API endpoints using OpenAPI/Swagger
- Include example requests and responses
- Document authentication requirements
- Document error responses and status codes

## Dependencies Management

### Backend Dependencies

- Use `pip` and `requirements.txt` for Python dependencies
- Pin all dependency versions for reproducibility
- Use `requirements-dev.txt` for development-only dependencies
- Document why dependencies are added in commit messages

### Frontend Dependencies

- Use `npm` for JavaScript/TypeScript dependencies
- Lock dependencies with `package-lock.json`
- Minimize production dependencies
- Regularly update dependencies to address security vulnerabilities

## Security Guidelines

- Never commit credentials or secrets to version control
- Use environment variables for all sensitive configuration
- Follow the principle of least privilege for all API endpoints
- Validate all user input on both client and server
- Use parameterized queries to prevent SQL injection
- Use HTTPS for all API communications
- Implement proper authentication and authorization checks
- Regularly update dependencies to address security vulnerabilities

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Chakra UI Documentation](https://chakra-ui.com/docs/getting-started)
- [Docker Documentation](https://docs.docker.com/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
