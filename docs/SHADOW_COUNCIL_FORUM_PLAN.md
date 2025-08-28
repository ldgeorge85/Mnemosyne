# Shadow Council & Forum of Echoes Implementation Plan
*Last Updated: August 27, 2025*

## Overview

Instead of porting each agent as an individual tool, we'll create two unified tools that orchestrate their respective sub-agents. This maintains cleaner architecture while preserving the rich multi-agent dynamics.

## Architecture Design

```
Tool Registry
    ├── Shadow Council Tool (single registration)
    │   └── Sub-agents (internal orchestration)
    │       ├── Artificer (technical expertise)
    │       ├── Archivist (knowledge management)
    │       ├── Mystagogue (pattern recognition)
    │       ├── Tactician (strategic planning)
    │       └── Daemon (devil's advocate)
    └── Forum of Echoes Tool (single registration)
        └── Voices (internal selection)
            ├── Stoic
            ├── Pragmatist
            ├── Idealist
            ├── Skeptic
            └── [50+ philosophical perspectives]
```

## Shadow Council Tool

### Purpose
A unified tool that provides technical, strategic, and analytical expertise through specialized sub-agents.

### Interface
```python
class ShadowCouncilTool(BaseTool):
    """Shadow Council - Technical and strategic expertise"""
    
    def _get_default_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="shadow_council",
            display_name="Shadow Council",
            description="Consult technical and strategic experts",
            category=ToolCategory.AGENT,
            capabilities=[
                "technical analysis",
                "knowledge synthesis", 
                "pattern recognition",
                "strategic planning",
                "critical evaluation"
            ],
            tags=["agents", "technical", "strategic", "analysis"]
        )
    
    async def execute(self, input: ToolInput) -> ToolOutput:
        # Determine which council member(s) to activate
        members = await self._select_members(input.query)
        
        # Get responses from selected members
        responses = await self._consult_members(members, input)
        
        # Synthesize into unified response
        synthesis = await self._synthesize_responses(responses)
        
        return ToolOutput(
            success=True,
            result=synthesis,
            metadata={"members_consulted": members}
        )
```

### Council Members

#### Artificer (formerly Engineer)
- **Role**: Technical expertise and implementation guidance
- **Expertise**: Code architecture, system design, debugging, optimization
- **Personality**: Precise, methodical, solution-oriented
- **Activation**: Technical questions, implementation details, debugging

#### Archivist (formerly Librarian)
- **Role**: Knowledge management and information synthesis
- **Expertise**: Research, documentation, knowledge graphs, memory systems
- **Personality**: Thorough, organized, detail-oriented
- **Activation**: Research queries, documentation needs, knowledge retrieval

#### Mystagogue (formerly Priest)
- **Role**: Pattern recognition and deep insights
- **Expertise**: Hidden patterns, symbolic connections, emergent behaviors
- **Personality**: Intuitive, philosophical, pattern-seeking
- **Activation**: Complex patterns, behavioral analysis, systemic questions

#### Tactician (new)
- **Role**: Strategic planning and decision optimization
- **Expertise**: Strategy, resource allocation, risk assessment, planning
- **Personality**: Analytical, forward-thinking, pragmatic
- **Activation**: Planning queries, strategy questions, decision-making

#### Daemon (new)
- **Role**: Devil's advocate and critical analysis
- **Expertise**: Finding flaws, challenging assumptions, stress-testing ideas
- **Personality**: Skeptical, provocative, constructively critical
- **Activation**: Validation needs, assumption checking, robustness testing

## Forum of Echoes Tool

### Purpose
A unified tool that provides diverse philosophical perspectives and facilitates intellectual discourse.

