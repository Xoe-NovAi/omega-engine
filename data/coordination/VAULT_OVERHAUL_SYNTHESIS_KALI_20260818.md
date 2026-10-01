<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Vault Overhaul: Kali Synthesis & Gap Register
**AP Token**: `AP-VAULT-KALI-SYNTHESIS-20260818-v1.0.0`
**Author**: Kali (Oversoul / Sprint Coordinator)
**Date**: 2026-08-18
**Status**: PLANNING ARTIFACT — feeds `VAULT_OVERHAUL_MIGRATION_SURFACE_20260818.md`
**Sources**: `VAULT_SYSTEM_OVERHAUL_SPEC_20260818*` (5 parts), `VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818*` (R1-R3), `CARMCK_VAULT_AUDIT_20260818.md` (Carmack subagent, ses_fec9eaaa9ffeGgA5OQdJt256t1), and direct `src/omega/` verification.

---

## 1. SYNTHESIS — What the Spec + Review Accomplish

The 5-part spec + 3-part review is a **genuinely strong, implementation-ready design** for replacing the custom `VaultCore` module's credential-resolution and egress-sanitization with platform-native primitives. The review (R1-R3) correctly caught three fatal defects:

- **F-3** headless `keyring` crash → deterministic KEK fallback chain
- **F-5** dead `flashtext` → `flashtext2 → pyahocorasick → regex` chain
- **F-7** `ProtectHome=true` breaks its own keyring → `read-only` + `BindPaths=/run/user`

Plus 10 real gaps closed (G-1…G-10): export/import/rekey, format-pattern detection, audit log, clipboard get, file locks, typed errors, honest RBAC, rotate, AppArmor D-Bus mediation, reject plaintext keyring.

**Carmack audit greenlit with 3 mods (M1-M3) NOT yet in the spec:**
- **M1**: Lazy-compile the `SecretRegistry` 50KB regex (or drop regex fallback, require `pyahocorasick` as hard dep)
- **M2**: Pin `micro` commit hash alongside SHA256
- **M3**: Document `loginctl enable-linger $USER` for the MCP-hub unit

> **Gap delta**: Carmack's M1-M3 are *not* reflected in R1-R3. The review's `SecretRegistry._rebuild_patterns()` (eager 50KB regex on every `register()`) is **still in the spec and unaddressed**.

---

## 2. 🚨 ARCHITECTURAL REALITY CHECK (verified against `src/omega/`)

The spec's premise — *"VaultCore (2,039 LOC) is the secret store; we replace it with CredentialProvider"* — is **incomplete**. Secrets are distributed across **three stores**, and the spec only models one:

