# AI Agent Guide for Chatter

This guide is specifically for AI coding agents (like Claude, GPT-4, etc.) working with the Chatter codebase.

## Quick Orientation

Chatter is a knowledge ingestion platform that:
1. Connects to documentation sources (Outline, BookStack, etc.)
2. Processes documents with LLM-based extraction
3. Stores in vector database for semantic search
4. Provides API for retrieval

## Code Structure

```
template/
├── sources/          # Data source connectors
├── processors/       # Document processing (summarization, extraction)
├── storage/         # Vector and structured storage
├── app/            # FastAPI application
└── docker/         # Container configuration
```

## Common Tasks

### 1. Adding a New Data Source

Create a new source by copying the pattern:

```python
# sources/mysource/connector.py
from ..base import BaseSource, SourceConfig, Collection

class MySource(BaseSource):
    """What this source does."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MYSOURCE_API_KEY")
        
    def get_config(self) -> SourceConfig:
        return SourceConfig(
            name="mysource",
            description="Description here",
            auth_type="api_key",
            required_env_vars=["MYSOURCE_API_KEY"]
        )
    
    def test_connection(self) -> bool:
        # Test API connection
        pass
        
    def get_collections(self) -> List[Collection]:
        return [Collection(
            name="mysource_data",
            description="What's stored",
            embedding_fields=["content"],
            metadata_fields=["id", "title"]
        )]
    
    def query_data(self) -> List[Dict]:
        # Your data fetching logic
        pass
```

Then register it in `sources/__init__.py`:
```python
from .mysource import MySource
SOURCE_REGISTRY["mysource"] = MySource
```

### 2. Adding Custom Prompts

Each source can have custom prompts:

```python
# sources/mysource/prompts.py
SUMMARY_PROMPT = """
Summarize this {data_type}:
{content}

Extract:
1. Main points
2. Key details
3. Action items
"""

def get_prompt(prompt_type: str, **kwargs):
    prompts = {"summary": SUMMARY_PROMPT}
    return prompts[prompt_type].format(**kwargs)
```

### 3. Testing Your Changes

1. **Test source connection**:
```python
from sources import get_source
source = get_source("mysource")
assert source.test_connection()
```

2. **Test data retrieval**:
```python
data = source.query_data()
print(f"Retrieved {len(data)} items")
```

3. **Test with Docker**:
```bash
docker-compose up --build
curl http://localhost:8000/sources
```

### 4. Working with the API

The FastAPI app auto-generates docs at `/docs`. Key endpoints:

- `GET /sources` - List available sources
- `POST /ingest/{source}` - Trigger ingestion
- `POST /search` - Search knowledge base
- `GET /health` - Check system status

### 5. Understanding Data Flow

```
1. User calls /ingest/outline
2. API fetches data from Outline
3. Documents sent to processor
4. Processor extracts information using prompts
5. Results stored in Qdrant vector DB
6. User can /search across all knowledge
```

## Best Practices for AI Agents

1. **Always test connections first** - Sources may be misconfigured
2. **Use type hints** - Makes code self-documenting
3. **Add docstrings** - Explain what methods do
4. **Handle errors gracefully** - External APIs fail
5. **Log important events** - Use structlog
6. **Keep prompts focused** - One task per prompt
7. **Preserve metadata** - Don't lose document IDs, timestamps

## Common Patterns

### Async Everything
```python
async def process_document(doc):
    # All I/O operations should be async
    result = await summarizer.process(doc)
    await vector_store.add_documents([result])
```

### Configuration from Environment
```python
api_key = os.getenv("SOURCE_API_KEY")
if not api_key:
    raise ValueError("SOURCE_API_KEY required")
```

### Structured Logging
```python
import structlog
logger = structlog.get_logger()

logger.info("Processing documents", 
    source=source_name, 
    count=len(documents))
```

## Debugging Tips

1. **Check logs**: `docker-compose logs -f api`
2. **Verify environment**: Ensure `.env` is configured
3. **Test source directly**: Run connector standalone
4. **Check vector DB**: Use Qdrant UI at http://localhost:6333/dashboard
5. **API debugging**: Use FastAPI's `/docs` interface

## Extension Points

- **New sources**: Add to `sources/` directory
- **New processors**: Add to `processors/` directory  
- **Custom storage**: Extend `storage/vectors.py`
- **API endpoints**: Add to `app/main.py`
- **Background tasks**: Use FastAPI's BackgroundTasks

## Need Help?

1. Read the source code - it's designed to be clear
2. Check existing implementations (Outline is the reference)
3. Use the `/docs` endpoint for API exploration
4. Look at type hints and docstrings

Remember: This codebase prioritizes clarity over cleverness. Make it obvious what your code does!