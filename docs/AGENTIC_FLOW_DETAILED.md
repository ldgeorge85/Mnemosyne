# Agentic Flow Architecture - Complete Technical Guide
*Last Updated: August 27, 2025*
*Status: Phase 1.A COMPLETE*

## Table of Contents
1. [Overview](#overview)
2. [Request Flow](#request-flow)
3. [Prompt Processing Pipeline](#prompt-processing-pipeline)
4. [Persona Selection & Application](#persona-selection--application)
5. [Available Tools & Actions](#available-tools--actions)
6. [ReAct Pattern Implementation](#react-pattern-implementation)
7. [Current Capabilities](#current-capabilities)
8. [Future Enhancements](#future-enhancements)

## Overview

The Mnemosyne Agentic Flow implements a sophisticated ReAct (Reasoning + Acting) pattern that transforms simple chat interactions into intelligent, multi-action workflows. Unlike traditional chatbots that directly pipe prompts to an LLM, the agentic system:

1. **Analyzes** the user's intent using LLM reasoning
2. **Plans** multiple actions to fulfill that intent
3. **Executes** actions in parallel for efficiency
4. **Reflects** on results to determine if more is needed
5. **Suggests** proactive next steps while respecting user sovereignty

## Request Flow

### 1. Entry Point: `/api/v1/chat/agentic/stream`

When a request arrives with the "Agentic" toggle enabled:

```python
POST /api/v1/chat/agentic/stream
{
    "messages": [...],           # Conversation history
    "use_agentic": true,         # Explicitly enable agentic mode
    "max_iterations": 3,         # Max reasoning loops
    "stream_status": true,       # Stream processing updates
    "include_reasoning": true,   # Include reasoning in response
    "parallel_actions": true     # Execute actions simultaneously
}
```

### 2. Authentication & Context Building

```python
# Step 1: Verify user authentication
user = get_current_user()  # JWT token validation

# Step 2: Extract query from messages
query = extract_last_user_message(messages)

# Step 3: Build initial context
context = {
    "user_id": user.user_id,
    "messages": messages,
    "persona_mode": None,  # To be determined by LLM
    "memories": [],        # To be populated
    "max_iterations": 3,
    "query": query,        # For suggestions generation
    "original_query": query,  # Preserved for reference
    "parallel": True       # Enable parallel execution
}
```

### 3. Memory Context Retrieval

Before any LLM processing, the system retrieves relevant memories:

```python
# Semantic search through user's memory vault
relevant_memories = await memory_service.get_relevant_memories(
    query=query,
    user_id=user_id,
    limit=5,                    # Top 5 most relevant
    score_threshold=0.3         # Minimum relevance score
)

# Yields: "Retrieving relevant memories..."
# Yields: "Found 3 relevant memories"
```

## Prompt Processing Pipeline

### Stage 1: LLM-Driven Persona Selection

Instead of keyword matching, the system uses LLM reasoning to select the appropriate persona:

**Prompt Template: `agentic_persona_selection.txt`**
```
You are the Mnemosyne Protocol's persona selector. Based on the user's query and context, determine the most appropriate persona mode to activate.

User Query: {query}
Current Mode: {current_mode}
Recent Context: {context}
User Mood Indicators: {mood_indicators}

Available Personas:
1. CONFIDANT - Deep listening, emotional support, empathic presence
2. MENTOR - Skill development, growth guidance, learning support
3. MEDIATOR - Conflict resolution, balanced perspectives, trust navigation
4. GUARDIAN - Protection, risk assessment, wellbeing focus
5. MIRROR - Pure reflection without judgment

Analyze the query and select the SINGLE most appropriate persona mode.
Return as JSON:
{
  "selected_mode": "MODE_NAME",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation"
}
```

### Stage 2: Query Analysis & Reasoning

The flow controller analyzes what needs to be done:

**Prompt Template: `agentic_reasoning.txt`**
```
Given the user query: {query}
Current persona mode: {current_persona}
Available memories: {available_memories}
Active tasks: {active_tasks}
Previous actions taken: {previous_actions}

Analyze what needs to be done to properly respond to this query.
Consider which actions would be most helpful.
Available actions: {available_actions}

Provide clear reasoning about what should be done and why.
```

### Stage 3: Action Planning

Based on reasoning, the system plans specific actions:

**Prompt Template: `agentic_planning.txt`**
```
Based on this reasoning: {reasoning}

Available actions: {available_actions}

Create a specific action plan as a JSON array. Each action should have:
- action: the action name from available actions
- parameters: any parameters needed
- reasoning: why this action is needed
- confidence: confidence score 0-1

Return ONLY valid JSON array, no other text.
```

## Persona Selection & Application

### How Personas Are Selected

1. **Context Analysis**: The LLM analyzes:
   - Emotional tone of the query
   - Type of support needed
   - User's historical patterns
   - Current conversation context

2. **Mode Selection Logic**:
   - **CONFIDANT**: Selected for emotional sharing, personal struggles, need for empathy
   - **MENTOR**: Activated for learning requests, skill development, goal setting
   - **MEDIATOR**: Chosen for conflict resolution, relationship issues, balanced analysis
   - **GUARDIAN**: Triggered by safety concerns, risk detection, vulnerability
   - **MIRROR**: Used for self-reflection, pattern analysis, neutral observation

### How Personas Are Applied

Once selected, the persona affects:

1. **System Prompt Enhancement**:
```python
# Base persona prompt is retrieved
system_prompt = persona.get_system_prompt()

# Worldview adaptations are applied
if user_profile:
    system_prompt = worldview_adapter.adapt_prompt(system_prompt)

# Context is added
system_prompt += f"""
Current Context:
- User Trust Level: {trust_level}
- User Values: {values}
- Mode: {persona_mode}
"""
```

2. **Response Parameters**:
```python
modifiers = persona.get_response_parameters()
# Returns: {
#     "temperature": 0.7,  # Varies by mode
#     "style": "empathetic",
#     "focus": "emotional_support"
# }
```

## Available Tools & Actions

### Current Implementation Status

#### ✅ Fully Implemented Actions

1. **SELECT_PERSONA** - LLM-driven mode selection
   ```python
   async def _select_persona(params, context, user_id):
       selected_mode = await persona_manager.select_mode_llm(query, context)
       persona = persona_manager.get_persona(selected_mode)
       return {"selected_mode": selected_mode, "reasoning": "..."}
   ```

2. **SEARCH_MEMORIES** - Vector similarity search
   ```python
   async def _search_memories(params, context, user_id):
       # Uses context memories if available
       memories = context.get("memories", [])
       return {"memories_found": len(memories), "memories": memories}
   ```

3. **LIST_TASKS** - Retrieve user's tasks (WORKING)
   ```python
   async def _list_tasks(params, context, user_id):
       tasks, total_count = await task_service.get_tasks_by_user_id(
           user_id=user_id,
           limit=params.get("limit", 10)
       )
       return {"tasks": task_list, "count": len(task_list)}
   ```

4. **CREATE_TASK** - Create new tasks
   ```python
   async def _create_task(params, context, user_id):
       task = await task_service.create_task(
           user_id=user_id,
           title=params.get("title"),
           description=params.get("description"),
           priority=TaskPriority(params.get("priority", "medium"))
       )
       return {"task_id": str(task.id), "created": True}
   ```

#### 🔄 Partially Implemented Actions

5. **CREATE_MEMORY** - Memory creation (backend exists, executor stub)
6. **UPDATE_TASK** - Task status updates (backend exists, executor stub)
7. **DECOMPOSE_TASK** - Break down complex tasks (returns stub)

#### 📋 Stub/Pending Actions

6. **LINK_MEMORIES** - Connect related memories (returns pending status)
7. **DECOMPOSE_TASK** - Break down complex tasks (returns pending status)
8. **ACTIVATE_SHADOW** - Technical agent activation
   ```python
   # Currently returns:
   {
       "agent_type": "Engineer",
       "status": "pending_integration",
       "message": "Would activate Engineer agent for: {query}"
   }
   ```

9. **ACTIVATE_DIALOGUE** - Philosophical debate orchestration
10. **UPDATE_TRUST** - Trust relationship modifications
11. **CREATE_APPEAL** - Trust decision appeals
12. **ANALYZE_PATTERNS** - Behavioral pattern analysis
13. **REFLECT** - Deep reflection on memories
14. **SUGGEST** - Proactive suggestion generation

#### Control Actions (Always Available)

15. **DONE** - Signal completion
16. **NEED_MORE** - Request additional context
17. **EXPLAIN** - Provide reasoning explanation
18. **WAIT_USER** - Wait for user input

### Action Execution Flow

```python
# Parallel execution example
if plan.parallel and len(actions) > 1:
    tasks = [
        flow_controller.execute_action(action, context, user_id)
        for action in actions
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
else:
    # Sequential execution
    results = []
    for action in actions:
        result = await flow_controller.execute_action(action, context, user_id)
        results.append(result)
```

## ReAct Pattern Implementation

### The Core Loop

```python
async def execute_flow(query, context, user_id):
    iteration = 0
    max_iterations = 3
    
    while iteration < max_iterations:
        iteration += 1
        
        # 1. REASONING: Analyze what needs to be done
        reasoning = await reason_about_query(query, context)
        # Yields: "Analyzing query (iteration 1)..."
        
        # 2. PLANNING: Determine specific actions
        actions = await plan_actions(reasoning, context)
        # Yields: "Planning actions..."
        # Yields: "Executing 3 actions: SEARCH_MEMORIES, SELECT_PERSONA, SUGGEST"
        
        # 3. ACTING: Execute actions in parallel
        results = await asyncio.gather(*[
            execute_action(action, context, user_id)
            for action in actions
        ])
        
        # 4. REFLECTION: Check if more needed
        needs_more = await needs_more_info(results, context)
        # Yields: "Checking if more needed..."
        
        if not needs_more or DONE in actions:
            break
            
        # Update context for next iteration
        context['previous_actions'] = actions
        context['previous_results'] = results
    
    # 5. SUGGESTIONS: Generate proactive next steps
    suggestions = await get_proactive_suggestions(actions, results, context)
    # Yields: "Generating suggestions..."
    
    # 6. TRANSPARENCY: Create decision receipt
    receipt = await create_decision_receipt(
        reasoning, actions, results, user_id
    )
    
    return response
```

### Iteration Examples

**Iteration 1**: User says "I'm feeling overwhelmed"
- Reasoning: "User expressing emotional distress"
- Actions: [SELECT_PERSONA(confidant), SEARCH_MEMORIES(stress, overwhelm)]
- Results: Found 2 related memories about work stress

**Iteration 2**: Needs more context
- Reasoning: "Found patterns, need to understand current situation"
- Actions: [ANALYZE_PATTERNS, SUGGEST]
- Results: Identified recurring Tuesday stress pattern

**Iteration 3**: Complete response
- Reasoning: "Have sufficient context to provide support"
- Actions: [DONE]
- Final response with empathetic support and pattern insights

## Current Capabilities

### What Works Today

1. **Intelligent Persona Selection**
   - LLM analyzes emotional tone and intent
   - Selects from 5 distinct personas
   - Applies persona-specific prompts and parameters

2. **Memory Integration**
   - Semantic search through user's memories
   - Relevant context retrieval
   - Memory-aware responses

3. **Parallel Processing**
   - Multiple actions execute simultaneously
   - Reduces response latency
   - Maintains result ordering

4. **Streaming Status Updates**
   - Real-time processing visibility
   - User sees what the system is doing
   - Builds trust through transparency

5. **Receipt Generation**
   - Every decision recorded
   - Full reasoning transparency
   - User can audit AI decisions

### Current Limitations

1. **Shadow/Dialogue Agents**: Not connected yet
2. **Task Decomposition**: Returns stub responses
3. **Trust Networks**: Backend exists, not integrated
4. **Pattern Analysis**: Basic implementation only
5. **Collective Intelligence**: Future phase

## Future Enhancements

### Phase 1.A Completion (Next 1-2 weeks)

1. **Connect Shadow Agents**
   ```python
   # Engineer: Code analysis, technical solutions
   # Librarian: Information retrieval, organization
   # Priest: Pattern recognition, deep insights
   ```

2. **Connect Dialogue Agents**
   ```python
   # 50+ philosophical agents for debate
   # Socrates, Confucius, Rumi, etc.
   ```

3. **Implement Pattern Analysis**
   ```python
   # Temporal patterns
   # Behavioral clusters
   # Emotional cycles
   ```

### Phase 2: Trust Networks

1. **Progressive Trust Exchange**
2. **Reputation Scoring**
3. **Privacy-Preserving Matching**

### Phase 3: Collective Intelligence

1. **Multi-Agent Collaboration**
2. **Collective Decision Making**
3. **Emergent Intelligence Patterns**

## Example: Complete Agentic Flow

### User Input
"I keep having the same argument with my partner about money"

### Agentic Processing

**Step 1: Memory Retrieval**
```
Status: "Retrieving relevant memories..."
Status: "Found 4 relevant memories"
```

**Step 2: Persona Selection (LLM)**
```
Status: "Selecting optimal persona mode..."
LLM Analysis: {
  "selected_mode": "mediator",
  "confidence": 0.92,
  "reasoning": "Relationship conflict requiring balanced perspective"
}
```

**Step 3: Query Analysis**
```
Status: "Analyzing query (iteration 1)..."
Reasoning: "Recurring relationship conflict about finances. 
           Need to understand patterns and provide mediation."
```

**Step 4: Action Planning**
```
Status: "Planning actions..."
Actions: [
  {
    "action": "ANALYZE_PATTERNS",
    "parameters": {"data_type": "memories", "topic": "money arguments"},
    "confidence": 0.85
  },
  {
    "action": "SEARCH_MEMORIES",
    "parameters": {"query": "financial stress partner"},
    "confidence": 0.90
  },
  {
    "action": "SUGGEST",
    "parameters": {"type": "conflict_resolution"},
    "confidence": 0.75
  }
]
```

**Step 5: Parallel Execution**
```
Status: "Executing 3 actions: ANALYZE_PATTERNS, SEARCH_MEMORIES, SUGGEST"
```

**Step 6: Response Generation**
With MEDIATOR persona active, generates balanced response acknowledging both perspectives

**Step 7: Proactive Suggestions**
```
Suggestions: [
  "Would you like to explore communication techniques for financial discussions?",
  "Should we create a task to schedule a calm money conversation?",
  "Would reviewing your shared financial goals be helpful?"
]
```

**Step 8: Receipt Creation**
All reasoning, actions, and results recorded for transparency

## Technical Architecture

### Service Dependencies

```
AgenticFlowController
    ├── LLMService (OpenAI/Anthropic/Ollama)
    ├── ReceiptService (Transparency)
    ├── PersonaManager (Mode selection)
    ├── MemoryContextService (Retrieval)
    ├── ActionExecutor
    │   ├── MemoryService
    │   ├── TaskService
    │   ├── VectorStore (Qdrant)
    │   └── TrustService (pending)
    └── PromptTemplates
        ├── agentic_reasoning.txt
        ├── agentic_planning.txt
        ├── agentic_needs_more.txt
        └── agentic_suggestions.txt
```

### SSE Event Stream Format

```javascript
event: status
data: {"status": "Retrieving relevant memories..."}

event: reasoning
data: {"reasoning": "User needs emotional support..."}

event: content
data: {"content": "I understand you're feeling..."}

event: suggestions
data: {"suggestions": [...]}

event: done
data: {"duration_ms": 2453, "iterations": 2}
```

## Configuration & Tuning

### Key Parameters

```python
# Maximum reasoning iterations
MAX_ITERATIONS = 3  # Prevents infinite loops

# Action execution timeout
ACTION_TIMEOUT_MS = 5000  # 5 seconds per action

# Memory retrieval
MEMORY_LIMIT = 5  # Max memories to retrieve
MEMORY_THRESHOLD = 0.3  # Minimum relevance score

# LLM Parameters
REASONING_TEMPERATURE = 0.7  # Balance creativity/consistency
PLANNING_TEMPERATURE = 0.3  # More deterministic planning

# Parallel execution
MAX_PARALLEL_ACTIONS = 5  # Limit concurrent actions
```

### Performance Characteristics

- **Initial latency**: 200-500ms (memory retrieval)
- **Persona selection**: 300-800ms (LLM call)
- **Action planning**: 400-1000ms (LLM call)
- **Action execution**: 100-2000ms per action (parallel)
- **Total flow**: 2-5 seconds typical

## Debugging & Monitoring

### Key Log Points

```python
logger.info(f"Received agentic request with {len(messages)} messages")
logger.info(f"Selected persona: {selected_mode} with confidence {confidence}")
logger.info(f"Planned {len(actions)} actions for iteration {iteration}")
logger.info(f"Action {action} completed in {duration_ms}ms")
```

### Common Issues & Solutions

1. **"No user message found"**: Ensure user message is in request
2. **Network chunked encoding error**: Check for exceptions in action executors
3. **Timeout on actions**: Reduce parallel actions or increase timeout
4. **LLM planning fails**: Check prompt template formatting

---

*The agentic flow transforms Mnemosyne from a reactive chatbot into a proactive cognitive assistant that thinks before acting, executes efficiently, and maintains transparency throughout.*