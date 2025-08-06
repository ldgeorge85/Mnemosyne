# Dynamic Agent Loading System

## Overview

The Dynamic Agent Loading System enhances the Philosophical Multi-Agent Debate System by allowing agents to be loaded from individual definition files, rather than being hardcoded in the source code. This approach offers several benefits:

1. **Modularity**: Each agent definition lives in its own file, making it easy to add, remove, or modify agents
2. **Scalability**: The system can now effortlessly incorporate all 56 philosophical perspectives defined in the system message files
3. **Parallel Processing**: Optional parallel API calls for faster debate processing

## How It Works

The system automatically scans a directory (`agent_definitions/`) for agent definition files (either Markdown or JSON), loads them, and creates agent instances at runtime.

### Agent Definition Files

Each agent is defined in a separate file with this format:

**Markdown Format** (converted from existing system messages):
```markdown
## Agent Name
```python
You are a [Philosophy Type] philosopher.
[Full system prompt with constraints, debate style, etc.]
```
```

**JSON Format** (alternative option):
```json
{
  "name": "StoicAgent",
  "archetype": "Stoicism",
  "system_prompts": {
    "analysis": "You are a Stoic philosopher...[full detailed prompt]",
    "critique": "You are a Stoic philosopher. Critique the following..."
  }
}
```

### Key Components

1. **DynamicAgent Class**: A flexible agent implementation that uses provided system prompts
2. **Agent Loader**: Scans directories for agent definitions and instantiates agents
3. **Dynamic Orchestrator**: Manages the debate flow with support for parallel processing
4. **Conversion Utility**: Converts existing system message files to individual agent definitions

## Using the Dynamic Agent System

1. Run the conversion utility to create individual agent files:
   ```bash
   python src/utils/convert_agent_definitions.py
   ```

2. Use the dynamic version of the system:
   ```bash
   python src/main_dynamic.py "Your philosophical prompt"
   ```

3. Enable parallel processing for faster debates:
   ```bash
   PARALLEL_AGENTS=4 python src/main_dynamic.py "Your philosophical prompt"
   ```

## Advantages

- **Easy Expansion**: Add new agents by simply creating new definition files
- **Configuration Flexibility**: Modify agents without changing code
- **Performance Optimizations**: Optional parallel processing for API calls
- **Complete Integration**: All 56 philosophical perspectives can now be used in debates
