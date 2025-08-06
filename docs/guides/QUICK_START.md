# Quick Start Guide

Get the Mnemosyne Protocol running in 15 minutes.

## Prerequisites

- Docker & Docker Compose
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
# LLM Provider (choose one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://user:pass@localhost/mnemosyne
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=generate-a-long-random-string
ENCRYPTION_KEY=another-long-random-string
```

### 3. Start Services

```bash
# Start all services
docker-compose up

# Or run in background
docker-compose up -d
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## First Use

### 1. Create Your Account

```bash
# Via CLI
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "your-name", "password": "secure-password"}'

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

### 4. Generate Your Deep Signal

```python
# Generate identity signal from your memories
signal = requests.post(
    'http://localhost:8000/api/signals/generate',
    headers={'Authorization': f'Bearer {token}'}
)

print(f"Your signal: {signal.json()}")
```

### 5. Join a Collective (Optional)

```python
# Create sharing contract
contract = {
    "collective_id": "test-collective",
    "domains": ["technical"],
    "depth": "summary",
    "duration_days": 30,
    "k_anonymity": 3
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
# Check logs
docker-compose logs -f

# Reset everything
docker-compose down -v
docker-compose up --build
```

### Database connection issues
```bash
# Verify postgres is running
docker-compose ps

# Test connection
docker-compose exec postgres psql -U postgres -d mnemosyne
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
- See [Troubleshooting Guide](TROUBLESHOOTING.md)

---

*Welcome to cognitive sovereignty.*