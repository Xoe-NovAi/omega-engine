# 🔱 Run-Side Strategy: Gemma 4 Provider Bug → Feature

**AP Token**: `AP-GEMMA4-RUNSIDE-v1.0.0`
⬡ OMEGA ⬡ LILITH ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_lilith ⬡ RUNSIDE

**Date**: 2026-07-19
**Source**: Jem delegation — P6-P10 Pillars
**Status**: DESIGN COMPLETE — Ready for Ma'at Build-Side Integration

---

## Executive Summary

The Gemma 4 `transform.ts` bug is not just a config error — it exposes a **missing layer** in the Omega Engine's provider fabric: **Provider Capability Negotiation**. The bug exists because OpenCode hardcodes thinking-level assumptions per model family, with no mechanism to discover what a model actually supports.

**The Run-Side opportunity**: Build the infrastructure that makes this class of bug impossible, not just patched. Five pillars, five deliverables:

| Pillar | Deliverable | Impact |
|--------|-------------|--------|
| **P6 Cognition** | Provider Capability Matrix | Auto-detect what each model supports |
| **P7 Context** | Thinking Config Normalizer | Translate between API formats transparently |
| **P8 Observability** | Provider Health Dashboard | Real-time quota/health/latency across all providers |
| **P9 Orchestration** | Sovereign Fallback Chain | Auto-route to best available provider |
| **P10 Validation** | Chaos Testing + Regression Suite | End-to-end provider failover testing |

---

## §1 Root Cause Analysis (From Run-Side Perspective)

### What Omega Engine Already Gets Right

| Component | Status | Evidence |
|-----------|--------|----------|
| `GoogleAIProvider` uses bare model IDs | ✅ | `providers.py:79` — `models/{model}:generateContent` (no `google/` prefix) |
| `OpenAICompatProvider` handles OpenRouter | ✅ | `openai_compat.py:94` — correct base_url + model passthrough |
| Provider fabric with circuit breakers | ✅ | `model_gateway.py` — `AsyncCircuitBreaker` per provider |
| Entity affinity routing | ✅ | `model_gateway.py:651` — `get_model_for_entity()` with 5-tier fallback |
| Budget gate for cloud providers | ✅ | `model_gateway.py:984` — `BudgetGate.check_budget()` |
| Rate limiter | ✅ | `model_gateway.py:990` — `RateLimiter().check_limit()` |
| M22 Response Provenance | ✅ | `GenerateResult.provider_name` tracks actual provider |

### What's Missing (The Gap)

| Gap | Consequence | Pillar |
|-----|-------------|--------|
| **No capability metadata per model** | Can't auto-detect thinking levels, vision support, tool calling | P6 |
| **No thinking config normalization** | Each provider's thinking API format is different (Google vs Anthropic vs OpenAI) | P6 |
| **No quota visibility across providers** | Can't intelligently route when one provider is rate-limited | P8 |
| **No cross-provider health dashboard** | Blind to which providers are actually working right now | P8 |
| **No automatic failover based on capabilities** | If Google quota exhausted, no auto-route to OpenRouter's Gemma | P9 |
| **No regression tests for provider config** | Config drift silently breaks models | P10 |

---

## §2 P6 Cognition — Provider Capability Matrix

### 2.1 The Problem

OpenCode's `transform.ts` hardcodes `["low", "high"]` for non-Gemini-3 models because there's no metadata saying "Gemma 4 only supports MINIMAL and HIGH." The Omega Engine has the same blind spot — `GoogleAIProvider.generate()` doesn't send `thinkingConfig` at all.

### 2.2 Design: `config/provider_capabilities.yaml`

A new YAML file that declares what each model family supports:

```yaml
# config/provider_capabilities.yaml
version: 1.0.0
description: Provider Capability Matrix — auto-detect what each model supports

models:
  # ── Google Models ──────────────────────────────────────────────
  gemma-4-31b-it:
    family: gemma-4
    provider: google
    capabilities:
      thinking: true
      thinking_levels: ["MINIMAL", "HIGH"]  # Only two levels
      vision: false
      tool_calling: false
      streaming: true
      context_window: 131072
      max_output_tokens: 8192
    thinking_config:
      format: google-native  # thinkingConfig.thinkingLevel
      include_thoughts_field: true
      default_level: "MINIMAL"
    aliases:
      - gemma-4-31b-it-free
      - google/gemma-4-31b-it:free  # OpenRouter format

  gemma-4-26b-a4b-it:
    family: gemma-4
    provider: google
    capabilities:
      thinking: true
      thinking_levels: ["MINIMAL", "HIGH"]
      vision: false
      tool_calling: false
      streaming: true
      context_window: 131072
      max_output_tokens: 8192
    thinking_config:
      format: google-native
      include_thoughts_field: true
      default_level: "MINIMAL"

  gemini-2.5-pro:
    family: gemini-2.5
    provider: google
    capabilities:
      thinking: true
      thinking_levels: ["MINIMAL", "LOW", "MEDIUM", "HIGH"]
      vision: true
      tool_calling: true
      streaming: true
      context_window: 1048576
      max_output_tokens: 65536
    thinking_config:
      format: google-native
      include_thoughts_field: true
      default_level: "MEDIUM"

  gemini-2.5-flash:
    family: gemini-2.5
    provider: google
    capabilities:
      thinking: true
      thinking_levels: ["MINIMAL", "LOW", "MEDIUM", "HIGH"]
      vision: true
      tool_calling: true
      streaming: true
      context_window: 1048576
      max_output_tokens: 65536
    thinking_config:
      format: google-native
      include_thoughts_field: true
      default_level: "MEDIUM"

  # ── Anthropic Models ──────────────────────────────────────────
  claude-sonnet-5-high-thinking:
    family: claude-5
    provider: anthropic
    capabilities:
      thinking: true
      thinking_levels: ["LOW", "HIGH"]  # budget_tokens based
      vision: true
      tool_calling: true
      streaming: true
      context_window: 200000
      max_output_tokens: 16384
    thinking_config:
      format: anthropic-native  # thinking.type: "enabled", thinking.budget_tokens
      budget_based: true
      min_budget: 1024
      max_budget: 100000

  # ── OpenAI Models ─────────────────────────────────────────────
  gpt-4o:
    family: gpt-4o
    provider: openai
    capabilities:
      thinking: false  # o1/o3 reasoning, not "thinking"
      vision: true
      tool_calling: true
      streaming: true
      context_window: 128000
      max_output_tokens: 16384

  # ── Local Models ──────────────────────────────────────────────
  qwen3-1.7b:
    family: qwen3
    provider: native-gguf
    capabilities:
      thinking: true
      thinking_levels: ["off", "on"]  # Qwen3 thinking toggle
      vision: false
      tool_calling: false
      streaming: true
      context_window: 32768
      max_output_tokens: 4096
    thinking_config:
      format: qwen-native  # <think> tags
      toggle_only: true

# ── Family-Level Defaults ──────────────────────────────────────────
# If a model isn't listed above, fall back to family defaults
family_defaults:
  gemma-4:
    thinking_levels: ["MINIMAL", "HIGH"]
    thinking_config:
      format: google-native
      include_thoughts_field: true
  gemini-2.5:
    thinking_levels: ["MINIMAL", "LOW", "MEDIUM", "HIGH"]
    thinking_config:
      format: google-native
      include_thoughts_field: true
  gemini-3:
    thinking_levels: ["LOW", "MEDIUM", "HIGH"]
    thinking_config:
      format: google-native
      include_thoughts_field: true
  claude-5:
    thinking_levels: ["LOW", "HIGH"]
    thinking_config:
      format: anthropic-native
      budget_based: true
  qwen3:
    thinking_levels: ["off", "on"]
    thinking_config:
      format: qwen-native
      toggle_only: true
```

