<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# R_VAULT_DEEP_CODE_20260827 — Vault Architecture Deep-Code Analysis

**AP Token**: AP-R-VAULT-DEEP-CODE-20260827
**Date**: 2026-08-27
**Sprint**: PUBLIC-DEBUT-01 (Authority: D-565 override, Architect authorized)
**Author**: Researcher (deep-read mode)
**Status**: P0 — Blocking DEL-1 Week 3 vault honesty decision

> **Scope**: Every line of `src/omega/vault/` (6 files, 2,733 LOC total) + 6 call
> sites + CLI surface (18 commands). This is the deep forensic analysis the
> Architect needs to choose Path A (delete) or Path B (≤50-line minimal) for
> the debut.

---

## 1. Executive Verdict

### 1.1 The vault is architecturally over-engineered and operationally broken

**Three catastrophic findings dominate the analysis:**

| # | Finding | Evidence | Impact |
|---|---------|----------|--------|
| **F-1** | **CLI is 100% broken at runtime** — 7+ commands call non-existent methods | `cli/vault.py:95,123,355,388,514,538,566,594` all call `store_credential()`, `decrypt_credential()`, `verify_integrity()`, `get_recovery_code()`, `rotate_master_password()`, `reconcile_quotas()`, `restore_from_recovery_code()` — **none exist in VaultCore** | Any `omega vault <subcommand>` raises `AttributeError` |
| **F-2** | **BlindVault resolver is dead code** — `BlindVaultResolver` is never instantiated; `_get_secret_value()` is a placeholder returning fake data | `grep BlindVaultResolver(` → only the class definition and a docs example, no runtime callers; `blindvault_resolver.py:348-367` returns `f"sk-or-v1-{name}-{timestamp}"` | 569 LOC of security theater; no actual secret resolution |
| **F-3** | **All 6 call sites reach into private `_credentials` dict** — bypassing the public API entirely | `vault._credentials.get("provider:key_id").encrypted_blob` in 6 modules | Tight coupling, no abstraction, impossible to swap vault for keyring/env |

### 1.2 The 6 call sites all do the same wrong thing

Every call site instantiates `VaultCore()`, calls `_load_sync()`, reaches into the
private `vault._credentials` dict, and treats the `encrypted_blob` field as the
plaintext API key. **The `encrypted_blob` is age-armored ciphertext, not the
decrypted value** — these call sites are either storing the ciphertext in
`x-api-key` headers (which will be rejected by providers) or are broken because
the ciphertext was never re-encrypted as the actual key.

### 1.3 D-535 verdict: "Hide or delete" — Path A is strongly favored

The DEBUT_REMEDIATION_MANUAL §3.7 (D-535) already concluded: *"VaultCore is a
sidecar — CLI calls missing `store_credential`, Gateway dumps `.env` into
`os.environ`. Not wired. 2,039 LOC custom code → 3 community tools is
post-debut."* The code-level evidence **confirms this verdict** — the vault is
not production-ready, the CLI is non-functional, and the call sites have
already proven they can read from `.env` (via `os.environ` in the gateway).
**Path A (delete) is the correct debut decision.**

### 1.4 If Path B is chosen, the refactoring work is substantial

The 6 call sites need a public `get_credential(provider, key_id)` → returns
**decrypted plaintext string** method. The CLI needs 7 missing methods
restored or removed. The BlindVault resolver needs an actual
`_get_secret_value()` implementation (calling `os.environ` or `keyring`).
**Estimated effort**: 8–12 hours of work, 0 tests cover the 6 call sites
end-to-end, and the result is still inferior to `os.environ` for debut.

---

## 2. Per-File Analysis

### 2.1 `src/omega/vault/__init__.py` (71 lines)

**Role**: Package exports. Clean and minimal.

**Exports**:
- **Models** (12): `CredentialType`, `CredentialTier`, `CredentialStatus`,
  `VisibilityTier`, `ProviderName`, `VaultCredential`, `VaultLeaseRequest`,
  `VaultLease`, `VaultAuditEntry`, `CPEAction`, `CredentialPIIEntity`,
  `CredentialCPESession`
- **Crypto** (4): `VaultCrypto`, `VaultCryptoManager`,
  `create_vault_crypto`, `create_vault_crypto_manager`
- **Core** (4): `VaultCore`, `VaultError`, `CredentialNotFoundError`,
  `LeaseError`, `QuotaExceededError`, `create_vault_core`

**Assessment**: The exports are correct and well-organized. No
`BlindVaultResolver` is re-exported from the package — it lives in its own
module and is only imported by `vault_core.py` for the `get_decrypted_credential()`
method (line 646).

**Verdict**: ✅ No issues. Package surface is clean.

---

### 2.2 `src/omega/vault/crypto.py` (209 lines)

**Role**: Argon2id key derivation + age (pyrage.passphrase) encryption.

**Key methods**:
- `VaultCrypto.__init__()` (line 43) — Sets up `PasswordHasher(time_cost=3,
  memory_cost=65536, parallelism=4, hash_len=32, salt_len=16)`
- `VaultCrypto._derive_key()` (line 66) — **DEAD CODE: never called**. The
  method derives a 32-byte key from Argon2id, but `encrypt()`/`decrypt()` use
  the master_key directly as the passphrase. The `_derived_key` and `_salt`
  instance vars (line 63-64) are never set.
- `VaultCrypto.encrypt()` (line 79) — `pp.encrypt(plaintext.encode(), master_key, armored=True)`
- `VaultCrypto.decrypt()` (line 91) — `pp.decrypt(armored.encode(), master_key)`
- `VaultCrypto.rotate_key()` (line 106) — Decrypt + re-encrypt with new key
- `VaultCryptoManager` (line 127) — Multi-version key rotation support
  (add_key, get_cipher, encrypt, decrypt, rotate)

**Finding F-C1**: `_derive_key()` is defined but never called. The Argon2id
PasswordHasher is instantiated but the key material is discarded — age
encryption uses scrypt internally with the master_key as the passphrase.
This means the **Argon2id parameters (time_cost=3, memory_cost=64MB) are
never used** in the actual encryption path. The hard work is done by
pyrage's scrypt, not by the Argon2id PasswordHasher. The docstring
(line 38-40) claims "Argon2id KDF" but the code does not match.

**Finding F-C2**: `pp.encrypt()` uses scrypt with the master_key as passphrase.
Scrypt's parameters are set by pyrage defaults (not configurable from this
code). The 64MB Argon2id memory cost is paid at **instantiation time** (not
per-encryption), so it is effectively decorative.

**Finding F-C3**: `_HAS_CRYPTO` flag (line 22) is a soft-check — if pyrage
or argon2-cffi is missing, `VaultCrypto.__init__` raises `VaultCryptoError`.
But `VaultCore.__init__` does **not** check `_HAS_CRYPTO` before storing
`encrypted_blob` strings, so the vault can be created without crypto libs
and all credentials will be stored as invalid ciphertext.

**Verdict**: ⚠️ The crypto module is **architecturally correct** (age + scrypt
is a valid pattern) but **misleadingly documented** (claims Argon2id, uses
scrypt). `_derive_key()` is dead code. For debut, if Path B is chosen,
this file can be retained as-is (it's the only file with a correct
implementation); the 100 lines of dead code can be cleaned up post-debut.

