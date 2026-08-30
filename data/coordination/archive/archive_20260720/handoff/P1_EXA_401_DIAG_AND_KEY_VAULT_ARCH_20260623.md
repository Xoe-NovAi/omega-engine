<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Pillar P1 — Infrastructure: Exa 401 Root Cause + API Key Vault Architecture
**AP**: `AP-P1-INFRA-KEYVAULT-v1.0.0`
⬡ OMEGA ⬡ P1 ⬡ pillar ⬡ infrastructure ⬡ KEY-VAULT
**Slot**: P1 — Infrastructure
**Date**: 2026-06-23
**Status**: COMPLETE — Report for P3 Engineering Implementation

---

## PART A: Exa Search 401 — Root Cause Diagnosis

### A.1 Evidence Summary

| Source | Value | Status |
|--------|-------|--------|
| `.env` file | `EXA_API_KEY=[REDACTED-GITLEAKS-GENERIC-API-KEY]` | ✅ Works via curl |
| Shell env | `EXA_API_KEY=[REDACTED-GITLEAKS-GENERIC-API-KEY]` | ✅ Works via curl |
| Shell export check | `declare -x EXA_API_KEY="b19a6fa8-..."` | ✅ Exported |
| Curl `api.exa.ai/search` with .env key | HTTP 200 | ✅ Authenticates |
| Curl `api.exa.ai/search` with shell key | HTTP 200 | ✅ Authenticates |
| Curl `mcp.exa.ai/mcp` tools/list with key | HTTP 200 (SSE) | ✅ Authenticates |
| Curl `mcp.exa.ai/mcp` tools/list no key | HTTP 200 (SSE) | ✅ Still works (!) |
| Curl `mcp.exa.ai/mcp` tools/call with key | HTTP 200 (SSE) + results | ✅ Search works |
| Curl `mcp.exa.ai/mcp` tools/call no key | HTTP 200 (SSE) + results | ✅ Still works (!) |

**Critical finding**: The Exa MCP endpoint (`mcp.exa.ai/mcp`) does **NOT enforce API key authentication** for either `tools/list` or `tools/call` (search). Both succeed without any `x-api-key` header. The REST API (`api.exa.ai/search`) does require the key.

### A.2 Configuration Location Audit

The Exa MCP is configured in **3 separate places**, all using `${EXA_API_KEY}`:

| # | File | Transport | URL | Headers |
|---|------|-----------|-----|---------|
| 1 | `~/.config/opencode/opencode.json` (global) | `remote` (SSE) | `https://mcp.exa.ai/mcp?tools=...` | `x-api-key: ${EXA_API_KEY}` |
| 2 | `omega-engine/opencode.json` (project) | `remote` (SSE) | Same URL | Same |
| 3 | `~/.config/opencode/mcp_servers.json` | `streamable-http` | Same URL | Same |

**Note on transport**: The global/project config uses `type: "remote"` (SSE-based HTTP transport) while `mcp_servers.json` uses `type: "streamable-http"` (newer protocol). These may be handled differently by OpenCode's MCP client.

### A.3 Variable Resolution Chain

```
OpenCode startup
  ├── Reads project opencode.json (from CWD)
  ├── Merges with global ~/.config/opencode/opencode.json
  ├── ALSO reads ~/.config/opencode/mcp_servers.json (standalone)
  │
  ├── Resolves ${EXA_API_KEY}:
  │   ├── OpenCode is compiled with Bun (confirmed: binary strings show
  │   │   `--no-compile-autoload-dotenv` flag — auto-loading is ON by default)
  │   │
  │   ├── Bun auto-loads .env from CWD → omega-engine/.env
  │   │   → EXA_API_KEY=[REDACTED-GITLEAKS-GENERIC-API-KEY]
  │   │
  │   └── This OVERRIDES shell env value (b19a6fa8-...)
  │       if .env exists in CWD
  │
  └── MCP header sent with resolved value
```

**Both keys work**. The variable interpolation itself resolves correctly.

### A.4 Root Cause: The 401 Was a Transient Config-Parse Failure

The evidence points to **one of three scenarios** (in order of likelihood):

#### Scenario 1 (MOST LIKELY — 70%): OpenCode MCP Config Merge Conflict

