# Philosophical Multi-Agent Debate System - Implementation Plan

## Debate-Oriented Agent Structure
The system is implemented in Python using the Autogen framework. Agents are loaded dynamically at runtime from agent definition files in agent_definitions/, using agent_loader.py. Each agent definition specifies its archetype, reasoning, and debate style. The debate protocol is structured into:
- **Opening Statement**: Each agent presents its stance on the topic, from its philosophical perspective.
- **Rebuttal**: Each agent rebuts the opening statements of the others, explicitly engaging in debate.
- **Judging**: Each agent summarizes its own performance, and a set of judge agents analyze all summaries, providing votes and rationale. A quorum system determines the winner.

Agents are always aware they are debating their stance against others, and prompts are wrapped to clarify the phase and expectations.

This structure ensures the codebase reflects a debate-first conceptual model, with extensibility for additional rounds, agent/judge customization, and advanced analysis.

## 1. System Overview

The Philosophical Multi-Agent Debate System facilitates structured debates between AI agents representing different philosophical traditions. Users submit prompts or questions, which are then debated through explicit phases (Opening Statement, Rebuttal, Judging), with all agent and judge actions logged for transparency. The system is designed for extensibility, allowing future addition of deeper rounds, agent/judge selection, and transcript output.

## 2. System Architecture

### Core Components:

1. **User Interface**: 
   - CLI (initial), with future web interface planned
   - Collects user prompts and displays debate results and transcripts

2. **Orchestrator Agent (orchestrator_dynamic.py)**: 
   - Central controller for the debate
   - Manages debate flow, agent/judge selection, and state tracking

3. **Philosophical Agents**: 
   - Multiple agents with distinct philosophical perspectives, loaded dynamically from agent definition files in agent_definitions/
   - Each agent debates its stance in Opening Statement and Rebuttal phases
   - Maintains internal consistency with its tradition

4. **Debate Manager**: 
   - Facilitates structured debate protocols (Opening → Rebuttal → Judging)
   - Manages turn-taking, response collection, and phase transitions
   - Logs all debate moves for transparency and traceability

5. **Judge Agents & Quorum Logic**: 
   - Specialized judge agents analyze agent summaries
   - Each judge votes for the agent with the strongest overall case, with rationale
   - Quorum logic: if 2+ judges agree, that agent wins; otherwise, results are shown as a tie
   - Judges may have different judging styles (logical rigor, ethical impact, originality, etc.)

6. **Token Usage Tracker**:
   - Tracks and reports token usage per agent, phase, and debate
   - Supports summary/short mode for reduced token consumption

### Data Flow:

```
User Input → Orchestrator → Philosophical Agents (Opening Statement) → Philosophical Agents (Rebuttal) → Judge Agents (Judging) → Quorum Logic → Transcript & Results to User
```

## 3. Agent Definitions

### Agent Types and Responsibilities:

1. **Orchestrator Agent**:
   - Receives and validates user input
   - Schedules and manages debate phases and agent/judge selection
   - Tracks debate state and logs all moves
   - Calls for judging and quorum logic when debate concludes
   - Returns final results and transcript to the user interface

2. **Philosophical Agents**:
   - Defined philosophical tradition/stance
   - Key principles and methods
   - Notable philosophers
   - Specialized prompting for debate context
   - Participate in Opening Statement and Rebuttal phases

3. **Judge Agents**:
   - Distinct judging styles (logical rigor, ethical impact, originality, etc.)
   - Analyze agent summaries and debate transcript
   - Vote for the strongest case and provide rationale
   - Quorum logic determines the winner

4. **Token Usage Tracker**:
   - Monitors token usage per agent and phase
   - Reports to user and logs for transparency
   - Supports summary/short mode for efficiency

5. **Extensibility Hooks**:
   - Easy addition of further debate rounds (e.g., Surrebuttal)
   - User/judge agent selection
   - Transcript and metrics output
   - Persistent agent learning (future extension)

