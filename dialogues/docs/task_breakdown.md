# Project Task Breakdown: Philosophical Multi-Agent Debate System

This document provides a structured, updatable breakdown of all major tasks and subtasks for the project. Each task includes a description, acceptance criteria, and references to relevant documentation. Tasks and phases reflect the new debate structure: Opening Statement, Rebuttal, and Judging, with extensibility and transparency as core principles.

---

## Phase 1: Core Architecture

### 1. Repository & Environment Setup [Complete]
- **Description:** Initialize repo, set up Python environment, add dependency management files.
- **Acceptance Criteria:** Project structure matches `source_of_truth.md`. All dependencies install without errors.
- **References:** `README.md`, `docs/source_of_truth.md`

### 2. Agent Framework [Complete]
- **Description:** Implement base agent class and archetype-specific agents.
- **Acceptance Criteria:** Agents are loaded dynamically from definition files in agent_definitions/ at runtime, using agent_loader.py.
- **References:** `docs/agent_specifications.md`

### 3. Orchestrator & Debate Flow [Complete]
- **Description:** Create orchestrator to manage debate, prompt flow, and judging/summary generation.
- **Acceptance Criteria:** OrchestratorDynamic (orchestrator_dynamic.py) loads all agent definitions dynamically and coordinates the debate flow.
- **References:** `docs/implementation_plan.md`

---

## Phase 2: Debate Logic & Rebuttal [Complete]

### 1. Opening Statement Logic [Complete]
- **Description:** Implement logic for agents to generate opening statements in response to prompts.
- **Acceptance Criteria:** Agents generate archetype-consistent opening statements to sample prompts.

### 2. Rebuttal Logic [Complete]
- **Description:** Enable agents to rebut other agents’ opening statements, referencing them directly.
- **Acceptance Criteria:** Rebuttals highlight philosophical differences and reasoning quality.

### 3. Debate Transcript Output [Complete]
- **Description:** Implement transcript logging for all debate moves (opening, rebuttal, judging).
- **Acceptance Criteria:** User can view a full transcript of each debate round, including agent/judge rationales.

---

## Phase 3: Memory, Judging, and Evaluation

### 1. Persistent Memory [Complete]
- **Description:** Build persistent memory for conversation and agent state.
- **Acceptance Criteria:** System can recall past debates and agent context.
- **Implementation:** 
  - Created `MemoryManager` class to handle persistent storage of agent memories and debate history
  - Implemented `OrchestratorWithMemory` that enhances prompts with context from past debates
  - Added topic indexing and cross-referencing for related debates
  - Enabled agents to maintain philosophical consistency across multiple debates
  - Integrated with Docker for persistent storage outside the container
- **References:** `docs/persistent_memory.md`, `src/memory/memory_manager.py`

### 2. Judging Phase & Quorum Logic [In Progress]

#### [2025-06] Closing Statement Phase (New)
- **Description:** After the rebuttal phase and before summary, each agent now generates a "closing statement". This phase allows agents to respond to all rebuttals against them, restate their worldview, and summarize their final position.
- **Inputs:** Agent worldview (from definition), opening statement, all rebuttals received.
- **How it works:** Each agent receives a prompt constructed from their worldview, opening, and all rebuttals against them. The agent is instructed to provide a closing response addressing the main challenges raised.
- **Parallelism:** This phase is parallelized and can be configured with `PARALLEL_AGENTS_CLOSING` (or falls back to global parallelism config).
- **Acceptance Criteria:** Each agent's closing is included in the transcript and available to the summarizer and judges.
- **References:** See `orchestrator_dynamic.py` for implementation details.


#### [2025-06] Per-Phase Parallelism Control
- **Description:** The system now supports configuring the maximum number of parallel prompts separately for each debate phase (opening, rebuttal, summary, judging).
- **How to Configure:**
  - Set environment variables `PARALLEL_AGENTS_OPENING`, `PARALLEL_AGENTS_REBUTTAL`, `PARALLEL_AGENTS_SUMMARY`, `PARALLEL_AGENTS_JUDGING` to control parallelism for each phase.
  - If a phase-specific variable is not set, the global `PARALLEL_AGENTS` is used as fallback.
  - Example: To limit summary phase parallelism (due to LLM provider context/KV cache constraints), set `PARALLEL_AGENTS_SUMMARY=1`.
- **Motivation:** This prevents LLM context overflow when running multiple large prompts (such as summaries or judging) in parallel, while still allowing parallelism for smaller prompts.
- **References:** See orchestrator_dynamic.py for details.

