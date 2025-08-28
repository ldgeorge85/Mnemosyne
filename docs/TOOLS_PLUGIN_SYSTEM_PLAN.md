# Tools & Plugin System Architecture Plan
*Last Updated: August 27, 2025*
*Status: CORE INFRASTRUCTURE COMPLETE!*

## Current Implementation Status

### ✅ Completed (August 27, 2025)
- **BaseTool Interface** - Abstract class with metadata, input/output, lifecycle hooks
- **ToolRegistry** - Discovery, registration, execution, lifecycle management
- **Tool Executors** - USE_TOOL, SELECT_TOOLS, COMPOSE_TOOLS actions in agentic flow
- **Simple Tools** - 5 working tools (calculator, datetime, json_formatter, text_formatter, word_counter)
- **Auto-registration** - Tools discovered and registered on app startup
- **Deadlock Fix** - Internal registration method prevents lock conflicts

### 🔴 Next Steps
- UI tool palette component for manual selection
- Port Shadow Council as unified tool with sub-agents (Artificer, Archivist, Mystagogue, Tactician, Daemon)
- Port Forum of Echoes as unified tool with philosophical perspectives (50+ voices)
- Protocol integrations (MCP, OpenAPI, A2A)

## Vision

Create a unified tool/plugin system for Mnemosyne that treats ALL capabilities as tools - whether they're sub-agents, external APIs, or composite orchestrations. This provides a consistent interface for extending functionality while maintaining clean architecture.

## Core Concept

Everything is a tool. Tools can be:
- **Simple**: Direct function calls (calculate, format, etc.)
- **Agent**: LLM-powered sub-agents (Engineer, Philosopher, etc.)  
- **External**: API integrations (SerpAPI, Wolfram, etc.)
- **Composite**: Tools that orchestrate other tools (Concept Checker, Debate)
- **Pipeline**: Tools that chain other tools in sequence

## Architecture

```
User Input
    ↓
Chat Interface
    ├── Tool Palette (manual selection)
    ├── Tool Status Display
    └── Tool Output Rendering
    ↓
Agentic Flow Controller
    ├── Core Actions (existing)
    └── USE_TOOL Action (new)
    ↓
Tool Registry System (new)
    ├── Tool Discovery
    ├── Tool Validation  
    ├── Tool Execution
    └── Tool State Management
    ↓
Tool Plugins
    ├── Simple Tools
    │   ├── Calculator
    │   ├── DateTime
    │   └── Formatter
    ├── Agent Tools
    │   ├── Shadow Council
    │   │   ├── Artificer
    │   │   ├── Archivist
    │   │   ├── Mystagogue
    │   │   ├── Tactician
    │   │   └── Daemon
    │   └── Forum of Echoes
    │       ├── StoicVoice
    │       ├── PragmatistVoice
    │       └── [50+ voices]
    ├── External Tools
    │   ├── WebSearch (SerpAPI)
    │   ├── WikipediaLookup
    │   └── ArxivSearch
    └── Composite Tools
        ├── ConceptChecker
        ├── ConceptDebate
        └── MultiPerspective
```

## Tool Interface Standard

### Base Tool Contract
```python
class BaseTool(ABC):
    """Standard interface all tools must implement"""
    
    # Metadata
    name: str                    # Unique identifier
    display_name: str            # Human-readable name
    description: str             # What it does
    category: ToolCategory       # simple|agent|external|composite
    capabilities: List[str]      # What it can help with
    
    # Configuration
    requires_auth: bool          # Needs API keys?
    cost_estimate: float         # Computational/API cost
    timeout: int                 # Max execution time
    
    # Execution
    async def can_handle(self, query: str, context: Dict) -> float:
        """Returns confidence (0-1) that this tool is relevant"""
        
    async def execute(self, input: ToolInput, context: Dict) -> ToolOutput:
        """Execute the tool with given input"""
        
    async def validate_input(self, input: Any) -> bool:
        """Validate input before execution"""
    
    # UI Integration
    def get_ui_schema(self) -> Dict:
        """Returns JSON schema for UI form generation"""
        
    def format_output(self, output: ToolOutput) -> str:
        """Format output for display in chat"""
```

