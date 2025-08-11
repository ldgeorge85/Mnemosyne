# AI-Mediated Communication: Theoretical Foundations

## Definition and Core Concepts

### What is AI-Mediated Communication?

According to Hancock, Naaman, and Levy (2020), AI-Mediated Communication (AI-MC) is:

> "Interpersonal communication in which an intelligent agent operates on behalf of a communicator by modifying, augmenting, or generating messages to accomplish communication goals."

This fundamentally differs from traditional Computer-Mediated Communication (CMC) because:
- AI acts as an active participant, not just a passive channel
- The system can modify intent, not just transmit it
- Agency becomes distributed between human and AI

### Key Theoretical Frameworks

#### 1. Trust in Automation (Lee & See, 2004)

**Appropriate Reliance Model:**
- **Calibration**: Trust should match actual system capabilities
- **Resolution**: Trust should be sensitive to context changes
- **Specificity**: Trust should differentiate between functions

**Application to Mnemosyne:**
- Display confidence scores for AI suggestions
- Provide clear capability boundaries
- Enable progressive trust building

#### 2. Organizational Trust Model (Mayer, Davis & Schoorman, 1995)

**ABI Dimensions:**
- **Ability**: Competence in specific domain
- **Benevolence**: Alignment with user interests
- **Integrity**: Adherence to acceptable principles

**Application to Mnemosyne:**
- Ability: Model Cards showing performance metrics
- Benevolence: Privacy-preserving architecture
- Integrity: Transparent provenance chains

#### 3. Media Equation Theory (Reeves & Nass, 1996)

Humans treat computers as social actors, applying social rules unconsciously:
- Politeness norms transfer to AI interactions
- Anthropomorphism is automatic, not deliberate
- Design choices trigger social responses

**Implications:**
- AI agents should respect social conventions
- Clear non-human identification prevents deception
- Behavioral consistency builds trust

## Communication Theory Foundations

### Information Theory (Shannon, 1948)

Traditional model: Source → Encoder → Channel → Decoder → Destination

AI-MC modification:
```
Human Intent → AI Mediator → Enhanced Message → Channel → AI Interpreter → Human Understanding
                     ↑                                          ↑
                Context/Goals                            Context/History
```

### Grice's Cooperative Principle

Maxims for communication that AI must respect:
1. **Quantity**: Provide appropriate amount of information
2. **Quality**: Don't say what you believe false
3. **Relation**: Be relevant
4. **Manner**: Be clear, brief, orderly

AI challenges:
- Can AI have beliefs (Quality)?
- Who determines relevance (Relation)?
- Whose clarity matters (Manner)?

### Speech Act Theory (Austin, 1962)

Three levels of meaning:
1. **Locutionary**: What is said
2. **Illocutionary**: What is intended
3. **Perlocutionary**: What effect occurs

AI-MC complexity:
- AI modifies locutionary acts
- May alter illocutionary force
- Can produce unintended perlocutionary effects

## Levels of AI Mediation

### 1. Augmentation Level
- **Smart Compose**: Predictive text completion
- **Grammar Correction**: Surface-level fixes
- **Translation**: Cross-language communication
- **Control**: High user control, low AI autonomy

### 2. Modification Level
- **Tone Adjustment**: Emotional modulation
- **Style Transfer**: Formality changes
- **Summarization**: Content reduction
- **Control**: Shared control, medium autonomy

### 3. Generation Level
- **Auto-Reply**: Full response creation
- **Agent Negotiation**: Autonomous interaction
- **Creative Writing**: Original content
- **Control**: Low user control, high autonomy

## Ethical Dimensions

### Transparency Requirements

**Disclosure Levels:**
1. **System Level**: Platform uses AI-MC
2. **Feature Level**: Specific function is AI-powered
3. **Instance Level**: This message was AI-modified
4. **Detail Level**: Exact modifications made

### Agency and Responsibility

**Key Questions:**
- Who is accountable for AI-generated content?
- How is consent managed in AI-mediated conversations?
- What are the boundaries of acceptable modification?

**Mnemosyne Approach:**
- Explicit user control over AI involvement
- Complete audit trails via W3C PROV
- Clear attribution in message metadata
- User-defined modification boundaries

### Privacy Implications

**Data Requirements:**
- AI needs context to mediate effectively
- Personal data improves personalization
- Behavioral patterns enable prediction

**Privacy-Preserving Solutions:**
- Local model deployment when possible
- Differential privacy for aggregations
- Encrypted computation for sensitive data
- User-controlled data retention

## Research Findings

### Impact on Communication (2020-2024)

**Positive Effects:**
- Reduced communication barriers
- Enhanced accessibility
- Improved cross-cultural communication
- Increased efficiency

**Negative Effects:**
- Authenticity concerns
- Trust degradation with disclosure
- Homogenization of expression
- Reduced emotional nuance

### Trust Dynamics

Recent studies show:
- Users trust AI suggestions 72% of the time
- Trust drops 31% when AI involvement disclosed
- Behavioral adaptation occurs within 2-3 weeks
- Cultural factors significantly affect acceptance

### Language Evolution

AI-MC is affecting language through:
- Convergence toward "standard" expressions
- Reduction in linguistic diversity
- Emergence of AI-detectable patterns
- Creation of new communication norms

## Implications for Mnemosyne

### Design Principles

1. **Progressive Disclosure**: Start with augmentation, enable generation
2. **Trust Calibration**: Show confidence, limitations, alternatives
3. **User Sovereignty**: Full control over AI involvement
4. **Cultural Sensitivity**: Adapt to communication norms
5. **Privacy by Design**: Minimize data requirements

### Implementation Requirements

- Model Cards for all AI components
- Provenance tracking for modifications
- Confidence scoring for suggestions
- User preference learning
- Behavioral consistency monitoring

### Research Opportunities

1. **Identity Compression**: Can behavioral patterns compress to 100-128 bits?
2. **Trust Formation**: How does AI mediation affect trust building?
3. **Cultural Adaptation**: Can AI respect diverse communication styles?
4. **Privacy Preservation**: Can effective mediation work with minimal data?

## Conclusion

AI-MC represents a fundamental shift in human communication, requiring careful consideration of trust, agency, and authenticity. The Mnemosyne Protocol must balance the benefits of AI mediation with preservation of human agency and authentic connection.

## References

- Austin, J. L. (1962). How to do things with words
- Grice, H. P. (1975). Logic and conversation
- Hancock, J. T., et al. (2020). AI-mediated communication: Definition, research agenda, and ethical considerations
- Lee, J. D., & See, K. A. (2004). Trust in automation: Designing for appropriate reliance
- Mayer, R. C., Davis, J. H., & Schoorman, F. D. (1995). An integrative model of organizational trust
- Reeves, B., & Nass, C. (1996). The media equation
- Shannon, C. E. (1948). A mathematical theory of communication