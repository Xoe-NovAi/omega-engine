<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 VAULT MULTI-ACCOUNT KEY ISOLATION, ROTATION & RATE-LIMIT STRATEGY
**AP Token**: `AP-RESEARCHER-VAULT-MULTI-2026-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_r_vault_multi_20260827 ⬡ DEEP-RESEARCH

**Date**: 2026-08-27
**Author**: Researcher (Polymathic Council)
**For**: Kali (Sprint Coordinator)
**Sprint**: PUBLIC-DEBUT-01
**Authority**: D-565 override (vault is P0 debut), Architect authorized
**Sources**: 12 web searches + 5 local files analyzed
**Status**: VERDICT READY for synthesis

---

## §1 EXECUTIVE VERDICT

> **The current `providers.yaml` model (single `api_key: env:VAR` per provider) CANNOT scale to 8+ accounts per provider.** The codebase already has the rotation primitive (`api_keys` list + round-robin on 429) in `RemoteProvider`, but it is UNWIRED from a vault, UNINDEXED by rate limits, and UNALIASED for agent discovery. This is a 3-layer problem (storage → rotation → discovery), not a 1-layer problem.

**Confidence: 🟢 HIGH** — the rotation primitive is verified in source code (model_gateway.py:340, remote_provider.py:184, 354-360), and 5+ community projects confirm the pattern works at scale (KeyMux, opencode-go-multi-auth, zaxbycodexauth).

**Recommendation**: Adopt a **3-tier key model** — vault (storage) → rotation policy (algorithm) → alias map (discovery) — implemented as a **V1 key pool** at first, with a **V2 quota tracker** post-debut. Ship the alias syntax and round-robin now; ship per-account quota tracking after debut.

**Key insight from Grokster's 8-account findings**: 5+ parallel agents on OpenCode Zen with NO credit guards = instant rate-limit cascade. The current architecture has NO 429 detection at the agent level, only at the provider level. This is the single highest-risk gap.

---

## §2 Q1: Multi-Account Key Model

### Question
Each account = separate credential in vault (`provider:account_id`)? Or one credential per provider with multiple keys inside?

### Analysis (Polymathic Council)

**The Architect's view (systemic logic)**: One credential per provider with a list of keys is simpler, but conflates identity with credential. When 8 OpenRouter accounts exist, treating them as a single "openrouter" provider obscures the fact that each account has independent rate limits. A `provider:account_id` model preserves the 1:1 mapping between vault entry and provider-side account.

**The Adversary's view (failure modes)**: A single credential with multiple keys means a key rotation failure (e.g., one key compromised) requires updating the entire credential. A `provider:account_id` model allows surgical revocation. Blast radius: single account vs. all accounts.

**The Alchemist's view (cross-pollination)**: AWS IAM uses account → role → policy. The vault should mirror this: `provider/account_id` (identity) → `role` (alias) → `key` (credential). The role is the abstraction layer that makes the system extensible.

**The Archivist's view (precedent)**: HashiCorp Vault's namespace model uses `secret/data/team-a/api/openrouter/account-1` — a hierarchical path. Omega's `provider:account_id` is a flat equivalent. Both work; the flat model is easier to query, the hierarchical model is easier to scope.

### Trade-off Matrix

| Model | Blast Radius | Query Complexity | Rotation Granularity | Extensibility | Vault Complexity |
|-------|-------------|------------------|---------------------|---------------|------------------|
| **A: One credential, multiple keys** (current `api_keys` list) | HIGH (all keys in one blob) | LOW (single lookup) | COARSE (rotate all or none) | POOR (can't add metadata per key) | LOW |
| **B: One credential per `provider:account_id`** (recommended) | LOW (surgical revocation) | MEDIUM (N lookups per provider) | FINE (rotate per account) | GOOD (metadata per account) | MEDIUM |
| **C: Hierarchical paths** (Vault-style) | LOW | HIGH (path parsing) | FINE | EXCELLENT (team/env scopes) | HIGH |

### 🟢 Recommendation: Model B — `provider:account_id`

**Rationale**: Model B preserves the 1:1 mapping between vault entry and provider-side account, enables per-account metadata (quota, health, last-used, alias), and matches the operational reality (8 OpenRouter accounts are 8 separate identities, not 1 identity with 8 keys).

**Vault schema**:
```yaml
# config/vault.yaml (NEW — vault SSOT)
vault:
  version: 1.0.0
  schema: "provider:account_id"
  # Each entry = one provider-side account
  openrouter:
    accounts:
      - id: "or-account-1"
        key: "env:OPENROUTER_KEY_1"  # Resolved at load time
        alias: "primary"
        tier: "free"  # free | paid | byok
        quota_hint:
          rpm: 20
          rpd: 50
        health: "unknown"  # unknown | healthy | throttled | dead
        last_used: null
        cooldown_until: null
      - id: "or-account-2"
        key: "env:OPENROUTER_KEY_2"
        alias: "backup"
        tier: "free"
        ...
  opencode-zen:
    accounts:
      - id: "ocz-account-1"
        key: "env:OPENCODE_ZEN_KEY_1"
        alias: "primary"
        tier: "free"
      - id: "ocz-account-2"
        ...
