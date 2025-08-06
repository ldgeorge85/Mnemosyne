# Philosophical Multi-Agent Debate System: Project Structure

This document serves as the source of truth for the project structure of the Philosophical Multi-Agent Debate System. It provides a comprehensive inventory of all files and their purposes.

> **Important Implementation Note:** While the system currently has 10 philosophical agents implemented in code, there are 56 different philosophical perspectives defined in the system message files. The architecture is designed to accommodate expansion to include these additional perspectives.

## Directory Structure

```
dialogues/
├── memory/                     # Persistent memory storage
│   ├── agents/                 # Agent-specific memories
│   ├── debates/                # Complete debate records
│   └── indexes/                # Memory indexing system
├── agents/                     # Agent system message definitions
│   ├── philosophical_agents_system_messages_part1.md  # System prompts for agents (part 1)
│   ├── philosophical_agents_system_messages_part2.md  # System prompts for agents (part 2)
│   ├── philosophical_agents_system_messages_part3.md  # System prompts for agents (part 3)
│   ├── philosophical_agents_system_messages_part4.md  # System prompts for agents (part 4)
│   ├── philosophical_agents_system_messages_part5.md  # System prompts for agents (part 5)
│   └── philosophical_agents_system_messages_part6.md  # System prompts for agents (part 6)
├── src/                        # Source code directory
│   ├── agents/                 # Agent implementations
│   │   ├── __init__.py         # Package initialization
│   │   ├── base.py             # Base agent class definition
│   │   ├── philosophical_agents.py  # Philosophical agent implementations (10 of 56 possible)
│   │   ├── orchestrator.py     # Orchestrator agent for coordination (original)
│   │   ├── orchestrator_dynamic.py  # Dynamic orchestrator agent with parallel processing support
│   │   ├── orchestrator_with_memory.py  # Memory-enhanced orchestrator with debate history
│   │   ├── dynamic_agent.py    # Dynamic agent class for file-defined agents
│   │   ├── agent_loader.py     # Utilities to load agents from definition files
│   │   └── synthesis.py        # Synthesis agent for summarizing debates
│   ├── memory/                 # Memory system for debate history
│   │   ├── __init__.py         # Package initialization
│   │   └── memory_manager.py   # Memory manager for storing and retrieving memories
│   ├── config/                 # Configuration settings
│   │   ├── __init__.py         # Package initialization
│   │   └── settings.py         # Configuration and settings management
│   ├── debate/                 # Debate management
│   │   ├── __init__.py         # Package initialization
│   │   ├── analyzer.py         # Debate analysis functionality
│   │   └── manager.py          # Debate process management
│   ├── utils/                  # Utility scripts
│   │   └── convert_agent_definitions.py  # Convert system messages to agent definition files
│   ├── __init__.py             # Root package initialization
│   ├── main.py                 # Main entry point (original)
│   ├── main_dynamic.py         # Main entry point with dynamic agent loading for application
│   ├── main_with_memory.py     # Main entry point with memory integration for application
│   └── ui/                     # User interface components
│       └── __init__.py         # UI package initialization
├── logs/                       # Log files directory
│   └── test1_log.txt           # Test run log
├── docs/                       # Documentation directory
│   ├── agent_architecture.md   # Documentation of agent architecture
│   └── project_structure.md    # This file - source of truth for project structure
├── .env.example                # Example environment variables
├── setup.py                    # Python package setup
├── requirements.txt            # Project dependencies
├── Dockerfile                  # Docker configuration
└── debate_history.jsonl        # History of past debates (may be in project root)
```

## File Descriptions

### Configuration Files
- **setup.py**: Package installation configuration
- **requirements.txt**: Project dependencies without version pinning (latest versions)
- **Dockerfile**: Container configuration with PYTHONPATH=/app
- **.env.example**: Example environment configuration

### Source Code

#### Main Components
- **src/main.py**: Entry point that initializes the OrchestratorAgent and processes user input

#### Agent System
- **src/agents/base.py**: Base agent class that all philosophical agents inherit from
- **src/agents/philosophical_agents.py**: Implementation of all philosophical agents (Stoic, Utilitarian, etc.)
- **src/agents/orchestrator.py**: Manages the debate flow between agents
- **src/agents/synthesis.py**: Creates a summary of all agent responses

#### Configuration
- **src/config/settings.py**: Loads and manages application settings including OpenAI API configuration

#### Debate Management
- **src/debate/analyzer.py**: Logic for analyzing debate content
- **src/debate/manager.py**: Management of debate processes

### Documentation
- **docs/agent_architecture.md**: Detailed explanation of the agent architecture and flow
- **docs/project_structure.md**: This file - source of truth for project structure

### Logs & History
- **logs/test1_log.txt**: Log file containing debate output and any errors
- **debate_history.jsonl**: JSON Lines file storing the history of debates (prompt, responses, summary)

## Important Technical Notes

1. **OpenAI API Integration**: Uses the new OpenAI client format (v1.0+)
2. **Docker Configuration**: Sets PYTHONPATH=/app to ensure proper module imports
3. **Package Structure**: Installed in editable mode with `pip install -e .`
4. **Environment Variables**: Configuration loaded from .env file (see .env.example)

## Updates History

| Date       | Change                                            |
|------------|--------------------------------------------------|
| 2025-06-08 | Initial documentation created                     |
| 2025-06-08 | Fixed OpenAI API integration to use v1.0+ format  |
| 2025-06-08 | Fixed Docker PYTHONPATH configuration             |
