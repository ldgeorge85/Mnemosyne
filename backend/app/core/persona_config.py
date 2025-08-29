"""
Persona-specific LLM configurations including temperature and reasoning levels.
"""
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ReasoningLevel(str, Enum):
    """Reasoning levels for models that support it (e.g., GPT-OSS 120B)"""
    LOW = "low"
    MEDIUM = "medium"  
    HIGH = "high"


class PersonaLLMConfig(BaseModel):
    """LLM configuration for a specific persona mode"""
    temperature: float = 0.7
    reasoning_level: Optional[ReasoningLevel] = None
    top_p: Optional[float] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    system_prompt_prefix: Optional[str] = None  # Added to system prompt


# Default persona configurations
PERSONA_CONFIGS: Dict[str, PersonaLLMConfig] = {
    "confidant": PersonaLLMConfig(
        temperature=0.8,  # Higher for empathetic responses
        reasoning_level=ReasoningLevel.MEDIUM,
        presence_penalty=0.1,  # Encourage variety
        system_prompt_prefix="Reasoning: medium\n"  # For GPT-OSS 120B
    ),
    "mentor": PersonaLLMConfig(
        temperature=0.6,  # Lower for instructional clarity
        reasoning_level=ReasoningLevel.HIGH,
        presence_penalty=0.0,
        system_prompt_prefix="Reasoning: high\n"
    ),
    "mediator": PersonaLLMConfig(
        temperature=0.5,  # Balanced and neutral
        reasoning_level=ReasoningLevel.HIGH,
        presence_penalty=0.0,
        system_prompt_prefix="Reasoning: high\n"
    ),
    "guardian": PersonaLLMConfig(
        temperature=0.3,  # Low for safety and caution
        reasoning_level=ReasoningLevel.HIGH,
        frequency_penalty=0.2,  # Avoid repetitive warnings
        system_prompt_prefix="Reasoning: high\n"
    ),
    "mirror": PersonaLLMConfig(
        temperature=0.7,  # Neutral reflection
        reasoning_level=ReasoningLevel.MEDIUM,
        presence_penalty=0.0,
        system_prompt_prefix="Reasoning: medium\n"
    ),
}


# Model capability profiles (not tied to specific models)
# These can be mapped to any model via LLM_MODEL_PROFILE env var
MODEL_PROFILES: Dict[str, Dict[str, Any]] = {
    "reasoning_channel": {
        # Models with explicit reasoning channels (e.g., GPT-OSS 120B, o1-preview)
        "force_temperature": 1.0,  # Often required for reasoning models
        "supports_reasoning_level": True,
        "reasoning_format": "prefix",  # How to add reasoning: "prefix" or "token"
    },
    "embedded_system": {
        # Models without separate system role (e.g., Gemma, some Llama variants)
        "force_temperature": None,  # Use persona-specific
        "supports_reasoning_level": False,
        "system_prompt_mode": "embedded",
    },
    "standard": {
        # Standard models with system role (e.g., GPT-4, Claude, most OpenAI-compatible)
        "force_temperature": None,  # Use persona-specific
        "supports_reasoning_level": False,
        "system_prompt_mode": "separate",
    },
    "deepseek": {
        # DeepSeek-style models with specific formatting needs
        "force_temperature": None,
        "supports_reasoning_level": False,
        "system_prompt_mode": "separate",
        "special_tokens": True,
    },
    "innogpt": {
        # InnoGPT-1 with Harmony format (reasoning + final messages)
        "force_temperature": None,
        "supports_reasoning_level": True,
        "system_prompt_mode": "harmony",  # Special mode for InnoGPT
        "reasoning_format": "harmony",  # Uses special Harmony format
        "expects_user_level": True,  # InnoGPT expects user-level in messages
    },
}


def get_llm_config_for_persona(
    persona: str,
    model_profile: Optional[str] = None,
    settings: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Get LLM configuration for a specific persona and model profile.
    
    Args:
        persona: Persona mode (confidant, mentor, etc.)
        model_profile: Optional model profile (reasoning_channel, embedded_system, etc.)
        settings: Optional settings object with env configurations
        
    Returns:
        Dictionary of LLM parameters
    """
    if settings is None:
        from app.core.config import settings as default_settings
        settings = default_settings
    
    result = {}
    
    # Get the model profile (defaults to "standard" if not specified)
    profile_name = model_profile or getattr(settings, 'LLM_MODEL_PROFILE', 'standard')
    profile = MODEL_PROFILES.get(profile_name, MODEL_PROFILES['standard'])
    
    # Handle temperature based on mode
    if settings.LLM_TEMPERATURE_MODE == "static":
        # Use static temperature from env
        result["temperature"] = settings.LLM_STATIC_TEMPERATURE
    else:
        # Use variable temperature from persona config
        config = PERSONA_CONFIGS.get(
            persona.lower(),
            PersonaLLMConfig()  # Default if persona not found
        )
        result["temperature"] = config.temperature
        
        # Add optional parameters if set
        if config.top_p is not None:
            result["top_p"] = config.top_p
        if config.presence_penalty is not None:
            result["presence_penalty"] = config.presence_penalty
        if config.frequency_penalty is not None:
            result["frequency_penalty"] = config.frequency_penalty
    
    # Apply profile-specific overrides
    if profile.get("force_temperature") is not None:
        result["temperature"] = profile["force_temperature"]
    
    # Handle reasoning level if supported by profile
    if profile.get("supports_reasoning_level") and settings.LLM_SUPPORTS_REASONING_LEVEL:
        config = PERSONA_CONFIGS.get(persona.lower(), PersonaLLMConfig())
        if config.reasoning_level:
            reasoning_format = profile.get("reasoning_format", "prefix")
            if reasoning_format == "prefix":
                result["system_prompt_prefix"] = f"Reasoning: {config.reasoning_level.value}\n"
            # Could add other formats here (e.g., "token" for special tokens)
    
    # Handle system prompt mode (profile override or settings)
    result["system_prompt_mode"] = profile.get(
        "system_prompt_mode",
        settings.LLM_SYSTEM_PROMPT_MODE
    )
    
    # Add any special tokens flag if needed
    if profile.get("special_tokens"):
        result["special_tokens"] = True
    
    return result