### Tool Input/Output Standards
```python
@dataclass
class ToolInput:
    query: str                   # Primary input
    parameters: Dict            # Tool-specific params
    context: Dict               # Conversation context
    options: ToolOptions        # Execution options

@dataclass
class ToolOutput:
    success: bool
    result: Any                 # Tool-specific output
    metadata: Dict              # Execution metadata
    display_format: str         # How to render (text|json|markdown|html)
    confidence: float           # Result confidence
    sources: List[str]          # Attribution/sources
    cost: float                 # Actual cost incurred
```

## Tool Categories

### 1. Simple Tools
Direct function implementations with no external dependencies.

```python
class CalculatorTool(BaseTool):
    name = "calculator"
    category = ToolCategory.SIMPLE
    
    async def execute(self, input: ToolInput, context: Dict) -> ToolOutput:
        # Direct calculation logic
        result = eval_math_safely(input.query)
        return ToolOutput(result=result, display_format="text")
```

### 2. Agent Tools
LLM-powered agents with specific personas/expertise.

```python
class PhilosophicalAgentTool(BaseTool):
    name = "stoic_philosopher"
    category = ToolCategory.AGENT
    
    def __init__(self):
        self.system_prompt = load_prompt("stoic.yaml")
        
    async def execute(self, input: ToolInput, context: Dict) -> ToolOutput:
        response = await llm_service.complete(
            system=self.system_prompt,
            query=input.query
        )
        return ToolOutput(result=response, confidence=0.85)
```

### 3. External Tools
Integrations with external services/APIs.

```python
class WebSearchTool(BaseTool):
    name = "web_search"
    category = ToolCategory.EXTERNAL
    requires_auth = True
    
    async def execute(self, input: ToolInput, context: Dict) -> ToolOutput:
        results = await serpapi.search(input.query)
        return ToolOutput(
            result=results,
            sources=[r.url for r in results],
            cost=0.002  # API cost
        )
```

### 4. Composite Tools
Tools that orchestrate multiple other tools.

```python
class ConceptCheckerTool(BaseTool):
    name = "concept_checker"
    category = ToolCategory.COMPOSITE
    
    def __init__(self):
        self.agents = ["stoic", "pragmatist", "humanist"]
        
    async def execute(self, input: ToolInput, context: Dict) -> ToolOutput:
        # Get perspectives from multiple agents
        perspectives = await asyncio.gather(*[
            tool_registry.get(agent).execute(input, context)
            for agent in self.agents
        ])
        
        # Synthesize responses
        synthesis = await self.synthesize(perspectives)
        return ToolOutput(
            result=synthesis,
            metadata={"perspectives": len(perspectives)}
        )
```

### 5. Debate Tool Example
```python
class ConceptDebateTool(BaseTool):
    name = "concept_debate"
    category = ToolCategory.COMPOSITE
    
    async def execute(self, input: ToolInput, context: Dict) -> ToolOutput:
        agents = input.parameters.get("agents", ["stoic", "pragmatist"])
        rounds = input.parameters.get("rounds", 3)
        
        debate_flow = DebateOrchestrator(agents)
        
        # Opening statements
        openings = await debate_flow.opening_statements(input.query)
        
        # Rebuttal rounds
        for _ in range(rounds):
            rebuttals = await debate_flow.rebuttal_round()
            
        # Synthesis
        synthesis = await debate_flow.synthesize()
        
        return ToolOutput(
            result=synthesis,
            metadata={"debate_log": debate_flow.get_log()}
        )
```

## Tool Registry System