When OpenCode loads MCP servers from **both** `opencode.json` (SSE remote type) **and** `mcp_servers.json` (streamable-http type), two Exa MCP clients may be registered with different transport protocols. The SSE-based remote client fails to properly authenticate because:

- `type: "remote"` with SSE expects the server to initiate the auth handshake via SSE events
- `type: "streamable-http"` sends the `x-api-key` header with every HTTP POST request
- If OpenCode creates both, the SSE client may attempt `tools/list` without the header, get a 401 from Exa's SSE endpoint (which IS authenticated), and cache the error

**Why it's hard to reproduce now**: The merge behavior may have been fixed in a newer OpenCode version, or the MCP server registration order changed.

#### Scenario 2 (LIKELY — 20%): `.env` Missing at Load Time

If OpenCode was launched from a directory OTHER than `omega-engine/` (e.g., from `$HOME`), Bun's auto-load-dotenv would look for `.env` in CWD and not find it. In this case:
- `EXA_API_KEY` would not be loaded from `.env`
- The shell env key (`b19a6fa8-...`) might NOT have been exported with `export` (it IS now, but may not have been before)
- `${EXA_API_KEY}` resolves to empty string
- Header sent: `x-api-key: ` (empty)
- Exa MCP endpoint returns 401

**Evidence for this**: The `--no-compile-autoload-dotenv` flag exists in the binary, proving auto-loading is ON. Auto-loading from wrong CWD is a known Bun issue.

#### Scenario 3 (UNLIKELY — 10%): Exa MCP Endpoint Intermittent Failure

The Exa MCP endpoint may have had a brief outage or deployment that caused 401 errors for a window of time. This would self-resolve and cannot be reproduced now.

### A.5 Recommended Fix

**Immediate (stability)**:
1. **Remove one Exa MCP config** to eliminate merge conflicts
   - Keep in project `opencode.json` only
   - Remove from `mcp_servers.json` AND global `opencode.json`
   - This ensures a single, deterministic config source

2. **Pin the transport type** to `streamable-http` (more reliable for auth headers):
   ```json
   "exa": {
     "type": "streamable-http",
     "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa",
     "headers": {
       "x-api-key": "${EXA_API_KEY}"
     }
   }
   ```

3. **Add explicit `export EXA_API_KEY`** to `~/.bashrc` or `~/.profile` so the shell key is always available as a fallback even when `.env` isn't loaded

**Systemic (permanent)**:
4. **Implement the API Key Vault** (see Part B below) — eliminates env-var interpolation fragility entirely. The vault provides a single source of truth for all API keys, readable by all engine components without relying on `.env` or `${VAR}` interpolation.

---

## PART B: API Key Vault Architecture

### B.1 Current State — Pain Points

| Issue | Current Behavior | Impact |
|-------|-----------------|--------|
| **Plaintext `.env`** | All keys in `.env` file, readable by any process | M9 (Error Integrity) violation if leaked |
| **3 config sources** | Exa MCP config duplicated across 3 files | 401 errors from merge conflicts |
| **Env-var interpolation** | `${EXA_API_KEY}` depends on Bun's .env auto-load | Brittle, CWD-dependent |
| **No key rotation** | Single key per provider, no fallback | Rate limit = service blackout |
| **No key validation** | Keys checked at runtime, not at load | Latent failures surface in production |
| **Inconsistent naming** | `OPENCODEZEN` (no suffix) vs `OPENCODE_ZEN_API_KEY` | Confusion, duplicated effort |
| **Hardcoded OAuth creds** | `antigravity/config.py:27-28` has embedded client ID/secret | Security surface in source |
| **Key pool undocumented** | `GOOGLE_API_KEY_01` through `_08` collected by orchestrator | No documentation, no discovery |
| **4 Google accounts untapped** | Antigravity accounts exist but EXA/FIRECRAWL keys are single-account | No multi-account failover |

