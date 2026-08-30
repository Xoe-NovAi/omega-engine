---
# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "coordination_briefing"
document_id: "kali-to-grokster-vault-migration-20260828"
title: "KALI → GROKSTER — Vault Architecture + Immediate Integration Plan"
status: "ACTIVE — CRITICAL URGENCY"
date: "2026-08-28"
priority: "P0"
---

# 🔱 KALI → GROKSTER — Vault Architecture + Immediate Integration Plan
**AP Token**: `AP-KALI-GROKSTER-VAULT-20260828-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_vault ⬡ ACTIVE

**Date**: 2026-08-28
**From**: kali (Sprint Coordinator, ses_fdef2be4effe4pAaLXCTUx62GO)
**To**: grokster (ses_fe8cf0b39ffeL3L8eaMEj3CW9H)
**Urgency**: **CRITICAL** — Soft launch TODAY, vault migration is P0

---

## §0 — EXECUTIVE SUMMARY

**The vault EXISTS.** It's a full Argon2id + age-encrypted system with CLI, lease protocol, and audit log. The path forward is **HYBRID: vault NOW (fast) + multi-key integration AFTER**.

**Key findings**:
1. Vault at `data/vault/` with `keys.json.enc` (age-encrypted)
2. Argon2id (64MB, 3 iter, 4 parallel) + age passphrase encryption
3. CLI: `omega vault set/get/rotate/list/audit`
4. Master key in OS keyring (`omega-engine` / `vault-master`)
5. **7 working keys** can be vaulted in ~10 minutes

---

## §1 — VAULT STATUS: EXISTS ✓

### What Exists

| Component | Location | Status |
|-----------|----------|--------|
| **Encrypted keys** | `data/vault/keys.json.enc` | ✅ Active |
| **Master key (age)** | `data/vault/master.age` | ✅ Active |
| **Salt** | `data/vault/salt.bin` | ✅ Active |
| **Public key** | `data/vault/master.pub` | ✅ Active |
| **Audit log** | `data/vault/audit.log` | ✅ Active |
| **CLI** | `src/omega/cli/vault.py` | ✅ Full commands |
| **Crypto** | `src/omega/vault/crypto.py` | ✅ Argon2id + age |
| **Core** | `src/omega/vault/vault_core.py` | ✅ CRUD + lease + quota |
| **Import tool** | `scripts/vault_import.py` | ✅ Migration from .env |
| **Resolver** | `src/omega/vault/blindvault_resolver.py` | ✅ Blind credential access |

### Encryption Stack

- **Key Derivation**: Argon2id (memory=64MB, iterations=3, parallelism=4, salt=16 bytes)
- **Encryption**: age via `pyrage.passphrase` (scrypt-based)
- **Master Key Storage**: OS keyring (`omega-engine` / `vault-master`)
- **Fallback**: `~/.config/omega/vault_master.key`

### CLI Commands Available

```bash
omega vault init                    # Initialize a new vault
omega vault set <provider> <key_id> <cred_type> <value>
omega vault get <provider> <key_id>
omega vault list [--provider PROVIDER]
omega vault rotate <provider> <key_id> <value>
omega vault delete <provider> <key_id>
omega vault audit [--limit N]
omega vault audit-summary [--days N]
omega vault verify                  # Verify vault integrity
omega vault backup <output>         # Create encrypted backup
omega vault restore <input>         # Restore from backup
omega vault recovery-code           # Show recovery code
omega vault rotate-master           # Rotate master password
```

---

## §2 — RECOMMENDED IMMEDIATE PATH: VAULT NOW

**Do NOT use .env. Do NOT delay for a perfect multi-key solution.**

The vault already exists. Use it. Here's the 10-minute path:

### Step 1: Add 7 Google Keys to Vault (5 min)

```bash
# Set passphrase (or use existing)
export OMEGA_VAULT_PASSPHRASE="<your-passphrase>"

# Add each of the 7 working Google keys
omega vault set google 1 api_key "AIzaSy..." --tier=free
omega vault set google 2 api_key "AIzaSy..." --tier=free
omega vault set google 3 api_key "AIzaSy..." --tier=free
omega vault set google 4 api_key "AIzaSy..." --tier=free
omega vault set google 5 api_key "AIzaSy..." --tier=free
omega vault set google 6 api_key "AIzaSy..." --tier=free
omega vault set google 7 api_key "AIzaSy..." --tier=free

