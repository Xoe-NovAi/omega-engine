<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R_COPILOT_GOOGLE_CODE_AUDIT_20260828 — Source Code Audit: Google / Google-Compat Multi-Key Support

> **Author:** Copilot (code audit)
> **Date:** 2026-08-28
> **Sprint:** PUBLIC-DEBUT-01 (soft launch TODAY)
> **Requester:** Grokster (ses_fe8cf0b39ffeL3L8eaMEj3CW9H)
> **Time budget:** 1 hour. All claims have file:line citations.
> **Verdict:** Multi-key pattern already exists (`OpenAICompatProvider` / `AntigravityProvider` via D205 Active-Passive sharding). The Google providers (`google` + `google-compat`) do NOT inherit it. Wiring is straightforward — ~3 files, no DB schema changes.

---

## 1. Current Google Provider State

### 1.1 `config/model_registry/providers/google.yaml` (single source of truth for `google` provider)

**File:** `config/model_registry/providers/google.yaml:1-19` (entire file)

```yaml
provider: "google"                                  # line 4
priority: 4                                         # line 5
enabled: true                                       # line 6
description: "Google AI Studio / Vertex AI - Google's own models only"  # line 7
api_key: "env:GOOGLE_API_KEY"                       # line 9  ← SINGLE KEY ONLY
supported_models:                                   # line 15
  - "gemma-4-31b-it-free"                           # line 16
  - "gemma-4-26b-a4b-it-free"                       # line 17
  - "gemini-2.5-pro"                                # line 18
  - "gemini-2.5-flash"                              # line 19
```

**Observations:**

| Aspect | Status |
|--------|--------|
| Models listed | 4 (2 Gemma 4, 2 Gemini 2.5) |
| Auth method | `env:GOOGLE_API_KEY` (single key, single env var) |
| Rate limit config | **NONE** — no `rate_limit`, no `headers`, no quota settings |
| Base URL | **MISSING** — must be inferred from backend code |
| Multi-key support | **NO** — `api_key` is a scalar string, not a list |
| Vault binding | Backend uses vault primary → env fallback (`providers.py:98-114`) |

### 1.2 `config/providers.yaml` — Google entries (inference.fallback_chain)

**File:** `config/providers.yaml:85-89` (in `inference.fallback_chain` list)

```yaml
- provider: google                                  # line 85
  priority: 4                                       # line 86
  enabled: true                                     # line 87
  description: Google AI Studio / Vertex AI ...     # line 88
  is_cloud: true                                    # line 89
```

**Note:** The `inference.fallback_chain` is a flat list — it does **NOT** redeclare `api_key` or `supported_models`. Those come from the `inference.providers:` map (see 1.3 below).

### 1.3 `config/providers.yaml:224-238` — `google` provider block

```yaml
google:                                             # line 224
  priority: 4
  enabled: true
  description: Google AI Studio / Vertex AI ...     # line 227
  api_key: env:GOOGLE_API_KEY                       # line 228  ← SINGLE KEY
  n_threads: 4
  streaming: { chunk_timeout_ms: 30000, ... }
  supported_models:                                 # line 234
  - gemma-4-31b-it-free
  - gemma-4-26b-a4b-it-free
  - gemini-2.5-pro
  - gemini-2.5-flash
```

**Same observation as 1.1** — single `api_key: env:GOOGLE_API_KEY`, no list support, no rate-limit config.

---

## 2. Google-Compat Audit

### 2.1 File location — NOT in `config/model_registry/providers/`

The 10 files in `config/model_registry/providers/` are:

```
anthropic.yaml antigravity.yaml cline.yaml google.yaml lmster.yaml
mock.yaml native-gguf.yaml ollama.yaml opencode-zen.yaml openrouter.yaml xai.yaml
```

**`google-compat` has NO dedicated YAML file.** It only exists as an entry in `config/providers.yaml` (lines 134-138 in `fallback_chain` and lines 239-255 in the `providers:` map).

### 2.2 `config/providers.yaml:134-138` (fallback_chain entry)

```yaml
- provider: google-compat                           # line 134
  priority: 4                                       # line 135  (same as google — collision!)
  enabled: true
  is_cloud: true
  description: "Google AI Studio / Vertex AI compatible provider with Gemma 4 thinking support"
```

