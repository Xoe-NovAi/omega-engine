# 🔱 Omega Engine — Vault Overhaul: Migration Surface Amendment
**AP Token**: `AP-VAULT-MIGRATION-SURFACE-20260818-v1.0.0`
**Author**: Kali (Oversoul / Sprint Coordinator)
**Date**: 2026-08-18
**Status**: SUPPLEMENTARY — **closes G-α…G-ε**; **supersedes Part 4 "Files to Modify" table** and R3 E-10 Day-4 checklist where noted.
**Depends on**: `VAULT_SYSTEM_OVERHAUL_SPEC_20260818*` + `VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818*` (R1-R3).

---

## 0. Why This Document Exists

Direct `src/omega/` verification (2026-08-18) shows the secret architecture is **distributed**, not centralized in `VaultCore`. The original deletion plan (`git rm -r src/omega/vault/` + 6-file modify list) would break **four modules** that import `VaultCore` and reach into its **private** `vault._credentials` dict. This amendment maps every consumption site to `CredentialProvider` so Day 4 is safe.

**Verified consumption sites (grep evidence):**

| Module | Line(s) | Vault usage |
|--------|---------|-------------|
| `src/omega/oracle/search_providers.py` | 39-44, 228-233 | `VaultCore()` → `_load_sync()` → `_credentials.get("firecrawl:api_key"\|"exa:api_key").encrypted_blob` |
| `src/omega/oracle/providers.py` | 68-114 | `VaultCore()` → `_load_sync()` (via `anyio.to_thread`) → `_credentials.get("google:api_key").encrypted_blob` |
| `src/omega/oracle/backends/google_compat.py` | 85-90 | `VaultCore()` → `_load_sync()` → `_credentials.get("google:api_key").encrypted_blob` |
| `src/omega/oracle/orchestrator.py` | 164-169 | `VaultCore()` → `_load_sync()` → all `c.provider.value == "google"` → `encrypted_blob` list |
| `src/omega/oracle/model_gateway.py` | 127, 316-341 | `_load_sovereign_secrets()` loads `.env` → `os.environ` (Carmack's finding) |
| `config/providers.yaml` | 196-340 | `api_key: env:OPENROUTER_API_KEY` etc. (env-var refs, not vault) |
| `src/omega/oracle/backends/antigravity_provider.py` | 66 | "vault-first chain" — **VERIFY** (no `from omega.vault import` found; likely env-only; confirm before Day 4) |

---

## 1. Canonical Key Naming (resolves G-γ)

The old vault keys are `provider:keyname` (e.g., `firecrawl:api_key`, `google:api_key`). The new `CredentialProvider` stores as `provider_account` (e.g., `openrouter_1`). **Mapping rule:**

```
vault key "X:Y"   →   CredentialProvider(provider="X", account_id="Y")
envelope file     →   ~/.omega/secrets/X_Y.enc
keyring username  →   "omega-engine" / "X_Y"
```

For LLM providers from `providers.yaml` (`openrouter`, `google`, `anthropic`, `xai`, `antigravity`), the account_id is the numeric shard index used in `providers.yaml` (e.g., `openrouter_1`). For non-LLM services (`firecrawl`, `exa`, `google` search key), account_id = `api_key` (single account).

**Migration action**: Users re-populate via `omega secrets import --from-file=secrets.md` (debut is private-repo single-operator). Document: *"After upgrade, re-run `omega secrets import`; old VaultCore data is not auto-migrated."*

---

## 2. Per-Module Migration (closes G-α, G-β, G-δ, G-ε)

### 2.1 `search_providers.py` (Firecrawl / Exa)
**Before:**
```python
from omega.vault import VaultCore
vault = VaultCore(); vault._load_sync()
cred = vault._credentials.get("firecrawl:api_key")
return cred.encrypted_blob if cred else ""
```
**After:**
```python
from omega.security.credential_provider import CredentialProvider
try:
    return CredentialProvider().get_provider_credential("firecrawl", "api_key")
except CredentialNotFoundError:
    return ""   # M9: log miss, fall back to empty (caller handles)
```
Apply same pattern for `exa:api_key`. **Remove `from omega.vault import VaultCore`.**

### 2.2 `providers.py` (Google resolve)
**Before:** `vault._credentials.get("google:api_key").encrypted_blob`
**After:**
```python
try:
    return CredentialProvider().get_provider_credential("google", "api_key")
except CredentialNotFoundError as e:
    # M9: distinguish "not configured" from "provider broken"
    logger.error("No usable 'google:api_key' credential found")
    raise OmegaError(message="No Google API key found", raw_error=e) from e
```
Keep the `anyio.to_thread.run_sync` wrapper if called from async (M1-compliant).

### 2.3 `backends/google_compat.py`
Same as 2.2 (single `google:api_key`). Replace `vault._load_sync()` + `_credentials.get` with `CredentialProvider().get_provider_credential("google", "api_key")`.

### 2.4 `orchestrator.py` (Google 8-account sharding)
**Before:**
```python
vault = VaultCore(); vault._load_sync()
google_creds = [c for c in vault._credentials.values() if c.provider.value == "google"]
keys = [c.encrypted_blob for c in google_creds]
```
**After:**
```python
provider = CredentialProvider()
google_creds = provider.list_credentials(provider="google")  # returns all google accounts
keys = [provider.get_provider_credential("google", c["account_id"]) for c in google_creds]
```
`CredentialProvider.list_credentials(provider=...)` MUST support a provider filter (add to v2 interface — currently `list_credentials()` returns all; add optional `provider` param). **This is a new interface requirement not in R2 E-1 — add it.**

### 2.5 `model_gateway.py` (Carmack's finding)
- **Remove** `_load_sovereign_secrets()` call at line 127 and the method (lines 316-341).
- Provider factory (`_create_openrouter`, `_create_antigravity`, etc.) currently reads `cfg.get("api_keys", [])` from `providers.yaml`. **Two options (pick one):**
  - **(A) Minimal**: Leave providers.yaml `env:XXX_API_KEY` resolution as-is (providers read `os.environ` at creation). `CredentialProvider` ALSO reads `OMEGA_<PROVIDER>_<ACCOUNT>_API_KEY` env (R2 E-1 step 3). **Conflict**: providers.yaml uses `OPENROUTER_API_KEY`; CredentialProvider expects `OMEGA_OPENROUTER_1_API_KEY`. → **Must standardize env-var names** (see §3).
  - **(B) Full**: Strip `api_keys` from `providers.yaml`; have `generate()` inject the key at call time via `get_provider_credential()`. Requires provider objects to accept a key at request time (refactor `OpenAICompatProvider` to not hold keys). **Larger change — recommend (A) for debut, (B) post-debut.**

### 2.6 `antigravity_provider.py` (VERIFY)
Confirm whether it imports `VaultCore`. Grep found no `from omega.vault import`, but line 66 references "vault-first chain." If it uses env only, no change. **Action: Ma'at to grep-verify on Day 1 before `git rm`.**

---

## 3. `providers.yaml` Reconciliation (closes G-β, G-γ)

**Decision**: For debut, **keep `env:XXX_API_KEY`** in `providers.yaml` (Option A above). Standardize the env-var name to match what `CredentialProvider` reads AND what users set:

| Current (`providers.yaml`) | New canonical | Set by |
|----------------------------|---------------|--------|
| `env:OPENROUTER_API_KEY` | `OMEGA_OPENROUTER_1_API_KEY` | user shell / `omega secrets import` writes to keyring+env |
| `env:GOOGLE_API_KEY` | `OMEGA_GOOGLE_API_KEY` | same |
| `env:ANTIGRAVITY_API_KEY` | `OMEGA_ANTIGRAVITY_1_API_KEY` | same |
| `env:ANTHROPIC_API_KEY` | `OMEGA_ANTHROPIC_1_API_KEY` | same |
| `env:XAI_API_KEY` | `OMEGA_XAI_1_API_KEY` | same |

**Note**: `CredentialProvider` env resolution (`OMEGA_{PROVIDER}_{ACCOUNT}_API_KEY`) and the `providers.yaml` `env:` prefix must agree. Either (a) update `providers.yaml` to the `OMEGA_` names, or (b) make the provider factory also try the bare `XXX_API_KEY` name as a fallback. **Recommend (a) + document the exact env names in `PUBLIC_ALLOWLIST`-adjacent setup docs.**

---

## 4. Corrected Deletion Plan (supersedes Part 4 "Files to Modify")

### ADD to "Files to Modify":
| File | Change |
|------|--------|
| `src/omega/oracle/search_providers.py` | Replace `VaultCore` → `CredentialProvider` (§2.1) |
| `src/omega/oracle/providers.py` | Replace `VaultCore` → `CredentialProvider` (§2.2) |
| `src/omega/oracle/backends/google_compat.py` | Replace `VaultCore` → `CredentialProvider` (§2.3) |
| `src/omega/oracle/orchestrator.py` | Replace `VaultCore` → `CredentialProvider` + `list_credentials(provider=)` (§2.4) |
| `src/omega/oracle/backends/antigravity_provider.py` | VERIFY; fix if VaultCore import present (§2.6) |
| `config/providers.yaml` | Standardize `env:` names to `OMEGA_` convention (§3) |
| `src/omega/security/credential_provider.py` | **ADD** `list_credentials(provider: str = None)` param (§2.4 requirement) |

### KEEP from original "Files to Modify":
`model_gateway.py` (remove `_load_sovereign_secrets`), `types.py`, `rbac.py`, `pyproject.toml`, `cli/__init__.py`, `session_end.py`.

### Deletion command (unchanged):
```bash
git rm -r src/omega/vault/ scripts/vault_import.py src/omega/cli/vault.py
# VERIFY zero remaining references:
rg -n "from omega.vault|VaultCore|vault\._credentials" src/omega/ --type py
# Must return ONLY the new CredentialProvider usages above.
```

---

## 5. Open Questions / Remaining (track, don't block)

1. **Old VaultCore data**: No auto-migration path. Debut = single operator re-imports via `omega secrets import`. Acceptable; document.
2. **`list_credentials(provider=)`**: New interface param — add to R2 E-1 `CredentialProvider` before Day 1.
3. **antigravity_provider.py**: Verify VaultCore usage before `git rm`.
4. **Option A vs B** for `model_gateway.py` (§2.5): Pick A for debut.
5. **`encrypted_blob` → plaintext**: `CredentialProvider` returns plaintext (decryption internal). Callers no longer touch `.encrypted_blob`. Confirm no caller expects the blob object.

---

## 6. Verification Gate (add to R3 E-11 Day-4 checklist)

- [ ] `rg -n "from omega.vault|VaultCore|vault\._credentials" src/omega/` → zero matches
- [ ] `omega talk "hello"` (native-gguf) works WITHOUT any vault import (INST-1 acceptance)
- [ ] `omega secrets get openrouter_1` returns key via CredentialProvider
- [ ] Firecrawl/Exa/Google search providers resolve keys via CredentialProvider (no ImportError)
- [ ] Orchestrator Google 8-account sharding still receives all keys via `list_credentials(provider="google")`

---

*⬡ OMEGA ⬡ KALI ⬡ hy3-free ⬡ opencode ⬡ trc_vault_migration ⬡ 2026-08-18*
