"""
llm_utils.py - Utility functions for LLM API calls (OpenAI, etc.)
"""

from src.config.settings import get_llm_config
from openai import OpenAI
import tiktoken

def estimate_prompt_size(prompt):
    """
    Estimate the size of a prompt in tokens using tiktoken.
    Fallback to a simple character count if tiktoken is not available.
    """
    try:
        return tiktoken.get_encoding(prompt).length
    except Exception:
        return len(prompt) // 4  # rough estimate, 1 token ~ 4 characters

def call_openai(system_prompt, user_prompt, return_usage=False):
    """
    Call OpenAI API with a system and user prompt, return the response text and optional token usage.
    Args:
        system_prompt (str): The system prompt (agent persona, instructions)
        user_prompt (str): The user or debate prompt
        return_usage (bool): If True, return dict with response and token usage info
    Returns:
        str: LLM response (default)
        OR
        dict: {'response': ..., 'usage': {'prompt_tokens': ..., 'completion_tokens': ..., 'total_tokens': ...}}
    """
    cfg = get_llm_config()
    if not cfg["api_key"]:
        return "[LLM not configured: Please set OPENAI_API_KEY]" if not return_usage else {"response": "[LLM not configured: Please set OPENAI_API_KEY]", "usage": {}}
    
    # Estimate prompt size
    prompt_size = estimate_prompt_size(system_prompt + user_prompt)
    
    # Get the actual model context window
    model_name = cfg["model_name"]
    # Default context window by model type
    if model_name.startswith("gpt-3.5"):
        model_context_window = 4096
    elif model_name.startswith("gpt-4"):
        model_context_window = 8192
    else:
        model_context_window = 2048
    # Allow override by OPENAI_MAX_TOKENS if set and larger
    env_max_tokens = int(cfg.get("max_tokens", 0))
    if env_max_tokens and env_max_tokens > model_context_window:
        model_context_window = env_max_tokens

    # Only print warnings if prompt or max_tokens are being forcibly reduced
    if prompt_size > model_context_window:
        print(f"Warning: Prompt size ({prompt_size}) exceeds context window ({model_context_window}). Truncating prompt.")
        prompt_size = model_context_window

    max_tokens = max(128, model_context_window - prompt_size)
    if model_context_window - prompt_size < 128:
        print(f"Warning: Available tokens for completion is very low (max_tokens={max_tokens}, context_window={model_context_window}, prompt_size={prompt_size})")
    
    try:
        client = OpenAI(
            api_key=cfg["api_key"],
            base_url=cfg["base_url"] if "base_url" in cfg and cfg["base_url"] else None
        )
        response = client.chat.completions.create(
            model=cfg["model_name"],
            temperature=cfg["temperature"],
            max_tokens=int(max_tokens),  # Use int() to ensure max_tokens is an integer
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        message_content = response.choices[0].message.content
        usage = getattr(response, 'usage', None)
        if return_usage:
            if usage:
                usage_dict = {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            else:
                usage_dict = {}
            return {"response": message_content, "usage": usage_dict}
        return message_content
    except Exception as e:
        if return_usage:
            return {"response": f"[LLM error: {e}]", "usage": {}}
        return f"[LLM error: {e}]"