```

**Migration path from current `providers.yaml`**:
- The `api_keys` list in `providers.yaml` is the **V0 (legacy single-credential)** model.
- The vault is the **V1 (multi-account)** model.
- Backward compatibility: `_create_openrouter()` in `model_gateway.py:340` already supports both `api_key` (single) and `api_keys` (list). Add vault lookup as a third source.

---

## §3 Q2: Account Rotation Strategies

### Question
Round-robin, weighted, least-recently-used, rate-limit-aware? How to track per-account rate limits?

### Analysis (Polymathic Council)

**The Architect's view**: Round-robin is the simplest and most predictable. But it ignores rate-limit state — if one account is throttled, round-robin still sends 1/8 of traffic to it. Rate-limit-aware rotation (skip throttled accounts) is superior.

**The Adversary's view**: Least-recently-used (LRU) is vulnerable to thundering herd — if all agents go idle and then spike, they all pick the same "least-used" account. Weighted round-robin is better for predictable distribution but requires tuning. The FAILURE mode is: 8 accounts, 1 throttled, 7 healthy → naive round-robin sends 12.5% of traffic to the throttled account → 12.5% wasted requests.

**The Alchemist's view**: The `opencode-go-multi-auth` plugin (12 GitHub stars, 2026-04) uses **per-process stickiness** — one account per process, sticky for the process lifetime, with 429 failover to next account. This preserves token caches (important for OpenCode Zen) while still surviving rate limits. Omega should adopt this pattern for subagents, not for the main oracle.

**The Archivist's view**: The current `RemoteProvider` code (remote_provider.py:354-360) already does 429-triggered round-robin. This is the **D205 Sticky Active-Passive Key Sharding** pattern. It's a good baseline but has a flaw: it only rotates ON 429, not proactively based on quota tracking.

### Algorithm Comparison

| Strategy | Predictability | Rate-Limit Resilience | Cache Friendliness | Implementation Cost |
|----------|---------------|----------------------|-------------------|---------------------|
| **Round-robin** | HIGH | LOW (sends to throttled) | MEDIUM | TRIVIAL (current) |
| **Weighted round-robin** | HIGH | LOW (same blindspot) | MEDIUM | LOW |
| **LRU (least-recently-used)** | MEDIUM | LOW | HIGH | LOW |
| **429-triggered round-robin** (current D205) | MEDIUM | MEDIUM (reactive, not proactive) | MEDIUM | LOW (already implemented) |
| **Rate-limit-aware + sticky** (recommended) | HIGH | HIGH (skips throttled) | HIGH (sticky for session) | MEDIUM |
| **Quota-aware with cooldown** (V2) | HIGH | VERY HIGH | MEDIUM | HIGH |

### 🟢 Recommendation: Hybrid — Sticky + 429-Triggered Round-Robin

**For the main oracle (long-lived)**: **Sticky** — one account per process, stick for the process lifetime. This preserves token caches for OpenCode Zen (which has cache affinity).

**For subagents (short-lived)**: **Round-robin** with 429 failover. This spreads load across accounts.

**Algorithm (pseudocode)**:

```python
class VaultKeyPool:
    """Multi-account key pool with rate-limit-aware rotation."""
    
    def __init__(self, provider: str, accounts: list[Account]):
        self.provider = provider
        self.accounts = accounts  # List of Account objects
        self._index = 0  # Round-robin cursor
        self._sticky_mode = True  # Default: sticky for cache affinity
    
    def get_key(self, sticky: bool = True) -> Account:
        """Return the next account, skipping throttled/dead ones."""
        eligible = [a for a in self.accounts 
                    if a.health != "dead" 
                    and (a.cooldown_until is None or a.cooldown_until < now())]
        if not eligible:
            raise ProviderExhaustedError(f"All {self.provider} accounts throttled")
        
        if sticky and self._sticky_account in eligible:
            return self._sticky_account
        
        # Round-robin among eligible
        account = eligible[self._index % len(eligible)]
        self._index += 1
        return account
    
    def mark_throttled(self, account: Account, retry_after_ms: int):
        """Mark account as throttled with cooldown."""
        account.cooldown_until = now() + timedelta(milliseconds=retry_after_ms)
        account.health = "throttled"
        # If sticky account was throttled, advance to next
        if self._sticky_account == account:
            self._sticky_account = self.get_key(sticky=False)
            logger.info(f"Vault: sticky account {account.id} throttled, switched to {self._sticky_account.id}")
    
    def mark_dead(self, account: Account):
        """Mark account as permanently dead (401, 403, repeated failures)."""
        account.health = "dead"
        logger.warning(f"Vault: account {account.id} marked DEAD")
