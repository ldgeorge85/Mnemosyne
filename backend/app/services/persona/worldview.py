"""
Worldview Adapter for Persona System

This module implements cultural and philosophical adaptations
for the persona based on user worldview preferences.
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class PhilosophicalTradition(Enum):
    """Philosophical traditions the persona can adapt to."""
    STOIC = "stoic"
    CONFUCIAN = "confucian"
    SUFI = "sufi"
    BUDDHIST = "buddhist"
    HUMANIST = "humanist"
    EXISTENTIALIST = "existentialist"
    PRAGMATIST = "pragmatist"
    INDIGENOUS = "indigenous"
    SECULAR = "secular"
    SPIRITUAL = "spiritual"


@dataclass
class WorldviewProfile:
    """User's worldview profile for persona adaptation."""
    primary_tradition: Optional[PhilosophicalTradition] = None
    secondary_traditions: List[PhilosophicalTradition] = None
    values_hierarchy: List[str] = None  # Ordered list of important values
    communication_style: str = "balanced"  # formal, casual, poetic, direct
    metaphysical_stance: str = "agnostic"  # materialist, dualist, idealist, agnostic
    ethical_framework: str = "pluralist"  # deontological, consequentialist, virtue, pluralist
    cultural_context: Optional[str] = None
    language_preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.secondary_traditions is None:
            self.secondary_traditions = []
        if self.values_hierarchy is None:
            self.values_hierarchy = []
        if self.language_preferences is None:
            self.language_preferences = {}