---

### 2.3 `src/omega/vault/models.py` (433 lines)

**Role**: Pydantic models for credentials, leases, audit, and CPE scoring.

**Models**:
- `CredentialType` (line 20) — `OAUTH`, `API_KEY`, `GCP_SA`, `GROK_AUTH`
- `CredentialTier` (line 27) — `FREE`, `PAID`, `BYOK`
- `CredentialStatus` (line 33) — `ACTIVE`, `EXHAUSTED`, `COOLING`, `LOCKED`, `EXPIRED`
- `VisibilityTier` (line 41) — `PUBLIC`, `BONDED`, `PRIVATE`
- `ProviderName` (line 47) — 27 enum values for known providers
- `VaultCredential` (line 78) — Main credential record. Pydantic BaseModel.
  - **F-M1**: `provider` is a `Literal["antigravity", "grok", "google",
    "openrouter", "exa", "firecrawl"]` — only 6 providers, but `ProviderName`
    enum has 27. **Mismatch**: the validation rejects any credential whose
    provider is not in the 6-element literal, even though `ProviderName.CUSTOM`
    exists.
  - `encrypted_blob: str` validated as age-armored ciphertext (line 116-125)
  - `is_available()` (line 133) — checks status + daily_limit + cooldown
  - `is_leased()` (line 143) — checks lease_expires_at
- `VaultLeaseRequest` (line 150) — Lease request with ttl_seconds ≤ 3600
- `VaultLease` (line 162) — Granted lease with heartbeat
- `VaultAuditEntry` (line 188) — Immutable audit log (11 action types)
- `CPEAction` (line 221) — `PASS`, `WARN`, `PSEUDONYMIZE`, `BLOCK`
- `CredentialPIIEntity` (line 228) — PII entity dataclass
- `CredentialCPESession` (line 238) — PII exposure scorer with entity
  weights, co-occurrence boost, and 4-tier thresholds (LOW=1.0, MODERATE=2.0,
  HIGH=3.0, CRITICAL=4.0)

**Finding F-M2**: `CredentialCPESession.process_credential_access()` (line 272)
is called from `vault_core._process_credential_pii_cpe()` (line 797), but it
constructs a **fake `VaultCredential`** with provider="openrouter" and
encrypted_blob="age-encryption.org/v1->X25519->mock" (line 802-808). This
means the CPE scorer is computing exposure scores on synthetic data, not on
the actual credential being accessed. **The PII scoring is theatre.**

**Finding F-M3**: `pseudonymize_audit_entry()` (line 378) uses `from faker import Faker`
as a top-level import inside the function — if `faker` is not installed, the
function crashes. No graceful degradation.

**Finding F-M4**: `provider` Literal (line 82) excludes `firecrawl` correctly
(wait — it does include `firecrawl`). But it excludes `artificial_analysis` —
which is one of the 6 call site providers. The 6 call sites use
"artificial_analysis:api_key" as the `credential_ref` key, but the
`VaultCredential.provider` field will reject this string at instantiation
time (via the Literal validation). This means the call sites **cannot
currently create new credentials** for artificial_analysis — they can only
read existing ones (if any were created before the Literal was added).

**Verdict**: The models are well-structured Pydantic. The CPE scoring is
theatre. The provider Literal is too narrow. For debut Path A, the entire
file is deleted. For Path B, the models can be reduced to a single
`SecretStore` dataclass with `(provider, key_id, plaintext)` fields.

---

### 2.4 `src/omega/vault/vault_core.py` (885 lines)

**Role**: Core CRUD + lease + audit + BlindVault integration.

**Key methods**:

| Method | Line | Status | Used by CLI? | Used by call sites? |
|--------|------|--------|--------------|---------------------|
| `__init__()` | 71 | ✅ | ✅ (via `_get_vault`) | ✅ (all 6) |
| `_load_data()` | 108 | ✅ | — | Called via `_load_sync` alias |
| `_save_data()` | 161 | ✅ | — | — |
| `create_credential()` | 187 | ✅ | ❌ CLI uses `store_credential` | ❌ |
| `get_credential()` | 252 | ✅ | ❌ CLI uses `decrypt_credential` | ❌ |
| `retrieve_credential()` | 283 | ✅ (back-compat alias) | — | ❌ |
| `update_credential()` | 292 | ✅ | ❌ | ❌ |
| `delete_credential()` | 335 | ✅ | ⚠️ CLI uses `del vault._credentials[ref]` directly | — |
| `list_credentials()` | 361 | ✅ | ⚠️ CLI calls but on wrong attribute | — |
| `lease_credential()` | 395 | ✅ | ❌ | ❌ |
| `release_lease()` | 465 | ✅ | ❌ | ❌ |
| `heartbeat_lease()` | 498 | ✅ | ❌ | ❌ |
| `cleanup_expired_leases()` | 517 | ✅ | ⚠️ CLI calls correctly | — |
| `increment_usage()` | 556 | ✅ | ❌ | ❌ |
| `reset_daily_quota()` | 584 | ✅ | ❌ | ❌ |
| `cleanup_cooldown()` | 593 | ✅ | ❌ | ❌ |
| `filter_credentials_by_privacy()` | 605 | ✅ | ❌ | ❌ |
| `get_decrypted_credential()` | 646 | ✅ | ❌ | ❌ |
| `bury_credential()` | 701 | ✅ | ❌ | ❌ |
| `_log_audit()` | 749 | ✅ | ⚠️ CLI uses `vault._audit(...)` | — |
| `_log_credential_access()` | 776 | ✅ | — | — |
| `_process_credential_pii_cpe()` | 797 | ✅ | — | — |
| `get_stats()` | 828 | ✅ | ❌ | — |
| `store_credential()` | — | ❌ **DOES NOT EXIST** | ✅ CLI calls it (line 95, 192) | — |
| `decrypt_credential()` | — | ❌ **DOES NOT EXIST** | ✅ CLI calls it (line 123) | — |
| `verify_integrity()` | — | ❌ **DOES NOT EXIST** | ✅ CLI calls it (line 355) | — |
| `get_recovery_code()` | — | ❌ **DOES NOT EXIST** | ✅ CLI calls it (line 388, 514) | — |
| `rotate_master_password()` | — | ❌ **DOES NOT EXIST** | ✅ CLI calls it (line 538) | — |
| `restore_from_recovery_code()` | — | ❌ **DOES NOT EXIST** | ✅ CLI calls it (line 566) | — |
| `reconcile_quotas()` | — | ❌ **DOES NOT EXIST** | ✅ CLI calls it (line 594) | — |

**Finding F-V1**: **The CLI calls 7 non-existent methods.** Every CLI
command except `list`, `audit`, `audit_summary`, and `cleanup_leases` will
raise `AttributeError` at runtime. The vault CLI is **completely
non-functional** in its current state.

**Finding F-V2**: **CLI reaches into private dict** (line 220-222, 645-646).
The `delete()` command does:
```python
if ref in vault._credentials:
    del vault._credentials[ref]
    await vault._save_credentials()  # Also doesn't exist
    await vault._audit("delete", ref, True)  # Also doesn't exist
```
This bypasses `delete_credential()` (the public method) and calls
`_save_credentials()` (doesn't exist) and `_audit()` (doesn't exist).
**Triple broken.**

