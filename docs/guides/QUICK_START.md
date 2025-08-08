# Quick Start Guide - Dual-Track System

Get the Mnemosyne Protocol running in 15 minutes with Track 1 (production) features.

## Prerequisites

- Docker & Docker Compose (use `docker compose`, not `docker-compose`)
- Python 3.9+
- Node.js 16+
- 4GB RAM minimum
- OpenAI/Anthropic API key (for agents)

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone [repository-url] protocol
cd protocol

# Run automated setup
./scripts/setup.sh
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

Required environment variables:
```bash
# Track Configuration
TRACK=production  # Use 'research' for Track 2
EXPERIMENTAL_FEATURES=false

# LLM Provider (choose one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://user:pass@localhost/mnemosyne
REDIS_URL=redis://localhost:6379
QDRANT_HOST=qdrant

# Security & Compliance
SECRET_KEY=generate-a-long-random-string
ENCRYPTION_KEY=another-long-random-string
EU_AI_ACT_COMPLIANCE=true

# W3C Standards
W3C_DID_ENABLED=true
W3C_DID_METHOD=mnem

# OAuth 2.0 (optional but recommended)
OAUTH_CLIENT_ID=your_oauth_id
OAUTH_CLIENT_SECRET=your_oauth_secret
```

### 3. Start Services

```bash
# Start Track 1 (Production) services
docker compose up

# Or run in background
docker compose up -d

# For Track 2 (Research) - requires consent
docker compose -f docker-compose.research.yml up
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## First Use

### 1. Create Your Account (Track 1 - OAuth/WebAuthn)

```bash
# OAuth 2.0 login (recommended)
curl -X GET http://localhost:8000/api/auth/oauth/authorize

# Or WebAuthn registration
curl -X POST http://localhost:8000/api/auth/webauthn/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your-name"}'

# Or visit http://localhost:3000/register
```

### 2. Capture Your First Memory

```python
# Python example
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login', 
    json={'username': 'your-name', 'password': 'secure-password'})
token = response.json()['access_token']

# Create memory
memory = {
    "content": "The Mnemosyne Protocol is running. This is my first memory.",
    "domains": ["technical", "personal"],
    "importance": 0.8
}

response = requests.post('http://localhost:8000/api/memories',
    json=memory,
    headers={'Authorization': f'Bearer {token}'})

print(f"Memory created: {response.json()['id']}")
```

### 3. Trigger Agent Reflection

```python
# Have agents analyze your memory
memory_id = response.json()['id']

# Engineer agent reflects
engineer = requests.post(
    f'http://localhost:8000/api/agents/engineer/reflect',
    json={'memory_id': memory_id},
    headers={'Authorization': f'Bearer {token}'}
)

print(f"Engineer says: {engineer.json()['reflection']}")

# Philosopher agent reflects  
philosopher = requests.post(
    f'http://localhost:8000/api/agents/sage/reflect',
    json={'memory_id': memory_id},
    headers={'Authorization': f'Bearer {token}'}
)

print(f"Sage says: {philosopher.json()['reflection']}")
```

### 4. Generate Your W3C DID (Track 1)

```python
# Generate W3C Decentralized Identifier
did = requests.post(
    'http://localhost:8000/api/identity/did/generate',
    headers={'Authorization': f'Bearer {token}'}
)

print(f"Your DID: {did.json()['did']}")

# For Track 2 (Experimental Deep Signal) - requires consent
# signal = requests.post(
#     'http://localhost:8000/api/experimental/signals/generate',
#     headers={'Authorization': f'Bearer {token}', 'X-Research-Consent': 'true'}
# )
```

### 5. Join a Collective with MLS Protocol (Track 1)

```python
# Create MLS-secured sharing contract
contract = {
    "collective_id": "test-collective",
    "domains": ["technical"],
    "depth": "summary",
    "duration_days": 30,
    "k_anonymity": 3,
    "mls_key_package": "base64_key_package"  # Generated via MLS
}

response = requests.post(
    'http://localhost:8000/api/collective/join',
    json=contract,
    headers={'Authorization': f'Bearer {token}'}
)

print(f"Joined collective: {response.json()}")
```

## Using the Web Interface

1. Navigate to http://localhost:3000
2. Register or login
3. Use the capture interface to add memories
4. View agent reflections in the insights panel
5. Generate and customize your signal
6. Explore collective features (if enabled)

## Track 2 (Research) Features

To enable experimental features:

```bash
# Set environment
export TRACK=research
export EXPERIMENTAL_FEATURES=true
export CONSENT_REQUIRED=true

# Restart services
docker compose down
docker compose -f docker-compose.research.yml up
```

### Available Experimental Features
- Identity compression (100-128 bit)
- Behavioral stability tracking (70/30 hypothesis)
- Symbolic resonance visualization
- Advanced collective intelligence

**Note**: All Track 2 features require explicit consent and contribute anonymized metrics for research validation.

## Common Operations

### Bulk Memory Import

```bash
# Import from markdown files
python scripts/import_memories.py --dir ~/Documents/notes

# Import from Obsidian
python scripts/import_obsidian.py --vault ~/ObsidianVault
```

### Backup Your Data

```bash
# Export all memories
python scripts/export.py --format json --output backup.json

# Backup database
docker-compose exec postgres pg_dump -U postgres mnemosyne > backup.sql
```

### Run Memory Consolidation

```bash
# Trigger consolidation cycle
curl -X POST http://localhost:8000/api/memories/consolidate \
  -H "Authorization: Bearer $TOKEN"
```

## Development Mode

For development with hot-reload:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Troubleshooting

### Services won't start
```bash
# Check logs (use docker compose, not docker-compose)
docker compose logs -f

# Reset everything
docker compose down -v
docker compose up --build
```

### Database connection issues
```bash
# Verify postgres is running
docker compose ps

# Test connection
docker compose exec postgres psql -U postgres -d mnemosyne
```

### Track 1/Track 2 Issues
```bash
# Verify track configuration
curl http://localhost:8000/api/system/track

# Check feature flags
curl http://localhost:8000/api/features

# View compliance status
curl http://localhost:8000/api/compliance/status
```

### Agent errors
- Verify API keys in .env
- Check rate limits
- Try with Ollama for local LLM

## Next Steps

1. **Customize agents** - Edit `backend/app/agents/` to modify behavior
2. **Add memories** - Build your knowledge base
3. **Generate signals** - Refine your identity compression
4. **Join collectives** - Find your people

## Getting Help

- Check [Documentation](../README.md)
- Review [API Reference](../reference/API.md)
- See [Dual-Track Implementation](../DUAL_TRACK_IMPLEMENTATION.md)
- Review [Protocol Spec](../spec/PROTOCOL.md)

---

*Welcome to cognitive sovereignty - built on proven foundations, exploring new frontiers.*