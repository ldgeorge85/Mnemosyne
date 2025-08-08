"""
Feature Flag System for Mnemosyne Dual-Track Implementation

This module provides centralized feature flag management to control
experimental features and ensure clear separation between proven
and unvalidated functionality.
"""

from typing import Dict, Any, Optional, Set, List
from enum import Enum
import json
import os
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FeatureStatus(str, Enum):
    """Feature flag status levels"""
    DISABLED = "disabled"  # Feature is completely disabled
    INTERNAL = "internal"  # Only for internal testing
    BETA = "beta"  # Available to beta users
    ENABLED = "enabled"  # Generally available
    DEPRECATED = "deprecated"  # Being phased out


class FeatureFlags:
    """
    Centralized feature flag management.
    
    Controls access to experimental features and provides
    audit trail for feature usage.
    """
    
    # Experimental feature flags
    EXPERIMENTAL_ID_COMPRESSION = "experimental.id_compression"
    EXPERIMENTAL_BEHAVIORAL_TRACKING = "experimental.behavioral_tracking"
    EXPERIMENTAL_RESONANCE = "experimental.resonance"
    EXPERIMENTAL_SYMBOLIC_IDENTITY = "experimental.symbolic_identity"
    EXPERIMENTAL_EVOLUTION_OPERATORS = "experimental.evolution_operators"
    EXPERIMENTAL_NULLIFIERS = "experimental.nullifiers"
    
    # Research feature flags
    RESEARCH_DATA_COLLECTION = "research.data_collection"
    RESEARCH_LONGITUDINAL_STUDIES = "research.longitudinal_studies"
    RESEARCH_METRICS_EXPORT = "research.metrics_export"
    
    # Core feature flags (for gradual rollout)
    CORE_MLS_MESSAGING = "core.mls_messaging"
    CORE_SPARSE_MERKLE = "core.sparse_merkle"
    CORE_MEMORY_V2 = "core.memory_v2"
    
    # Feature flag configuration
    _config: Dict[str, Dict[str, Any]] = {}
    _user_overrides: Dict[str, Dict[str, bool]] = {}
    _instance_config: Dict[str, Any] = {}
    _audit_log: List[Dict[str, Any]] = []
    
    @classmethod
    def initialize(cls, config_path: Optional[str] = None) -> None:
        """
        Initialize feature flags from configuration.
        
        Args:
            config_path: Path to feature flag configuration file
        """
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                cls._config = config.get('features', {})
                cls._instance_config = config.get('instance', {})
                logger.info(f"Loaded feature flags from {config_path}")
        else:
            # Default configuration
            cls._config = {
                # All experimental features disabled by default
                cls.EXPERIMENTAL_ID_COMPRESSION: {
                    "status": FeatureStatus.DISABLED,
                    "hypothesis_doc": "docs/hypotheses/id_compression.md",
                    "requires_consent": True,
                    "validation_required": True
                },
                cls.EXPERIMENTAL_BEHAVIORAL_TRACKING: {
                    "status": FeatureStatus.DISABLED,
                    "hypothesis_doc": "docs/hypotheses/behavioral_stability.md",
                    "requires_consent": True,
                    "validation_required": True
                },
                cls.EXPERIMENTAL_RESONANCE: {
                    "status": FeatureStatus.DISABLED,
                    "hypothesis_doc": "docs/hypotheses/resonance.md",
                    "requires_consent": True,
                    "validation_required": True
                },
                cls.EXPERIMENTAL_SYMBOLIC_IDENTITY: {
                    "status": FeatureStatus.DISABLED,
                    "hypothesis_doc": "docs/hypotheses/symbolic_identity.md",
                    "requires_consent": True,
                    "validation_required": True
                },
                cls.EXPERIMENTAL_EVOLUTION_OPERATORS: {
                    "status": FeatureStatus.DISABLED,
                    "hypothesis_doc": "docs/hypotheses/evolution_operators.md",
                    "requires_consent": False,
                    "validation_required": True
                },
                cls.EXPERIMENTAL_NULLIFIERS: {
                    "status": FeatureStatus.DISABLED,
                    "hypothesis_doc": "docs/hypotheses/nullifiers.md",
                    "requires_consent": False,
                    "validation_required": True
                },
                
                # Research features
                cls.RESEARCH_DATA_COLLECTION: {
                    "status": FeatureStatus.DISABLED,
                    "requires_consent": True,
                    "irb_approved": False
                },
                cls.RESEARCH_LONGITUDINAL_STUDIES: {
                    "status": FeatureStatus.DISABLED,
                    "requires_consent": True,
                    "irb_approved": False
                },
                
                # Core features enabled by default
                cls.CORE_MLS_MESSAGING: {
                    "status": FeatureStatus.ENABLED,
                    "stable": True
                },
                cls.CORE_SPARSE_MERKLE: {
                    "status": FeatureStatus.ENABLED,
                    "stable": True
                },
                cls.CORE_MEMORY_V2: {
                    "status": FeatureStatus.BETA,
                    "stable": False
                }
            }
            logger.info("Using default feature flag configuration")
    
    @classmethod
    def is_enabled(
        cls,
        flag: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if a feature flag is enabled.
        
        Args:
            flag: Feature flag name
            user_id: Optional user ID for per-user flags
            context: Optional context for flag evaluation
            
        Returns:
            True if feature is enabled for this context
        """
        # Check if flag exists
        if flag not in cls._config:
            logger.warning(f"Unknown feature flag: {flag}")
            return False
        
        flag_config = cls._config[flag]
        
        # Check user override first
        if user_id and user_id in cls._user_overrides:
            if flag in cls._user_overrides[user_id]:
                cls._log_access(flag, user_id, cls._user_overrides[user_id][flag], "user_override")
                return cls._user_overrides[user_id][flag]
        
        # Check instance configuration
        if flag in cls._instance_config:
            enabled = cls._instance_config[flag].get('enabled', False)
            cls._log_access(flag, user_id, enabled, "instance_config")
            return enabled
        
        # Check flag status
        status = flag_config.get('status', FeatureStatus.DISABLED)
        
        if status == FeatureStatus.DISABLED:
            cls._log_access(flag, user_id, False, "disabled")
            return False
        elif status == FeatureStatus.ENABLED:
            cls._log_access(flag, user_id, True, "enabled")
            return True
        elif status == FeatureStatus.INTERNAL:
            # Only enabled for internal users
            is_internal = context and context.get('is_internal', False)
            cls._log_access(flag, user_id, is_internal, "internal_only")
            return is_internal
        elif status == FeatureStatus.BETA:
            # Check if user is in beta program
            is_beta = context and context.get('is_beta_user', False)
            cls._log_access(flag, user_id, is_beta, "beta_only")
            return is_beta
        elif status == FeatureStatus.DEPRECATED:
            cls._log_access(flag, user_id, False, "deprecated")
            return False
        
        return False
    
    @classmethod
    def require_consent(cls, flag: str) -> bool:
        """
        Check if a feature requires user consent.
        
        Args:
            flag: Feature flag name
            
        Returns:
            True if feature requires consent
        """
        if flag not in cls._config:
            return True  # Unknown features require consent by default
        
        return cls._config[flag].get('requires_consent', False)
    
    @classmethod
    def get_hypothesis_doc(cls, flag: str) -> Optional[str]:
        """
        Get hypothesis documentation for experimental feature.
        
        Args:
            flag: Feature flag name
            
        Returns:
            Path to hypothesis documentation or None
        """
        if flag not in cls._config:
            return None
        
        return cls._config[flag].get('hypothesis_doc')
    
    @classmethod
    def get_validation_status(cls, flag: str) -> Dict[str, Any]:
        """
        Get validation status for experimental feature.
        
        Args:
            flag: Feature flag name
            
        Returns:
            Validation status information
        """
        if flag not in cls._config:
            return {"status": "unknown", "validation_required": True}
        
        config = cls._config[flag]
        return {
            "status": config.get('status'),
            "validation_required": config.get('validation_required', False),
            "hypothesis_doc": config.get('hypothesis_doc'),
            "last_validated": config.get('last_validated')
        }
    
    @classmethod
    def set_user_override(cls, user_id: str, flag: str, enabled: bool) -> None:
        """
        Set per-user feature flag override.
        
        Args:
            user_id: User ID
            flag: Feature flag name
            enabled: Whether to enable for this user
        """
        if user_id not in cls._user_overrides:
            cls._user_overrides[user_id] = {}
        
        cls._user_overrides[user_id][flag] = enabled
        logger.info(f"Set user override: {user_id} -> {flag} = {enabled}")
    
    @classmethod
    def get_experimental_features(cls) -> List[str]:
        """Get list of all experimental features"""
        return [
            flag for flag in cls._config
            if flag.startswith('experimental.')
        ]
    
    @classmethod
    def get_enabled_features(cls, user_id: Optional[str] = None) -> List[str]:
        """
        Get list of enabled features for a user.
        
        Args:
            user_id: Optional user ID
            
        Returns:
            List of enabled feature flags
        """
        enabled = []
        for flag in cls._config:
            if cls.is_enabled(flag, user_id):
                enabled.append(flag)
        return enabled
    
    @classmethod
    def get_feature_report(cls) -> Dict[str, Any]:
        """
        Generate comprehensive feature flag report.
        
        Returns:
            Report with feature statuses and metrics
        """
        experimental_count = len(cls.get_experimental_features())
        experimental_enabled = sum(
            1 for flag in cls.get_experimental_features()
            if cls._config[flag].get('status') != FeatureStatus.DISABLED
        )
        
        return {
            "features": {
                flag: {
                    "status": config.get('status'),
                    "requires_consent": config.get('requires_consent', False),
                    "is_experimental": flag.startswith('experimental.'),
                    "hypothesis_doc": config.get('hypothesis_doc')
                }
                for flag, config in cls._config.items()
            },
            "summary": {
                "total_features": len(cls._config),
                "experimental_features": experimental_count,
                "experimental_enabled": experimental_enabled,
                "core_features": len([f for f in cls._config if f.startswith('core.')]),
                "research_features": len([f for f in cls._config if f.startswith('research.')])
            },
            "audit_summary": {
                "total_accesses": len(cls._audit_log),
                "unique_users": len(set(log['user_id'] for log in cls._audit_log if log['user_id'])),
                "experimental_accesses": sum(
                    1 for log in cls._audit_log 
                    if log['flag'].startswith('experimental.')
                )
            }
        }
    
    @classmethod
    def _log_access(cls, flag: str, user_id: Optional[str], result: bool, reason: str) -> None:
        """Log feature flag access for auditing"""
        cls._audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "flag": flag,
            "user_id": user_id,
            "result": result,
            "reason": reason
        })
        
        # Rotate log if too large
        if len(cls._audit_log) > 10000:
            cls._audit_log = cls._audit_log[-5000:]
    
    @classmethod
    def export_audit_log(cls) -> List[Dict[str, Any]]:
        """Export audit log for analysis"""
        return cls._audit_log.copy()


class FeatureFlagMiddleware:
    """
    Middleware to inject feature flags into request context.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request, call_next):
        """Add feature flags to request context"""
        # Extract user ID from request (implementation depends on auth system)
        user_id = getattr(request.state, 'user_id', None)
        
        # Add feature flag checker to request
        request.state.features = FeatureFlagChecker(user_id)
        
        response = await call_next(request)
        return response


class FeatureFlagChecker:
    """Per-request feature flag checker"""
    
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id
        self._cache = {}
    
    def is_enabled(self, flag: str) -> bool:
        """Check if feature is enabled (with caching)"""
        if flag not in self._cache:
            self._cache[flag] = FeatureFlags.is_enabled(flag, self.user_id)
        return self._cache[flag]
    
    def require(self, flag: str) -> None:
        """Require feature to be enabled or raise exception"""
        if not self.is_enabled(flag):
            from .plugins import ExperimentalFeatureDisabled
            raise ExperimentalFeatureDisabled(
                f"Feature '{flag}' is not enabled for this user"
            )