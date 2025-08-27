# AI-Assisted Development Guide for Mnemosyne
*How to effectively use AI coding assistants on this project*
*Last Updated: August 27, 2025*

## Core Principles

### 1. Context-First Development
- Always provide complete file paths and current state
- Reference specific line numbers when discussing code
- Include acceptance criteria upfront
- Share relevant documentation sections

### 2. No Mocking Policy
- Build real features or explicitly defer them
- No fake implementations or placeholder code
- If something can't be built now, mark it as "DEFERRED TO PHASE X"
- Test with real data, real databases, real integrations

### 3. Isolated Task Execution
- Each task should be independently completable
- Minimize cross-dependencies during implementation
- Clear input/output specifications
- Test each component in isolation first

### 4. Documentation as Code
- Update docs in same session as code changes
- Use inline documentation heavily
- Keep CLAUDE.md updated with project decisions
- Generate API docs from code annotations

## Effective AI Prompting Patterns

### Pattern 1: Code Cleanup
```
"Review [file_path] and identify:
1. Competing auth patterns
2. Deprecated imports
3. Unused code
4. Inconsistent patterns
Then delete or consolidate to single approach."
```

### Pattern 2: Feature Implementation
```
"Implement [feature] in [file_path]:
- Current state: [describe]
- Desired state: [describe]
- Use existing pattern from [reference_file]
- Test with: [test criteria]
No mocks, real implementation only."
```

### Pattern 3: Integration
```
"Connect [component A] to [component B]:
- A location: [file_path:lines]
- B location: [file_path:lines]
- Data flow: [describe]
- Validation: [test command]"
```

### Pattern 4: Research Validation
```
"Create validation study for [concept]:
- Hypothesis: [state clearly]
- Data needed: [specify]
- Success metrics: [define]
- Failure criteria: [define]
- Implementation in: [file_path]"
```

## Common Tasks & AI Context

### Task: Shadow Agent Integration (Phase 1.B)
**Context**: "Agents exist but need wiring to agentic flow."
**Files**: 
- `backend/app/services/agentic/executors.py` (add agent activation)
- `shadow/agents/engineer.py` (existing agent)
- `shadow/agents/librarian.py` (existing agent)
- `shadow/agents/priest.py` (existing agent)

### Task: CREATE_MEMORY Action Wiring
**Context**: "Action stub exists, needs executor implementation."
**Files**:
- `backend/app/services/agentic/executors.py` (implement _create_memory)
- `backend/app/services/memory/memory_service.py` (existing service)
**Requirements**: Create real memories with embeddings

### Task: Multi-Agent Collaboration
**Context**: "Test agents working together on complex queries."
**Files**:
- `backend/app/services/agentic/flow_controller.py` (orchestration)
- `backend/app/services/agentic/actions.py` (action definitions)
**Requirements**: Agents should debate and reach consensus

### Task: Receipt UI Components ✅ COMPLETE
**Context**: "Receipt UI viewer is complete and working."
**Files**:
- `frontend/src/pages/ReceiptsSimple.tsx` (complete)
- `frontend/src/api/receipts.ts` (API client complete)
- `frontend/src/pages/Receipts.tsx` (working)
**Status**: Receipt viewer with filtering working

### Task: ICV Research Setup
**Context**: "Begin collecting data for Identity Compression validation."
**Files**:
- `backend/app/services/icv/` (create)
- `backend/app/models/behavioral_signal.py` (create)
**Requirements**: Non-invasive data collection, user consent

## Testing Guidelines for AI

### Unit Tests
```python
# Always write tests like this:
def test_real_database_operation(db: Session):
    """Test with real database, no mocks"""
    user = User(email="test@example.com")
    db.add(user)
    db.commit()
    
    retrieved = db.query(User).filter_by(email="test@example.com").first()
    assert retrieved is not None
    assert retrieved.email == "test@example.com"
```

### Integration Tests
```python
def test_full_auth_flow(client: TestClient):
    """Test complete auth flow, no mocks"""
    # Real login
    response = client.post("/api/v1/auth/login", json={...})
    assert response.status_code == 200
    
    # Real protected endpoint
    token = response.json()["access_token"]
    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
```

## File Structure Context for AI

```
backend/
  app/
    api/v1/         # Endpoints
    core/           # Config, auth, security
    models/         # SQLAlchemy models
    schemas/        # Pydantic schemas
    services/       # Business logic
    db/             # Database utilities
frontend/
  src/
    components/     # React components
    contexts/       # React contexts
    pages/          # Page components
    api/            # API client
    hooks/          # Custom hooks
docs/
  spec/           # Protocol specifications
  concepts/       # Theoretical frameworks
  guides/         # Implementation guides
```

## Common Pitfalls to Avoid

1. **Don't Mock What Should Be Real**
   - Bad: `mock_database_connection()`
   - Good: Use test database with real connection

2. **Don't Estimate Time**
   - Bad: "This will take 2 hours"
   - Good: "This depends on prior task completion"

3. **Don't Build on Unvalidated Concepts**
   - Bad: Implement ICV without validation data
   - Good: Collect data first, validate, then implement

4. **Don't Create New Patterns**
   - Bad: Invent new auth system
   - Good: Use existing AuthManager pattern

## Incremental Development Flow

1. **Clean First**: Remove competing patterns
2. **Connect Second**: Wire existing components
3. **Enhance Third**: Add new capabilities
4. **Validate Fourth**: Test with real data
5. **Document Fifth**: Update all docs

## When to Defer

Mark as "DEFERRED TO PHASE X" when:
- Dependency not yet validated (e.g., ICV)
- Requires user base (e.g., collective intelligence)
- Needs external infrastructure (e.g., IPFS)
- Theoretical concept unproven

## AI Agent Instructions Template

```markdown
PROJECT: Mnemosyne Protocol
PHILOSOPHY: No mocks, build real or defer
CURRENT PHASE: [phase]
TASK: [specific task]
FILES: [list files]
CONTEXT: [provide context]
SUCCESS CRITERIA: [define success]
TEST: [how to test]
```

---

*This guide helps AI assistants understand the project's development philosophy and provide consistent, high-quality contributions.*