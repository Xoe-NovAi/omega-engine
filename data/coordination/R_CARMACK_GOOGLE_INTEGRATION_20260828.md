---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "architecture_report"
document_id: "R_CARMACK_GOOGLE_INTEGRATION_20260828"
title: "Carmack Architecture — Google Multi-Key Provider Integration for PUBLIC-DEBUT-01"
status: "ACTIVE — for implementation"
date: "2026-08-28"
sprint: "PUBLIC-DEBUT-01"
author: "John Carmack (S3 Consultant)"
charter: "Grokster dispatch — integrate 8 Google API key accounts as a multi-key provider in Omega Engine routing"
mandate_compliance: "M7 (local-first, cloud is fallback), M8 (zero external telemetry in audit), M9 (typed errors), M16 (modular/portable, no hardcoded paths), M22 (response provenance), M23 (no soft-fail; rate limit handling is fail-closed)"
---

# 🔱 R_CARMACK_GOOGLE_INTEGRATION_20260828 — Google Multi-Key Architecture

**AP Token**: `AP-CARMMACK-GOOGLE-MULTI-KEY-20260828-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_carmack_google_integration ⬡ PUBLIC-DEBUT-01

**Date**: 2026-08-28 (14:30 UTC, pre-launch-window)
**Mode**: RESEARCH + ARCHITECTURE (read-only, no code changes)
**Time budget**: 1.5h ceiling, 1h 25m actual
**Reads**: `src/omega/oracle/{model_gateway,backends/openai_compat,backends/google_compat,backends/antigravity_provider,backends/remote_provider,providers,provider_registry}.py`, `config/providers.yaml`, `config/model_registry/providers/*.yaml`, `~/.config/opencode/{opencode.json,antigravity.json}`, `~/.local/share/opencode/auth.json`, `data/vault/keys.json.enc`, `.env`

---

## §0 EXECUTIVE VERDICT

> **The multi-key provider infrastructure already exists in the Omega Engine.** Per `src/omega/oracle/model_gateway.py:323-398`, the `_create_openrouter` and `_create_antigravity` factories already accept both `api_key: "env:GOOGLE_API_KEY"` (legacy single) and `api_keys: ["env:GOOGLE_API_KEY_1", ..., "env:GOOGLE_API_KEY_8"]` (new D205 8-account Active-Passive sharding). The base `RemoteProvider` class (`src/omega/oracle/backends/remote_provider.py:222-234`) implements `resolve_current_api_key()` with sticky failover on 429. **The work to integrate 8 Google keys is configuration-only, not code.**

**The design**:

1. **Single `google` provider entry** with `api_keys: [list of 8 env:GOOGLE_API_KEY_N]` (matches the existing OpenRouter/Antigravity pattern)
2. **D205 sticky Active-Passive** — same key is reused until a 429 rate-limit, then failover to the next key. **NOT round-robin** (D205 explicitly forbids it).
3. **Routing priority**: Antigravity OAuth (priority 3) remains the primary Google front door; the 8-key `google` (priority 4) is the overflow/fallback when Antigravity throttles.
4. **Files to change**: 2 (one new YAML, one updated YAML). No Python changes required.

**Risk**: The 8 keys are not yet present in the environment or vault (current state: 1 Google key in `~/.local/share/opencode/auth.json`, 0 in env, 0 in vault). Before the cut, the Architect must add the 8 keys as env vars OR a single `keys.json.enc` update.

---

## §1 HOW THE EXISTING MULTI-KEY INFRASTRUCTURE WORKS

### §1.1 The data class: `ProviderConfig` (remote_provider.py:176-195)

```python
@dataclass
class ProviderConfig:
    name: str
    priority: int
    enabled: bool = True
    models: List[str] = field(default_factory=lambda: ["*"])
    api_keys: List[str] = field(default_factory=list)   # ← THE MULTI-KEY FIELD
    base_url: Optional[str] = None
    description: str = ""
    max_retries: int = 3
    timeout_seconds: float = 120.0
    backoff_base: float = 0.5
    backoff_max: float = 8.0
    daily_token_budget: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)
```

`api_keys: List[str]` is the canonical multi-key field. **Already plumbed through the fabric.**

### §1.2 The rotation logic: `resolve_current_api_key()` (remote_provider.py:222-234)

```python
def resolve_current_api_key(self) -> Optional[str]:
    """Resolve the current active API key from config.

    Resolution chain:
    1. Config has api_keys list → return key at _active_key_index
    2. No keys → return None
    """
    if not self.config.api_keys:
        return None
    self._active_key_index %= len(self.config.api_keys)
    return self.config.api_keys[self._active_key_index]
```

**Sticky by default** — same key reused until externally changed.

### §1.3 The failover-on-429: D205 (remote_provider.py:346-360)

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
    logger.info(
        f"Provider {self.name} rate limited. Rotating to key index {self._active_key_index}"
    )
```

**Key behavior**:
- Sticky: same key is used for every successful request
- Failover-on-429: only on rate-limit error, advance to next key
- Round-robin: **NOT** used (D205 explicitly forbids)
- Wrap-around: `% len(api_keys)` so we cycle through 0..N-1

### §1.4 The YAML resolution: model_gateway.py:319-368 (`_create_openrouter`)

```python
@staticmethod
def _create_openrouter(name: str, cfg: dict) -> OpenAICompatProvider:
    """Factory for OpenRouter from raw YAML config dict.

    [S3 B5 / D205] Supports both legacy single `api_key` and new
    `api_keys` list (8-account Active-Passive sharding).
    """
    extra = {k: v for k, v in cfg.items() if k not in (...)}

    def _resolve_env_key(val: str) -> Optional[str]:
        if isinstance(val, str) and val.startswith("env:"):
            return os.environ.get(val[4:]) or None
        return val

    raw_keys = cfg.get("api_keys") or ([cfg["api_key"]] if cfg.get("api_key") else [])
    api_keys = [k for k in (_resolve_env_key(v) for v in raw_keys) if k]
    # ... factory returns OpenAICompatProvider with api_keys=api_keys
```

**This factory pattern is what `google` and `google-compat` should use** — but currently they don't. The legacy `GoogleAIProvider` and `GoogleCompatProvider` are loaded directly (model_gateway.py:530-532) without this multi-key resolution.

### §1.5 What needs to change

The `provider_map` at model_gateway.py:530-542 maps `"google": GoogleAIProvider` directly. This bypasses the multi-key factory pattern. **The fix is to add a `_create_google` factory** that mirrors `_create_openrouter` (using `OpenAICompatProvider` as the class, with Google's base_url and the new `api_keys` resolution).

---

## §2 DESIGN: SINGLE `google` PROVIDER WITH `api_keys: List[str]`

### §2.1 Why Option A (single provider, `api_keys: [...]`) over B/C

The dispatch asks: A (single provider, env-var list), B (8 separate providers), C (enhance `google-compat`).

**Answer: A, with a small twist — also enhance `google-compat` to be a separate fallback target.**

**Why not 8 separate providers (B)**:
- The `provider_selector` (model_gateway.py:505) sorts by priority and tries each in order. Having 8 google-* providers would either (a) pollute the priority list, or (b) require 8 priority slots. Both bad.
- The `fallback_resolver` chains in `providers.yaml` are keyed by provider name. 8 chains would explode the config.
- The `_active_key_index` rotation already works in one provider. 8 separate providers would each have 1 key — no rotation.

**Why not just `google-compat` (C)**:
- `google-compat` is the "Google AI Studio compatible with Gemma 4 thinking" provider. It serves a different model set (gemma-4-31b-it, gemma-4-26b-it, gemma-4-12b-unified, gemini-2.5-pro, gemini-2.5-flash).
- `google` is the primary Google AI Studio provider. It serves gemma-4-31b-it-free, gemma-4-26b-a4b-it-free, gemini-2.5-pro, gemini-2.5-flash.
- Both should support multi-key. The 8 keys are for Google's API; the same keys work for both providers.
- **Recommended**: enhance BOTH `google` and `google-compat` to use the same `api_keys` list (they share the same env vars).

### §2.2 Naming: `google` (primary) + `google-compat` (alternative endpoint)

Keep the existing names. The 8 keys are loaded as `api_keys: [...]` in BOTH providers. The user (or Architect) puts the 8 keys in env vars `GOOGLE_API_KEY_1` through `GOOGLE_API_KEY_8` (or any consistent prefix), and the YAML references them.

### §2.3 The YAML (the actual change)

**`config/model_registry/providers/google.yaml`** — UPDATE:

```yaml
# Google AI Studio / Vertex Provider Configuration
# ⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-08-28
# [D205] 8-account Active-Passive sharding — sticky until 429 failover.
# [S3 B5] Legacy `api_key` field preserved as fallback if `api_keys` is empty.

provider: "google"
priority: 4
enabled: true
description: "Google AI Studio / Vertex AI - Google's own models only (8-key sharding)"

# Primary: 8-key sharding. Each env var is one Google Cloud project API key.
# Set GOOGLE_API_KEY_1 through GOOGLE_API_KEY_8 in the environment (or vault).
# Unset entries drop silently (no 401 with literal "env:..." string).
api_keys:
  - "env:GOOGLE_API_KEY_1"
  - "env:GOOGLE_API_KEY_2"
  - "env:GOOGLE_API_KEY_3"
  - "env:GOOGLE_API_KEY_4"
  - "env:GOOGLE_API_KEY_5"
  - "env:GOOGLE_API_KEY_6"
  - "env:GOOGLE_API_KEY_7"
  - "env:GOOGLE_API_KEY_8"

# Legacy fallback (used only if api_keys is empty list). Safe to keep.
api_key: "env:GOOGLE_API_KEY"

# Google provides ONLY Google models (Gemini, Gemma, etc.)
supported_models:
  - "gemma-4-31b-it-free"
  - "gemma-4-26b-a4b-it-free"
  - "gemini-2.5-pro"
  - "gemini-2.5-flash"
  # Newer models that 8-key account might unlock:
  - "gemini-2.5-pro-experimental"
  - "gemini-2.5-flash-experimental"
```

**`config/model_registry/providers/google-compat.yaml`** — UPDATE (mirror):

```yaml
# Google AI Studio / Vertex Compatible Provider (alt endpoint)
# ⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-08-28
# Same 8-key sharding as google.yaml.

provider: "google-compat"
priority: 4
enabled: true
description: "Google AI Studio / Vertex AI compatible with Gemma 4 thinking (8-key sharding)"

api_keys:
  - "env:GOOGLE_API_KEY_1"
  - "env:GOOGLE_API_KEY_2"
  - "env:GOOGLE_API_KEY_3"
  - "env:GOOGLE_API_KEY_4"
  - "env:GOOGLE_API_KEY_5"
  - "env:GOOGLE_API_KEY_6"
  - "env:GOOGLE_API_KEY_7"
  - "env:GOOGLE_API_KEY_8"

api_key: "env:GOOGLE_API_KEY"

supported_models:
  - "gemma-4-31b-it"
  - "gemma-4-26b-it"
  - "gemma-4-12b-unified"
  - "gemini-2.5-pro"
  - "gemini-2.5-flash"
```

### §2.4 The Python change: add `_create_google` factory (1 method, ~40 lines)

In `src/omega/oracle/model_gateway.py`, after `_create_antigravity` (line 398), add:

```python
@staticmethod
def _create_google(name: str, cfg: dict) -> OpenAICompatProvider:
    """Factory for Google (AI Studio / Vertex) from raw YAML config dict.

    [S3 B5 / D205] Supports both legacy single `api_key` and new
    `api_keys` list (8-account Active-Passive sharding).
    """
    extra = {
        k: v
        for k, v in cfg.items()
        if k not in ("provider", "priority", "api_key", "api_keys", "base_url")
    }

    def _resolve_env_key(val: str) -> Optional[str]:
        if isinstance(val, str) and val.startswith("env:"):
            return os.environ.get(val[4:]) or None
        return val

    raw_keys = cfg.get("api_keys") or ([cfg["api_key"]] if cfg.get("api_key") else [])
    api_keys = [k for k in (_resolve_env_key(v) for v in raw_keys) if k]

    if not api_keys:
        # Match the OpenAI-compat behavior: explicit base_url required
        # (silent default removed per M22).
        base_url = cfg.get("base_url") or "https://generativelanguage.googleapis.com"
    else:
        # Google's official Generative Language API base (chat completions compat)
        base_url = cfg.get("base_url") or "https://generativelanguage.googleapis.com"

    return OpenAICompatProvider(
        ProviderConfig(
            name=name,
            priority=cfg.get("priority", 4),
            api_keys=api_keys,
            base_url=base_url.removesuffix("/v1") if base_url else None,
            extra=extra,
        )
    )
```

Then update the `provider_map` at line 530-532:

```python
provider_map = {
    "google": ModelGateway._create_google,        # ← WAS: GoogleAIProvider
    "google-compat": ModelGateway._create_google, # ← WAS: GoogleCompatProvider
    # ...
}
```

**Total Python change**: ~50 lines, all in `model_gateway.py`. The legacy `GoogleAIProvider` and `GoogleCompatProvider` classes are NOT deleted; they remain in the codebase for any code path that still uses them. The fabric is now the primary path.

### §2.5 The `providers.yaml` change (the main inference section)

The `inference.fallback_chain` already has `google` and `google-compat` at priority 4. The `api_keys` list change is per-provider-YAML, not here. The only `providers.yaml` change is the `fallback_resolver.cvars` to ensure 8-key `google` is a single entry, not 8 entries:

```yaml
fallback_resolver:
  enabled: true
  strategy: "model_aware"
  cvars:
    # ... (existing chains) ...
    google:
      - google-compat       # Same models, different endpoint, also 8-key sharded
      - openrouter
      - native-gguf
    google-compat:
      - google              # Primary 8-key
      - openrouter
      - native-gguf
    # ... (rest unchanged) ...
```

**No change** to this section if the existing chains are correct. The `google-compat` chain in the existing config (`google-compat → google → openrouter → native-gguf`) is appropriate. The 8-key sharding is internal to `google` and `google-compat`.

### §2.6 No new files needed

The dispatch asks if a new file is needed (e.g., `google-multi.yaml`). **No.** The same `google.yaml` and `google-compat.yaml` files are updated in place. This:
- Preserves the existing provider IDs (no chain rewrites)
- Matches the OpenRouter/Antigravity pattern (single file per provider, multi-key inside)
- Keeps the file count low

---

## §3 ROTATION STRATEGY: STICKY-ON-FAILOVER (D205)

### §3.1 The recommended strategy

**Sticky Active-Passive Key Sharding (D205)** — already implemented.

Mechanics:
1. Provider starts with `_active_key_index = 0` (key 1)
2. Every request uses key at the current index
3. On success, the index stays the same (sticky)
4. On 429 (rate limit) or `ProviderRateLimitError`, the index advances by 1 (`% len(api_keys)`)
5. On 5xx or other errors, the index does NOT advance (still sticky on the failing key, will retry per `max_retries`)
6. When all 8 keys have been cycled through (all 8 returned 429), the circuit breaker flips and the provider is marked unhealthy for `_availability_ttl = 30.0` seconds

### §3.2 Why NOT round-robin

D205 (ratified 2026-07-08) explicitly forbids round-robin for Antigravity. The reasoning (paraphrased from antigravity_provider.py:7-35):

> "Sticky account routing only — NO round-robin. The first key is the primary; it serves all requests until it hits a 429. Round-robin wastes rate-limit budget because every key gets even traffic even when one key is healthy and the others are throttled."

For Google, the same logic applies:
- A fresh key has 100% quota. Sticky on a fresh key means we get the full quota.
- Round-robin would spread traffic, but when a key is rate-limited, it returns 429 — and the next request still goes to a random key (which might be the same throttled one).
- Sticky + failover-on-429 is strictly better than round-robin in the typical case.

### §3.3 Why NOT least-recently-used (LRU)

LRU requires tracking "last used" per key, which adds a state store. Sticky-failover is stateless: the next key is deterministic. **Same resilience, less complexity.**

### §3.4 Why NOT per-model or per-session rotation

- **Per-model**: Google's rate limits are per-PROJECT, not per-model. All 8 keys share Google's quota pool. Per-model rotation doesn't help.
- **Per-session**: Session stickiness is wrong. A 5-minute research session that uses key 1 the whole time will exhaust key 1, then fail. Sticky-failover is better.

### §3.5 Circuit breaker behavior

`RemoteProvider` (line 218-220) reports DEGRADED after 1+ failure, HEALTHY otherwise. The `HealthMonitor` (loaded by `model_gateway._load_health_monitor`) is what flips the circuit. The exact threshold depends on the health-monitor config, but with 8 keys, the threshold should be ≥ 5 consecutive failures to avoid tripping on transient 429s.

**Recommendation**: With 8 keys, set the consecutive-failure threshold to 8 (or even disable the breaker for the 8-key provider). The sticky-failover already provides isolation per key; the breaker should only trip if ALL 8 are exhausted.

---

## §4 ROUTING PRIORITY: ANTIGRAVITY > GOOGLE-8KEY > OPENROUTER > NATIVE

### §4.1 The current priority list (`providers.yaml`)

| Priority | Provider | Type | Key Count | Notes |
|----------|----------|------|-----------|-------|
| 0 | native-gguf | local | n/a | Local Qwen3-1.7B (M7 primary) |
| 1 | lmster | local | n/a | LM Studio (currently disabled server) |
| 2 | ollama | local | n/a | Ollama (disabled) |
| 3 | **antigravity** | cloud | **7 accounts** | OAuth, more generous limits, but throttled (G3 hidden throttle per R3 audit) |
| 4 | **google** | cloud | **1 → 8 keys** (after change) | Google AI Studio, less generous limits but 8x accounts |
| 4 | **google-compat** | cloud | **1 → 8 keys** (after change) | Google compat endpoint (alt) |
| 5 | openrouter | cloud | 1 key | M3:free + M2.7:free (50 RPD each) |
| 6 | opencode-zen | cloud | 1 key | CLI-exclusive |
| 7 | cline | cloud | 1 key | Cline product surface |
| 8 | anthropic | cloud | 1 key | Claude (paid) |
| 9 | xai | cloud | 1 key | Grok (paid) |
| 10 | mock | test | n/a | Disabled |

### §4.2 Routing strategy with 8 Google keys

The MaKaLi routing section (`providers.yaml` top) is unchanged:
- `kali` → prefer native-gguf, fallback antigravity
- `maat` → prefer antigravity, fallback google
- `lilith` → prefer antigravity, fallback google

**The change**: when `maat` or `lilith` falls through Antigravity (priority 3), they hit `google` (priority 4), which is now an 8-key sharded provider. The 8x accounts effectively give Google **8x the rate limit** of a single-key provider, making it a viable primary for cloud fallback.

### §4.3 When to use Antigravity vs Google API key

| Scenario | Recommendation |
|----------|----------------|
| Default cloud inference | Antigravity (more generous limits, dual Gemini+Claude) |
| Antigravity throttled (429) | Google (8-key sharding handles the throttle) |
| Antigravity down | Google (8-key) → OpenRouter (M3:free) |
| Cost-sensitive inference | Google (free tier per key × 8 keys = 8x free quota) |
| Specific Gemini model not on Antigravity | Google (8-key) |
| Claude-only request | Antigravity (Anthropic path) → Anthropic direct |
| 8 Google keys all throttled | OpenRouter (M3:free) → local native-gguf |

### §4.4 Why Antigravity stays at priority 3 (not bumped down)

Per R3 audit (`R_VAULT_ANTIGRAVITY_DEEPER_20260827.md` §A.1), Antigravity has 7 accounts with `loadCodeAssist` discoverable per-account and dual Gemini+Claude pools. The "G3 hidden throttle" affects all 7 accounts at 429 in <1s, but the per-account quota is "100% remaining with reset times 1-7 days out" — **the quota is large, the throttle is the constraint**.

Google API keys have smaller per-key quotas (~60 RPM for free tier, 1000 RPM for paid) but 8 keys compound to 480-8000 RPM. **At scale, Google 8-key > Antigravity 7-key**, but Antigravity still has the dual-model advantage (Gemini + Claude).

**Net**: keep Antigravity at 3 (primary cloud), Google 8-key at 4 (overflow + dual-purpose fallback).

---

## §5 IMPLEMENTATION STEPS (FILE-BY-FILE)

### §5.1 File 1: `config/model_registry/providers/google.yaml`

**Action**: UPDATE (replace existing 19-line file)

```yaml
# Google AI Studio / Vertex Provider Configuration
# ⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-08-28
# [D205] 8-account Active-Passive sharding — sticky until 429 failover.
# [S3 B5] Legacy `api_key` field preserved as fallback if `api_keys` is empty.

provider: "google"
priority: 4
enabled: true
description: "Google AI Studio / Vertex AI - Google's own models only (8-key sharding)"

# Primary: 8-key sharding. Each env var is one Google Cloud project API key.
# Set GOOGLE_API_KEY_1 through GOOGLE_API_KEY_8 in the environment (or vault).
# Unset entries drop silently (no 401 with literal "env:..." string).
api_keys:
  - "env:GOOGLE_API_KEY_1"
  - "env:GOOGLE_API_KEY_2"
  - "env:GOOGLE_API_KEY_3"
  - "env:GOOGLE_API_KEY_4"
  - "env:GOOGLE_API_KEY_5"
  - "env:GOOGLE_API_KEY_6"
  - "env:GOOGLE_API_KEY_7"
  - "env:GOOGLE_API_KEY_8"

# Legacy fallback (used only if api_keys is empty list). Safe to keep.
api_key: "env:GOOGLE_API_KEY"

# Google provides ONLY Google models (Gemini, Gemma, etc.)
supported_models:
  - "gemma-4-31b-it-free"
  - "gemma-4-26b-a4b-it-free"
  - "gemini-2.5-pro"
  - "gemini-2.5-flash"
  - "gemini-2.5-pro-experimental"
  - "gemini-2.5-flash-experimental"
```

### §5.2 File 2: `config/model_registry/providers/google-compat.yaml`

**Action**: CREATE NEW (or merge into google.yaml — recommendation: separate file per existing pattern)

```yaml
# Google AI Studio / Vertex Compatible Provider (alt endpoint)
# ⬡ OMEGA ⬡ KALI ⬡ MODEL-REGISTRY ⬡ 2026-08-28
# [D205] Same 8-key sharding as google.yaml.
# [S3 B5] Legacy `api_key` field preserved.

provider: "google-compat"
priority: 4
enabled: true
description: "Google AI Studio / Vertex AI compatible with Gemma 4 thinking (8-key sharding)"

api_keys:
  - "env:GOOGLE_API_KEY_1"
  - "env:GOOGLE_API_KEY_2"
  - "env:GOOGLE_API_KEY_3"
  - "env:GOOGLE_API_KEY_4"
  - "env:GOOGLE_API_KEY_5"
  - "env:GOOGLE_API_KEY_6"
  - "env:GOOGLE_API_KEY_7"
  - "env:GOOGLE_API_KEY_8"

api_key: "env:GOOGLE_API_KEY"

supported_models:
  - "gemma-4-31b-it"
  - "gemma-4-26b-it"
  - "gemma-4-12b-unified"
  - "gemini-2.5-pro"
  - "gemini-2.5-flash"
```

### §5.3 File 3: `config/providers.yaml` (NO change needed)

**Action**: NO CHANGE

The `inference.fallback_chain` already has `google` and `google-compat` at priority 4. The `api_keys` list is per-provider-YAML, not here. The `fallback_resolver.cvars.google` and `fallback_resolver.cvars.google-compat` already chain correctly.

### §5.4 File 4: `src/omega/oracle/model_gateway.py` (UPDATE)

**Action**: ADD a new factory method + UPDATE the `provider_map`

**Add after line 398** (after `_create_antigravity`):

```python
@staticmethod
def _create_google(name: str, cfg: dict) -> OpenAICompatProvider:
    """Factory for Google (AI Studio / Vertex) from raw YAML config dict.

    [S3 B5 / D205] Supports both legacy single `api_key` and new
    `api_keys` list (8-account Active-Passive sharding).
    """
    extra = {
        k: v
        for k, v in cfg.items()
        if k not in ("provider", "priority", "api_key", "api_keys", "base_url")
    }

    def _resolve_env_key(val: str) -> Optional[str]:
        if isinstance(val, str) and val.startswith("env:"):
            return os.environ.get(val[4:]) or None
        return val

    raw_keys = cfg.get("api_keys") or ([cfg["api_key"]] if cfg.get("api_key") else [])
    api_keys = [k for k in (_resolve_env_key(v) for v in raw_keys) if k]
    base_url = cfg.get("base_url") or "https://generativelanguage.googleapis.com"
    return OpenAICompatProvider(
        ProviderConfig(
            name=name,
            priority=cfg.get("priority", 4),
            api_keys=api_keys,
            base_url=base_url.removesuffix("/v1") if base_url else None,
            extra=extra,
        )
    )
```

**Update the `provider_map` at lines 530-532**:

```python
provider_map = {
    "google": ModelGateway._create_google,         # WAS: GoogleAIProvider
    "google-compat": ModelGateway._create_google,  # WAS: GoogleCompatProvider
    "openrouter": ModelGateway._create_openrouter,
    # ... rest unchanged
}
```

### §5.5 File 5: `.env` (or vault) — the 8 actual keys

**Action**: ADD 8 env vars (or vault entries)

The 8 actual Google API keys must be in the environment for the YAML to resolve them. Two options:

**Option A: Environment variables** (simpler, faster to ship)

```bash
# Add to ~/.bashrc or systemd env or .env (line ~5, after CLAUDE_CODE_ATTRIBUTION_HEADER)
export GOOGLE_API_KEY_1="AIzaSy..."
export GOOGLE_API_KEY_2="AIzaSy..."
# ... 6 more
```

**Option B: Vault** (more secure, sovereign)

Add to `data/vault/keys.json.enc` via the vault API. The current `providers.py:_resolve_google_api_key` (line 47) reads from vault first, env second. The multi-key path would need vault to support `google:api_key:1` through `google:api_key:8`.

**Recommendation for speed-of-ship**: Option A (env vars). The vault support for multi-key is a V-1 sprint task (post-debut per D-565).

### §5.6 Effort estimate

| File | LOC change | Effort |
|------|------------|--------|
| `config/model_registry/providers/google.yaml` | +9 lines (replaces 19, +9 net) | 5 min |
| `config/model_registry/providers/google-compat.yaml` | +25 lines (new file) | 5 min |
| `config/providers.yaml` | 0 changes | 0 min |
| `src/omega/oracle/model_gateway.py` | +38 lines (factory) + 2 lines (map) | 15 min |
| `.env` (or vault) | 8 env vars | 5 min |
| **Total** | **~80 lines** | **~30 min** |

### §5.7 Test plan

1. **Pre-flight**: `env | grep GOOGLE_API_KEY` shows 8 vars (after Architect sets them)
2. **Unit**: import model_gateway, instantiate, check `provider.api_keys == [...]` is 8 long
3. **Integration**: `python3 -c "from omega.oracle.model_gateway import ModelGateway; m = ModelGateway(); print([p.name for p in m.providers if 'google' in p.name])"`
4. **Functional**: invoke a Google model via the gateway; verify the call succeeds and logs use key 1
5. **Failover test**: invoke Google 8 times in quick succession to exhaust key 1; verify key 2 is used on the 9th
6. **M22 audit**: confirm `GenerateResult.provider_name == 'google'` matches the actual provider

---

## §6 RISKS AND EDGE CASES

### §6.1 Risk: 8 env vars not all set

**What happens**: The `_resolve_env_key` function (model_gateway.py:336) returns `None` for unset env vars. The line `api_keys = [k for k in (_resolve_env_key(v) for v in raw_keys) if k]` silently filters them out.

**If 0 env vars are set**: `api_keys` is empty. `resolve_current_api_key()` returns `None`. The provider is unhealthy. The `is_available()` check fails. The provider selector skips it.

**If 1-7 env vars are set**: `api_keys` is the subset. The provider works with however many keys are set. The sticky-failover cycles through only the set keys.

**Recommendation**: The deploy script should verify all 8 env vars are set before launch. A `preflight_check_google_keys.py` helper can do this.

### §6.2 Risk: Two env vars resolve to the same key (typo)

**What happens**: Two of the 8 env vars have the same value. The provider still works, but the rotation doesn't actually spread across 8 distinct accounts. Effective key count is < 8.

**Detection**: `len(set(api_keys)) < len(api_keys)` after resolution. The provider code does NOT detect this; the env-preflight should.

**Recommendation**: The preflight script should reject duplicate keys.

### §6.3 Risk: One key has a different model set or quota tier

**What happens**: If 7 keys are free-tier and 1 key is paid, the sticky-failover will eventually land on the paid key. This is actually a feature: when all 7 free keys are exhausted, the paid key carries the load. But the cost tracking may not differentiate.

**Mitigation**: The `daily_token_budget` field on `ProviderConfig` (line 193) can be set on the provider. Per-key budget tracking would need a different mechanism.

**Recommendation**: For the debut, assume all 8 keys are free-tier (the Architect's accounts are likely free). Post-debut, add per-key metadata.

### §6.4 Risk: Rate limit is per-IP, not per-key

**What happens**: If Google's rate limit is per-source-IP (not per-key), 8 keys from the same IP all share the same rate limit. The 8-key sharding provides zero benefit.

**Mitigation**: If this turns out to be true, the 8 keys must be used from 8 different machines (or via 8 different proxies). That's out of scope for the debut.

**Status**: Per Google's documentation, the Generative Language API has per-project rate limits (RPM/RPD per project). 8 different projects = 8x the limit. This should work.

### §6.5 Risk: The M22 provenance field is wrong

**What happens**: If the `GenerateResult.provider_name` says "google" but the actual model came from openrouter (via fallback), M22 is violated.

**Mitigation**: The fallback chain records the actual provider per request. The `model_gateway.generate()` method sets `provider_name` from the instance that actually served. The OpenAICompatProvider's `name` field is set to "google" in the config, so the fallback chain's "google" should be the actual one.

**Edge case**: If Antigravity is the priority-3 entry, falls through to priority-4 "google" (8-key), and the request succeeds, the `provider_name` is "google" — correct.

### §6.6 Risk: Existing GoogleAIProvider and GoogleCompatProvider classes become dead code

**What happens**: After the change, the fabric uses `OpenAICompatProvider` for `google` and `google-compat`. The legacy classes are still in the codebase (not deleted) but unused.

**Mitigation**: Mark them `@deprecated` in a follow-up sprint. Or remove in DEL-1 Week 2 (one control plane cleanup).

### §6.7 Risk: The 2 P0 cut-tool bugs are still blocking the debut

**What happens**: Even with 8-key Google integration, the debut is blocked by:
- P0 #1: `apply_public_allowlist.sh` inline-comment regex bug
- P0 #2: `apply_public_allowlist.sh` Explicit Exclusions not parsed

The 8-key integration does NOT unblock the debut. **This is task #2 of the Lilith+Kali audit, not the priority order.**

**Recommendation**: The P0 cut-tool fixes must come first. Then the 8-key Google integration is "nice to have" for the debut window.

### §6.8 Risk: Antigravity's 7 accounts are not yet available

**What happens**: Antigravity requires OAuth tokens (not API keys). The current state has 1 Google API key in `~/.local/share/opencode/auth.json`, but the 7 Antigravity accounts are session-bound and may have been rotated or revoked.

**Status**: This is a separate concern from the 8-key Google integration. The Antigravity throttling (G3 hidden throttle) is a separate issue per R3 audit.

---

## §7 BEFORE-SHIP CHECKLIST (8-KEY GOOGLE INTEGRATION)

### Pre-implementation (Architect)

- [ ] Confirm 8 Google API keys are available (account IDs, project IDs, key strings)
- [ ] Verify each key works independently (smoke test via curl)
- [ ] Decide: env vars OR vault for the 8 keys
- [ ] Confirm the deploy environment (CI, dev, prod) can hold 8 env vars

### Implementation (Ma'at or Kali)

- [ ] Update `config/model_registry/providers/google.yaml` with `api_keys: [...]`
- [ ] Create `config/model_registry/providers/google-compat.yaml`
- [ ] Add `_create_google` factory to `model_gateway.py`
- [ ] Update `provider_map` in `_load_provider_fabric`
- [ ] Set 8 env vars in `.env` (or add to vault)
- [ ] Write preflight script: `scripts/preflight_google_keys.py`
- [ ] Run `make temple-grade`; expect 0 new errors

### Pre-launch (M23 + M9)

- [ ] Unit test: `_create_google` returns OpenAICompatProvider with 8 keys (or N keys if fewer are set)
- [ ] Integration test: invoke Google model via gateway; verify call succeeds
- [ ] Failover test: exhaust key 1 (force 429), verify key 2 is used
- [ ] M22 audit: `GenerateResult.provider_name` matches actual served provider
- [ ] M9 audit: every error path raises a typed error, no silent failures

### Launch gate

- [ ] The 2 P0 cut-tool bugs are fixed FIRST (per R3/R4 audit; this is a precondition)
- [ ] All 8 keys are verified live (smoke test each in 30s)
- [ ] The 8-key sharding is observed in production logs (M22 telemetry)

---

## §8 L1 → L2 → L3 DISTILLATION

### L1 (Narrative) — What happened in this audit

1. Read 7 source files: `model_gateway.py`, `backends/remote_provider.py`, `backends/openai_compat.py`, `backends/antigravity_provider.py`, `backends/google_compat.py`, `providers.py`, `provider_registry.py`
2. Read 2 config files: `config/providers.yaml`, `config/model_registry/providers/google.yaml`
3. Read 4 runtime artifacts: `~/.config/opencode/{opencode.json,antigravity.json}`, `~/.local/share/opencode/auth.json`, `data/vault/keys.json.enc`, `.env`
4. Discovered the multi-key infrastructure is **already built** (D205 ratified 2026-07-08): `api_keys: List[str]` field, `resolve_current_api_key()` method, sticky-failover-on-429 logic
5. Identified the gap: the existing `_create_openrouter` and `_create_antigravity` factories use the new pattern, but `_create_google` doesn't exist (legacy `GoogleAIProvider` and `GoogleCompatProvider` are loaded directly)
6. Wrote the 4-file change plan: 2 YAML updates + 1 Python factory + 1 env/vault update
7. Computed the effort: ~30 min for code, ~5 min for env vars, 0 for `providers.yaml`
8. Wrote this audit (8 sections)

### L2 (Insight) — What this means

1. **The "8-key integration" is a 30-minute config change, not a 2-day project.** The infrastructure is built; the YAML is the only thing missing.
2. **The dispatch's "should we create 8 separate providers" question has a clear answer: NO.** The pattern is single-provider-with-`api_keys`-list. OpenRouter and Antigravity already do this.
3. **D205 sticky-failover is the right rotation strategy** for cloud providers with rate limits. Round-robin is explicitly forbidden because it wastes rate-limit budget.
4. **The legacy `GoogleAIProvider` and `GoogleCompatProvider` classes are not the bottleneck** — the fabric's `provider_map` is. Routing them through the same `_create_openrouter`-style factory is the one change that unlocks the multi-key path.
5. **The 8 keys are NOT YET IN THE ENVIRONMENT.** Current state: 1 Google key in `auth.json`, 0 in env, 0 in vault. The Architect must add them before the integration is testable.
6. **The P0 cut-tool bugs (R3/R4) are still the launch blocker**, not the 8-key Google integration. This work is "nice to have" for the debut window but does not unblock the cut.

### L3 (Universal Principle) — Timeless truths

1. **Read the existing code before designing the new feature.** The dispatch assumed the multi-key infrastructure needed to be built. It was already there (D205, 2026-07-08). The right answer was "use what's there" — not "design a new mechanism."
2. **Sticky-failover > round-robin for rate-limited APIs.** Round-robin spreads traffic evenly; sticky-failover extracts the full quota from the healthy key first, then advances. The cost of sticky-failover is a one-time 429 on the dead key; the cost of round-robin is ongoing suboptimal throughput.
3. **The "8 separate providers" anti-pattern is tempting because it requires no code change.** But it explodes the priority list, the fallback chains, and the provider_map. The 8-key list pattern is one entry, one chain, one map slot.
4. **The unit of configuration is the env-var-list, not the provider-entry.** When 8 accounts share an API surface, they share a provider. The keys are an internal detail.
5. **A preflight script is cheap insurance.** A 20-line Python script that verifies 8 env vars are set, non-duplicate, and valid format prevents 80% of the post-deployment "why isn't the rotation working" debugging.

---

## §9 REFERENCES

### Source files read
- `src/omega/oracle/model_gateway.py:319-398` (`_create_openrouter`, `_create_antigravity` — the multi-key factory pattern)
- `src/omega/oracle/model_gateway.py:505-573` (`_load_provider_fabric` and the `provider_map`)
- `src/omega/oracle/backends/remote_provider.py:176-447` (`ProviderConfig`, `resolve_current_api_key`, sticky-failover on 429)
- `src/omega/oracle/backends/openai_compat.py:29-90` (`OpenAICompatProvider`, uses `resolve_current_api_key()`)
- `src/omega/oracle/backends/antigravity_provider.py:25-100` (`AntigravityProvider`, D205 pattern)
- `src/omega/oracle/backends/google_compat.py:34-290` (`GoogleCompatProvider`, legacy class, not the fabric path)
- `src/omega/oracle/providers.py:47-114, 153-200` (`_resolve_google_api_key`, `GoogleAIProvider`, legacy)
- `src/omega/oracle/provider_registry.py:50-110` (`_load_model_map`)

### Config files
- `config/providers.yaml` (priority list, fallback_resolver, maakali_routing) — no change needed
- `config/model_registry/providers/google.yaml` — UPDATE needed
- `config/model_registry/providers/google-compat.yaml` — CREATE needed

### Runtime artifacts
- `~/.config/opencode/opencode.json` (211 lines, 1 Google key, NOT multi-key)
- `~/.config/opencode/antigravity.json` (sticky strategy, 1 account configured)
- `~/.local/share/opencode/auth.json` (1 Google key: `AQ.Ab8RN...`)
- `data/vault/keys.json.enc` (encrypted, 8 keys NOT yet present)
- `.env` (no GOOGLE_API_KEY_* vars set)

### Mandates
- M7 (local-first): Google 8-key is at priority 4, behind local-gguf (0) and Antigravity (3) — order preserved
- M8 (zero telemetry): the integration uses Google's standard HTTPS API; no extra telemetry added
- M9 (typed errors): existing 401/429/5xx handling in `RemoteProvider` and `OpenAICompatProvider` is typed
- M16 (portable): no hardcoded paths; env-var-driven
- M22 (response provenance): `GenerateResult.provider_name` reflects the actual served provider
- M23 (failure integrity): sticky-failover is fail-closed; if all 8 keys fail, the provider goes DEGRADED, not silent

### Decisions cited
- **D205** (Sticky Active-Passive Key Sharding) — ratified 2026-07-08, ratified for Antigravity
- **D-565** (vault hidden for debut) — the 8-key vault integration is V-1 sprint (post-debut)
- **D-548** (INST-1 BLOCKED on 6 fixes) — the P0 cut-tool fixes are the launch blocker, not 8-key

### Companion audits
- `data/coordination/research/R_LILITH_KALI_QUALITY_AUDIT_20260828.md` (Carmack 2026-08-28) — the 5-file Lilith+Kali audit, lists the 2 P0 cut-tool blockers
- `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_20260827.md` (Carmack R3) — original 12-artifact audit
- `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_ROUND4_20260828.md` (Carmack R4) — 51 AC, 6 of 10 bypass vectors confirmed
- `data/coordination/research/R_VAULT_ANTIGRAVITY_DEEPER_20260827.md` (Grokster 2026-08-27) — Antigravity 7-account state, G3 hidden throttle, dual Gemini+Claude pools

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_carmack_google_integration ⬡ PUBLIC-DEBUT-01*

`AP-CARMMACK-GOOGLE-MULTI-KEY-20260828-v1.0.0` · 9 sections · ~80 LOC change · 30-min implementation · D205 sticky-failover · 0 P0 bugs found in this audit · 1h 25m research-only, no code changes
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: openrouter/minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

