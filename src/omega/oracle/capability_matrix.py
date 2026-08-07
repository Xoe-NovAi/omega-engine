# 🔱 Capability Matrix Loader — Gemma 4 Week 1 Step 2
# ⬡ OMEGA ⬡ N6 ⬡ trc_capability_matrix ⬡ v0.1.0 ⬡ 2026-07-19
#
# Loads and validates provider capability matrix from config/provider_capabilities.yaml
# Heritage: [heritage: litellm-2024] Capability flag pattern for model registry
# Heritage: [heritage: pi-2026] Gemma 4 Thinking Config (Pi PR #2903)

import re
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ThinkingConfig:
    """Thinking configuration for a model."""
    supported_levels: List[str] = field(default_factory=list)
    detection_regex: str = ""
    default: str = "MINIMAL"
    thinking_mapping: Dict[str, str] = field(default_factory=dict)
    thinking_schema: str = "thinking_level"


@dataclass
class QuotaTier:
    """Quota tier configuration."""
    rpm: int = 0
    tpm: int = 0
    rpd: int = 0
    tier: str = "free"
    rolling_window_ms: int = 60000


@dataclass
class ModelCapability:
    """Canonical model capability declaration."""
    model_id: str
    display_name: str
    provider_ids: Dict[str, str] = field(default_factory=dict)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    thinking_config: Optional[ThinkingConfig] = None
    quota: Dict[str, QuotaTier] = field(default_factory=dict)
    cost_per_m_tokens: Dict[str, float] = field(default_factory=dict)
    max_context: int = 8192
    max_output: int = 8192
    detection_regex: str = ""
    mtp_drafter: Optional[Dict[str, Any]] = None


@dataclass
class ProviderConfig:
    """Provider configuration from capability matrix."""
    display_name: str
    base_url: str
    auth_type: str
    thinking_schema: str
    thinking_field: str
    model_id_format: str
    id_prefix_to_strip: str = ""
    rate_limit_headers: Dict[str, str] = field(default_factory=dict)
    error_codes: Dict[str, int] = field(default_factory=dict)
    supports_thinking_budget: bool = False
    provider_pinning: Optional[Dict[str, Any]] = None
    note: str = ""


