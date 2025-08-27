# Unified Sub-Agent System Planning Document
*Last Updated: August 27, 2025*

## Current State Assessment

### Shadow System (PoC Stage)
- **Maturity**: Early proof of concept with basic LLM integration
- **Architecture**: Orchestrator → Specialized Agents → Aggregation
- **Agents**: Engineer, Librarian, Priest (basic implementations with prompts)
- **Strengths**: 
  - Has memory integration concept (vector, relational, document)
  - Session management infrastructure
  - Basic task decomposition
- **Weaknesses**:
  - Separate from main Mnemosyne system
  - Own API/frontend (duplicate infrastructure)
  - Mock fallbacks throughout
  - Not integrated with our agentic flow

### Dialogue System (PoC Stage)  
- **Maturity**: Early proof of concept with Autogen framework
- **Architecture**: Dynamic agent loader from markdown definitions
- **Agents**: 10+ philosophical agents, judge agents for evaluation
- **Strengths**:
  - Dynamic agent creation from markdown
  - Debate protocol (opening, rebuttal, judging)
  - Quorum voting system
- **Weaknesses**:
  - Separate from main system
  - Different LLM integration approach
  - No connection to memory/tasks
  - Autogen dependency may not align with our architecture

## Proposed Unified Sub-Agent System

### Design Principles
1. **Single Infrastructure**: Use Mnemosyne's existing agentic flow as the foundation
2. **Modular Agents**: Agents as lightweight plugins, not separate systems
3. **User Control**: Manual enable/disable of agents in UI
4. **Progressive Activation**: Start with manual, evolve to automatic
5. **Unified Memory**: All agents share Mnemosyne's memory/task systems

### Architecture Vision

```
User Input
    ↓
Chat Interface (Enhanced)
    ├── Manual Agent Selection UI
    ├── Flow Layer Controls
    └── Agent Status Display
    ↓
Agentic Flow Controller (Extended)
    ├── Core Actions (existing)
    ├── Sub-Agent Registry (new)
    └── Agent Orchestration (new)
    ↓
Sub-Agent System (new)
    ├── Technical Agents (from Shadow)
    │   ├── Engineer
    │   ├── Librarian
    │   └── Researcher (renamed Priest)
    ├── Philosophical Agents (from Dialogue)
    │   ├── Core Set (5-10 agents)
    │   └── Extended Set (loadable)
    └── Custom Agents (future)
```

## Implementation Phases

### Phase 1.B: Foundation (1-2 weeks)
**Goal**: Create basic sub-agent infrastructure

1. **Sub-Agent Base Class**
   ```python
   class SubAgent:
       name: str
       description: str
       capabilities: List[str]
       system_prompt: str
       
       async def process(query: str, context: Dict) -> AgentResponse
       async def can_handle(query: str) -> float  # confidence 0-1
   ```

2. **Agent Registry**
   - Central registry in `backend/app/services/agents/`
   - Dynamic loading from configuration
   - Enable/disable per user preference

3. **UI Controls**
   - Add agent selector to chat interface
   - Show active agents in conversation
   - Manual enable/disable toggles

4. **Integration Points**
   - New action type: `CONSULT_AGENT`
   - Extend executors to call sub-agents
   - Add agent responses to receipts

### Phase 1.C: Migration & Enhancement (1-2 weeks)
**Goal**: Port best agents from Shadow/Dialogue

1. **Port Core Agents**
   - Engineer → TechnicalAgent
   - Librarian → ResearchAgent
   - Top 5 philosophical agents

2. **Standardize Prompts**
   - Convert to unified prompt format
   - Store in `backend/app/prompts/agents/`
   - Version control for prompts

3. **Add Agent Interactions**
   - Agents can see each other's responses
   - Basic debate/collaboration modes
   - Synthesis generation

4. **Enhanced UI**
   - Agent contribution visualization
   - Confidence scores display
   - Response attribution

