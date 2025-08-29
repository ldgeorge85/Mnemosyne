# Tool Parallel Execution Configuration

## Overview

Each tool in Mnemosyne can specify its maximum parallel execution limit, controlling how many concurrent operations it can perform. This is especially important for multi-agent tools like Shadow Council and Forum of Echoes that need to query multiple LLM agents.

## Configuration Levels

### 1. Global Default
Set in environment variable or `.env` file:
```bash
TOOL_MAX_PARALLEL_DEFAULT=2  # Default for all tools
```

### 2. Tool-Specific Settings
Override for specific tools:
```bash
SHADOW_COUNCIL_MAX_PARALLEL=2     # Shadow Council (5 members total)
FORUM_OF_ECHOES_MAX_PARALLEL=2    # Forum of Echoes (10+ voices)
```

### 3. Per-Tool Metadata
Each tool defines its own limit in metadata:
```python
class ToolMetadata:
    max_parallel: int = 1  # 1 = sequential, >1 = parallel batches
```

## How It Works

### Shadow Council Example
With `SHADOW_COUNCIL_MAX_PARALLEL=2` and 5 council members:
```
Batch 1 (parallel): Artificer, Archivist
  ↓ (0.5s delay)
Batch 2 (parallel): Mystagogue, Tactician
  ↓ (0.5s delay)
Batch 3 (parallel): Daemon
```

### Forum of Echoes Example  
With `FORUM_OF_ECHOES_MAX_PARALLEL=2` and 10 voices selected:
```
Batch 1 (parallel): Stoic, Pragmatist
  ↓ (0.5s delay)
Batch 2 (parallel): Buddhist, Existentialist
  ↓ (0.5s delay)
Batch 3 (parallel): Confucian, Taoist
  ↓ (0.5s delay)
Batch 4 (parallel): Skeptic, Idealist
  ↓ (0.5s delay)
Batch 5 (parallel): Absurdist, Materialist
```

## Benefits

1. **Rate Limiting**: Prevents overwhelming the LLM API
2. **Resource Management**: Controls memory and CPU usage
3. **Cost Control**: Limits concurrent API calls
4. **Stability**: Avoids timeout issues with too many parallel requests
5. **Flexibility**: Different limits for different tools based on their needs

## Implementation

### In Tool Class
```python
class ShadowCouncilTool(BaseTool):
    def __init__(self):
        super().__init__()
        from ....core.config import settings
        self._max_parallel_override = settings.SHADOW_COUNCIL_MAX_PARALLEL
    
    def _get_default_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="shadow_council",
            max_parallel=self._max_parallel_override
        )
```

### In Execution Method
```python
async def _consult_members(self, members: List[str], input: ToolInput):
    max_parallel = self.metadata.max_parallel
    
    for i in range(0, len(members), max_parallel):
        batch = members[i:i + max_parallel]
        
        # Execute batch in parallel
        tasks = [self._consult_member(m, input) for m in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Small delay between batches
        if i + max_parallel < len(members):
            await asyncio.sleep(0.5)
```

## Tuning Guidelines

### For Multi-Agent Tools
- **Shadow Council**: 2 parallel (5 total agents = 3 batches)
- **Forum of Echoes**: 2 parallel (10+ voices = 5+ batches)
- Consider your LLM provider's rate limits
- Default of 2 provides good balance of speed vs. stability

### For Simple Tools
- Usually 1 (sequential) is fine
- Increase only if tool makes multiple independent operations

### For External API Tools
- Check API rate limits
- Consider cost per call
- Start conservative, increase gradually

## Monitoring

Watch logs for parallel execution:
```
INFO: Consulting batch of 3 council members in parallel (max 3)
INFO: Consulting batch of 2 council members in parallel (max 3)
```

## Environment Variables

Add to your `.env` file:
```bash
# Tool Parallel Execution Limits
TOOL_MAX_PARALLEL_DEFAULT=2
SHADOW_COUNCIL_MAX_PARALLEL=2
FORUM_OF_ECHOES_MAX_PARALLEL=2

# Can add more as needed
# CUSTOM_TOOL_MAX_PARALLEL=2
```

## Future Enhancements

1. **Dynamic Adjustment**: Adjust based on response times
2. **Priority Queues**: High-priority queries get more parallel slots
3. **Cost-Based Limits**: Different limits based on user tier
4. **Provider-Specific**: Different limits for different LLM providers
5. **Adaptive Batching**: Automatically optimize batch sizes based on performance