### Registry Implementation
```python
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.categories: Dict[ToolCategory, List[str]] = {}
        
    def register(self, tool: BaseTool):
        """Register a tool in the system"""
        self.tools[tool.name] = tool
        self.categories[tool.category].append(tool.name)
        
    def discover(self, path: str):
        """Auto-discover tools from a directory"""
        # Load tool definitions from YAML/Python files
        
    def get_relevant_tools(self, query: str) -> List[BaseTool]:
        """Get tools relevant to a query"""
        relevance_scores = []
        for tool in self.tools.values():
            score = await tool.can_handle(query, {})
            if score > 0.3:  # Threshold
                relevance_scores.append((tool, score))
        return sorted(relevance_scores, key=lambda x: x[1], reverse=True)
```

## Integration with Agentic Flow

### New Action Type
```python
class ToolUseAction(AgenticAction):
    action = "USE_TOOL"
    
    async def execute(self, params: Dict, context: Dict) -> Dict:
        tool_name = params["tool"]
        tool_input = ToolInput(
            query=params.get("query"),
            parameters=params.get("parameters", {}),
            context=context
        )
        
        tool = tool_registry.get(tool_name)
        output = await tool.execute(tool_input, context)
        
        return {
            "tool": tool_name,
            "output": output.result,
            "confidence": output.confidence,
            "sources": output.sources
        }
```

### LLM Tool Selection
```python
async def select_tools(query: str, available_tools: List[str]) -> List[str]:
    """LLM selects which tools to use"""
    prompt = f"""
    Query: {query}
    
    Available tools:
    {format_tool_descriptions(available_tools)}
    
    Select the most relevant tools (0-3) for this query.
    """
    
    response = await llm_service.complete(prompt)
    return parse_tool_selection(response)
```

## UI Integration

### Manual Tool Selection
```
┌─────────────────────────────────────┐
│  Tool Palette                       │
├─────────────────────────────────────┤
│ 🔍 Search Tools                     │
│   ☐ Web Search  ☐ Wikipedia        │
│                                     │
│ 🤖 Agent Tools                      │
│   ☐ Technical  ☐ Research          │
│   ☐ Stoic  ☐ Pragmatist           │
│                                     │
│ 🎭 Composite Tools                  │
│   ☐ Concept Checker                │
│   ☐ Concept Debate                 │
│                                     │
│ [Configure Tools...]                │
└─────────────────────────────────────┘
```

### Tool Output Display
```
User: What would different philosophies say about AI safety?

Assistant: Using the Concept Checker tool...

▼ Concept Checker (3 perspectives analyzed)
   Stoic: AI safety requires disciplined restraint...
   Pragmatist: Focus on practical safeguards...
   Humanist: Center human dignity in all designs...

Based on these philosophical perspectives...
```

## External Protocol Support

### MCP (Model Context Protocol) Integration
Anthropic's MCP provides standardized context exchange with data sources.

#### MCP Server Adapter
```python
class MCPToolAdapter(BaseTool):
    """Adapter to expose MCP servers as Mnemosyne tools"""
    
    def __init__(self, mcp_server_config: Dict):
        self.mcp_client = MCPClient(mcp_server_config)
        self.name = f"mcp_{mcp_server_config['name']}"
        self.category = ToolCategory.EXTERNAL
        
    async def execute(self, input: ToolInput, context: Dict) -> ToolOutput:
        # Convert Mnemosyne format to MCP format
        mcp_request = self.convert_to_mcp(input)
        
        # Call MCP server
        mcp_response = await self.mcp_client.call_tool(
            tool_name=input.parameters['mcp_tool'],
            arguments=mcp_request
        )
        
        # Convert back to Mnemosyne format
        return self.convert_from_mcp(mcp_response)
```

#### Benefits of MCP Support
- Access to pre-built MCP servers (Google Drive, Slack, GitHub, etc.)
- Standardized protocol for data access
- Community ecosystem of MCP tools
- Built-in security and authentication

### OpenAPI Tools Integration
Support for any REST API with OpenAPI specification.