- **Description:** Implement agent self-summaries, judge agents with distinct judging styles, and quorum logic for winner selection.
- **Acceptance Criteria:**
  - Each agent generates a summary of its opening statement and rebuttals.
  - Judge agents analyze all summaries and debate transcript, voting for the best overall case with rationale.
  - Quorum logic determines the winner and logs all judge rationales.
- **Implementation:**
  - Create `JudgeAgent` class with configurable judging styles (logical rigor, ethical impact, originality, etc.)
  - Implement quorum logic (majority wins; tie if no majority)
  - Output transcript and rationale for transparency
- **References:** `docs/implementation_plan.md`, `docs/agent_architecture.md`

### 3. Token Usage Tracking [In Progress]
- **Description:** Track and report token usage per agent, phase, and debate. Support summary/short mode for efficiency.
- **Acceptance Criteria:**
  - Token usage is logged and reported to the user after each debate.
  - Optionally enable summary mode for reduced token consumption.
- **Implementation:**
  - Integrate token usage tracker in OrchestratorDynamic (orchestrator_dynamic.py) and agent classes
  - Log usage in debate transcript and metrics output
- **References:** `docs/implementation_plan.md`, `src/metrics/debate_metrics.py`

### 4. Evaluation Metrics [Complete]
- **Description:** Develop metrics for philosophical accuracy, coherence, diversity, and user satisfaction.
- **Acceptance Criteria:** System can evaluate and display these metrics for each debate.
- **Implementation:**
  - Created `debate_metrics.py` module for calculating philosophical quality metrics:
    - Coherence: measures logical consistency and clarity
    - Diversity: evaluates representation of different philosophical viewpoints
    - Philosophical Depth: assesses sophistication and detail of arguments
    - Agent Consistency: tracks consistency of philosophical positions over time
  - Implemented `visualizers.py` with text-based visualizations:
    - Time-series charts showing metrics evolution across debates
    - Agent performance comparisons focusing on philosophical consistency
    - Topic diversity visualization showing the most diverse debate topics
  - Added `analyze_debates.sh` script for calculating and visualizing metrics
- **References:** `src/metrics/debate_metrics.py`, `src/metrics/visualizers.py`

---

## Phase 4: Visualization & Extensibility

### 1. Argument Mapping
- **Description:** Visualize debate structure and agent arguments.
- **Acceptance Criteria:** Users can see argument flow and relationships.

### 2. Position Clustering & Relation Graphs
- **Description:** Implement clustering and graph visualization of philosophical positions.
- **Acceptance Criteria:** Visualizations reflect agent similarities/differences.

### 3. Debate Progression Visualization
- **Description:** Show debate progression over time.
- **Acceptance Criteria:** Users can track debate stages and evolution.

---

## Phase 5: Design Considerations & Extension Points

### 1. Extensibility
- Support for additional debate rounds (e.g., Surrebuttal, Cross-Examination)
- User and judge agent selection and configuration
- Transcript and metrics output for user review
- Persistent agent learning and adaptation
- Token usage optimization and reporting
- Visualizations for debate structure and agent arguments

### 2. Transparency & Traceability
- All agent and judge moves, rationales, and quorum results are logged and available in the debate transcript
- Token usage and debate metrics are reported to the user
- System is designed for future expansion and easy integration of new features

---

## Phase 5: User Interface & Deployment

### 1. CLI & Web Interface
- **Description:** Develop command-line and web-based user interfaces.
- **Acceptance Criteria:** Users can interact with the system via CLI and web UI.

### 2. Configuration & Customization
- **Description:** Implement agent selection, debate configuration, and verbosity controls.
- **Acceptance Criteria:** Users can customize debates and agent participation.

### 3. History, Export, and Archiving
- **Description:** Enable saving, exporting, and resuming conversations.
- **Acceptance Criteria:** Users can export debates and resume previous sessions.

### 4. Documentation & Examples
- **Description:** Create user docs, API docs, usage examples, and topic suggestions.
- **Acceptance Criteria:** Documentation is clear, complete, and up-to-date.
- **References:** `README.md`, `docs/agent_specifications.md`, `docs/implementation_plan.md`

---

## Maintenance & Updates
- **Description:** Regularly update this breakdown as tasks are completed or requirements change.
- **Acceptance Criteria:** `docs/task_breakdown.md` and `docs/source_of_truth.md` remain accurate and current.

---

_Last updated: 2025-06-07_