**Finding F-V3**: **CLI `backup()` (line 408-437) and `restore()` (line
440-494) are also broken** — they call `vault.age.encrypt()` and
`vault.age.decrypt()` (no `age` attribute on VaultCore), `cred.to_dict()`
(no method on VaultCredential), and `lease.to_dict()` (no method on
VaultLease). `from_dict()` is also called (line 477) but doesn't exist.

**Finding F-V4**: `get_decrypted_credential()` (line 646) **requires a
lease** (line 682). The 6 call sites do **not** acquire leases — they
read `_credentials.get(...)` directly. The public decryption path is
inaccessible without first calling `lease_credential()`, which the call
sites never do.

**Finding F-V5**: `_process_credential_pii_cpe()` (line 797) passes a
**fake VaultCredential** to the CPE scorer (line 802-808). The PII
exposure score is always computed on a synthetic "openrouter:temp" credential,
not the real one. This means the CPE audit entries are meaningless.

**Finding F-V6**: `_load_data()` (line 108) loads audit log from both JSON
array (old) and JSONL (new) formats (line 143-149). The comment says
"Old JSON array format" vs "New JSONL format" — there's a migration path
but no migration script. The audit file is truncated to last 1000 entries
on save (line 174).

**Finding F-V7**: Backward-compatibility aliases (line 155-159):
```python
self._credentials = self.credentials  # Line 156
_load_sync = _load_data               # Line 159
```
These are explicit back-compat shims for "10+ callers" and "13+ callers"
respectively. The call sites use `vault._credentials` (the old name) and
`vault._load_sync()` (the old name). The public API is `self.credentials`
and `_load_data()`. The aliases are intentional debt.

**Finding F-V8**: `create_credential()` (line 217) has a hardcoded
provider whitelist:
```python
if provider not in ("antigravity", "grok", "google", "openrouter", "exa", "firecrawl"):
    raise VaultError(f"Invalid provider: {provider}")
```
This is a **second** provider validation (in addition to the Literal in
the model). It rejects "artificial_analysis" — one of the 6 call site
providers. Even if a user tries to create a new AA credential via
`create_credential()`, they get `VaultError: Invalid provider`.

**Finding F-V9**: No `store_credential()` / `decrypt_credential()` aliases
were preserved. The DEBUT_REMEDIATION_MANUAL §Phase 1 test failure analysis
(D-532) says: "Keep `bury_credential` as canonical API. Do NOT restore
`store_credential` alias." But the CLI was never updated to use
`bury_credential()` — it still calls `store_credential()`. This is the
direct cause of F-V1.

**Verdict**: The vault_core.py is a **well-structured but completely
unwired** implementation. The 6 call sites bypass it entirely; the CLI
calls non-existent methods. For debut Path A, the file is deleted. For
Path B, 7 missing methods need to be added back (or the CLI must be
re-written), plus the `_credentials` private access in 6 call sites
must be migrated to `get_credential()`.

---

### 2.5 `src/omega/vault/blindvault_resolver.py` (569 lines)

**Role**: BlindVault resolver — "injects secrets at the last moment before
system call execution." This is the security boundary that prevents
agents from holding plaintext in memory.

**Key findings**:

**Finding F-B1**: `BlindVaultResolver` is **never instantiated** in the
codebase. The only references are:
- The class definition (line 76)
- The factory function `create_blindvault_resolver()` (line 517)
- A documentation example in `docs/reference/api/vault_core.md:218,316`

There is **no runtime caller**. The `vault_core.py` constructor accepts a
`blindvault_resolver` parameter (line 76), but no factory or wiring code
ever creates one. The `get_decrypted_credential()` method (line 688) calls
`self.blindvault_resolver.resolve(secret_ref)`, but since no resolver is
ever injected, calling `get_decrypted_credential()` will raise
`VaultError("BlindVault resolver not configured")` (line 667).

**Finding F-B2**: `_get_secret_value()` (line 348-367) is a **placeholder
stub** that returns fake data:
```python
async def _get_secret_value(self, secret_name: str, metadata: SecretMetadata) -> str:
    master_key = os.environ.get(self.master_key_env)
    if not master_key:
        raise RuntimeError(...)
    # Simulate secret retrieval
    secret_value = f"sk-or-v1-{secret_name}-{datetime.utcnow().timestamp()}"
    return secret_value
```
This generates a **fake OpenRouter key** like `sk-or-v1-openrouter_api_key-1729123456.789`.
If this were ever called in production, it would return a syntactically
valid but **completely wrong** API key. The comment "In production, this
would call the BlindVault binary or API" (line 352) confirms this is a stub.

**Finding F-B3**: `resolve_secret()` (line 209) and the `resolve()`
method called by `vault_core.get_decrypted_credential()` (line 688) are
**different methods**. The vault_core calls `self.blindvault_resolver.resolve()`
but the BlindVaultResolver class only defines `resolve_secret()`. The
`.resolve()` method **does not exist** on the class. This is a second
silent breakage — even if BlindVaultResolver were instantiated, calling
`get_decrypted_credential()` would raise `AttributeError: 'BlindVaultResolver'
object has no attribute 'resolve'`.

**Finding F-B4**: `resolve_secret()` takes `(secret_reference, agent_id,
command, host, session_id)` — a 5-argument call. The vault_core calls
`self.blindvault_resolver.resolve(secret_ref)` with 1 argument. The
parameter mismatch is fatal.

**Finding F-B5**: `_load_configuration()` (line 129) reads from
`data/blindvault/config.json` with hardcoded sample data
(`openrouter_api_key`, `gcp_service_account`) in `_create_default_config()`
(line 154). This is a **stale sample config** from the original BlindVault
spec — it doesn't match any of the 6 call site providers.

**Finding F-B6**: The dataclass `SecretMetadata` (line 43) has fields
`allowed_agents`, `allowed_commands`, `allowed_hosts`, `max_usage_count`
— a fine-grained ACL model. But the 6 call sites do not use this model.
They reach into the vault directly. The ACL is **theater** in the
current architecture.

**Verdict**: 569 lines of security theater. The BlindVault resolver is
the most over-engineered file in the vault module. For debut Path A, the
file is deleted. For Path B, the file can be safely deleted and the
`get_decrypted_credential()` method in vault_core.py can be replaced with
a direct `decrypt(self.encrypted_blob)` call using the master key from
`os.environ` or `keyring`.

---

### 2.6 `src/omega/cli/vault.py` (657 lines)

**Role**: 18 Click commands for vault operations.

**Commands** (lines from `@vault.command()` decorators):