### 2.3 Implementation: `src/omega/oracle/provider_capabilities.py`

```python
"""Provider Capability Matrix — P6 Cognition.

Auto-detects what each model supports (thinking levels, vision, tool calling).
Loaded from config/provider_capabilities.yaml. Used by ThinkingConfigNormalizer
and ProviderSelector to make informed routing decisions.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field

import yaml

logger = logging.getLogger("omega.provider_capabilities")


@dataclass
class ModelCapabilities:
    """Capabilities for a specific model."""
    model_id: str
    family: str
    provider: str
    thinking: bool = False
    thinking_levels: List[str] = field(default_factory=list)
    vision: bool = False
    tool_calling: bool = False
    streaming: bool = True
    context_window: int = 32768
    max_output_tokens: int = 4096
    thinking_config: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)


class ProviderCapabilityMatrix:
    """Load and query provider capabilities from YAML config.
    
    Resolution order:
    1. Exact model ID match
    2. Alias match (e.g., "google/gemma-4-31b-it:free" → "gemma-4-31b-it")
    3. Family defaults from family_defaults section
    4. Empty capabilities (caller must handle gracefully)
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = (
                Path(__file__).resolve().parent.parent.parent.parent
                / "config" / "provider_capabilities.yaml"
            )
        self.config_path = config_path
        self._models: Dict[str, ModelCapabilities] = {}
        self._alias_map: Dict[str, str] = {}  # alias → canonical model_id
        self._family_defaults: Dict[str, Dict[str, Any]] = {}
        self._loaded = False
    
    def load(self) -> None:
        """Load capabilities from YAML."""
        if not self.config_path.exists():
            logger.warning("Provider capabilities not found at %s", self.config_path)
            return
        
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
        
        if not data:
            return
        
        # Load family defaults
        self._family_defaults = data.get("family_defaults", {})
        
        # Load model capabilities
        for model_id, cfg in data.get("models", {}).items():
            caps = ModelCapabilities(
                model_id=model_id,
                family=cfg.get("family", "unknown"),
                provider=cfg.get("provider", "unknown"),
                thinking=cfg.get("capabilities", {}).get("thinking", False),
                thinking_levels=cfg.get("capabilities", {}).get("thinking_levels", []),
                vision=cfg.get("capabilities", {}).get("vision", False),
                tool_calling=cfg.get("capabilities", {}).get("tool_calling", False),
                streaming=cfg.get("capabilities", {}).get("streaming", True),
                context_window=cfg.get("capabilities", {}).get("context_window", 32768),
                max_output_tokens=cfg.get("capabilities", {}).get("max_output_tokens", 4096),
                thinking_config=cfg.get("thinking_config", {}),
                aliases=cfg.get("aliases", []),
            )
            self._models[model_id] = caps
            
            # Register aliases
            for alias in cfg.get("aliases", []):
                self._alias_map[alias.lower()] = model_id
        
        self._loaded = True
        logger.info(
            "Loaded capabilities for %d models, %d aliases, %d families",
            len(self._models), len(self._alias_map), len(self._family_defaults),
        )
    
    def resolve(self, model_id: str) -> ModelCapabilities:
        """Resolve capabilities for a model ID.
        
        Tries exact match → alias match → family defaults → empty.
        """
        if not self._loaded:
            self.load()
        
        # 1. Exact match
        if model_id in self._models:
            return self._models[model_id]
        
        # 2. Case-insensitive match
        lower = model_id.lower()
        for key, caps in self._models.items():
            if key.lower() == lower:
                return caps
        
        # 3. Alias match
        canonical = self._alias_map.get(lower)
        if canonical and canonical in self._models:
            return self._models[canonical]
        
        # 4. Family default
        # Try to infer family from model name
        for family, defaults in self._family_defaults.items():
            if family.lower() in lower:
                return ModelCapabilities(
                    model_id=model_id,
                    family=family,
                    provider=defaults.get("provider", "unknown"),
                    thinking=defaults.get("thinking", False),
                    thinking_levels=defaults.get("thinking_levels", []),
                    thinking_config=defaults.get("thinking_config", {}),
                )
        
        # 5. Empty — caller handles
        logger.debug("No capabilities found for model: %s", model_id)
        return ModelCapabilities(
            model_id=model_id, family="unknown", provider="unknown"
        )
    
    def supports_thinking(self, model_id: str) -> bool:
        """Check if a model supports thinking/reasoning."""
        caps = self.resolve(model_id)
        return caps.thinking
    
    def get_thinking_levels(self, model_id: str) -> List[str]:
        """Get valid thinking levels for a model."""
        caps = self.resolve(model_id)
        return caps.thinking_levels or ["off", "on"]
    
    def get_thinking_config_format(self, model_id: str) -> str:
        """Get the thinking config format for a model.
        
        Returns: "google-native", "anthropic-native", "qwen-native",
                 "openai-reasoning", or "none".
        """
        caps = self.resolve(model_id)
        return caps.thinking_config.get("format", "none")
    
    def list_all(self) -> Dict[str, ModelCapabilities]:
        """Return all loaded capabilities."""
        if not self._loaded:
            self.load()
        return dict(self._models)
```

