# Mnemosyne Protocol Glossary

*For research-specific and theoretical terms, see [Research Glossary](research/GLOSSARY.md)*

## Core Concepts (Production)

### Dual-Track Development
The separation of proven, standards-based features (Track 1) from experimental, hypothesis-driven features (Track 2). Track 1 is production-ready; Track 2 requires validation.

### Plugin Architecture
Modular system allowing experimental features to be sandboxed and clearly labeled, preventing unvalidated code from entering production systems.

### Feature Flag
Configuration mechanism controlling access to experimental features, with per-user and per-instance overrides, requiring explicit opt-in for Track 2 features.

### Research Bus
Event publishing infrastructure with built-in anonymization (differential privacy) for collecting research data with consent verification.

## Standards & Protocols

### W3C DID (Decentralized Identifier)
W3C standard for portable, self-sovereign identity that doesn't depend on centralized authorities. Replaces custom UUID systems.

### W3C VC (Verifiable Credential)
Cryptographically secure, privacy-respecting digital credentials that can make claims about identity attributes.

### W3C PROV
Data model for expressing provenance information, creating complete audit trails of data lineage and transformations.

### OAuth 2.0
Industry-standard protocol for authorization, allowing secure API access without sharing passwords.

### OIDC (OpenID Connect)
Identity layer built on OAuth 2.0, providing authentication and single sign-on capabilities.

### WebAuthn/FIDO2
W3C standard for phishing-resistant authentication using public key cryptography, supporting hardware security keys and biometrics.

### MLS (Messaging Layer Security)
IETF RFC 9420 protocol for scalable end-to-end encrypted group messaging with forward secrecy and post-compromise security.

### C2PA (Coalition for Content Provenance and Authenticity)
Standard for cryptographically binding content credentials to media, providing "nutrition labels" for AI-generated content.

## Privacy Technologies

### Differential Privacy
Mathematical framework (Dwork et al.) for adding calibrated noise to data to provide formal privacy guarantees while preserving statistical utility.

### PSI (Private Set Intersection)
Cryptographic protocol allowing two parties to find common elements in their sets without revealing non-matching elements.

### K-Anonymity
Privacy model requiring each record to be indistinguishable from at least k-1 other records. Minimum k=3 for Track 1, k=5 for Track 2.

## Experimental Concepts (Track 2)

### Deep Signal
[EXPERIMENTAL] Hypothesized 100-128 bit identity compression. See [hypothesis doc](hypotheses/id_compression.md).

### Behavioral Stability Ratio
[EXPERIMENTAL] Proposed 70/30 stability pattern in cognitive behaviors. See [hypothesis doc](hypotheses/behavioral_stability.md).

### Kartouche
[EXPERIMENTAL] Symbolic identity representation system. Track 1 uses standard avatars; Track 2 explores symbolic resonance.

### Collective Intelligence
[EXPERIMENTAL] Emergent intelligence from privacy-preserving memory aggregation. See [hypothesis doc](hypotheses/collective_intelligence.md).

### Bloom Filter
Space-efficient probabilistic data structure for set membership testing with configurable false positive rates.

### FHE (Fully Homomorphic Encryption)
Encryption scheme allowing computation on encrypted data without decrypting it first (currently experimental due to performance).

## Trust & Reputation

### Lee & See Framework
Research-based framework for "appropriate reliance" on automation, providing metrics for trust calibration in human-AI interaction.

### MDS/ABI Model
Mayer-Davis-Schoorman model measuring trust through three dimensions: Ability, Benevolence, and Integrity.

### EigenTrust
Algorithm for computing global trust values in P2P networks based on transitive trust relationships.

### PageRank
Google's original algorithm for ranking web pages, applicable to trust propagation in social networks.

### SybilGuard
Defense mechanism against Sybil attacks where adversaries create multiple fake identities.

## AI Transparency

### Model Card
Standardized documentation (Mitchell et al. 2019) describing an AI model's intended use, performance characteristics, and limitations.

### Data Sheet
Documentation standard (Gebru et al. 2018) for datasets, describing collection methods, biases, and intended uses.

### Trust Calibration
Process of aligning user trust with actual system capabilities, preventing over-reliance or under-utilization.

## Experimental Concepts (Track 2)

### Identity Compression (HYPOTHESIS)
Unvalidated hypothesis that human identity can be meaningfully compressed to 100-128 bits while preserving distinctiveness. Requires validation: MI > 80%, F1 > 0.75.

### Behavioral Stability (HYPOTHESIS)
Unvalidated hypothesis that human behavior exhibits 70% stability and 30% change over time. Requires validation: ICC > 0.7, PSI < 0.2.

### Resonance (EXPERIMENTAL)
Proposed compatibility metric between identities. Currently being replaced with proven algorithms like EigenTrust.

### Symbolic Identity (RESEARCH)
Mapping of identity to symbolic systems (Tarot, I Ching, etc.). No empirical validation exists.

## Validation Metrics

### MI (Mutual Information)
Information-theoretic measure of the mutual dependence between variables, used to assess information retention in compression.

### ICC (Intraclass Correlation Coefficient)
Statistical measure of reliability for repeated measurements, used to validate behavioral stability over time.

### PSI (Population Stability Index)
Metric measuring the shift in population distribution over time, used to assess behavioral drift.

### KL Divergence
Kullback-Leibler divergence measuring difference between probability distributions, used for behavioral consistency.

### F1 Score
Harmonic mean of precision and recall, used to evaluate classification performance in downstream tasks.

## Regulatory & Compliance

### EU AI Act
European Union regulation on artificial intelligence, in force since August 2024, requiring transparency, risk assessment, and provenance.

### ISO/IEC 42001:2023
International standard for AI management systems, providing framework for responsible AI development and deployment.

### NIST AI RMF
National Institute of Standards and Technology's AI Risk Management Framework for identifying and mitigating AI risks.

### GDPR
General Data Protection Regulation, EU law on data protection and privacy.

### IRB (Institutional Review Board)
Committee that reviews and approves research involving human subjects to ensure ethical standards.

## Development Terms

### Sprint (AI Coding)
Focused coding session (2-4 hours) where an AI agent implements a complete subsystem without interruption.

### Hypothesis Document
Required documentation for experimental features stating the hypothesis, success metrics, validation methods, and failure criteria.

### Model Cards
Transparency documentation describing AI model capabilities, limitations, and appropriate use cases.

### Consent Management
System for obtaining and verifying informed consent for research data collection, compliant with IRB requirements.

### Validation Study
Empirical research to test experimental hypotheses with real data and predefined success criteria.

## Architecture Terms

### Pipeline Architecture
Asynchronous processing system where data flows through transformation stages with concurrent execution.

### Vector Store
Database optimized for similarity search on high-dimensional embeddings (e.g., Qdrant).

### Event Streaming
Asynchronous message passing system using Redis/KeyDB for decoupled communication between services.

### Sandbox
Isolated execution environment for experimental code that cannot affect core system stability.

## Philosophical Terms

### Cognitive Sovereignty
The principle that individuals should have complete control over their cognitive tools and data.

### Progressive Trust
Trust building approach where relationships deepen gradually through verified interactions.

### Scientific Validation
Requirement that hypotheses be empirically tested with real data before implementation in production.

### No Mocking Policy
Development philosophy requiring real implementations or explicit deferral, prohibiting fake or placeholder code.

---

*This glossary covers both Track 1 (proven) and Track 2 (experimental) concepts. Terms marked as HYPOTHESIS, EXPERIMENTAL, or RESEARCH are not validated and should not be treated as established facts.*