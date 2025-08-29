# Shadow Council Trigger Flow - Complete Documentation

## Example User Query
"I need help designing a blockchain protocol for distributed identity. Please consult the Shadow Council."

## Phase 1: Persona Selection (13:25:15 - 13:25:19)

### Prompt Assembly
**File**: `/home/lewis/dev/personal/mnemosyne/backend/app/services/persona/manager.py` lines 306-341

Since `/app/backend/app/prompts/agentic_persona_selection.txt` doesn't exist, it falls back to exception handling at line 363.

**What ACTUALLY happens**: 
- The code tries to parse JSON from LLM response at line 345
- InnoGPT-1 returns plain text, not JSON
- Exception is caught, tries to call `self.select_mode()` which doesn't exist
- This causes ANOTHER exception, but somehow still works (bug needs investigation)

### Actual LLM Call
```python
# System prompt
"You are a persona mode selector for the Mnemosyne Protocol."

# User prompt (from fallback, since file doesn't exist)
# This is constructed but never properly sent due to the exception
```

**LLM Response** (InnoGPT-1 format):
```
The user is requesting technical assistance with designing a blockchain protocol, which aligns with the Mentor persona's focus on skill development, learning support, and expert guidance rather than emotional support or conflict mediation.
```

**Result**: MENTOR mode selected (despite the bugs)

---

## Phase 2: Reasoning (13:25:19 - 13:25:39) - 20 seconds

### Prompt Assembly
**File**: `/home/lewis/dev/personal/mnemosyne/backend/app/services/agentic/flow_controller.py`

#### Step 1: Load prompt template (lines 177-178)
- Tries to load `/app/backend/app/prompts/agentic_reasoning.txt` 
- File doesn't exist
- Falls back to `_get_default_prompt("agentic_reasoning")` at line 476

#### Step 2: Get default prompt (lines 492-525)
```python
defaults["agentic_reasoning"] = """
Given the user query: {query}
Current persona mode: {current_persona}
Available memories: {available_memories}
Active tasks: {active_tasks}
Previous actions taken: {previous_actions}

Analyze what needs to be done to properly respond to this query.

IMPORTANT: Use these specific actions (DO NOT use ACTIVATE_SHADOW or ACTIVATE_DIALOGUE - those are deprecated):

- USE_TOOL: Execute specialized tools for complex analysis. ALWAYS use this when:
  * User mentions "Shadow Council" or needs technical help → USE_TOOL with tool_name="shadow_council"
  * User mentions "Forum of Echoes" or needs philosophical perspectives → USE_TOOL with tool_name="forum_of_echoes"
  * User needs calculations → USE_TOOL with tool_name="calculator"
  * User needs date/time → USE_TOOL with tool_name="datetime"
- SEARCH_MEMORIES: Search user's stored memories
- CREATE_MEMORY: Store new information as a memory
- LIST_TASKS/CREATE_TASK: Manage user's tasks
- EXPLAIN: Provide direct explanation without tools
- DONE: Simple response is sufficient

DO NOT USE: ACTIVATE_SHADOW, ACTIVATE_DIALOGUE (these are legacy - use USE_TOOL instead)

Available tools:
[TOOL LIST WOULD BE INSERTED HERE BUT FAILS - registry.get_tool_metadata() throws error]

Consider if any tools would enhance the response, especially for:
- Technical/architectural questions → Shadow Council
- Philosophical/ethical questions → Forum of Echoes
- Complex analysis requiring multiple perspectives

Provide clear reasoning about what should be done and why.
"""
```

#### Step 3: Fill template variables (lines 181-188)
```python
llm_context = {
    "query": "I need help designing a blockchain protocol for distributed identity. Please consult the Shadow Council.",
    "current_persona": "mentor",
    "available_memories": 5,
    "active_tasks": 0,
    "previous_actions": [],
    "available_actions": ["USE_TOOL", "SEARCH_MEMORIES", "CREATE_MEMORY", "LIST_TASKS", "CREATE_TASK", "UPDATE_TASK", "EXPLAIN", "DONE", "NEED_MORE"]
}
```