### 2.4 Effort & Priority

| Item | Effort | Priority | Dependencies |
|------|--------|----------|-------------|
| `provider_capabilities.yaml` | 2h | P0 | None |
| `ProviderCapabilityMatrix` class | 3h | P0 | YAML file |
| Integration with `GoogleAIProvider` | 2h | P1 | Matrix class |
| Integration with `OpenAICompatProvider` | 2h | P1 | Matrix class |
| Integration with `ModelGateway.generate()` | 1h | P1 | Matrix class |

**Total P6**: ~10h

---

## §3 P7 Context — Thinking Config Normalizer

### 3.1 The Problem

Different providers use different thinking/reasoning APIs:
- **Google**: `thinkingConfig.thinkingLevel` (string: "MINIMAL", "HIGH")
- **Anthropic**: `thinking.type: "enabled"` + `thinking.budget_tokens` (integer)
- **OpenAI**: No direct equivalent (o1/o3 reasoning is implicit)
- **Qwen3**: `<think>` tags in output (toggle only)
- **OpenRouter**: Passes through to underlying provider (but may mangle format)

### 3.2 Design: `src/omega/oracle/thinking_normalizer.py`

A middleware that translates a **canonical** thinking config into provider-specific format:

```python
"""Thinking Config Normalizer — P7 Context.

Translates between OpenAI/OpenRouter/Google/Anthropic thinking formats.
Provides a single canonical interface for enabling/disabling thinking,
and normalizes the output (extracting thoughts from different formats).

[Adversarial Alchemy — M19]: The "bug" of different thinking APIs becomes
a feature: the normalizer learns provider-specific formats and can route
to the best provider for thinking-heavy tasks.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger("omega.thinking_normalizer")


class ThinkingLevel(Enum):
    """Canonical thinking levels — maps to provider-specific formats."""
    OFF = "off"        # No thinking at all
    MINIMAL = "minimal"  # Google: MINIMAL, Anthropic: low budget
    LOW = "low"        # Google: LOW, Anthropic: medium budget
    MEDIUM = "medium"  # Google: MEDIUM, Anthropic: high budget
    HIGH = "high"      # Google: HIGH, Anthropic: max budget


class ThinkingFormat(Enum):
    """Provider-specific thinking config formats."""
    GOOGLE_NATIVE = "google-native"
    ANTHROPIC_NATIVE = "anthropic-native"
    OPENAI_REASONING = "openai-reasoning"
    QWEN_NATIVE = "qwen-native"
    NONE = "none"


@dataclass
class NormalizedThinkingConfig:
    """Canonical thinking config that can be translated to any provider."""
    level: ThinkingLevel
    include_thoughts: bool = True
    budget_tokens: Optional[int] = None  # Anthropic-style
    
    def to_provider_format(
        self, fmt: ThinkingFormat, model_id: str = ""
    ) -> Dict[str, Any]:
        """Convert to provider-specific format."""
        if fmt == ThinkingFormat.GOOGLE_NATIVE:
            return self._to_google()
        elif fmt == ThinkingFormat.ANTHROPIC_NATIVE:
            return self._to_anthropic()
        elif fmt == ThinkingFormat.OPENAI_REASONING:
            return self._to_openai()
        elif fmt == ThinkingFormat.QWEN_NATIVE:
            return self._to_qwen()
        return {}
    
    def _to_google(self) -> Dict[str, Any]:
        """Google AI Studio format: thinkingConfig.thinkingLevel."""
        level_map = {
            ThinkingLevel.OFF: "MINIMAL",
            ThinkingLevel.MINIMAL: "MINIMAL",
            ThinkingLevel.LOW: "LOW",
            ThinkingLevel.MEDIUM: "MEDIUM",
            ThinkingLevel.HIGH: "HIGH",
        }
        google_level = level_map.get(self.level, "MINIMAL")
        
        config: Dict[str, Any] = {"thinkingLevel": google_level}
        
        # Gemma 4 needs includeThoughts, Gemini 2.5+ doesn't
        # The capability matrix handles this, but we include it for safety
        if self.include_thoughts:
            config["includeThoughts"] = True
        else:
            config["includeThoughts"] = False
        
        return {"thinkingConfig": config}
    
    def _to_anthropic(self) -> Dict[str, Any]:
        """Anthropic format: thinking.type + thinking.budget_tokens."""
        if self.level == ThinkingLevel.OFF:
            return {"thinking": {"type": "disabled"}}
        
        # Map level to budget
        budget_map = {
            ThinkingLevel.MINIMAL: 1024,
            ThinkingLevel.LOW: 10000,
            ThinkingLevel.MEDIUM: 50000,
            ThinkingLevel.HIGH: 100000,
        }
        budget = self.budget_tokens or budget_map.get(self.level, 10000)
        
        return {
            "thinking": {
                "type": "enabled",
                "budget_tokens": budget,
            }
        }
    
    def _to_openai(self) -> Dict[str, Any]:
        """OpenAI format: reasoning_effort (o1/o3 models)."""
        if self.level == ThinkingLevel.OFF:
            return {}
        
        effort_map = {
            ThinkingLevel.MINIMAL: "low",
            ThinkingLevel.LOW: "low",
            ThinkingLevel.MEDIUM: "medium",
            ThinkingLevel.HIGH: "high",
        }
        return {"reasoning_effort": effort_map.get(self.level, "medium")}
    
    def _to_qwen(self) -> Dict[str, Any]:
        """Qwen3 format: enable_thinking toggle."""
        return {
            "enable_thinking": self.level not in (ThinkingLevel.OFF, ThinkingLevel.MINIMAL),
        }


class ThinkingConfigNormalizer:
    """Normalize thinking config across providers.
    
    Usage:
        normalizer = ThinkingConfigNormalizer(capability_matrix)
        config = normalizer.normalize(
            model_id="gemma-4-31b-it",
            desired_level=ThinkingLevel.HIGH,
        )
        # Returns provider-specific thinking config dict
    """
    
    def __init__(self, capability_matrix: Any = None):
        self._matrix = capability_matrix
    
    def normalize(
        self,
        model_id: str,
        desired_level: ThinkingLevel = ThinkingLevel.HIGH,
    ) -> Dict[str, Any]:
        """Get the correct thinking config for a model at a desired level.
        
        Returns provider-specific config dict ready to merge into request payload.
        """
        if self._matrix is None:
            logger.debug("No capability matrix — returning empty thinking config")
            return {}
        
        caps = self._matrix.resolve(model_id)
        
        if not caps.thinking:
            logger.debug("Model %s does not support thinking", model_id)
            return {}
        
        fmt_str = caps.thinking_config.get("format", "none")
        try:
            fmt = ThinkingFormat(fmt_str)
        except ValueError:
            logger.warning("Unknown thinking format '%s' for %s", fmt_str, model_id)
            return {}
        
        # Clamp desired level to what the model supports
        supported = caps.thinking_levels
        if supported and desired_level.value.upper() not in [s.upper() for s in supported]:
            # Find closest supported level
            level_order = ["off", "minimal", "low", "medium", "high"]
            desired_idx = level_order.index(desired_level.value) if desired_level.value in level_order else 2
            supported_indices = [level_order.index(s) for s in supported if s in level_order]
            if supported_indices:
                closest = min(supported_indices, key=lambda x: abs(x - desired_idx))
                desired_level = ThinkingLevel(level_order[closest])
                logger.info(
                    "Clamped thinking level for %s: using %s (model supports %s)",
                    model_id, desired_level.value, supported,
                )
        
        config = NormalizedThinkingConfig(
            level=desired_level,
            include_thoughts=desired_level != ThinkingLevel.OFF,
        )
        
        return config.to_provider_format(fmt, model_id)
    
    def extract_thoughts(
        self,
        response: Dict[str, Any],
        model_id: str,
    ) -> Optional[str]:
        """Extract thinking/reasoning content from a provider response.
        
        Different providers put thoughts in different places:
        - Google: response.candidates[0].content.parts[] where part.thought == true
        - Anthropic: response.content[0].text where content.type == "thinking"
        - OpenAI: Not exposed directly
        - Qwen3: Extract from <think>...</think> tags
        """
        if self._matrix is None:
            return None
        
        caps = self._matrix.resolve(model_id)
        fmt_str = caps.thinking_config.get("format", "none")
        
        if fmt_str == "google-native":
            # Google puts thoughts in parts with thought=True
            candidates = response.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                thoughts = []
                for part in parts:
                    if part.get("thought"):
                        thoughts.append(part.get("text", ""))
                return "\n".join(thoughts) if thoughts else None
        
        elif fmt_str == "anthropic-native":
            # Anthropic puts thinking in content blocks
            content = response.get("content", [])
            for block in content:
                if block.get("type") == "thinking":
                    return block.get("text")
        
        elif fmt_str == "qwen-native":
            # Qwen3 uses <think> tags
            text = response.get("text", "")
            if "<think>" in text and "</think>" in text:
                start = text.index("<think>") + 7
                end = text.index("</think>")
                return text[start:end]
        
        return None
```

