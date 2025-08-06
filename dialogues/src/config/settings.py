"""
Configuration loader for LLM and system settings.
Supports environment variables and optional .env file.
"""
import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

LLM_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    "model_name": os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
    "temperature": float(os.getenv("OPENAI_TEMPERATURE", 0.7)),
    "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", 512)),
}

def get_llm_config():
    """Return a copy of the current LLM config."""
    return dict(LLM_CONFIG)