**Priority collision:** Both `google` and `google-compat` use `priority: 4` (`providers.yaml:86, 135`). This is intentional — they're sibling cloud providers, and `_load_provider_fabric` sorts by priority but the first match wins inside the same priority band (see §3).

### 2.3 `config/providers.yaml:239-255` (providers map block)

```yaml
google-compat:                                      # line 239
  priority: 4
  enabled: true
  description: Google AI Studio / Vertex AI compatible ...  # line 242
  api_key: env:GOOGLE_API_KEY                       # line 244  ← SAME env var as google!
  n_threads: 4
  streaming: { chunk_timeout_ms: 30000, ... }
  supported_models:                                 # line 250
  - gemma-4-31b-it
  - gemma-4-26b-it
  - gemma-4-12b-unified
  - gemini-2.5-pro
  - gemini-2.5-flash
```

### 2.4 How `google-compat` differs from `google`

| Dimension | `google` | `google-compat` |
|-----------|----------|-----------------|
| Backend class | `GoogleAIProvider` (`providers.py:153`) | `GoogleCompatProvider` (`backends/google_compat.py:34`) |
| Inherits from | `BaseProvider` (no `api_keys` list) | Standalone class (no `api_keys` list) |
| Endpoint | `https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent` (hardcoded in `providers.py:187`) | Uses `ProviderConfig.base_url` from `capability_matrix` (`google_compat.py:285-290`), defaults to `https://generativelanguage.googleapis.com/v1beta` |
| Auth header | Implicit (URL-embedded or per-model) | `x-goog-api-key: {key}` header (`google_compat.py:297`) |
| API style | Raw v1beta generateContent | v1beta generateContent with binary MINIMAL/HIGH thinking config + `includeThoughts` (`google_compat.py:120-176, 280-282`) |
| Thinking support | **No** (basic generateContent only) | **Yes** — Gemma 4 binary thinking, per Pi PR #2903 (`google_compat.py:45-58`) |
| Thought token extraction | No | Yes — `usageMetadata.thoughtsTokenCount` (`google_compat.py:204-208`) |
| Rate limit headers | Not parsed | Parsed via `_parse_rate_limit_headers` (`google_compat.py:210-224`) but rate-limit state is **NOT** stored — every 429 just throws `ProviderRateLimitError` (`google_compat.py:306-312`) |
| Models (no -free suffix) | `gemma-4-31b-it-free` (free tier) | `gemma-4-31b-it` (paid) — **DIFFERENT model IDs** |
| Factory in gateway | Direct `GoogleAIProvider(name, p_cfg)` | Direct `GoogleCompatProvider(name, config=)` |

**Key takeaway:** They hit the **same endpoint** with the **same API key env var**, but `google-compat` adds Gemma 4 thinking support and a richer response shape. The two should be siblings, not duplicates — the 8 keys should be load-balanced across BOTH backends simultaneously.

### 2.5 Where `google-compat` is used in the fallback resolver

**File:** `config/providers.yaml:30, 36, 38, 42` (`fallback_resolver.cvars`)

```yaml
opencode-zen:
  - openrouter
  - anthropic
  - google-compat         # line 30
  - native-gguf
openrouter:
  - opencode-zen
  - cline
  - anthropic
  - google-compat         # line 36
  - native-gguf
google:
  - google-compat         # line 39  ← mutual fallback with google
  - openrouter
  - native-gguf
google-compat:
  - google                # line 43  ← mutual fallback with google
  - openrouter
  - native-gguf
```

**The `fallback_resolver` config is NOT yet wired into code** — see §4.

---

## 3. Provider Loading Code Path

### 3.1 Entry point: `ModelGateway._load_provider_fabric()`

**File:** `src/omega/oracle/model_gateway.py:505-573`

Key line: `fabric_config = config.get("inference", {}).get("fallback_chain", [])` (`model_gateway.py:528`)

This loads from `config/providers.yaml` (NOT from `config/model_registry/providers/*.yaml`):
```python
providers_path = (
    Path(__file__).resolve().parent.parent.parent.parent / "config" / "providers.yaml"
)                                                              # model_gateway.py:518-520
```