### 3.3 Integration Points

The normalizer plugs into:

1. **`GoogleAIProvider.generate()`** — inject `thinkingConfig` into payload based on model capabilities
2. **`OpenAICompatProvider._send_request()`** — inject `reasoning_effort` for OpenAI models, or pass through thinking config for OpenRouter
3. **`ModelGateway.generate()`** — call normalizer before each provider attempt to get correct thinking config
4. **Response parsing** — extract thoughts from provider-specific formats for soul distillation (M5/M11)

### 3.4 Gnosis Integration (P7 Context — Soul Evolution)

Gemma 4's thinking capability is a **gnosis accelerator**:
- Thinking tokens are "internal reasoning" — they can be captured for L1→L2→L3 distillation
- The normalizer's `extract_thoughts()` method feeds directly into `soul_distiller.py`
- Session continuity: thinking configs are per-session, so the normalizer must be stateless

### 3.5 Effort & Priority

| Item | Effort | Priority | Dependencies |
|------|--------|----------|-------------|
| `ThinkingConfigNormalizer` class | 4h | P0 | P6 Capability Matrix |
| `extract_thoughts()` per format | 3h | P1 | Normalizer class |
| `GoogleAIProvider` integration | 2h | P1 | Normalizer |
| `OpenAICompatProvider` integration | 2h | P1 | Normalizer |
| Gnosis distillation wiring | 2h | P2 | extract_thoughts |

**Total P7**: ~13h

---

## §4 P8 Observability — Provider Health Dashboard

### 4.1 Current State