#### OpenAPI Tool Generator
```python
class OpenAPIToolGenerator:
    """Generate tools from OpenAPI specifications"""
    
    def generate_tools(self, openapi_spec: Dict) -> List[BaseTool]:
        tools = []
        for path, methods in openapi_spec['paths'].items():
            for method, operation in methods.items():
                tool = self.create_tool_from_operation(
                    path=path,
                    method=method,
                    operation=operation
                )
                tools.append(tool)
        return tools
    
    def create_tool_from_operation(self, path, method, operation):
        return OpenAPITool(
            name=operation.get('operationId'),
            description=operation.get('summary'),
            path=path,
            method=method,
            parameters=operation.get('parameters', [])
        )
```

#### OpenAPI Tool Implementation
```python
class OpenAPITool(BaseTool):
    """Tool generated from OpenAPI specification"""
    
    async def execute(self, input: ToolInput, context: Dict) -> ToolOutput:
        # Build request from OpenAPI spec
        request = self.build_request(input.parameters)
        
        # Execute HTTP request
        response = await http_client.request(
            method=self.method,
            url=f"{self.base_url}{self.path}",
            **request
        )
        
        return ToolOutput(
            result=response.json(),
            sources=[response.url],
            metadata={'status_code': response.status_code}
        )
```

### A2A (Agent-to-Agent) Protocol Support
Google's A2A protocol for agent interoperability.

#### A2A Agent Wrapper
```python
class A2AAgentTool(BaseTool):
    """Wrapper for external A2A agents"""
    
    def __init__(self, agent_card_url: str):
        # Fetch agent card
        self.agent_card = self.fetch_agent_card(agent_card_url)
        self.name = f"a2a_{self.agent_card['name']}"
        self.description = self.agent_card['description']
        self.capabilities = self.agent_card['capabilities']
        
    async def execute(self, input: ToolInput, context: Dict) -> ToolOutput:
        # Create A2A request
        a2a_request = {
            "task": input.query,
            "context": context,
            "parameters": input.parameters
        }
        
        # Send to A2A agent
        response = await self.send_a2a_request(a2a_request)
        
        # Handle streaming or sync response
        if response.get('streaming'):
            return await self.handle_streaming(response)
        else:
            return ToolOutput(result=response['result'])
```

#### Mnemosyne as A2A Provider (Bidirectional Support)

##### Agent Card Generation
Mnemosyne generates dynamic A2A agent cards based on user configuration, supporting multiple exposure levels.

