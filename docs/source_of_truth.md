# Mnemosyne - Source of Truth

This document serves as the definitive reference for the Mnemosyne project structure, tracking all files and directories as they are created, modified, or deleted.

> **Note:** Mnemosyne (named after the ancient Greek Titan goddess of memory and remembrance) is a web-based conversational AI system with advanced memory capabilities, scheduling features, and agentic task execution abilities. The implementation plan (`implementation_plan.md`) includes a detailed phase-based task tracker table, expanded best practices for testing, documentation, CI/CD, security, deployment, and compliance. Refer to both this document and the implementation plan for the most up-to-date project guidance.

## Project Structure

```
/home/lewis/dev/personal/mnemosyne/
├── docs/
│   ├── implementation_plan.md   # Detailed system architecture and technical implementation details
│   ├── task_tracker.md          # Project phases and specific tasks with checkboxes
│   ├── source_of_truth.md       # This file - tracking all project files and structure
│   ├── ai_patterns.md           # Implementation patterns for AI assistants (planned)
│   ├── progress_template.md     # Template for AI progress reporting (planned)
│   ├── feedback_process.md      # Process for AI assistants to request human feedback (planned)
│   ├── configuration.md         # Configuration parameter documentation (planned)
│   ├── database/
│   │   └── schema_changes.md    # Documentation of database schema changes (planned)
│   ├── components/              # Documentation for individual system components (planned)
│   └── api/                     # API specifications and examples (planned)
```

## Documentation Overview

### implementation_plan.md
Contains the complete system architecture, technical implementation details, and a detailed phase-based task tracker table for Mnemosyne, including:
- Project identity and overview
- Core components (backend and frontend)
- Data architecture
- Core services
- Technical implementation details
- API design
- Deployment architecture
- Best practices for testing, documentation, CI/CD, security, deployment, and compliance
- Task tracker table mapping features to phases, AI assistant roles, human review requirements, dependencies, and status
- Future extension points
- Documentation hierarchy and AI assistant collaboration framework

### task_tracker.md
Outlines all project tasks organized into logical phases and provides detailed, granular checklists for each:
- Phase 1: Project Setup and Foundation (1-2 weeks)
- Phase 2: Core Functionality (2-3 weeks)
- Phase 3: Advanced Features (2-3 weeks)
- Phase 4: Integration and Testing (1-2 weeks)
- Phase 5: Polishing and Deployment (1 week)

Each phase contains detailed tasks with checkboxes for tracking progress, with additional information on:
- AI assistant roles (Primary, Support, Review)
- Human review requirements (Required, Optional, None)
- Implementation guidelines for AI assistants
- Human oversight guidelines

> The task tracker in `implementation_plan.md` provides a high-level, phase-based overview, while `task_tracker.md` contains granular, actionable tasks for day-to-day tracking. Keep both documents in sync as the project evolves.

## Update History

- **2025-05-28**: Initial project structure and documentation created
  - Created docs directory
  - Added implementation_plan.md
  - Added task_tracker.md
  - Added source_of_truth.md
- **2025-05-28**: Updated documentation with recommendations
  - Updated `implementation_plan.md` with detailed recommendations on task ownership, database migration strategy (Alembic), environment configuration, and testing goals.
  - Updated `task_tracker.md` to include notes on task ownership and refined timelines for better project tracking.
- **2025-05-28**: Updated project branding and AI assistant implementation approach
  - Renamed project to "Mnemosyne" throughout all documentation
  - Updated `implementation_plan.md` to reflect the AI assistant implementation approach, expanded documentation hierarchy, and additional future extension points
  - Updated `task_tracker.md` with AI assistant roles, human review requirements, and implementation guidelines
  - Updated `source_of_truth.md` to reflect new documentation structure and Mnemosyne branding

### AI Assistant Collaboration Documents (Planned)

#### ai_patterns.md
Standardized implementation patterns for AI assistants working on the Mnemosyne codebase, including:
- Code organization and style guidelines
- Testing patterns and requirements
- Documentation standards
- Error handling approaches
- State management patterns
- Component architecture

#### progress_template.md
Template for AI assistants to report progress on tasks, including:
- Task ID and description
- Current status and completion percentage
- Implementation details and approach
- Challenges encountered and solutions applied
- Next steps and dependencies
- Questions or areas requiring human guidance

#### feedback_process.md
Process for AI assistants to request human feedback during implementation, including:
- When to request feedback (decision points, architecture questions, etc.)
- How to format feedback requests for maximum clarity
- How to respond to and incorporate received feedback
- Escalation paths for critical blockers

#### configuration.md
Comprehensive documentation of all configurable parameters in Mnemosyne, including:
- Environment variables and their purposes
- Configuration file formats and locations
- Default values and valid ranges
- Security considerations for sensitive configuration
- Configuration inheritance and override patterns

### Database Documentation (Planned)

#### schema_changes.md
Documentation of all database schema changes, including:
- Migration version and timestamp
- Description of changes
- Reason for changes
- Backward compatibility considerations
- Rollback procedures