### Phase 1.D: Intelligence (2-3 weeks)
**Goal**: Automatic agent activation

1. **Smart Routing**
   - LLM determines which agents to consult
   - Confidence-based activation
   - User preference learning

2. **Multi-Agent Orchestration**
   - Parallel agent execution
   - Consensus mechanisms
   - Conflict resolution

3. **Advanced Features**
   - Agent memory (per-agent context)
   - Agent specialization training
   - Custom agent creation UI

## Technical Decisions Needed

### 1. Agent Storage Format
**Options**:
- Python classes (current Shadow approach)
- Markdown files (current Dialogue approach)
- JSON/YAML configuration
- **Recommendation**: YAML with embedded prompts for flexibility

### 2. LLM Integration
**Options**:
- Direct OpenAI calls per agent
- Shared LLM service with queuing
- **Recommendation**: Use existing LLMService with sub-agent context

### 3. Agent Activation
**Options**:
- Always manual selection
- Automatic based on keywords
- LLM-driven selection
- **Recommendation**: Start manual, add automatic as optional mode

### 4. Response Format
**Options**:
- Inline agent responses in main chat
- Separate agent response section
- Collapsible agent contributions
- **Recommendation**: Collapsible sections with attribution

## UI/UX Mockup

```
┌─────────────────────────────────────┐
│  Chat Enhanced                      │
├─────────────────────────────────────┤
│ [Manual] [Agentic] [Agents: ON ▼]  │
│                                     │
│ Active Agents:                      │
│ ☑ Technical  ☑ Research  ☐ Ethics  │
│ ☐ Stoic  ☐ Pragmatist  [More...]   │
├─────────────────────────────────────┤
│ User: How do I optimize this code? │
│                                     │
│ Assistant: I'll help optimize your │
│ code. Let me consult our technical │
│ specialist...                       │
│                                     │
│ ▼ Technical Agent (confidence: 92%)│
│   [Agent's detailed response]       │
│                                     │
│ Based on the technical analysis... │
└─────────────────────────────────────┘
```

## Migration Path

### From Shadow System
1. Extract agent prompts and logic
2. Remove separate infrastructure (API, frontend)
3. Convert to sub-agent format
4. Integrate with main memory/task systems

### From Dialogue System
1. Extract agent definitions
2. Remove Autogen dependency
3. Convert to sub-agent format
4. Preserve debate mechanisms as orchestration modes

## Success Metrics

1. **Phase 1.B Success**:
   - 3+ agents integrated
   - Manual selection working
   - Responses properly attributed

2. **Phase 1.C Success**:
   - 10+ agents available
   - Agent interactions working
   - UI clearly shows contributions

3. **Phase 1.D Success**:
   - Automatic routing achieving 80% accuracy
   - Multi-agent debates producing coherent synthesis
   - User satisfaction with agent suggestions

## Risks & Mitigations

1. **Risk**: Complexity explosion
   - **Mitigation**: Start simple, iterate based on usage

2. **Risk**: Response latency with multiple agents
   - **Mitigation**: Parallel execution, caching, selective activation

3. **Risk**: Confusing UI with too many agents
   - **Mitigation**: Progressive disclosure, smart defaults

4. **Risk**: Prompt management chaos
   - **Mitigation**: Version control, testing framework

## Next Steps

1. **Review & Approve**: Discuss this plan, make adjustments
2. **Create Base Infrastructure**: SubAgent class and registry
3. **Build UI Controls**: Manual agent selection interface
4. **Port First Agent**: Start with Technical/Engineer as test case
5. **Iterate**: Get working, then enhance

## Open Questions

1. Should agents have their own memory spaces or share global?
2. How much autonomy should agents have in spawning sub-tasks?
3. Should we support custom user-created agents from day one?
4. What's the right balance between Shadow's specialization and Dialogue's philosophical diversity?

---

*This plan prioritizes pragmatic integration over architectural purity. We can build a working system quickly by leveraging existing infrastructure and iterating based on actual usage.*