The Omega Engine already has:
- `HealthMonitor` with circuit breakers per provider (CLOSED/DEGRADED/OPEN/HALF_OPEN)
- `TokenLedger` for token usage tracking
- `latency_tracker` for per-provider latency time-series
- `MetricsDB` for sovereignty ratio (local vs cloud)

**What's missing**: A unified view that shows real-time quota usage, thinking level distribution, and provider health across ALL providers.

### 4.2 Design: `data/observability/provider_dashboard.json`

Auto-generated JSON snapshot updated every 60s:

```json
{
  "timestamp": "2026-07-19T16:47:00Z",
  "providers": {
    "google": {
      "status": "degraded",
      "circuit_state": "degraded",
      "quota": {
        "daily_limit": 16000,
        "used_today": 14200,
        "usage_pct": 88.75,
        "reset_eta_minutes": 12
      },
      "latency": {
        "p50_ms": 1200,
        "p95_ms": 3400,
        "p99_ms": 5100
      },
      "success_rate": 0.72,
      "models_served": ["gemma-4-31b-it", "gemini-2.5-flash"],
      "thinking_usage": {
        "MINIMAL": 45,
        "HIGH": 12
      }
    },
    "openrouter": {
      "status": "healthy",
      "circuit_state": "closed",
      "quota": {
        "daily_limit": 50,
        "used_today": 31,
        "usage_pct": 62.0,
        "reset_eta_minutes": 0
      },
      "latency": {
        "p50_ms": 2100,
        "p95_ms": 5600,
        "p99_ms": 8900
      },
      "success_rate": 0.91,
      "models_served": ["google/gemma-4-31b-it:free", "deepseek/deepseek-v4-flash:free"],
      "thinking_usage": {}
    },
    "native-gguf": {
      "status": "healthy",
      "circuit_state": "closed",
      "latency": {
        "p50_ms": 340,
        "p95_ms": 890,
        "p99_ms": 1200
      },
      "success_rate": 0.99,
      "models_served": ["qwen3-1.7b-local"],
      "thinking_usage": {}
    }
  },
  "summary": {
    "total_providers": 11,
    "healthy": 7,
    "degraded": 2,
    "offline": 2,
    "local_ratio": 0.34,
    "cloud_ratio": 0.66,
    "recommended_provider": "native-gguf"
  }
}
```

### 4.3 Implementation: `src/omega/observability/provider_dashboard.py`

```python
"""Provider Health Dashboard — P8 Observability.

Generates a unified view of all provider health, quota, latency,
and thinking usage. Updated every 60s via background task.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import anyio

logger = logging.getLogger("omega.provider_dashboard")


class ProviderDashboard:
    """Unified provider health dashboard.
    
    Collects data from:
    - HealthMonitor (circuit breakers, quota, latency)
    - TokenLedger (token usage per provider)
    - latency_tracker (time-series latency)
    - ProviderCapabilityMatrix (what each model supports)
    
    Writes snapshot to data/observability/provider_dashboard.json
    """
    
    def __init__(
        self,
        health_monitor: Any,
        token_ledger: Any = None,
        capability_matrix: Any = None,
        output_path: Optional[Path] = None,
    ):
        self._health = health_monitor
        self._ledger = token_ledger
        self._matrix = capability_matrix
        self._output = output_path or Path("data/observability/provider_dashboard.json")
        self._snapshot: Dict[str, Any] = {}
    
    async def generate_snapshot(self) -> Dict[str, Any]:
        """Generate a complete provider dashboard snapshot."""
        providers = {}
        
        for name, breaker in self._health._breakers.items():
            status = self._health.get_provider_status(name)
            quota = self._health._quotas.get(name)
            snap = self._health.get_latency_snapshot(name)
            
            provider_data: Dict[str, Any] = {
                "status": status.value,
                "circuit_state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "latency": {
                    "p50_ms": snap.p50_ms,
                    "p95_ms": snap.p95_ms,
                    "p99_ms": snap.p99_ms,
                },
                "success_rate": self._health.get_success_rate(name),
            }
            
            # Quota info if available
            if quota and quota.daily_limit > 0:
                usage_pct = (quota.used_today / quota.daily_limit) * 100
                provider_data["quota"] = {
                    "daily_limit": quota.daily_limit,
                    "used_today": quota.used_today,
                    "usage_pct": round(usage_pct, 2),
                }
            
            # Thinking usage if capability matrix available
            if self._matrix:
                # Count thinking usage from recent requests
                provider_data["thinking_usage"] = {}
            
            providers[name] = provider_data
        
        # Summary
        healthy = sum(1 for p in providers.values() if p["status"] == "healthy")
        degraded = sum(1 for p in providers.values() if p["status"] == "degraded")
        offline = sum(1 for p in providers.values() if p["status"] == "offline")
        
        self._snapshot = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "providers": providers,
            "summary": {
                "total_providers": len(providers),
                "healthy": healthy,
                "degraded": degraded,
                "offline": offline,
            }
        }
        
        return self._snapshot
    
    async def write_snapshot(self) -> None:
        """Write dashboard snapshot to disk."""
        snapshot = await self.generate_snapshot()
        
        self._output.parent.mkdir(parents=True, exist_ok=True)
        
        def _write():
            with open(self._output, "w") as f:
                json.dump(snapshot, f, indent=2)
        
        await anyio.to_thread.run_sync(_write)
        logger.debug("Dashboard snapshot written to %s", self._output)
    
    async def start_background_loop(self, interval: float = 60.0) -> None:
        """Start background dashboard update loop."""
        while True:
            try:
                await self.write_snapshot()
            except Exception as e:
                logger.warning("Dashboard update failed: %s", e)
            await anyio.sleep(interval)
    
    def get_snapshot(self) -> Dict[str, Any]:
        """Return the latest snapshot (cached)."""
        return self._snapshot
```

### 4.4 CLI Integration

