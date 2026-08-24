# 🔱 VaultCore — Credential Management & Encryption (R_CG04)
**AP Token**: `AP-API-VAULT-CORE-v2.0.0`
⬡ OMEGA ⬡ P3 ⬡ vault ⬡ API-REFERENCE
**Package**: `omega.vault`

---

## Overview

The `omega.vault` package implements the **VaultCore credential management system** (R_CG04). It provides:

1. **Credential Models** — `VaultCredential`, `VaultLease`, audit entries, CPE scoring for PII
2. **Encryption** — Argon2id KDF + age (pyrage.passphrase) with multi-version key support
3. **VaultCore** — CRUD operations, lease management (grant/release/heartbeat/cleanup), daily quota reset, privacy-tier filtering, BlindVault resolver, Bury fallback
4. **BlindVault Resolver** — `{{secret:NAME}}` reference injection at last moment

---

## Models (`omega.vault.models`)

### Enums

| Enum | Values | Purpose |
|------|--------|---------|
| `CredentialType` | `OAUTH`, `API_KEY`, `GCP_SA`, `GROK_AUTH`, `PASSWORD`, `SSH_KEY`, `CUSTOM` | Type of stored credential |
| `CredentialTier` | `FREE`, `PAID`, `PREMIUM`, `CUSTOM` | Service tier |
| `CredentialStatus` | `ACTIVE`, `EXHAUSTED`, `COOLING`, `ROTATING`, `REVOKED`, `EXPIRED` | Lifecycle state |
| `VisibilityTier` | `PUBLIC`, `BONDED`, `PRIVATE` | R19 privacy tier |
| `ProviderName` | `ANTIGRAVITY`, `GROK`, `GOOGLE`, `OPENROUTER`, `EXA`, `FIRECRAWL`, `GITHUB`, `CEREBRAS`, `GROQ`, `SAMBA_NOVA`, `SILICON_FLOW`, `NVIDIA_NIM`, `OPENCODE`, `ANTHROPIC`, `XAI`, `CUSTOM` | Supported providers |

### DataClasses

#### `VaultCredential`
```python
@dataclass
class VaultCredential:
    id: str
    provider: ProviderName
    cred_type: CredentialType
    tier: CredentialTier
    visibility: VisibilityTier
    encrypted_blob: str                    # age-armored ciphertext
    expires_at: Optional[str] = None
    rotated_at: Optional[str] = None
    tags: List[str] = field(default_factory=list)
```

#### `VaultLease`
```python
@dataclass
class VaultLease:
    id: str
    credential_id: str
    agent_name: str
    pid: int                               # Bound to process tree
    granted_at: str
    expires_at: str
    last_heartbeat: str
    purpose: str
```

#### `VaultLeaseRequest`
```python
@dataclass
class VaultLeaseRequest:
    credential_id: str
    agent_name: str
    purpose: str
    ttl_seconds: int = 300                 # Default 5 min
```

#### `VaultAuditEntry`
```python
@dataclass
class VaultAuditEntry:
    action: str                            # grant, release, renew, rotate, access, block
    credential_id: str
    agent_name: str
    timestamp: str
    details: Optional[dict] = None
```

---

## Crypto (`omega.vault.crypto`)

### Exports

| Export | Type | Purpose |
|--------|------|---------|
| `VaultCrypto` | class | Per-key encryption with `pyrage.passphrase` |
| `VaultCryptoManager` | class | Multi-version key management & rotation |
| `VaultCryptoError` | exception | Base crypto exception |
| `create_vault_crypto()` | factory | Create `VaultCrypto` with master key |
| `create_vault_crypto_manager()` | factory | Create `VaultCryptoManager` |

### Architecture

```
Master Password (str)
  │
  ▼
pyrage.passphrase.encrypt(plaintext, passphrase)
  │
  ▼
age-armored ciphertext (includes scrypt salt in header)
```

