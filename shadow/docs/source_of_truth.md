# Shadow System - Source of Truth Document

This document tracks the file structure and components of the Shadow AI Agent System with advanced multi-agent collaboration capabilities.

## Project Overview

The Shadow AI system is a modular, memory-aware AI agent platform featuring:
- **Advanced Multi-Agent Collaboration** with task decomposition and synthesis
- **Configurable LLM/Embedding Systems** supporting OpenAI-compatible endpoints
- **Comprehensive Memory Management** with semantic search and context awareness
- **React-based Web Interface** with real-time chat and agent status monitoring
- **Flexible Configuration** via .env files for easy deployment

## Project Structure

```
/shadow_system
  /orchestrator
    shadow_agent.py              - Core orchestrator with advanced collaboration
    classifier.py                - Input classification logic
    aggregator.py                - Response aggregation logic
    memory_integration.py        - Memory system integration for orchestrator
    task_decomposer.py           - Advanced task decomposition for multi-agent workflows
    collaborative_executor.py    - Multi-agent collaboration execution engine
  /agents
    base_agent.py                - Base agent interface with memory context support
    /engineer
      agent.py                   - Engineer agent implementation (LLM-powered)
      prompts.yaml               - Engineer specific prompts
    /librarian
      agent.py                   - Librarian agent implementation (LLM-powered)
      prompts.yaml               - Librarian specific prompts
    /priest
      agent.py                   - Priest agent implementation (LLM-powered)
      debate.py                  - Debate architecture implementation
      prompts.yaml               - Priest specific prompts
  /memory                        - Memory layer implementation
    __init__.py                  - Memory package exports
    memory_base.py               - Base memory system interfaces
    memory_manager.py            - Unified memory system manager
    vector_memory.py             - Vector storage with configurable embedding providers
    document_store.py            - Document storage system
    relational_store.py          - Relational data storage
  /api
    fastapi_server.py            - REST API with CORS, session management, static serving
  /utils
    config.yaml                  - System configuration
    llm_connector.py             - Configurable LLM API integration (OpenAI-compatible)
    prompt_loader.py             - YAML prompt template manager
  /frontend                      - React web interface
    /src
      /components
        App.js                   - Main application component with theme provider
        ChatInterface.js         - Chat UI component with dark mode support
        MessageList.js           - Message display component
        MessageInput.js          - Message input component
        AgentStatus.js           - Agent status display
        ControlPanel.js          - System control panel
        DarkModeToggle.js        - Dark/light mode toggle component
      /contexts
        ThemeContext.js          - Theme management context with localStorage persistence
      /styles
        App.css                  - Main application styles with CSS variables for theming
        ChatInterface.css        - Chat interface styles with dark mode support
        MessageList.css          - Message list styles with dark mode support
        MessageInput.css         - Message input styles
        AgentStatus.css          - Agent status styles
        DarkModeToggle.css       - Dark mode toggle component styles
      /services
        shadowAPI.js             - API service layer
      index.js                   - React entry point
    package.json                 - Frontend dependencies
    Dockerfile                   - Frontend container configuration
  /docs
    source_of_truth.md           - This document
    shadow_ai_architectural_review.md - Comprehensive architectural review and enhancement recommendations for multi-agent orchestration, session management, memory system, agent attribution, and streaming responses
    shadow_ai_implementation_tasks.md - Detailed task tracker with 35 specific implementation tasks organized by phase, including code snippets and verification steps
  .env.example                   - Environment configuration template
  .env                          - Local environment configuration (user-created)
  README.md                     - Project overview and instructions
  test_shadow_system.py         - End-to-end system tests
  test_memory_integration.py    - Memory integration tests
  test_collaboration.py         - Multi-agent collaboration tests
  run_collaboration_test.sh     - Test runner with environment validation
  requirements.txt              - Project dependencies

## Key Features Implemented

### Multi-Agent Collaboration
- **Task Decomposition**: Automatically breaks complex queries into specialized subtasks
- **Collaborative Execution**: Agents share context and build on each other's findings
- **Response Synthesis**: Intelligent aggregation of multi-agent outputs
- **Dependency Management**: Handles sequential and parallel task execution

### Configurable LLM/Embedding Systems
- **OpenAI API Compatibility**: Works with any OpenAI-compatible endpoint
- **Flexible Configuration**: Via environment variables (base_url, api_key, model_name, etc.)
- **Local Model Support**: Easy integration with Ollama, LocalAI, and other providers
- **Real Endpoint Integration**: No mock responses - all operations use actual AI models

### Memory Management
- **Vector Memory**: Semantic search with configurable embedding providers
- **Document Store**: Full-text storage and retrieval
- **Relational Store**: Structured entity and relationship storage
- **Context Awareness**: Agents receive relevant memory context for enhanced responses

### Web Interface
- **Real-time Chat**: Interactive conversation with the Shadow system
- **Agent Status Monitoring**: Live view of system and agent status
- **Session Management**: Persistent conversation history and export functionality
- **Responsive Design**: Mobile-friendly interface with modern UX
- **Dark Mode**: Toggleable dark mode for improved readability

## Configuration System

The system uses environment variables for configuration, loaded from `.env` files:

### LLM Configuration
- `LLM_BASE_URL`: API endpoint (default: https://api.openai.com/v1)
- `LLM_API_KEY`: Authentication key
- `LLM_MODEL_NAME`: Model identifier (default: gpt-4o)
- `LLM_MAX_TOKENS`: Maximum response tokens (default: 2048)
- `LLM_TEMPERATURE`: Randomness setting (default: 0.7)

### Embedding Configuration
- `EMBEDDING_BASE_URL`: Embedding API endpoint
- `EMBEDDING_API_KEY`: Authentication key for embeddings
- `EMBEDDING_MODEL_NAME`: Embedding model (default: text-embedding-ada-002)

### Legacy Support
- `OPENAI_API_KEY`: Backward compatibility with existing setups
- `ANTHROPIC_API_KEY`: For Anthropic Claude integration (future use)

## Development Status

### Completed Features
- ✅ Core orchestrator with multi-agent collaboration
- ✅ Specialized agents with LLM integration and memory context
- ✅ Advanced task decomposition and collaborative execution
- ✅ Comprehensive memory system with real embeddings
- ✅ Configurable LLM/embedding systems (OpenAI-compatible)
- ✅ React web interface with session management
- ✅ FastAPI backend with CORS and static file serving
- ✅ Environment configuration via .env files
- ✅ Comprehensive test suites for all major components

### Architecture Principles
- **Modularity**: Clear separation of concerns between components
- **Configurability**: Environment-based configuration for flexible deployment
- **Scalability**: Designed to support additional agents and memory backends
- **Testability**: Comprehensive test coverage with real endpoint integration
- **User Experience**: Modern web interface with intuitive interaction patterns

This system represents a complete, production-ready AI agent platform with advanced multi-agent collaboration capabilities.