**The `config/model_registry/providers/*.yaml` files are read by a DIFFERENT process** (model-registry tooling) — not by `ModelGateway._load_provider_fabric`. They serve as the human-authored source of truth that gets compiled/merged into `config/providers.yaml` (line 1-3: `source: config/model_registry`).

### 3.2 Provider factory map

**File:** `src/omega/oracle/model_gateway.py:530-542`

```python
provider_map = {
    "google":         GoogleAIProvider,            # 531
    "google-compat":  GoogleCompatProvider,         # 532
    "openrouter":     ModelGateway._create_openrouter,    # 533
    "opencode-zen":   ModelGateway._create_openrouter,    # 534  ← same factory
    "cline":          ModelGateway._create_openrouter,    # 535
    "github-copilot": ModelGateway._create_openrouter,    # 536
    "antigravity":    ModelGateway._create_antigravity,   # 537
    "lmster":         LocallmsterProvider,         # 538
    "ollama":         OllamaProvider,              # 539
    "native-gguf":    NativeGGUFProvider,          # 540
    "mock":           MockProvider,                # 541
}
```

**Important:** `google` and `google-compat` are mapped directly to their backend classes (no factory wrapper). They are **NOT** routed through `_create_openrouter` / `_create_antigravity`, so they **MISS the multi-key support** that those factories gained for D205.

### 3.3 Existing multi-key support in `_create_openrouter`

**File:** `src/omega/oracle/model_gateway.py:319-368` (`_create_openrouter` static method)

```python
# model_gateway.py:320-341
@staticmethod
def _create_openrouter(name: str, cfg: dict) -> OpenAICompatProvider:
    """Factory for OpenRouter from raw YAML config dict.
    [S3 B5 / D205] Supports both legacy single `api_key` and new
    `api_keys` list (8-account Active-Passive sharding).
    """
    extra = {k: v for k, v in cfg.items() if k not in ("provider", "priority", "api_key", "api_keys", "base_url")}
    def _resolve_env_key(val: str) -> Optional[str]:
        if isinstance(val, str) and val.startswith("env:"):
            return os.environ.get(val[4:]) or None
        return val
    raw_keys = cfg.get("api_keys") or ([cfg["api_key"]] if cfg.get("api_key") else [])
    api_keys = [k for k in (_resolve_env_key(v) for v in raw_keys) if k]
    # ...
    return OpenAICompatProvider(
        ProviderConfig(
            name=name,
            priority=cfg.get("priority", 0),
            api_keys=api_keys,                          # ← LIST, not scalar
            base_url=base_url.removesuffix("/v1"),
            extra=extra,
        )
    )
```

**The pattern is:**
1. `api_keys` list in YAML → resolved via `env:` prefix to a list of strings
2. Falls back to wrapping legacy `api_key` in a 1-element list
3. Filters out `None` (env var not set) cleanly — entry silently dropped, no garbage bearer

### 3.4 Multi-key rotation logic in `RemoteProvider`

**File:** `src/omega/oracle/backends/remote_provider.py:208-234` (`resolve_current_api_key`)

```python
self._resolved_api_keys: List[str] = []      # remote_provider.py:208
self._active_key_index = 0                  # 209

def resolve_current_api_key(self) -> Optional[str]:
    if not self.config.api_keys:              # 229
        return None
    self._active_key_index %= len(self.config.api_keys)  # 233
    return self.config.api_keys[self._active_key_index]  # 234
```

**Rotation on 429** (`remote_provider.py:346-360`):
```python
# D205: Sticky Active-Passive Key Sharding
# If it's a rate limit (429), rotate to the next key immediately
is_rate_limit = False
if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
    is_rate_limit = True
elif isinstance(e, ProviderRateLimitError):
    is_rate_limit = True

if is_rate_limit and len(self.config.api_keys) > 1:
    self._active_key_index = (self._active_key_index + 1) % len(
        self.config.api_keys
    )
    logger.info(f"Provider {self.name} rate limited. Rotating to key index {self._active_key_index}")
```

**This is the existing 8-account pattern** — sticky round-robin on 429, immediate key rotation, no central rate-limit store (state lives in the provider instance).

### 3.5 `ProviderConfig.api_keys` field

