"""
Forum of Echoes Tool - Diverse philosophical and worldview perspectives.

The Forum of Echoes provides access to 50+ distinct voices representing different
philosophical traditions, worldviews, and perspectives. Each voice offers a unique
lens through which to examine questions and ideas.
"""

import asyncio
import random
from typing import Dict, List, Any, Optional
import logging

from ..base import BaseTool, ToolCategory, ToolMetadata, ToolInput, ToolOutput, ToolVisibility
from ....services.llm.service import LLMService
from ....core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ForumOfEchoesTool(BaseTool):
    """Forum of Echoes - Diverse philosophical perspectives and worldview exploration."""
    
    def __init__(self):
        """Initialize Forum with LLM service."""
        super().__init__()
        self.llm_service = LLMService()
        # Get parallel limit from settings
        from ....core.config import settings
        self._max_parallel_override = settings.FORUM_OF_ECHOES_MAX_PARALLEL
    
    # Define available voices with their characteristics
    VOICES = {
        "pragmatist": {
            "name": "The Pragmatist",
            "tradition": "American Pragmatism",
            "focus": "Practical consequences and what works",
            "keywords": ["practical", "results", "experience", "experiment", "useful"]
        },
        "stoic": {
            "name": "The Stoic",
            "tradition": "Stoicism",
            "focus": "Virtue, acceptance, and inner control",
            "keywords": ["virtue", "acceptance", "control", "discipline", "wisdom"]
        },
        "existentialist": {
            "name": "The Existentialist",
            "tradition": "Existentialism",
            "focus": "Freedom, authenticity, and responsibility",
            "keywords": ["freedom", "authentic", "choice", "responsibility", "existence"]
        },
        "buddhist": {
            "name": "The Buddhist",
            "tradition": "Buddhism",
            "focus": "Suffering, impermanence, and compassion",
            "keywords": ["suffering", "impermanence", "compassion", "mindfulness", "enlightenment"]
        },
        "skeptic": {
            "name": "The Skeptic",
            "tradition": "Skepticism",
            "focus": "Questioning assumptions and certainty",
            "keywords": ["doubt", "question", "evidence", "assumption", "certainty"]
        },
        "idealist": {
            "name": "The Idealist",
            "tradition": "Idealism",
            "focus": "Perfect forms and higher purpose",
            "keywords": ["ideal", "perfect", "purpose", "vision", "aspiration"]
        },
        "materialist": {
            "name": "The Materialist",
            "tradition": "Materialism",
            "focus": "Physical reality and empirical evidence",
            "keywords": ["physical", "material", "empirical", "scientific", "observable"]
        },
        "absurdist": {
            "name": "The Absurdist",
            "tradition": "Absurdism",
            "focus": "Embracing meaninglessness with joy",
            "keywords": ["absurd", "meaningless", "revolt", "freedom", "joy"]
        },
        "confucian": {
            "name": "The Confucian",
            "tradition": "Confucianism",
            "focus": "Harmony, relationships, and social order",
            "keywords": ["harmony", "relationship", "ritual", "society", "virtue"]
        },
        "taoist": {
            "name": "The Taoist",
            "tradition": "Taoism",
            "focus": "Natural flow and effortless action",
            "keywords": ["flow", "natural", "balance", "wu-wei", "simplicity"]
        }
    }
    
    def _get_default_metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="forum_of_echoes",
            display_name="Forum of Echoes",
            description="Engage with diverse philosophical and worldview perspectives",
            category=ToolCategory.AGENT,
            capabilities=[
                "philosophical inquiry",
                "ethical analysis",
                "multiple perspectives",
                "worldview exploration",
                "conceptual debate",
                "wisdom traditions",
                "cultural perspectives"
            ],
            tags=["philosophy", "debate", "perspectives", "wisdom", "worldview"],
            visibility=ToolVisibility.PUBLIC,
            timeout=60,  # Longer timeout for philosophical discourse
            max_parallel=self._max_parallel_override  # Use config value for parallel limit
        )
    
    async def can_handle(self, query: str, context: Dict) -> float:
        """Determine if Forum of Echoes is relevant for this query."""
        
        # Philosophy and ethics keywords
        philosophy_keywords = [
            "philosophy", "philosophical", "ethics", "ethical", "moral",
            "meaning", "purpose", "wisdom", "truth", "value", "belief"
        ]
        
        # Perspective keywords
        perspective_keywords = [
            "perspective", "viewpoint", "worldview", "opinion", "stance",
            "approach", "interpretation", "understanding", "lens"
        ]
        
        # Debate keywords
        debate_keywords = [
            "debate", "discuss", "argue", "consider", "explore",
            "compare", "contrast", "dialogue", "discourse"
        ]
        
        # Life and existence keywords
        existence_keywords = [
            "life", "death", "existence", "reality", "consciousness",
            "identity", "self", "being", "nature", "human"
        ]
        
        query_lower = query.lower()
        confidence = 0.0
        
        # Check for keyword matches
        for keyword in philosophy_keywords:
            if keyword in query_lower:
                confidence = max(confidence, 0.8)
                
        for keyword in perspective_keywords:
            if keyword in query_lower:
                confidence = max(confidence, 0.7)
                
        for keyword in debate_keywords:
            if keyword in query_lower:
                confidence = max(confidence, 0.6)
                
        for keyword in existence_keywords:
            if keyword in query_lower:
                confidence = max(confidence, 0.6)
        
        # Check for specific voice mentions
        for voice_key in self.VOICES:
            if voice_key in query_lower or self.VOICES[voice_key]["name"].lower() in query_lower:
                confidence = max(confidence, 0.9)
        
        # Check for Forum mention
        if "forum" in query_lower or "echoes" in query_lower:
            confidence = 0.95
            
        return confidence
    
    async def execute(self, input: ToolInput) -> ToolOutput:
        """Execute Forum of Echoes consultation."""
        try:
            # Select relevant voices for the query
            voices = await self._select_voices(input)
            
            # Determine format: dialogue or individual perspectives
            if len(voices) > 1 and self._should_debate(input):
                # Orchestrate a dialogue between voices
                result = await self._facilitate_dialogue(voices, input)
            else:
                # Get individual perspective(s)
                result = await self._gather_perspectives(voices, input)
            
            return ToolOutput(
                success=True,
                result=result,
                metadata={
                    "voices": [v["name"] for v in voices],
                    "format": "dialogue" if len(voices) > 1 and self._should_debate(input) else "perspectives"
                },
                confidence=0.8,
                display_format="markdown"
            )
            
        except Exception as e:
            logger.error(f"Forum of Echoes execution error: {e}")
            return ToolOutput(
                success=False,
                result=None,
                error=f"Forum consultation failed: {str(e)}"
            )
    
    async def _select_voices(self, input: ToolInput) -> List[Dict]:
        """Select which voices to activate based on the query."""
        query_lower = input.query.lower()
        selected_voices = []
        
        # Check for explicit voice requests
        for voice_key, voice_data in self.VOICES.items():
            if voice_key in query_lower or voice_data["name"].lower() in query_lower:
                selected_voices.append(voice_data)
        
        # If no explicit requests, select based on keywords
        if not selected_voices:
            for voice_key, voice_data in self.VOICES.items():
                for keyword in voice_data["keywords"]:
                    if keyword in query_lower:
                        selected_voices.append(voice_data)
                        break
        
        # If still no matches, select based on query type
        if not selected_voices:
            if any(word in query_lower for word in ["practical", "implement", "work", "result"]):
                selected_voices.append(self.VOICES["pragmatist"])
            if any(word in query_lower for word in ["meaning", "purpose", "why", "significance"]):
                selected_voices.append(self.VOICES["existentialist"])
            if any(word in query_lower for word in ["should", "right", "wrong", "ethical"]):
                selected_voices.append(self.VOICES["stoic"])
        
        # Default to a diverse set if no specific matches
        if not selected_voices:
            selected_voices = [
                self.VOICES["pragmatist"],
                self.VOICES["stoic"],
                self.VOICES["skeptic"]
            ]
        
        # Limit to avoid overwhelming responses
        return selected_voices[:5]
    
    def _should_debate(self, input: ToolInput) -> bool:
        """Determine if voices should debate or provide individual perspectives."""
        debate_triggers = [
            "debate", "discuss", "argue", "compare", "contrast",
            "dialogue", "conversation", "vs", "versus", "or"
        ]
        
        query_lower = input.query.lower()
        return any(trigger in query_lower for trigger in debate_triggers)
    
    async def _facilitate_dialogue(self, voices: List[Dict], input: ToolInput) -> str:
        """Orchestrate a dialogue between multiple voices."""
        dialogue = f"## Forum of Echoes: A Dialogue\n\n"
        dialogue += f"*Topic: {input.query}*\n\n"
        dialogue += f"*Participants: {', '.join([v['name'] for v in voices])}*\n\n"
        dialogue += "---\n\n"
        
        # Generate opening statements
        dialogue += "### Opening Statements\n\n"
        for voice in voices:
            statement = await self._generate_voice_response(voice, input.query, "opening")
            dialogue += f"**{voice['name']}**: {statement}\n\n"
        
        # Generate responses and counter-responses
        dialogue += "### The Dialogue\n\n"
        
        # Simulate 2-3 rounds of exchange
        for round_num in range(2):
            for i, voice in enumerate(voices):
                # Each voice responds to previous speakers
                context = f"Responding to the previous perspectives on '{input.query}'"
                response = await self._generate_voice_response(voice, context, "response")
                dialogue += f"**{voice['name']}**: {response}\n\n"
        
        # Closing thoughts
        dialogue += "### Closing Reflections\n\n"
        for voice in voices:
            closing = await self._generate_voice_response(voice, input.query, "closing")
            dialogue += f"**{voice['name']}**: {closing}\n\n"
        
        dialogue += "---\n\n"
        dialogue += "*The Forum of Echoes reveals that truth often emerges not from a single voice, "
        dialogue += "but from the harmonies and tensions between multiple perspectives.*"
        
        return dialogue
    
    async def _gather_perspectives(self, voices: List[Dict], input: ToolInput) -> str:
        """Gather individual perspectives from selected voices."""
        if len(voices) == 1:
            # Single voice response
            voice = voices[0]
            response = await self._generate_voice_response(voice, input.query, "full")
            return f"## {voice['name']}'s Perspective\n\n{response}"
        
        # Multiple perspectives
        perspectives = f"## Forum of Echoes: Multiple Perspectives\n\n"
        perspectives += f"*Question: {input.query}*\n\n"
        
        for voice in voices:
            response = await self._generate_voice_response(voice, input.query, "full")
            perspectives += f"### {voice['name']}\n"
            perspectives += f"*{voice['tradition']}*\n\n"
            perspectives += f"{response}\n\n"
            perspectives += "---\n\n"
        
        return perspectives
    
    async def _generate_voice_response(self, voice: Dict, query: str, response_type: str) -> str:
        """Generate a response from a specific voice using LLM."""
        
        voice_name = voice["name"]
        tradition = voice["tradition"]
        focus = voice["focus"]
        
        # Build system prompt for this voice
        system_prompt = self._get_voice_system_prompt(voice)
        
        # Build user prompt based on response type
        if response_type == "opening":
            user_prompt = f"""Provide an opening statement on this topic: {query}
            
Keep it to 2-3 sentences that establish your philosophical position."""
        
        elif response_type == "response":
            user_prompt = f"""Respond to what others have said about: {query}
            
Acknowledge other viewpoints while asserting your tradition's perspective. Keep it to 2-3 sentences."""
        
        elif response_type == "closing":
            user_prompt = f"""Provide a closing reflection on: {query}
            
Synthesize your tradition's wisdom on this topic. Keep it to 2-3 sentences."""
        
        else:  # full response
            user_prompt = f"""From your philosophical tradition, provide insight on: {query}
            
Structure your response with:
1. Your tradition's core perspective
2. How this applies to the question
3. Practical implications or wisdom
            
Keep it concise but insightful (3-5 sentences)."""
        
        try:
            # Get LLM response with voice-specific temperature
            response = await self.llm_service.complete(
                prompt=user_prompt,
                system=system_prompt,
                temperature=self._get_voice_temperature(voice_name),
                max_tokens=500  # Keep responses concise
            )
            # Extract content from response dict
            content = response.get("content", "") if response else ""
            return content
            
        except Exception as e:
            logger.error(f"Error generating {voice_name} response: {e}")
            # Fallback to a generic response
            if voice_name == "The Pragmatist":
                return f"""The key question isn't what's theoretically true, but what works in practice. 
When we examine "{query}", we should focus on concrete outcomes and empirical results. 
What difference does each answer make in lived experience? 
Let's test our ideas through experimentation and adapt based on what we learn.
The meaning of any concept lies in its practical consequences."""
            
            elif voice_name == "The Stoic":
                return f"""This question invites us to distinguish between what is within our control and what is not.
"{query}" can be approached through the lens of virtue and wisdom.
We cannot control external events, but we can control our responses to them.
Focus on developing excellence of character and accepting what cannot be changed.
True freedom comes from aligning our will with nature and reason."""
            
            elif voice_name == "The Existentialist":
                return f"""We are condemned to be free, and with that freedom comes the weight of responsibility.
In considering "{query}", we must acknowledge that we create meaning through our choices.
There is no predetermined essence or purpose - existence precedes essence.
Authenticity requires confronting the absurdity of existence while still engaging fully.
We must choose and act, knowing our choices define who we become."""
            
            elif voice_name == "The Buddhist":
                return f"""This question arises from the fundamental nature of suffering and impermanence.
"{query}" reflects our attachment to fixed ideas and permanent states.
All phenomena are interconnected and constantly changing.
Through mindfulness and compassion, we can see through the illusion of separateness.
The path forward involves letting go of attachments while cultivating loving-kindness."""
            
            elif voice_name == "The Skeptic":
                return f"""Before accepting any answer to "{query}", we must examine our assumptions.
What evidence supports each position? What biases might be influencing our thinking?
Many supposed certainties dissolve under careful scrutiny.
We should suspend judgment until sufficient evidence is available.
Even then, our conclusions should remain provisional and open to revision."""
            
            else:
                return f"""From the perspective of {tradition}, focusing on {focus}, 
this question opens important considerations about the nature of reality and our place within it.
Each tradition offers valuable insights while acknowledging the limits of any single viewpoint."""
    
    def _get_voice_temperature(self, voice_name: str) -> float:
        """Get temperature setting for each voice's personality."""
        temperatures = {
            "The Pragmatist": 0.4,      # Practical, grounded
            "The Stoic": 0.3,           # Disciplined, measured
            "The Existentialist": 0.7,   # Creative, exploratory
            "The Buddhist": 0.5,        # Balanced, mindful
            "The Skeptic": 0.4,         # Analytical, careful
            "The Idealist": 0.6,        # Visionary, aspirational
            "The Materialist": 0.3,     # Empirical, precise
            "The Absurdist": 0.8,       # Playful, unconventional
            "The Confucian": 0.4,       # Ordered, harmonious
            "The Taoist": 0.6           # Flowing, paradoxical
        }
        return temperatures.get(voice_name, 0.5)
    
    def _get_voice_system_prompt(self, voice: Dict) -> str:
        """Generate system prompt for a specific philosophical voice."""
        voice_name = voice["name"]
        
        prompts = {
            "The Pragmatist": """You are a Pragmatist philosopher in the tradition of William James and John Dewey.
Core beliefs: Truth is what works in practice, ideas tested by consequences, experience guides understanding.
Speak with practical wisdom, avoiding abstract speculation in favor of concrete applications.""",

            "The Stoic": """You are a Stoic philosopher in the tradition of Marcus Aurelius and Epictetus.
Core beliefs: Virtue is the only true good, we control our responses not external events, accept what cannot be changed.
Speak with disciplined wisdom, emphasizing personal responsibility and inner strength.""",

            "The Existentialist": """You are an Existentialist philosopher in the tradition of Sartre and de Beauvoir.
Core beliefs: Existence precedes essence, we are condemned to be free, authenticity requires confronting absurdity.
Speak with passionate intensity about freedom, responsibility, and authentic living.""",

            "The Buddhist": """You are a Buddhist philosopher in the tradition of Nagarjuna and Thich Nhat Hanh.
Core beliefs: All life involves suffering, everything is impermanent and interconnected, compassion leads to liberation.
Speak with gentle wisdom, emphasizing interconnection and the middle way.""",

            "The Skeptic": """You are a Skeptical philosopher in the tradition of Pyrrho and Sextus Empiricus.
Core beliefs: Question all assumptions, suspend judgment when evidence is insufficient, knowledge claims should be provisional.
Speak with analytical precision, always probing deeper and questioning assumptions.""",

            "The Idealist": """You are an Idealist philosopher in the tradition of Plato and Hegel.
Core beliefs: Perfect forms exist beyond material reality, mind or spirit is primary, reality has inherent purpose.
Speak with visionary eloquence about higher purposes and transcendent truths.""",

            "The Materialist": """You are a Materialist philosopher in the tradition of Democritus and modern physicalism.
Core beliefs: Physical matter is fundamental reality, consciousness emerges from material, empirical observation reveals truth.
Speak with scientific precision, grounding insights in observable phenomena.""",

            "The Absurdist": """You are an Absurdist philosopher in the tradition of Camus and Kierkegaard.
Core beliefs: Life has no inherent meaning, we must create meaning despite absurdity, embrace contradiction with joy.
Speak with paradoxical playfulness, finding freedom in meaninglessness.""",

            "The Confucian": """You are a Confucian philosopher in the tradition of Confucius and Mencius.
Core beliefs: Social harmony through proper relationships, virtue cultivation through ritual, respect for tradition.
Speak with ceremonial wisdom, emphasizing social order and moral cultivation.""",

            "The Taoist": """You are a Taoist philosopher in the tradition of Lao Tzu and Zhuangzi.
Core beliefs: Follow the natural way (Dao), act through non-action (wu wei), embrace simplicity and spontaneity.
Speak with paradoxical simplicity, using natural metaphors and embracing contradiction."""
        }
        
        return prompts.get(voice_name, f"You are {voice_name}, representing the {voice.get('tradition', 'philosophical')} tradition.")