## 4. Implementation Phases

**Note:** All phases and acceptance criteria use the new debate structure and terminology. Extension points and token tracking are included.

### Phase 1: Setup and Basic Framework (Week 1)

1. **Project Initialization**:
   - Set up project directory structure
   - Create virtual environment
   - Initialize git repository
   - Create initial documentation

2. **Dependency Installation**:
   - Install Autogen
   - Install OpenAI API library or alternative LLM access
   - Set up configuration management
   - Install additional libraries as needed

3. **Base Agent Implementation**:
   - Create abstract base agent class
   - Implement basic communication patterns
   - Set up message passing infrastructure
   - Create simple memory/context management

4. **Simple Orchestrator Implementation**:
   - Implement basic conversation flow
   - Create agent registration system
   - Set up simple CLI interface
   - Implement basic logging

### Phase 2: Philosophical Agent Implementation (Week 2)

1. **Agent Persona Definition**:
   - Research and define philosophical stances
   - Create detailed agent specifications
   - Design persona-specific prompting
   - Implement philosophical consistency mechanisms

2. **Prompt Analysis Capabilities**:
   - Implement topic extraction
   - Create philosophical concept identification
   - Build theme categorization
   - Develop question framing mechanisms

3. **Agent Specialization**:
   - Create specialized philosophical agents
   - Implement tradition-specific reasoning
   - Develop philosophical principle application
   - Create historical philosopher references

4. **Initial Critique Mechanisms**:
   - Implement position comparison
   - Create argument identification
   - Develop fallacy detection
   - Build philosophical assumption recognition

### Phase 3: Orchestration and Debate Management (Week 3)

1. **Full Conversation Flow**:
   - Implement multi-turn conversations
   - Create dynamic agent selection
   - Build topic threading
   - Develop conversation branching

2. **Advanced Debate Management**:
   - Implement structured debate protocols
   - Create topic-based agent grouping
   - Develop position tracking
   - Build argument mapping

3. **Turn-Taking and Response Management**:
   - Implement controlled agent activation
   - Create response prioritization
   - Develop relevance scoring
   - Build conversation pacing

4. **Basic Judging Capabilities**:
   - Implement agent self-summary (each agent summarizes its own opening and rebuttals)
   - Implement judge agents to analyze all summaries and vote with rationale
   - Develop quorum logic for winner selection
   - Log all judging moves and rationales
   - Aggregate and present results and transcript to user

### Phase 4: Refinement and Enhancement (Week 4)

1. **Debate Quality Improvement**:
   - Refine agent prompts
   - Enhance philosophical accuracy
   - Improve argument quality
   - Develop nuance recognition

2. **Memory and Context Management**:
   - Implement persistent memory
   - Create cross-reference capabilities
   - Develop historical tracking
   - Build conversation memory

3. **Visualization Development**:
   - Create argument mapping visualization
   - Implement position clustering
   - Develop philosophical relation graphs
   - Build debate progression visualization

4. **Evaluation Mechanisms**:
   - Create philosophical accuracy metrics
   - Implement coherence evaluation
   - Develop diversity measurement
   - Build user satisfaction tracking

### Phase 5: User Interface and Deployment (Week 5)

1. **Enhanced User Interface**:
   - Develop CLI refinements
   - Create web interface prototype
   - Implement response formatting
   - Build interaction feedback mechanisms

2. **Configuration and Customization**:
   - Implement agent selection interface
   - Create debate configuration options
   - Develop philosophical emphasis controls
   - Build verbosity/conciseness settings

3. **History and Export Features**:
   - Implement conversation saving
   - Create export to various formats
   - Develop conversation resumption
   - Build debate archiving

4. **Documentation and Examples**:
   - Create user documentation
   - Develop API documentation
   - Build usage examples
   - Create philosophical topic suggestions

## 5. Technical Specifications