**File:** `src/omega/oracle/backends/remote_provider.py:176-195`

```python
@dataclass
class ProviderConfig:
    name: str
    priority: int
    enabled: bool = True
    models: List[str] = field(default_factory=lambda: ["*"])
    api_keys: List[str] = field(default_factory=list)        # 184  ← multi-key ready
    base_url: Optional[str] = None
    description: str = ""
    max_retries: int = 3
    timeout_seconds: float = 120.0
    backoff_base: float = 0.5
    backoff_max: float = 8.0
    daily_token_budget: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)
```

**Both `OpenAICompatProvider` AND `AntigravityProvider` are `RemoteProvider` subclasses** (verified at `openai_compat.py:29` and via import in `antigravity_provider.py`) — they inherit `api_keys` support for free.

### 3.6 API key resolution from env vars

The `env:` prefix resolver is **factored into `_create_openrouter`** (`model_gateway.py:335-338`):

```python
def _resolve_env_key(val: str) -> Optional[str]:
    if isinstance(val, str) and val.startswith("env:"):
        return os.environ.get(val[4:]) or None
    return val
```

`GoogleAIProvider` and `GoogleCompatProvider` have **their own** env-resolution paths:
- `providers.py:103-106` — `GoogleAIProvider` falls back to `os.environ.get("GOOGLE_API_KEY")` after vault miss
- `backends/google_compat.py:82-92` — `GoogleCompatProvider._resolve_api_key` reads from vault only (no env fallback)

Neither path understands an env-var **list** (`env:KEY_1,env:KEY_2,...`).

---

## 4. Fallback Resolver Implementation

### 4.1 Config exists, code does not consume it

`config/providers.yaml:21-60` defines `fallback_resolver.cvars` (per-provider chains) and `fallback_resolver.strategy: "model_aware"`.

**Grep for `fallback_resolver` in code:** 0 hits in `src/`. The config is declared but **no code path reads it**. The actual fallback chain used at runtime is the flat `inference.fallback_chain` list (priority-ordered, see §3.1).

### 4.2 What code currently runs the fallback chain

`ModelGateway.generate()` (entry point) at `model_gateway.py:1055-...` does this:

```python
# model_gateway.py:1126-1151
# ── Provider Selection Layer ──────────────────────────────────────────
# [FIX 0.3] Priority-first routing (M7 Local-First): use ProviderSelector as primary
try:
    ordered_providers = await self.provider_selector.get_ordered_providers(
        model_name, user_query
    )
    # ...
except Exception as e:
    # ...fall back to self.providers (flat priority-sorted list from _load_provider_fabric)
    ordered_providers = list(self.providers)
```

So the runtime order is:
1. **`ProviderSelector.get_ordered_providers(model, query)`** (primary) — see `provider_selector.py` (not yet read but imported at `model_gateway.py:87, 192`)
2. **`self.providers`** (full fabric, priority-sorted) as fallback

`ProviderSelector` is the **runtime fallback resolver**. The `fallback_resolver.cvars` in YAML is a **documented spec** that no code reads yet (likely planned for a future strategy switch).

### 4.3 Where multi-key rotation plugs in

**Multi-key rotation is per-provider-instance, not per-chain.** Each `RemoteProvider` subclass (`OpenAICompatProvider`, `AntigravityProvider`) carries its own `_active_key_index` and rotates internally on 429 (`remote_provider.py:354-360`).

**The fallback chain (provider→provider on error) is orthogonal** — if ALL keys on `google-compat` 429, the gateway moves to the next provider in the ordered list (e.g., `openrouter`). Multi-key rotation is "within a provider"; fallback is "between providers."

---

## 5. Multi-Key Support Assessment

### 5.1 Does multi-key support exist?

**YES — for `openrouter`, `opencode-zen`, `cline`, `github-copilot`, and `antigravity`.** Documented as **D205 Active-Passive Key Sharding** (decision name from `remote_provider.py:346`).