**Key properties:**
- Uses `pyrage.passphrase` (scrypt-based, NOT X25519)
- Age handles scrypt salt internally — no manual salt management
- Work factor: default 18 (~256 MiB memory)
- Armored output for file storage

### VaultCryptoManager

Supports **multi-version key rotation**:
```python
manager = create_vault_crypto_manager()
manager.add_key("v1", "old_master_key", default=False)
manager.add_key("v2", "new_master_key", default=True)

# Encrypts with default (v2)
encrypted = manager.encrypt("sensitive data")

# Decrypts trying v2 first, then v1 (backward compat)
plaintext = manager.decrypt(encrypted)
```

---

## VaultCore (`omega.vault.vault_core`)

### Exports

| Export | Type | Purpose |
|--------|------|---------|
| `VaultCore` | class | Central credential store with CRUD, lease, quota |
| `VaultError` | exception | Base vault exception |
| `CredentialNotFoundError` | exception | Credential not found |
| `LeaseError` | exception | Lease operation failed |
| `QuotaExceededError` | exception | Daily quota exceeded |
| `create_vault_core()` | factory | Create `VaultCore` |

### VaultCore

```python
class VaultCore(
    crypto_manager: VaultCryptoManager,
    store_path: Optional[Path] = None,
    audit_path: Optional[Path] = None,
    lease_store: Optional[Any] = None,
    blindvault: Optional["BlindVaultResolver"] = None,
)
```

#### CRUD Operations

| Method | Description |
|--------|-------------|
| `store(credential, overwrite=False)` | Store encrypted credential |
| `retrieve(credential_id)` | Retrieve and decrypt credential |
| `delete(credential_id)` | Delete credential |
| `list_credentials(provider=None, tier=None)` | List credentials by filter |
| `search(query)` | Search credentials by tags/provider |
| `rotate(credential_id, new_blob)` | Re-encrypt with new key version |

#### Lease Operations

| Method | Description |
|--------|-------------|
| `grant_lease(request)` | Grant a lease (returns `VaultLease`) |
| `release_lease(lease_id)` | Release a lease early |
| `heartbeat_lease(lease_id)` | Extend lease TTL (30s grace) |
| `get_lease(lease_id)` | Get lease details |
| `cleanup_expired_leases()` | Reap expired leases (PID-bound + TTL) |
| `list_active_leases()` | List all active leases |

#### Quota Operations

| Method | Description |
|--------|-------------|
| `get_daily_quota(credential_id)` | Get remaining daily quota |
| `reset_daily_quotas()` | Reset all daily quotas |
| `check_quota_and_lease(request)` | Check quota before granting lease |

#### Admin Operations

| Method | Description |
|--------|-------------|
| `get_audit_log(limit=100)` | Get recent audit log entries |
| `get_stats()` | Get vault statistics |
| `export_backup()` | Export encrypted backup |
| `import_backup(data)` | Import encrypted backup |
| `verify_integrity()` | Verify all credentials decryptable |

#### Privacy Operations

| Method | Description |
|--------|-------------|
| `list_by_visibility(tier)` | List credentials by visibility tier |
| `get_cpe_score(credential_id)` | Get CPE score for credential |
| `pseudonymize_audit_log()` | Pseudonymize audit entries |

---

## BlindVault Resolver (`omega.vault.blindvault_resolver`)

### Exports

| Export | Type | Purpose |
|--------|------|---------|
| `BlindVaultResolver` | class | `{{secret:NAME}}` reference injection |

### BlindVaultResolver

```python
class BlindVaultResolver(vault: VaultCore, allowlist: Optional[dict] = None)
```

#### Key Methods

| Method | Description |
|--------|-------------|
| `resolve(text)` | Replace `{{secret:NAME}}` with actual credentials |
| `resolve_in_command(template, host, cmd)` | Resolve in command context with host/command allowlist |
| `get_access_log()` | Get resolver access log |
| `rotate_all()` | Rotate all managed secrets |

