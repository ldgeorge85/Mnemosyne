# ADR-003: Strategic Reset and Documentation Cleanup

## Status
Accepted

## Date
August 2025

## Context
Project review identified a disconnect between designed components and running implementation. Key findings:
- Security components built but not integrated
- Documentation not aligned with current state
- Frontend and backend developed separately
- Need for cleaner repository structure

## Decision
Execute a strategic reset focused on:
1. **Immediate security activation** - Wire existing auth components into main.py
2. **Documentation accuracy** - Archive outdated docs, align remaining with reality
3. **Strategic simplification** - Focus on single-user value before collective features
4. **Clean repository structure** - Archive assessment/review materials for clean state

## Rationale

### Why Reset Now
- Project at critical inflection point between failure and success
- Security vulnerabilities are existential risk
- Clean slate enables focused execution
- Documentation confusion prevents collaboration

### Why This Approach
- Activation over rebuilding (components exist, just need wiring)
- Simplification over complexity (prove value incrementally)
- Accuracy over aspiration (document what IS, not what MIGHT BE)

## Implementation

### Immediate Actions
1. Created archive directory for historical docs
2. Moved assessment/, review/, and stale docs to archive
3. Created INTEGRATED_VISION_2025.md as strategic guide (Protocol, not Collective)
4. Created MNEMOSYNE_PRIMER.md as project introduction
5. Updated repository structure for clarity

### Repository Structure
```
mnemosyne/
├── README.md              # Updated with current reality
├── CLAUDE.md              # AI assistant instructions
├── ATTRIBUTION.md         # Credits and acknowledgments
├── archive/               # Historical documents
├── docs/
│   ├── decisions/         # Architecture decisions
│   ├── research/          # Research documentation
│   ├── spec/              # Protocol specifications
│   ├── guides/            # Implementation guides
│   ├── philosophy/        # Vision and principles
│   ├── aimc/              # AI-mediated communication
│   ├── INTEGRATED_VISION_2025.md  # Strategic roadmap
│   └── MNEMOSYNE_PRIMER.md        # Project introduction
├── backend/               # FastAPI implementation
├── frontend/              # React implementation
└── scripts/               # Setup and utilities
```

## Consequences

### Positive
- Clear focus on immediate security fixes
- Honest documentation reflecting actual state
- Clean repository for collaboration
- Preserved historical context in archive

### Negative
- Loss of some planning documentation
- Need to recreate some roadmaps
- Temporary disruption to workflow

### Neutral
- Historical materials preserved but hidden
- Focus shift from vision to execution
- Simplified scope may feel like regression

## Success Metrics
- Authentication working in production
- Zero security vulnerabilities in running code
- Documentation accurately reflects implementation
- New contributors can understand project quickly

## Next Steps
1. Execute Activation Sprint for security
2. Fix core features (chat, memory)
3. Update README with current state
4. Begin building from secure foundation

## References
- [INTEGRATED_VISION_2025.md](../INTEGRATED_VISION_2025.md)
- [MNEMOSYNE_PRIMER.md](../MNEMOSYNE_PRIMER.md)
- Original assessments in archive/assessment/
- Historical reviews in archive/review/