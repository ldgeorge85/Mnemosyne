# ADR-001: Production-Ready Architecture

## Status
Accepted

## Context
Mnemosyne is at a transformation point, moving from prototype to production. We need robust, scalable patterns that align with our "No Mocking Policy" and sovereignty principles.

## Decision
Adopt production-tested architectural patterns including:
- Pydantic Settings for configuration management
- Async pipeline architecture for processing
- Event-driven orchestration via Redis streams
- Qdrant for vector storage with multi-embedding support
- Real integration testing without mocks
- Docker Swarm for production orchestration

## Rationale

### Why These Patterns
1. **Battle-tested**: These patterns run in production systems processing real data
2. **Privacy-first**: Self-hosted, no vendor lock-in, full data control
3. **AI-native**: First-class support for LLM operations and vector search
4. **Scalable**: Horizontal scaling ready from day one
5. **Observable**: Built-in metrics and structured logging

### Why Now
- Current codebase is barely running and needs structure
- These patterns accelerate development without compromising philosophy
- Async-first design matches our performance needs
- Event-driven architecture enables the 50+ agent system

## Consequences

### Positive
- Faster development with proven patterns
- Production-ready from the start
- Better performance through async processing
- Easier scaling when needed
- Clear separation of concerns

### Negative
- More initial complexity than simple approach
- Additional services to manage (Redis, Qdrant)
- Learning curve for async patterns
- More configuration to manage

### Neutral
- Need to migrate existing code gradually
- Docker Swarm instead of Kubernetes (simpler but less features)
- LangChain dependency for agent orchestration

## Implementation Plan

### Week 1
- Pydantic Settings configuration
- Qdrant vector database setup
- Async pipeline architecture
- Redis event streaming

### Week 2
- Event-driven agent orchestration
- LangChain integration
- Webhook system
- Real integration tests

### Week 3
- Docker Swarm configuration
- Monitoring and metrics
- Production deployment
- Performance optimization

## Alternatives Considered

### Simple Monolith
- **Rejected**: Won't scale to 50+ agents
- Would require major refactoring later

### Microservices
- **Rejected**: Too complex for current stage
- Can evolve to this if needed

### Serverless
- **Rejected**: Conflicts with sovereignty principles
- Vendor lock-in concerns

### Mock-Heavy Testing
- **Rejected**: Violates "No Mocking Policy"
- Real integration tests provide more confidence

## References
- [System Architecture](../spec/ARCHITECTURE.md)
- [Updated Roadmap](../ROADMAP.md)
- Production systems demonstrating these patterns in action