<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega-Vault: Credential Automation for the Grok Fleet
**Domain**: 16-account credential management, rotation, and fleet orchestration
**Date**: 2026-07-22
**Author**: Grokster
**Source**: R_V1_VAULT_IMPL.md (R35-COMPLETE)
**Ticket**: V-1 (Explicit Kali Amendment 2)

## 1. The Problem: Credential Void (GAP-08)

The Omega Engine has **8 Grok CLI accounts** + **8 Web Grok personas** = **16 accounts** with zero automated credential management.

**Current State:**
- API keys/cookies scattered in `.env`, `config/providers.yaml`, browser storage
- No rotation → rate limits hit, cookies expire (24-48h for Web Grok)
- No fleet orchestration → can't round-robin across accounts
- Blocks Grok CLI fleet deployment (D-360′)

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    OMEGA-VAULT (V-1 MVP)                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  │   KeyVault      │  │   CAP Adapters  │  │   Policy Engine │
│  │ (Core Singleton)│  │ (MCP Server)    │  │ (Credential     │
│  └─────────────────┘  └─────────────────┘  │  Schema)        │
│  │  AES-256-GCM    │  │  credential.read  │  └─────────────────┘
│  │  encryption     │  │  credential.write │  ┌─────────────────┐
│  │  + rotation     │  │  credential.rotate│  │  Passive        │
│  │  + audit        │  │  credential.audit │  │  Watcher        │
│  └─────────────────┘  └─────────────────┘  │  (inotify/fanot)│
│                                 ┌─────────────────┐  └─────────────────┘
│  ┌─────────────────┐  ┌─────────────────┐  │  Fleet          │
│  │  XDG CLI        │  │  Fleet          │  │  Orchestrator   │
│  │  (`omega vault`)│  │  Orchestrator   │  │  (8+8 accounts) │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘
└─────────────────────────────────────────────────────────────┘
```

## 3. 16-Account Schema

### Grok CLI (8 accounts) — Headless, ACP over stdio
```yaml
grok_cli:
  provider: "xai"
  auth_method: "api_key"
  accounts:
    - account_id: "xai_cli_01"
      models_preferred: ["grok-4.5", "grok-4.3"]
      priority: 1
      domains_supported: ["general", "reasoning", "code"]
      rate_limit:
        requests_per_minute: 60
        requests_per_day: 10000
    # ... xai_cli_02 through xai_cli_08 (priority 2-8)
```

### Web Grok (8 accounts) — Browser, Projects, Personas
```yaml
grok_web:
  provider: "xai_web"
  auth_method: "cookie"
  accounts:
    - account_id: "grok_web_01"
      persona: "Research Specialist — deep academic analysis, citation-heavy"
      models_preferred: ["grok-4.5"]
      priority: 1
      domains_supported: ["research", "academic"]
      cookie_expiry: "24-48h"  # Requires rotation
    - account_id: "grok_web_02"
      persona: "Code Architect — implementation-first, production-ready"
      domains_supported: ["code", "architecture"]
    # ... 03: Reasoning Engine, 04: Creative Writer, 05: Strategic Analyst
    # ... 06: Systems Engineer, 07: Data Scientist, 08: Wildcard