### ACTUAL PROMPT SENT TO LLM
```
System: You are an intelligent assistant that reasons about user queries and determines what actions to take.

User: Given the user query: I need help designing a blockchain protocol for distributed identity. Please consult the Shadow Council.
Current persona mode: mentor
Available memories: 5
Active tasks: 0
Previous actions taken: []

Analyze what needs to be done to properly respond to this query.

IMPORTANT: Use these specific actions (DO NOT use ACTIVATE_SHADOW or ACTIVATE_DIALOGUE - those are deprecated):

- USE_TOOL: Execute specialized tools for complex analysis. ALWAYS use this when:
  * User mentions "Shadow Council" or needs technical help → USE_TOOL with tool_name="shadow_council"
  * User mentions "Forum of Echoes" or needs philosophical perspectives → USE_TOOL with tool_name="forum_of_echoes"
  * User needs calculations → USE_TOOL with tool_name="calculator"
  * User needs date/time → USE_TOOL with tool_name="datetime"
- SEARCH_MEMORIES: Search user's stored memories
- CREATE_MEMORY: Store new information as a memory
- LIST_TASKS/CREATE_TASK: Manage user's tasks
- EXPLAIN: Provide direct explanation without tools
- DONE: Simple response is sufficient

DO NOT USE: ACTIVATE_SHADOW, ACTIVATE_DIALOGUE (these are legacy - use USE_TOOL instead)

Available tools:


Consider if any tools would enhance the response, especially for:
- Technical/architectural questions → Shadow Council
- Philosophical/ethical questions → Forum of Echoes
- Complex analysis requiring multiple perspectives

Provide clear reasoning about what should be done and why.
```

**Max Tokens**: 1000 (from settings.OPENAI_MAX_TOKENS_REASONING)

### Expected LLM Response
Plain text reasoning like:
```
The user is asking for help designing a blockchain protocol for distributed identity and explicitly requests the Shadow Council. This is a technical/architectural question that requires expert analysis. I should USE_TOOL with the shadow_council to provide comprehensive technical guidance on blockchain protocol design, focusing on distributed identity management aspects.
```

---

## Phase 3: Action Planning (13:25:39 - 13:26:44) - 65 seconds!

### Prompt Assembly
**File**: `/home/lewis/dev/personal/mnemosyne/backend/app/services/agentic/flow_controller.py` lines 214-226

#### Step 1: Load prompt (line 215)
- Tries to load `/app/backend/app/prompts/agentic_planning.txt`
- Doesn't exist
- Falls back to default at lines 526-559

#### Step 2: Default planning prompt
```python
defaults["agentic_planning"] = """
Based on this reasoning: {reasoning}

CRITICAL - Use ONLY these actions (NOT ACTIVATE_SHADOW or ACTIVATE_DIALOGUE):
- USE_TOOL: Execute tools (parameters: tool_name, query, parameters)
  * For Shadow Council: tool_name="shadow_council"
  * For Forum of Echoes: tool_name="forum_of_echoes"
- SEARCH_MEMORIES: Find relevant memories (parameters: query, limit)
- CREATE_MEMORY: Store information (parameters: content, type, tags)
- LIST_TASKS: Get user tasks (parameters: status, limit)
- EXPLAIN: Direct response (parameters: none)
- DONE: Complete (parameters: none)

NEVER USE: ACTIVATE_SHADOW, ACTIVATE_DIALOGUE (deprecated - use USE_TOOL)

Available tools for USE_TOOL action:
[TOOL LIST WOULD BE HERE BUT FAILS]

Create a specific action plan as a JSON array. Each action should have:
- action: the action name (e.g., "USE_TOOL", "SEARCH_MEMORIES")
- parameters: any parameters needed (for USE_TOOL: tool_name, query)
- reasoning: why this action is needed
- confidence: confidence score 0-1

Example for using Shadow Council (EXACT format required):
[{"action": "USE_TOOL", "parameters": {"tool_name": "shadow_council", "query": "design a blockchain protocol", "parameters": {}}, "reasoning": "User needs technical expertise", "confidence": 0.9}]

Example for using Forum of Echoes (EXACT format required):
[{"action": "USE_TOOL", "parameters": {"tool_name": "forum_of_echoes", "query": "what is the meaning of life", "parameters": {}}, "reasoning": "User needs philosophical perspectives", "confidence": 0.9}]

IMPORTANT: Always use exact parameter names: tool_name (NOT tool), query (NOT input)

Return ONLY valid JSON array, no other text.
"""
```

