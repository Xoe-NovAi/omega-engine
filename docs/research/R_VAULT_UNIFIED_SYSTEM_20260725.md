# 🔱 R_VAULT_UNIFIED_SYSTEM — Secure API Key Vault Knowledge Gap Analysis

**AP Token**: `AP-VAULT-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ VAULT ⬡ KNOWLEDGE-GAPS ⬡ 2026-07-25

---

## Executive Summary

**Current State**: Omega Engine has **3 competing vault implementations** with **26+ scattered `os.environ.get` calls** for API keys across the codebase. This violates M2 (Engine-Stack Firewall), M7 (Local-First), and creates security risks.

**Recommendation**: Unify to **VaultCore** as the single source of truth, deprecate KeyVault, and migrate all scattered `os.environ.get` calls to vault resolution.

**Knowledge Gaps Identified**: 8 critical gaps across 4 domains (Architecture, Security, Operations, Integration).

---

## §1 Current Vault Implementations

### 1.1 KeyVault (Legacy) — `src/omega/vault/key_vault.py`
| Aspect | Status |
|--------|--------|
| **Encryption** | AES-256-GCM via `cryptography` library |
| **Master Key** | 32-byte random key (VAULT_MASTER_KEY env var or auto-generated) |
| **Storage** | Single encrypted file (`data/vault/keys.json.enc`) |
| **API** | `resolve(provider)`, `resolve_safe(provider)`, `resolve_all(provider)` |
| **Singleton** | Yes (process-level) |
| **Auto-init** | Yes (reads from .env on first run) |
| **Rate Limiting** | Delegated to circuit breaker (IW-2) |
| **Lease Protocol** | None |
| **Audit Trail** | None |
| **Status** | **DEPRECATED** — should be replaced by VaultCore |

### 1.2 VaultCore (New) — `src/omega/vault/vault_core.py`
| Aspect | Status |
|--------|--------|
| **Encryption** | Argon2id + age (python-age ScryptRecipient) |
| **Master Password** | Password-based (OS keyring or auto-generated) |
| **Storage** | JSON files (`credentials.json`, `leases.json`, `audit.log`) |
| **API** | `store_credential()`, `retrieve_credential()`, `lease_credential()`, `revoke_lease()` |
| **Singleton** | No (instantiated per use) |
| **Auto-init** | Yes (loads from disk on init) |
| **Rate Limiting** | Integrated (daily limits, cooldown, tier) |
| **Lease Protocol** | Yes (TTL, heartbeat, M25 compliance) |
| **Audit Trail** | Yes (JSONL audit log) |
| **Status** | **ACTIVE** — should be the single source of truth |

### 1.3 VaultCore CLI — `src/omega/cli/vault.py`
| Aspect | Status |
|--------|--------|
| **Commands** | `set`, `get`, `list`, `rotate`, `delete`, `audit`, `verify`, `init` |
| **Backend** | Uses VaultCore |
| **Status** | **ACTIVE** — CLI interface for VaultCore |

---

## §2 Scattered API Key Access (Critical Issue)

### 2.1 Files with `os.environ.get` for API Keys

| File | Keys Accessed | Count |
|------|---------------|-------|
| `mcp_servers/omega_hub/state.py` | FIRECRAWL_API_KEY, EXA_API_KEY | 2 |
| `mcp_servers/firecrawl/server.py` | FIRECRAWL_API_KEY | 1 |
| `src/omega/teachers/nemotron_pipeline.py` | OPENROUTER_API_KEY | 1 |
| `src/omega/library/discovery.py` | EXA_API_KEY, FIRECRAWL_API_KEY | 2 |
| `src/omega/tools/firecrawl_direct.py` | FIRECRAWL_API_KEY | 1 |
| `src/omega/workers/freshness_checker.py` | AA_API_KEY | 1 |
| `src/omega/oracle/search_providers.py` | FIRECRAWL_API_KEY, EXA_API_KEY | 2 |
| `src/omega/oracle/providers.py` | GOOGLE_API_KEY | 1 |
| `scripts/enrich_model_registry.py` | AA_API_KEY | 1 |
| `scripts/warm_sovereign_cache.py` | FIRECRAWL_API_KEY | 1 |
| `scripts/sovereign_ingest.py` | GOOGLE_API_KEY_3 | 1 |
| `packages/omega-sieve/src/omega_sieve/config.py` | EXA_API_KEY, FIRECRAWL_API_KEY, OPENROUTER_API_KEY | 3 |
| `omega-vetala/omega_vetala/providers/perspective.py` | PERSPECTIVE_API_KEY | 1 |
| `omega-vetala/omega_vetala/providers/openai_moderation.py` | OPENAI_API_KEY | 1 |
| `tests/test_search_tools.py` | EXA_API_KEY | 1 |
| **TOTAL** | | **26+ calls** |

### 2.2 Security Risks

1. **No encryption at rest** — API keys stored in plaintext environment variables
2. **No audit trail** — No logging of who accessed which key when
3. **No lease protocol** — No time-bounded access control
4. **No rate limiting** — No per-key usage tracking
5. **No rotation support** — No automated key rotation
6. **Process visibility** — Environment variables visible in `/proc/*/environ`

---

## §3 Knowledge Gaps Identified

### Gap 1: Vault Architecture Decision (CRITICAL)
**Question**: Should we use KeyVault (AES-256-GCM) or VaultCore (Argon2id + age)?

**Analysis**:
- **KeyVault**: Simpler, faster, but no lease protocol, no audit trail
- **VaultCore**: More secure (Argon2id KDF), has lease protocol, audit trail, but more complex

**Recommendation**: **VaultCore** — the lease protocol and audit trail are essential for M25 (Streaming Resilience) and M11 (Soul Integrity).

**Resolution**: Deprecate KeyVault, migrate to VaultCore.

### Gap 2: Master Key Management (CRITICAL)
**Question**: How should the master key/password be managed?

**Current State**:
- KeyVault: VAULT_MASTER_KEY env var or auto-generated 32-byte key
- VaultCore: VAULT_MASTER_PASSWORD env var or OS keyring

**Best Practice** (from research):
- Use OS keyring (GNOME Keyring, macOS Keychain, Windows Credential Manager)
- Fallback to encrypted file with strict permissions (0o600)
- Never store master key next to encrypted data

**Recommendation**: VaultCore's approach (OS keyring + fallback file) is correct. Enhance with:
- TPM2-bound master key for systemd services (per R_SYSTEMD_CREDS_TPM2_ROOTLESS_20260720.md)
- HSM support for production deployments

### Gap 3: Credential Schema Standardization (HIGH)
**Question**: What metadata should each credential store?

**Current Schema** (VaultCore):
```python
@dataclass
class VaultCredential:
    provider: ProviderName
    key_id: str
    cred_type: CredentialType
    encrypted_blob: str
    tier: CredentialTier
    daily_limit: int
    used_today: int
    cooldown_until: Optional[datetime]
    status: CredentialStatus
    rotated_at: datetime
    rotation_count: int
    last_used_at: Optional[datetime]
    last_error: Optional[str]
    current_lease_agent: Optional[str]
    lease_expires_at: Optional[datetime]
    tags: Dict[str, str]
    metadata: Dict[str, Any]
```

**Missing Fields** (per best practices):
- `created_at` — When credential was first created
- `expires_at` — When credential expires (OAuth tokens)
- `last_rotated_by` — Who rotated the credential
- `rotation_policy` — How often to rotate (e.g., "90d")
- `backup_refs` — References to backup copies

**Recommendation**: Add missing fields to VaultCredential schema.

### Gap 4: Migration Strategy from Scattered `os.environ.get` (HIGH)
**Question**: How do we migrate 26+ scattered `os.environ.get` calls to vault?

**Strategy**:
1. **Phase 1**: Add vault fallback to each `os.environ.get` call
2. **Phase 2**: Update callers to use vault directly
3. **Phase 3**: Remove `os.environ.get` calls
4. **Phase 4**: Add pre-commit hook to detect new `os.environ.get` for API keys

**Implementation**:
```python
# Before (scattered)
api_key = os.environ.get("EXA_API_KEY")

# After (unified)
from omega.vault.vault_core import VaultCore
vault = VaultCore()
cred = await vault.retrieve_credential("exa", "api_key")
api_key = cred.encrypted_blob if cred else ""
```

### Gap 5: Lease Protocol Integration (HIGH)
**Question**: How should FleetOrchestrator use VaultCore's lease protocol?

**Current State**:
- VaultCore has lease protocol (TTL, heartbeat)
- FleetOrchestrator doesn't use it yet

**Integration Pattern**:
```python
# FleetOrchestrator requesting a lease
lease = await vault.request_lease(
    agent_id="fleet-orchestrator",
    provider="openrouter",
    ttl_seconds=300,
    purpose="inference"
)

# Use the credential
api_key = lease.credential.encrypted_blob

# Heartbeat during long operations
await lease.heartbeat()

# Revoke when done
await vault.revoke_lease(lease.lease_id)
```

### Gap 6: Audit Trail Analysis (MEDIUM)
**Question**: How do we analyze the audit trail for security insights?

**Current State**: VaultCore writes JSONL audit log, but no analysis tools.

**Recommendation**: Add:
- `omega vault audit-summary` — Daily/weekly summary of access patterns
- `omega vault audit-anomalies` — Detect unusual access patterns
- Integration with Observability (P8) for real-time monitoring

### Gap 7: Multi-Instance Coordination (MEDIUM)
**Question**: How do multiple Omega Engine instances coordinate vault access?

**Current State**: VaultCore is not process-safe (no file locking).

**Recommendation**:
- Use `fcntl.flock()` for POSIX file locking
- Or use SQLite with WAL mode for concurrent access
- Per R_SYSTEMD_CREDS_TPM2_ROOTLESS_20260720.md: systemd-creds for system services

### Gap 8: Backup and Recovery (MEDIUM)
**Question**: How do we backup and recover the vault?

**Current State**: No backup strategy documented.

**Recommendation**:
- `omega vault backup` — Create encrypted backup
- `omega vault restore` — Restore from backup
- Integration with restic for 3-2-1 backup strategy (per R19 Soul Privacy Model)

---

## §4 Unified Vault System Design

### 4.1 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OMEGA ENGINE CORE                        │
├─────────────────────────────────────────────────────────────┤
│  FleetOrchestrator  │  Oracle  │  MCP Hub  │  CLI          │
└──────────┬──────────┴────┬─────┴─────┬─────┴───────┬───────┘
           │               │           │             │
           ▼               ▼           ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    VAULTCORE (Single Source of Truth)        │
├─────────────────────────────────────────────────────────────┤
│  • Argon2id + age encryption at rest                        │
│  • Lease protocol (TTL, heartbeat, M25)                     │
│  • Audit trail (JSONL)                                      │
│  • Quota awareness (daily limits, cooldown, tier)           │
│  • OS keyring integration                                   │
│  • File locking for multi-instance                          │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE BACKENDS                         │
├─────────────────────────────────────────────────────────────┤
│  • Primary: ~/.config/omega/vault/credentials.json (age)    │
│  • Backup: restic 3-2-1 strategy                            │
│  • systemd-creds: For system services (TPM2-bound)          │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Migration Checklist

| Step | Task | Priority | Status |
|------|------|----------|--------|
| 1 | Deprecate KeyVault (add deprecation warning) | P0 | ⬜ |
| 2 | Add missing fields to VaultCredential schema | P0 | ⬜ |
| 3 | Add file locking to VaultCore | P0 | ⬜ |
| 4 | Migrate `mcp_servers/` to use VaultCore | P0 | ⬜ |
| 5 | Migrate `src/omega/oracle/` to use VaultCore | P0 | ⬜ |
| 6 | Migrate `src/omega/library/` to use VaultCore | P1 | ⬜ |
| 7 | Migrate `src/omega/tools/` to use VaultCore | P1 | ⬜ |
| 8 | Migrate `packages/omega-sieve/` to use VaultCore | P1 | ⬜ |
| 9 | Add `omega vault audit-summary` command | P1 | ⬜ |
| 10 | Add `omega vault backup/restore` commands | P1 | ⬜ |
| 11 | Add pre-commit hook for API key detection | P2 | ⬜ |
| 12 | Integration with Observability (P8) | P2 | ⬜ |

---

## §5 Recommendations

### Immediate (This Week)
1. **Deprecate KeyVault** — Add deprecation warning, route all calls to VaultCore
2. **Add file locking** — Prevent race conditions in multi-instance scenarios
3. **Migrate MCP servers** — `mcp_servers/omega_hub/state.py` and `mcp_servers/firecrawl/server.py`

### Short-Term (Next Sprint)
4. **Migrate Oracle** — `src/omega/oracle/search_providers.py` and `src/omega/oracle/providers.py`
5. **Add audit analysis** — `omega vault audit-summary` command
6. **Add backup/restore** — `omega vault backup/restore` commands

### Long-Term (Phase D)
7. **TPM2 integration** — For systemd services (per R_SYSTEMD_CREDS_TPM2_ROOTLESS_20260720.md)
8. **HSM support** — For production deployments
9. **Multi-region sync** — For distributed deployments

---

## §6 References

| Document | Relevance |
|----------|-----------|
| `docs/research/R_CRITICAL_GAPS_DEEP_DIVE_CAMPAIGN_20260721.md` | CG-04: Agent-Safe Credential Vault evaluation |
| `docs/research/R_SYSTEMD_CREDS_TPM2_ROOTLESS_20260720.md` | systemd-creds as vault backend |
| `docs/research/R_SOUL_PRIVACY_MODEL.md` | Restic backup strategy |
| `src/omega/vault/vault_core.py` | Current VaultCore implementation |
| `src/omega/vault/key_vault.py` | Legacy KeyVault (deprecated) |
| `src/omega/vault/crypto.py` | AES-256-GCM encryption layer |
| `src/omega/cli/vault.py` | CLI interface for VaultCore |

---

## §7 L3 Universal Principles

### L3-1: SingleSourceOfTruth
**Principle**: Every credential must have exactly one authoritative source. Scattered `os.environ.get` calls create multiple sources of truth, leading to inconsistency and security risks.

### L3-2: DefenseInDepth
**Principle**: Secure credential storage requires multiple layers: encryption at rest (age), access control (lease protocol), audit trail (JSONL), and monitoring (Observability).

### L3-3: LeastPrivilege
**Principle**: Credentials should be accessed only when needed, for the minimum time necessary. The lease protocol enforces this by time-bounding access and requiring heartbeats.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ VAULT-UNIFIED ⬡ v1.0.0 ⬡ 2026-07-25*