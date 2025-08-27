#!/usr/bin/env python3
"""
Test script to verify LLM configuration with different settings.
"""
import asyncio
import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.config import settings
from app.core.persona_config import get_llm_config_for_persona

def test_persona_configs():
    """Test temperature configurations for different personas."""
    print("\n=== Testing Persona Configurations ===")
    print(f"Temperature Mode: {settings.LLM_TEMPERATURE_MODE}")
    print(f"Static Temperature: {settings.LLM_STATIC_TEMPERATURE}")
    print(f"System Prompt Mode: {settings.LLM_SYSTEM_PROMPT_MODE}")
    print(f"Supports Reasoning Level: {settings.LLM_SUPPORTS_REASONING_LEVEL}")
    print(f"Model Name: {settings.LLM_MODEL_NAME}\n")
    
    personas = ["confidant", "mentor", "mediator", "guardian", "mirror"]
    
    for persona in personas:
        config = get_llm_config_for_persona(persona, settings.LLM_MODEL_NAME)
        print(f"{persona.capitalize()}:")
        print(f"  Temperature: {config.get('temperature')}")
        print(f"  System Prompt Mode: {config.get('system_prompt_mode')}")
        if config.get('system_prompt_prefix'):
            print(f"  System Prefix: {config.get('system_prompt_prefix').strip()}")
        if config.get('top_p'):
            print(f"  Top P: {config.get('top_p')}")
        if config.get('presence_penalty'):
            print(f"  Presence Penalty: {config.get('presence_penalty')}")
        if config.get('frequency_penalty'):
            print(f"  Frequency Penalty: {config.get('frequency_penalty')}")
        print()

def test_model_overrides():
    """Test model-specific overrides."""
    print("\n=== Testing Model-Specific Overrides ===")
    
    # Test with GPT-OSS 120B settings
    os.environ["LLM_SUPPORTS_REASONING_LEVEL"] = "true"
    os.environ["LLM_MODEL_NAME"] = "gpt-oss-120b"
    
    # Need to reload settings
    from importlib import reload
    import app.core.config
    reload(app.core.config)
    from app.core.config import settings as reloaded_settings
    
    print(f"Model: {reloaded_settings.LLM_MODEL_NAME}")
    print(f"Supports Reasoning: {reloaded_settings.LLM_SUPPORTS_REASONING_LEVEL}\n")
    
    for persona in ["confidant", "guardian"]:
        config = get_llm_config_for_persona(persona, "gpt-oss-120b", reloaded_settings)
        print(f"{persona.capitalize()}:")
        print(f"  Temperature: {config.get('temperature')}")
        if config.get('system_prompt_prefix'):
            print(f"  Reasoning Level: {config.get('system_prompt_prefix').strip()}")
        print()

def test_static_vs_variable():
    """Test static vs variable temperature modes."""
    print("\n=== Testing Static vs Variable Modes ===")
    
    # Test static mode
    os.environ["LLM_TEMPERATURE_MODE"] = "static"
    os.environ["LLM_STATIC_TEMPERATURE"] = "0.9"
    
    from importlib import reload
    import app.core.config
    reload(app.core.config)
    from app.core.config import settings as static_settings
    
    config_static = get_llm_config_for_persona("confidant", settings=static_settings)
    print(f"Static Mode - Confidant Temperature: {config_static.get('temperature')}")
    
    # Test variable mode
    os.environ["LLM_TEMPERATURE_MODE"] = "variable"
    reload(app.core.config)
    from app.core.config import settings as variable_settings
    
    config_variable = get_llm_config_for_persona("confidant", settings=variable_settings)
    print(f"Variable Mode - Confidant Temperature: {config_variable.get('temperature')}")

def test_embedded_system_prompt():
    """Test embedded vs separate system prompt modes."""
    print("\n=== Testing System Prompt Modes ===")
    
    # Test embedded mode (for Gemma)
    os.environ["LLM_SYSTEM_PROMPT_MODE"] = "embedded"
    
    from importlib import reload
    import app.core.config
    reload(app.core.config)
    from app.core.config import settings as embedded_settings
    
    config = get_llm_config_for_persona("mentor", settings=embedded_settings)
    print(f"Embedded Mode - System Prompt Mode: {config.get('system_prompt_mode')}")
    
    # Test separate mode (default)
    os.environ["LLM_SYSTEM_PROMPT_MODE"] = "separate"
    reload(app.core.config)
    from app.core.config import settings as separate_settings
    
    config = get_llm_config_for_persona("mentor", settings=separate_settings)
    print(f"Separate Mode - System Prompt Mode: {config.get('system_prompt_mode')}")