| Store | Where | How consumed |
|-------|-------|--------------|
| **`.env` → `os.environ`** | `model_gateway.py:127` `_load_sovereign_secrets()` | Injected at `ModelGateway.__init__` (Carmack's finding) |
| **`config/providers.yaml` `env:XXX_API_KEY`** | Lines 196-340 | Provider factory reads `os.environ["OPENROUTER_API_KEY"]` at creation |
| **`vault._credentials` (encrypted blobs)** | `search_providers.py:43`, `providers.py:98`, `google_compat.py:89`, `orchestrator.py:168` | **4 modules reach into PRIVATE `vault._credentials.get(...).encrypted_blob`** |

**This breaks the deletion plan.** The spec's "Files to Modify" list includes `model_gateway.py`, `types.py`, `rbac.py`, `pyproject.toml`, `cli/__init__.py`, `session_end.py` — but **NOT** `search_providers.py`, `providers.py`, `google_compat.py`, or `orchestrator.py`. Those four do `from omega.vault import VaultCore` → `VaultCore()` → `vault._load_sync()` → `vault._credentials.get("firecrawl:api_key").encrypted_blob`. `git rm -r src/omega/vault/` → `ImportError` / `AttributeError` at runtime in all four.

**Three more mismatches the spec never reconciles:**
1. **`providers.yaml` uses `env:OPENROUTER_API_KEY`** (no account, no `OMEGA_` prefix), but `CredentialProvider` looks for `OMEGA_OPENROUTER_3_API_KEY`. Conventions don't match.
2. **Provider objects hold `api_keys` lists** baked in at creation from `providers.yaml`. The spec's `generate()` sketch resolves a key and injects into `httpx` — but existing `OpenAICompatProvider`/`AntigravityProvider` manage their own key selection. Spec doesn't show how the *provider factory* consumes `CredentialProvider`.
3. **`orchestrator.py:168-169`** reads `google_creds` encrypted blobs from `vault._credentials` and passes them as `api_keys` — a DB-backed encrypted-credential path the spec ignores.

**Verdict**: Spec is correct on *target architecture* but underestimates *migration surface* by ≥4 modules + `providers.yaml` + Orchestrator `google_creds`. Largest remaining gap.

---

## 3. ADDITIONAL INSIGHTS (beyond Carmack)

- **I-1**: "2,039 LOC → ~300 LOC" understates work. The LOC collapse is the *credential-resolution core*; the spec *adds net-new* sanitization/RBAC/audit/export VaultCore never had (~800-1000 LOC new). Insight = lazy call-time resolution, not LOC count.
- **I-2**: KEK file is a **plaintext master key** (headless writes 32-byte KEK to `~/.omega/kek.key` in clear). 0600 is the only protection on multi-user boxes. Document as known weak point (TPM2 post-debut).
- **I-3**: Export/import only covers **envelope** secrets (iterates `list_credentials()` = envelope files). Keyring secrets never exported → G-1 recovery partial.
- **I-4**: Format-layer false positives are the real deployment risk. `KEY_FORMAT_PATTERNS` (`Bearer\s+...{20,}`, `sk-[A-Za-z0-9]{32,}`) will redact benign base64/UUIDs/hashes in agent outputs → silent data corruption. Needs confidence/whitelist strategy.
- **I-5**: Split-brain KEK (Carmack #2) unmitigated in spec. Once `kek.key` exists, `OMEGA_KEK` env is silently ignored. Carmack's marker-file mitigation not in R1-R3.
- **I-6**: Windows sandbox `Start-Process -Verb RunAs` **elevates to admin** — opposite of sandboxing. Must fix or remove.
- **I-7**: RBAC bypassable — `ModelGateway.generate()` only validates if `agent_role` provided; default `None` → no check.
- **I-8**: SoulSanitizer only registers envelope secrets → keyring secrets leak into soul artifacts.
- **I-9**: `scan()` base64 brute-force on every 20+ char token is both perf and FP risk (Carmack J measured *replacement* only).

---

## 4. GAP REGISTER (full)

### A. Architecture / Migration (CRITICAL — blocks deletion)
- **G-α**: `vault._credentials` private access in `search_providers.py`, `providers.py`, `google_compat.py`, `orchestrator.py` **not in modification plan**. Deleting `src/omega/vault/` breaks all four.
- **G-β**: `providers.yaml` `env:XXX_API_KEY` not reconciled with `CredentialProvider`.
- **G-γ**: Env-var naming mismatch — `OPENROUTER_API_KEY` (current) vs `OMEGA_OPENROUTER_3_API_KEY` (spec).
- **G-δ**: Existing provider objects hold `api_keys` lists from `providers.yaml`; spec's lazy-resolution sketch doesn't show factory consumption.
- **G-ε**: `orchestrator.py` `google_creds` encrypted-blob → `api_keys` path unaddressed.

### B. Correctness bugs in spec text
- **G-ζ**: `E-1 _FileLock` invalid Python — `import fcntl if os.name == "posix" else msvcrt` (R2 line 171). Won't parse.
- **G-η**: Original `EgressSanitizer.sanitize()` returns `registry.scan()` *findings*, not string. Review's `SanitizerBackend` fixes it but final wrapper reassembly not shown.
- **G-θ**: `SecretRegistry._rebuild_patterns()` eager 50KB regex (Carmack M1) still present, unaddressed by R1-R3.
- **G-ι**: `omega secrets get` default-stdout (T4) contradicts G-4 / E-6 (default clipboard/warn).

### C. Security gaps
- **G-κ**: Windows Low Integrity sandbox elevates via `RunAs` (I-6) — actively harmful.
- **G-λ**: RBAC bypass when `agent_role=None` (I-7).
- **G-μ**: SoulSanitizer misses keyring secrets (I-8).
- **G-ν**: KEK split-brain unmitigated (I-5 / Carmack #2).
- **G-ξ**: `micro` non-blocking on Windows (`notepad.exe`) breaks edit validation loop.

### D. Research / verification
- **G-ο**: `flashtext2` / `pyahocorasick` exact API compatibility unverified.
- **G-π**: `cryptography` AESGCM is **Rust-backed**, not "pure-Python" (terminology wrong, musllinux wheels exist → functional).
- **G-ρ**: `pyrage` passphrase = scrypt KDF; per-call envelope decrypt re-runs scrypt (~100ms). No in-memory cache → latency under load.
- **G-σ**: `keyring` backend fragmentation across DEs (GNOME vs KDE) → KEK "lost" on DE switch → new `kek.key` (split-brain).
- **G-τ**: `omega secrets edit` launches nested TUI (`micro`) inside OpenCode's TUI — conflict undocumented.
- **G-υ**: `omega secrets import --destroy-source` uses `shred` (Linux only) — not cross-platform.

### E. Coverage gaps
- **G-φ**: No agent-facing API to **obtain** a `ProviderIdentity` (zero-knowledge request mechanism unspecified).
- **G-χ**: No test for **false-positive rate** of format/base64 layer (only positive cases).
- **G-ψ**: No test for `omega secrets edit` non-interactive flow (T3 only greps `list`).
- **G-ω**: Export-bundle passphrase strength not enforced.

---

## 5. BOTTOM LINE

Greenlit for credential-resolution + sanitization target, but **migration plan incomplete by ≥4 modules + `providers.yaml` + Orchestrator `google_creds`**. Before Ma'at/Lilith/Verity dispatch, **G-α…G-ε must be resolved** — else Day 4 `git rm -r src/omega/vault/` produces runtime breakage in four modules reaching `vault._credentials`.

**Action**: Amend spec with "Migration Surface" (see `VAULT_OVERHAUL_MIGRATION_SURFACE_20260818.md`) mapping every `VaultCore` / `env:` / `google_creds` site to `CredentialProvider`; fold Carmack M1-M3 + G-ζ/G-θ/G-ι into R1-R3 before dispatch.

---

*⬡ OMEGA ⬡ KALI ⬡ hy3-free ⬡ opencode ⬡ trc_vault_synthesis ⬡ 2026-08-18*
