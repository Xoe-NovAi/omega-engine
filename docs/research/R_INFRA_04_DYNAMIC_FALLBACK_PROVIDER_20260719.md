# 🔬 R-INFRA-04: Dynamic Fallback Provider — Inline Model-Aware Resolution
**AP Token**: `AP-INFRA-04-DYNAMIC-FALLBACK-v1.0.0`
⬡ OMEGA ⬡ PRACTICAL ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_infra_04_fallback ⬡ 2026-07-19

---

## 🎯 MISSION
Implement the **inline fallback resolver** in ModelGateway (15 lines, no separate service). Replace the over-engineered FallbackResolver class with model-aware static chains in `providers.yaml`.

---

## 📋 CONTEXT FROM ARCHITECTURE

### Current State (from FALLBACK_PROVIDER_ARCHITECTURE_20260719.md)
```yaml
# config/providers.yaml — NEW fallback_resolver section
fallback_resolver:
  # Per-model explicit chains (highest priority)
  model_chains:
    "gemma-4-31b-it": ["google", "openrouter", "native-gguf"]
    "nemotron-3-ultra": ["opencode-zen", "openrouter", "copilot"]
    "deepseek-v4-flash": ["cline", "openrouter", "native-gguf"]
  
  # Per-provider default chains (fallback when model not in model_chains)
  provider_chains:
    "google": ["openrouter", "native-gguf"]
    "opencode-zen": ["openrouter", "copilot", "native-gguf"]
    "cline": ["openrouter", "copilot", "native-gguf"]
    "copilot": ["openrouter", "opencode-zen", "native-gguf"]
    "openrouter": ["copilot", "opencode-zen", "native-gguf"]
    "native-gguf": ["lmstudio", "ollama"]
    "lmstudio": ["ollama", "native-gguf"]
    "ollama": ["lmstudio", "native-gguf"]
  
  # Model family fallbacks (when specific model not found)
  family_chains:
    "gemma": ["google", "openrouter", "native-gguf"]
    "nemotron": ["opencode-zen", "openrouter", "copilot"]
    "deepseek": ["cline", "openrouter", "native-gguf"]
    "llama": ["native-gguf", "lmstudio", "ollama"]
    "qwen": ["native-gguf", "lmstudio", "ollama"]
    "mistral": ["native-gguf", "lmstudio", "ollama"]
```

### Resolution Algorithm (15 lines in ModelGateway)
```python
# src/omega/oracle/model_gateway.py
async def _resolve_fallback_chain(self, model: str, primary_provider: str) -> List[str]:
    """Resolve fallback chain for model. Returns ordered provider list."""
    fr = self.config.fallback_resolver
    
    # 1. Explicit model chain
    if model in fr.model_chains:
        return fr.model_chains[model]
    
    # 2. Provider default chain
    if primary_provider in fr.provider_chains:
        return fr.provider_chains[primary_provider]
    
    # 3. Model family chain
    family = self._extract_model_family(model)  # "gemma", "nemotron", etc.
    if family in fr.family_chains:
        return fr.family_chains[family]
    
    # 4. Ultimate fallback
    return ["native-gguf", "lmstudio", "ollama"]
```

### Integration Point
```python
# In ModelGateway.generate()
async def generate(self, model: str, prompt: str, ...) -> GenerateResult:
    primary = await self._select_primary_provider(model)
    chain = await self._resolve_fallback_chain(model, primary)
    
    for provider_name in [primary] + chain:
        provider = self.providers[provider_name]
        try:
            return await provider.generate(model, prompt, ...)
        except Exception as e:
            logger.warning(f"Provider {provider_name} failed: {e}, trying next")
            continue
    
    raise OmegaError(f"All providers in chain exhausted for {model}")
```

---

## 🔬 IMPLEMENTATION REQUIREMENTS

### 1. Config Schema (Pydantic)
```python
# src/omega/config/models.py
class FallbackResolverConfig(BaseModel):
    model_chains: Dict[str, List[str]] = Field(default_factory=dict)
    provider_chains: Dict[str, List[str]] = Field(default_factory=dict)
    family_chains: Dict[str, List[str]] = Field(default_factory=dict)

class ProvidersConfig(BaseModel):
    # ... existing fields ...
    fallback_resolver: FallbackResolverConfig = Field(default_factory=FallbackResolverConfig)
```