if __name__ == "__main__":
    # Set default env vars if not set
    os.environ.setdefault("LLM_TEMPERATURE_MODE", "variable")
    os.environ.setdefault("LLM_STATIC_TEMPERATURE", "0.7")
    os.environ.setdefault("LLM_SYSTEM_PROMPT_MODE", "separate")
    os.environ.setdefault("LLM_SUPPORTS_REASONING_LEVEL", "false")
    os.environ.setdefault("LLM_MODEL_NAME", "gpt-4")
    
    print("=" * 60)
    print("LLM Configuration Comprehensive Test Suite")
    print("=" * 60)
    
    # Core configuration tests
    test_persona_configs()
    test_model_overrides()
    test_static_vs_variable()
    test_embedded_system_prompt()
    
    # Additional validation tests
    test_integration_with_llm_service()
    test_all_personas_have_configs()
    test_gemma_compatibility()
    test_config_json_serializable()
    
    print("\n" + "=" * 60)
    print("✅ ALL LLM CONFIGURATION TESTS PASSED!")
    print("=" * 60)

def test_integration_with_llm_service():
    """Test that configs properly integrate with LLM service."""
    print("\n=== Testing Integration with LLM Service ===")
    
    # Import LLM service
    from app.services.llm.service import LLMService
    from app.services.persona.manager import PersonaManager
    
    # Test that service accepts kwargs
    service = LLMService()
    
    # Test complete method signature
    import inspect
    complete_sig = inspect.signature(service.complete)
    print(f"Complete method params: {list(complete_sig.parameters.keys())}")
    assert "kwargs" in str(complete_sig), "complete() should accept **kwargs"
    
    # Test stream_complete method signature  
    stream_sig = inspect.signature(service.stream_complete)
    print(f"Stream_complete params: {list(stream_sig.parameters.keys())}")
    assert "kwargs" in str(stream_sig), "stream_complete() should accept **kwargs"
    
    print("✅ LLM Service properly accepts additional parameters")

def test_all_personas_have_configs():
    """Verify all 5 personas have proper configurations."""
    print("\n=== Testing All Personas Have Configs ===")
    
    personas = ["confidant", "mentor", "mediator", "guardian", "mirror"]
    
    for persona in personas:
        config = get_llm_config_for_persona(persona)
        assert config.get("temperature") is not None, f"{persona} missing temperature"
        print(f"✅ {persona}: Temperature={config.get('temperature')}")
    
    print("All personas have temperature configurations")

def test_gemma_compatibility():
    """Test configuration for Gemma model (embedded system prompt)."""
    print("\n=== Testing Gemma Compatibility ===")
    
    os.environ["LLM_MODEL_NAME"] = "gemma-27b"
    os.environ["LLM_SYSTEM_PROMPT_MODE"] = "embedded"
    os.environ["LLM_SUPPORTS_REASONING_LEVEL"] = "false"
    
    from importlib import reload
    import app.core.config
    reload(app.core.config)
    from app.core.config import settings as gemma_settings
    
    config = get_llm_config_for_persona("guardian", model_name="gemma-27b", settings=gemma_settings)
    
    print(f"Model: {gemma_settings.LLM_MODEL_NAME}")
    print(f"System Prompt Mode: {config.get('system_prompt_mode')}")
    print(f"Has Reasoning Prefix: {bool(config.get('system_prompt_prefix'))}")
    
    assert config.get('system_prompt_mode') == 'embedded', "Gemma should use embedded mode"
    assert not config.get('system_prompt_prefix'), "Gemma shouldn't have reasoning prefix"
    print("✅ Gemma compatibility verified")

def test_config_json_serializable():
    """Ensure all configs are JSON serializable for API responses."""
    print("\n=== Testing JSON Serialization ===")
    
    personas = ["confidant", "mentor", "mediator", "guardian", "mirror"]
    
    for persona in personas:
        config = get_llm_config_for_persona(persona)
        try:
            json_str = json.dumps(config)
            parsed = json.loads(json_str)
            assert parsed == config, f"Config for {persona} changed during serialization"
            print(f"✅ {persona} config is JSON serializable")
        except Exception as e:
            print(f"❌ {persona} config failed JSON serialization: {e}")
            raise
    
    print("All configs are JSON serializable")