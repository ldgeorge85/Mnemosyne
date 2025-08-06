# Persistent Memory System

## Overview

The Persistent Memory System enables the Philosophical Multi-Agent Debate System to maintain context and continuity across debate sessions. This system allows philosophical agents to remember past debates, maintain consistent positions, and build on previous insights over time.

## Key Features

1. **Debate History Persistence**
   - Complete debates are stored in a structured JSON format
   - Debates are indexed by topics for efficient retrieval
   - Historical debates can be retrieved based on relevance to current prompts

2. **Agent-Specific Memory**
   - Each agent maintains a personal memory of past positions and arguments
   - Enables philosophical consistency across multiple debates
   - Allows for position evolution while maintaining core principles

3. **Topic Indexing & Cross-Referencing**
   - Automatically extracts key topics from debate prompts
   - Creates indexes that link related debates across sessions
   - Enables finding past debates on similar philosophical questions

4. **Context-Aware Prompting**
   - Enhances debate prompts with relevant historical context
   - Provides agents with reminders of their past positions
   - Creates more coherent and consistent philosophical arguments

## System Architecture

The memory system consists of these key components:

### MemoryManager Class

Core class that handles all memory operations:

```python
class MemoryManager:
    def __init__(self, memory_dir=None):
        # Initialize memory storage directories and cache
        
    def save_debate(self, debate_data):
        # Persist a complete debate record and update indexes
        
    def get_agent_memory(self, agent_name):
        # Retrieve an agent's complete memory
        
    def get_relevant_debates(self, prompt, limit=5):
        # Find debates relevant to current prompt
        
    def get_agent_position(self, agent_name, topic):
        # Get agent's past position on a specific topic
```

### Memory Directory Structure

```
memory/
├── agents/                 # Agent-specific memories (JSON)
│   ├── StoicAgent.json
│   ├── UtilitarianAgent.json
│   └── ...
├── debates/               # Complete debate records (JSON)
│   ├── debate_20250608_120134.json
│   └── ...
└── indexes/               # Memory indexing system
    ├── debate_index.json  # All debates with metadata
    └── topic_index.json   # Topics linked to debate IDs
```

### Integration with Orchestrator

The enhanced `OrchestratorWithMemory` class:
- Initializes and manages the MemoryManager
- Enhances debate prompts with memory context
- Maintains debate history and agent memories
- Provides memory-aware debate functionality

## Using the Memory System

### Running a Debate with Memory

```bash
# Run the debate system with memory integration
python src/main_with_memory.py "What is the nature of free will?"

# Parallel processing still works with memory integration
PARALLEL_AGENTS=4 python src/main_with_memory.py "Is consciousness an emergent property?"
```

### Memory-Enhanced Features

1. **Contextualized Prompts**: When an agent is asked about a topic it has previously discussed, relevant context is automatically provided.

2. **Philosophical Consistency**: Agents maintain consistent philosophical positions across multiple debates.

3. **Evolution of Thought**: Long-term usage allows agents to evolve their philosophical positions while maintaining core principles.

4. **Related Debates**: Each new debate is informed by relevant past discussions.

## Technical Implementation Details

### Data Persistence Strategy

All memory data is stored in JSON files for:
- Human readability
- Easy debugging and inspection
- Simple import/export operations
- No database dependencies

### Memory Cache System

The memory system uses a three-tier caching strategy:
- In-memory cache for current session performance
- File-based persistent storage for long-term memory
- Indexing system for efficient access patterns

### Debate History Format

Each debate is stored with:
- Unique debate ID
- Timestamp
- Original prompt
- Extracted topics
- Agent responses
- Inter-agent critiques
- Debate summary
- Cross-references to related debates
