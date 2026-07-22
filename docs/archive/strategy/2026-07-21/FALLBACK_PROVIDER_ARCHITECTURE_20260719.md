# 🔱 Fallback Provider Architecture
**AP Token**: `AP-FALLBACK-ARCH-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_fallback_arch ⬡ 2026-07-19

---

## 🎯 Problem Statement

Current `config/providers.yaml` has hardcoded fallbacks:
```yaml
streaming:
  fallback_on_timeout: true
  fallback_provider: native-gguff  # Same for ALL providers
```

**Issues**:
1. **Hardcoded** — requires config file edit to change
2. **One-size-fits-all** — `native-gguff` may not have the same model
3. **No model-awareness** — doesn't check if fallback provider actually has the model
4. **No priority chain** — single fallback, no cascade

---

## 🏗️ Proposed Architecture: Dynamic Fallback Resolver

### 1. Fallback Config (CVars in providers.yaml)

```yaml
# config/providers.yaml
fallback_resolver:
  enabled: true
  strategy: "model_aware"  # "model_aware" | "priority_chain" | "static"
  cvars:
    # Per-provider fallback chain (ordered)
    opencode-zen:
      - openrouter          # Same models often available
      - anthropic           # Claude models
      - google-compat       # Gemini models
      - native-gguf         # Last resort
    openrouter:
      - opencode-zen
      - anthropic
      - google-compat
      - native-gguf
    google:
      - google-compat       # Same models, different endpoint
      - openrouter
      - native-gguf
    google-compat:
      - google
      - openrouter
      - native-gguf
    anthropic:
      - openrouter
      - opencode-zen
      - native-gguf
    xai:
      - openrouter
      - native-gguf
    cline:
      - openrouter          # DeepSeek V4 Flash, MiMo
      - opencode-zen
      - native-gguf
    antigravity:
      - openrouter
      - opencode-zen
      - native-gguf
