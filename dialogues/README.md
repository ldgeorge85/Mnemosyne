# Philosophical Multi-Agent Debate System

A Python-based multi-agent system that simulates philosophical debates between AI agents representing different philosophical traditions. This system leverages the Autogen framework to create a rich, interactive dialogue between philosophical archetypes.

## Project Overview

This project creates a multi-agent AI system where each agent embodies a distinct philosophical archetype (e.g., Stoic, Utilitarian, Existentialist, etc.). Each agent:
- Analyzes user prompts from its archetype’s perspective
- Critiques the analyses of other agents, highlighting philosophical strengths and disagreements
- Contributes to a debate summary, ensuring a rich, multi-perspective analysis for the user

When given a philosophical prompt or question by the user, the system:

1. Analyzes the prompt through different philosophical lenses
2. Facilitates a debate between philosophical agents loaded dynamically from `agent_definitions/` at runtime using `agent_loader.py`.
- The canonical orchestrator (`orchestrator_dynamic.py`) implements the full debate protocol: Opening Statement, Rebuttal, and Judging (with judge agents and quorum voting).
- Dynamic agents support `opening_statement` and `rebuttal` methods for new debate phases, falling back to legacy methods for compatibility. Agent definitions can include explicit prompts for these phases.
3. Synthesizes diverse viewpoints into a coherent response
4. Returns a summarized view of multiple philosophical perspectives

## Philosophical Perspectives

The system implements agents representing various philosophical traditions, which are loaded dynamically from `agent_definitions/` at runtime.

## System Architecture

The architecture consists of several key components:

- **OrchestratorDynamic (orchestrator_dynamic.py)**: Loads all agent definitions dynamically and coordinates the debate flow.
- **Philosophical Agents**: Multiple agents representing different philosophical traditions, loaded dynamically from agent_definitions/ at runtime.
- **Analysis Engine**: Breaks down prompts into philosophical components
- **Debate Manager**: Facilitates structured interactions between agents
- **Synthesis Agent**: Summarizes the debate into a coherent response

## Project Structure

```
├── .env.example               # Example environment config for LLM settings
dialogues/
├── docs/                      # Documentation
│   ├── source_of_truth.md     # Project overview and file tracking
│   ├── implementation_plan.md # Detailed implementation plan
│   └── agent_specifications.md # Specifications for philosophical agents
├── src/                       # Source code (to be implemented)
│   ├── agents/                # Agent implementations
│   ├── debate/                # Debate management
│   ├── src/config/__init__.py         # Config package init
src/config/settings.py         # Loads LLM and system settings
│   ├── ui/                    # User interface
│   └── main.py                # Entry point
├── requirements.txt           # Project dependencies (to be implemented)
└── README.md                  # This file
```

## Getting Started

*Note: Implementation in progress. This section will be updated as the project develops.*

### Prerequisites

- Python 3.9+
- Autogen
- OpenAI API key or other LLM access

### Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your API keys in a `.env` file
4. Run the application: `python src/main.py`

## LLM Configuration

The system uses the OpenAI API for agent reasoning. You must provide configuration for:
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_BASE_URL`: API endpoint (default: https://api.openai.com/v1)
- `OPENAI_MODEL_NAME`: Model name (default: gpt-3.5-turbo)
- `OPENAI_TEMPERATURE`: Sampling temperature (default: 0.7)
- `OPENAI_MAX_TOKENS`: Max tokens for each response (default: 512)

You can set these as environment variables or in a `.env` file (see `.env.example`).

### Docker Compose Usage

Edit your `.env` file or export variables before running:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

docker compose up --build
```

## Usage

*Coming soon: Examples of usage and sample prompts*

## Implementation Plan

See [Implementation Plan](docs/implementation_plan.md) for a detailed breakdown of the development phases and timeline.

## Agent Specifications

See [Agent Specifications](docs/agent_specifications.md) for detailed descriptions of each agent, their philosophical traditions, and implementation guidelines.

## License

*Coming soon*

## Acknowledgments

- This project is inspired by philosophical dialogue traditions across cultures and histories
- Built using the Autogen multi-agent framework