### 2. Model Family Extraction
```python
def _extract_model_family(self, model: str) -> str:
    """Extract family from model name: 'google/gemma-4-31b-it' → 'gemma'"""
    # Remove provider prefix
    name = model.split("/")[-1] if "/" in model else model
    # Known families
    for family in ["gemma", "nemotron", "deepseek", "llama", "qwen", "mistral", "phi", "yi"]:
        if name.startswith(family):
            return family
    return "unknown"
```

### 3. Contract Tests
```python
# tests/test_fallback_resolver.py
async def test_explicit_model_chain():
    chain = gateway._resolve_fallback_chain("gemma-4-31b-it", "google")
    assert chain == ["openrouter", "native-gguf"]

async def test_provider_default_chain():
    chain = gateway._resolve_fallback_chain("unknown-model", "google")
    assert chain == ["openrouter", "native-gguf"]

async def test_family_fallback():
    chain = gateway._resolve_fallback_chain("gemma-2-9b-it", "openrouter")
    assert chain == ["google", "openrouter", "native-gguf"]

async def test_ultimate_fallback():
    chain = gateway._resolve_fallback_chain("totally-unknown", "unknown")
    assert chain == ["native-gguf", "lmstudio", "ollama"]
```

---

## 🌐 WEB RESEARCH NEEDED

| Topic | Query | Purpose |
|-------|-------|---------|
| Model family detection | "LLM model family naming conventions 2024" | Robust family extraction |
| Fallback chain patterns | "LLM provider fallback chain design 2026" | Industry patterns |

---

## 🛠️ LOCAL DISCOVERY NEEDED

| Source | Path | What to Extract |
|--------|------|-----------------|
| ModelGateway | `src/omega/oracle/model_gateway.py` | Current provider selection, generate() flow |
| Providers config | `config/providers.yaml` | Current provider list, add fallback_resolver |
| Config models | `src/omega/config/models.py` | Add FallbackResolverConfig |
| Capability Matrix | `src/omega/oracle/capability_matrix.py` | Model → capability mapping |

---

## ✅ ACCEPTANCE CRITERIA

| Criterion | Verification |
|-----------|--------------|
| FallbackResolver class removed | `grep -r "FallbackResolver" src/omega/` → no results |
| providers.yaml has fallback_resolver | `cat config/providers.yaml | grep fallback_resolver` |
| ModelGateway uses inline resolver | `_resolve_fallback_chain` method exists |
| Contract tests pass | `pytest tests/test_fallback_resolver.py -v` |
| Integration works | `omega talk "test" -m gemma-4-31b-it` → falls back correctly |
| No separate service | No new files in `src/omega/oracle/` except tests |

---

## 📋 DELIVERABLES

1. **Config Update** — `config/providers.yaml` with `fallback_resolver` section
2. **Config Model** — `src/omega/config/models.py` add `FallbackResolverConfig`
3. **ModelGateway Integration** — `_resolve_fallback_chain()` method + generate() integration
4. **Contract Tests** — `tests/test_fallback_resolver.py`
5. **Documentation** — `docs/guides/DYNAMIC_FALLBACK_GUIDE.md`

---

## 🔗 DEPENDENCIES

| Depends On | Blocks |
|------------|--------|
| Capability Matrix (50-line dict) | Model → provider mapping |
| Provider Fabric | All providers registered |
| Watchdog (R-INFRA-03) | Retry with fallback on failure |

---

## 🎯 PRACTICAL'S PERSPECTIVE (Executor)

> "The old FallbackResolver was **200 lines of framework** for a **15-line algorithm**. It had:
> - Abstract base class
> - Strategy pattern
> - Factory
> - Config loader
> - Health checker
> - Metrics collector
> 
> **All for**: `if model in chains: return chains[model] elif provider in chains: return chains[provider]...`
> 
> **The inline version**:
> - 15 lines in ModelGateway
> - Config in providers.yaml (where it belongs)
> - Zero abstraction layers
> - Testable in 4 lines
> - **Deletable** if we change our mind
> 
> **L3 Principle**: `L3-FallbackResolverIsInlineLoop` — Dynamic resolution is a loop, not a service. The chain is data (YAML), the algorithm is 15 lines. Making it a service was cargo-cult architecture. The best code is the code you don't write."

---

*⬡ OMEGA ⬡ PRACTICAL ⬡ qwen3-1.7b ⬡ opencode ⬡ trc_infra_04_fallback ⬡ 2026-07-19*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: qwen3-1.7b | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