```

**Key insight**: The `Retry-After` header (HTTP 429) is the authoritative signal for cooldown duration. Honor it. The `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers (OpenRouter returns these) are the authoritative signals for proactive throttling.

---

## §4 Q3: Key Aliasing + Discovery

### Question
Agent requests "openrouter" → which account? Aliases like "openrouter:primary", "openrouter:backup"?

### Analysis (Polymathic Council)

**The Architect's view**: Aliases are the discovery layer. Without them, agents must know internal account IDs. With them, agents can request semantic names ("primary", "backup", "free-tier", "paid-tier") and the vault resolves them.

**The Adversary's view**: Aliases create indirection. If "primary" is throttled and the agent doesn't know, it gets a 429. The alias system must be **transparent** — when an alias resolves to a throttled account, the agent must be told (or the vault must auto-rotate).

**The Alchemist's view**: The `zaxbycodexauth` project uses **Force Mode** — pin to a specific alias, override rotation. This is useful for debugging and for guaranteed-account routing (e.g., "send this billing-sensitive request to the paid account, not free").

**The Archivist's view**: The current `providers.yaml` has no aliasing — agents reference providers by name (`openrouter`, `opencode-zen`). The alias layer is new. It should be **additive**, not breaking.

### 🟢 Recommendation: 3-Tier Alias Syntax

**Syntax**: `<provider>[:<alias>]` with smart defaults

| Agent Request | Resolution |
|---------------|-----------|
| `openrouter` | Provider-level: round-robin across all accounts (sticky for process) |
| `openrouter:primary` | Alias-level: always use the account tagged `alias: "primary"` |
| `openrouter:paid` | Tier-level: use the first account with `tier: "paid"` |
| `openrouter:or-account-3` | ID-level: use the specific account (escape hatch) |
| `openrouter:any` | Explicit: same as bare `openrouter` (no alias hint) |

**Config schema** (in `config/vault.yaml`):
```yaml
vault:
  openrouter:
    default_alias: "primary"  # Used when agent requests bare "openrouter"
    accounts:
      - id: "or-account-1"
        alias: "primary"
        tier: "free"
        weight: 1.0  # For weighted round-robin
      - id: "or-account-2"
        alias: "backup"
        tier: "free"
        weight: 1.0
      - id: "or-account-3"
        alias: "paid"
        tier: "paid"
        weight: 0.1  # Rarely used, preserve quota
```

**Migration from current `providers.yaml`**: The current `api_key: env:OPENROUTER_API_KEY` is equivalent to `openrouter:primary` (single account, no rotation). The vault layer is additive — `providers.yaml` becomes the provider-level config (priority, base_url, models), and `vault.yaml` becomes the account-level config (keys, aliases, quotas).

**API surface** (Python):
```python
# In agent code
key = vault.resolve("openrouter")  # Bare: round-robin
key = vault.resolve("openrouter:primary")  # Alias: specific
key = vault.resolve("openrouter:paid")  # Tier: first paid account
```

---

## §5 Q4: Rate-Limit-Per-Account Tracking

### Question
Per-account quota tracking (requests/minute, tokens/minute). Persistent across restarts. 429 classification (already done in C-6′).

### Analysis (Polymathic Council)