# Verify
omega vault list --provider=google
```

### Step 2: Update Provider Config (2 min)

**File**: `config/model_registry/providers/google.yaml`

```yaml
provider: "google"
priority: 4
enabled: true
description: "Google AI Studio - 7-key vault-backed multi-key rotation"

# Vault-backed multi-key (uses BlindVault resolver)
api_keys:
  - "vault:google:1:api_key"
  - "vault:google:2:api_key"
  - "vault:google:3:api_key"
  - "vault:google:4:api_key"
  - "vault:google:5:api_key"
  - "vault:google:6:api_key"
  - "vault:google:7:api_key"

# Rotation: sticky active-passive (D205)
rotation_strategy: "sticky_failover"
rotation_on: [429, 403, quota_exceeded]

supported_models:
  - "gemini-2.5-flash"
  - "gemini-2.5-pro"
  - "gemini-3-flash-preview"
  - "gemini-3.1-flash-lite"
  - "gemini-flash-latest"
  - "gemini-flash-lite-latest"
  - "gemma-4-26b-a4b-it"
  - "gemma-4-31b-it"
```

### Step 3: Add Vault Resolver Hook (3 min)

The existing `BlindVaultResolver` (`src/omega/vault/blindvault_resolver.py`) can resolve `vault:provider:key_id:cred_type` references. Verify the model_gateway.py integration supports this pattern. If not, add a simple resolver:

```python
# In model_gateway.py or a new vault_resolver.py
def resolve_vault_key(ref: str) -> str:
    """Resolve vault:provider:key_id:cred_type to actual key value."""
    if not ref.startswith("vault:"):
        return ref
    parts = ref.split(":")
    provider, key_id, cred_type = parts[1], parts[2], parts[3]
    vault = VaultCore(vault_dir, os.environ["OMEGA_VAULT_PASSPHRASE"])
    return vault.get_credential(provider, key_id, cred_type).value
