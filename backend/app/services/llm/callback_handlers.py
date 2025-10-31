"""
LangChain Callback Handlers

This module provides custom callback handlers for LangChain operations.
These handlers allow monitoring, logging, and custom event handling for LLM interactions.
"""
import time
import logging
from typing import Dict, Any, List, Optional, Union
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import LLMResult

# Set up module logger
logger = logging.getLogger(__name__)


class MnemosyneCallbackHandler(BaseCallbackHandler):
    """
    Custom callback handler for LangChain operations within Mnemosyne.
    
    This handler provides logging, usage tracking, and event handling
    for all LLM interactions, prompts, and completions.
    """
    
    def __init__(
        self, 
        track_tokens: bool = True,
        verbose: bool = False,
        conversation_id: Optional[str] = None,
    ):
        """
        Initialize the callback handler.
        
        Args:
            track_tokens: Whether to track token usage
            verbose: Whether to enable verbose logging
            conversation_id: ID of the associated conversation, if any
        """
        super().__init__()
        self.track_tokens = track_tokens
        self.verbose = verbose
        self.conversation_id = conversation_id
        
        # Timing and usage statistics
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.total_tokens: int = 0
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        
        # Content storage
        self.stored_prompts: List[str] = []
        self.stored_responses: List[str] = []

    def on_llm_start(
        self, 
        serialized: Dict[str, Any], 
        prompts: List[str], 
        **kwargs: Any
    ) -> None:
        """
        Called when LLM starts processing.
        
        Args:
            serialized: Serialized LLM data
            prompts: List of prompts being sent to the LLM
            **kwargs: Additional keyword arguments
        """
        self.start_time = time.time()
        model_name = serialized.get("name", "unknown")
        
        # Store prompts for later analysis
        self.stored_prompts.extend(prompts)
        
        if self.verbose:
            logger.info(f"Starting LLM request to model: {model_name}")
            if len(prompts) == 1:
                logger.debug(f"Prompt: {prompts[0][:100]}...")
            else:
                logger.debug(f"Sending {len(prompts)} prompts to LLM")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """
        Called when LLM completes processing.
        
        Args:
            response: The result from the LLM
            **kwargs: Additional keyword arguments
        """
        self.end_time = time.time()
        self.successful_requests += 1
        duration = self.end_time - self.start_time if self.start_time else 0
        
        # Store generated text
        for generations in response.generations:
            for generation in generations:
                self.stored_responses.append(generation.text)
        
        # Track token usage if available
        if self.track_tokens and hasattr(response, "llm_output"):
            llm_output = response.llm_output
            if llm_output and isinstance(llm_output, dict):
                token_usage = llm_output.get("token_usage", {})
                
                self.total_tokens += token_usage.get("total_tokens", 0)
                self.prompt_tokens += token_usage.get("prompt_tokens", 0)
                self.completion_tokens += token_usage.get("completion_tokens", 0)
        
        if self.verbose:
            logger.info(f"LLM request completed in {duration:.2f}s")
            if self.track_tokens:
                logger.debug(f"Token usage: {self.prompt_tokens} prompt, {self.completion_tokens} completion")

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """
        Called when LLM encounters an error.
        
        Args:
            error: The exception that occurred
            **kwargs: Additional keyword arguments
        """
        self.failed_requests += 1
        logger.error(f"LLM error: {str(error)}")

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """
        Called when a chain starts processing.
        
        Args:
            serialized: Serialized chain data
            inputs: Chain inputs
            **kwargs: Additional keyword arguments
        """
        if self.verbose:
            chain_type = serialized.get("name", "unknown")
            logger.debug(f"Starting chain: {chain_type}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """
        Called when a chain completes.
        
        Args:
            outputs: Chain outputs
            **kwargs: Additional keyword arguments
        """
        if self.verbose:
            logger.debug("Chain completed")

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """
        Called when a chain encounters an error.
        
        Args:
            error: The exception that occurred
            **kwargs: Additional keyword arguments
        """
        logger.error(f"Chain error: {str(error)}")

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """
        Called when a tool starts processing.
        
        Args:
            serialized: Serialized tool data
            input_str: Tool input
            **kwargs: Additional keyword arguments
        """
        if self.verbose:
            tool_name = serialized.get("name", "unknown")
            logger.debug(f"Starting tool: {tool_name} with input: {input_str[:50]}...")

    def on_agent_action(
        self, action: AgentAction, **kwargs: Any
    ) -> Any:
        """
        Called when an agent takes an action.
        
        Args:
            action: The action being taken
            **kwargs: Additional keyword arguments
        """
        if self.verbose:
            logger.debug(f"Agent action: {action.tool} with input: {action.tool_input}")

    def on_agent_finish(
        self, finish: AgentFinish, **kwargs: Any
    ) -> None:
        """
        Called when an agent finishes processing.
        
        Args:
            finish: Information about the agent completion
            **kwargs: Additional keyword arguments
        """
        if self.verbose:
            logger.debug(f"Agent finished: {finish.return_values}")

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about LLM usage.
        
        Returns:
            Dictionary containing timing and token usage statistics
        """
        duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        
        return {
            "duration_seconds": duration,
            "total_tokens": self.total_tokens,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
        }