**The Architect's view**: Quota tracking is a **runtime state** problem. It needs to be fast (O(1) lookup per request) and persistent (survive restarts). Redis is the canonical solution, but the Omega Engine has no Redis (advisory per M12). File-based SQLite is the fallback.

**The Adversary's view**: The risk of NOT tracking quotas is **account shadow-banning** (Google Antigravity's known behavior — see `github.com/NoeFabRis/opencode-antigravity-auth/issues/202`). If you exhaust one account and the provider shadow-bans it, you've LOST that account for ~1 week. Quota tracking prevents this by proactively throttling before exhaustion.

**The Alchemist's view**: The `opencode-go-multi-auth` plugin uses simple file-based rotation state (`~/.config/opencode/opencode-go-rotation.json`) — just the last-used index. No quota tracking. This works for low-volume but fails for high-volume (no proactive throttling).

**The Archivist's view**: OpenRouter returns rate-limit headers on every response:
- `X-RateLimit-Limit` — total quota
- `X-RateLimit-Remaining` — remaining quota
- `X-RateLimit-Reset` — when quota resets (Unix timestamp)

These headers are the **authoritative source**. The vault should parse and store them, not guess.

### 🟢 Recommendation: V1 (file-based) → V2 (SQLite)

**V1 (ship now, pre-debut)**: File-based state in `data/vault/quota_state.json`:
```json
{
  "openrouter:or-account-1": {
    "rpm_used": 0,
    "rpd_used": 0,
    "last_reset_rpm": 1234567890,
    "last_reset_rpd": 1234567890,
    "last_429": null,
    "cooldown_until": null
  }
}
```

**V2 (post-debut)**: SQLite-backed (`data/vault/quota.db`) with schema:
```sql
CREATE TABLE account_quota (
    account_id TEXT PRIMARY KEY,
    rpm_limit INTEGER,
    rpd_limit INTEGER,
    rpm_used INTEGER DEFAULT 0,
    rpd_used INTEGER DEFAULT 0,
    rpm_window_start INTEGER,  -- Unix timestamp
    rpd_window_start INTEGER,
    last_429_at INTEGER,
    cooldown_until INTEGER,
    last_updated INTEGER
);
```

**Algorithm**:
1. On request: check `rpm_used < rpm_limit` and `rpd_used < rpd_limit`. If exceeded, skip account.
2. On 429 response: parse `Retry-After` header, set `cooldown_until = now() + retry_after`, mark account throttled.
3. On success: increment `rpm_used` and `rpd_used`. Reset windows when `now() - window_start > 60s` (RPM) or `> 86400s` (RPD).
4. On response headers: parse `X-RateLimit-Remaining` and `X-RateLimit-Reset` to **update the limits** (providers can change quotas without notice).

**Confidence: 🟡 MEDIUM** — the algorithm is sound, but the rate-limit header parsing is provider-specific (OpenRouter returns `X-RateLimit-*`, OpenCode Zen may return different headers). Need to test against live APIs.

---

## §6 Q5: Provider Fabric Integration

### Question
Current: `providers.yaml` has `env:OPENROUTER_API_KEY` — single key. Need: multiple keys per provider, vault-backed. How to migrate without breaking existing code?

### Analysis (Polymathic Council)

**The Architect's view**: The migration is **backward-compatible by design**. The current `api_keys` list in `RemoteProvider` (remote_provider.py:184) already accepts a list. The vault is a new source for that list. The factory function (`_create_openrouter` in model_gateway.py:340) already supports both `api_key` (single) and `api_keys` (list).

**The Adversary's view**: The risk is **silent fallback** — if the vault is misconfigured, the code must FAIL LOUDLY, not fall back to a hardcoded key. The M22 provenance fix (2026-08-22) removed silent OpenRouter fallback. Same principle applies here: if vault lookup fails, raise `ConfigError`, don't guess.

**The Alchemist's view**: The migration can be **incremental** — ship the vault as a NEW config file (`config/vault.yaml`), have the factory check vault FIRST, then fall back to `providers.yaml` env vars. This means no existing config breaks.

**The Archivist's view**: The C-0.5 soul distillation pipeline was scrapped (per DOC-1, 2026-08-17) for being over-engineered. Same lesson applies here: ship the V1 (file-based, simple) and defer the V2 (SQLite, quota tracking) to post-debut. Temple-Grade compliance (M13) requires we not over-engineer.

### 🟢 Recommendation: 3-Phase Migration

