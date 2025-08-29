# Shadow Council Internal Execution Flow

## Overview
When the Shadow Council tool is triggered, it orchestrates a sophisticated multi-agent discussion among five specialized technical advisors. Here's what happens behind the scenes.

## The Council Members

1. **Artificer** - Systems architect and engineer
2. **Archivist** - Data structures and information expert  
3. **Mystagogue** - Security and cryptography specialist
4. **Tactician** - Strategy and optimization expert
5. **Daemon** - Infrastructure and operations specialist

## Execution Flow

### Step 1: Query Reception
When `USE_TOOL` action triggers with `tool_name="shadow_council"`:
```json
{
  "action": "USE_TOOL",
  "parameters": {
    "tool_name": "shadow_council",
    "query": "design a secure blockchain system",
    "parameters": {}
  }
}
```

### Step 2: Council Initialization (shadow_council.py)
```python
# The tool executor calls the Shadow Council service
result = await shadow_council_tool.execute(
    query="design a secure blockchain system",
    context={...}
)
```

### Step 3: Multi-Agent Orchestration

#### Phase 1: Individual Analysis (Parallel)
Each council member receives the query simultaneously and prepares their perspective:

```
Query: "design a secure blockchain system"
         ↓
    [Parallel Execution]
         ↓
┌─────────────┬─────────────┬──────────────┬──────────────┬──────────────┐
│  Artificer  │  Archivist  │  Mystagogue  │  Tactician   │   Daemon     │
├─────────────┼─────────────┼──────────────┼──────────────┼──────────────┤
│ Engineering │ Data Model  │  Security    │  Strategy    │ Operations   │
│ Blueprint   │ Design      │  Analysis    │  Roadmap     │ Architecture │
└─────────────┴─────────────┴──────────────┴──────────────┴──────────────┘
```

**Artificer's Process:**
- Analyzes technical requirements
- Designs system architecture
- Proposes consensus mechanisms
- Outlines smart contract runtime

**Archivist's Process:**
- Designs data structures
- Plans storage layers
- Defines state management
- Creates indexing strategies

**Mystagogue's Process:**
- Threat modeling
- Cryptographic scheme selection
- Zero-knowledge proof integration
- Security audit framework

**Tactician's Process:**
- Scalability planning
- Network topology optimization
- Economic incentive design
- Governance mechanisms

**Daemon's Process:**
- Infrastructure requirements
- Deployment strategies
- Monitoring and alerting
- Performance optimization

#### Phase 2: Synthesis Discussion
After individual analyses, the agents engage in structured debate:

```python
# Pseudo-code of internal discussion
discussion_rounds = 3
for round in range(discussion_rounds):
    for agent in council_members:
        # Each agent reviews others' proposals
        critique = agent.review_proposals(other_proposals)
        
        # Agent refines their position
        agent.refine_position(critique)
        
        # Identify consensus points
        consensus_points = find_agreements(all_positions)
```

#### Phase 3: Consensus Building
The council identifies:
- **Unanimous agreements** - Core requirements all agree on
- **Majority positions** - Recommended approaches with broad support
- **Dissenting opinions** - Alternative approaches worth noting
- **Open questions** - Areas requiring user clarification

### Step 4: Response Compilation

The final response is structured as:

```markdown
## Shadow Council Consensus Report

### Unanimous Recommendations
- [Core security requirements]
- [Essential architectural patterns]

### Individual Expert Analyses
**Artificer's Blueprint:**
[Detailed engineering proposal]

**Archivist's Data Model:**
[Storage and state management design]

**Mystagogue's Security Framework:**
[Cryptographic and threat analysis]

**Tactician's Strategic Roadmap:**
[Implementation phases and governance]

**Daemon's Operations Plan:**
[Infrastructure and deployment strategy]

### Synthesis & Next Steps
[Integrated recommendations combining all perspectives]
```

### Step 5: Result Delivery
The compiled response is returned through the action executor:
```python
return ActionResult(
    action="USE_TOOL",
    success=True,
    data={
        "tool_name": "shadow_council",
        "result": compiled_response,
        "confidence": 0.95,
        "contributors": ["Artificer", "Archivist", "Mystagogue", "Tactician", "Daemon"]
    }
)
```

## Example Execution Timeline

For the blockchain query example:

```
T+0ms    : Query received by Shadow Council
T+50ms   : Individual prompts dispatched to 5 agents (parallel)
T+100ms  : Agents begin analysis with their specialized prompts
T+3000ms : Artificer completes engineering blueprint
T+3200ms : Archivist completes data model
T+3500ms : Mystagogue completes security analysis
T+3600ms : Tactician completes strategy roadmap
T+3800ms : Daemon completes operations plan
T+4000ms : Synthesis phase begins
T+5000ms : Discussion rounds complete
T+5500ms : Final response compiled and formatted
T+5600ms : Response returned to user
```

## Key Features

### 1. Parallel Processing
All five agents work simultaneously, reducing total response time.

### 2. Specialized Expertise
Each agent has a distinct system prompt and knowledge domain:
- Artificer: Low-level implementation details
- Archivist: Information organization and retrieval
- Mystagogue: Security and cryptography
- Tactician: High-level strategy and planning
- Daemon: Infrastructure and operations

### 3. Structured Output
Responses follow a consistent format:
- Clear section headers
- Technical depth with practical examples
- Code snippets where relevant
- Actionable recommendations

### 4. Conflict Resolution
When agents disagree:
1. Present majority view as primary recommendation
2. Include minority perspectives as alternatives
3. Highlight trade-offs explicitly
4. Request user input for critical decisions

## Configuration

The Shadow Council behavior can be tuned via environment variables:

```bash
# Response detail level
SHADOW_COUNCIL_DETAIL=high  # low, medium, high

# Maximum response length per agent
SHADOW_COUNCIL_MAX_TOKENS=2000

# Enable/disable discussion rounds
SHADOW_COUNCIL_DISCUSSION=true

# Parallel vs sequential execution
SHADOW_COUNCIL_PARALLEL=true
```

## Error Handling

If an agent fails:
1. Council continues with remaining agents
2. Failed agent's domain marked as "pending review"
3. Partial response delivered with clear notation
4. User advised of incomplete analysis

## Integration Points

The Shadow Council integrates with:
- **Memory Service**: Stores technical decisions for future reference
- **Task Service**: Can generate implementation tasks from recommendations
- **Receipt Service**: Creates audit trail of technical consultations
- **Persona System**: Adjusts technical depth based on user expertise level