### Interface
```python
class ForumOfEchoesTool(BaseTool):
    """Forum of Echoes - Philosophical perspectives and debate"""
    
    def _get_default_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="forum_of_echoes",
            display_name="Forum of Echoes",
            description="Engage with diverse philosophical perspectives",
            category=ToolCategory.AGENT,
            capabilities=[
                "philosophical inquiry",
                "ethical analysis",
                "multiple perspectives",
                "conceptual debate",
                "wisdom traditions"
            ],
            tags=["philosophy", "debate", "perspectives", "wisdom"]
        )
    
    async def execute(self, input: ToolInput) -> ToolOutput:
        # Select voices based on query
        voices = await self._select_voices(input.query)
        
        # Orchestrate discussion
        if len(voices) > 1:
            dialogue = await self._facilitate_dialogue(voices, input)
            result = self._format_dialogue(dialogue)
        else:
            response = await self._get_perspective(voices[0], input)
            result = response
        
        return ToolOutput(
            success=True,
            result=result,
            metadata={"voices": voices},
            display_format="markdown"
        )
```

### Initial Voices (Start with 10, expand to 50+)

1. **Stoic** - Marcus Aurelius inspired, focus on virtue and acceptance
2. **Pragmatist** - William James inspired, focus on practical outcomes
3. **Idealist** - Plato inspired, focus on perfect forms and ideals
4. **Skeptic** - Pyrrho inspired, questioning all assumptions
5. **Existentialist** - Sartre inspired, focus on freedom and responsibility
6. **Buddhist** - Nagarjuna inspired, focus on emptiness and compassion
7. **Confucian** - Focus on harmony and social order
8. **Taoist** - Lao Tzu inspired, focus on flow and natural way
9. **Humanist** - Focus on human dignity and potential
10. **Systems Thinker** - Focus on interconnections and emergence

## Implementation Phases

### Phase 1: Core Structure (Week 1)
- [ ] Create ShadowCouncilTool class
- [ ] Create ForumOfEchoesTool class
- [ ] Implement member/voice selection logic
- [ ] Build response synthesis mechanisms
- [ ] Register both tools with ToolRegistry

### Phase 2: Council Members (Week 2)
- [ ] Port Artificer from existing Engineer code
- [ ] Port Archivist from existing Librarian code
- [ ] Port Mystagogue from existing Priest code
- [ ] Implement new Tactician member
- [ ] Implement new Daemon member

### Phase 3: Forum Voices (Week 2)
- [ ] Implement 10 initial philosophical voices
- [ ] Create dialogue orchestration logic
- [ ] Build perspective selection algorithm
- [ ] Add debate facilitation features

### Phase 4: Integration (Week 2)
- [ ] Connect to agentic flow
- [ ] Add UI components for tool selection
- [ ] Implement streaming responses
- [ ] Create tool-specific output formatting

## Usage Examples

### Shadow Council Examples
```python
# Technical question - activates Artificer
"How should I architect a distributed cache system?"

# Research question - activates Archivist
"What are the historical precedents for cognitive sovereignty?"

# Pattern analysis - activates Mystagogue
"What patterns emerge in my task completion behavior?"

# Strategic planning - activates Tactician
"How should I prioritize these competing objectives?"

# Validation - activates Daemon
"What are the potential flaws in this approach?"

# Complex question - activates multiple members
"Design a secure, scalable authentication system with privacy preservation"
# → Artificer (technical), Tactician (strategy), Daemon (security critique)
```

### Forum of Echoes Examples
```python
# Single perspective
"What would a Stoic say about dealing with failure?"

# Multiple perspectives
"How should we balance individual freedom with collective good?"
# → Triggers debate between Libertarian, Communitarian, and Humanist voices

# Philosophical inquiry
"What is the nature of consciousness?"
# → Activates relevant philosophical traditions

# Ethical dilemma
"Is it ethical to create AGI?"
# → Multi-voice discussion with different ethical frameworks
```

## Benefits of Unified Approach

1. **Cleaner Architecture**: Two tools instead of dozens
2. **Better Orchestration**: Internal logic for member/voice selection
3. **Richer Interactions**: Members can consult each other
4. **Easier Management**: Single entry point for each system
5. **Flexible Composition**: Can add new members/voices without new tool registrations
6. **Consistent Interface**: Users interact with councils, not individuals

## Next Steps

1. Complete Phase 1.B Week 1 infrastructure
2. Build ShadowCouncilTool with simplified member stubs
3. Build ForumOfEchoesTool with 2-3 initial voices
4. Test integration with existing tool system
5. Gradually port existing agent code
6. Expand voices and capabilities over time