```python
class MnemosyneA2AProvider:
    """Expose Mnemosyne capabilities as A2A agents with privacy controls"""
    
    def __init__(self, user_config: UserA2AConfig):
        self.exposure_level = user_config.exposure_level  # none|local|selective|public
        self.exposed_tools = user_config.exposed_tools
        self.privacy_guards = PrivacyGuardChain()
    
    def generate_base_card(self) -> Dict:
        """Base agent card with core metadata"""
        return {
            "name": "mnemosyne_sovereign",
            "version": "1.0.0",
            "description": "Cognitive sovereignty platform with adaptive personas",
            "privacy": {
                "data_retention": "none",
                "telemetry": False,
                "user_data_access": "never"
            },
            "endpoints": self.get_endpoints(),
            "authentication": self.get_auth_methods()
        }
    
    def generate_public_card(self) -> Dict:
        """Minimal public card with only safe capabilities"""
        card = self.generate_base_card()
        card.update({
            "name": "mnemosyne_public",
            "capabilities": [
                {
                    "id": "concept_checker",
                    "name": "Philosophical Concept Analysis",
                    "description": "Analyze concepts through multiple philosophical lenses",
                    "stateless": True,
                    "frameworks": ["stoic", "pragmatist", "humanist"]
                }
            ],
            "limits": {
                "rate": "10/minute",
                "context_window": 4096
            }
        })
        return card
    
    def generate_partner_card(self, partner_id: str) -> Dict:
        """Enhanced card for trusted partners"""
        card = self.generate_base_card()
        card.update({
            "name": f"mnemosyne_partner_{partner_id}",
            "capabilities": self.get_partner_capabilities(partner_id),
            "limits": {
                "rate": "100/minute",
                "context_window": 8192
            }
        })
        return card
    
    def generate_local_card(self) -> Dict:
        """Full capabilities for local network use"""
        card = self.generate_base_card()
        card.update({
            "name": "mnemosyne_local",
            "capabilities": self.get_all_capabilities(),
            "endpoints": {
                "card": "http://localhost:8000/a2a/card",
                "task": "http://localhost:8000/a2a/task",
                "stream": "http://localhost:8000/a2a/stream",
                "admin": "http://localhost:8000/a2a/admin"  # Local only
            },
            "limits": {
                "rate": "unlimited",
                "context_window": 64000
            }
        })
        return card
    
    def get_capabilities_for_exposure(self, level: str) -> List[Dict]:
        """Get capabilities based on exposure level"""
        capabilities = []
        
        # Persona capabilities (selective exposure)
        if self.exposed_tools.get('personas'):
            for persona in self.exposed_tools['personas']['modes']:
                capabilities.append({
                    "id": f"persona_{persona}",
                    "name": f"{persona.title()} Persona",
                    "description": self.get_persona_description(persona),
                    "parameters": {
                        "max_tokens": 2000,
                        "temperature_range": [0.3, 0.9]
                    }
                })
        
        # Tool capabilities
        if self.exposed_tools.get('tools'):
            for tool_name, tool_config in self.exposed_tools['tools'].items():
                if tool_config.get('exposed'):
                    capabilities.append(self.tool_to_capability(tool_name))
        
        # Composite capabilities
        if level in ['partner', 'local']:
            capabilities.extend([
                {
                    "id": "concept_debate",
                    "name": "Multi-Agent Concept Debate",
                    "description": "Orchestrate philosophical debate between agents",
                    "parameters": {
                        "max_agents": 5,
                        "max_rounds": 3
                    }
                },
                {
                    "id": "multi_perspective",
                    "name": "Multi-Perspective Analysis",
                    "description": "Analyze through all available personas simultaneously"
                }
            ])
        
        return capabilities
```

##### Dynamic Card Endpoints
```python
@app.get("/a2a/card/{exposure_level}")
async def get_agent_card(
    exposure_level: str,
    auth: Optional[str] = Header(None),
    user_id: Optional[str] = Depends(get_current_user)
):
    """Serve appropriate agent card based on requester"""
    
    # Determine what card to serve
    if exposure_level == "public":
        # Anyone can get public card
        return provider.generate_public_card()
    
    elif exposure_level == "partner":
        # Requires partner authentication
        partner = await verify_partner(auth)
        if not partner:
            raise HTTPException(403, "Partner authentication required")
        return provider.generate_partner_card(partner.id)
    
    elif exposure_level == "local":
        # Only local network access
        if not is_local_request():
            raise HTTPException(403, "Local access only")
        return provider.generate_local_card()
    
    elif exposure_level == "discovery":
        # Minimal card for discovery services
        return {
            "name": "mnemosyne",
            "description": "Cognitive sovereignty platform",
            "card_endpoints": [
                "/a2a/card/public",
                "/a2a/card/partner",
                "/a2a/card/local"
            ]
        }
```

##### Privacy-Preserving Request Handler
```python
class A2ARequestHandler:
    """Handle incoming A2A requests with privacy protection"""
    
    async def handle_a2a_request(self, 
                                 request: A2ARequest,
                                 auth_level: str) -> A2AResponse:
        """Process A2A request based on authentication level"""
        
        # Check if requested capability is exposed at this auth level
        if not self.is_capability_allowed(request.capability, auth_level):
            return A2AResponse(
                error="Capability not available at this access level",
                code=403
            )
        
        # Apply privacy guards
        sanitized_request = self.privacy_guard.sanitize_input(request)
        
        # Route to appropriate handler
        if request.capability.startswith('persona_'):
            result = await self.handle_persona_request(sanitized_request)
        elif request.capability.startswith('tool_'):
            result = await self.handle_tool_request(sanitized_request)
        elif request.capability == 'concept_debate':
            result = await self.handle_debate_request(sanitized_request)
        else:
            result = await self.handle_generic_request(sanitized_request)
        
        # Sanitize output based on auth level
        sanitized_result = self.privacy_guard.sanitize_output(
            result, 
            auth_level
        )
        
        return A2AResponse(
            result=sanitized_result,
            metadata={
                "source": "mnemosyne",
                "privacy_filtered": True,
                "auth_level": auth_level
            }
        )
```