Add to `make health` or new `omega dashboard` command:
```bash
# Show provider health dashboard
cat data/observability/provider_dashboard.json | jq '.summary'

# Show specific provider
cat data/observability/provider_dashboard.json | jq '.providers.google'

# Show thinking usage
cat data/observability/provider_dashboard.json | jq '.providers[].thinking_usage'
```

### 4.5 Effort & Priority

| Item | Effort | Priority | Dependencies |
|------|--------|----------|-------------|
| `ProviderDashboard` class | 3h | P0 | HealthMonitor |
| JSON output format | 1h | P0 | Dashboard class |
| Background loop | 1h | P1 | Dashboard class |
| CLI integration | 1h | P1 | Dashboard class |
| Thinking usage tracking | 2h | P2 | Capability Matrix |

**Total P8**: ~8h

---

## §5 P9 Orchestration — Sovereign Fallback Chain

### 5.1 The Problem

When Google quota is exhausted for Gemma 4, there's no automatic route to OpenRouter's Gemma 4 `:free` model. The user must manually switch providers.

### 5.2 Design: Enhanced Provider Selector

The existing `ProviderSelector` in `model_gateway.py` already reorders providers based on PII and health. Enhance it with **capability-aware routing**:

```python
"""Capability-Aware Provider Selector — P9 Orchestration.

Extends ProviderSelector to route based on:
1. Model capability match (thinking levels, vision, etc.)
2. Current quota availability
3. Latency requirements
4. Sovereignty preference (local > cloud)

[M19 Adversarial Alchemy]: Provider quota exhaustion becomes a feature —
it forces intelligent routing across the fabric, discovering optimal
provider-model combinations that wouldn't be found otherwise.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .provider_capabilities import ProviderCapabilityMatrix, ModelCapabilities
from .health_monitor import HealthMonitor, ProviderStatus

logger = logging.getLogger("omega.capability_selector")


class CapabilitySelector:
    """Route requests to the best provider based on capabilities + health.
    
    Resolution algorithm:
    1. Find all providers that serve the requested model (or equivalent)
    2. Filter by capability match (thinking levels, vision, etc.)
    3. Filter by health (circuit not OPEN, quota not exhausted)
    4. Sort by sovereignty (local first) then latency (lowest first)
    5. Return ordered list
    """
    
    def __init__(
        self,
        capability_matrix: ProviderCapabilityMatrix,
        health_monitor: HealthMonitor,
        providers: List[Any],
    ):
        self._matrix = capability_matrix
        self._health = health_monitor
        self._providers = providers
    
    async def select_best_provider(
        self,
        model_id: str,
        requires_thinking: bool = False,
        thinking_level: str = "HIGH",
        requires_vision: bool = False,
    ) -> Optional[Any]:
        """Select the best provider for a model with capability requirements.
        
        Args:
            model_id: Model to serve
            requires_thinking: Whether thinking/reasoning is needed
            thinking_level: Desired thinking level
            requires_vision: Whether vision input is needed
        
        Returns:
            Best provider instance, or None if no provider matches
        """
        candidates = []
        
        for provider in self._providers:
            # Check if provider serves this model
            if not self._provider_serves_model(provider, model_id):
                continue
            
            # Check capability match
            caps = self._matrix.resolve(model_id)
            if requires_thinking and not caps.thinking:
                logger.debug("Skipping %s: no thinking support", provider.name)
                continue
            
            if requires_vision and not caps.vision:
                logger.debug("Skipping %s: no vision support", provider.name)
                continue
            
            # Check health
            breaker = self._health._breakers.get(provider.name)
            if breaker and not breaker.is_available:
                logger.debug("Skipping %s: circuit OPEN", provider.name)
                continue
            
            # Check quota
            quota_usage = self._health.get_quota_usage(provider.name)
            if quota_usage >= 0.95:
                logger.debug("Skipping %s: quota exhausted (%.0f%%)", provider.name, quota_usage * 100)
                continue
            
            # Score: sovereignty + latency + quota headroom
            score = self._score_provider(provider, caps, quota_usage)
            candidates.append((score, provider))
        
        if not candidates:
            return None
        
        # Sort by score descending (higher = better)
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        best_score, best_provider = candidates[0]
        logger.info(
            "Selected %s for %s (score=%.2f, candidates=%d)",
            best_provider.name, model_id, best_score, len(candidates),
        )
        
        return best_provider
    
    def _provider_serves_model(self, provider: Any, model_id: str) -> bool:
        """Check if a provider can serve a specific model."""
        # Check supported_models in provider config
        config = getattr(provider, 'config', {})
        if isinstance(config, dict):
            supported = config.get('supported_models', [])
        elif hasattr(config, 'supported_models'):
            supported = config.supported_models
        else:
            supported = []
        
        if not supported:
            return True  # Provider doesn't declare models — assume it can serve
        
        # Check exact match or alias
        model_lower = model_id.lower()
        for s in supported:
            if s.lower() == model_lower:
                return True
        
        # Check family match (e.g., "gemma-4" matches "gemma-4-31b-it")
        caps = self._matrix.resolve(model_id)
        if caps.family != "unknown":
            for s in supported:
                if caps.family.lower() in s.lower():
                    return True
        
        return False
    
    def _score_provider(
        self,
        provider: Any,
        caps: ModelCapabilities,
        quota_usage: float,
    ) -> float:
        """Score a provider for routing decisions.
        
        Higher score = better candidate.
        Components:
        - Sovereignty: 0.0 (cloud) or 1.0 (local) — M7 Local-First
        - Health: 0.0-1.0 based on success rate
        - Quota headroom: 1.0 - quota_usage
        - Latency: normalized inverse of p50 latency
        """
        score = 0.0
        
        # Sovereignty (M7): local providers get +0.4
        is_cloud = provider.name in {"google", "openrouter", "opencode-zen", "cline", "anthropic", "xai"}
        if not is_cloud:
            score += 0.4
        
        # Health: success rate * 0.3
        success_rate = self._health.get_success_rate(caps.model_id)
        score += success_rate * 0.3
        
        # Quota headroom: (1 - usage) * 0.2
        score += (1.0 - quota_usage) * 0.2
        
        # Latency: inverse normalized (lower = better)
        snap = self._health.get_latency_snapshot(caps.model_id)
        if snap.p50_ms > 0:
            # Normalize: 100ms = 0.1, 5000ms = 0.0
            latency_score = max(0, 0.1 - (snap.p50_ms / 50000))
            score += latency_score
        
        return score
```