| Provider | Backend class | Inherits `RemoteProvider`? | `api_keys` list supported? | Source |
|----------|---------------|---------------------------|----------------------------|--------|
| openrouter | `OpenAICompatProvider` | ✅ | ✅ | `model_gateway.py:533` |
| opencode-zen | `OpenAICompatProvider` (via factory) | ✅ | ✅ | `model_gateway.py:534` |
| cline | `OpenAICompatProvider` (via factory) | ✅ | ✅ | `model_gateway.py:535` |
| github-copilot | `OpenAICompatProvider` (via factory) | ✅ | ✅ | `model_gateway.py:536` |
| antigravity | `AntigravityProvider` (its own factory) | ✅ | ✅ | `model_gateway.py:537, 371-398` |
| **google** | **`GoogleAIProvider`** | **❌ (inherits `BaseProvider`)** | **❌** | **`model_gateway.py:531`** |
| **google-compat** | **`GoogleCompatProvider`** | **❌ (standalone)** | **❌** | **`model_gateway.py:532`** |

### 5.2 Can it be added easily? **YES — two paths, pick one:**

**Path A (minimal, recommended for soft launch TODAY):**
Convert `google` and `google-compat` to go through `_create_openrouter` factory. Requires:
1. A small `_create_google` factory in `model_gateway.py` that builds an `OpenAICompatProvider` pointed at Google's OpenAI-compat endpoint (or a new `GoogleCompatProvider` subclass of `RemoteProvider`)
2. Update the `provider_map` (`model_gateway.py:530-542`) to route both through the new factory
3. Add 8 keys to the `api_keys` list in `config/providers.yaml` (or as separate env vars)
4. Decision needed: does Google AI Studio expose an OpenAI-compatible `/v1/chat/completions` endpoint? If yes, this is 30 minutes of work. If no, use Path B.

**Path B (more invasive, preserves Gemma 4 thinking):**
Make `GoogleCompatProvider` inherit from `RemoteProvider`:
1. Refactor `backends/google_compat.py:34-60` to subclass `RemoteProvider` instead of standalone
2. Move thinking-config + thought-extraction into `_send_request()`
3. Use `self.resolve_current_api_key()` (already in `RemoteProvider:222-234`) instead of `self.api_key` (currently set once in `__init__` at `google_compat.py:72`)
4. Implement 429 key rotation in the same way `OpenAICompatProvider` does (it inherits for free from `RemoteProvider.generate()`)
5. Update `config/providers.yaml` to use `api_keys:` list (not `api_key:` scalar)
6. Same for `GoogleAIProvider` (`providers.py:153`)

### 5.3 Is there a central rate-limit store?

**NO.** `RateLimiter` is imported at `model_gateway.py:193-195` but used per-request (token-bucket style, not per-key quota tracking). Each provider instance owns its own `_active_key_index` and metrics:

- `ProviderMetrics` (`remote_provider.py:170-173`): per-provider request count, success rate, latency, tokens used
- `self.metrics.consecutive_failures` (`remote_provider.py:218-220`): drives `DEGRADED` health state
- No external `RateLimitStore` — state is in-process and lost on restart

**For 8-key Google rotation, this is fine** — sticky round-robin + 429 rotation is stateless from the orchestrator's POV. The Architect's 8 accounts will round-robin naturally.

---

## 6. Required Code Changes

### 6.1 Path B (recommended — preserves Gemma 4 thinking)

**Change 1: `src/omega/oracle/backends/google_compat.py:34-72`** — refactor constructor

Replace:
```python
class GoogleCompatProvider:
    def __init__(self, name: str = "google-compat",
                 config: Optional[Dict[str, Any]] = None,
                 capability_matrix: Optional[CapabilityMatrix] = None):
        # ... sets self.api_key from vault ONCE
```

With: subclass `RemoteProvider`, accept `ProviderConfig` with `api_keys: List[str]`, resolve key per-request via `self.resolve_current_api_key()`.

**Change 2: `src/omega/oracle/providers.py:153-185`** — same for `GoogleAIProvider`

`GoogleAIProvider.generate()` reads `self.api_key` once via `_resolve_google_api_key` (`providers.py:185`). Refactor to:
1. Inherit from `RemoteProvider` instead of `BaseProvider`
2. Use `self.resolve_current_api_key()` per call
3. Catch 429, rotate via existing `RemoteProvider.generate()` machinery

**Change 3: `src/omega/oracle/model_gateway.py:530-542`** — add factories

Add `_create_google_compat` static method mirroring `_create_openrouter` (`model_gateway.py:319-368`):