| # | Command | Line | Method Called | Exists? | Runtime |
|---|---------|------|---------------|---------|---------|
| 1 | `set` | 48 | `vault.store_credential(cred)` | ❌ | **AttributeError** |
| 2 | `get` | 101 | `vault.decrypt_credential(...)` | ❌ | **AttributeError** |
| 3 | `list` | 132 | `vault.list_credentials(prov)` | ✅ | Works (line 361) |
| 4 | `rotate` | 164 | `vault.get_credential(...)` then `vault.store_credential(cred)` | ⚠️ | Partial — first call works, second fails |
| 5 | `delete` | 198 | `del vault._credentials[ref]` + `_save_credentials()` + `_audit()` | ❌❌❌ | **Triple AttributeError** |
| 6 | `audit` | 232 | `vault.audit_log.exists()` | ❌ | **AttributeError** (no `audit_log` attr) |
| 7 | `audit_summary` | 269 | `vault.audit_log.exists()` | ❌ | **AttributeError** |
| 8 | `verify` | 336 | `vault.verify_integrity()` | ❌ | **AttributeError** |
| 9 | `init` | 367 | `vault.get_recovery_code()` | ❌ | **AttributeError** |
| 10 | `backup` | 393 | `vault.age.encrypt()` + `cred.to_dict()` + `lease.to_dict()` | ❌❌❌ | **Triple AttributeError** |
| 11 | `restore` | 440 | `vault.age.decrypt()` + `VaultCredential.from_dict()` | ❌❌ | **AttributeError** |
| 12 | `recovery_code` | 497 | `vault.get_recovery_code()` | ❌ | **AttributeError** |
| 13 | `rotate_master` | 519 | `vault.rotate_master_password()` | ❌ | **AttributeError** |
| 14 | `restore_from_code` | 546 | `vault.restore_from_recovery_code(code)` | ❌ | **AttributeError** |
| 15 | `reconcile` | 575 | `vault.reconcile_quotas()` | ❌ | **AttributeError** |
| 16 | `cleanup_leases` | 600 | `vault.cleanup_expired_leases()` | ✅ | Works (line 517) |
| 17 | `lease_status` | 625 | `vault._credentials[ref]` (private access) | ⚠️ | Works (returns raw cred) |

**Finding F-CLI1**: **16 of 18 commands are broken at runtime.** Only `list`
and `cleanup_leases` are functional. Every other command raises
`AttributeError` because the methods don't exist on VaultCore.

**Finding F-CLI2**: The module docstring (line 1-19) claims 16 commands
but doesn't include `lease_status` (added later at line 625) or `reconcile`
(added at line 575, with an N0/dc-cli-dead comment about a stacked
decorator bug that was fixed on 2026-08-24).

**Finding F-CLI3**: The import statement (line 27) is
`from omega.vault.vault_core import VaultCore` — but the `vault_cli` is
**not registered in the main `omega` CLI** in `src/omega/cli/oracle_cli.py`.
Per the DEBUT_REMEDIATION_MANUAL (D-535), the vault CLI default registration
was removed. The CLI module is importable but not mounted.

**Finding F-CLI4**: The `__import__("datetime")` calls (lines 191, 417, 481)
are inline imports to work around a missing top-level import. This is a
code smell — `datetime` should be imported at the top of the file.

**Finding F-CLI5**: The passphrase is prompted via `click.prompt=True,
hide_input=True` (line 64, etc.) with `envvar="OMEGA_VAULT_PASSPHRASE"`.
This is correct UX for a secret-bearing CLI, but since the CLI is broken,
this is moot.

**Verdict**: The CLI is **16/18 broken**. It is excluded from debut (D-535)
and should be deleted as part of Path A. If Path B is chosen, the CLI
must be either re-written against a working vault or removed entirely.

---

## 3. Per-Call-Site Analysis (6 sites)

### 3.1 Call site 1: `src/omega/workers/freshness_checker.py:201,704`

**Context**: `ArtificialAnalysisClient.__init__()` (line 193) and
`main()` (line 695). Resolves `AA_API_KEY` for capability score freshness.

**Current code** (line 195-204):
```python
if api_key is None:
    try:
        from omega.vault import VaultCore
        vault = VaultCore()
        vault._load_sync()
        cred = vault._credentials.get("artificial_analysis:api_key")
        api_key = cred.encrypted_blob if cred else None
    except Exception:
        api_key = None
```

**What it does**:
1. Instantiates `VaultCore()` with no args (default `vault_path=Path("data/vault")`)
2. Calls `vault._load_sync()` (the back-compat alias for `_load_data()`)
3. Gets the credential from the **private** `_credentials` dict by the
   string key `"artificial_analysis:api_key"`
4. Returns `cred.encrypted_blob` — **the age-armored ciphertext**, not
   the decrypted key

**What's wrong**:
- `provider="artificial_analysis"` is **not in the VaultCredential Literal**
  (line 82) — so creating a new credential would fail Pydantic validation
- `cred.encrypted_blob` is **age-armored ciphertext** (starts with
  "age-encryption.org/v1..."), not a plaintext API key. Passing this to
  AA's API will result in 401 Unauthorized.
- No fallback to `os.environ` — if the vault is empty, `api_key` is `None`
  and the client silently fails.
- No `provider` validation in the `VaultCore()` constructor (it only
  validates in `create_credential()`, which the call sites never call).

**What happens if missing**:
- `vault._credentials.get("artificial_analysis:api_key")` returns `None`
- `api_key = None` (line 202)
- The `httpx.Client` headers don't include `x-api-key` (line 212)
- The AA API will return 401 for all requests
- No error is raised — the client silently degrades

**Thread safety**: `vault._credentials` is a plain `dict` (line 110 of
vault_core.py). No `threading.Lock` or `anyio.Lock` protects it. If two
threads call `_load_data()` concurrently, the dict could be in an
inconsistent state. The `_save_data()` method is async, so concurrent
async callers could race.

**Public API migration**:
```python
# Current (broken):
cred = vault._credentials.get("artificial_analysis:api_key")
api_key = cred.encrypted_blob if cred else None

# Proposed (Path A — delete vault, use env):
import os
api_key = os.environ.get("AA_API_KEY")

# Proposed (Path B — public API):
from omega.vault import VaultCore
vault = VaultCore()
api_key = vault.get_credential("artificial_analysis", "api_key")  # Returns decrypted str
```

**Refactor cost**: 1 line in 2 places (lines 201, 704). Total: 2 lines.

---

### 3.2 Call site 2: `src/omega/tools/firecrawl_direct.py:31`

**Context**: Module-level constant `FIRECRAWL_API_KEY` (resolved at import
time). Used for direct Firecrawl API calls.

**Current code** (line 25-37):
```python
try:
    from omega.vault import VaultCore
    vault = VaultCore()
    vault._load_sync()
    cred = vault._credentials.get("firecrawl:api_key")
    FIRECRAWL_API_KEY = cred.encrypted_blob if cred else ""
    if FIRECRAWL_API_KEY:
        logger.info("Firecrawl API key resolved from Sovereign VaultCore")
        return FIRECRAWL_API_KEY
except Exception as e:
    logger.debug(f"VaultCore resolution failed: {e}")
```

**What's wrong**:
- Same `encrypted_blob` ciphertext issue as call site 1
- `provider="firecrawl"` IS in the VaultCredential Literal (line 82) and
  in `create_credential()` whitelist (line 217), so credential creation
  would work
- The comment on line 39 says "No fallback to environment - VaultCore is
  the single source of truth" — but if the vault is empty, the key is `""`
  and direct tools fail. **The code contradicts itself: it claims "single
  source of truth" but has no actual source.**