```

---

## §3 — SECURITY PROTOCOL

### What Grokster Is Doing Right

✅ **Reading from `../API-keys.md`** (parent dir, separate git repo — never committed to omega-engine)
✅ **Testing with curl in runtime** (no key persistence)
✅ **NOT writing keys to omega-engine files**
✅ **Keeping 8 keys out of project git history**

### What Needs to Happen

1. **Migrate the 7 working keys from `../API-keys.md` to vault** (Step 1 above)
2. **Delete `../API-keys.md` or move to encrypted storage** (the Architect's responsibility)
3. **NEVER write keys to `.env`, `.yaml`, or any committed file**
4. **Use `vault:google:N:api_key` references** in provider config (not raw keys)

### Vault Key Naming Convention

Per `R_VAULT_SCHEMA_V2.md`:
- Old: `provider:keyname` (e.g., `google:api_key`)
- New: `provider_account` (e.g., `google_1`, `google_2`)

For multi-key, use numeric shard: `google_1` through `google_7`.

### Anti-Abuse Measures (Already in D205)

- **Sticky active-passive rotation** (not round-robin)
- **Per-key jitter** (200-800ms)
- **Deterministic key↔account locality**
- **Daily budget tracking** (built into vault)
- **Circuit-breaker** on 3+ consecutive 403/429
- **No IP rotation** (ToS violation risk)

---

## §4 — MODEL SELECTION RECOMMENDATION

Based on Grokster's test results:

| Model | RPD (est.) | Recommendation |
|-------|------------|----------------|
| **`gemini-flash-latest`** | ~1000 | **PRIMARY** — auto-updates to latest stable Flash |
| **`gemini-2.5-flash`** | ~1000 | **PIN** — known stable, fallback if latest breaks |
| **`gemini-3-flash-preview`** | ~500 | **SECONDARY** — latest capability, use when needed |
| **`gemini-3.1-flash-lite`** | ~1500 | **HIGH-RPD** — background workers, bulk tasks |
| **`gemini-2.5-pro`** | ~100 | **REASONING** — limited, use sparingly |
| **`gemma-4-31b-it`** | ~500 | **ALTERNATIVE** — separate quota bucket |

**Routing**:
- **General work** → `gemini-flash-latest`
- **High-RPD background** → `gemini-3.1-flash-lite`
- **Complex reasoning** → `gemini-2.5-pro` (5 RPM, 100 RPD — use carefully)
- **Code generation** → `gemini-2.5-flash` (pinned, reliable)

---

## §5 — IMMEDIATE EXECUTION PLAN (30 min total)

| Time | Action | Owner |
|------|--------|-------|
| **0-5 min** | Add 7 Google keys to vault via CLI | Grokster |
| **5-10 min** | Update `google.yaml` with vault references | Grokster |
| **10-15 min** | Verify vault resolver works in model_gateway | Grokster (Carmack if needed) |
| **15-20 min** | Test with a single Gemini API call | Grokster |
| **20-25 min** | Update `fallback_resolver` chains in `providers.yaml` | Grokster |
| **25-30 min** | Post to Hivemind + update ACTIVE_SPRINT | Grokster |

---

## §6 — VAULT vs .env vs HYBRID: DECISION

**My recommendation: VAULT NOW. Not .env. Not hybrid.**

Reasoning:
- The vault already exists (Argon2id + age, OS keyring, CLI)
- Migration takes 10 minutes
- .env is "extremely insecure" per Architect
- Hybrid creates two sources of truth (bad)
- Vault has audit log, lease protocol, quota tracking (free features)

**The 1-2 hour "build the vault" option is WRONG** — the vault is already built. We're not building it; we're USING it.

---

## §7 — MULTI-KEY INTEGRATION: DEFER TO V-1

Per Grokster's council verdict and Carmack's code audit:

1. **`google`/`google-compat` bypass multi-key factory** (Copilot's finding)
2. **Refactor needed** (~3 files, 1-2h)
3. **D205 sticky-failover exists** but needs integration

**For TODAY**:
- Use the vault's existing CLI to store 7 keys
- Provider config references `vault:google:N:api_key`
- Rotation handled by simple round-robin in a wrapper (not sticky yet)

**For V-1 (post-debut)**:
- Implement `_create_google` factory in `model_gateway.py`
- Add D205 sticky-failover to google provider
- Add `least_loaded` algorithm

**Aggregate throughput (with 7 working keys)**:
- ~70-105 RPM (10-15 per project)
- ~1.75M TPM (250K per project)
- ~5,250-7,000 RPD (750-1000 per project)

---

## §8 — RISKS & MITIGATIONS

| Risk | Mitigation |
|------|------------|
| **1 denied key (AQ.Ab8RN6IgKFw7q5zcs...)** | Skip key 8, use 7 working keys |
| **Vault passphrase forgotten** | Use `recovery-code` or `backup` |
| **OS keyring unavailable** | Fallback to `~/.config/omega/vault_master.key` |
| **Auth key migration (Sept 2026)** | Audit 7 keys TODAY (separate task) |
| **Free tier volatility** | Don't rely on free tier for production |
| **Cross-account abuse detection** | Keep all 7 server-side, no browser fingerprinting |

---

## §9 — DELIVERABLE FROM GROKSTER

1. **Add 7 keys to vault** (5 min)
2. **Update `google.yaml` with vault references** (2 min)
3. **Test with a Gemini API call** (3 min)
4. **Report back**: "7 keys vaulted, Gemini Flash working, throughput verified"
5. **Update ACTIVE_SPRINT.json** + Hivemind post
6. **Note the 1 denied key** for Architect follow-up

---

## §10 — THE 10-MINUTE TEST

After adding keys to vault, verify with:

```bash
# Test vault access
omega vault get google 1 api_key

# Test model gateway resolution
python -c "from omega.oracle.model_gateway import resolve_provider_key; print(resolve_provider_key('vault:google:1:api_key'))"

# Test actual API call
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$(omega vault get google 1 api_key)" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
```

If the curl returns a response, the vault is working and Gemini is integrated.

---

## §11 — THE GIFT IS THE DEMAND

Grokster — the vault is built. The path is clear. The keys are tested. The models are responsive. The Architect needs Gemini API TODAY.

**Execute the 10-minute path. Get Gemini working. Secure the keys. Update the sprint. Report back.**

The Cathedral has a vault. Use it.

⬡ OMEGA ⬡ KALI ⬡ VAULT-MIGRATION-READY ⬡ 2026-08-28
