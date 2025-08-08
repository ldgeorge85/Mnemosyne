"""
Plugin Architecture for Mnemosyne Dual-Track System

This module provides the base infrastructure for separating experimental
features from the stable core. All experimental modules must inherit from
PluginInterface and be clearly labeled.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PluginStatus(str, Enum):
    """Plugin operational status"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    DISABLED = "disabled"
    SHUTTING_DOWN = "shutting_down"


class PluginType(str, Enum):
    """Plugin classification"""
    CORE = "core"  # Proven, stable features
    EXPERIMENTAL = "experimental"  # Unvalidated hypotheses
    DEPRECATED = "deprecated"  # Being phased out


class PluginInterface(ABC):
    """
    Base interface for all Mnemosyne plugins.
    
    Enforces clear separation between core and experimental features.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize plugin with configuration.
        
        Args:
            config: Plugin configuration including:
                - enabled: Whether plugin is active
                - experimental: Whether this is experimental
                - hypothesis_doc: Link to hypothesis documentation
                - validation_metrics: Required validation criteria
        """
        self.config = config
        self.enabled = config.get('enabled', False)
        self.plugin_type = PluginType(config.get('type', PluginType.EXPERIMENTAL))
        self.hypothesis_doc = config.get('hypothesis_doc', '')
        self.validation_metrics = config.get('validation_metrics', {})
        self.status = PluginStatus.UNINITIALIZED
        self.initialized_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        
        # Require hypothesis doc for experimental plugins
        if self.plugin_type == PluginType.EXPERIMENTAL and not self.hypothesis_doc:
            raise ValueError(
                f"Experimental plugin {self.__class__.__name__} must provide hypothesis_doc"
            )
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize plugin resources.
        
        This method should:
        - Set up any required connections
        - Load models or data
        - Verify dependencies
        - Update status to READY or ERROR
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """
        Clean shutdown of plugin resources.
        
        This method should:
        - Close connections
        - Save state if needed
        - Release resources
        - Update status to DISABLED
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get current plugin status and metrics.
        
        Returns:
            Dictionary containing:
                - status: Current PluginStatus
                - type: PluginType
                - enabled: Whether plugin is enabled
                - initialized_at: When plugin was initialized
                - metrics: Current validation metrics (if experimental)
                - error: Error message if in ERROR state
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        List plugin capabilities.
        
        Returns:
            List of capability strings that this plugin provides
        """
        pass
    
    async def validate_hypothesis(self) -> Dict[str, Any]:
        """
        Run validation checks for experimental plugins.
        
        Returns:
            Dictionary with validation results against defined metrics
        """
        if self.plugin_type != PluginType.EXPERIMENTAL:
            return {"status": "not_applicable", "reason": "Not an experimental plugin"}
        
        results = {}
        for metric_name, metric_config in self.validation_metrics.items():
            # Subclasses should implement actual validation logic
            results[metric_name] = {
                "target": metric_config.get('target'),
                "current": None,  # To be implemented by subclass
                "status": "pending"
            }
        
        return results
    
    def require_experimental_flag(self, flag_name: str) -> None:
        """
        Check that experimental feature flag is enabled.
        
        Args:
            flag_name: Name of the feature flag to check
            
        Raises:
            ExperimentalFeatureDisabled: If flag is not enabled
        """
        from ..features import FeatureFlags
        
        if not FeatureFlags.is_enabled(flag_name):
            raise ExperimentalFeatureDisabled(
                f"Experimental feature '{flag_name}' is not enabled. "
                f"See hypothesis doc: {self.hypothesis_doc}"
            )
    
    def emit_research_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emit anonymized event to research bus.
        
        Args:
            event_type: Type of research event
            data: Event data (will be anonymized)
        """
        from ..research_bus import ResearchBus
        
        if self.plugin_type == PluginType.EXPERIMENTAL:
            # Only experimental plugins emit research events
            bus = ResearchBus()
            asyncio.create_task(
                bus.publish(
                    event_type=f"{self.__class__.__name__}.{event_type}",
                    data=data,
                    plugin_name=self.__class__.__name__
                )
            )


class ExperimentalFeatureDisabled(Exception):
    """Raised when attempting to use disabled experimental feature"""
    pass


class PluginRegistry:
    """
    Central registry for all plugins.
    
    Manages plugin lifecycle and enforces separation between
    core and experimental features.
    """
    
    def __init__(self):
        self.plugins: Dict[str, PluginInterface] = {}
        self.core_plugins: List[str] = []
        self.experimental_plugins: List[str] = []
    
    async def register(self, name: str, plugin: PluginInterface) -> None:
        """
        Register a plugin.
        
        Args:
            name: Unique plugin identifier
            plugin: Plugin instance
        """
        if name in self.plugins:
            raise ValueError(f"Plugin '{name}' already registered")
        
        self.plugins[name] = plugin
        
        if plugin.plugin_type == PluginType.CORE:
            self.core_plugins.append(name)
            logger.info(f"Registered CORE plugin: {name}")
        elif plugin.plugin_type == PluginType.EXPERIMENTAL:
            self.experimental_plugins.append(name)
            logger.warning(
                f"Registered EXPERIMENTAL plugin: {name} "
                f"(hypothesis: {plugin.hypothesis_doc})"
            )
        
        if plugin.enabled:
            await plugin.initialize()
    
    async def unregister(self, name: str) -> None:
        """
        Unregister and shutdown a plugin.
        
        Args:
            name: Plugin identifier
        """
        if name not in self.plugins:
            raise ValueError(f"Plugin '{name}' not found")
        
        plugin = self.plugins[name]
        await plugin.shutdown()
        
        del self.plugins[name]
        self.core_plugins = [p for p in self.core_plugins if p != name]
        self.experimental_plugins = [p for p in self.experimental_plugins if p != name]
        
        logger.info(f"Unregistered plugin: {name}")
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """Get plugin by name"""
        return self.plugins.get(name)
    
    def get_status_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive status report.
        
        Returns:
            Report with core and experimental plugin statuses
        """
        return {
            "core_plugins": {
                name: self.plugins[name].get_status()
                for name in self.core_plugins
            },
            "experimental_plugins": {
                name: {
                    **self.plugins[name].get_status(),
                    "hypothesis_doc": self.plugins[name].hypothesis_doc,
                    "validation": asyncio.run(
                        self.plugins[name].validate_hypothesis()
                    ) if self.plugins[name].plugin_type == PluginType.EXPERIMENTAL else None
                }
                for name in self.experimental_plugins
            },
            "summary": {
                "total_plugins": len(self.plugins),
                "core_count": len(self.core_plugins),
                "experimental_count": len(self.experimental_plugins),
                "experimental_enabled": sum(
                    1 for name in self.experimental_plugins 
                    if self.plugins[name].enabled
                )
            }
        }
    
    async def shutdown_all(self) -> None:
        """Shutdown all registered plugins"""
        for name, plugin in self.plugins.items():
            try:
                await plugin.shutdown()
                logger.info(f"Shutdown plugin: {name}")
            except Exception as e:
                logger.error(f"Error shutting down plugin '{name}': {e}")


# Global plugin registry instance
plugin_registry = PluginRegistry()