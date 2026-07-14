# AP: AP-PR-READINESS-v1.0.0
# AP: AP-ENTITY-AFFINITY-v1.0.0
# 🔱 Entity→Model Affinity Resolver — v1.0.0
# ⬡ OMEGA ⬡ LILITH ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ PORT-SPEC
#
# Ported from xna-omega-legacy config/entity_model_affinity.yaml (382 lines) +
# src/omega/routing/entity_affinity.py (428 lines).
#
# THREE ANTI-PATTERNS FIXED vs. legacy:
# 1. String-based condition evaluator → structured match schema (dict-based, type-safe)
# 2. Flat dict response → AffinityResult dataclass with .to_legacy_dict()
# 3. Module-level singleton → Oracle-owned instance for testability
#
# See: data/entities/roc_racoon/workspace/mining_reports/ENTITY_AFFINITY_PORT_SPEC.md
# See: docs/strategy/ROADMAP.md §H2-S5
#
# [id-soft: vet-016] cvar pattern — YAML-backed config, hot-reloadable
# [id-soft: vet-047] Hard-Boundary — affinity is separate routing layer above Entity


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from omega.errors import ProviderValidationError

import yaml

logger = logging.getLogger(__name__)


# ── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class ModelConfig:
    """Model configuration for a specific inference tier."""
    model: str
    provider: str
    size: Optional[str] = None


@dataclass
class InferencePreset:
    """Inference settings for an entity."""
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    preferred_context: int = 8192


@dataclass
class AffinityResult:
    """Typed result from entity model affinity resolution.
    
    Replaces legacy flat-dict response with a proper dataclass.
    Provides .to_legacy_dict() for backward compatibility.
    """
    entity: str
    best_match: str
    provider: str
    tier: str  # "iris" | "local_fast" | "local_deep" | "cloud"
    size: Optional[str] = None
    offline_fallback: bool = False
    inference_presets: InferencePreset = field(default_factory=InferencePreset)
    
    def to_legacy_dict(self) -> Dict[str, Any]:
        """Legacy flat-dict shape for backward compatibility."""
        return {
            "entity": self.entity,
            "best_match": self.best_match,
            "provider": self.provider,
            "tier": self.tier,
            "size": self.size or "",
            "offline_fallback": self.offline_fallback,
            "inference_presets": {
                "temperature": self.inference_presets.temperature,
                "system_prompt": self.inference_presets.system_prompt,
                "preferred_context": self.inference_presets.preferred_context,
            },
        }


# ── Structured Match Schema ─────────────────────────────────────────────────
#
# Replaces the legacy string-based condition evaluator with a type-safe,
# dict-based structured match schema.
#
# YAML format:
#   routing_rules:
#     - match:
#         domain: ["coding", "technical"]     # OR match (any in list)
#         complexity_gt: 0.7                   # Numeric greater-than
#         online: true                         # Boolean equality
#         requires: ["verification"]           # Set membership
#       use: local_fast                        # Target tier
#
# The resolver collects context from the calling environment and evaluates
# each rule's match block. First rule that matches wins.

