# Philosophical Multi-Agent Debate System Architecture

## System Overview

The Philosophical Multi-Agent Debate System orchestrates structured debates between multiple AI agents, each representing a distinct philosophical tradition. The system processes user prompts through a sequence of **Opening Statement**, **Rebuttal**, and **Judging** phases, with explicit debate framing, agent/judge roles, and transparency for all moves.

> **Note:** Agents are loaded dynamically from definition files in `agent_definitions/` at runtime, using `agent_loader.py`. There are 56 different philosophical perspectives defined in the system message files that could be integrated. The architecture is designed for easy expansion and extensibility.

## Agent Layout

### Core Components

1. **Main Entry Point**
   - `main.py` - Accepts user input prompt and passes it to the OrchestratorAgent

2. **Orchestrator** (Central Controller)
   - `OrchestratorDynamic` (`orchestrator_dynamic.py`) loads all agent definitions dynamically and coordinates the debate flow.
   - Manages the entire debate flow, including phase transitions, agent/judge selection, and state tracking
   - Logs all debate moves and token usage

3. **Philosophical Agents**
   - Agents are loaded dynamically from `agent_definitions/` using `agent_loader.py`
   - Each represents a different philosophical perspective
     - UtilitarianAgent (Utilitarianism)
     - ExistentialistAgent (Existentialism)
     - EmpiricistAgent (Empiricism)
     - RationalistAgent (Rationalism)
     - PragmatistAgent (Pragmatism)
     - AnalyticAgent (Analytic Philosophy)
     - ContinentalAgent (Continental Philosophy)
     - EasternAgent (Eastern Philosophy)
     - MoralAgent (Moral Philosophy)
   - All inherit from BaseAgent
   - Participate in Opening Statement and Rebuttal phases, always aware they are debating against others

4. **Judge Agents & Quorum Logic**
   - `JudgeAgent` class (planned)
   - Each judge has a distinct judging style (e.g., logical rigor, ethical impact, originality)
   - Judges analyze agent self-summaries and debate transcript, vote for the best case, and provide rationale
   - Quorum logic: if 2+ judges agree, that agent wins; otherwise, results are shown as a tie
   - All judgments and rationales are logged and included in the transcript

5. **Token Usage Tracker**
   - Tracks and reports token usage per agent, phase, and debate
   - Supports summary/short mode for reduced token consumption

6. **Transcript Output & Extensibility**
   - All debate moves, rationales, and results are logged for transparency
   - Designed for easy extension (additional rounds, agent/judge config, persistent learning)


## Flow Diagram

```
┌─────────────────┐
│                 │
│  User Prompt    │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│                 │
│    main.py      │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│                                         │
│          OrchestratorAgent              │
│                                         │
└┬────────────┬─────────────┬─────────────┘
 │            │             │
 │            │             │
 ▼            ▼             ▼
┌────────┐ ┌────────┐  ┌────────────┐
│Phase 1:│ │Phase 2:│  │ Phase 3:   │
│Analysis│ │Critique│  │ Synthesis  │
└────┬───┘ └───┬────┘  └─────┬──────┘
     │         │             │
     ▼         ▼             ▼
┌────────────────────────────────────────────┐
│                                            │
│             10 Philosophical Agents         │
│                                            │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌─────┐  │
│  │Stoic   │ │Utilit- │ │Existen-│ │...  │  │
│  │Agent   │ │arian   │ │tialist │ │     │  │
│  └────────┘ └────────┘ └────────┘ └─────┘  │
│                                            │
└────────┬─────────────────────┬─────────────┘
         │                     │
         │                     │
         ▼                     │
┌─────────────────┐            │
│                 │            │
│ SynthesisAgent  │            │
│                 │            │
└────────┬────────┘            │
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│                 │   │                 │
│ Debate Summary  │   │  debate_history │
│                 │   │     .jsonl      │
└─────────────────┘   └─────────────────┘
```

## Process Flow in Detail

1. **Input Stage**: 
   - User enters a philosophical prompt in `main.py`
   - Prompt is passed to `OrchestratorAgent.run()`

2. **Analysis Phase**:
   - Each of the 10 philosophical agents processes the prompt
   - Agents call OpenAI API via `call_openai()` function with agent-specific system prompts
   - Each agent produces an analysis from its philosophical perspective
   - Results are displayed individually: `Agent (Philosophy): [Analysis]`

3. **Critique Phase**:
   - Each agent reviews and critiques all other agents' responses
   - 90 total critiques (10 agents critiquing 9 other agents each)
   - Each agent uses its philosophical lens to critique others
   - Results are displayed as: `Agent1 critiques Agent2: [Critique]`

4. **Synthesis Phase**:
   - The SynthesisAgent compiles all initial agent responses
   - Creates a comprehensive summary attributing each perspective to its agent
   - Displays the final debate summary

5. **Logging**:
   - Debate history saved to `debate_history.jsonl` file
   - Each entry includes prompt, all agent responses, and summary

## Technical Implementation

### API Interface
Each agent uses the `call_openai()` function which:
- Gets LLM config (API key, base URL, model name, etc.)
- Initializes OpenAI client
- Sends system and user prompts
- Returns the response or error message
     
### Agent Structure
- Each agent inherits from BaseAgent
- They implement `analyze_prompt()` and `critique()` methods
- Each applies its philosophical perspective to the analysis/critique

### Configuration
- OpenAI API settings loaded from environment variables
- Configuration managed via `src/config/settings.py`

## File Structure

```
dialogues/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py             # Base agent class
│   │   ├── philosophical_agents.py  # All philosophical agents
│   │   ├── orchestrator.py     # Orchestrator agent
│   │   └── synthesis.py        # Synthesis agent
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration settings
│   ├── debate/
│   │   ├── __init__.py
│   │   ├── analyzer.py         # Debate analysis
│   │   └── manager.py          # Debate management
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   └── ui/
│       └── __init__.py         # UI components (future)
├── setup.py                    # Package setup
├── requirements.txt            # Dependencies
├── Dockerfile                  # Docker configuration
└── docs/
    └── agent_architecture.md   # This document
```