- All phases and modules are designed for extensibility (additional rounds, agent/judge config, transcript output).
- Token usage is tracked and reported per agent, phase, and debate.
- All results, moves, and judge rationales are logged for transparency.

### Dependencies:

```
autogen>=0.2.0
openai>=1.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
rich>=10.0.0
typer>=0.9.0
```

### Key Implementation Details:

1. **Debate Phases**:
   - Opening Statement: Each agent presents its stance
   - Rebuttal: Each agent rebuts others’ opening statements
   - Judging: Each agent summarizes its performance; judge agents analyze, vote, and quorum logic determines the winner

2. **Agent Communication**:
   - Based on Autogen's agent-to-agent protocols
   - Structured message passing and event tracking
   - All moves and rationales logged for transcript

3. **Token Usage Tracking**:
   - Track and report tokens per agent, phase, and debate
   - Option for summary/short mode

4. **Extensibility**:
   - Add further debate rounds, agent/judge types, and user configuration easily
   - Support for transcript output and persistent learning

5. **Evaluation Metrics**:
   - Philosophical coherence
   - Tradition accuracy
   - Argument quality
   - Response diversity
   - Token efficiency
   - Argument quality
   - Response diversity
   - User engagement

## 6. Future Extensions

- Deeper debate rounds (e.g., Surrebuttal, Cross-Examination)
- User/judge agent selection and configuration
- Transcript and metrics output for user review
- Persistent agent learning and adaptation
- Token usage optimization and reporting
- Visualizations for debate structure and agent arguments

1. **Enhanced Agent Learning**:
   - Allow agents to evolve positions based on debates
   - Implement philosophical position refinement
   - Create argument effectiveness learning
   - Develop adaptive philosophical reasoning

2. **Historical Context**:
   - Add historical progression of philosophical ideas
   - Implement era-specific philosophical understanding
   - Create historical influence tracking
   - Develop philosophical genealogy

3. **Interactive Debate Participation**:
   - Allow user to join ongoing debates
   - Create user position analysis
   - Implement user argument evaluation
   - Build personalized philosophical guidance

4. **Visual Representation**:
   - Create interactive argument maps
   - Implement philosophical position spaces
   - Develop conceptual relationship visualization
   - Build intellectual history timelines

5. **Multi-topic Analysis**:
   - Implement related topic identification
   - Create thematic linking
   - Develop cross-domain philosophical application
   - Build comprehensive worldview construction

## 7. Evaluation and Testing

1. **Philosophical Accuracy**:
   - Expert review of agent responses
   - Consistency with philosophical traditions
   - Proper attribution and representation
   - Conceptual accuracy

2. **Debate Quality**:
   - Argument coherence and soundness
   - Logical progression
   - Charitable interpretation
   - Productive disagreement

3. **User Experience**:
   - Clarity of responses
   - Educational value
   - Engagement metrics
   - Satisfaction surveys

4. **System Performance**:
   - Response time
   - Token efficiency
   - Scalability with multiple agents
   - API usage optimization

## 8. Risks and Mitigations

- Token overuse: Mitigated by summary/short mode, token tracking, and reporting
- Debate incoherence: Mitigated by structured protocols, logging, and judge agent rationale
- Philosophical misrepresentation: Mitigated by expert review, prompt engineering, and transparency


1. **Philosophical Misrepresentation**:
   - Risk: Agents may present inaccurate philosophical positions
   - Mitigation: Extensive research, expert review, continuous refinement

2. **Debate Incoherence**:
   - Risk: Agents talking past each other without productive engagement
   - Mitigation: Structured debate protocols, relevance checking, coherence evaluation

3. **Token Consumption**:
   - Risk: Multi-agent debates can consume large amounts of tokens
   - Mitigation: Efficient prompting, summarization of context, controlled debate length

4. **Bias in Synthesis**:
   - Risk: Synthesis agent may favor certain philosophical positions
   - Mitigation: Balanced representation requirements, diversity metrics, fairness evaluation