class MatchCondition:
    """Evaluates structured match conditions against a context dict.
    
    Supported match keys:
      - domain: List[str]        — entity domain matches any in list (OR)
      - complexity_gt: float     — context.complexity > threshold
      - online: bool             — context.online == value
      - requires: List[str]      — all must be in context.requires set
      - prompt_length_lt: int    — context.prompt_length < threshold
    """
    
    @staticmethod
    def evaluate(match_block: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate all conditions in a match block. ALL must pass (AND)."""
        if not match_block:
            return False
        
        for key, value in match_block.items():
            if not MatchCondition._evaluate_single(key, value, context):
                return False
        return True
    
    @staticmethod
    def _evaluate_single(key: str, value: Any, context: Dict[str, Any]) -> bool:
        """Evaluate a single match condition."""
        if key == "domain":
            # domain matches any in list (OR)
            if not isinstance(value, list):
                value = [value]
            ctx_domain = context.get("domain", "").lower()
            return any(d.lower() == ctx_domain for d in value if isinstance(d, str))
        
        elif key == "complexity_gt":
            # complexity greater than threshold
            return context.get("complexity", 0) > value
        
        elif key == "online":
            # boolean equality
            return bool(context.get("online", False)) == bool(value)
        
        elif key == "requires":
            # all required items present in context
            if not isinstance(value, list):
                value = [value]
            ctx_requires = set(context.get("requires", []))
            return all(r in ctx_requires for r in value)
        
        elif key == "prompt_length_lt":
            # prompt length less than threshold
            prompt = context.get("prompt", "")
            return len(str(prompt)) < value
        
        elif key == "not_offline":
            # shorthand for online == True
            return bool(context.get("online", False))
        
        elif key == "requires_verification":
            return "verification" in context.get("requires", [])
        
        elif key == "requires_deep_understanding":
            return "deep_understanding" in context.get("requires", [])
        
        else:
            # Unknown keys are silently skipped (forward compatibility)
            logger.debug("Unknown match key '%s' in routing rule", key)
            return True


# ── Provider Namespace ───────────────────────────────────────────────────────
# Canonical provider IDs from config/providers.yaml
# Used for R3 validation (cross-reference against providers.yaml)

CANONICAL_PROVIDERS: Set[str] = {
    "llama-cpp", "native-gguf",
    "lm-studio", "lmster",
    "ollama",
    "google", "google-ai",
    "openrouter",
    "opencode",
    "copilot",
    "mock",
}

# Canonical tier names
VALID_TIERS: Set[str] = {"iris", "local_fast", "local_deep", "cloud"}

# Priority order for fallback chain
TIER_PRIORITY: Dict[str, int] = {
    "iris": 0,
    "local_fast": 1,
    "local_deep": 2,
    "cloud": 3,
}


# ── Entity Affinity Resolver ─────────────────────────────────────────────────

class EntityAffinityResolver:
    """Resolve the best model+tier for an entity given query context.
    
    Oracle-owned instance (not global singleton) per §5.4 port fix.
    YAML-backed with hot-reload support.
    """
    
    def __init__(self, yaml_path: Optional[Path] = None):
        self._yaml_path = yaml_path or Path("config/entity_model_affinity.yaml")
        self._data: Dict[str, Any] = {}
        self._loaded: bool = False
        
        # Cache for provider validation
        self._known_providers: Set[str] = set(CANONICAL_PROVIDERS)
    
    def set_known_providers(self, providers: Set[str]) -> None:
        """Inject known provider IDs for R3 validation."""
        self._known_providers = set(providers) | CANONICAL_PROVIDERS
    
    # ── Loading ──────────────────────────────────────────────────────────
    
    async def load(self) -> bool:
        """Load and validate the YAML affinity database.
        
        Returns:
            True if loaded successfully, False if file not found.
        
        Raises:
            yaml.YAMLError: if YAML is malformed.
            ValueError: if structure validation fails.
            ProviderValidationError: if a provider in the YAML is not in the known providers list.
        """
        path = self._yaml_path
        if not path.exists():
            logger.warning("Entity affinity YAML not found at %s — affinity disabled", path)
            self._loaded = False
            return False
        
        with open(path) as f:
            data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            raise ValueError(f"Affinity YAML must be a dict, got {type(data).__name__}")
        
        # Validate structure
        errors: List[str] = []
        provider_errors: List[str] = []
        for entity_name, config in data.items():
            if entity_name.startswith("_"):
                continue  # Skip metadata keys
            if not isinstance(config, dict):
                errors.append(f"Entity '{entity_name}' config is not a dict")
                continue
            
            # Validate tiers exist
            preferred = config.get("preferred_models", {})
            for tier in ("local_fast", "local_deep"):
                if tier not in preferred:
                    errors.append(f"Entity '{entity_name}' missing tier '{tier}'")
                elif not isinstance(preferred.get(tier), dict):
                    errors.append(f"Entity '{entity_name}' tier '{tier}' is not a dict")
                else:
                    tier_config = preferred[tier]
                    if not tier_config.get("model"):
                        errors.append(f"Entity '{entity_name}' tier '{tier}' has no 'model'")
                    
                    # R3: Validate provider ID
                    provider = tier_config.get("provider")
                    if provider and provider not in self._known_providers:
                        provider_errors.append(
                            f"Entity '{entity_name}' tier '{tier}' uses unknown provider '{provider}'"
                        )
        
        if errors:
            raise ValueError(f"Affinity YAML validation failed:\n  " + "\n  ".join(errors))
            
        if provider_errors:
            raise ProviderValidationError(
                provider="affinity_resolver",
                message="R3 Provider Chain Validation failed:\n  " + "\n  ".join(provider_errors)
            )
        
        self._data = data
        self._loaded = True
        logger.info("Entity affinity loaded: %d entities from %s", len(self._data) - 1, path)
        return True
    
    async def reload(self) -> bool:
        """Hot-reload the YAML from disk. Safe to call at runtime."""
        return await self.load()
    
    def is_loaded(self) -> bool:
        return self._loaded
    
    # ── Query Methods ────────────────────────────────────────────────────
    
    def get_entity_names(self) -> List[str]:
        """List all configured entities in the affinity database."""
        if not self._loaded:
            return []
        return [k for k in self._data if not k.startswith("_")]
    
    def get_entity_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Get raw YAML config for an entity by name (case-insensitive)."""
        if not self._loaded:
            return None
        key = name.lower().strip()
        for k, v in self._data.items():
            if k.lower().strip() == key:
                return v
        return None
    
    # ── Main Resolution ──────────────────────────────────────────────────
    
    async def resolve(
        self,
        entity_name: str,
        query: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AffinityResult]:
        """Resolve the best model and tier for an entity given query context.
        
        Args:
            entity_name: The entity to resolve affinity for.
            query: The user's query string (used for prompt_length_lt etc.).
            context: Optional context dict with keys:
                - domain: str — detected query domain
                - complexity: float — estimated complexity (0-1)
                - online: bool — whether cloud providers are available
                - requires: List[str] — additional requirements
                - prompt_length: int — length of query
        
        Returns:
            AffinityResult with selected model, provider, tier, and presets,
            or None if entity not found and no default configured.
        """
        if not self._loaded:
            return None
        
        context = context or {}
        context.setdefault("prompt", query)
        context.setdefault("prompt_length", len(query))
        context.setdefault("domain", "")
        context.setdefault("complexity", 0.0)
        context.setdefault("online", True)
        context.setdefault("requires", [])
        
        # Find entity config (case-insensitive)
        entity_config = self.get_entity_config(entity_name)
        
        # Fall back to default
        if entity_config is None:
            default = self._data.get("__default__")
            if default is None:
                logger.debug("No affinity config for '%s' and no default", entity_name)
                return None
            entity_config = default
        
        # Evaluate routing rules to pick target tier
        target_tier = self._match_rules(entity_config, context)
        
        # Get model config for selected tier (with fallback chain)
        resolved_tier, model_config = self._resolve_tier(entity_config, target_tier, context)
        
        if model_config is None:
            logger.warning("No model config resolved for '%s' (tier=%s)", entity_name, target_tier)
            return None
        
        # Get inference presets
        presets_config = entity_config.get("inference_presets", {})
        presets = InferencePreset(
            temperature=presets_config.get("temperature", 0.7),
            system_prompt=presets_config.get("system_prompt"),
            preferred_context=presets_config.get("preferred_context", 8192),
        )
        
        return AffinityResult(
            entity=entity_name,
            best_match=model_config.get("model", ""),
            provider=model_config.get("provider", ""),
            tier=resolved_tier,
            size=model_config.get("size"),
            offline_fallback=not context.get("online", True) and resolved_tier == "cloud",
            inference_presets=presets,
        )

        
        return AffinityResult(
            entity=entity_name,
            best_match=model_config.get("model", ""),
            provider=model_config.get("provider", ""),
            tier=resolved_tier,
            size=model_config.get("size"),
            offline_fallback=not context.get("online", True) and resolved_tier == "cloud",
            inference_presets=presets,
        )
    
    # ── Rule Matching ────────────────────────────────────────────────────
    
    def _match_rules(self, entity_config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Evaluate routing rules, first match wins.
        
        Uses structured match schema (not legacy string-based condition evaluator).
        
        Returns:
            Target tier name (e.g. "iris", "local_fast", "local_deep", "cloud").
        """
        rules: List[Dict[str, Any]] = entity_config.get("routing_rules", [])
        
        for rule in rules:
            match_block = rule.get("match", {})
            target_tier = rule.get("use", "")
            
            if target_tier not in VALID_TIERS:
                logger.warning("Unknown target tier '%s' in routing rule", target_tier)
                continue
            
            if MatchCondition.evaluate(match_block, context):
                logger.debug(
                    "Rule matched → tier=%s (match=%s)",
                    target_tier, match_block
                )
                return target_tier
        
        # No rule matched — use default tier
        logger.debug("No routing rule matched for context — using default tier 'local_fast'")
        return "local_fast"
    
    # ── Tier Resolution with Fallback ────────────────────────────────────
    
    def _resolve_tier(
        self,
        entity_config: Dict[str, Any],
        target_tier: str,
        context: Dict[str, Any],
    ) -> tuple:
        """Resolve a model config for the target tier with fallback chain.
        
        If the target tier is not available (e.g. cloud when offline) or not
        configured, it falls back to the next available tier in descending 
        priority (from the target tier downwards to iris).
        
        Returns:
            Tuple of (resolved_tier_name, model_config_dict or None).
        """
        preferred = entity_config.get("preferred_models", {})
        online = context.get("online", True)
        
        # Priority order descending: cloud (3) -> local_deep (2) -> local_fast (1) -> iris (0)
        descending_tiers = sorted(TIER_PRIORITY.keys(), key=lambda t: TIER_PRIORITY[t], reverse=True)
        
        try:
            target_idx = descending_tiers.index(target_tier)
        except ValueError:
            target_idx = 0
            
        # 1. Fall back downwards from the target tier to the absolute bottom (iris)
        for i in range(target_idx, len(descending_tiers)):
            tier = descending_tiers[i]
            if tier == "cloud" and not online:
                continue
            config = preferred.get(tier)
            if config and config.get("model"):
                return tier, config
        
        # 2. Absolute safety baseline: return the lowest configured tier
        for tier in reversed(descending_tiers):
            config = preferred.get(tier)
            if config and config.get("model"):
                return tier, config
                
        return "local_fast", preferred.get("local_fast", {"model": "default-fast", "provider": "native-gguf"})