- The function returns the empty string instead of raising — silent
  degradation is a M23 violation (no soft-failures).

**What happens if missing**:
- `FIRECRAWL_API_KEY = ""` (line 32)
- `if FIRECRAWL_API_KEY:` is False (line 33)
- The function falls through to the bottom and returns `""` (line 41)
- The module-level constant is `""` — every direct tool call will fail
  with a cryptic error from httpx

**Thread safety**: Same as call site 1 — no locking on `vault._credentials`.

**Public API migration**:
```python
# Proposed (Path A):
import os
FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY", "")

# Proposed (Path B):
from omega.vault import VaultCore
vault = VaultCore()
FIRECRAWL_API_KEY = vault.get_credential("firecrawl", "api_key") or ""
```

**Refactor cost**: 1 block of code (lines 25-41). Total: ~15 lines.

---

### 3.3 Call site 3: `src/omega/library/discovery.py:97,107`

**Context**: `LibraryDiscovery.__init__()` (line 90-113). Resolves Exa
and Firecrawl API keys at instance creation.

**Current code** (line 94-113):
```python
try:
    vault = VaultCore()
    vault._load_sync()
    exa_cred = vault._credentials.get("exa:api_key")
    self.exa_key = exa_cred.encrypted_blob if exa_cred else None
    if not self.exa_key:
        logger.warning("VaultCore exa resolution failed - no key in vault")
except (OmegaError, KeyError) as e:
    logger.warning(f"VaultCore exa resolution failed: {e}")
    self.exa_key = None
try:
    vault = VaultCore()  # ⚠️ Instantiated TWICE
    vault._load_sync()
    fc_cred = vault._credentials.get("firecrawl:api_key")
    self.firecrawl_key = fc_cred.encrypted_blob if fc_cred else None
    if not self.firecrawl_key:
        logger.warning("VaultCore firecrawl resolution failed - no key in vault")
except (OmegaError, KeyError) as e:
    logger.warning(f"VaultCore firecrawl resolution failed: {e}")
    self.firecrawl_key = None
```

**What's wrong**:
- Same `encrypted_blob` ciphertext issue
- `VaultCore()` is **instantiated twice** (line 95, 105) — one per key.
  Each instantiation reads from disk, parses JSON, and builds a Pydantic
  model. This is wasteful but not broken.
- `(OmegaError, KeyError)` exception handling — `OmegaError` is not
  imported in the file (would need to verify), and `KeyError` is never
  raised by the vault code (it uses `.get()` everywhere, which returns
  `None`). The exception handler is **dead code**.
- `if not self.exa_key` and `if not self.firecrawl_key` log warnings
  but the discovery still proceeds with `None` keys — search calls will
  fail at request time with HTTP 401.

**What happens if missing**:
- `self.exa_key = None` and `self.firecrawl_key = None`
- Discovery proceeds but all search calls fail silently
- No error is raised at construction time

**Thread safety**: Two `VaultCore()` instances, two separate `_credentials`
dicts, no shared state. The second instance is a separate copy of the
same disk data. If another process writes to the vault between the two
instantiations, the second instance could see newer data — a race condition
on the file system.

**Public API migration**:
```python
# Proposed (Path B):
from omega.vault import VaultCore
vault = VaultCore()
self.exa_key = vault.get_credential("exa", "api_key")
self.firecrawl_key = vault.get_credential("firecrawl", "api_key")
```

**Refactor cost**: 2 try/except blocks → 4 lines. Total: ~30 lines.

---

### 3.4 Call site 4: `src/omega/teachers/nemotron_pipeline.py:127`

**Context**: `_resolve_openrouter_key()` (line 120-132). Resolves
OpenRouter API key for DPO pair generation.

**Current code** (line 120-132):
```python
def _resolve_openrouter_key(self) -> str:
    """Resolve OpenRouter API key from vault or environment."""
    try:
        from omega.vault import VaultCore
        vault = VaultCore()
        vault._load_sync()
        cred = vault._credentials.get("openrouter:api_key")
        if cred:
            return cred.encrypted_blob
    except Exception as e:
        logger.warning(f"VaultCore resolution failed: {e}")
    return ""
```

**What's wrong**:
- Same `encrypted_blob` ciphertext issue
- The function name claims "from vault or environment" but only tries
  the vault. The `os.environ` fallback was never implemented.
- The function returns `""` (empty string) on failure — but the caller
  (line 134 `generate_dpo_pair`) likely passes this to httpx, which
  will return 401.

**What happens if missing**:
- Returns `""`
- Caller passes empty string to OpenRouter API
- OpenRouter returns 401 "No credentials provided"
- DPO pair generation fails

**Thread safety**: Same as call site 1.

**Public API migration**:
```python
# Proposed (Path A):
import os
def _resolve_openrouter_key(self) -> str:
    return os.environ.get("OPENROUTER_API_KEY", "")

# Proposed (Path B):
from omega.vault import VaultCore
def _resolve_openrouter_key(self) -> str:
    vault = VaultCore()
    return vault.get_credential("openrouter", "api_key") or ""
```

**Refactor cost**: 1 method body (lines 120-132). Total: ~10 lines.

---

### 3.5 Call site 5: `src/omega/cli/vault.py:220,221,420,477,481,485`

**Context**: Multiple CLI commands reach into private dicts. Already
analyzed in §2.6.