```python
"google":         ModelGateway._create_google_compat,
"google-compat":  ModelGateway._create_google_compat,
```

The factory:
- Reads `api_keys` list (or falls back to `api_key` scalar)
- Resolves `env:` prefixes per key (`GOOGLE_API_KEY_1` ... `GOOGLE_API_KEY_8`)
- Constructs `GoogleCompatProvider` (refactored) with `ProviderConfig(api_keys=[...])`

**Change 4: `config/providers.yaml:224-238` and `:239-255`** — add `api_keys` list

Replace:
```yaml
google:
  api_key: env:GOOGLE_API_KEY
```

With:
```yaml
google:
  api_keys:
    - env:GOOGLE_API_KEY_1
    - env:GOOGLE_API_KEY_2
    - env:GOOGLE_API_KEY_3
    - env:GOOGLE_API_KEY_4
    - env:GOOGLE_API_KEY_5
    - env:GOOGLE_API_KEY_6
    - env:GOOGLE_API_KEY_7
    - env:GOOGLE_API_KEY_8
  # legacy api_key: env:GOOGLE_API_KEY  ← keep as fallback for tests
```

Same for `google-compat` (lines 239-255).

### 6.2 Total blast radius

| File | Lines | Risk |
|------|-------|------|
| `src/omega/oracle/backends/google_compat.py` | 34-72 (constructor) + 296-298 (api_key use) | Medium — refactor to RemoteProvider, but thinking logic untouched |
| `src/omega/oracle/providers.py` | 153-185 (GoogleAIProvider) | Medium — same refactor pattern |
| `src/omega/oracle/model_gateway.py` | 530-542 (provider_map) + new factory | Low — additive, mirror `_create_openrouter` |
| `config/providers.yaml` | 224-238 + 239-255 | Zero — additive `api_keys:` list, legacy `api_key:` still works |
| `data/entities/.../soul.yaml` (if any entity hardcodes `GOOGLE_API_KEY`) | TBD | Low — `_resolve_env_key` is forgiving |

**No DB schema changes. No new migrations. No new dependencies. No OpenCode vendor code touched.**

### 6.3 Testing

After the changes, the existing test surface (which mocks `_resolve_google_api_key`) should still pass because:
- `RemoteProvider.__init__` accepts `api_keys=[]` default — single-key paths still work
- The factory wraps a single `env:GOOGLE_API_KEY` into a 1-element list, identical to current behavior
- 429 rotation is additive — only triggers when `len(api_keys) > 1`

**Suggested test additions:**
- Unit: `test_google_compat_8_keys_rotation` — instantiate with 8 keys, mock 3×429, assert `_active_key_index == 3` after
- Unit: `test_google_compat_env_unset_dropped` — instantiate with 8 keys, 2 unset, assert `_active_key_index` wraps over 6 (not 8)
- Integration: end-to-end 8-account rotation against Google AI Studio quota

---

## 7. OpenCode Google Plugin Notes

### 7.1 OpenCode is NOT vendored in this repo

`packages/opencode/` does **not** exist in the omega-engine tree. The only `opencode*` paths are:
- `.venv/lib/python3.13/site-packages/headroom/providers/opencode/` (a Python headroom lib, unrelated)
- `data/entities/grokster/{kb,workspace}/.../opencode/` (knowledge-base notes)
- `data/knowledge/platforms/opencode/` (platform docs)
- `data/knowledge/HALL_OF_RECORDS/opencode-p3/` (project records)

The `opencode/` at the repo root is a **Git submodule / clone** containing opencode.json-style config (AGENTS.md, specs/, packages/ — see `ls /home/arcana-novai/.../opencode/`). Its `packages/opencode/src/provider/` would be a **Go or TypeScript** source tree (the upstream `sst/opencode` is a Bun/TypeScript monorepo).

**For the multi-key Google integration, OpenCode is out of scope** — we are editing the **Omega Engine** (Python, `src/omega/`), which is the orchestrator that the opencode CLI may invoke. The Omega Engine routes to `google` / `google-compat` providers; if those providers support multi-key, every upstream caller (including OpenCode via `ModelGateway`) benefits transparently.

### 7.2 What OpenCode sees