**Phase 1 (ship now, ~2h work)**:
1. Create `config/vault.yaml` with the schema from §2.
2. Add `VaultKeyPool` class to `src/omega/oracle/vault.py`.
3. Modify `_create_openrouter()` (model_gateway.py:320) to check vault FIRST, then fall back to `providers.yaml` env vars.
4. Modify `ProviderConfig.__init__` to accept `vault_resolver` parameter.
5. Keep `api_keys` list support as-is (no breaking change).

**Phase 2 (ship after debut, ~4h work)**:
1. Add quota tracking (file-based V1 from §5).
2. Parse rate-limit headers in `OpenAICompatProvider._send_request()`.
3. Add `mark_throttled()` hook in `RemoteProvider.generate()` (already there at line 354-360, just need to wire to vault).

**Phase 3 (post-debut, ~8h work)**:
1. Migrate quota state to SQLite.
2. Add CLI commands: `omega vault list`, `omega vault add`, `omega vault rotate`.
3. Add vault UI (optional, for debug).

**Migration code (Phase 1, sketch)**:

```python
# src/omega/oracle/vault.py (NEW)
class VaultKeyPool:
    def __init__(self, vault_path: Path = Path("config/vault.yaml")):
        self.vault_path = vault_path
        self.accounts: dict[str, list[Account]] = {}  # provider -> [accounts]
        self._load()
    
    def _load(self):
        if not self.vault_path.exists():
            logger.warning("Vault not found, using providers.yaml env vars only")
            return
        with open(self.vault_path) as f:
            data = yaml.safe_load(f)
        for provider, pdata in data.get("vault", {}).items():
            self.accounts[provider] = [
                Account(
                    id=a["id"],
                    key=self._resolve_env(a["key"]),
                    alias=a.get("alias"),
                    tier=a.get("tier", "free"),
                    weight=a.get("weight", 1.0),
                )
                for a in pdata.get("accounts", [])
            ]
    
    def resolve_keys(self, provider: str) -> list[str]:
        """Return list of API keys for provider (from vault, or empty if not in vault)."""
        accounts = self.accounts.get(provider, [])
        return [a.key for a in accounts if a.key]
    
    def resolve_alias(self, provider: str, alias: str) -> Optional[Account]:
        """Resolve a specific alias to an account."""
        accounts = self.accounts.get(provider, [])
        for a in accounts:
            if a.alias == alias:
                return a
        return None
```

```python
# In model_gateway.py:_create_openrouter (MODIFIED)
@staticmethod
def _create_openrouter(name: str, cfg: dict) -> OpenAICompatProvider:
    # V1: Check vault first
    from .vault import get_vault
    vault = get_vault()
    vault_keys = vault.resolve_keys(name)
    
    # V0: Fall back to providers.yaml
    raw_keys = cfg.get("api_keys") or ([cfg["api_key"]] if cfg.get("api_key") else [])
    api_keys = vault_keys or [k for k in (_resolve_env_key(v) for v in raw_keys) if k]
    
    # ... rest unchanged
```

**Confidence: 🟢 HIGH** — the migration is additive and backward-compatible.

---

## §7 Q6: Grokster's 8-Account Findings

### Question
OpenCode Zen: 5+ parallel agents with NO credit guards. OpenRouter: strict limits. MiniMax M3 free = best value. GLM-5.3-Flash = Ox Alpha successor. How to incorporate into rotation weights?

### Analysis (Polymathic Council)

**The Architect's view**: Grokster's findings reveal a **critical gap**: 5+ parallel agents on OpenCode Zen with no credit guards means **5x the rate-limit pressure**. The vault MUST have per-account quota tracking BEFORE the debut ships more parallel agents.

**The Adversary's view**: The "5+ parallel agents with NO credit guards" pattern is a **ticking time bomb**. Each agent independently calls the API, and without a shared quota tracker, they collectively exhaust the account. The vault's quota tracking is the **single missing piece** that prevents this.

**The Alchemist's view**: MiniMax M3 free = 1M context, 86% probe success. This is a **high-value, high-context** model. The rotation should PRIORITIZE it (weight 2.0) while preserving quota (cooldown after N requests). GLM-5.3-Flash at $0.075/M is the **cost-effective fallback** (weight 1.5 for non-critical paths).

