# 🔱 Gemma 4 Bug-to-Feature Strategy — Build Side (P1-P5)

**AP Token**: `AP-GEMMA4-FEATURE-v1.0.0`
⬡ OMEGA ⬡ MAAT ⬡ {session_model} ⬡ opencode ⬡ trc_maat ⬡ GEMMA4-FEATURE

**Date**: 2026-07-19
**Purpose**: Transform the OpenCode `transform.ts` Gemma 4 bug into a sovereign provider pattern.

---

## Executive Summary

The OpenCode CLI's `transform.ts` sends incorrect parameters for Gemma 4 models:
1. Wrong model prefix (`google/gemma-4-31b-it` vs `gemma-4-31b-it`)
2. Wrong thinking levels (`LOW`/`HIGH` vs `MINIMAL`/`HIGH`)
3. Missing `thinkingLevel` in base config
4. Config merge failure excluding Gemma 4

**Cline CLI works** because it bypasses OpenCode's `transform.ts` entirely.

**The Pi project fixed this 3 months ago** (PR #2903) with regex detection + thinking level mapping.

**Our opportunity**: Build a **Sovereign Provider Pattern** that works across OpenCode, Cline, and Omega Engine — turning a bug into a reusable architecture for any model with non-standard API requirements.

---

## 🏗️ P1 Infrastructure — Provider Architecture

### Current State
- `GoogleAIProvider` in `providers.py` uses raw Google API
- No thinking config support for Gemma 4
- Model registry has Gemma 4 cards but no thinking config metadata
- OpenCode's `transform.ts` is the source of the bug

### Required Changes

#### 1.1 Provider Config Extension
**File**: `config/providers.yaml` (lines 129-139)
**Change**: Add thinking config metadata to Google provider

```yaml
google:
  priority: 4
  enabled: true
  description: "Google AI Studio / Vertex AI - Google's own models only"
  api_key: "env:GOOGLE_API_KEY"
  thinking_config:
    gemma_4:
      supported_levels: ["MINIMAL", "HIGH"]
      level_mapping:
        minimal: "MINIMAL"
        low: "MINIMAL"
        medium: "HIGH"
        high: "HIGH"
      include_thoughts: true
    gemini_3:
      supported_levels: ["MINIMAL", "LOW", "MEDIUM", "HIGH"]
      level_mapping:
        minimal: "MINIMAL"
        low: "LOW"
        medium: "MEDIUM"
        high: "HIGH"
      include_thoughts: true
    gemini_2:
      supported_levels: ["MINIMAL", "LOW", "MEDIUM", "HIGH"]
      level_mapping:
        minimal: "MINIMAL"
        low: "LOW"
        medium: "MEDIUM"
        high: "HIGH"
      include_thoughts: true
  supported_models:
    - "gemma-4-31b-it-free"
    - "gemma-4-26b-a4b-it-free"
    - "gemini-2.5-pro"
    - "gemini-2.5-flash"
```

**Effort**: 30 minutes
**Priority**: P0 — Blocks all other work

#### 1.2 Model Registry Extension
**File**: `config/model_registry/models/cloud/gemma-4-31b-it-free.yaml.md`
**Change**: Add thinking config metadata to model card

```yaml
thinking_config:
  api_format: "thinkingLevel"
  supported_levels: ["MINIMAL", "HIGH"]
  level_mapping:
    minimal: "MINIMAL"
    low: "MINIMAL"
    medium: "HIGH"
    high: "HIGH"
  include_thoughts: true
  disable_method: "thinkingLevel: MINIMAL"
```

**Effort**: 15 minutes
**Priority**: P0 — Model card is source of truth

#### 1.3 Gateway Routing Extension
**File**: `src/omega/oracle/model_gateway.py` (lines 411-422)
**Change**: Add thinking config resolution to provider map

```python
provider_map = {
    "google": GoogleAIProvider,  # Already handles thinking config
    # ... existing providers
}
```

**Effort**: 1 hour
**Priority**: P1 — Gateway needs to pass thinking config

---

## 💾 P2 Persistence — Config & Model Cards

### Current State
- Global OpenCode config (`~/.config/opencode/opencode.json`) has Gemma 4 variants
- Project config (`opencode.json`) removed Google provider section
- Model registry has Gemma 4 cards but no thinking config metadata

### Required Changes

#### 2.1 OpenCode Config Package
**File**: `config/opencode/gemma4-provider.json` (NEW)
**Purpose**: Reusable OpenCode config for Gemma 4

```json
{
  "provider": {
    "google": {
      "whitelist": ["gemma-4-31b-it", "gemma-4-26b-a4b-it"],
      "models": {
        "gemma-4-31b-it": {
          "name": "Gemma 4 31B (Google API)",
          "limit": { "context": 262144, "output": 32768 },
          "modalities": { "input": ["text", "image"], "output": ["text"] },
          "variants": {
            "low": { "thinkingConfig": { "thinkingLevel": "minimal", "includeThoughts": false } },
            "high": { "thinkingConfig": { "thinkingLevel": "high", "includeThoughts": true } }
          }
        },
        "gemma-4-26b-a4b-it": {
          "name": "Gemma 4 26B A4B (Google API)",
          "limit": { "context": 262144, "output": 32768 },
          "modalities": { "input": ["text", "image", "video"], "output": ["text"] },
          "variants": {
            "low": { "thinkingConfig": { "thinkingLevel": "minimal", "includeThoughts": false } },
            "high": { "thinkingConfig": { "thinkingLevel": "high", "includeThoughts": true } }
          }
        }
      }
    }
  }
}
```

**Effort**: 30 minutes
**Priority**: P0 — Community contribution potential

#### 2.2 Model Card Template Extension
**File**: `config/model_registry/model_card_template.yaml.md`
**Change**: Add thinking config section to template

```yaml
thinking_config:
  api_format: "thinkingLevel" | "thinkingBudget" | "none"
  supported_levels: ["MINIMAL", "LOW", "MEDIUM", "HIGH"]
  level_mapping:
    minimal: "MINIMAL"
    low: "LOW"
    medium: "MEDIUM"
    high: "HIGH"
  include_thoughts: true | false
  disable_method: "thinkingLevel: MINIMAL" | "thinkingBudget: 0" | "none"
```

**Effort**: 15 minutes
**Priority**: P1 — Enables future model cards

#### 2.3 Cline Config Package
**File**: `config/cline/gemma4-provider.json` (NEW)
**Purpose**: Reusable Cline config for Gemma 4

```json
{
  "providers": {
    "my-google": {
      "baseUrl": "https://generativelanguage.googleapis.com/v1beta",
      "api": "google-generative-ai",
      "apiKey": "GEMINI_API_KEY",
      "models": [
        {
          "id": "gemma-4-31b-it",
          "name": "Gemma 4 31B",
          "input": ["text", "image"],
          "contextWindow": 262144,
          "reasoning": true
        }
      ]
    }
  }
}
```

**Effort**: 30 minutes
**Priority**: P1 — Cross-platform integration

---

## ⚙️ P3 Engineering — Code Changes

### Current State
- `GoogleAIProvider` in `providers.py` uses raw Google API
- No thinking config support
- Model ID format not validated

### Required Changes

#### 3.1 GoogleAIProvider Enhancement
**File**: `src/omega/oracle/providers.py` (lines 68-134)
**Change**: Add thinking config support

```python
class GoogleAIProvider(BaseProvider):
    """Google AI Studio provider (handles Gemini and Gemma models)."""
    
    # Model family detection
    GEMMA_4_PATTERN = re.compile(r'gemma-?4', re.IGNORECASE)
    GEMINI_3_PATTERN = re.compile(r'gemini-3', re.IGNORECASE)
    GEMINI_2_PATTERN = re.compile(r'gemini-2', re.IGNORECASE)
    
    def _detect_model_family(self, model: str) -> str:
        """Detect model family for thinking config routing."""
        if self.GEMMA_4_PATTERN.search(model):
            return "gemma_4"
        if self.GEMINI_3_PATTERN.search(model):
            return "gemini_3"
        if self.GEMINI_2_PATTERN.search(model):
            return "gemini_2"
        return "unknown"
    
    def _get_thinking_config(self, model: str, thinking_level: Optional[str] = None) -> dict:
        """Get thinking config for model family."""
        family = self._detect_model_family(model)
        
        if family == "gemma_4":
            # Gemma 4 only supports MINIMAL and HIGH
            level = "MINIMAL" if thinking_level in ["minimal", "low"] else "HIGH"
            return {
                "thinkingConfig": {
                    "thinkingLevel": level,
                    "includeThoughts": level == "HIGH"
                }
            }
        elif family in ["gemini_3", "gemini_2"]:
            # Gemini 3.x supports full range
            level = (thinking_level or "high").upper()
            return {
                "thinkingConfig": {
                    "thinkingLevel": level,
                    "includeThoughts": True
                }
            }
        return {}
    
    def _normalize_model_id(self, model: str) -> str:
        """Normalize model ID format for Google API."""
        # Remove google/ prefix if present
        if model.startswith("google/"):
            model = model[7:]
        # Ensure proper format
        return model
    
    async def generate(self, model: str, system_prompt: str, user_query: str, 
                      temperature: float, max_tokens: int, 
                      thinking_level: Optional[str] = None,
                      trace_id: Optional[str] = None, 
                      session_id: Optional[str] = None,
                      logit_bias: Optional[Dict[int, float]] = None, 
                      repetition_penalty: float = 1.0, 
                      api_key: Optional[str] = None) -> Optional[str]:
        # Normalize model ID
        model = self._normalize_model_id(model)
        
        # Use provided api_key or fallback to the sovereign vault
        key = api_key or _resolve_google_api_key()
        if not key:
            raise ProviderAuthError(provider="google", message="No Google API key provided", trace_id=trace_id)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\nUser: {user_query}"}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "repetitionPenalty": repetition_penalty,
            }
        }
        
        # Add thinking config
        thinking_config = self._get_thinking_config(model, thinking_level)
        if thinking_config:
            payload["generationConfig"].update(thinking_config)
        
        if logit_bias:
            payload["generationConfig"]["logitBias"] = logit_bias
        
        # ... rest of implementation
```

**Effort**: 2-3 hours
**Priority**: P0 — Core fix

#### 3.2 Model Gateway Integration
**File**: `src/omega/oracle/model_gateway.py` (lines 285-300)
**Change**: Pass thinking config through gateway

```python
async def generate_with_thinking(self, model: str, system_prompt: str, user_query: str,
                                thinking_level: Optional[str] = None, **kwargs) -> GenerateResult:
    """Generate with thinking config support."""
    # ... existing generate logic
    # Pass thinking_level to provider
    result = await provider.generate(
        model=model,
        system_prompt=system_prompt,
        user_query=user_query,
        thinking_level=thinking_level,
        **kwargs
    )
    # ... rest of implementation
```

**Effort**: 1 hour
**Priority**: P1 — Gateway integration

#### 3.3 Provider Health Monitor Extension
**File**: `src/omega/oracle/health_monitor.py`
**Change**: Add thinking config validation

```python
def validate_thinking_config(provider_name: str, model: str, thinking_config: dict) -> bool:
    """Validate thinking config for model family."""
    # Check if model supports thinking
    # Check if thinking level is valid for model family
    # Log warning if config is invalid
    pass
```

**Effort**: 1 hour
**Priority**: P2 — Quality gate

---

## 🔗 P4 Integration — Cross-Platform

### Current State
- OpenCode has Gemma 4 variants in global config
- Cline works with direct API
- Omega Engine has GoogleAIProvider but no thinking config

### Required Changes

#### 4.1 OpenCode Upstream Contribution
**File**: `packages/opencode/src/provider/transform.ts` (upstream)
**Change**: Add Gemma 4 detection and thinking level mapping

```typescript
function isGemma4Model(apiId: string): boolean {
  return /gemma-?4/.test(apiId.toLowerCase());
}

function googleThinkingLevelEfforts(apiId: string) {
  const id = apiId.toLowerCase()
  if (isGemma4Model(id)) return ["minimal", "high"]  // NEW
  if (!id.includes("gemini-3")) return ["low", "high"]
  // ... existing logic
}

function getThinkingLevel(effort: string, model: Provider.Model): string {
  if (isGemma4Model(model.api.id)) {
    switch (effort) {
      case "minimal":
      case "low":
        return "MINIMAL";
      case "medium":
      case "high":
        return "HIGH";
    }
  }
  // ... existing logic
}
```

**Effort**: 2-4 hours (PR preparation + testing)
**Priority**: P1 — Community contribution

#### 4.2 Community Config Package
**File**: `packages/gemma4-opencode-config/` (NEW)
**Purpose**: Installable config package for OpenCode users

```
packages/gemma4-opencode-config/
├── README.md
├── install.sh
├── opencode.json
└── docs/
    └── GEMMA4_SETUP.md
```

**Effort**: 2-3 hours
**Priority**: P2 — Community value

#### 4.3 Provider Adapter Pattern
**File**: `src/omega/oracle/backends/google_compat.py` (NEW)
**Purpose**: Google-specific provider adapter

```python
class GoogleCompatProvider(OpenAICompatProvider):
    """Google AI Studio provider with thinking config support."""
    
    async def _send_request(self, model_name: str, system_prompt: str, user_query: str,
                           temperature: float, max_tokens: int, 
                           thinking_level: Optional[str] = None, **kwargs) -> str:
        """Send request with thinking config."""
        # Detect model family
        # Apply thinking config
        # Normalize model ID
        # Send request
        pass
```

**Effort**: 3-4 hours
**Priority**: P1 — Reusable pattern

---

## 🛡️ P5 Governance — Mandates & Quality

### Mandate Compliance

| Mandate | Impact | Action |
|---------|--------|--------|
| **M7 Local-First** | Gemma 4 is cloud-only | Document as cloud fallback, ensure local-first priority |
| **M16 Modularization** | Provider adapter pattern | Ensure no hardcoded paths, use config-driven |
| **M22 Response Provenance** | Track thinking config | Log thinking level in GenerateResult |
| **M9 Error Integrity** | Thinking config errors | Typed errors for invalid thinking levels |
| **M13 Temple-Grade** | Code quality | Pass T1-T11 gates |

### Quality Gates

#### 5.1 Test Coverage
**File**: `tests/test_google_thinking_config.py` (NEW)
**Purpose**: Validate thinking config for all model families

```python
def test_gemma4_thinking_config():
    """Test Gemma 4 thinking config mapping."""
    provider = GoogleAIProvider("google", {})
    
    # Test MINIMAL
    config = provider._get_thinking_config("gemma-4-31b-it", "minimal")
    assert config["thinkingConfig"]["thinkingLevel"] == "MINIMAL"
    assert config["thinkingConfig"]["includeThoughts"] == False
    
    # Test HIGH
    config = provider._get_thinking_config("gemma-4-31b-it", "high")
    assert config["thinkingConfig"]["thinkingLevel"] == "HIGH"
    assert config["thinkingConfig"]["includeThoughts"] == True
    
    # Test invalid level maps to HIGH
    config = provider._get_thinking_config("gemma-4-31b-it", "medium")
    assert config["thinkingConfig"]["thinkingLevel"] == "HIGH"

def test_model_id_normalization():
    """Test model ID normalization."""
    provider = GoogleAIProvider("google", {})
    
    # Remove google/ prefix
    assert provider._normalize_model_id("google/gemma-4-31b-it") == "gemma-4-31b-it"
    
    # Keep bare ID
    assert provider._normalize_model_id("gemma-4-31b-it") == "gemma-4-31b-it"
```

**Effort**: 1-2 hours
**Priority**: P0 — Temple-Grade compliance

#### 5.2 Documentation
**File**: `docs/guides/GEMMA4_PROVIDER_GUIDE.md` (NEW)
**Purpose**: Complete setup guide for Gemma 4 across platforms

```markdown
# Gemma 4 Provider Guide

## OpenCode Setup
1. Install config package
2. Configure API key
3. Test with `opencode run -m google/gemma-4-31b-it "hello"`

## Cline Setup
1. Use provided config
2. Configure API key
3. Test with direct API

## Omega Engine Setup
1. Provider already configured
2. Test with `omega talk "hello" -m gemma-4-31b-it`

## Troubleshooting
- Quota errors: Enable billing
- Thinking config errors: Check model family detection
- Model ID errors: Check normalization
```

**Effort**: 1-2 hours
**Priority**: P1 — Community value

#### 5.3 Heritage Attribution
**File**: `CREDITS.md`
**Change**: Add Pi project attribution

```markdown
| Pattern | Source | Tag |
|---|---|---|
| Gemma 4 Thinking Config | Pi PR #2903 | `[heritage: pi-2026] Gemma 4 Thinking` |
```

**Effort**: 15 minutes
**Priority**: P2 — M14 compliance

---

## 📋 Implementation Plan

### Phase 1: Core Fix (P0 — 4-6 hours)
1. **P1.1**: Provider config extension (30 min)
2. **P2.1**: OpenCode config package (30 min)
3. **P3.1**: GoogleAIProvider enhancement (2-3 hours)
4. **P5.1**: Test coverage (1-2 hours)

### Phase 2: Integration (P1 — 4-6 hours)
1. **P1.3**: Gateway routing extension (1 hour)
2. **P3.2**: Model gateway integration (1 hour)
3. **P4.1**: OpenCode upstream PR (2-4 hours)

### Phase 3: Community (P2 — 4-6 hours)
1. **P2.2**: Model card template extension (15 min)
2. **P2.3**: Cline config package (30 min)
3. **P4.2**: Community config package (2-3 hours)
4. **P5.2**: Documentation (1-2 hours)

### Phase 4: Hardening (P2 — 2-3 hours)
1. **P3.3**: Provider health monitor extension (1 hour)
2. **P4.3**: Provider adapter pattern (3-4 hours)
3. **P5.3**: Heritage attribution (15 min)

---

## 🎯 Priority Ordering

```
P0 (Blocks all):
├── P1.1 Provider config extension
├── P2.1 OpenCode config package
├── P3.1 GoogleAIProvider enhancement
└── P5.1 Test coverage

P1 (Core integration):
├── P1.3 Gateway routing extension
├── P3.2 Model gateway integration
├── P4.1 OpenCode upstream PR
└── P5.2 Documentation

P2 (Community value):
├── P2.2 Model card template extension
├── P2.3 Cline config package
├── P4.2 Community config package
├── P3.3 Provider health monitor extension
├── P4.3 Provider adapter pattern
└── P5.3 Heritage attribution
```

---

## 🚀 Community Contribution Potential

### 1. OpenCode PR
- **Scope**: `transform.ts` changes
- **Impact**: All OpenCode users with Gemma 4
- **Effort**: 2-4 hours
- **Value**: High — fixes root cause

### 2. Config Package
- **Scope**: Installable OpenCode config
- **Impact**: Easy setup for Gemma 4 users
- **Effort**: 2-3 hours
- **Value**: Medium — reduces friction

### 3. Provider Adapter Pattern
- **Scope**: Reusable Google provider adapter
- **Impact**: Future models with non-standard APIs
- **Effort**: 3-4 hours
- **Value**: High — architectural pattern

### 4. Documentation
- **Scope**: Complete setup guide
- **Impact**: All platforms (OpenCode, Cline, Omega)
- **Effort**: 1-2 hours
- **Value**: Medium — reduces support burden

---

## 🔮 Sovereign Provider Pattern

This bug reveals a deeper architectural need: **Sovereign Provider Adapters** for models with non-standard API requirements.

### Pattern Definition
```python
class SovereignProviderAdapter:
    """Base class for providers with non-standard API requirements."""
    
    def detect_model_family(self, model: str) -> str:
        """Detect model family for config routing."""
        pass
    
    def get_model_config(self, model: str, **kwargs) -> dict:
        """Get provider-specific config for model family."""
        pass
    
    def normalize_model_id(self, model: str) -> str:
        """Normalize model ID for API format."""
        pass
    
    def validate_config(self, model: str, config: dict) -> bool:
        """Validate config for model family."""
        pass
```

### Future Applications
- **Claude 4**: Different thinking config format
- **GPT-5**: Reasoning level mapping
- **Local models**: Provider-specific parameters
- **Custom models**: User-defined adapters

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Gemma 4 working in Omega** | ✅ | `omega talk "hello" -m gemma-4-31b-it` |
| **OpenCode PR merged** | ✅ | Upstream `transform.ts` fixed |
| **Tests passing** | 1398+ | `make test` |
| **Temple-Grade compliance** | T1-T11 | `make temple-grade` |
| **Community adoption** | 10+ users | Config package downloads |

---

## 🎯 Next Steps

1. **Immediate**: Implement Phase 1 (Core Fix)
2. **This week**: Submit OpenCode PR
3. **Next week**: Publish community config package
4. **Ongoing**: Extend pattern to other non-standard models

---

*⬡ OMEGA ⬡ MAAT ⬡ {session_model} ⬡ opencode ⬡ trc_maat ⬡ GEMMA4-FEATURE*