# 🔱 Phase 1C: Cline CLI Multi-Account Isolation Spec
**AP Token**: `AP-RESEARCHER-PHASE1C-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ gemini-3.1-pro-preview-customtools ⬡ opencode ⬡ trc_phase1c_cline ⬡ ACTIVE
**Date**: 2026-07-23
**Source**: Cline CLI v2.0+ (GitHub: cline/cline, fd8cecdd)
**Architect Constraint**: D-432 — Zero paid accounts, all free tier. D-437 — Phase 1 free-tier only, no proxy layer.

---

## 🎯 Executive Summary (L1)

Cline CLI achieves multi-account isolation via **configuration directory separation** (`--config` flag or `CLINE_DATA_DIR` env var). Each account gets its own `~/.cline-<account>/` directory containing independent `providers.json` (API keys, OAuth tokens), `globalState.json`, `secrets.json` (legacy), and SQLite session DB. **No built-in rotation** — isolation is manual via directory switching. VaultCore must orchestrate 8 Cline instances by managing 8 config directories and injecting credentials via `providers.json` at lease acquisition.

---

## 🔬 Deep Dialectic (L2)

### 1. The Architect (Systemic Logic)
**Mechanism**: `--config <path>` or `CLINE_DATA_DIR=<path>` redirects **all** Cline state:
```
<config_dir>/
├── data/
│   ├── settings/
│   │   ├── providers.json      # ← API keys, OAuth tokens (PRIMARY)
│   │   ├── global-settings.json
│   │   └── cline_mcp_settings.json
│   ├── globalState.json
│   ├── workspace/
│   ├── tasks/
│   └── sessions/               # SQLite session DB
└── log/
```
**Provider Config** (`providers.json` v1):
```json
{
  "version": 1,
  "lastUsedProvider": "anthropic",
  "providers": {
    "anthropic": {
      "settings": {
        "provider": "anthropic",
        "auth": {
          "accessToken": "sk-ant-...",
          "refreshToken": "...",
          "expiresAt": 1899578924000,
          "accountId": "..."
        },
        "model": "anthropic/claude-sonnet-4.6"
      },
      "updatedAt": "2026-01-01T00:00:00.000Z",
      "tokenSource": "oauth"
    },
    "openai": { ... },
    "google": { ... }
  }
}
```

### 2. The Adversary (Critical Rigor)
**Gaps**:
- **No credential rotation API** — Cline CLI doesn't expose "swap key" at runtime
- **Secrets encryption**: `secrets.json` (legacy) was plaintext; `providers.json` stores tokens in plaintext (OS keychain integration in PR #6233, macOS only, Linux/Windows fallback to file)
- **Session DB isolation**: Each config dir has own SQLite — good for isolation, bad for cross-account analytics
- **MCP settings per-instance**: `cline_mcp_settings.json` duplicated per account — VaultCore must sync MCP config across 8 dirs

### 3. The Alchemist (Creative Synthesis)
**Pattern**: "Config directory as credential namespace" — maps perfectly to VaultCore lease model. Lease = write `providers.json` to account's config dir → spawn Cline with `--config <dir>`. **Innovation**: Use `CLINE_PROVIDER_SETTINGS_PATH` env var (test helper) to inject `providers.json` at runtime without file write — but production needs file persistence for plugin compatibility.

### 4. The Archivist (Historical Truth)
**Migration**: `secrets.json` (expiresAt in seconds) → `providers.json` (expiresAt in milliseconds, 2026-03-24 commit 9b29903). **Keychain PR #6233** (2026-07): macOS `security`, Linux `secret-tool`, Windows `CredentialManager` — but E2E tests reduced to macOS only (regression). **Standalone Cline** (JetBrains, CLI) uses this; VS Code extension uses VS Code `context.secrets`.

---

## 📋 Actionable Config Specs (L3)

### 1. 8-Account Directory Layout
```
/home/arcana-novai/.cline-fleet/
├── acct-01/  # providers.json → Anthropic key 1
├── acct-02/  # providers.json → Anthropic key 2
├── acct-03/  # providers.json → OpenAI key 1
├── acct-04/  # providers.json → OpenAI key 2
├── acct-05/  # providers.json → Google key 1 (Antigravity OAuth)
├── acct-06/  # providers.json → Google key 2
├── acct-07/  # providers.json → OpenRouter key 1
├── acct-08/  # providers.json → OpenRouter key 2
┎ shared/
    ├── cline_mcp_settings.json  # Symlinked into each acct-XX/
    └── global-settings.json     # Symlinked