class WorldviewAdapter:
    """
    Adapts persona responses based on user's worldview and cultural context.
    """
    
    # Philosophical wisdom patterns for each tradition
    TRADITION_PATTERNS = {
        PhilosophicalTradition.STOIC: {
            "core_values": ["resilience", "rationality", "virtue", "acceptance"],
            "language_style": "measured and logical",
            "metaphors": ["fortress of mind", "river of fate", "inner citadel"],
            "guidance_approach": "Focus on what is within your control",
            "prompt_modifier": """Apply Stoic wisdom: emphasize personal agency, 
            rational thinking, and emotional equanimity. Use Marcus Aurelius and 
            Epictetus as inspiration."""
        },
        
        PhilosophicalTradition.CONFUCIAN: {
            "core_values": ["harmony", "relationships", "duty", "learning"],
            "language_style": "respectful and relational",
            "metaphors": ["family bonds", "social fabric", "cultivated garden"],
            "guidance_approach": "Consider your relationships and responsibilities",
            "prompt_modifier": """Apply Confucian wisdom: emphasize social harmony,
            reciprocal relationships, and continuous self-cultivation. Reference
            concepts like ren (仁) and li (礼) when appropriate."""
        },
        
        PhilosophicalTradition.SUFI: {
            "core_values": ["love", "unity", "surrender", "divine beauty"],
            "language_style": "poetic and mystical",
            "metaphors": ["ocean and drop", "lover and beloved", "veil and truth"],
            "guidance_approach": "Seek the divine spark within all things",
            "prompt_modifier": """Apply Sufi wisdom: use poetic language, emphasize
            divine love and unity, and the journey of the heart. Draw from Rumi
            and Ibn Arabi's teachings."""
        },
        
        PhilosophicalTradition.BUDDHIST: {
            "core_values": ["compassion", "mindfulness", "impermanence", "liberation"],
            "language_style": "gentle and aware",
            "metaphors": ["flowing stream", "empty mirror", "lotus bloom"],
            "guidance_approach": "Observe without attachment, act with compassion",
            "prompt_modifier": """Apply Buddhist wisdom: emphasize mindfulness,
            non-attachment, and compassion. Reference the Four Noble Truths and
            Eightfold Path when relevant."""
        },
        
        PhilosophicalTradition.HUMANIST: {
            "core_values": ["dignity", "reason", "progress", "human potential"],
            "language_style": "empowering and rational",
            "metaphors": ["human flourishing", "shared humanity", "potential realized"],
            "guidance_approach": "Celebrate human agency and potential",
            "prompt_modifier": """Apply Humanist wisdom: emphasize human dignity,
            rational inquiry, and the potential for growth and progress. Focus on
            human agency and ethical reasoning."""
        },
        
        PhilosophicalTradition.EXISTENTIALIST: {
            "core_values": ["freedom", "authenticity", "responsibility", "meaning-making"],
            "language_style": "provocative and introspective",
            "metaphors": ["abyss of freedom", "authentic self", "burden of choice"],
            "guidance_approach": "Embrace your freedom and create your meaning",
            "prompt_modifier": """Apply Existentialist wisdom: emphasize radical
            freedom, personal responsibility, and authentic self-creation. Channel
            Sartre, de Beauvoir, and Camus."""
        },
        
        PhilosophicalTradition.PRAGMATIST: {
            "core_values": ["practicality", "experimentation", "results", "adaptation"],
            "language_style": "clear and action-oriented",
            "metaphors": ["tools in toolbox", "paths forward", "what works"],
            "guidance_approach": "Focus on practical outcomes and what works",
            "prompt_modifier": """Apply Pragmatist wisdom: emphasize practical
            solutions, experimentation, and judging ideas by their consequences.
            Think William James and John Dewey."""
        },
        
        PhilosophicalTradition.INDIGENOUS: {
            "core_values": ["interconnection", "ancestors", "land", "cycles"],
            "language_style": "holistic and narrative",
            "metaphors": ["web of relations", "seven generations", "sacred circle"],
            "guidance_approach": "Honor your connections to all beings",
            "prompt_modifier": """Apply Indigenous wisdom: emphasize interconnection,
            respect for nature, ancestral wisdom, and cyclical time. Acknowledge
            the sacred in everyday life."""
        }
    }
    
    def __init__(self):
        """Initialize the worldview adapter."""
        self.current_profile: Optional[WorldviewProfile] = None
    
    def set_profile(self, profile: WorldviewProfile):
        """
        Set the current worldview profile.
        
        Args:
            profile: User's worldview profile
        """
        self.current_profile = profile
        logger.info(f"Worldview profile set: {profile.primary_tradition}")
    
    def adapt_prompt(self, base_prompt: str) -> str:
        """
        Adapt a base prompt according to the user's worldview.
        
        Args:
            base_prompt: Original system prompt
            
        Returns:
            Adapted prompt with worldview modifications
        """
        if not self.current_profile:
            return base_prompt
        
        adaptations = []
        
        # Add primary tradition modifier
        if self.current_profile.primary_tradition:
            tradition_data = self.TRADITION_PATTERNS.get(
                self.current_profile.primary_tradition, {}
            )
            if "prompt_modifier" in tradition_data:
                adaptations.append(tradition_data["prompt_modifier"])
        
        # Add secondary traditions
        for tradition in self.current_profile.secondary_traditions[:2]:  # Limit to 2
            tradition_data = self.TRADITION_PATTERNS.get(tradition, {})
            if "prompt_modifier" in tradition_data:
                adaptations.append(f"Secondary influence: {tradition_data['guidance_approach']}")
        
        # Add communication style
        style_modifiers = {
            "formal": "Use formal, respectful language with proper grammar.",
            "casual": "Use relaxed, conversational language.",
            "poetic": "Use metaphorical and lyrical language.",
            "direct": "Be concise and straightforward.",
            "academic": "Use precise, scholarly language.",
            "warm": "Use warm, nurturing language.",
        }
        
        if self.current_profile.communication_style in style_modifiers:
            adaptations.append(style_modifiers[self.current_profile.communication_style])
        
        # Add value hierarchy
        if self.current_profile.values_hierarchy:
            top_values = ", ".join(self.current_profile.values_hierarchy[:3])
            adaptations.append(f"Prioritize these values in guidance: {top_values}")
        
        # Add ethical framework
        ethical_modifiers = {
            "deontological": "Emphasize duties, rules, and moral obligations.",
            "consequentialist": "Focus on outcomes and consequences of actions.",
            "virtue": "Emphasize character development and virtuous traits.",
            "care": "Prioritize relationships and caring responsibilities.",
            "pluralist": "Balance multiple ethical considerations.",
        }
        
        if self.current_profile.ethical_framework in ethical_modifiers:
            adaptations.append(ethical_modifiers[self.current_profile.ethical_framework])
        
        # Combine with base prompt
        if adaptations:
            adapted_prompt = base_prompt + "\n\nWorldview Adaptations:\n" + "\n".join(adaptations)
        else:
            adapted_prompt = base_prompt
        
        return adapted_prompt
    
    def get_cultural_greeting(self) -> str:
        """
        Get a culturally appropriate greeting.
        
        Returns:
            Greeting string
        """
        if not self.current_profile:
            return "Hello"
        
        greetings = {
            "arabic": "As-salaam alaikum",
            "hebrew": "Shalom",
            "hindi": "Namaste",
            "chinese": "你好 (Nǐ hǎo)",
            "japanese": "こんにちは (Konnichiwa)",
            "swahili": "Jambo",
            "hawaiian": "Aloha",
            "lakota": "Hau",
        }
        
        if self.current_profile.cultural_context:
            context_lower = self.current_profile.cultural_context.lower()
            for culture, greeting in greetings.items():
                if culture in context_lower:
                    return greeting
        
        # Return based on philosophical tradition
        if self.current_profile.primary_tradition == PhilosophicalTradition.SUFI:
            return "Peace be upon your heart"
        elif self.current_profile.primary_tradition == PhilosophicalTradition.BUDDHIST:
            return "May you be well"
        elif self.current_profile.primary_tradition == PhilosophicalTradition.STOIC:
            return "Greetings, friend"
        
        return "Hello"
    
    def apply_linguistic_preferences(self, text: str) -> str:
        """
        Apply linguistic preferences to text.
        
        Args:
            text: Original text
            
        Returns:
            Text with linguistic adaptations
        """
        if not self.current_profile or not self.current_profile.language_preferences:
            return text
        
        preferences = self.current_profile.language_preferences
        
        # Apply formality level
        if preferences.get("avoid_contractions"):
            contractions = {
                "don't": "do not",
                "won't": "will not",
                "can't": "cannot",
                "isn't": "is not",
                "aren't": "are not",
                "wasn't": "was not",
                "weren't": "were not",
                "haven't": "have not",
                "hasn't": "has not",
                "hadn't": "had not",
                "wouldn't": "would not",
                "shouldn't": "should not",
                "couldn't": "could not",
                "mightn't": "might not",
                "mustn't": "must not",
            }
            for contraction, expanded in contractions.items():
                text = text.replace(contraction, expanded)
                text = text.replace(contraction.capitalize(), expanded.capitalize())
        
        # Apply pronoun preferences
        if preferences.get("pronouns"):
            # This would be more complex in production
            pass
        
        return text
    
    def get_wisdom_quote(self) -> Optional[str]:
        """
        Get a relevant wisdom quote based on worldview.
        
        Returns:
            Quote string or None
        """
        if not self.current_profile or not self.current_profile.primary_tradition:
            return None
        
        quotes = {
            PhilosophicalTradition.STOIC: [
                "You have power over your mind - not outside events. Realize this, and you will find strength. - Marcus Aurelius",
                "We cannot choose our external circumstances, but we can always choose how we respond to them. - Epictetus",
            ],
            PhilosophicalTradition.BUDDHIST: [
                "Peace comes from within. Do not seek it without. - Buddha",
                "In the end, only three things matter: how much you loved, how gently you lived, and how gracefully you let go. - Buddha",
            ],
            PhilosophicalTradition.SUFI: [
                "Let yourself be silently drawn by the strange pull of what you really love. - Rumi",
                "Your task is not to seek for love, but to seek and find all the barriers within yourself that you have built against it. - Rumi",
            ],
            PhilosophicalTradition.CONFUCIAN: [
                "The man who moves a mountain begins by carrying away small stones. - Confucius",
                "When we see men of worth, we should think of equaling them; when we see men of a contrary character, we should turn inwards and examine ourselves. - Confucius",
            ],
            PhilosophicalTradition.HUMANIST: [
                "The good life is one inspired by love and guided by knowledge. - Bertrand Russell",
                "We are not going to change the world. But in the small place where each of us stands, we can make a difference. - Rachel Naomi Remen",
            ],
            PhilosophicalTradition.EXISTENTIALIST: [
                "Man is condemned to be free; because once thrown into the world, he is responsible for everything he does. - Jean-Paul Sartre",
                "The only way to deal with an unfree world is to become so absolutely free that your very existence is an act of rebellion. - Albert Camus",
            ],
        }
        
        tradition_quotes = quotes.get(self.current_profile.primary_tradition, [])
        if tradition_quotes:
            import random
            return random.choice(tradition_quotes)
        
        return None


# Global worldview adapter instance
_worldview_adapter = None


def get_worldview_adapter() -> WorldviewAdapter:
    """
    Get the global worldview adapter instance.
    
    Returns:
        WorldviewAdapter instance
    """
    global _worldview_adapter
    if _worldview_adapter is None:
        _worldview_adapter = WorldviewAdapter()
    return _worldview_adapter