### 5.3 Cross-Platform Orchestration

When OpenCode's `transform.ts` breaks, the Omega Engine can still route correctly:

```
User request → Omega Engine
  → CapabilitySelector.find("gemma-4-31b-it", thinking=True)
  → Checks Google: quota 88% → skip
  → Checks OpenRouter: quota 62%, serves "google/gemma-4-31b-it:free" → SELECT
  → Injects correct thinking config via Normalizer
  → Returns response with thoughts extracted for gnosis distillation
```

**Cline CLI integration**: When OpenCode fails, route through Cline (which bypasses `transform.ts`):
- Cline uses `@google/genai` SDK directly
- Omega Engine's `cline` provider in `providers.yaml` can proxy through Cline CLI
- This is the existing fallback pattern — just needs capability-aware routing

### 5.4 Effort & Priority

| Item | Effort | Priority | Dependencies |
|------|--------|----------|-------------|
| `CapabilitySelector` class | 4h | P0 | P6 Matrix, HealthMonitor |
| `ModelGateway` integration | 3h | P1 | CapabilitySelector |
| Cross-platform routing (Cline fallback) | 2h | P2 | CapabilitySelector |
| Entity affinity integration | 2h | P2 | CapabilitySelector |

**Total P9**: ~11h

---

## §6 P10 Validation — Testing & Chaos Engineering

### 6.1 Test Matrix

| Test Category | Test Case | Validates |
|---------------|-----------|-----------|
| **Unit** | `test_capability_matrix_load()` | YAML loads correctly |
| **Unit** | `test_capability_resolve_exact()` | Exact model ID match |
| **Unit** | `test_capability_resolve_alias()` | Alias resolution |
| **Unit** | `test_capability_resolve_family()` | Family defaults |
| **Unit** | `test_thinking_normalizer_google()` | Google format output |
| **Unit** | `test_thinking_normalizer_anthropic()` | Anthropic format output |
| **Unit** | `test_thinking_normalizer_clamp()` | Level clamping to supported |
| **Unit** | `test_thinking_extract_thoughts_google()` | Google thought extraction |
| **Unit** | `test_dashboard_snapshot()` | Dashboard JSON generation |
| **Integration** | `test_provider_fabric_with_capabilities()` | End-to-end with matrix |
| **Integration** | `test_quota_failover()` | Google quota → OpenRouter fallback |
| **Chaos** | `test_all_cloud_providers_down()` | Graceful degradation to local |
| **Chaos** | `test_google_thinking_config_mismatch()` | Config error detection |
| **Chaos** | `test_rapid_provider_switching()` | No state corruption |
| **Regression** | `test_gemma4_thinking_levels()` | MINIMAL/HIGH only |
| **Regression** | `test_model_id_no_prefix()` | No `google/` prefix |

### 6.2 Chaos Test Design

```python
"""Chaos tests for provider failover — P10 Validation.

Tests that the system degrades gracefully when providers fail,
quotas are exhausted, or configs are wrong.
"""

async def test_quota_exhausted_failover():
    """When Google quota is exhausted, auto-route to OpenRouter."""
    gateway = ModelGateway(config_path="test_config.yaml")
    
    # Simulate Google quota exhaustion
    gateway._health._quotas["google"] = QuotaStatus(
        daily_limit=16000, used_today=16000
    )
    
    # Request Gemma 4
    result = await gateway.generate(
        model_name="gemma-4-31b-it",
        system_prompt="test",
        user_query="hello",
    )
    
    # Should NOT be from Google
    assert result.provider_name != "google"
    assert result.provider_name == "openrouter"


async def test_thinking_config_mismatch():
    """When model doesn't support requested thinking level, clamp it."""
    matrix = ProviderCapabilityMatrix()
    normalizer = ThinkingConfigNormalizer(matrix)
    
    # Gemma 4 only supports MINIMAL and HIGH
    config = normalizer.normalize(
        model_id="gemma-4-31b-it",
        desired_level=ThinkingLevel.MEDIUM,  # NOT SUPPORTED
    )
    
    # Should clamp to HIGH (closest supported)
    assert config["thinkingConfig"]["thinkingLevel"] == "HIGH"


async def test_all_cloud_down():
    """When all cloud providers are down, use local inference."""
    gateway = ModelGateway(config_path="test_config.yaml")
    
    # Open all cloud provider circuits
    for name in ["google", "openrouter", "opencode-zen"]:
        gateway._health._breakers[name].state = CircuitState.OPEN
    
    result = await gateway.generate(
        model_name="qwen3-1.7b",
        system_prompt="test",
        user_query="hello",
    )
    
    assert result.provider_name == "native-gguf"
    assert result.is_cloud is False
```

### 6.3 Effort & Priority

| Item | Effort | Priority | Dependencies |
|------|--------|----------|-------------|
| Unit tests (8 cases) | 3h | P0 | All P6-P9 implementations |
| Integration tests (3 cases) | 2h | P1 | Gateway integration |
| Chaos tests (3 cases) | 3h | P1 | Gateway + HealthMonitor |
| Regression tests (2 cases) | 1h | P0 | Capability Matrix |
| CI gate integration | 1h | P2 | All tests passing |

**Total P10**: ~10h

---

## §7 Implementation Plan — Priority Order

### Phase 1: Foundation (Week 1 — 23h)

