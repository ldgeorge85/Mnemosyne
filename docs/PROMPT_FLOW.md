# Mnemosyne Prompt Flow Architecture
*Last Updated: August 27, 2025*
*Status: Phase 1.A COMPLETE*

## Overview
The agentic flow uses a ReAct (Reasoning + Acting) pattern with multiple decision points.

## Flow Sequence

### 1. User Message Arrives
- Endpoint: `/api/v1/chat/agentic/stream`
- Initial context includes: user query, conversation history, user profile

### 2. Persona Selection (First Decision)
- **Prompt**: `agentic_persona_selection.txt`
- **LLM analyzes**: Query content, emotional indicators, task type
- **Output**: Selected persona mode (Confidant/Mentor/Mediator/Guardian/Mirror)
- **Confidence**: Target >80% (currently achieving 92%)

### 3. Action Planning
- **Prompt**: `agentic_planning.txt`  
- **LLM determines**: What actions needed (memory search, task creation, etc.)
- **Output**: List of actions with parameters
- **Execution**: Actions run in parallel via `asyncio.gather()`

### 4. Reasoning & Reflection
- **Prompt**: `agentic_reasoning.txt`
- **LLM reflects**: On action results and determines meaning
- **Output**: Synthesized understanding of results

### 5. More Information Check
- **Prompt**: `agentic_needs_more.txt`
- **LLM decides**: If additional actions needed
- **Output**: Boolean (yes/no) with reasoning
- **If yes**: Loop back to Action Planning (max 3 iterations)

### 6. Response Generation
- **System Prompt**: Persona-specific prompt based on selected mode
- **Temperature**: Currently 0.7 (hardcoded)
- **Output**: Final response to user

### 7. Proactive Suggestions
- **Prompt**: `agentic_suggestions.txt`
- **LLM suggests**: 3 relevant next actions
- **Output**: Array of suggestions with rationale

## Current Configuration

### Temperature Settings
- **Variable Mode Active**: Per-persona temperatures implemented
  - Confidant: 0.8 (empathetic)
  - Mentor: 0.6 (instructive)
  - Mediator: 0.5 (balanced)
  - Guardian: 0.3 (protective)
  - Mirror: 0.9 (creative)
- **Static Mode Available**: Can use fixed temperature from env
- **Configurable via**: `LLM_TEMPERATURE_MODE` env variable

### Model Support
- Primary: OpenAI GPT-4/3.5 or compatible
- Configurable base URL for any OpenAI-compatible endpoint
- Reasoning level support via `LLM_SUPPORTS_REASONING_LEVEL`
- Model profiles: standard, reasoning_channel, embedded_system, deepseek

### Conversation Handling
- **First message**: Full system prompt + persona context
- **Subsequent messages**: Smart truncation to fit context window
- **System prompt**: Flexible modes (separate or embedded)
- **Context window**: 64k tokens supported with intelligent truncation
- **Token limits**: 
  - Context: 64k (configurable via VITE_MAX_CONTEXT_TOKENS)
  - Response: Unlimited (no max_tokens for final responses)
  - Reasoning: 1000 tokens (for decision prompts)

## Prompt Files Location
```
backend/app/prompts/
├── agentic_persona_selection.txt
├── agentic_reasoning.txt
├── agentic_planning.txt
├── agentic_needs_more.txt
├── agentic_suggestions.txt
└── personas/
    ├── confidant.txt
    ├── mentor.txt
    ├── mediator.txt
    ├── guardian.txt
    └── mirror.txt
```

## Key Design Decisions

1. **LLM-First**: Every decision goes through LLM reasoning (no hardcoded rules)
2. **Parallel Execution**: Actions execute simultaneously for speed
3. **Transparent Reasoning**: All decisions logged (receipts infrastructure ready)
4. **User Override**: Manual persona selection available via UI toggle
5. **Stateless**: Each request independent (no session state beyond conversation)

## Recently Completed Enhancements

1. **Temperature Control** ✅: 
   - Per-persona temperature configs implemented
   - Support for reasoning level in system prompts
   - Variable/static modes configurable

2. **Context Management** ✅:
   - Smart truncation for long conversations
   - 64k context window support
   - Preserves most recent messages when truncating

3. **Model-Specific Optimizations** ✅:
   - Flexible system prompt modes (embedded/separate)
   - Model profile support for different architectures
   - Configurable reasoning levels

## Next Priorities (Phase 1.B)

1. **Agent Integration**:
   - Connect Shadow agents (Engineer, Librarian, Priest)
   - Wire up Dialogue agents (50+ philosophical)
   - Multi-agent collaboration

2. **Action Expansion**:
   - Wire CREATE_MEMORY to executor
   - Wire UPDATE_TASK to executor
   - Implement DECOMPOSE_TASK
   - Model-aware prompt formatting