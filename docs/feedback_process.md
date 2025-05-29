# Mnemosyne - AI Feedback Process

This document outlines the standardized process for AI assistants to request and incorporate human feedback during the implementation of Mnemosyne. Following this process ensures effective collaboration between AI assistants and human developers.

## When to Request Feedback

AI assistants should request human feedback in the following scenarios:

### Critical Decision Points
- **Architecture Decisions**: When multiple architectural approaches are viable and a decision would significantly impact the project structure
- **Technology Selection**: When choosing between different libraries, frameworks, or tools that have long-term implications
- **Performance Trade-offs**: When performance optimizations might affect readability, maintainability, or other quality attributes
- **Security Considerations**: When implementing security-critical features or making decisions that affect data protection

### Implementation Challenges
- **Technical Blockers**: When encountering technical limitations that prevent progress
- **Requirement Clarification**: When requirements are ambiguous or conflicting
- **Edge Cases**: When handling complex edge cases that might require business logic decisions
- **Implementation Complexity**: When a task is unexpectedly complex or requires significant deviations from the original plan

### Quality Assurance
- **Review Requests**: When completing significant features or components that require human validation
- **Testing Strategy**: When designing test strategies for critical system components
- **Performance Concerns**: When identifying potential performance bottlenecks
- **Security Vulnerabilities**: When discovering potential security issues

## How to Format Feedback Requests

When requesting feedback, format your request clearly to maximize the likelihood of receiving actionable guidance:

### Feedback Request Template

```markdown
## Feedback Request: [Brief Title]

### Context
[Provide sufficient background information for the human to understand the situation without requiring additional context]

### Current Approach
[Describe your current implementation or the approach you're considering]

### Alternatives Considered
[List alternative approaches you've considered, with pros and cons for each]

### Specific Questions
1. [Ask clear, specific questions that can be directly answered]
2. [Limit to 3-5 questions maximum]

### Impact on Project
[Explain how this decision affects project timeline, architecture, or other aspects]

### Urgency
[Specify if this is blocking progress and any time sensitivity]
```

### Example Feedback Request

```markdown
## Feedback Request: Memory Embedding Storage Strategy

### Context
I'm implementing the vector embedding storage for the memory system. We need to store and query potentially millions of embeddings efficiently.

### Current Approach
I'm planning to use pgvector's HNSW index type for efficient similarity search with the following configuration:
- 16 dimensions per vector
- Cosine similarity as the distance metric
- HNSW index with m=16, ef_construction=64

### Alternatives Considered
1. **IVFFlat index**: Faster to build but less accurate for our use case
   - Pros: Quicker indexing time, lower memory usage during creation
   - Cons: Less accurate for high-dimensional vectors, requires retraining

2. **Direct Qdrant integration**: Using a dedicated vector DB instead of pgvector
   - Pros: Purpose-built for vector search, potentially better performance
   - Cons: Additional service dependency, more complex architecture

### Specific Questions
1. Is pgvector with HNSW the preferred approach, or should we use a dedicated vector database?
2. Are the HNSW parameters (m=16, ef_construction=64) appropriate for our use case?
3. Should we implement a fallback strategy if vector search performance degrades with scale?

### Impact on Project
This decision affects the scalability of the memory system and query performance. It also impacts our database migration strategy and potential future transitions.

### Urgency
Medium urgency - I can continue implementation with pgvector but would prefer guidance before finalizing the indexing strategy.
```

## Responding to Feedback

After receiving human feedback, acknowledge it and incorporate it into your implementation:

### Feedback Incorporation Process

1. **Acknowledge the Feedback**: Explicitly acknowledge the feedback received
2. **Clarify if Needed**: If any aspects of the feedback are unclear, ask follow-up questions
3. **Update Implementation Plan**: Explain how you'll modify your approach based on the feedback
4. **Document the Decision**: Record the decision and rationale in the appropriate documentation
5. **Implement the Changes**: Apply the feedback to your implementation
6. **Report Back**: After implementing the changes, report back on the outcome

### Example Feedback Incorporation

```markdown
Thank you for the feedback on the memory embedding storage strategy. Based on your guidance, I will:

1. Proceed with pgvector using the HNSW index as the primary approach
2. Adjust the parameters to m=32 and ef_construction=100 as suggested for better recall
3. Implement the suggested monitoring mechanism to track query performance
4. Document the approach in the database architecture document
5. Add a note about potential future migration to a dedicated vector DB if scale requires it

I'll update the implementation and report back when the changes are complete.
```

## Escalation Process

If feedback is critical for progress but not received in a timely manner, follow this escalation process:

1. **Initial Request**: Submit a well-formatted feedback request as outlined above
2. **Follow-up**: If no response within 24 hours (or the agreed timeframe), send a follow-up with a clear subject line indicating it's a follow-up
3. **Proceed with Best Judgment**: If no response after follow-up, proceed with your best judgment, documenting your decision and rationale
4. **Flag for Review**: Mark the implementation for priority review when human availability improves

## Tracking Feedback

To maintain a record of feedback requests and responses:

1. **Document in Progress Reports**: Include a summary of feedback requested and received in your progress reports
2. **Reference Task IDs**: Always reference the relevant task ID in feedback requests
3. **Update Documentation**: Update relevant documentation with decisions made based on feedback
4. **Link to Discussions**: When possible, include links to the feedback discussions in commit messages or code comments

## Best Practices for Feedback Requests

### Do's
- Be specific and concise in your questions
- Provide sufficient context for informed decisions
- Propose a recommended approach when possible
- Include pros and cons of alternatives
- Specify the impact and urgency of the decision

### Don'ts
- Request feedback on minor implementation details that don't significantly impact the project
- Ask open-ended questions without providing context or alternatives
- Overwhelm with too many questions in a single request
- Wait until an implementation is complete before seeking feedback on the approach
- Assume human developers are familiar with all details of your implementation

## Continuous Improvement

The feedback process itself should evolve as the project progresses:

1. **Feedback on Feedback**: Periodically review the effectiveness of the feedback process
2. **Adjust Templates**: Refine templates based on which feedback requests receive the most helpful responses
3. **Build Knowledge Base**: Document common feedback patterns to reduce the need for repetitive questions
4. **Automate Where Possible**: Implement automated checks that can reduce the need for human feedback on routine matters
