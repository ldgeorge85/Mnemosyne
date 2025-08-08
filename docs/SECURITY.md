# Security Architecture - Dual-Track System

## Overview

Security in Mnemosyne follows a dual-track approach:
- **Track 1**: Production security using proven standards (OAuth 2.0, MLS, W3C DIDs)
- **Track 2**: Experimental security with additional consent and isolation layers

## Track 1: Production Security

### Authentication & Authorization

#### Primary: OAuth 2.0 + OpenID Connect
```yaml
Provider: Any OIDC-compliant provider
Flow: Authorization Code with PKCE
Tokens: JWT with RS256 signing
Refresh: Rotating refresh tokens
```

#### Secondary: WebAuthn/FIDO2
```yaml
Authenticator: Platform or roaming
Attestation: Direct or none
User Verification: Required
Resident Keys: Supported
```

#### Identity: W3C DIDs
```yaml
Method: did:mnem
Key Type: Ed25519VerificationKey2020
Resolution: Local resolver
Revocation: Status list 2021
```

### Encryption

#### Data at Rest
- **Database**: Transparent Data Encryption (TDE)
- **Files**: AES-256-GCM
- **Keys**: Hardware Security Module (HSM) or KMS
- **Backups**: Encrypted with separate keys

#### Data in Transit
- **TLS**: Version 1.3 minimum
- **E2E**: MLS Protocol (RFC 9420)
- **API**: HTTPS only, HSTS enabled
- **WebSockets**: WSS with origin validation

#### Group Communication (MLS)
```yaml
Cipher Suite: MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519
Key Rotation: Every 7 days or member change
Forward Secrecy: Yes
Post-Compromise Security: Yes
```

### Privacy Protection

#### Differential Privacy
```python
# Track 1: Conservative epsilon
EPSILON_PRODUCTION = 1.0  # Strong privacy
DELTA = 1e-5

# Applied to all aggregate queries
def add_noise(value: float, sensitivity: float) -> float:
    return value + laplace.rvs(scale=sensitivity/EPSILON_PRODUCTION)
```

#### K-Anonymity
```python
# Minimum group size for any data release
K_ANONYMITY_THRESHOLD = 5

# Enforce in queries
def validate_query_result(results: List) -> bool:
    return len(results) >= K_ANONYMITY_THRESHOLD
```

#### Private Set Intersection (PSI)
```python
# For collective operations without revealing members
class PSIProtocol:
    def __init__(self):
        self.hash_functions = 3
        self.false_positive_rate = 0.01
    
    def compute_intersection(self, set_a: Set, set_b: Set) -> int:
        # Returns size without revealing elements
        bloom_a = self.create_bloom_filter(set_a)
        bloom_b = self.create_bloom_filter(set_b)
        return self.estimate_intersection_size(bloom_a, bloom_b)
```

### Access Control

#### Role-Based Access Control (RBAC)
```yaml
Roles:
  - user: Own data only
  - contributor: Share to collectives
  - researcher: Track 2 access (with consent)
  - admin: System management

Permissions:
  - memories:read:own
  - memories:write:own
  - collective:join
  - research:participate
```

#### Attribute-Based Access Control (ABAC)
```python
# Fine-grained control
@require_attributes({
    "track": "production",
    "consent": True,
    "age": ">= 18",
    "region": "allowed_regions"
})
def access_sensitive_feature():
    pass
```

## Track 2: Research Security

### Additional Isolation

#### Container Isolation
```yaml
Research Containers:
  - Separate network namespace
  - Resource limits enforced
  - No production data access
  - Audit logging enabled
```

#### Data Segregation
```python
# Separate databases
PRODUCTION_DB = "postgresql://prod_host/mnemosyne"
RESEARCH_DB = "postgresql://research_host/mnemosyne_research"

# Never cross-connect
assert not can_connect(PRODUCTION_DB, RESEARCH_DB)
```

### Consent Management

#### Granular Consent
```python
class ConsentManager:
    def request_consent(self, user_id: str, experiment: str) -> bool:
        consent = {
            "user_id": user_id,
            "experiment": experiment,
            "timestamp": datetime.utcnow(),
            "ip_address": hash(request.ip),  # Hashed for privacy
            "details": self.get_experiment_details(experiment),
            "risks": self.get_risks(experiment),
            "benefits": self.get_benefits(experiment),
            "data_usage": self.get_data_usage(experiment),
            "duration": "6 months",
            "revocable": True
        }
        return self.store_consent(consent)
```

