"""
Prompt Loader for the Shadow system.

This module handles loading and parsing prompt templates from YAML files.
"""

import os
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("shadow.prompts")


class PromptLoader:
    """
    Loads and manages prompt templates for agents.
    """
    
    def __init__(self, agent_type: str):
        """
        Initialize the prompt loader for a specific agent type.
        
        Args:
            agent_type: The type of agent (engineer, librarian, priest)
        """
        self.agent_type = agent_type
        self.prompts: Dict[str, str] = {}
        self._load_prompts()
    
    def _load_prompts(self) -> None:
        """
        Load prompts from the agent's prompts.yaml file.
        """
        prompts_path = Path(__file__).parent.parent / "agents" / self.agent_type / "prompts.yaml"
        
        try:
            if prompts_path.exists():
                with open(prompts_path, "r") as f:
                    self.prompts = yaml.safe_load(f) or {}
                logger.info(f"Loaded {len(self.prompts)} prompts for {self.agent_type} agent")
            else:
                logger.warning(f"Prompts file not found: {prompts_path}")
        except Exception as e:
            logger.error(f"Error loading prompts for {self.agent_type}: {str(e)}")
            self.prompts = {}
    
    def get_prompt(self, prompt_key: str, default: str = "") -> str:
        """
        Get a specific prompt by key.
        
        Args:
            prompt_key: The key of the prompt to retrieve
            default: Default value if prompt is not found
            
        Returns:
            The prompt string
        """
        return self.prompts.get(prompt_key, default)
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for the agent.
        
        Returns:
            The system prompt string
        """
        return self.get_prompt("system_prompt", f"You are the {self.agent_type.capitalize()} agent.")


def get_prompt_loader(agent_type: str) -> PromptLoader:
    """
    Get a prompt loader for a specific agent type.
    
    Args:
        agent_type: The type of agent (engineer, librarian, priest)
        
    Returns:
        PromptLoader instance
    """
    return PromptLoader(agent_type)