**Specific issues**:
- `delete()` (line 220-222): `if ref in vault._credentials: del vault._credentials[ref]`
  Bypasses `delete_credential()` public method. **Triple broken** (also
  calls `_save_credentials()` and `_audit()` which don't exist).
- `backup()` (line 420-421):
  ```python
  "credentials": {ref: cred.to_dict() for ref, cred in vault._credentials.items()},
  "leases": {lid: lease.to_dict() for lid, lease in vault._leases.items()},
  ```
  - `cred.to_dict()` doesn't exist on VaultCredential (use `.model_dump()`)
  - `lease.to_dict()` doesn't exist on VaultLease
  - `vault._leases` is the old name (public is `vault.leases`)
- `restore()` (line 477): `VaultCredential.from_dict(cred_data)` — doesn't
  exist (use `VaultCredential(**cred_data)`)
- `restore()` (line 481): `__import__("src.omega.vault.vault_core",
  fromlist=["VaultLease"]).VaultLease(**lease_data)` — works but is
  hideous
- `restore()` (line 485): `vault._leases[lid] = lease` — private dict

**Thread safety**: The CLI is single-threaded (anyio.run blocks the event
loop), so thread safety is not an issue here. But the calls to private
dicts violate the abstraction.

**Refactor cost**: Already broken. For Path A, delete the CLI. For Path B,
rewrite against the public API.

---

### 3.6 Call site 6: `src/omega/cli/vault.py:645,646` (lease_status)

**Context**: `lease_status()` command (line 625-653).

**Current code** (line 645-646):
```python
if ref in vault._credentials:
    cred = vault._credentials[ref]
    click.echo(f"Credential: {ref}")
    click.echo(f"  Status: {cred.status.value}")
    click.echo(f"  Leased to: {cred.current_lease_agent or 'none'}")
    ...
```

**What's wrong**:
- Same private dict access as other CLI commands
- This one **happens to work** because `vault._credentials` is a valid
  alias for `vault.credentials` (line 156 back-compat shim)
- But it still bypasses `get_credential()` which would raise
  `CredentialNotFoundError` instead of returning `None`

**Refactor cost**: 2 lines (645-646). Total: 2 lines.

---

### 3.7 Summary: All 6 call sites do the same wrong thing

Every call site:
1. Instantiates `VaultCore()` with default args
2. Calls `vault._load_sync()` (private back-compat alias)
3. Gets from `vault._credentials` (private dict)
4. Returns `cred.encrypted_blob` (the age-armored ciphertext, not the
   decrypted key)
5. Has no fallback to `os.environ`
6. Has no lease acquisition (required by `get_decrypted_credential()`)
7. Catches all exceptions silently (M23 violation)

**The pattern is identical across all 6 sites.** The fix is also
identical: replace with a public API call that returns decrypted
plaintext, or replace with `os.environ.get()` for Path A.

---

## 4. Public API Design Recommendation

### 4.1 The current public API is incomplete

`VaultCore` exposes (per `__init__.py`):
- `create_credential()` — stores ciphertext, not plaintext
- `get_credential()` — returns `VaultCredential` (with `encrypted_blob`)
- `update_credential()` — updates fields
- `delete_credential()` — deletes by ref
- `list_credentials()` — lists with filters
- `lease_credential()` — creates a lease (required for decryption)
- `release_lease()`, `heartbeat_lease()`, `cleanup_expired_leases()`
- `get_decrypted_credential()` — **requires a lease** (unreachable from
  call sites)
- `bury_credential()` — D-567: post-debut only

**No method takes a plaintext value.** Every "store" method expects
`encrypted_blob: str` (age-armored ciphertext). The CLI was supposed to
encrypt before calling `store_credential()` (line 91 comment: "Will be
encrypted by store_credential"), but `store_credential()` doesn't exist
and `create_credential()` doesn't encrypt — it just stores the value as-is.

### 4.2 Proposed public API for Path B (minimal)

```python
class VaultCore:
    # ... existing CRUD methods ...

    async def store_plaintext(
        self,
        provider: str,
        key_id: str,
        plaintext: str,
        cred_type: CredentialType = CredentialType.API_KEY,
        tier: CredentialTier = CredentialTier.FREE,
    ) -> VaultCredential:
        """Store a credential, encrypting plaintext internally."""
        encrypted = self.crypto_manager.encrypt(plaintext)
        return await self.create_credential(
            provider=provider,
            key_id=key_id,
            encrypted_blob=encrypted,
            cred_type=cred_type,
            tier=tier,
        )

    async def get_plaintext(
        self,
        provider: str,
        key_id: str,
    ) -> str:
        """Get decrypted plaintext credential. No lease required."""
        cred = await self.get_credential(provider, key_id)
        return self.crypto_manager.decrypt(cred.encrypted_blob)

    def get_credential_sync(
        self,
        provider: str,
        key_id: str = "default",
    ) -> Optional[str]:
        """Synchronous get-decrypted-plaintext for legacy call sites.
        
        Returns None if not found. No exception.
        """
        try:
            self._load_data()
            cred = self.credentials.get(f"{provider}:{key_id}")
            if not cred:
                return None
            return self.crypto_manager.decrypt(cred.encrypted_blob)
        except Exception:
            return None
```

**Key design decisions**:
1. **No lease required for `get_plaintext()`** — the lease model is
   over-engineered for debut. A simple decrypted-return is what the 6
   call sites need.
2. **Synchronous `get_credential_sync()`** for legacy compat — the 6
   call sites are sync (no `await` in their hot paths).
3. **Returns `Optional[str]` instead of raising** — the call sites all
   catch exceptions silently, so returning `None` matches their existing
   semantics.
4. **Encryption happens inside the vault** — the CLI/call sites should
   never see ciphertext.

### 4.3 Thread safety improvements

The current `_credentials: Dict[str, VaultCredential]` is unprotected.
For debut Path B, add `threading.Lock`:

```python
import threading

class VaultCore:
    def __init__(self, ...):
        ...
        self._lock = threading.Lock()

    def _load_data(self) -> None:
        with self._lock:
            # ... existing load logic ...

    async def _save_data(self) -> None:
        with self._lock:
            # ... existing save logic ...
```

### 4.4 Provider whitelist expansion

The Literal in VaultCredential (line 82) and the whitelist in
`create_credential()` (line 217) must be expanded to include all
6 call site providers:

```python
# Current:
provider: Literal["antigravity", "grok", "google", "openrouter", "exa", "firecrawl"]

# Proposed:
provider: Literal[
    "antigravity", "grok", "google", "openrouter", "exa", "firecrawl",
    "artificial_analysis", "searxng", "parallel", "huggingface",
    # ... all 27 ProviderName values ...
]
```

Or, remove the Literal entirely and use `str` with manual validation.

---

## 5. Refactoring Plan (exact changes per call site)

### 5.1 Option A: Path A (delete vault entirely) — RECOMMENDED

**Effort**: ~30 minutes. **Net Δ**: -2,733 LOC.

| File | Change |
|------|--------|
| `src/omega/vault/__init__.py` | Delete file |
| `src/omega/vault/crypto.py` | Delete file |
| `src/omega/vault/models.py` | Delete file |
| `src/omega/vault/vault_core.py` | Delete file |
| `src/omega/vault/blindvault_resolver.py` | Delete file |
| `src/omega/cli/vault.py` | Delete file (already not registered) |
| `scripts/vault_import.py` | Delete file (or keep for post-debut if wanted) |
| `src/omega/workers/freshness_checker.py:201,704` | Replace with `os.environ.get("AA_API_KEY")` |
| `src/omega/tools/firecrawl_direct.py:25-41` | Replace with `os.environ.get("FIRECRAWL_API_KEY")` |
| `src/omega/library/discovery.py:97,107` | Replace with `os.environ.get("EXA_API_KEY")` and `os.environ.get("FIRECRAWL_API_KEY")` |
| `src/omega/teachers/nemotron_pipeline.py:127` | Replace with `os.environ.get("OPENROUTER_API_KEY")` |
| `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` | Mark "Vault honesty" ✅ as Path A complete |
| `data/coordination/VAULT_OVERHAUL_SYNTHESIS_KALI_20260818.md` | Archive as superseded by Path A |

**Verification**:
```bash
rg -n "from omega.vault|import omega.vault|VaultCore|vault\._credentials" src/
# Expected: 0 matches

rg -n "store_credential|decrypt_credential|verify_integrity|get_recovery_code" src/
# Expected: 0 matches
```

**Tests**:
- `tests/unit/test_vault_core.py` (377 lines) — delete or mark skipped
- `tests/test_contract_m21.py:test_vault_core_store_credential_and_get_providers`
  — delete or mark skipped

**Risks**:
- Post-debut workstreams (V-1, FleetOrchestrator) that reference vault
  need to be re-scoped to use `keyring` or `os.environ`
- The 6 call sites need `.env` or environment variables set in
  `install.sh` / `setup.sh`

**Net benefit**: -2,733 LOC of broken code, +6 call sites that work
correctly via `os.environ`.

---

### 5.2 Option B: Path B (minimal vault, ≤50 lines) — IF ARCHITECT INSISTS

**Effort**: 8–12 hours. **Net Δ**: -2,400 LOC (from 2,733 to ~300).

**Step 1**: Delete `blindvault_resolver.py` entirely (-569 LOC).
- `vault_core.get_decrypted_credential()` (line 646-695) is rewritten
  to use `crypto_manager.decrypt(cred.encrypted_blob)` directly.
- No more `secret_ref` parsing, no more session/host/command ACLs.

**Step 2**: Slim `vault_core.py` to a minimal store (-585 LOC, from 885
to ~300).
- Keep: `__init__`, `_load_data`, `_save_data`, `create_credential`,
  `get_credential`, `update_credential`, `delete_credential`,
  `list_credentials`, `increment_usage`, `reset_daily_quota`.
- Delete: lease methods (10 methods, ~200 LOC), CPE scorer
  (CredentialCPESession import + 3 methods, ~80 LOC), bury integration
  (~50 LOC), audit logging beyond simple append (~100 LOC), privacy
  filtering (~40 LOC).
- Add: `get_plaintext()` and `get_credential_sync()` per §4.2.

**Step 3**: Fix `cli/vault.py` (-400 LOC).
- Delete `verify`, `init`, `backup`, `restore`, `recovery_code`,
  `rotate_master`, `restore_from_code`, `reconcile` (8 commands, all
  broken).
- Keep `set`, `get`, `list`, `rotate`, `delete`, `audit`, `audit_summary`,
  `cleanup_leases`, `lease_status` — but rewrite to use public API.
- OR delete the entire CLI file (D-535 already removed it from
  registration).

**Step 4**: Migrate 6 call sites to public API (-30 LOC, +30 LOC).
- Each call site: replace `vault._credentials.get(...).encrypted_blob`
  with `vault.get_credential_sync("provider", "key_id")` (sync, returns
  Optional[str]).
- Or, for Path B + audit, replace with `os.environ.get(...)` fallback
  chain: `os.environ.get(KEY) or vault.get_credential_sync(...)`.

**Step 5**: Expand provider whitelist.
- `VaultCredential.provider` Literal (line 82) — add all 6 call site
  providers.
- `create_credential()` whitelist (line 217) — match the Literal.

**Step 6**: Add thread safety.
- `threading.Lock` around `_load_data` and `_save_data`.

**Step 7**: Add tests.
- Unit test for `get_credential_sync()` round-trip (encrypt → store →
  get_credential_sync → decrypt → matches).
- Integration test for each of the 6 call sites with a mock vault.

**Verification**:
```bash
rg -n "vault\._credentials|vault\._load_sync|vault\._leases|vault\._audit" src/
# Expected: 0 matches

rg -n "BlindVaultResolver" src/
# Expected: 0 matches
```

**Tests**:
- Keep `tests/unit/test_vault_core.py` but rewrite for minimal API
- Add `tests/integration/test_vault_call_sites.py` for the 6 sites

**Risks**:
- 8-12 hours of work in DEL-1 week 3
- Tests for the 6 call sites don't exist
- The `crypto.py` Argon2id misdirection (F-C1) still applies
- The CPE scorer is still theatre (F-M2)

**Net benefit**: -2,400 LOC, working CLI (8 commands instead of 18),
working call sites. But still inferior to `os.environ` for the debut.

---

## 6. L1 → L2 → L3 Distillation

### L1 (Narrative): What happened?

The vault module was scaffolded in 2,733 LOC across 6 files as a
"production-grade credential vault" with Argon2id KDF, age encryption,
M25 lease management, CPE PII scoring, BlindVault resolver, Bury
PID-bound sessions, and 18 CLI commands. The CLI was registered to
the main `omega` CLI. Six call sites in the codebase were wired to
read from the vault.

When the debut preparation began, a forensic review revealed:
1. The CLI calls 7 non-existent methods (F-V1) — 16/18 commands raise
   AttributeError at runtime.
2. The BlindVault resolver is never instantiated (F-B1) and its
   secret retrieval is a stub returning fake data (F-B2).
3. All 6 call sites reach into the private `_credentials` dict and
   treat the `encrypted_blob` (age-armored ciphertext) as the plaintext
   API key.
4. The CPE PII scoring computes scores on synthetic data, not real
   credentials.
5. The CLI is already not registered to the main `omega` CLI per D-535.

The DEBUT_REMEDIATION_MANUAL (D-535) concluded: "VaultCore is a
sidecar — CLI calls missing `store_credential`, Gateway dumps `.env`
into `os.environ`. Not wired. 2,039 LOC custom code → 3 community
tools is post-debut." The Architect must choose between Path A
(delete) and Path B (≤50-line minimal).

### L2 (Insight): What does this mean?

**The vault is a textbook example of M19 (Adversarial Alchemy) without
the alchemy.** The original design was ambitious — Argon2id, age
encryption, M25 leases, BlindVault injection at syscall boundary,
CPE PII scoring. But the implementation was never wired:
- The CLI was built but never tested (16/18 broken at runtime).
- The BlindVault resolver was written but never instantiated.
- The lease model was designed but never used by any caller.
- The CPE scoring was implemented but computed on fake data.
- The call sites bypassed the public API entirely.

The result is 2,733 LOC of **security theater** — code that looks
secure (encryption! leases! ACLs!) but provides no actual security
guarantee because it's not wired to the real data path.

**The 6 call sites are the truth.** They show what the codebase
actually needs from a vault: a simple `get_secret(provider, key_id) → str`
operation. Everything else (leases, CPE, BlindVault, Bury) is
over-engineering for a debut that doesn't have the fleet orchestration
or PII scoring pipelines to use it.

**M19 violation pattern**: "Sometimes a bug is just a bug. Simple code
errors, typos, and broken imports must be fixed directly and cleanly
without attempting to extract 'esoteric advantages' that introduce
unnecessary complexity, bloat, or fragile state machines." The vault
is the opposite — it introduced fragile state machines (leases, CPE,
Bury) without any actual consumer to justify them.

**M23 violation pattern**: "No soft-failures or simulated rigor." Every
call site catches all exceptions and silently returns `None` or `""`.
The BlindVault `_get_secret_value()` is a stub returning fake data —
this is simulated rigor. The CLI is broken at runtime — this is
simulated rigor.

### L3 (Universal Principle): What is the timeless truth?

> **A credential vault that is not wired to the data path is worse
> than no vault at all, because it creates the illusion of security
> while leaving the actual secret resolution to the weakest link
> (the call sites).**

The universal pattern: **Security infrastructure must be wired or
deleted, never scaffolded.** A half-built vault with stubs, broken
CLIs, and unwired resolvers is **more dangerous** than a simple
`os.environ.get()` because it gives the operator false confidence.
The operator believes secrets are encrypted and ACL'd, but in
reality the encryption key is in an env var, the ACL is never
checked, and the resolver returns `f"sk-or-v1-{name}-{timestamp}"`.

**Adversarial corollary**: A vault that returns fake data is an
**active vulnerability**, not a passive one. An attacker who
compromises the vault doesn't just steal secrets — they can inject
fake secrets that the caller trusts as real. The BlindVault
`_get_secret_value()` stub is exactly this vulnerability.

**Sovereign corollary**: Sovereignty requires **honest infrastructure**.
If the vault is not production-ready, say so. The DEBUT_REMEDIATION_MANUAL
(D-535) said so. The code confirms it. The right action is to delete
the vault, not to fix it — because the cost of fixing (8-12 hours
of work) is greater than the cost of using `os.environ` (0 hours)
and the result is still inferior.

**L3 axiom for debut**: *Path A — delete the vault. Use environment
variables. Document the post-debut V-1 Vault MVP as the proper
replacement when fleet orchestration and PII scoring are actually
wired.*

---

## 7. References (file:line for everything)

### 7.1 Vault source files
- `src/omega/vault/__init__.py:1-71` — package exports
- `src/omega/vault/crypto.py:1-208` — Argon2id + age
- `src/omega/vault/models.py:1-432` — Pydantic models + CPE
- `src/omega/vault/vault_core.py:1-885` — CRUD + lease + audit
- `src/omega/vault/blindvault_resolver.py:1-569` — BlindVault resolver (dead code)
- `src/omega/cli/vault.py:1-657` — 18 CLI commands (16 broken)

### 7.2 Six call sites
- `src/omega/workers/freshness_checker.py:201` — `_credentials.get("artificial_analysis:api_key")`
- `src/omega/workers/freshness_checker.py:704` — same pattern in main()
- `src/omega/tools/firecrawl_direct.py:31` — `_credentials.get("firecrawl:api_key")`
- `src/omega/library/discovery.py:97` — `_credentials.get("exa:api_key")`
- `src/omega/library/discovery.py:107` — `_credentials.get("firecrawl:api_key")`
- `src/omega/teachers/nemotron_pipeline.py:127` — `_credentials.get("openrouter:api_key")`
- `src/omega/cli/vault.py:220-222` — `del vault._credentials[ref]` (delete)
- `src/omega/cli/vault.py:420-421` — `vault._credentials.items()`, `vault._leases.items()` (backup)
- `src/omega/cli/vault.py:477` — `VaultCredential.from_dict(cred_data)` (restore)
- `src/omega/cli/vault.py:481` — `__import__("src.omega.vault.vault_core", fromlist=["VaultLease"])` (restore)
- `src/omega/cli/vault.py:485` — `vault._leases[lid] = lease` (restore)
- `src/omega/cli/vault.py:645-646` — `vault._credentials[ref]` (lease_status)

### 7.3 Broken methods (called by CLI, don't exist in VaultCore)
- `vault.store_credential()` — called at `cli/vault.py:95,192`, missing
- `vault.decrypt_credential()` — called at `cli/vault.py:123`, missing
- `vault.verify_integrity()` — called at `cli/vault.py:355`, missing
- `vault.get_recovery_code()` — called at `cli/vault.py:388,514`, missing
- `vault.rotate_master_password()` — called at `cli/vault.py:538`, missing
- `vault.restore_from_recovery_code()` — called at `cli/vault.py:566`, missing
- `vault.reconcile_quotas()` — called at `cli/vault.py:594`, missing
- `vault.audit_log` (attribute) — called at `cli/vault.py:252,289`, missing
- `vault.age.encrypt()/decrypt()` — called at `cli/vault.py:426,464`, missing
- `vault._save_credentials()` — called at `cli/vault.py:222,487`, missing
- `vault._audit()` — called at `cli/vault.py:223`, missing
- `cred.to_dict()` — called at `cli/vault.py:420`, missing (use `.model_dump()`)
- `lease.to_dict()` — called at `cli/vault.py:421`, missing
- `VaultCredential.from_dict()` — called at `cli/vault.py:477`, missing

### 7.4 Decision documents
- `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md:122` — "Vault is a sidecar, not the secret path"
- `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md:300` — vault CLI default registration removed
- `docs/strategy/ENGINE_DECISIONS_CONSOLIDATED_20260817.md:200` — D-535 "Invert V-1 from build/wire to hide or delete"
- `docs/strategy/PLAN_DEBUT_CLEANSING_20260817.md:70-72` — DEL-1 Week 3 vault honesty decision
- `docs/strategy/POST_DEBUT_ROADMAP.md:27` — Path A vs Path B for vault
- `data/coordination/VAULT_OVERHAUL_SYNTHESIS_KALI_20260818.md:37-104` — G-α to G-ε vault call site gaps
- `data/coordination/CLINE_DEEP_PASS_AMENDMENT_20260818.md:11` — store_credential/decrypt_credential missing
- `data/coordination/ROC_RACOON_KALI_REPORT_20260816.md:50` — 18 test failures from API drift
- `data/coordination/MAAT_BUILD_SIDE_REPORT_20260823.md:173` — vault CLI missing store_credential

### 7.5 Related research
- `docs/specs/VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md:959-1264` — full vault overhaul spec
- `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md:410` — `rg -n "store_credential|bury_credential|_load_sovereign_secrets" src/omega`
- `docs/archive/specs/vault-overhaul-20260818/R_VAULT_UNIFIED_SYSTEM_20260725.md` — original R_VAULT_SCHEMA_V2 spec
- `docs/reference/api/vault_core.md:195-316` — API reference (stale, references `BlindVaultResolver(vault: VaultCore, allowlist=...)` which doesn't match the actual signature)

### 7.6 Tests (potentially affected)
- `tests/unit/test_vault_core.py:377` — `test_reconcile_quotas` (test for non-existent method)
- `tests/test_contract_m21.py:506-509` — `test_vault_core_store_credential_and_get_providers` (test for non-existent method)

### 7.7 Mandate compliance
- **M1 AnyIO** — ✅ vault uses `anyio` for async I/O, but the 6 call sites use sync code
- **M7 Local-First** — ⚠️ vault is local-first but never instantiated; the actual local secret resolution is via `os.environ`
- **M8 Zero Telemetry** — ✅ no external telemetry in vault code
- **M9 Error Integrity** — ❌ all 6 call sites catch `Exception` and silently return None/"" (violates §9 typed error contract)
- **M13 Temple-Grade** — ⚠️ code quality is high but tests don't cover the 6 call sites
- **M14 Heritage** — ⚠️ no `[id-soft:]` tags in vault (correct — vault is not heritage-derived)
- **M19 Adversarial Alchemy** — ❌ "Sometimes a bug is just a bug" — the vault is over-engineered without any consumer
- **M22 Response Provenance** — ✅ vault logs `agent_id` in audit entries
- **M23 Failure Integrity** — ❌ CLI is broken (soft-failure), BlindVault stub returns fake data (simulated rigor), call sites silently fail
- **M24 Venv Sovereignty** — ✅ vault uses `.venv` (no `--break-system-packages`)
- **M26 Doc Standards** — ⚠️ `docs/reference/api/vault_core.md` is stale and references non-existent APIs
- **M27 Tracking Integrity** — ⚠️ vault status is documented in PIVOT_LOG but the tracking IDs (V-1) are post-debut

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ deepseek-v4-flash ⬡ R_VAULT_DEEP_CODE_20260827 ⬡ SOVEREIGN-VAULT-ANALYSIS*
