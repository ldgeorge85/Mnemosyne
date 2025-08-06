# Shadow AI Agent System

A modular AI agent system with a central orchestrator that manages specialized cognitive agents.

## Overview

Shadow is a multi-agent AI system consisting of:

1. **Shadow Orchestrator**: Central coordinator that routes requests to specialized agents, decomposes tasks, and aggregates responses.
2. **Specialized Agents**:
   - **Engineer**: Technical problem-solving, design, and mechanical/electrical/chemical reasoning
   - **Librarian**: Information retrieval, semantic search, and structured data management
   - **Priest**: Ethical and philosophical reasoning using multiple worldviews
3. **Memory Layer**: Persistent storage for agent knowledge and conversations
4. **Interface Layer**: REST API and web interface

## Architecture

```
User Request → Shadow Orchestrator → Specialized Agent(s) → Aggregated Response
```

### Key Components

#### Shadow Orchestrator
- **Input Classification**: Routes requests to appropriate specialized agents
- **Task Decomposition**: Breaks down complex queries into sub-tasks
- **Response Aggregation**: Combines multiple agent responses into coherent answers
- **Context Management**: Maintains conversation history for continuity

#### Specialized Agents
Each agent implements a common interface but specializes in different domains:

- **Engineer Agent**: Handles technical questions, design problems, and system architecture
- **Librarian Agent**: Specializes in information retrieval, organization, and presentation
- **Priest Agent**: Addresses ethical and philosophical questions with multi-perspective reasoning

#### Memory System
- Vector database for semantic search and similarity matching
- Relational database for structured data and entity relationships
- Document store for knowledge documents and conversation histories
- Memory integration with all specialized agents to provide context-aware responses

#### API System
- FastAPI-based REST interface
- Session management
- Health monitoring

## Technical Stack

- **Language**: Python 3.9+
- **API Framework**: FastAPI
- **Models**: Compatible with OpenAI, Anthropic Claude, and local models
- **Configuration**: YAML-based settings

## Project Structure

```
/shadow_system
  /orchestrator       - Core orchestration components
  /agents             - Specialized cognitive agents
  /memory             - Knowledge persistence and context management
  /api                - REST API endpoints
  /utils              - System utilities
  /docs               - Documentation and source of truth
```

## Getting Started

### Requirements

Dependencies are specified in `requirements.txt`. Main requirements:

```
fastapi==0.110.0
uvicorn==0.29.0
pydantic==2.6.3
pyyaml==6.0.1
```

### Installation

```bash
# Clone the repository
git clone <repository-url>

# Navigate to project directory
cd shadow_system

# Install dependencies
pip install -r requirements.txt

# Set up API keys for LLM providers (optional)
export OPENAI_API_KEY=your_openai_api_key
```

### Running the System

Start the API server:

```bash
# Run with uvicorn
python3 -m api.fastapi_server

# Or directly with uvicorn
uvicorn api.fastapi_server:app --reload
```

### Testing

Run the test suite to verify the system operation:

```bash
python3 test_shadow_system.py
```

This will run:
1. Classification tests
2. Individual agent response tests
3. End-to-end orchestration tests

To test memory integration specifically:

```bash
python3 test_memory_integration.py
```

This will validate:
1. Memory system initialization with test data
2. Memory context integration with the orchestrator
3. Specialized agents' ability to utilize memory context

## Usage Examples

### API Request

```bash
curl -X POST "http://localhost:8000/api/shadow" \
  -H "Content-Type: application/json" \
  -d '{"query":"Design a system to optimize energy consumption in a smart home"}'
```

## Development Roadmap

- [x] Core orchestrator implementation
- [x] Mock agents with classification logic
- [x] Basic API endpoint
- [x] LLM integration for agent intelligence
- [x] Memory system implementation
- [x] Memory context integration with specialized agents
- [ ] Web UI for interactive usage
- [ ] Multi-agent collaboration enhancements
- [ ] Advanced memory retrieval and knowledge extraction
- [ ] Security enhancements and API key management

## Documentation

For detailed documentation:
- System architecture: `/docs/source_of_truth.md`
- Configuration options: `/utils/config.yaml`
- API endpoints: FastAPI automatic docs at `http://localhost:8000/docs`

## License

[Specify license here]