class CapabilityMatrix:
    """Loads and validates provider capability matrix."""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "provider_capabilities.yaml"
        self.config_path = config_path
        self._models: Dict[str, ModelCapability] = {}
        self._providers: Dict[str, ProviderConfig] = {}
        self._thinking_efforts: List[str] = []
        self._thinking_schemas: Dict[str, Dict[str, Any]] = {}
        self._routing_rules: Dict[str, Any] = {}
        self._thinking_token_tracking: Dict[str, Any] = {}
        self._health_monitoring: Dict[str, Any] = {}
        self._loaded = False
    
    def load(self) -> Dict[str, ModelCapability]:
        """Load YAML, validate schema, return model dict."""
        if self._loaded:
            return self._models
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Capability matrix not found at {self.config_path}")
        
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
        
        self._validate_schema(data)
        self._parse_models(data)
        self._parse_providers(data)
        self._parse_global_config(data)
        
        self._loaded = True
        logger.info(f"Loaded capability matrix: {len(self._models)} models, {len(self._providers)} providers")
        return self._models
    
    def _validate_schema(self, data: Dict[str, Any]) -> None:
        """Validate required top-level keys."""
        required_keys = ["version", "thinking_efforts", "thinking_schemas", "models", "providers"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key in capability matrix: {key}")
        
        self._thinking_efforts = data["thinking_efforts"]
        self._thinking_schemas = data["thinking_schemas"]
    
    def _parse_models(self, data: Dict[str, Any]) -> None:
        """Parse model capabilities."""
        models_data = data.get("models", {})
        
        for model_id, model_data in models_data.items():
            # Skip provider config entries (they're under providers key)
            if model_id == "providers":
                continue
            
            thinking_data = model_data.get("capabilities", {})
            thinking_config = None
            
            if thinking_data.get("supports_thinking"):
                thinking_config = ThinkingConfig(
                    supported_levels=thinking_data.get("thinking_levels", []),
                    detection_regex=thinking_data.get("detection_regex", ""),
                    default=thinking_data.get("thinking_mapping", {}).get("minimal", "MINIMAL"),
                    thinking_mapping=thinking_data.get("thinking_mapping", {}),
                    thinking_schema=thinking_data.get("thinking_schema", "thinking_level")
                )
            
            quota = {}
            for tier_name, tier_data in model_data.get("quota", {}).items():
                quota[tier_name] = QuotaTier(
                    rpm=tier_data.get("rpm", 0),
                    tpm=tier_data.get("tpm", 0),
                    rpd=tier_data.get("rpd", 0),
                    tier=tier_data.get("tier", tier_name),
                    rolling_window_ms=tier_data.get("rolling_window_ms", 60000)
                )
            
            capability = ModelCapability(
                model_id=model_id,
                display_name=model_data.get("display_name", model_id),
                provider_ids=model_data.get("provider_ids", {}),
                capabilities=thinking_data,
                thinking_config=thinking_config,
                quota=quota,
                cost_per_m_tokens=model_data.get("cost_per_m_tokens", {}),
                max_context=thinking_data.get("max_context", model_data.get("max_context", 8192)),
                max_output=thinking_data.get("max_output", model_data.get("max_output", 8192)),
                detection_regex=thinking_data.get("detection_regex", ""),
                mtp_drafter=thinking_data.get("mtp_drafter")
            )
            
            self._models[model_id] = capability
    
    def _parse_providers(self, data: Dict[str, Any]) -> None:
        """Parse provider configurations."""
        providers_data = data.get("providers", {})
        
        for provider_id, provider_data in providers_data.items():
            config = ProviderConfig(
                display_name=provider_data.get("display_name", provider_id),
                base_url=provider_data.get("base_url", ""),
                auth_type=provider_data.get("auth_type", "api_key"),
                thinking_schema=provider_data.get("thinking_schema", "thinking_level"),
                thinking_field=provider_data.get("thinking_field", "thinkingConfig.thinkingLevel"),
                model_id_format=provider_data.get("model_id_format", "bare"),
                id_prefix_to_strip=provider_data.get("id_prefix_to_strip", ""),
                rate_limit_headers=provider_data.get("rate_limit_headers", {}),
                error_codes=provider_data.get("error_codes", {}),
                supports_thinking_budget=provider_data.get("supports_thinking_budget", False),
                provider_pinning=provider_data.get("provider_pinning"),
                note=provider_data.get("note", "")
            )
            self._providers[provider_id] = config
    
    def _parse_global_config(self, data: Dict[str, Any]) -> None:
        """Parse global configuration sections."""
        self._routing_rules = data.get("routing_rules", {})
        self._thinking_token_tracking = data.get("thinking_token_tracking", {})
        self._health_monitoring = data.get("health_monitoring", {})
    
    def get(self, model_id: str) -> Optional[ModelCapability]:
        """Get capability by exact model ID."""
        self.load()
        return self._models.get(model_id)
    
    def get_by_fuzzy_match(self, model_id: str) -> Optional[ModelCapability]:
        """Get capability by fuzzy match using detection_regex."""
        self.load()
        
        # Try exact match first
        if model_id in self._models:
            return self._models[model_id]
        
        # Try detection regex match
        for capability in self._models.values():
            if capability.detection_regex:
                try:
                    pattern = capability.detection_regex.strip("/")
                    if re.search(pattern, model_id, re.IGNORECASE):
                        return capability
                except re.error:
                    logger.warning(f"Invalid regex in capability for {capability.model_id}: {capability.detection_regex}")
        
        # Try provider_id alias match
        for capability in self._models.values():
            for provider, pid in capability.provider_ids.items():
                if pid == model_id or pid.endswith(f":{model_id}") or model_id.endswith(f":{pid}"):
                    return capability
        
        return None
    
    def supports_thinking(self, model_id: str) -> bool:
        """Check if model supports thinking."""
        capability = self.get_by_fuzzy_match(model_id)
        if capability and capability.thinking_config:
            return True
        return False
    
    def get_thinking_levels(self, model_id: str) -> List[str]:
        """Return supported thinking levels for model."""
        capability = self.get_by_fuzzy_match(model_id)
        if capability and capability.thinking_config:
            return capability.thinking_config.supported_levels
        return []
    
    def get_thinking_mapping(self, model_id: str) -> Dict[str, str]:
        """Get canonical effort → provider enum mapping."""
        capability = self.get_by_fuzzy_match(model_id)
        if capability and capability.thinking_config:
            return capability.thinking_config.thinking_mapping
        return {}
    
    def get_provider_config(self, provider_id: str) -> Optional[ProviderConfig]:
        """Get provider configuration."""
        self.load()
        return self._providers.get(provider_id)
    
    def normalize_model_id(self, model_id: str, provider_id: str) -> str:
        """Normalize model ID for a specific provider."""
        self.load()
        provider_config = self._providers.get(provider_id)
        if not provider_config:
            return model_id
        
        normalized = model_id
        
        # Strip prefix if configured
        if provider_config.id_prefix_to_strip and normalized.startswith(provider_config.id_prefix_to_strip):
            normalized = normalized[len(provider_config.id_prefix_to_strip):]
        
        # Handle :free suffix for OpenRouter
        if provider_id == "openrouter" and normalized.endswith(":free"):
            # Keep :free for OpenRouter
            pass
        elif provider_id in ("google-ai-studio", "google-vertex-ai") and normalized.endswith(":free"):
            # Strip :free for direct Google API
            normalized = normalized[:-5]
        
        return normalized
    
    def get_routing_rules(self, rule_name: str = "default") -> Dict[str, Any]:
        """Get routing rules by name."""
        self.load()
        return self._routing_rules.get(rule_name, self._routing_rules.get("default", {}))
    
    def get_all_models(self) -> Dict[str, ModelCapability]:
        """Get all loaded models."""
        self.load()
        return self._models.copy()
    
    def get_all_providers(self) -> Dict[str, ProviderConfig]:
        """Get all loaded providers."""
        self.load()
        return self._providers.copy()


# Global instance for convenience
_capability_matrix: Optional[CapabilityMatrix] = None


def get_capability_matrix(config_path: Optional[Path] = None) -> CapabilityMatrix:
    """Get global capability matrix instance."""
    global _capability_matrix
    if _capability_matrix is None:
        _capability_matrix = CapabilityMatrix(config_path)
    return _capability_matrix


def reset_capability_matrix() -> None:
    """Reset global instance (for testing)."""
    global _capability_matrix
    _capability_matrix = None