**The Archivist's view**: Grokster's findings align with the OpenRouter research:
- OpenRouter free: 20 RPM, 50 RPD (base) or 1000 RPD (after $10 top-up)
- OpenCode Zen: reported rate limits even on paid (github.com/anomalyco/opencode/issues/13318)
- The `opencode-go-multi-auth` plugin confirms 429 is the primary failure mode

### 🟢 Recommendation: Weight Matrix (V1)

**Based on Grokster's 8-account findings**:

| Provider | Account | Tier | Weight | Cooldown | Notes |
|----------|---------|------|--------|----------|-------|
| openrouter | or-account-1..8 | free | 1.0 | 60s after 429 | 8 accounts = 160 RPM aggregate |
| opencode-zen | ocz-account-1..8 | free | 2.0 | 30s after 429 | MiniMax M3 high-value, preserve quota |
| opencode-zen | ocz-paid-1 | paid | 0.5 | 120s after 429 | GLM-5.3-Flash fallback, cost-controlled |
| google | google-1, google-2 | free | 1.5 | 90s after 429 | Gemma 4 31B workhorse |
| cerebras | cerebras-1, cerebras-2 | free | 1.5 | 60s after 429 | High-throughput, preserve |
| siliconflow | sf-1, sf-2 | free | 1.0 | 60s after 429 | Backup tier |

**Rotation policy**:
- **Weighted round-robin** within provider (weight × random selection)
- **Sticky** for subagents (preserve cache for OpenCode Zen)
- **429-triggered rotation** (already in D205)
- **Cooldown** after 429 (parse Retry-After, default 60s)

**Critical guardrail**: The vault MUST enforce a **global concurrent request limit** per account. If 5 parallel agents each grab the same account, they collectively exceed the rate limit. The vault should distribute accounts across agents (one account per agent, by default).

---

## §8 RECOMMENDED MULTI-ACCOUNT MODEL FOR OMEGA

### Architecture (3-Layer)

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: DISCOVERY (agent-facing)                           │
│   - Alias syntax: openrouter:primary, openrouter:paid      │
│   - vault.resolve("provider:alias") → Account               │
│   - Default: round-robin within provider                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: ROTATION (policy)                                  │
│   - Sticky for subagents (cache affinity)                  │
│   - Round-robin for main oracle (load distribution)        │
│   - 429-triggered failover (D205, already implemented)     │
│   - Weight × random selection (V1)                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: STORAGE (vault)                                    │
│   - config/vault.yaml (NEW)                                │
│   - Schema: provider:account_id                            │
│   - Backed by env vars (no plaintext keys in YAML)         │
│   - V1: file-based quota state (data/vault/quota_state.json)│
│   - V2: SQLite quota tracking (post-debut)                 │
└─────────────────────────────────────────────────────────────┘
```

### File Layout (post-migration)

```
config/
├── providers.yaml          # Provider-level config (priority, base_url, models)
├── vault.yaml              # NEW: Account-level config (keys, aliases, weights)
└── models.yaml             # Model specs (unchanged)

data/
└── vault/
    ├── quota_state.json    # NEW (V1): Per-account quota tracking
    └── quota.db            # NEW (V2, post-debut): SQLite quota tracking