#### Reference Format

```
{{secret:PROVIDER_NAME_CREDENTIAL_ID}}
{{secret:ANTIGRAVITY_ACCOUNT_1}}
{{secret:GROK_ACCOUNT_3}}
```

Allows:
- **Host allowlist**: Only resolve for authorized hosts
- **Command allowlist**: Only resolve for authorized commands
- **Session management**: Track which processes accessed which secrets

#### Bury Fallback

When BlindVault is unavailable, falls back to **PID-bound session vault**:
- Credentials die with the process (PID + start time detection)
- Real-time `access.log` JSONL audit trail
- Zero persistence between process restarts

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pyrage` | >=1.3.0 | age encryption (passphrase.scrypt) |
| `argon2-cffi` | >=23.1.0 | Argon2id key derivation |
| `cryptography` | >=41.0.0 | X25519, ChaCha20-Poly1305 |

Install:
```bash
source .venv/bin/activate
pip install pyrage argon2-cffi cryptography
```

---

## Usage Examples

### Basic CRUD
```python
from omega.vault import create_vault_core, create_vault_crypto_manager
from omega.vault.models import VaultCredential, ProviderName, CredentialType, CredentialTier

crypto = create_vault_crypto_manager()
crypto.add_key("v1", "my-master-password", default=True)

vault = create_vault_core(crypto)

# Store
cred = VaultCredential(
    id="groq-api-key-1",
    provider=ProviderName.GROQ,
    cred_type=CredentialType.API_KEY,
    tier=CredentialTier.FREE,
    visibility="private",
    encrypted_blob=crypto.encrypt("gsk_my_groq_key")
)
vault.store(cred)

# Retrieve (with lease)
lease = vault.grant_lease(credential_id="groq-api-key-1", agent_name="maat", purpose="inference")
retrieved = vault.retrieve("groq-api-key-1")  # Auto-decrypts
```

### Lease Protocol
```python
# Grant
request = VaultLeaseRequest(credential_id="groq-api-key-1", agent_name="maat", purpose="inference", ttl_seconds=300)
lease1 = vault.grant_lease(request)

# Heartbeat (extend TTL)
vault.heartbeat_lease(lease1.id)

# Release
vault.release_lease(lease1.id)

# Auto-cleanup (cron: every 5 min)
vault.cleanup_expired_leases()
```

### BlindVault Reference
```python
from omega.vault.blindvault_resolver import BlindVaultResolver

resolver = BlindVaultResolver(vault)

# In text config
config = "openrouter_api_key: {{secret:OPENROUTER_API_KEY_1}}"
resolved = resolver.resolve(config)
# → "openrouter_api_key: sk-or-..."

# In command execution (with allowlist)
result = resolver.resolve_in_command(
    template="grok -p 'analyze'",
    host="localhost",
    cmd="grok"
)
```

---

## Cross-Reference

| System | Relation |
|--------|----------|
| `omega.config.loader` | VaultCore stores provider credentials loaded by ConfigLoader |
| `omega.privacy.cpe_scorer` | VaultAuditEntry uses CPE scoring for PII exposure |
| `omega.soul.loader` | SoulLoader accesses VaultCore for encrypted soul data |
| `docs/research/R_CG04_AGENT_SAFE_CREDENTIAL_VAULT.md` | Full R_CG04 spec |
| `docs/research/R_VAULT_SCHEMA_V2.md` | Schema v2 design |
| `docs/research/R_VAULTCORE_LEASE_PROTOCOL.md` | Lease protocol spec |
| `SOVEREIGN_MANDATES.md` M15 | Persistent state management |
| `SOVEREIGN_MANDATES.md` M22 | Response provenance (encryption audit) |

---

*⬡ OMEGA ⬡ P3 ⬡ vault ⬡ v2.0.0*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: vault | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