### ACTUAL PROMPT SENT TO LLM
```
System: Convert reasoning into a specific action plan. Return JSON array of actions.

User: Based on this reasoning: [REASONING FROM PHASE 2]

CRITICAL - Use ONLY these actions (NOT ACTIVATE_SHADOW or ACTIVATE_DIALOGUE):
- USE_TOOL: Execute tools (parameters: tool_name, query, parameters)
  * For Shadow Council: tool_name="shadow_council"
  * For Forum of Echoes: tool_name="forum_of_echoes"
- SEARCH_MEMORIES: Find relevant memories (parameters: query, limit)
- CREATE_MEMORY: Store information (parameters: content, type, tags)
- LIST_TASKS: Get user tasks (parameters: status, limit)
- EXPLAIN: Direct response (parameters: none)
- DONE: Complete (parameters: none)

NEVER USE: ACTIVATE_SHADOW, ACTIVATE_DIALOGUE (deprecated - use USE_TOOL)

Available tools for USE_TOOL action:


Create a specific action plan as a JSON array. Each action should have:
- action: the action name (e.g., "USE_TOOL", "SEARCH_MEMORIES")
- parameters: any parameters needed (for USE_TOOL: tool_name, query)
- reasoning: why this action is needed
- confidence: confidence score 0-1

Example for using Shadow Council (EXACT format required):
[{"action": "USE_TOOL", "parameters": {"tool_name": "shadow_council", "query": "design a blockchain protocol", "parameters": {}}, "reasoning": "User needs technical expertise", "confidence": 0.9}]

Example for using Forum of Echoes (EXACT format required):
[{"action": "USE_TOOL", "parameters": {"tool_name": "forum_of_echoes", "query": "what is the meaning of life", "parameters": {}}, "reasoning": "User needs philosophical perspectives", "confidence": 0.9}]

IMPORTANT: Always use exact parameter names: tool_name (NOT tool), query (NOT input)

Return ONLY valid JSON array, no other text.
```

### Expected LLM Response
```json
[{"action": "USE_TOOL", "parameters": {"tool_name": "shadow_council", "query": "I need help designing a blockchain protocol for distributed identity", "parameters": {}}, "reasoning": "User explicitly requested Shadow Council for technical blockchain architecture guidance", "confidence": 0.95}]
```

---

## Problems Identified

### 1. Tool Registry Not Loading in Prompts
The prompts try to include available tools but `tool_registry.get_tool_metadata()` fails, leaving "Available tools:" empty.

### 2. InnoGPT-1 Response Format Issues
- Returns `reasoning_content` instead of `content` (we fixed this)
- May not be returning proper JSON for action planning
- 65 seconds for action planning is suspiciously long

### 3. JSON Parsing Failures
- Line 230 in flow_controller.py: `json.loads(response.get("content", "[]"))`
- If this fails, returns empty array `[]`
- No error logging when JSON parsing fails

### 4. Missing Prompt Files
All prompt files are missing, falling back to hardcoded defaults which may not be optimal for the model.

### 5. Persona Selection Bug
The code has a bug where it calls non-existent `select_mode()` method but somehow still works.

---

## What SHOULD Happen

1. **Reasoning Phase**: Should take <5 seconds for a reasoning model with 40+ TPS
2. **Action Planning**: Should take <5 seconds and return proper JSON
3. **Action Execution**: Should execute the Shadow Council tool
4. **Response**: Shadow Council should provide multi-agent technical analysis

The total flow should complete in 10-20 seconds, not 97 seconds.