#### Consent Verification
```python
@require_consent("behavioral_tracking")
@require_track("research")
def track_experimental_behavior(user_id: str, action: Dict):
    # Only executes with valid consent
    pass
```

### Research Data Protection

#### Additional Anonymization
```python
# Track 2: Stronger anonymization
def anonymize_research_data(data: Dict) -> Dict:
    # Remove direct identifiers
    data.pop('user_id', None)
    data.pop('email', None)
    
    # Generalize quasi-identifiers
    data['age'] = generalize_age(data.get('age'))
    data['location'] = generalize_location(data.get('location'))
    
    # Add noise to sensitive attributes
    data['score'] = add_laplace_noise(data.get('score'), epsilon=0.5)
    
    return data
```

## Security Monitoring

### Audit Logging

#### Comprehensive Logging
```python
@audit_log
def sensitive_operation(user_id: str, action: str):
    # Automatically logged:
    # - Timestamp
    # - User ID (hashed)
    # - Action
    # - Result
    # - IP address (hashed)
    # - Track mode
    pass
```

#### Log Retention
```yaml
Production Logs: 90 days
Research Logs: 2 years (for validation)
Security Events: 1 year
Audit Trail: 7 years
```

### Intrusion Detection

#### Anomaly Detection
```python
class AnomalyDetector:
    def __init__(self):
        self.baseline = self.load_baseline()
        self.threshold = 3.0  # Standard deviations
    
    def check_request(self, request: Request) -> bool:
        features = self.extract_features(request)
        anomaly_score = self.calculate_anomaly_score(features)
        
        if anomaly_score > self.threshold:
            self.alert_security_team(request, anomaly_score)
            return False
        return True
```

#### Rate Limiting
```python
RATE_LIMITS = {
    "api": "100/minute",
    "auth": "5/minute",
    "research": "10/minute",
    "export": "1/hour"
}
```

## Incident Response

### Response Plan

1. **Detection**: Automated alerts or user reports
2. **Triage**: Assess severity and scope
3. **Containment**: Isolate affected systems
4. **Investigation**: Determine root cause
5. **Remediation**: Fix vulnerability
6. **Recovery**: Restore normal operations
7. **Lessons Learned**: Update procedures

### Breach Notification

#### Timeline
- Internal notification: Within 1 hour
- User notification: Within 72 hours (GDPR)
- Authority notification: As required by law

#### Transparency
- Public incident report
- Affected user notifications
- Remediation steps published
- Regular status updates

## Compliance

### Regulatory Compliance

#### EU AI Act
- Risk assessment documented
- Transparency requirements met
- Human oversight implemented
- Model cards available

#### GDPR
- Privacy by design
- Data minimization
- Right to erasure
- Data portability

#### CCPA/CPRA
- Opt-out mechanisms
- Data inventory maintained
- Consumer rights honored

### Security Standards

#### OWASP Top 10
- SQL injection prevention
- XSS protection
- CSRF tokens
- Security headers

#### NIST Cybersecurity Framework
- Identify assets
- Protect systems
- Detect incidents
- Respond quickly
- Recover fully

## Security Testing

### Continuous Testing

#### Automated Scanning
```yaml
Daily:
  - Dependency vulnerabilities (Dependabot)
  - Container scanning (Trivy)
  - SAST (Semgrep)

Weekly:
  - DAST (OWASP ZAP)
  - Infrastructure scanning
  - Compliance checks
```

#### Manual Testing
```yaml
Monthly:
  - Code review for security
  - Access control audit
  - Encryption verification

Quarterly:
  - Penetration testing
  - Social engineering assessment
  - Disaster recovery drill
```

## Security Checklist

### Before Deployment
- [ ] All dependencies updated
- [ ] Security headers configured
- [ ] TLS 1.3 enforced
- [ ] Rate limiting enabled
- [ ] Audit logging active
- [ ] Backup encryption verified
- [ ] Incident response team ready

### Track 2 Specific
- [ ] Consent system operational
- [ ] Data segregation verified
- [ ] Additional anonymization active
- [ ] Research firewall configured
- [ ] Hypothesis documentation complete
- [ ] Ethics review completed

## Contact

### Security Team
- Email: security@mnemosyne.org
- PGP Key: [Published on website]

### Bug Bounty
- Program: Active
- Scope: Production systems only
- Rewards: $100 - $10,000
- Safe harbor: Yes

---

*Security is not a feature, it's a foundation. Build on solid ground.*