```

### 2. VaultCore Lease → Cline Config Injection
```python
# VaultCore lease acquisition for Cline account
async def lease_cline_account(vault, account_id: str) -> str:
    # 1. Get credential from VaultCore
    cred = await vault.get_secret(f"cline/{account_id}")
    # cred = { "provider": "anthropic", "api_key": "sk-ant-...", "model": "claude-sonnet-4.6" }
    
    # 2. Build providers.json
    providers_json = {
        "version": 1,
        "lastUsedProvider": cred["provider"],
        "providers": {
            cred["provider"]: {
                "settings": {
                    "provider": cred["provider"],
                    "auth": {
                        "accessToken": cred["api_key"],
                        "expiresAt": 0,  # API keys don't expire
                        "tokenSource": "api_key"
                    },
                    "model": cred["model"]
                },
                "updatedAt": datetime.utcnow().isoformat() + "Z",
                "tokenSource": "api_key"
            }
        }
    }
    
    # 3. Write to account's config dir
    config_dir = Path(f"/home/arcana-novai/.cline-fleet/{account_id}")
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "data" / "settings").mkdir(parents=True, exist_ok=True)
    (config_dir / "data" / "settings" / "providers.json").write_text(json.dumps(providers_json, indent=2))
    
    # 4. Symlink shared MCP config
    shared_mcp = Path("/home/arcana-novai/.cline-fleet/shared/cline_mcp_settings.json")
    target_mcp = config_dir / "data" / "settings" / "cline_mcp_settings.json"
    if not target_mcp.exists():
        target_mcp.symlink_to(shared_mcp)
    
    return str(config_dir)
```

### 3. Spawning Cline with Leased Config
```bash
# VaultCore returns config_dir, agent spawns:
cline --config /home/arcana-novai/.cline-fleet/acct-03 "your task here"

# Or via env var:
CLINE_DATA_DIR=/home/arcana-novai/.cline-fleet/acct-03 cline "task"
```

### 4. Multi-Provider Per Account (Advanced)
Single account dir can hold multiple providers in `providers.json`:
```json
{
  "providers": {
    "anthropic": { "settings": { "auth": { "accessToken": "sk-ant-..." }, "model": "claude-sonnet-4.6" }},
    "openai": { "settings": { "auth": { "accessToken": "sk-..." }, "model": "gpt-4o" }},
    "google": { "settings": { "auth": { "accessToken": "ya29..." }, "model": "gemini-3-flash" }}
  }
}
```
**Rotation at Cline level**: `cline --config <dir> -P anthropic` vs `-P openai` — but VaultCore should manage at lease level (one provider per lease for clean quota isolation).

---

## 🛡️ Mandate Alignment Checklist

| Mandate | Status | Evidence |
|---------|--------|----------|
| **M1 AnyIO** | ✅ | Cline CLI is Node.js; VaultCore Python uses AnyIO for subprocess |
| **M7 Local-First** | ✅ | All credentials local filesystem; no cloud secret store |
| **M8 Zero Telemetry** | ✅ | `CLINE_TELEMETRY_DISABLED=1` in spawn env |
| **M14 Heritage** | N/A | No id Software patterns |
| **M23 Failure Integrity** | ⚠️ | Plaintext `providers.json` — **must encrypt at rest via VaultCore** |
| **M25 Streaming Resilience** | N/A | Cline handles streaming; VaultCore lease TTL covers session |

---

## 🚀 Dev Strategy Revisal Recommendations

### Immediate (P0-2 — This Week)
1. **Provision 8 config directories** with symlinked shared MCP/settings
2. **VaultCore `providers.json` generator** per credential type (API key, OAuth, Antigravity)
3. **Encrypt `providers.json` at rest** in VaultCore; decrypt on lease → write to config dir

### Short-term (P1-1 — VaultCore Schema)
1. **Cline credential schema**:
   ```yaml
   provider: "cline"
   cred_type: "api_key" | "oauth" | "antigravity"
   encrypted_blob: "<age-encrypted providers.json fragment>"
   metadata:
     config_dir: "/home/arcana-novai/.cline-fleet/acct-03"
     provider: "anthropic"
     model: "claude-sonnet-4.6"
   ```

### Medium-term (P2 — Orchestration)
1. **Cline fleet manager**: Track 8 spawned processes, health, quota via Cline's `--json` output parsing
2. **Session persistence**: VaultCore checkpoints Cline SQLite session DB on lease release

---

## 📦 Deliverables for Phase 3 Synthesis

| Artifact | Location | Purpose |
|----------|----------|---------|
| Cline Fleet Directory Spec | `docs/research/R_CLINE_FLEET_LAYOUT.md` | 8-account isolation layout |
| VaultCore Cline Credential Schema | `docs/research/R_VAULT_SCHEMA_V2.md` (extended) | `cred_type: cline_api_key` etc. |
| Providers.json Generator | `src/omega/vaultcore/cline_config.py` | Lease → config dir injection |
| Shared MCP Sync Script | `scripts/sync_cline_mcp.py` | Keep 8 dirs in sync |

---

## 🔗 Cross-References

| Provider | Phase 1 Report | Key Integration Point |
|----------|----------------|----------------------|
| **Antigravity OAuth** | `PHASE1B_ANTIGRAVITY_OAUTH_...` | Stored as `providers.json` entry type `google` with `tokenSource: oauth` |
| **OpenRouter** | `PHASE1D_OPENROUTER_...` | `providers.json` entry type `openrouter` with BYOK keys |
| **Grok CLI** | Grokster G1-15 | Separate binary; not Cline-compatible — different isolation |

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ PHASE1C-COMPLETE ⬡ 2026-07-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: gemini-3.1-pro-preview-customtools | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
