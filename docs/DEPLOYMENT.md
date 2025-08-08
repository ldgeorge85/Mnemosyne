# Deployment Guide - Dual-Track System

## Docker Commands

### ⚠️ IMPORTANT: Use Correct Docker Commands

**NEVER use `docker-compose` (hyphenated) - it's deprecated**

#### Correct Usage:
```bash
# Development
docker compose up         # Start services
docker compose down       # Stop services
docker compose logs -f    # View logs

# Production (Swarm)
docker stack deploy -c docker-compose.yml mnemosyne
docker service ls
docker service logs mnemosyne_backend
```

## Dual-Track Deployment

### Track 1: Production Core
```yaml
# docker-compose.prod.yml
services:
  backend:
    image: mnemosyne:latest
    environment:
      - TRACK=production
      - EXPERIMENTAL_FEATURES=false
      - EU_AI_ACT_COMPLIANCE=true
      - W3C_DID_ENABLED=true
```

### Track 2: Research Environment
```yaml
# docker-compose.research.yml
services:
  backend:
    image: mnemosyne:research
    environment:
      - TRACK=research
      - EXPERIMENTAL_FEATURES=true
      - CONSENT_REQUIRED=true
      - METRICS_COLLECTION=true
```

## Environment Variables

### Required for Track 1
```bash
# .env.production
DATABASE_URL=postgresql://user:pass@db:5432/mnemosyne
REDIS_URL=redis://redis:6379
OAUTH_CLIENT_ID=your_oauth_id
OAUTH_CLIENT_SECRET=your_oauth_secret
W3C_DID_METHOD=mnem
```

### Additional for Track 2
```bash
# .env.research
RESEARCH_MODE=true
CONSENT_SERVICE_URL=http://consent:8001
METRICS_ENDPOINT=http://metrics:9090
HYPOTHESIS_VALIDATION=true
```

## Deployment Checklist

### Pre-deployment (Track 1)
- [ ] EU AI Act compliance documented
- [ ] Model Cards generated for all AI components
- [ ] W3C DID resolver configured
- [ ] OAuth 2.0 provider configured
- [ ] MLS key packages initialized
- [ ] Differential privacy parameters set

### Pre-deployment (Track 2)
- [ ] Consent management system deployed
- [ ] IRB approval obtained (if applicable)
- [ ] Metrics collection configured
- [ ] Hypothesis documents published
- [ ] Research partnerships established

## Security Considerations

### Track 1 Requirements
- TLS 1.3 for all connections
- OAuth 2.0 + OIDC authentication
- WebAuthn for 2FA
- W3C DIDs for identity
- MLS Protocol for E2E encryption

### Track 2 Additional
- Anonymization pipeline active
- Differential privacy enabled
- Consent verification on all data
- Research data segregation

## Monitoring

### Track 1 Metrics
```prometheus
# Core system health
up{job="mnemosyne_core"} == 1
http_requests_total{track="production"}
auth_failures_total
did_resolutions_total
```

### Track 2 Metrics
```prometheus
# Research metrics
experimental_features_used_total
consent_verifications_total
hypothesis_tests_run_total
validation_metrics{hypothesis="id_compression"}
```

## Rollback Procedures

### Track 1
```bash
# Quick rollback to previous version
docker service update --image mnemosyne:previous mnemosyne_backend

# Or using Swarm
docker stack deploy -c docker-compose.previous.yml mnemosyne
```

### Track 2
```bash
# Disable all experimental features immediately
docker exec mnemosyne_backend python -c "
from app.core.features import FeatureFlags
FeatureFlags.disable_all_experimental()
"
```

## Health Checks

### Endpoints
- `/health` - Basic health check
- `/health/detailed` - Detailed component status
- `/metrics` - Prometheus metrics
- `/compliance/status` - EU AI Act compliance status

---

*Always deploy Track 1 (production) and Track 2 (research) separately to maintain clear boundaries.*