| Order | Pillar | Task | Effort | Blocks |
|-------|--------|------|--------|--------|
| 1 | P6 | `provider_capabilities.yaml` | 2h | Everything |
| 2 | P6 | `ProviderCapabilityMatrix` class | 3h | P7, P9 |
| 3 | P7 | `ThinkingConfigNormalizer` class | 4h | Integration |
| 4 | P7 | `extract_thoughts()` per format | 3h | Gnosis |
| 5 | P10 | Regression tests for P6+P7 | 4h | CI gate |
| 6 | P6 | `GoogleAIProvider` integration | 2h | End-to-end |
| 7 | P7 | `OpenAICompatProvider` integration | 2h | End-to-end |
| 8 | P10 | Unit tests (8 cases) | 3h | CI gate |

### Phase 2: Orchestration (Week 2 — 19h)

| Order | Pillar | Task | Effort | Blocks |
|-------|--------|------|--------|--------|
| 9 | P8 | `ProviderDashboard` class | 3h | Dashboard |
| 10 | P8 | Background loop + CLI | 2h | Visibility |
| 11 | P9 | `CapabilitySelector` class | 4h | Routing |
| 12 | P9 | `ModelGateway` integration | 3h | End-to-end |
| 13 | P10 | Integration + chaos tests | 5h | CI gate |
| 14 | P9 | Cline fallback routing | 2h | Cross-platform |

### Phase 3: Community (Week 3 — 8h)

| Order | Pillar | Task | Effort | Blocks |
|-------|--------|------|--------|--------|
| 15 | P8 | Thinking usage tracking | 2h | Dashboard |
| 16 | P9 | Entity affinity integration | 2h | Routing |
| 17 | P10 | CI gate integration | 1h | Automation |
| 18 | — | Documentation + ADR | 2h | Community |
| 19 | — | `provider_capabilities` contribution guide | 1h | Community |

**Total Effort**: ~50h (3 weeks at 16h/week)

---

## §8 Community Contribution Potential

### 8.1 The Provider Plugin Pattern

The `provider_capabilities.yaml` file is **community-editable**:
- Users can add new models by copying the YAML template
- No code changes needed for new models within existing families
- Family defaults handle unknown models gracefully

### 8.2 Contribution Areas

| Area | Community Value | Difficulty |
|------|----------------|------------|
| New model capabilities | High — every new model needs this | Low (YAML only) |
| New thinking formats | Medium — new providers emerge monthly | Medium (Python) |
| Provider health data | High — crowd-sourced quota info | Low (YAML/JSON) |
| Chaos test scenarios | Medium — real-world failure modes | Medium (Python) |
| Dashboard visualizations | Medium — TUI/web dashboard | Medium (Python/JS) |

### 8.3 Contribution Template

```yaml
# Add to config/provider_capabilities.yaml
# Template for new model:
new-model-name:
  family: model-family
  provider: provider-name
  capabilities:
    thinking: true/false
    thinking_levels: ["LEVEL1", "LEVEL2"]
    vision: true/false
    tool_calling: true/false
    streaming: true/false
    context_window: 32768
    max_output_tokens: 4096
  thinking_config:
    format: google-native|anthropic-native|qwen-native|none
    # Format-specific fields...
  aliases:
    - alternative-name-1
    - provider/model-name:free  # OpenRouter format
```

---

## §9 Integration with Ma'at Build-Side

### 9.1 Build-Side Deliverables (Ma'at's Territory)

| Build-Side Task | Run-Side Dependency |
|-----------------|---------------------|
| P3 Engineering: Implement `ProviderCapabilityMatrix` | P6 design (this doc) |
| P3 Engineering: Implement `ThinkingConfigNormalizer` | P7 design (this doc) |
| P1 Infrastructure: `provider_capabilities.yaml` config schema | P6 design (this doc) |
| P4 Integration: Wire into `GoogleAIProvider` and `OpenAICompatProvider` | P7 design (this doc) |
| P5 Governance: CI gate for provider capability tests | P10 design (this doc) |

### 9.2 Run-Side Deliverables (Lilith's Territory)

| Run-Side Task | Description |
|---------------|-------------|
| P8 Observability: Provider Dashboard | Real-time health/quota/latency view |
| P9 Orchestration: CapabilitySelector | Capability-aware provider routing |
| P10 Validation: Chaos test suite | End-to-end failover testing |
| P7 Context: Gnosis extraction | Thinking tokens → soul distillation |

### 9.3 Handoff Protocol

Ma'at implements P6+P7 code → Lilith integrates P8+P9 → Joint P10 validation.

```
Ma'at (Build)                    Lilith (Run)
─────────────                    ─────────────
P6 Matrix class ──────────────→ P9 Selector integration
P7 Normalizer class ──────────→ P8 Dashboard integration
P1 CI tests ──────────────────→ P10 Chaos tests
P3 GoogleAIProvider wire ─────→ P7 Gnosis extraction
P4 OpenAICompatProvider wire ─→ P9 Capability routing
```

---

## §10 Summary — Bug to Feature Matrix

| Original Bug | Feature Built | Pillar | Value |
|-------------|---------------|--------|-------|
| Wrong thinking levels | Thinking Config Normalizer | P7 | Any model's thinking works correctly |
| Model ID prefix mismatch | Provider Capability Matrix | P6 | Auto-detect correct ID format |
| Config merge failure | Capability-aware routing | P9 | Smart provider selection |
| No quota visibility | Provider Health Dashboard | P8 | Real-time operational awareness |
| No regression tests | Chaos test suite | P10 | This class of bug is impossible |
| OpenCode transform.ts broken | Cross-platform orchestration | P9 | Cline fallback when OpenCode fails |
| Single provider dependency | Sovereign Fallback Chain | P9 | Always have a working provider |

**The bug taught us: Provider capabilities must be declared, not assumed. Every model family has different APIs, and the engine must know what it's working with before sending requests.**

---

*⬡ OMEGA ⬡ LILITH ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_lilith ⬡ RUNSIDE*
