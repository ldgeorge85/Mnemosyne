# Shadow AI Control Panel Documentation

## Overview

The Shadow AI Control Panel provides a comprehensive user interface and API for managing agents, memory, routing, and system configuration. This addresses the need for long-term, built-in solutions rather than manual workarounds.

## Features

### 1. Agent Control
**Purpose**: Force specific agents to handle queries, bypassing automatic routing.

**UI Access**: 
- Click "Show Control Panel" in the header
- Navigate to "Agent Control" tab
- Enter query and select desired agents
- Choose force mode (single agent, all agents, or normal pool)

**API Access**:
```bash
curl -X POST http://localhost:8001/api/control/agent/override \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Design a database schema",
    "agents": ["engineer"],
    "force_single": true
  }'
```

### 2. Memory Management
**Purpose**: Query and manage conversation history, documents, and memory stores.

#### Query Memory
**UI Access**:
- Navigate to "Memory Management" tab
- Select query type (history, documents, search, entities)
- Click "Query Memory"

**API Access**:
```bash
# Query conversation history
curl http://localhost:8001/api/control/memory/query?query_type=history&limit=10

# Semantic search
curl http://localhost:8001/api/control/memory/query?query_type=search&search_term=database&limit=5
```

#### Clear Memory
**UI Access**:
- Use "Clear History", "Clear Documents", or "Clear All Memory" buttons
- Confirms before clearing

**API Access**:
```bash
# Clear all memory
curl -X POST http://localhost:8001/api/control/memory/manage \
  -H "Content-Type: application/json" \
  -d '{"operation": "clear", "filters": {"all": true}}'
```

#### Filter Memory (Remove Test Messages)
**UI Access**:
- Enter comma-separated patterns to filter
- Click "Filter Out Patterns"

**API Access**:
```bash
# Remove test messages and errors
curl -X POST http://localhost:8001/api/control/memory/manage \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "filter",
    "filters": {
      "patterns": ["test message", "error generating response", "testing 123"]
    }
  }'
```

### 3. Agent Configuration
**Purpose**: Dynamically update agent prompts, keywords, and parameters.

**UI Access**:
- Navigate to "Configuration" tab
- Select agent and configuration type
- Enter JSON configuration
- Click "Update Configuration"

**API Examples**:
```bash
# Update agent prompt
curl -X POST http://localhost:8001/api/control/agent/config \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "engineer",
    "config_type": "prompt",
    "config_data": {
      "system_prompt": "You are an expert software engineer specializing in scalable architectures..."
    },
    "persist": true
  }'

# Update routing keywords
curl -X POST http://localhost:8001/api/control/agent/config \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "writer",
    "config_type": "keywords",
    "config_data": {
      "add": ["documentation", "readme"],
      "remove": ["story"]
    }
  }'
```

### 4. Routing Configuration
**Purpose**: Control multi-agent collaboration and routing strategies.

**UI Access**:
- Toggle "Enable Agent Collaboration" checkbox
- Select routing strategy (keyword, semantic, manual)
- Click "Update Routing Configuration"

**API Access**:
```bash
# Enable collaboration
curl -X POST http://localhost:8001/api/control/routing/config \
  -H "Content-Type: application/json" \
  -d '{
    "enable_collaboration": true,
    "enable_multi_agent": true,
    "routing_strategy": "keyword"
  }'
```

### 5. System Status
**Purpose**: Monitor agent usage, memory status, and system performance.

**UI Access**:
- Navigate to "System Status" tab
- View agent statistics, memory info, routing config
- Click "Refresh Status" to update

**API Access**:
```bash
curl http://localhost:8001/api/control/status
```

## Common Use Cases

### 1. Force Specific Agent for Writing
```bash
# Force writer agent for documentation
curl -X POST http://localhost:8001/api/control/agent/override \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Write comprehensive API documentation",
    "agents": ["writer"],
    "force_single": true
  }'
```

### 2. Clean Up Test Messages
```bash
# Remove all test/error messages from history
curl -X POST http://localhost:8001/api/control/memory/manage \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "filter",
    "filters": {
      "patterns": ["test", "error", "testing", "hello world"]
    }
  }'
```

### 3. Force Multi-Agent Collaboration
```bash
# Enable collaboration and force multiple agents
curl -X POST http://localhost:8001/api/control/routing/config \
  -H "Content-Type: application/json" \
  -d '{
    "enable_collaboration": true,
    "enable_multi_agent": true
  }'

# Then query with multiple agents
curl -X POST http://localhost:8001/api/control/agent/override \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Design and document a microservices architecture",
    "agents": ["engineer", "architect", "writer"],
    "force_all": true
  }'
```

### 4. View Agent Definitions
```bash
# Get current agent configuration via status
curl http://localhost:8001/api/control/status

# Or directly check prompt files
docker exec shadow-ai-system cat /app/agents/engineer/prompts.yaml
```

### 5. Export/Import Memory
```bash
# Export current memory state
curl -X POST http://localhost:8001/api/control/memory/manage \
  -H "Content-Type: application/json" \
  -d '{"operation": "export"}' > memory_backup.json

# Import memory state
curl -X POST http://localhost:8001/api/control/memory/manage \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "import",
    "data": <contents of memory_backup.json>
  }'
```

## Integration with Frontend

The control panel is seamlessly integrated into the React frontend:

1. **Access**: Click "Show Control Panel" button in the header
2. **Tabs**: Navigate between Agent Control, Memory Management, Configuration, and System Status
3. **Real-time Updates**: Changes take effect immediately
4. **Feedback**: Success/error messages displayed for all operations
5. **Responsive Design**: Works on desktop and mobile devices

## Best Practices

1. **Agent Selection**: Use force_single when you need a specific agent's expertise
2. **Memory Filtering**: Regularly clean test messages to maintain context quality
3. **Configuration Persistence**: Set persist=true to save changes across restarts
4. **Collaboration**: Enable only when needed for complex multi-domain tasks
5. **Monitoring**: Check system status regularly to understand agent usage patterns

## Troubleshooting

### Control Panel Not Loading
- Ensure Docker container is running: `docker ps`
- Check API health: `curl http://localhost:8001/api/health`
- Verify control endpoints: `curl http://localhost:8001/api/control/help`

### Agent Override Not Working
- Verify agent names match exactly (case-sensitive)
- Check system status to ensure agents are active
- Review logs: `docker logs shadow-ai-system`

### Memory Operations Failing
- Ensure memory manager is initialized (check system status)
- Verify JSON format for configuration data
- Check memory limits aren't exceeded

## API Reference

Full API documentation available at:
```bash
curl http://localhost:8001/api/control/help
```

This includes all endpoints, parameters, and example requests for programmatic access.