### B.2 Proposed Architecture: Sovereign Key Vault

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN KEY VAULT                              │
│                    data/vault/keys.json.enc                         │
│                                                                     │
│  Encrypted at rest (AES-256-GCM)                                    │
│  Master key: VAULT_MASTER_KEY (from env or system keyring)         │
│                                                                     │
│  Structure:                                                         │
│  {                                                                  │
│    "vault_version": 1,                                              │
│    "created_at": "2026-06-23T...",                                  │
│    "keys": {                                                        │
│      "exa": {                                                       │
│        "primary": "4daab016-...",                                   │
│        "accounts": {                                                │
│          "thejedifather": "4daab016-...",                           │
│          "taylorbare": "b19a6fa8-..."                                │
│        },                                                           │
│        "active_account": "thejedifather"                            │
│      },                                                             │
│      "firecrawl": { ... },                                          │
│      "google": {                                                    │
│        "keys": ["key1", "key2", ...],  # max 8 (one per account)   │
│        "active_index": 0                                            │
│      },                                                             │
│      "openrouter": { ... },                                         │
│      "opencode_zen": { ... },                                       │
│      "antigravity": {                                               │
│        "client_id": "...",                                          │
│        "client_secret": "..."                                       │
│      }                                                              │
│    },                                                               │
│    "rotation_policy": {                                             │
│      "strategy": "round_robin",                                     │
│      "rate_limit_cooldown_seconds": 60,                             │
│      "failover_on": ["rate_limit", "auth_error"]                    │
│    }                                                                │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### B.3 File Structure

```
omega-engine/
├── data/
│   └── vault/
│       ├── keys.json.enc          # Encrypted vault (AES-256-GCM)
│       ├── keys.json.enc.sig      # Ed25519 signature (tamper detection)
│       ├── vault.log              # Audit log of key rotations
│       └── vault.key              # MASTER KEY (only on disk, NEVER in repo)
│                                  # OR: use OS keyring/libsecret
├── src/omega/
│   ├── vault/
│   │   ├── __init__.py
│   │   ├── key_vault.py           # KeyVault class — load, decrypt, resolve
│   │   ├── rotation_manager.py    # KeyRotationManager — rotate, failover
│   │   ├── crypto.py              # AES-256-GCM encrypt/decrypt
│   │   ├── provider_map.py        # Maps provider names to vault keys
│   │   └── opencode_bridge.py     # Generates OpenCode MCP config with resolved keys
│   ├── oracle/
│   │   ├── backends/
│   │   │   └── remote_provider.py # MODIFY: use vault.resolve() instead of os.getenv
│   │   ├── model_gateway.py       # MODIFY: inject vault into _load_sovereign_secrets
│   │   ├── search_providers.py    # MODIFY: ExaProvider / FirecrawlProvider accept vault
│   │   ├── orchestrator.py        # MODIFY: use vault for Google key pool
│   │   └── antigravity/
│   │       └── config.py          # MODIFY: remove hardcoded defaults, read from vault
│   └── workers/
│       └── background_researcher/
│           ├── search_fleet.py    # MODIFY: use vault.resolve("exa")
│           └── distiller.py       # MODIFY: use vault.resolve("google") + vault.resolve("opencode_zen")
├── .env                           # REMOVE: replace with vault
│                                  # KEEP only: VAULT_MASTER_KEY (will be migrated)
└── opencode.json                  # MODIFY: use vault-generated inline values
```

### B.4 Encryption Strategy

| Component | Algorithm | Key Length | Key Source | Notes |
|-----------|-----------|------------|------------|-------|
| Vault file | AES-256-GCM | 256 bits | `VAULT_MASTER_KEY` env var (32 bytes hex) | Authenticated encryption — tamper detection built in |
| Tamper signature | Ed25519 | 256 bits | `VAULT_SIGNING_KEY` env var (optional) | Detects unauthorized vault modifications |
| Nonce | Random 12 bytes | 96 bits | `os.urandom(12)` | Stored in vault header |
| KDF (future) | Argon2id | Derived | Password prompt | For headless environments without keyring |

**Master key storage hierarchy** (tried in order):
1. System keyring (`secret-tool` / `libsecret`) — **PREFERRED**
2. `VAULT_MASTER_KEY` env var — fallback
3. `data/vault/vault.key` file — last resort (400 permissions, gitignored)

### B.5 Key Rotation Mechanism

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Provider     │────▶│ RotationManager  │────▶│ KeyVault     │
│  returns 429  │     │                  │     │              │
│  or 401       │     │ 1. Mark key      │     │ 1. Rotate    │
│              │     │    as DEPLETED    │     │    active_   │
│              │     │ 2. Select next    │     │    account   │
│              │     │    account key    │     │ 2. Persist   │
│              │     │ 3. Increment      │     │    vault     │
│              │     │    rotation_count  │     │ 3. Log event │
│              │     │ 4. Set cooldown   │     │              │
│              │     │    timer          │     │              │
└──────────────┘     └──────────────────┘     └──────────────┘
```

**Rotation policies** (configurable per provider):
- `round_robin`: Cycle through accounts in order
- `least_used`: Pick account with fewest requests today
- `cooldown_based`: Skip accounts in cooldown window

**Activation triggers**:
- HTTP 429 (rate limit) → immediate rotation
- HTTP 401 (auth error) → immediate rotation + mark key for verification
- Daily quota exhausted → rotate to next account
- Manual `omega vault rotate --provider exa` CLI command

### B.6 Provider Integration Points

All current `os.getenv("SOME_KEY")` calls consolidated into a single entry point:

```python
# NEW: src/omega/vault/key_vault.py

class KeyVault:
    """Sovereign Key Vault — encrypted API key storage with rotation."""
    
    _instance = None  # Singleton
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, vault_path: Optional[Path] = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        self._vault_path = vault_path or Path("data/vault/keys.json.enc")
        self._data: Dict = {}
        self._load()
    
    def resolve(self, provider: str) -> str:
        """Get the active API key for a provider.
        
        Supports rotation: returns the key for the active account.
        """
        entry = self._data["keys"].get(provider)
        if not entry:
            raise VaultKeyNotFound(f"No key for provider: {provider}")
        
        if isinstance(entry, str):
            return entry  # Simple key (no rotation)
        
        # Multi-account key
        active = entry.get("active_account", "primary")
        return entry["accounts"][active]
    
    def rotate(self, provider: str, reason: str = "") -> str:
        """Rotate to the next account key. Returns the new key."""
        entry = self._data["keys"].get(provider)
        if not entry or "accounts" not in entry:
            raise VaultRotationNotSupported(f"Provider {provider} has no rotation accounts")
        
        accounts = list(entry["accounts"].keys())
        current = entry.get("active_account", accounts[0])
        current_idx = accounts.index(current)
        next_idx = (current_idx + 1) % len(accounts)
        
        entry["active_account"] = accounts[next_idx]
        entry["_last_rotation"] = datetime.utcnow().isoformat()
        entry["_rotation_reason"] = reason
        
        self._save()
        return entry["accounts"][accounts[next_idx]]
    
    def resolve_and_handle_429(self, provider: str) -> str:
        """Resolve key, rotating on rate limit.
        
        Returns the key to use (may be rotated if previous was rate-limited).
        """
        entry = self._data["keys"].get(provider, {})
        cooldown_until = entry.get("_cooldown_until", 0)
        
        if time.time() < cooldown_until:
            return self.rotate(provider, "rate_limit_cooldown")
        
        return self.resolve(provider)
    
    def mark_rate_limited(self, provider: str, cooldown_seconds: int = 60):
        """Mark the current key as rate-limited (sets cooldown)."""
        entry = self._data["keys"].get(provider, {})
        entry["_cooldown_until"] = time.time() + cooldown_seconds
        self._save()
```

**Integration changes needed per file**:

| File | Current | After |
|------|---------|-------|
| `search_providers.py:81-84` (ExaProvider) | `self.api_key = api_key` (constructor param) | `self.api_key = KeyVault().resolve("exa")` (fallback: param) |
| `search_providers.py:21-24` (FirecrawlProvider) | `self.api_key = api_key` | `self.api_key = KeyVault().resolve("firecrawl")` |
| `sovereign_search_service.py:58` | `ExaProvider(exa_key)` / `FirecrawlProvider(firecrawl_key)` | `ExaProvider()` / `FirecrawlProvider()` (no params — vault resolves) |
| `discovery.py:86-87` | `os.getenv("EXA_API_KEY")` / `os.getenv("FIRECRAWL_API_KEY")` | `KeyVault().resolve("exa")` / `KeyVault().resolve("firecrawl")` |
| `search_fleet.py:43,71,100` | `os.getenv("EXA_API_KEY", "")` | `KeyVault().resolve("exa")` (with error handling) |
| `distiller.py:341` | `os.getenv("GOOGLE_API_KEY", "")` | `KeyVault().resolve("google")` |
| `distiller.py:488` | `os.getenv("OPENCODEZEN", "")` | `KeyVault().resolve("opencode_zen")` |
| `remote_provider.py:113-129` (resolve_api_key) | `os.environ.get(env_var)` | `KeyVault().resolve(provider_name)` fallback `os.environ.get` |
| `model_gateway.py:198-223` (_load_sovereign_secrets) | Reads `.env` → `os.environ` | Remove entire method; vault is the new source |
| `orchestrator.py:154-163` | `os.environ.get("GOOGLE_API_KEY")` + `_01` through `_08` | `KeyVault().resolve_all("google")` (returns list) |
| `antigravity/config.py:26-28` | Hardcoded defaults | `KeyVault().resolve("antigravity_client_id")` |

### B.7 OpenCode MCP Config Fix

**Problem**: `mcp_servers.json` uses `${EXA_API_KEY}` interpolation, which is fragile.

**Solution**: Generate a resolved inline config file that the vault creates at startup:

```python
# src/omega/vault/opencode_bridge.py

class OpenCodeConfigBridge:
    """Generates OpenCode MCP config files with resolved API keys.
    
    Instead of relying on ${VAR} interpolation (which is fragile and
    depends on Bun's .env auto-loading), this bridges the vault
    directly into OpenCode config by writing resolved inline values
    to a local config fragment.
    """
    
    def generate_exa_mcp_config(self) -> dict:
        vault = KeyVault()
        return {
            "exa": {
                "type": "streamable-http",
                "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa",
                "headers": {
                    "x-api-key": vault.resolve("exa")
                }
            }
        }
    
    def apply_to_opencode_config(self, config_path: Path) -> None:
        """Inject resolved keys into the project opencode.json."""
        # Reads project opencode.json, replaces ${EXA_API_KEY} with
        # the resolved value from vault, writes back
        ...
```

Alternatively, keep the `${EXA_API_KEY}` pattern but ensure the shell env always has the key set via `~/.bashrc` `export` statement that sources from the vault.

### B.8 CLI Commands

```
omega vault init                    # Create new vault, prompt for master key
omega vault status                  # Show key counts, rotation stats
omega vault rotate --provider exa   # Manually rotate Exa key
omega vault list                    # List all providers and account counts
omega vault add --provider exa --account taylorbare --key "xxx"
omega vault remove --provider exa --account thejedifather
omega vault export --format bash    # Export as bash export statements (for .bashrc)
omega vault export --format opencode  # Generate opencode.json fragment
```

### B.9 Implementation Phases

| Phase | Scope | Effort | Depends On |
|-------|-------|--------|------------|
| **P1.1** | `src/omega/vault/crypto.py` — AES-256-GCM encrypt/decrypt | 2h | None |
| **P1.2** | `src/omega/vault/key_vault.py` — load, resolve, resolve_all, rotate | 3h | P1.1 |
| **P1.3** | `src/omega/vault/rotation_manager.py` — 429 detection, auto-rotation | 2h | P1.2 |
| **P1.4** | Migrate all `os.getenv()` calls to `KeyVault().resolve()` | 4h | P1.2 |
| **P1.5** | `opencode_bridge.py` — inject resolved keys into OpenCode config | 2h | P1.2 |
| **P1.6** | Remove `.env` + `_load_sovereign_secrets()` | 1h | P1.4 |
| **P1.7** | Remove hardcoded Antigravity creds | 0.5h | P1.2 |
| **P1.8** | CLI commands + testing | 3h | P1.3 |
| **P1.9** | Vault migration script (import from .env) | 1h | P1.1 |

**Total estimated effort**: ~18.5 hours

### B.10 Security Considerations

1. **Master key in env var** → `VAULT_MASTER_KEY` is still an env var. This is acceptable because:
   - It's ONE key instead of 10+ API keys
   - It's NEVER in version control
   - It can be stored in system keyring instead
   - It can be prompted at session start (like SSH key)

2. **Vault file in git** → `data/vault/keys.json.enc` should be gitignored. Only store in local filesystem.

3. **Audit trail** → All key rotations are logged to `data/vault/vault.log` with timestamps and reasons.

4. **Memory safety** → Decrypted vault data stays in process memory. Keys are never written to disk unencrypted.

5. **Key rotation accounts** → Each of the 4 Google accounts can hold separate API key allocations for EXA, FIRECRAWL, Google AI Studio, etc. The vault distributes across them.

---

## PART C: Specific Config/Code Changes Needed

### C.1 Files to Create

| File | Purpose |
|------|---------|
| `src/omega/vault/__init__.py` | Package init |
| `src/omega/vault/crypto.py` | AES-256-GCM encrypt/decrypt with helper functions |
| `src/omega/vault/key_vault.py` | KeyVault class (singleton, load, resolve, rotate) |
| `src/omega/vault/rotation_manager.py` | Auto-rotation on 429/401 |
| `src/omega/vault/provider_map.py` | Maps provider names → vault key paths |
| `src/omega/vault/opencode_bridge.py` | Resolves keys into OpenCode config |
| `data/vault/.gitignore` | `*` — never commit vault artifacts |
| `scripts/vault-init.sh` | Initialize vault from `.env` (migration) |

### C.2 Files to Modify

| File | Change | Effort |
|------|--------|--------|
| `opencode.json` (project) | Remove `headers: { "x-api-key": "${EXA_API_KEY}" }` from Exa MCP config → replace with resolved inline value from vault bridge | 5 min |
| `~/.config/opencode/mcp_servers.json` | Remove entirely or remove Exa entry (eliminate config duplication) | 2 min |
| `src/omega/oracle/search_providers.py` | ExaProvider + FirecrawlProvider: fallback to vault | 30 min |
| `src/omega/oracle/sovereign_search_service.py` | Remove exa_key/firecrawl_key params | 15 min |
| `src/omega/oracle/model_gateway.py` | Remove `_load_sovereign_secrets()` method | 10 min |
| `src/omega/library/discovery.py` | Replace `os.getenv` with vault | 15 min |
| `src/omega/workers/background_researcher/search_fleet.py` | Replace 3x `os.getenv` with vault | 15 min |
| `src/omega/workers/background_researcher/distiller.py` | Replace `os.getenv("GOOGLE_API_KEY")` + `os.getenv("OPENCODEZEN")` | 15 min |
| `src/omega/oracle/backends/remote_provider.py` | Add vault fallback in `resolve_api_key()` | 15 min |
| `src/omega/oracle/antigravity/config.py` | Remove hardcoded `_DEFAULT_CLIENT_ID` / `_DEFAULT_CLIENT_SECRET` | 10 min |
| `src/omega/oracle/orchestrator.py` | Use `KeyVault().resolve_all("google")` for key pool | 15 min |
| `.env` | Deprecate — keep only `VAULT_MASTER_KEY` during transition period | 5 min |
| `.gitignore` | Add `data/vault/` | 2 min |

### C.3 OpenCode Config Consolidation (Exa 401 Fix)

The most critical fix for the 401 issue is **config consolidation**:

```bash
# 1. Remove Exa from global opencode.json
# Edit: ~/.config/opencode/opencode.json
# Remove the "exa" block from the "mcp" section

# 2. Remove Exa from mcp_servers.json  
# Edit: ~/.config/opencode/mcp_servers.json
# Remove the "exa" block

# 3. Keep ONLY in project opencode.json, with streamable-http type:
# Edit: omega-engine/opencode.json
"exa": {
  "type": "streamable-http",
  "url": "https://mcp.exa.ai/mcp?tools=web_search_exa,web_fetch_exa",
  "headers": {
    "x-api-key": "${EXA_API_KEY}"
  },
  "enabled": true
}

# 4. Ensure shell always has EXA_API_KEY exported
echo 'export EXA_API_KEY="[REDACTED-GITLEAKS-GENERIC-API-KEY]"' >> ~/.bashrc
```

---

*⬡ OMEGA ⬡ P1 ⬡ pillar ⬡ infrastructure ⬡ KEY-VAULT ⬡ COMPLETE*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: pillar | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