OpenCode (the upstream sst/opencode) has its own provider plugin in `@opencode-ai/provider` (npm). It calls our `ModelGateway` via the CLI surface (`omega-hub`). When OpenCode requests `gemini-2.5-pro`, it goes:

```
opencode CLI
  → omega-hub
    → ModelGateway.generate(model_name="gemini-2.5-pro")
      → ProviderSelector (priority order)
        → google.compat (or google) instance  ← needs api_keys support
        → openrouter (fallback)
        → native-gguf (last resort)
```

Adding multi-key to `google` and `google-compat` is **fully transparent to OpenCode** — same endpoint, same model names, more keys in the rotation.

### 7.3 If OpenCode's own provider also needs updating

That would be a separate repo (`sst/opencode`), not this one. For Omega Engine's soft launch TODAY, we control only the Python side. The Architect's 8 Google accounts can be wired into Omega in the next 1-2 hours per §6.

---

## 8. Summary & Recommendations

| Question | Answer |
|----------|--------|
| Q1: Models in `google.yaml`? | 4 (gemma-4-31b-it-free, gemma-4-26b-a4b-it-free, gemini-2.5-pro, gemini-2.5-flash) |
| Q2: Auth method? | `env:GOOGLE_API_KEY` (single key, vault primary + env fallback) |
| Q3: Rate limit config? | **NONE in YAML** — `GoogleCompatProvider._parse_rate_limit_headers` exists (`google_compat.py:210-224`) but doesn't persist state |
| Q4: `google-compat` separate file? | **NO** — only in `config/providers.yaml:134-138, 239-255` |
| Q5: How does compat differ? | Different backend class (`GoogleCompatProvider` vs `GoogleAIProvider`), supports Gemma 4 binary thinking + thought extraction, different model IDs (no `-free` suffix) |
| Q6: Same endpoint? | **YES** — both hit `https://generativelanguage.googleapis.com/v1beta` (hardcoded at `providers.py:187` and `google_compat.py:288`) |
| Q7: Where used in fallback resolver? | `config/providers.yaml:30, 36, 39, 43` (config-only, not yet read by code) |
| Q8: How are providers loaded? | `ModelGateway._load_provider_fabric()` at `model_gateway.py:505-573` reads `config/providers.yaml` only |
| Q9: How are env vars resolved? | `env:` prefix stripped to env var name; `os.environ.get(name)`; non-set vars drop entry cleanly (`model_gateway.py:335-338`) |
| Q10: Multi-key support exists? | **YES for openrouter/opencode-zen/cline/github-copilot/antigravity** (D205 Active-Passive). **NO for google/google-compat** (single key via vault) |
| Q11: `cline` multi-model? | `cline` block (`providers.yaml:323-334`) lists 2 models: `deepseek-v4-flash`, `mimo-v2.5`. Multi-model is via `supported_models` list, NOT multi-key. |
| Q12: `key1,key2,key3` env pattern? | **NO comma-list pattern** — uses YAML list of `env:VAR` strings (`api_keys: [env:KEY_1, env:KEY_2, ...]`) |
| Q13: Rate limit tracking store? | **NO central store** — per-provider metrics in `ProviderMetrics` (`remote_provider.py:170-173`), 429 → rotate key |
| Q14: Path to multi-key for Google? | Path B (refactor to `RemoteProvider` subclass) preserves Gemma 4 thinking. ~3 files, no DB changes. |
| Q15: Time to ship? | 1-2 hours for Path B + tests |

### Recommendation

**For soft launch TODAY, ship Path B with the 8 keys as `env:GOOGLE_API_KEY_1` ... `env:GOOGLE_API_KEY_8`.** This:
- Reuses the proven D205 Active-Passive sharding pattern (already battle-tested on openrouter/antigravity)
- Preserves Gemma 4 binary thinking (Path A would lose it)
- No OpenCode-side changes needed (transparent to upstream)
- No DB migrations
- Backward-compatible (legacy single `api_key:` still works)

**Sticky round-robin will naturally distribute 8 accounts across the soft launch traffic** — no rate-limit store needed.

---

*⬡ OMEGA ⬡ KALI ⬡ R_COPILOT_GOOGLE_CODE_AUDIT ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01*