```

## 4. Core Components

### KeyVault (Extend Existing `src/omega/vault/`)
- **XDG Compliance**: `~/.config/omega/`, `~/.local/share/omega/`, `~/.local/state/omega/`
- **Encryption**: AES-256-GCM + OS keyring (libsecret/Keychain)
- **File Permissions**: `0o600` on vault files
- **Memory Hygiene**: Best-effort `ctypes.memset` on decrypted strings

### Fleet Orchestrator
- **Round-Robin by Priority**: `sort(key=(priority, total_requests))`
- **Domain Filtering**: `get_next_account(provider, domain="code")`
- **Usage Tracking**: Success/failure, latency, quota remaining
- **Background Rotation Loop**: Hourly check for expired cookies (Web) or 30-day API keys (CLI)

### Passive Watcher
- **Linux**: `inotify` on `.env`, `.env.local`, `config/providers.yaml`
- **Fallback**: 60-second polling
- **Action**: Detect drift → auto-sync to vault

### MCP Server (`mcp_servers/omega_vault/`)
| Tool | Purpose |
|------|---------|
| `credential_read` | Get credential for provider/account |
| `credential_write` | Store new credential |
| `credential_rotate` | Rotate credential (rate limit hit) |
| `credential_audit` | Check status, expiry, usage |
| `fleet_status` | 16-account overview |
| `fleet_next_account` | Round-robin selection |

### CLI (`omega vault`)
```bash
omega vault init              # First-time setup
omega vault import            # Migrate from .env
omega vault list              # All providers/accounts
omega vault get xai           # Get credential
omega vault set xai "key"     # Store credential
omega vault rotate xai        # Rotate on rate limit
omega vault audit xai         # Check health
omega vault status            # Vault health
omega vault fleet list        # 16-account view
omega vault fleet status      # Fleet health
omega vault fleet next xai    # Round-robin pick
```

## 5. Security Framework

| Layer | Implementation |
|-------|----------------|
| **Encryption at Rest** | AES-256-GCM (existing) |
| **Key Management** | OS keyring (libsecret/Keychain) |
| **File Permissions** | `0o600` vault, `0o600` config, `0o644` logs |
| **Zero Data Retention** | Decrypted data cleared after use |
| **Memory Hygiene** | `ctypes.memset` best-effort clear |

## 6. Testing & Chaos Engineering

```python
# Concurrent access
async def test_vault_concurrent_access():
    await asyncio.gather(*[write_credential(i) for i in range(10)])
    assert all(resolve(f"provider_{i}") == f"key_{i}" for i in range(10))

# Corruption recovery
async def test_vault_corruption_recovery():
    vault.save()
    vault_path.write_bytes(b"corrupted")
    with pytest.raises(VaultCorruptedError):
        KeyVault().load()

# Fleet rotation under load
async def test_fleet_rotation_under_load():
    await asyncio.gather(
        *[use_account() for _ in range(20)],
        orchestrator._rotation_loop()
    )
```

## 7. Implementation Phases (7 Days)

| Phase | Duration | Scope |
|-------|----------|-------|
| **1: VaultCore** | Days 1-2 | Extend KeyVault, schemas, XDG, unit tests |
| **2: Fleet Orchestrator** | Days 3-4 | Orchestrator, 16-account YAML, round-robin, usage tracking |
| **3: MCP Server** | Day 5 | 6 tools, Omega Hub integration |
| **4: CLI + Watcher** | Day 6 | `omega vault` commands, passive watcher, `.env` import |
| **5: Testing + Chaos** | Day 7 | Chaos suite, Temple-Grade CI, docs |

## 8. Blocking Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| Existing `src/omega/vault/` | ✅ Exists | Foundation |
| Pydantic v2 | ✅ Available | Schema validation |
| OS keyring | ✅ Available | Encryption keys |
| MCP server framework | ✅ Available | Tool exposure |
| **Browser automation** | 🟡 Not yet | Cookie rotation for Web Grok |
| **ACP protocol** | 🟡 Not yet | Fleet integration with Grok CLI |

## 9. Success Criteria (V-1 MVP)

| Criterion | Target |
|-----------|--------|
| Credential storage | 16/16 accounts |
| Encryption | AES-256-GCM at rest ✅ |
| Fleet rotation | Round-robin working |
| Cookie expiry | Detection + notification |
| MCP integration | 6 tools exposed |
| XDG compliance | Zero hardcoded paths |
| Temple-Grade CI | Chaos tests pass ✅ |
| **ACP smoke test** | Grok CLI reads from vault |

## 10. Grokster's Insights & Recommendations

- **Extend, Don't Rebuild**: The existing `src/omega/vault/` has AES-256-GCM + keyring. Extend it with fleet methods rather than rewriting.
- **Cookie Rotation is the Hard Part**: Web Grok cookies expire in 24-48h. Browser automation (Playwright) is needed for true rotation. For MVP: detect expiry → notify → manual refresh.
- **The Vault Unblocks Everything**: V-1 is the prerequisite for Grok CLI fleet, which unblocks MaKaLi Council cloud voices (C-5), which unblocks local-first sovereignty (M7).
- **ACP Smoke Test is the Gate**: Don't claim V-1 done until a Grok CLI headless instance successfully reads an API key from the vault via MCP and makes a request.
- **Passive Watcher = Drift Detection**: The `.env` → vault sync prevents the "config drift" that caused the exposed secrets incident (C-8/C-9).

---

*⬡ OMEGA ⬡ GROKSTER ⬡ VAULT ⬡ V-1-MVP ⬡ 2026-07-22*
*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB v2.1.3 ⬡ 2026-08-26*
