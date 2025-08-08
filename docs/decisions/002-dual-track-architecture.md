# ADR-002: Dual-Track Architecture

## Status
Accepted

## Context
Critical review revealed that Mnemosyne was conflating unvalidated hypotheses with proven approaches. We need clear separation between production-ready features and experimental research to maintain scientific integrity while delivering value.

## Decision
Implement a dual-track architecture:
- **Track 1 (Production)**: Standards-based, proven features using W3C DIDs, OAuth 2.0, MLS Protocol
- **Track 2 (Research)**: Experimental features with hypothesis documentation, consent, and validation metrics

## Rationale

### Why Dual-Track
1. **Scientific Integrity**: Prevents "research laundering" by clearly marking experimental features
2. **User Safety**: Production track guarantees stable, proven functionality
3. **Research Freedom**: Allows bold experimentation without compromising stability
4. **Compliance**: Track 1 meets EU AI Act requirements immediately
5. **Trust Building**: Clear separation builds user trust through transparency

### Key Principles
- No experimental code in Track 1
- All Track 2 features require hypothesis documentation
- Graduation criteria defined before implementation
- User consent required for Track 2 participation
- Metrics collection for validation

## Consequences

### Positive
- Clear boundaries between proven and experimental
- Faster production deployment (Track 1 only)
- Rigorous research validation framework
- User trust through transparency
- Compliance-ready architecture

### Negative
- Increased complexity in codebase
- Dual maintenance burden
- Feature flag management overhead
- Slower experimental feature graduation

### Neutral
- Plugin architecture required
- Separate deployment pipelines
- Additional documentation needs
- Metrics infrastructure investment

## Implementation

### Architecture Components
1. **Plugin System**: Enforces track separation at runtime
2. **Feature Flags**: Controls experimental feature access
3. **Research Bus**: Anonymized metrics collection
4. **Consent Service**: Manages Track 2 participation
5. **Validation Pipeline**: Tests hypothesis graduation

### Graduation Criteria
Features move from Track 2 to Track 1 when:
- Hypothesis validated with p < 0.05
- 1000+ user validation (or equivalent)
- No privacy violations observed
- Performance metrics acceptable
- Documentation complete

## Alternatives Considered

### Single Track with Flags
- **Rejected**: Too easy to accidentally enable experimental features
- No clear research methodology enforcement

### Complete Separation
- **Rejected**: Too much code duplication
- Difficult to graduate features

### Beta/Alpha Model
- **Rejected**: Doesn't enforce scientific rigor
- No hypothesis validation framework

## Migration Strategy

### Phase 1: Infrastructure
- Implement plugin architecture
- Add feature flag system
- Deploy research bus

### Phase 2: Feature Migration
- Move experimental features to Track 2
- Document all hypotheses
- Add validation metrics

### Phase 3: Production Hardening
- Remove all experimental code from Track 1
- Add compliance documentation
- Deploy consent management

## Success Metrics
- 0 experimental features in Track 1
- 100% hypothesis documentation for Track 2
- < 5% performance overhead from dual-track
- > 95% user satisfaction with transparency

## References
- [Dual Track Implementation](../DUAL_TRACK_IMPLEMENTATION.md)
- [Critical Review](../CRITICAL_REVIEW_COMPREHENSIVE.md)
- [EU AI Act Compliance](../spec/PROTOCOL.md#compliance)