##### Configuration Schema
```yaml
# a2a_config.yaml
a2a_provider:
  enabled: true
  exposure_level: selective  # none|local|selective|public
  
  endpoints:
    public:
      enabled: true
      rate_limit: 10/minute
      capabilities:
        - concept_checker
    
    partner:
      enabled: true
      rate_limit: 100/minute
      require_auth: true
      capabilities:
        - concept_checker
        - concept_debate
        - persona_confidant
        - persona_mentor
    
    local:
      enabled: true
      rate_limit: unlimited
      capabilities: all
  
  exposed_capabilities:
    personas:
      confidant:
        exposed: true
        description: "Deep listening and empathetic analysis"
        rate_limit: 20/hour
      mentor:
        exposed: true
        description: "Guidance and skill development perspective"
        rate_limit: 20/hour
      guardian:
        exposed: false  # Keep private
      mirror:
        exposed: false  # Keep private
    
    tools:
      concept_checker:
        exposed: true
        stateless: true  # Safe to expose
      memory_search:
        exposed: false  # Never expose user memories
      task_manager:
        exposed: false  # Keep private
  
  privacy_guards:
    strip_pii: true
    strip_memories: true
    strip_internal_refs: true
    add_watermark: true
  
  authentication:
    public:
      required: false
    partner:
      required: true
      methods: [api_key, oauth2]
    local:
      required: false
      ip_whitelist: ["127.0.0.1", "192.168.0.0/16"]
```

## Protocol Comparison & Selection

### When to Use Each Protocol

| Protocol | Best For | Limitations |
|----------|----------|-------------|
| **Native Tools** | Internal capabilities, custom logic | Only works within Mnemosyne |
| **MCP** | Data access, file systems, databases | Focused on context/data, not actions |
| **OpenAPI** | REST APIs, existing services | Limited to HTTP endpoints |
| **A2A** | Agent collaboration, complex workflows | Newer standard, less adoption |

### Unified Adapter Pattern
```python
class UniversalToolAdapter:
    """Detect and adapt any tool format to Mnemosyne"""
    
    @classmethod
    def from_spec(cls, spec_url: str) -> BaseTool:
        spec_type = cls.detect_spec_type(spec_url)
        
        if spec_type == 'openapi':
            return OpenAPIToolGenerator().from_url(spec_url)
        elif spec_type == 'mcp':
            return MCPToolAdapter.from_url(spec_url)
        elif spec_type == 'a2a':
            return A2AAgentTool(spec_url)
        else:
            raise ValueError(f"Unknown spec type: {spec_type}")
    
    @classmethod
    def export_as_spec(cls, tool: BaseTool, format: str) -> Dict:
        """Export Mnemosyne tool in requested format"""
        if format == 'a2a':
            return cls.tool_to_a2a_capability(tool)
        elif format == 'openapi':
            return cls.tool_to_openapi_operation(tool)
        elif format == 'mcp':
            return cls.tool_to_mcp_tool(tool)
```

## Implementation Phases with Protocol Support

### Phase 1.B.1: Core Infrastructure (Week 1)
- Base tool system with native tools
- Tool registry and discovery
- Basic UI for tool selection

### Phase 1.B.2: OpenAPI Support (Week 2)
- OpenAPI spec parser
- Tool generation from specs
- Authentication handling
- Test with common APIs (GitHub, etc.)

### Phase 1.C.1: MCP Integration (Week 3)
- MCP client implementation
- Adapter for MCP servers
- Test with Anthropic's MCP tools
- Context management integration