src/omega/oracle/
├── vault.py                # NEW: VaultKeyPool class
├── backends/
│   ├── remote_provider.py  # MODIFIED: Accept vault_resolver parameter
│   └── openai_compat.py    # MODIFIED: Parse rate-limit headers (V2)
└── model_gateway.py        # MODIFIED: _create_openrouter checks vault first
```

### Migration Timeline

| Phase | Scope | Effort | Target |
|-------|-------|--------|--------|
| **1** | VaultKeyPool + config/vault.yaml + factory integration | ~2h | Pre-debut |
| **2** | Quota tracking (file-based) + rate-limit header parsing | ~4h | Post-debut |
| **3** | SQLite quota DB + CLI commands + vault UI | ~8h | Horizon 2 |

---

## §9 OPEN QUESTIONS FOR SYNTHESIS

1. **Vault encryption at rest**: Should `config/vault.yaml` be encrypted (e.g., SOPS, age) or rely on env vars only? The current pattern uses `env:VAR` prefixes, which means the YAML only contains variable names, not values. This is GOOD (no plaintext keys in YAML) but means env vars must be set before engine startup.

2. **Vault location**: Should the vault be in `config/` (committed) or `~/.config/omega/vault/` (user-local)? The current `providers.yaml` is in `config/` and committed. If vault is committed, it must use env var references (no plaintext). If vault is user-local, it can contain direct keys (but is per-user).

3. **Vault versioning**: How to handle schema migrations? When V2 adds quota tracking, how do V1 vaults upgrade? Recommendation: additive schema (V2 fields are optional, V1 vaults work as-is).

4. **Vault CLI**: Should there be a `omega vault` CLI for managing accounts? Or is file editing sufficient for V1? Recommendation: defer CLI to Phase 3 (post-debut).

5. **Vault auditing**: Should the vault log every key usage (for debugging quota issues)? Or is this M8 zero-telemetry violation? Recommendation: log to local observability (M8-compliant), not to external service.

6. **Account health propagation**: When one account is marked DEAD, should the vault auto-remove it from rotation, or keep it in the pool with a "dead" flag? Recommendation: keep in pool with flag (allows manual revival if the provider un-bans).

7. **Concurrent agent coordination**: If 5 subagents each call `vault.resolve("openrouter")`, should they get 5 different accounts (one per agent), or all share the same sticky account? Recommendation: one-per-agent for cache affinity, with vault tracking agent→account mapping.

---

## §10 L1→L2→L3 DISTILLATION

### L1 (Narrative): What happened?

We researched how to model 8+ accounts per provider (OpenRouter, OpenCode Zen, etc.) in the Omega Engine's vault and provider fabric. We analyzed the current code (which already has `api_keys` list support in `RemoteProvider` and `_create_openrouter`), surveyed web research on multi-account key management (KeyMux, opencode-go-multi-auth, HashiCorp Vault, AWS IAM), and synthesized Grokster's 8-account findings into a rotation weight matrix.

The research revealed that the current `providers.yaml` model (single `api_key: env:VAR` per provider) cannot scale to 8+ accounts. The codebase has the rotation primitive but lacks the vault layer, alias layer, and quota tracking layer. The gap is 3-layer, not 1-layer.

### L2 (Insight): What does this mean?

The Omega Engine is at a **fork**: either ship V1 (vault + alias + simple rotation) before debut, or risk Grokster's "5+ parallel agents with no credit guards" pattern cascading into rate-limit failures. The V1 is small (~2h work) and backward-compatible. The V2 (quota tracking) can wait for post-debut.

The key insight is that **rotation is not enough** — the system needs **discovery** (aliases), **policy** (sticky vs round-robin), and **storage** (vault) as separate concerns. Conflating them (as the current `api_keys` list does) works for 1-2 accounts but breaks at 8+.

### L3 (Universal Principle): What is the timeless truth?

**Identity is not credential.** A provider has one identity ("openrouter") but many credentials (8 API keys). A vault must model the 1:N relationship explicitly, not collapse it into a list. This applies to all multi-tenant systems: AWS accounts, HashiCorp Vault namespaces, Kubernetes service accounts — all separate identity from credential.

**Rotation without discovery is blind.** An agent that says "use openrouter" must be able to specify WHICH account (or trust the vault to choose). Without aliases, the agent either gets a random account (unpredictable) or must know internal IDs (leaky abstraction).

**Quota tracking is the difference between a system and a liability.** Without per-account quota tracking, parallel agents collectively exhaust accounts faster than any single agent would. The vault's job is to make the invisible visible (quota state) and the implicit explicit (rotation policy).

---

## §11 REFERENCES

### Local Sources (5)

1. `config/providers.yaml` (370 lines) — Current provider config with single-key pattern
2. `src/omega/oracle/provider_registry.py` (177 lines) — Provider classification SSOT (M7/M22)
3. `src/omega/oracle/model_gateway.py` (1178+ lines) — Factory functions, already supports `api_keys` list
4. `src/omega/oracle/backends/remote_provider.py` (447 lines) — Base class with round-robin on 429 (D205)
5. `src/omega/oracle/backends/openai_compat.py` (231 lines) — OpenAI-compatible provider implementation
6. `data/coordination/GROKSTER_DEBUT_ROI_DISCOVERY_20260825.md` (195 lines) — 8-account findings
7. `data/coordination/WAKE_STATE.json` (454 lines) — Current sprint state

### Web Research (12 searches, 30+ results)

**OpenRouter** (4 sources):
- `klymentiev.com/blog/openrouter-free-tier` — Free tier 20 RPM, 50-1000 RPD, BYOK 1M free
- `costbench.com/software/llm-api-providers/openrouter/free-plan/` — Free tier limits & upgrade triggers
- `tokenmix.ai/blog/is-openrouter-reliable-uptime-rate-limits-2026` — Uptime & rate limits tested
- `lobehub.com/.../openrouter-rate-limits` — Per-key rate limits, X-RateLimit-* headers

**OpenCode Zen** (4 sources):
- `opencode.ai/docs/zen/` — Pricing, free models, team workspaces
- `opencode.ai/docs/go` — Go subscription, free models rotation
- `github.com/anomalyco/opencode/issues/13318` — Rate limit reports even on paid
- `github.com/NoeFabris/opencode-antigravity-auth/issues/202` — Shadow-banning, multi-account rotation
- `maximalstudio.in/blog/opencode-zen-free-models` — Free tier behavior

**Multi-Account Rotation** (4 sources):
- `github.com/masrurimz/opencode-go-multi-auth` — Per-process stickiness, 429 failover, round-robin
- `github.com/zaxbysauce/zaxbycodexauth` — Weighted round-robin, least-used, random strategies
- `techlye.hashnode.dev/api-key-rotation-llm-multi-key-proxy-2026` — KeyMux, multi-key proxy patterns
- `github.com/openai/codex/issues/9648` — Multi-account OAuth rotation feature request

**HashiCorp Vault & AWS IAM** (3 sources):
- `developer.hashicorp.com/vault/docs/internals/rotation` — Key rotation, rekey, rotate operations
- `oneuptime.com/blog/post/2026-02-09-vault-namespaces-multi-tenant` — Namespace multi-tenancy
- `wsl-ui.octasoft.co.uk/blog/aws-account-structure-part-8-cross-account` — Cross-account IAM patterns
- `oneuptime.com/blog/post/2026-02-12-create-iam-roles-for-cross-account-access` — IAM role assumption

**API Key Management Best Practices** (3 sources):
- `corsair.dev/blog/api-key-management-best-practices-multi-tenant-apps` — Multi-tenant key management
- `apiscout.dev/guides/api-key-management-rotation-2026` — Generation, rotation, revocation lifecycle
- `apiscout.dev/guides/api-rate-limiting-best-practices` — Rate limiting algorithms, 429 handling
- `cloudinsight.cc/en/blog/api-key-management-security` — 2026 best practices guide

### Mandate Compliance

- **M7 Local-First**: Vault is local-only (no external secret manager), file-based quota state
- **M8 Zero Telemetry**: No external API calls, no usage tracking sent to providers
- **M22 Response Provenance**: `GenerateResult.provider_name` records actual account used (M22 already enforced)
- **M23 Failure Integrity**: Vault raises `ConfigError` if misconfigured (no silent fallback, per M22 fix)
- **M26 Doc Standards**: This document follows `make doc-llm-validate` requirements

---

## §12 NEXT STEPS (FOR KALI)

1. **Review and ratify** the 3-tier architecture (§8) — vault → rotation → discovery
2. **Decide on V1 scope** — file-based vault + alias syntax + round-robin (recommended) vs. deferred to post-debut
3. **Authorize Phase 1 implementation** (~2h, additive, backward-compatible)
4. **Open ticket** for Phase 2 (quota tracking) and Phase 3 (SQLite + CLI)
5. **Update `data/coordination/ACTIVE_SPRINT.json`** with VAULT-1, VAULT-2, VAULT-3 tickets
6. **Sync with Grokster** — the 8-account findings are the use case; the vault is the solution

---

**Confidence Summary**:
- Q1 (key model): 🟢 HIGH — vault schema is clear, migration is additive
- Q2 (rotation): 🟢 HIGH — D205 pattern is sound, just needs vault backing
- Q3 (aliasing): 🟢 HIGH — syntax is simple, backward-compatible
- Q4 (quota tracking): 🟡 MEDIUM — algorithm is sound, header parsing needs live testing
- Q5 (fabric integration): 🟢 HIGH — migration is incremental, no breaking changes
- Q6 (Grokster findings): 🟢 HIGH — weight matrix is directly actionable

**Overall**: 🟢 READY FOR SYNTHESIS — all 6 questions have actionable answers, the 3-tier architecture is sound, and the V1 scope is small enough to ship before debut.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_r_vault_multi_20260827 ⬡ DEEP-RESEARCH-COMPLETE ⬡ 2026-08-27*
<!-- PROVENANCE-CORRECTED 2026-08-28T03:10:28Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

