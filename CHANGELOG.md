# Changelog

## 2025-08-06: Major Specification Update

### Changed
- **No More Mocking**: Removed all references to mocking or fake implementations across all documentation
  - ZK proofs deferred to v2 (not mocked)
  - All features are either built real or deferred
  - Updated TASK_TRACKING.md, CRITICAL_PATH.md, IMPLEMENTATION_DESIGN.md

### Added
- **MNEMOSYNE_PROTOCOL_SPECIFICATION_v3.md**: Cleaned up, deduplicated specification
  - Better organization with clear sections
  - Clarified naming: "The Mnemosyne Protocol" is the full system
  - "Collective Codex" is a component (special Mnemosyne instance)
  - Integrated all research findings
  - Clear implementation phases

- **ROADMAP.md**: Clear, concise development roadmap
  - Shows what's real vs deferred
  - User journey and technical journey
  - No mocking philosophy clearly stated

- **PROJECT_STATUS.md**: Current state summary
  - 40% complete overall
  - All integration tasks done
  - Ready for Week 1 development

### Fixed
- Removed host-specific paths from documentation
- Clarified Mnemosyne Protocol vs Collective Codex naming
- Updated privacy implementation to show phased approach (not mocked)

### Repository State
- ✅ Git initialized
- ✅ All codebases integrated
- ✅ Docker configuration complete
- ✅ Documentation updated
- ✅ Ready for development

### Key Decisions
1. **No Mocking Policy**: Build real features or defer them
2. **Naming**: "The Mnemosyne Protocol" (full system), "Collective Codex" (component)
3. **ZK Proofs**: Deferred to v2.0 - will build real implementation when ready
4. **MVP Focus**: K-anonymity (k=3) for privacy, basic trust system, real features only

### Next Steps
- Begin Week 1: Extend memory model for sharing
- Implement sharing contracts
- Integrate Shadow orchestration

---

## 2025-08-06: Repository Integration

### Added
- Merged 4 codebases into unified repository:
  - backend/ (from Mnemosyne)
  - frontend/ (from Mnemosyne)
  - shadow/ (from Shadow)
  - dialogues/ (from Dialogues)
  - collective/ (new, with Chatter template)

### Created
- docker-compose.yml for unified deployment
- .env.example with all configuration
- scripts/setup.sh for easy installation
- Docker postgres configuration with pgvector

### Documentation Created
- INTEGRATION_PLAN.md
- PRIVACY_IMPLEMENTATION.md
- MVP_FEATURES.md
- CRITICAL_PATH.md
- RESEARCH_FINDINGS_2025.md

---

*For detailed commit history, see git log*