### Phase 1.C.2: A2A Support (Week 4)
- A2A agent wrapper (consume external agents)
- Dynamic agent card generation (multiple exposure levels)
- Expose Mnemosyne as A2A provider with privacy controls
- Multi-agent orchestration
- Local-first testing, then selective public exposure

## Benefits of Protocol Support

### Consuming External Tools
1. **Ecosystem Access**: Tap into existing tools without building from scratch
2. **Interoperability**: Work with tools from different vendors
3. **Future-Proof**: Support emerging standards as they develop
4. **Flexibility**: Choose the right protocol for each use case
5. **Community**: Leverage community-built tools and integrations

### Providing Mnemosyne Capabilities
1. **Discoverability**: Other systems can find and use Mnemosyne's unique capabilities
2. **Sovereignty-Preserving**: Users control what capabilities are exposed
3. **Value Exchange**: Trade capabilities with other platforms (future)
4. **Ecosystem Participation**: Become a first-class citizen in the A2A ecosystem
5. **Multi-Instance Collaboration**: Run multiple Mnemosyne instances that work together

## Configuration Example

```yaml
# tools.config.yaml
tools:
  native:
    - calculator
    - memory_search
    - task_manager
  
  mcp_servers:
    - name: google_drive
      url: mcp://drive.google.com
      auth: oauth2
    
    - name: local_files
      url: mcp://localhost:5000
      auth: none
  
  openapi:
    - name: github
      spec: https://api.github.com/openapi.json
      auth:
        type: bearer
        token: ${GITHUB_TOKEN}
    
    - name: serpapi
      spec: https://serpapi.com/openapi.yaml
      auth:
        type: api_key
        key: ${SERPAPI_KEY}
  
  a2a_agents:
    - name: research_agent
      card: https://agents.example.com/research/card.json
      auth: api_key
    
    - name: code_reviewer
      card: https://reviewer.ai/a2a/card.json
      auth: oauth2
```

## Security Considerations

### Authentication Flow
1. Store credentials securely (encrypted in database)
2. Use OAuth2 where possible for user-specific access
3. Rotate API keys regularly
4. Audit tool usage for security monitoring

### Sandboxing External Tools
```python
class SandboxedToolExecutor:
    """Execute external tools with security constraints"""
    
    async def execute_safely(self, tool: BaseTool, input: ToolInput):
        # Rate limiting
        await self.rate_limiter.check(tool.name)
        
        # Input validation
        if not await tool.validate_input(input):
            raise ValueError("Invalid input")
        
        # Timeout enforcement
        with timeout(tool.timeout):
            result = await tool.execute(input)
        
        # Output sanitization
        return self.sanitize_output(result)
```

## Summary: Unified Tools & Protocol Architecture

### Core Design Principles
1. **Everything is a Tool**: Agents, APIs, and composite functions all share the same interface
2. **Bidirectional Protocol Support**: Both consume external tools AND provide Mnemosyne capabilities
3. **User Sovereignty**: Users control what tools are enabled and what capabilities are exposed
4. **Progressive Exposure**: Start local, gradually expose capabilities based on trust
5. **Privacy-First**: Multiple guards ensure no personal data leaks through external protocols

### Implementation Roadmap
- **Week 1**: Core tool infrastructure + native tools
- **Week 2**: OpenAPI support for REST APIs
- **Week 3**: MCP integration for data sources
- **Week 4**: A2A bidirectional support with agent cards
- **Future**: Tool marketplace, reputation, credits

### Key Innovations
- **Dynamic Agent Cards**: Different exposure levels (public/partner/local)
- **Universal Adapter**: Auto-detect and convert between protocols
- **Privacy Guards**: Automatic sanitization of inputs/outputs
- **Composite Tools**: Higher-level tools that orchestrate others
- **Tool Palette UI**: Manual control with optional automation

---

*This unified architecture makes Mnemosyne both a powerful tool consumer and a responsible tool provider, maintaining cognitive sovereignty while participating in the broader AI ecosystem.*