```

### 2. Fallback Resolver Service

```python
# src/omega/oracle/fallback_resolver.py
"""Dynamic fallback provider resolution with model awareness."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Set
from pathlib import Path
import yaml

@dataclass
class FallbackCandidate:
    provider: str
    has_model: bool
    priority: int
    reason: str  # "same_model" | "same_family" | "configured_chain" | "last_resort"

class FallbackResolver:
    """Resolves fallback providers dynamically based on model availability."""
    
    def __init__(self, providers_config: Dict, capability_matrix: "CapabilityMatrix"):
        self.config = providers_config.get("fallback_resolver", {})
        self.capability_matrix = capability_matrix
        self._model_provider_cache: Dict[str, Set[str]] = {}
    
    def resolve(
        self, 
        failed_provider: str, 
        model_id: str,
        exclude: List[str] = None
    ) -> List[FallbackCandidate]:
        """
        Returns ordered list of fallback candidates for a model.
        
        Resolution order:
        1. Providers with EXACT same model (from capability matrix)
        2. Providers in configured fallback chain for failed_provider
        3. Providers with same model family (fuzzy match)
        4. native-gguff (last resort)
        """
        exclude = exclude or [failed_provider]
        candidates = []
        
        # 1. Same model providers (highest priority)
        same_model_providers = self._get_providers_with_model(model_id)
        for p in same_model_providers:
            if p not in exclude:
                candidates.append(FallbackCandidate(
                    provider=p, has_model=True, priority=10,
                    reason="same_model"
                ))
        
        # 2. Configured fallback chain
        chain = self.config.get("cvars", {}).get(failed_provider, [])
        for i, p in enumerate(chain):
            if p not in exclude and p not in [c.provider for c in candidates]:
                has_model = p in same_model_providers
                candidates.append(FallbackCandidate(
                    provider=p, has_model=has_model, 
                    priority=20 - i,  # Chain order
                    reason="configured_chain" if has_model else "configured_chain_no_model"
                ))
        
        # 3. Same family (fuzzy match on model family)
        family = self._extract_model_family(model_id)
        family_providers = self._get_providers_with_family(family)
        for p in family_providers:
            if p not in exclude and p not in [c.provider for c in candidates]:
                candidates.append(FallbackCandidate(
                    provider=p, has_model=False, priority=50,
                    reason="same_family"
                ))
        
        # 4. Last resort
        if "native-gguff" not in exclude and "native-gguff" not in [c.provider for c in candidates]:
            candidates.append(FallbackCandidate(
                provider="native-gguff", has_model=False, priority=100,
                reason="last_resort"
            ))
        
        # Sort by priority, then by has_model desc
        candidates.sort(key=lambda c: (c.priority, not c.has_model))
        return candidates
    
    def _get_providers_with_model(self, model_id: str) -> Set[str]:
        """Query capability matrix for providers supporting this model."""
        if model_id in self._model_provider_cache:
            return self._model_provider_cache[model_id]
        
        providers = set()
        for provider_name, provider_config in self.config.get("providers", {}).items():
            if model_id in provider_config.get("supported_models", []):
                providers.add(provider_name)
        
        self._model_provider_cache[model_id] = providers
        return providers
    
    def _extract_model_family(self, model_id: str) -> str:
        """Extract family from model ID: 'nemotron-3-ultra' -> 'nemotron'"""
        # Remove provider prefixes
        model = model_id.split("/")[-1]
        # Remove common suffixes
        for suffix in [":free", "-free", "-it", "-unified", "-a4b"]:
            model = model.removesuffix(suffix)
        # Take first segment as family
        return model.split("-")[0]
    
    def _get_providers_with_family(self, family: str) -> Set[str]:
        """Find providers with models from same family."""
        providers = set()
        for provider_name, provider_config in self.config.get("providers", {}).items():
            for model in provider_config.get("supported_models", []):
                if self._extract_model_family(model) == family:
                    providers.add(provider_name)
        return providers
```

### 3. Integration with ModelGateway

```python
# In model_gateway.py generate()
async def generate(self, request: GenerateRequest) -> GenerateResult:
    # ... existing provider selection ...
    
    # On streaming timeout or provider error:
    except (StreamingTimeout, ProviderError) as e:
        # Resolve dynamic fallbacks
        candidates = self.fallback_resolver.resolve(
            failed_provider=current_provider,
            model_id=request.model,
            exclude=[current_provider]
        )
        
        for candidate in candidates:
            if candidate.provider not in self.providers:
                continue
            
            fallback_provider = self.providers[candidate.provider]
            logger.warning(
                f"Falling back to {candidate.provider} "
                f"(reason: {candidate.reason}, has_model: {candidate.has_model})"
            )
            
            try:
                return await fallback_provider.generate(request)
            except Exception as fallback_error:
                logger.warning(f"Fallback {candidate.provider} also failed: {fallback_error}")
                continue
        
        # All fallbacks exhausted
        raise AllFallbacksExhausted(f"No fallback succeeded for {request.model}")
```

---

## 📊 Fallback Decision Matrix

| Failed Provider | Model | 1st Fallback | 2nd Fallback | 3rd Fallback | Last Resort |
|-----------------|-------|--------------|--------------|--------------|--------------|
| opencode-zen | nemotron-3-ultra | openrouter (has it) | native-gguff | — | — |
| openrouter | deepseek-v4-flash | cline (has it) | opencode-zen | native-gguff | — |
| google | gemma-4-31b-it | google-compat (same) | openrouter | native-gguff | — |
| anthropic | claude-opus-4.8 | openrouter (has it) | opencode-zen | native-gguff | — |
| xai | grok-4.3-web | openrouter (has it) | native-gguff | — | — |
| cline | deepseek-v4-flash | openrouter (has it) | opencode-zen | native-gguff | — |

---

## ⚙️ CVars vs Hardcoded

| Approach | Pros | Cons |
|----------|------|------|
| **Hardcoded in providers.yaml** | Simple, version-controlled, reviewable | Requires redeploy to change |
| **CVars (env vars)** | Runtime configurable, per-deployment | Harder to audit, drift risk |
| **Hybrid** (config file + env override) | Best of both | More complex |

**Recommendation**: Hybrid — `providers.yaml` defines defaults, `FALLBACK_CHAIN_<PROVIDER>` env vars override at runtime.

```yaml
# providers.yaml
fallback_resolver:
  cvars:
    opencode-zen:
      - openrouter
      - anthropic
      - native-gguf
```

```bash
# Runtime override (e.g., for testing)
export FALLBACK_CHAIN_OPENCODE_ZEN="openrouter,google-compat,native-gguff"
```

---

## 🔄 Migration Plan

1. **Phase 1**: Add `fallback_resolver` section to `providers.yaml` (current PR)
2. **Phase 2**: Implement `FallbackResolver` class
3. **Phase 3**: Wire into `ModelGateway.generate()` with streaming timeout handling
4. **Phase 4**: Add contract tests for fallback resolution
5. **Phase 5**: Deprecate static `fallback_provider` field

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_fallback_arch ⬡ 2026-07-19*