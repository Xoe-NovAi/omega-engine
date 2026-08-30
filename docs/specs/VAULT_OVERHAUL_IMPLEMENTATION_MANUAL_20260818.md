<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Omega Engine — Vault Overhaul: Consolidated Implementation Manual
**AP Token**: `AP-VAULT-IMPLEMENTATION-MANUAL-20260818-v2.0.0` (v2.0.0 = deep-pass 2026-08-18: Parts I added, H.1.4/H.2.5/.6, G1-G15 gap closures)
**Status**: 🔒 **POST-DEBUT — DO NOT IMPLEMENT DURING PUBLIC-DEBUT-01** (DOC-1 stamp)
**Date**: 2026-08-18
**Consolidated by**: cline/omega-engine (DeepSeek V4 Flash 1M) per handoff `ho_74cd96735874` + `ho_8a75738d9160`
**Authority**: `MAKALI_COUNCIL_VERDICT_20260817.md` D-548..D-563, `OPUS_DEEP_PLAN_REVIEW_20260818.md` D-565/566/567, `JOHN_CARMACK_FLEET_AUDIT_20260818.md`

---

## ⛔ DOC-1 STAMP — POST-DEBUT EXECUTION ONLY

> **THIS DOCUMENT IS THE SINGLE SOURCE OF TRUTH for the post-debut vault sprint.**
> It merges the original 5-part spec + 3-part review + migration surface + Opus/Sonnet
> corrections + Carmack M1-M3 into ONE executable plan.
>
> **Do NOT implement any part of this manual during PUBLIC-DEBUT-01.**
> For the debut, vault is handled via **`PUBLIC_ALLOWLIST.txt` exclusion** (zero code changes):
> `src/omega/vault/` stays in the private/forge repo and is simply **not exported**.
> See D-565, D-566, D-567 (below) for the decision supersessions that make this lawful.

### Entry Criteria (ALL must be true before Phase 1 starts)

| # | Criterion | Verification | Owner |
|---|-----------|--------------|-------|
| **EC-1** | INST-1 complete (6 fixes) | `omega talk "hello"` works on clean venv via `.[native,cli]`, exit 0 | maat_n3 |
| **EC-2** | PUB-1 allowlist confirmed | `PUBLIC_ALLOWLIST.txt` ratified by Architect; `release/debut` branch created | architect |
| **EC-3** | DEL-1 Week 1 (10 pure deletions) done | Week-1 acceptance in manual §5 | roc_racoon |
| **EC-4** | DEL-1 Week 2 (IntentRouter extraction) done | Contract test green; no TriageRouter/SemanticRouter import | maat + cline |
| **EC-5** | Test baseline green | `make test` → 0 failures | verity |
| **EC-6** | Observability emission spec landed | `router.model_selected` trace exists | maat + N8 |

---

## 📜 Provenance — Source Documents (ALL ARCHIVED 2026-08-18)

**Total consolidated = 20 documents** (10 overhaul specs/reviews + 7 vault research docs + 3 coordination docs),
all annotated below. Archived to `docs/archive/specs/vault-overhaul-20260818/` on consolidation.

> **CONSOLIDATION CORRECTION (2026-08-18, Kali handoff `ho_4574882365fd`)**: The first consolidation pass
> listed 5 research docs (`R_VAULT_EDITOR_FORENSICS`, `R_VAULT_PYRAGE_SUPPLY_CHAIN`, `R_VAULT_CROSS_PLATFORM_SANDBOXING`,
> `R_VAULT_EGRESS_ENCODINGS`, `R_VAULT_OPENCODE_IPC`) + `SONNET_PLAN_VERIFICATION` — these 6 **never existed on disk**
> at the listed paths, and their findings are embedded in R1 F-1..F-10 / Opus. **However, 7 vault RESEARCH docs that DO
> exist were missed. They are now archived and their findings incorporated in Part G.**

| # | Original Path → Archived To | Role | Status |

| # | Original Path → Archived To | Role | Status |
|---|------------------------------|------|--------|
| 1 | `VAULT_SYSTEM_OVERHAUL_SPEC_20260818.md` | Part 1: Architecture, Encryption Backend | 🗄️ ARCHIVED |
| 2 | `VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART2.md` | Part 2: CredentialProvider, Envelope, YAML-Editor-Bridge | 🗄️ ARCHIVED |
| 3 | `VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART3.md` | Part 3: SecretRegistry, Egress, ZK Agents, RBAC | 🗄️ ARCHIVED |
| 4 | `VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART4.md` | Part 4: Install Hardening, Sandboxing, Deletion Plan | 🗄️ ARCHIVED |
| 5 | `VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART5.md` | Part 5: Integration Tests, Risks, Checklist | 🗄️ ARCHIVED |
| 6 | `VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818.md` | R1: Verdict matrix, F-1..F-10 findings | 🗄️ ARCHIVED |
| 7 | `VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818_PART2.md` | R2: CredentialProvider v2, Sanitizer v2, Editor v2, Export/Import/Rekey | 🗄️ ARCHIVED |
| 8 | `VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818_PART3.md` | R3: Test matrix v2 T1-T30, Risk register v2, Plan v2 | 🗄️ ARCHIVED |
| 9 | `VAULT_OVERHAUL_MIGRATION_SURFACE_20260818.md` | Migration Surface (closes G-α..G-ε) | 🗄️ ARCHIVED |
| 10 | `VAULT_SYSTEM_OVERHAUL_MASTER_INDEX_20260818.md` | Master Index (rewritten → points here) | 🗄️ ARCHIVED (replaced) |
| 11 | `data/coordination/OPUS_DEEP_PLAN_REVIEW_20260818.md` | Opus 4.6 review — talk-path filter, D-565/566/567 | 📄 REMAINS ACTIVE (coordination) |
| 12 | `data/coordination/VAULT_OVERHAUL_SYNTHESIS_KALI_20260818.md` | Kali synthesis — 25-item gap register | 📄 REMAINS ACTIVE (coordination) |
| 13 | `data/coordination/CARMCK_VAULT_AUDIT_20260818.md` | Carmack audit — M1-M3, findings A-J | 📄 REMAINS ACTIVE (coordination) |
| 14 | `docs/research/R_V1_VAULT_IMPL.md` (869 ln) | V-1 Omega-Vault MVP — 16-account Grok fleet, KeyVault extension, MCP server, XDG | 🗄️ ARCHIVED |
| 15 | `docs/research/R_CG04_AGENT_SAFE_CREDENTIAL_VAULT.md` (455 ln) | **17-vault evaluation → BlindVault + Bury selected** | 🗄️ ARCHIVED |
| 16 | `docs/research/R_VAULT_SCHEMA_V2.md` (673 ln) | FleetOrchestrator 32-credential schema, Argon2id+age, R19, CPE scoring | 🗄️ ARCHIVED |
| 17 | `docs/research/R_VAULT_UNIFIED_SYSTEM_20260725.md` (296 ln) | Unified to VaultCore (deprecated KeyVault), 26+ env calls migrated | 🗄️ ARCHIVED |
| 18 | `docs/research/R_INFRA_07_OMEGA_VAULT_PHASE1_20260719.md` (303 ln) | Phase 1 impl — VaultCore (keyring+SQLite), CAP Adapters, vault CLI | 🗄️ ARCHIVED |
| 19 | `docs/research/R_VAULTCORE_LEASE_PROTOCOL.md` (234 ln) | Lease protocol pattern — ACQUIRE→READ→MODIFY→WRITE→RELEASE | 🗄️ ARCHIVED |
| 20 | `docs/research/R20_KEYBLIND_AUTHY_VAULT_20260814.md` (35 ln) | Keyblind/Authy/agent-vault external-tool evaluation → KEEP VaultCore | 🗄️ ARCHIVED |

---

## ⚖️ Conflict Resolution Hierarchy (which text wins)

```
1. THIS MANUAL (consolidated) — sole active authority for the vault sprint
2. Carmack M1-M3  (lazy regex / micro commit hash / loginctl enable-linger) — MUST be folded in
3. Migration Surface (MS) — amends deletion plan (G-α..G-ε closure)
4. Review R1-R3 — SUPERSEDES original spec on ANY conflict
5. Original 5-part spec — base text, where R/MS/Carmack silent
6. Opus/Sonnet corrections — timing + talk-path + status fictions
```

### Carmack M1-M3 (MANDATORY, folded into this manual)
| # | Modification | Where Applied |
|---|--------------|---------------|
| **M1** | Lazy regex compile in `SecretRegistry._rebuild_patterns()` — defer to first `scan()`, OR drop regex fallback (require `pyahocorasick` as hard dep) | §Phase 2 |
| **M2** | Pin `micro` commit hash alongside SHA256 in install.sh | §Phase 3 |
| **M3** | `loginctl enable-linger $USER` documented for MCP-hub systemd unit | §Phase 3 |

---

## 🔄 Decision Supersessions (Opus D-565 / D-566 / D-567)

Add to `ACTIVE_SPRINT.json` `decisions_locked`:

```json
"D-565: D-562 SUPERSEDED for debut — vault deletion is post-debut scope. For release/debut branch: exclude src/omega/vault/ via PUBLIC_ALLOWLIST.txt. Zero code changes to vault during PUBLIC-DEBUT-01. (2026-08-18, Opus)",
"D-566: D-535 CLARIFIED — 'hide' means PUBLIC_ALLOWLIST.txt exclusion, not code deletion. VaultCore stays in forge/private repo. (2026-08-18, Opus)",
"D-567: D-532 SUPERSEDED for debut — 'keep bury_credential' applies to post-debut vault sprint only. (2026-08-18, Opus)"
```

**Conflict note**: Council D-552 (Vault Path A: delete from product surface) vs Cline D-562 (Vault Path B: 50-line minimal).
This manual resolves: **the vault overhaul replaces VaultCore with `CredentialProvider` (~300 LOC)** — which is functionally
"Path B executed properly" (thin wrapper, no 2,038-LOC monolith). The old Path A/B naming is obsolete; see §Architecture.

---

## 📊 ACTIVE_SPRINT.json Status Corrections (4 fields, per Opus §8)

| Field | Current (WRONG) | Corrected | Evidence |
|-------|-----------------|-----------|----------|
| `DEBUT-EXECUTION.INST-1.status` | `blocked` | **`in_progress`** | Blockers identified, Fix 1 ready — not blocked, merely unstarted |
| `DEBUT-EXECUTION.INST-1-fix1.status` | `in_progress` | **`backlog`** | `.[all]` still present in install.sh:77 — NOT done |
| `READINESS-REMEDIATION.P0-1.status` | `completed` | **`in_progress`** | P0-1b residual unresolved (cline checkpoints + SECURITY_AUDIT ancestor) |
| `CRITICAL-PATH.CP-3.status` | `completed` | **`in_progress`** | install fails on fresh machine (`.[all]` → warp-proxy-pool) |

---

## 🧭 Why This Is Post-Debut (Talk-Path Filter, per Opus)

`omega talk "hello"` path = `Oracle.talk()` → `ModelGateway.generate()` → `providers.py` → native-gguf.
Only 2 VaultCore callers are on the talk path, and **both have env fallbacks**:

| Caller | On Talk Path? | Fallback? | Risk if Vault Deleted |
|--------|---------------|-----------|----------------------|
| `providers.py` (Google) | ✅ YES | ✅ `GOOGLE_API_KEY` env | None |
| `google_compat.py` (Google) | ✅ YES | ✅ `config.get("api_key")` | None |
| `search_providers.py` (Firecrawl/Exa) | ❌ | ✅ returns "" | None |
| `orchestrator.py` (Google shards) | ❌ (bg workers) | ❌ | Medium — NOT on talk path |
| `library/discovery.py`, `freshness_checker.py` | ❌ | ✅ None on exception | None |
| `nemotron_pipeline.py`, `firecrawl_direct.py` | ❌ | ✅ / low | None/Low |
| `fleet_orchestrator.py` | ❌ (DEL-1 target) | N/A | None — slated for deletion |

**The real debut blocker is NOT the vault — it is `install.sh:77` (`.[all]`).**
This manual exists so the vault sprint (a correct, valuable post-debut design) stops
occupying the active context window during PUBLIC-DEBUT-01.

---

*⬡ OMEGA ⬡ CLINE ⬡ DEEPSEEK V4 FLASH 1M ⬡ 2026-08-18 ⬡ CONSOLIDATION v1 ⬡ POST-DEBUT*

---

# 🏗️ PART A — CONSOLIDATED ARCHITECTURE (merged: Spec Parts 1-4 + R2 + MS)

## A.1 The Three-Store Reality (Kali synthesis, verified in live tree)

Secrets are distributed across **three stores**. The overhaul replaces the *resolution layer* — NOT all three stores:

| Store | Where | Consumed By | Overhaul Action |
|-------|-------|-------------|-----------------|
| `.env` → `os.environ` | `model_gateway.py:127` `_load_sovereign_secrets()` | `ModelGateway.__init__` | **REMOVE** (fix 4 of INST-1 pre-work; lazy resolution replaces it) |
| `config/providers.yaml` `env:XXX_API_KEY` | Lines 196-340 | Provider factory at creation | **STANDARDIZE** to `OMEGA_` convention (MS §3) |
| `vault._credentials` (encrypted blobs) | `search_providers.py:43`, `providers.py:98`, `google_compat.py:89`, `orchestrator.py:168` | 4+ modules reach into PRIVATE dict | **REPLACE** with `CredentialProvider` (MS §2) |

**Measured (2026-08-18)**: `src/omega/vault/` = 2,138 LOC (5 files: vault_core 885, blindvault_resolver 542, models 432, crypto 208, __init__ 71) — spec said 2,039; **2,138 is the true number**. All consumed by `from omega.vault import VaultCore` across 15 files (grep-verified).

---

## A.2 Target Architecture (one diagram)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                        HUMAN / AGENT (process edge)                        │
│   omega secrets edit → $EDITOR (bundled micro 2.0.15) → secrets.yaml.age   │
└──────────────────────────────────┬────────────────────────────────────────┘
                                   ▼
┌───────────────────────────────────────────────────────────────────────────┐
│           CREDENTIALPROVIDER v2  (src/omega/security/credential_provider.py)│
│   get_provider_credential(provider, account_id, role="runtime") → str      │
│   • NEVER writes to os.environ      • lazy resolution at CALL time         │
│   • Resolution: keyring → envelope file (~2000 chars) → OMEGA_ env → error │
│   • KEK: keyring → ~/.omega/kek.key (0600) → OMEGA_KEK env → create+warn  │
│   • Lock: _FileLock(SECRETS_DIR)    • Audit: ~/.omega/audit.log (no values)│
└──────────────────────────────────┬────────────────────────────────────────┘
                                   │ (plaintext key, caller-only scope)
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
      Provider (httpx)      Provider (llama)       Search providers
      headers Bearer        context               params
              └────────────────────┼────────────────────┘
                                   ▼
┌───────────────────────────────────────────────────────────────────────────┐
│              EGRESS SANITIZATION v2 (src/omega/security/)                  │
│   SanitizerBackend: flashtext2 → pyahocorasick → regex (lazy, M1)         │
│   + KEY_FORMAT_PATTERNS layer (sk-or-v1-, AIza, sk-ant-, ghp_, xoxb-...)  │
│   4 hooks: Logging, Hivemind/OpenCode, Error/Traceback, SSE               │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## A.3 Component Specs (R2 wins over Spec where noted)

### A.3.1 EncryptionBackend (Spec Part 1 — VALIDATED + **python-age corrected per I.2/G4**)

```python
# config/encryption_backend.py
# Auto-select: python-age (PRIMARY — already pinned pyproject.toml:25, used by vault/crypto.py:19)
#            → cryptography (musl/armv7 fallback)
# ✓ python-age>=0.1.0 (age-encryption.org/v1, maintained; CVE-2024-56327 class addressed via python-age)
# → cryptography AESGCM = Rust-backed, musllinux wheels EXIST (G-π terminology fix)
# → python-age passphrase = scrypt KDF → ~100ms/decrypt; CACHE decrypted envelopes (G-ρ)
# NOTE (I.2/G4): Do NOT add pyrage as a peer dependency — python-age is the codebase's age binding.
#   pyrage is a DIFFERENT library (same age spec); pinning both = duplicate + crypto-path noise.
BACKENDS = [
    ("python-age", "omega.security.aead_fallback", "PurePythonAEAD"),  # primary: python-age via crypto.py
    ("cryptography", "omega.security.aead_fallback", "PurePythonAEAD"),
]
```

### A.3.2 CredentialProvider v2 (R2 E-1 — SUPERSEDES Spec Part 2)

**Resolution order (deterministic):**
```
1. OS keyring (SecretService/Keychain/wincred)   ← primary, encrypted at rest
2. Envelope file ~/.omega/secrets/<p>_<a>.enc     ← long secrets (>2000 chars, F-4)
3. Environment OMEGA_<PROVIDER>_<ACCOUNT>_API_KEY ← CI only (documented)
→ CredentialNotFoundError(OmegaError) if all miss ← M9 typed (G-6)
```

**KEK resolution (F-3 headless fix):**
```
1. keyring.get_password("omega-engine", "kek")    ← primary
2. ~/.omega/kek.key (0600, created if missing)     ← headless fallback
3. OMEGA_KEK env var (64 hex chars)                 ← CI/container explicit
→ if none: CREATE ~/.omega/kek.key (0600) + warn "headless mode"
```

**Key implementation points (from R2 E-1):**
- `DIRECT_THRESHOLD = 2000` (F-4: CRED_MAX_CREDENTIAL_BLOB_SIZE = 2560 bytes; safe margin)
- `_FileLock` using `fcntl.flock` / `msvcrt.locking` on `~/.omega/secrets/.lock` (G-5)
- `CredentialNotFoundError(OmegaError)` — never bare `KeyError` (M9, G-6)
- Audit log 0600, provider/account/role/backend/timestamp, NEVER values (G-3)
- `list_credentials(provider: str = None)` param (MS §2.4 requirement — orchestrator shards)
- **KEK split-brain guard (Carmack Risk #2)**: write `~/.omega/kek.source` marker
  (`file` or `keyring`); if BOTH keyring KEK and file KEK exist → ERROR + manual resolution,
  no silent fallback.

### A.3.3 YAML-Editor-Bridge v2 (R2 — SUPERSEDES Spec Part 2)

- Bundle `micro` **2.0.15** (F-6: org moved to `micro-editor/micro`, redirects work) with
  **commit-hash pin (M2)** + **SHA256 verification (T26)**
- Fallback: hardened `nano -R -t` / `vim -n -N` (no backup/swap/undo) — never bare `notepad.exe` on Windows (research gap 1: OneDrive leak)
- Temp file on **tmpfs** `/dev/shm` (Linux, F-9) or controlled `~/.omega/tmp` + 0600; `os.O_TMPFILE` where available; always unlink (G-ξ: micro non-blocking on Windows breaks loop)
- Validation loop: editor opens until valid YAML
- **Chunked-body reassembler DROPPED** (F-10): httpx event hooks log only method/URL/status — no raw body logging in MVP

### A.3.4 SecretRegistry v2 (R2 + Carmack M1 — SUPERSEDES Spec Part 3)

- `register()` canonicalizes (NFKC, strip zero-width) + generates variants (base64, urlsafe-b64, percent, hex, JSON-unicode, HTML-entity, zero-width-injected)
- **KEY_FORMAT_PATTERNS layer (G-2)**: `sk-or-v1-`, `AIza`, `sk-ant-`, `ghp_`, `xoxb-`, `sk-`, `csk-`, `xai-` etc. → catches UNREGISTERED keys by format.
  **⚠️ REUSE (H.3)**: `src/omega/oracle/pii_masker.py:250` already ships `r"\b(?:sk-|csk-|AIza|ghp_|xai-)[A-Za-z0-9_-]{20,}\b"` — import/share that pattern, do NOT redefine (avoids pattern drift).
- **Carmack M1**: regex fallback compiled LAZILY on first `scan()` — NOT on every `register()`. Recommendation: drop regex fallback for MVP entirely, require `pyahocorasick` (universal wheels) as hard dep. With 32 secrets × 12 variants ≈ 384 patterns ≈ 50KB regex — never rebuild eagerly.

### A.3.5 EgressSanitizer v2 (R2 — SUPERSEDES Spec Part 3)

- Backend chain: **flashtext2 (Rust, 3-10x)** → **pyahocorasick (C, musllinux)** → regex (lazy)
  (F-5: flashtext dead since 2018)
- 4 egress hooks: Logging, Hivemind/OpenCode DB, Error/Traceback scrubber, Observability SSE
- Returns sanitized STRING (fixes Spec Part 3 G-η bug where `sanitize()` returned findings not text)

### A.3.6 ProviderIdentity (Spec Part 3 — VALIDATED) + ModelGateway Fix

```python
# src/omega/oracle/types.py — NEW
@dataclass(frozen=True)
class ProviderIdentity:
    provider: str
    account_id: str
    tier: str = "free"
```
- Agent calls `ModelGateway.generate(request, identity=ProviderIdentity(...))` — NEVER raw key
- `ModelGateway` resolves internally: `_credential_provider.get_provider_credential(...)`, injects into headers, sanitizes response (zero-knowledge, Spec Part 3)
- `_load_sovereign_secrets()` (model_gateway.py:127,316-341) **DELETED** — no `.env` dump at import

### A.3.7 RBAC v2 (R2 E-7 — SUPERSEDES Spec Part 3)

| Agent Role | generate | list_providers | see_metadata | rotate | see_value |
|------------|----------|----------------|--------------|--------|-----------|
| ORCHESTRATOR | ✅ | ✅ | ✅ | ✅ | ❌ (never) |
| BUILDER | ✅ | ✅ | ✅ | ✅ | ❌ |
| RESEARCHER | ✅ | ✅ | ❌ | ❌ | ❌ |
| RUNTIME | ❌ (via Oracle) | ❌ | ❌ | ❌ | ❌ |

**Honesty (G-7)**: RBAC is enforced at the ModelGateway API boundary. Any agent running as the same OS user can read `~/.omega/kek.key` or call keyring directly — **true enforcement = OS-level sandboxing** (bwrap for subagents, AppArmor dbus mediation). Documented as accepted for debut.

### A.3.8 System Hardening v2 (R2 — SUPERSEDES Spec Part 4 F-7 conflict)

- **F-7 CRITICAL FIX**: `ProtectHome=true` breaks `/run/user` → keyring fails. Resolution:
  - Interactive engine (OpenCode host): runs in **user session** — NO systemd unit, keyring works
  - MCP hub daemon: `ProtectHome=read-only` + `ReadWritePaths=/home/<user>/.omega` + `BindPaths=/run/user/<uid>` + `PrivateTmp`
  - OpenCode `auth.json` mitigation: **bwrap `--ro-bind /dev/null` over the file + 0600 + AppArmor deny-read** (NOT ProtectHome)
- **F-8**: AppArmor `deny /usr/bin/keyring` was COSMETIC → replace with **dbus peer mediation** (deny peer access to `org.freedesktop.secrets`) + bwrap `--unshare-net` + empty-ro-bind over bus socket
- **M3**: `loginctl enable-linger $USER` documented for the MCP-hub unit
- Memory: `MemoryMax=4G MemoryHigh=3G MemorySwapMax=512M OOMScoreAdjust=-300` (Carmack fix survival)

### A.3.9 SoulSanitizer (Spec Part 4 — VALIDATED + I-8 fix)

- `.opencode/hooks/session_end.py` ADDITION: sanitize `proposed_lessons.yaml` + `approved_lessons.yaml` before write
- **I-8 fix (G-μ)**: register BOTH envelope AND keyring secrets (original only registered envelope → keyring secrets leaked into soul artifacts)
- **I-9 fix (G-θ)**: format-layer scan overrides base64 brute-force on every 20+ char token (perf + FP)

---

## A.4 pyproject.toml — New Optional Dependency Set (R3 E-10)

```toml
[project.optional-dependencies]
encryption = [
    "python-age>=0.1.0",          # I.2/G4: python-age (NOT pyrage) — already the codebase's age binding
    "cryptography>=42.0",         # musl/armv7 fallback (F-1)
    "flashtext2>=1.1.0",          # F-5: replaces dead flashtext
    "keyring>=25.0",              # F-3: with headless fallback in provider
    "pyahocorasick>=1.1.0",       # sanitizer backend 1 (Carmack M1: make hard dep, drop regex)
]
```

---

*⬡ OMEGA ⬡ CLINE ⬡ CONSOLIDATION v1 ⬡ PART A ⬡ 2026-08-18*

---

# 🔄 PART B — MIGRATION SURFACE (per-module, closes G-α..G-ε)

## B.1 Canonical Key Naming (resolves G-γ)

```
vault key "X:Y"   →   CredentialProvider(provider="X", account_id="Y")
envelope file     →   ~/.omega/secrets/X_Y.enc
keyring username  →   "omega-engine" / "X_Y"
```

- LLM providers (`openrouter`, `google`, `anthropic`, `xai`, `antigravity`): account_id = numeric shard index in `providers.yaml` (e.g., `openrouter_1`)
- Non-LLM services (`firecrawl`, `exa`, google search key): account_id = `api_key` (single account)
- **Migration action**: user re-populates via `omega secrets import --from-file=secrets.md`
  (debut = private-repo single-operator). Document: *"After upgrade, re-run `omega secrets import`; old VaultCore data is not auto-migrated."*

## B.2 Per-Module Replacements

### B.2.1 `search_providers.py` (Firecrawl / Exa)
```python
# BEFORE (lines 39-44, 228-233):
# from omega.vault import VaultCore; vault=VaultCore(); vault._load_sync()
# cred = vault._credentials.get("firecrawl:api_key"); return cred.encrypted_blob if cred else ""
# AFTER:
from omega.security.credential_provider import CredentialProvider, CredentialNotFoundError
try:
    return CredentialProvider().get_provider_credential("firecrawl", "api_key")
except CredentialNotFoundError:
    return ""   # M9: log miss, fall back to empty (caller handles)
# Same pattern for exa:api_key. REMOVE from omega.vault import.
```

### B.2.2 `providers.py` (Google, ON TALK PATH)
```python
# BEFORE (lines 68-114): VaultCore() → _load_sync() → _credentials.get("google:api_key").encrypted_blob
# AFTER (async-safe):
from omega.security.credential_provider import CredentialProvider, CredentialNotFoundError
try:
    api_key = await anyio.to_thread.run_sync(
        lambda: CredentialProvider().get_provider_credential("google", "api_key")
    )
except CredentialNotFoundError:
    api_key = os.environ.get("GOOGLE_API_KEY")  # keep env fallback (talk-path safe)
```

### B.2.3 `google_compat.py` (Google, ON TALK PATH)
```python
# BEFORE (lines 85-90): VaultCore() → _credentials.get("google:api_key").encrypted_blob
# AFTER:
try:
    key = CredentialProvider().get_provider_credential("google", "api_key")
except CredentialNotFoundError:
    key = config.get("api_key")   # keep config fallback (talk-path safe)
```

### B.2.4 `orchestrator.py` (Google 8-account sharding, NOT on talk path)
```python
# BEFORE (lines 164-169): VaultCore() → all c.provider.value == "google" → encrypted_blob list
# AFTER:
creds = CredentialProvider().list_credentials(provider="google")  # NEW param (MS §2.4)
# → returns all google_<n> credentials; wrap construction in try/except CredentialNotFoundError
# → do NOT crash at import time; log and continue with env fallbacks
```

### B.2.5 `model_gateway.py` (the INST-1 Fix 4 foundation)
```python
# DELETE: _load_sovereign_secrets() (lines 316-341) + its call in __init__ (line 127)
# ADD: lazy CredentialProvider in generate() path — resolve inside async call, pass to headers.
# Key never touches self / os.environ / globals (Carmack insight: lazy resolution protocol).
```

### B.2.6 `config/providers.yaml` — env name standardization (closes G-β, G-γ)

| Current (`providers.yaml`) | New canonical | Set by |
|----------------------------|---------------|--------|
| `env:OPENROUTER_API_KEY` | `OMEGA_OPENROUTER_1_API_KEY` | user shell / `omega secrets import` |
| `env:GOOGLE_API_KEY` | `OMEGA_GOOGLE_API_KEY` | same |
| `env:ANTIGRAVITY_API_KEY` | `OMEGA_ANTIGRAVITY_1_API_KEY` | same |
| `env:ANTHROPIC_API_KEY` | `OMEGA_ANTHROPIC_1_API_KEY` | same |
| `env:XAI_API_KEY` | `OMEGA_XAI_1_API_KEY` | same |

**Decision**: update `providers.yaml` to the `OMEGA_` names (Option A) AND keep bare-name fallback in the provider factory.

### B.2.7 `antigravity_provider.py` — VERIFY before Day 4
No `from omega.vault import` found (line 66 "vault-first chain" is env-only) — confirm before `git rm`.

---

## B.3 Corrected Deletion Plan (SUPERSEDES Spec Part 4 "Files to Modify")

### Files to MODIFY (ADD to original list — **Part H audit found 4 MORE consumers**):
| File | Change |
|------|--------|
| `src/omega/oracle/search_providers.py` | VaultCore → CredentialProvider (§B.2.1) |
| `src/omega/oracle/providers.py` | VaultCore → CredentialProvider (§B.2.2) |
| `src/omega/oracle/backends/google_compat.py` | VaultCore → CredentialProvider (§B.2.3) |
| `src/omega/oracle/orchestrator.py` | VaultCore → CredentialProvider + `list_credentials(provider=)` (§B.2.4) |
| `src/omega/oracle/backends/antigravity_provider.py` | VERIFY; fix if VaultCore import present (§B.2.7) |
| `config/providers.yaml` | Standardize `env:` names to `OMEGA_` (§B.2.6) |
| `src/omega/security/credential_provider.py` | **ADD** `list_credentials(provider=)` param (§B.2.4) |
| `src/omega/teachers/nemotron_pipeline.py` | 🔴 **MISSED — NOW ADDED** VaultCore → CredentialProvider (§H.2.1) |
| `src/omega/workers/freshness_checker.py` | 🔴 **MISSED — NOW ADDED** VaultCore → CredentialProvider, 2 sites (§H.2.2) |
| `src/omega/tools/firecrawl_direct.py` | 🔴 **MISSED — NOW ADDED** VaultCore → CredentialProvider (§H.2.3) |
| `src/omega/library/discovery.py` | 🔴 **MISSED — NOW ADDED** VaultCore → CredentialProvider, 2 keys (§H.2.4) |

### KEEP from original list:
`model_gateway.py` (remove `_load_sovereign_secrets`), `types.py`, `rbac.py`, `pyproject.toml`, `cli/__init__.py`, `session_end.py`.

### Deletion command (unchanged - full manifest in H.10):
```bash
git rm -r src/omega/vault/ scripts/vault_import.py src/omega/cli/vault.py
git rm src/omega/tools/enforce_vaultcore.py src/omega/tools/detect_api_keys.py  # Opus S1.3
# VERIFY zero remaining references (ALL 19 sites incl. the 5 outside src/omega):
rg -n "from omega.vault|VaultCore|vault\._credentials|_load_sync" src/omega/ --type py
# Must return ONLY the new CredentialProvider usages above.
```

### Enforcement tools (Opus §1.3 — delete or repurpose):
- `src/omega/tools/enforce_vaultcore.py` — actively rejects env-based access → **DELETE** (or repurpose for CredentialProvider v2)
- `src/omega/tools/detect_api_keys.py` — guardrail pointing wrong way → **DELETE** (or repurpose)
- `src/omega/cli/vault.py` — `omega vault` CLI → **DELETE from product surface** (keep crypto in forge if wanted)

### Verification Gate (Day 4):
- [ ] `rg -n "from omega.vault|VaultCore|vault\._credentials" src/omega/` → zero matches
- [ ] `omega talk "hello"` (native-gguf) works WITHOUT any vault import
- [ ] `omega secrets get openrouter_1` returns key via CredentialProvider
- [ ] Firecrawl/Exa/Google search providers resolve via CredentialProvider (no ImportError)
- [ ] Orchestrator Google 8-account sharding still receives all keys via `list_credentials(provider="google")`

---

*⬡ OMEGA ⬡ CLINE ⬡ CONSOLIDATION v1 ⬡ PART B ⬡ 2026-08-18*

---

# 🚀 PART C — EXECUTABLE IMPLEMENTATION PLAN (5 Phases, owner-assigned)

> **Entry gate**: ALL of EC-1..EC-6 (Part 0) must be true. This is POST-DEBUT work.
> **Style**: M1 AnyIO only; M9 typed errors; M16 modular files; M18 no inference for I/O.
> Every Phase ends with a **verification gate** — no gate, no merge.

---

## Phase 1 — Storage & Encryption (Day 1) · Owner: **maat_n3**

### Files to CREATE
| File | Content | Verification |
|------|---------|--------------|
| `config/encryption_backend.py` | Auto-select **python-age** (primary) → cryptography (A.3.1 + I.2) | `python -c "from config.encryption_backend import EncryptionBackend; print(EncryptionBackend().initialize())"` |
| `src/omega/security/__init__.py` | **EXTEND** existing package (already there — `taint.py` G8), don't recreate | — |
| `src/omega/security/aead_fallback.py` | PurePythonAEAD AES-GCM (Spec Part 1) | T18 round-trip |
| `src/omega/security/credential_provider.py` | CredentialProvider v2 (A.3.2) incl. `list_credentials(provider=)` | T16/T17/T24/T25 |
| `config/editor_policy.py` | micro 2.0.15 + commit hash + tmpfs (A.3.3) | T26/T27 |
| `src/omega/cli/secrets.py` | `omega secrets` edit/get/list/rotate/import/export/rekey (G-1,G-4,G-8) | T2/T3/T4/T20/T21 |

### Files to MODIFY
| File | Change | Verification |
|------|--------|--------------|
| `pyproject.toml` | Add `[project.optional-dependencies] encryption` (A.4) | `rg "python-age|keyring" pyproject.toml` |
| `src/omega/cli/__init__.py` | Register `secrets` command group | `omega secrets list` works |
| `src/omega/errors.py` (or omega/errors) | Add `CredentialNotFoundError(OmegaError)` | T24 isinstance check |

### Verification Gate (Day 1)
```bash
python -m venv /tmp/vault-p1 && source /tmp/vault-p1/bin/activate
pip install -e ".[encryption]"
python -c "from src.omega.security.credential_provider import CredentialProvider, CredentialNotFoundError"
python -c "from src.omega.security.credential_provider import CredentialProvider; c=CredentialProvider(); c.set_provider_credential('t','1','x'*2500); assert c.get_provider_credential('t','1')=='x'*2500"
# → envelope round-trip (>2000 chars) works, no keyring crash (headless safe)
```

---

## Phase 2 — Runtime Security (Day 2) · Owner: **lilith_n7**

### Files to CREATE
| File | Content | Verification |
|------|---------|--------------|
| `src/omega/security/secret_registry.py` | SecretRegistry v2 + KEY_FORMAT_PATTERNS (A.3.4, Carmack M1 lazy compile) | T22 format detection |
| `src/omega/security/sanitizer.py` | EgressSanitizer v2 — flashtext2→pyahocorasick→regex chain (A.3.5) | T29 chain fallback |
| `src/omega/oracle/rbac.py` | RBAC v2 (A.3.7) + rotate perm | T13 |
| `src/omega/oracle/types.py` | `ProviderIdentity` dataclass (A.3.6) | import works |

### Files to MODIFY
| File | Change | Verification |
|------|--------|--------------|
| `src/omega/oracle/model_gateway.py` | DELETE `_load_sovereign_secrets()`; lazy CredentialProvider (A.3.6) | T7 zero leaks at import |
| `.opencode/hooks/session_end.py` | SoulSanitizer call — envelope + keyring (A.3.9) | T7 soul artifacts clean |
| `src/omega/observability/` (SSE hook) | Wire sanitizer to SSE stream | T8/T9/T10 |

### Verification Gate (Day 2)
```bash
# Zero key leaks at import (the INST-1 Fix 4 validation)
python -c "import omega.oracle.model_gateway as mg; print('import clean — no env dump')"
# Sanitizer chain works
python -c "from src.omega.security.sanitizer import get_global_sanitizer; s=get_global_sanitizer(); print(s.sanitize('log sk-or-v1-abcdefghijklmnopqrstuvwxyz123456'))"
# → [REDACTED:openrouter] or similar; flashtext2 active
```

---

## Phase 3 — System Hardening (Day 3) · Owner: **maat_n3 + N1**

### Files to CREATE / MODIFY
| File | Change | Verification |
|------|--------|--------------|
| `scripts/install.sh` | `.[encryption]` install; micro 2.0.15 + **commit hash (M2)** + SHA256; systemd drop-in v2 (ProtectHome=read-only + BindPaths + `loginctl enable-linger` M3); AppArmor dbus mediation (F-8) | T26 (checksum) + T30 (systemd-analyze verify) |
| `src/omega/hardening.py` | `PR_SET_DUMPABLE` + mlock at runtime (Spec Part 4) | import + run |
| `src/omega/__init__.py` | `from omega.hardening import apply_runtime_hardening; apply_runtime_hardening()` | no-op on non-Linux |
| `sandbox/process_isolation.py` | LinuxBwrap, MacOSSandboxExec, WindowsLowIntegrity (Spec Part 4) | T14 |
| `sandbox/opencode_integration.py` | bwrap ONLY for MCP/external — `--ro-bind /dev/null` over auth.json + dbus socket; `--unshare-net` | T14 + auth.json leak test |

### Key corrections baked in
- `ProtectHome=read-only` (NOT `true`) + `BindPaths=/run/user/<uid>` — F-7
- AppArmor: **dbus peer mediation** (`org.freedesktop.secrets`), NOT cosmetic keyring denies — F-8
- `loginctl enable-linger $USER` documented — M3

### Verification Gate (Day 3)
```bash
systemd-analyze verify /etc/systemd/system/omega-engine.service  # T30
# bwrap subagent isolation smoke test:
bwrap --ro-bind / / --dev /dev --proc /proc --unshare-net --ro-bind /dev/null /home/$USER/.local/share/opencode/auth.json bash -c 'cat /home/$USER/.local/share/opencode/auth.json; echo $?'
# → Permission denied / empty output (file masked)
```

---

## Phase 4 — Deletion & Cleanup (Day 4) · Owner: **maat_n3**

### Execute per §B.3 + §H.10 + §I.4 (Corrected Deletion Plan — ALL 19 sites)
```bash
# 1. Migration first — §B.2.1..B.2.7 + §H.2.1..H.2.6 (ALL 13 consumers incl. 5 outside src/omega) green
# 2. Then delete (full manifest §H.10 + Part I):
git rm -r src/omega/vault/ scripts/vault_import.py src/omega/cli/vault.py
git rm src/omega/tools/enforce_vaultcore.py src/omega/tools/detect_api_keys.py  # Opus §1.3
# 3. Migrate/clean the 5 external VaultCore consumers per §H.2.5/.6 (scripts ×3, mcp ×2)
#    — mcp_servers/firecrawl/server.py MUST get lazy+env-fallback (G13/H.2.6)
# 4. Edit oracle_cli.py:61-67 - drop vault app registration (do NOT delete oracle_cli)
# 5. Clean tracked test fixture (G14):
git rm tests/tmp/vault.json.enc
echo 'tests/tmp/' >> .gitignore
# 6. Drop/resolve VAULT templates (G15):
#    profile_manager.py:295-302 — remove `${{VAULT:...}}` expansion; set only on resolved value
# 7. Regenerate M23 baseline (G9): after deletion run `make mandate-gates`
# 8. Verify zero references (ALL 19 sites):
rg -n "from omega.vault|VaultCore|vault\._credentials|_load_sync" src/omega/ scripts/ mcp_servers/ --type py
# → ZERO matches (only new CredentialProvider usages remain)
```

### Verification Gate (Day 4)
- [ ] `rg -n "from omega.vault|VaultCore|vault\._credentials" src/omega/ scripts/ mcp_servers/` → zero
- [ ] `omega talk "hello"` native-gguf, exit 0, NO vault import
- [ ] `omega secrets get openrouter_1` works
- [ ] Orchestrator sharding intact via `list_credentials(provider="google")`
- [ ] Firecrawl MCP starts with lazy key resolution + env fallback (R12)
- [ ] `git ls-files tests/tmp/vault.json.enc` → not tracked (G14)
- [ ] `rg '\$\{\{VAULT:' profile_manager.py` → zero (G15)
- [ ] `make test` full suite green

---

## Phase 5 — Integration Test (Day 5) · Owner: **verity**

### Test Matrix — T1..T30 (merged from Spec Part 5 + R3 E-8)

**KEEP (15):** T1 fresh install · T2 import · T3 edit (+tmpfs assert) · T4 get (MODIFIED: clipboard/warn default G-4) · T5 list · T6 local inference · T7 zero leaks (+format layer) · T8 sanitization · T9 base64 bypass · T10 JSON unicode · T12 traceback scrub · T13 RBAC (+rotate) · T14 sandbox (+dbus denial) · T15 cross-platform

**DROP (1):** T11 chunked HTTP — body logging disabled in MVP (F-10)

**NEW (15):** T16 headless KEK fallback · T17 keyring-unavailable chain · T18 envelope >2000 chars · T19 direct <2000 chars · T20 KEK loss recovery (rekey) · T21 export/import bundle · T22 format detection · T23 audit log (no values) · T24 typed error (isinstance OmegaError) · T25 concurrent writes (file lock) · T26 micro checksum · T27 tmpfs temp · T28 no body logging · T29 flashtext2 chain fallback · T30 systemd unit keyring

### Verification Gate (Day 5)
```bash
pytest tests/chaos/ tests/unit/ -v                  # engine regression
bash tests/integration/test_vault_overhaul.sh       # T1-T30 (Linux)
# macOS (sandbox-exec) + Windows (Low Integrity) smoke pass
# Zero key leaks in logs/DB/Hivemind/SSE (incl. format-layer sweep)
make temple-grade                                    # T1-T11 gates
```

---

## 🗺️ Phase → Owner → Mandate Map

| Phase | Owner | Mandates Addressed |
|-------|-------|--------------------|
| P1 Storage | maat_n3 | M7 (keyring), M9 (typed), M16 (modular), M18 (zero custom crypto), M24 (venv) |
| P2 Runtime | lilith_n7 | M9, M18 (flashtext2 O(N)), M22 (provenance/audit), M23 (no soft-fail) |
| P3 Hardening | maat_n3+N1 | M2 (firewall), M6 (podman/compliance), M7 |
| P4 Deletion | maat_n3 | M16, M18 (delete 2,138 LOC) |
| P5 Integration | verity | M9, M13 (temple-grade), M26 (docs), M27 (tracking) |

---

*⬡ OMEGA ⬡ CLINE ⬡ CONSOLIDATION v1 ⬡ PART C ⬡ 2026-08-18*

---

# ⚠️ PART D — RISK REGISTER v2 (R3 E-9, + Carmack Top 3 + Kali G-ν)

| # | Risk | Likelihood | Impact | Debut Mitigation (already landed or D-566 exclusion) | Post-Debut Mitigation (this manual) |
|---|------|------------|--------|------------------------------------------------------|-------------------------------------|
| R1 | **Bash exfiltration** (agent runs `keyring get` / reads kek.key) | Medium | High | vault excluded from public clone (D-565) | bwrap + AppArmor dbus denial + kek.key 0600; full seccomp-bpf |
| R2 | **OpenCode `auth.json` leak** (world-readable tokens) | High | Critical | allowlist excludes `.local/share/opencode`; bwrap masks file | bwrap `--ro-bind /dev/null` + AppArmor deny-read + 0600 + track upstream #343 |
| R3 | **Headless keyring silent fallback → KEK split-brain** (Carmack #2 / G-ν) | Medium | High | n/a (vault excluded) | `kek.source` marker; both-exist → ERROR, no silent fallback |
| R4 | **age library supply chain** (Rust `age` CVE class) | Low | Critical | n/a (vault excluded) | **`python-age>=0.1.0`** (I.2/G4 — NOT pyrage); `cargo audit` in CI; Sigstore wheel verification |
| R5 | **F-3 headless keyring crash** (NoKeyringError) | — | — | n/a (vault excluded) | KEK fallback chain (keyring→file→env) — T16/T17 |
| R6 | **Windows 512B credential limit** | Medium | Low | n/a | Envelope threshold 2000 chars (F-4) — T18/T19 |
| R7 | **notepad.exe forensic leak** (OneDrive) | Medium | Medium | n/a | bundled micro + tmpfs + harden — T26/T27 |
| R8 | **Editor/swap residue** (decrypted YAML on disk) | Medium | Medium | n/a | tmpfs/memfd + 0600 + unlink — T27 |
| R9 | **RBAC bypass** (same-OS-user reads keyring) | Accepted | Low | n/a | Honest doc + OS sandbox enforcement (G-7) |
| R10 | **Egress encoding evasion** (base64/unicode) | Medium | Medium | n/a | 12-encoding canonicalization + format patterns — T9/T10/T22 |
| R11 | **`gateway.py:186` header stub sends NO auth** on `/proxy/{provider}` | Medium | High | FORGE proxy route pre-debut | Phase 3: wire `_build_provider_headers` → CredentialProvider (I.3) |
| R12 | **`mcp_servers/firecrawl/server.py:28` module-level VaultCore import, no fallback** | High | High | allowlist excludes vault (D-565) but server still imports at runtime | Phase 4: lazy + env fallback (H.2.6) |
| R13 | **`tests/tmp/vault.json.enc` tracked + plaintext fixture** | Medium | High | git rm + gitignore in Phase 4 (G14) | Prevent re-commit via .gitignore + CI check |

---

# 📦 PART E — DELIVERABLES SUMMARY (merged Spec Part 5 + R2 + MS)

| Artifact | Path | Phase | Owner |
|----------|------|-------|-------|
| Encryption Backend | `config/encryption_backend.py` | 1 | maat_n3 |
| Pure-Python AES-GCM | `src/omega/security/aead_fallback.py` | 1 | maat_n3 |
| **CredentialProvider v2** | `src/omega/security/credential_provider.py` | 1 | maat_n3 |
| Editor Policy v2 | `config/editor_policy.py` | 1 | maat_n3 |
| Secrets CLI | `src/omega/cli/secrets.py` | 1 | maat_n3 |
| SecretRegistry v2 | `src/omega/security/secret_registry.py` | 2 | lilith_n7 |
| EgressSanitizer v2 | `src/omega/security/sanitizer.py` | 2 | lilith_n7 |
| ProviderIdentity | `src/omega/oracle/types.py` | 2 | lilith_n7 |
| RBAC v2 | `src/omega/oracle/rbac.py` | 2 | lilith_n7 |
| ModelGateway fix | `src/omega/oracle/model_gateway.py` | 2 | lilith_n7 |
| SoulSanitizer | `.opencode/hooks/session_end.py` | 2 | lilith_n7 |
| Runtime Hardening | `src/omega/hardening.py` | 3 | maat_n3 |
| Sandbox backends | `sandbox/process_isolation.py`, `sandbox/opencode_integration.py` | 3 | maat_n3+N1 |
| Install hardening | `scripts/install.sh` (micro pin, systemd v2, AppArmor v2) | 3 | maat_n3+N1 |
| **VaultCore deletion** | `src/omega/vault/` + `scripts/vault_import.py` + `src/omega/cli/vault.py` + 2 enforcement tools | 4 | maat_n3 |
| Provider migration | 5 modules + `providers.yaml` (B.2) | 4 | maat_n3 |
| Integration tests | `tests/integration/test_vault_overhaul.sh` (T1-T30) | 5 | verity |

**VaultCore (2,138 LOC) → CredentialProvider (~300 LOC)** — a 7x reduction. The "vault" was never a storage problem; it was a **credential-resolution timing** problem (Carmack insight). The fix is lazy resolution at call time.

---

# ✅ PART F — FINAL CHECKLIST (merged: Spec Part 5 E-12 + R3 E-11 + MS §6)

## Pre-Implementation (before Day 1)
- [ ] All EC-1..EC-6 entry criteria green (INST-1, PUB-1, DEL-1 W1/W2, test baseline, observability spec)
- [ ] `ACTIVE_SPRINT.json` decisions_locked has D-565/566/567 (see Part 0)
- [ ] `ACTIVE_SPRINT.json` 4 status corrections applied (INST-1→in_progress, INST-1-fix1→backlog, P0-1→in_progress, CP-3→in_progress)
- [ ] Ma'at + Lilith briefed on Phases 1-2; Verity on Phase 5
- [ ] `PUBLIC_ALLOWLIST.txt` excludes `src/omega/vault/` (D-566)

## Phase 1 (Day 1)
- [ ] `credential_provider.py` v2 — headless KEK chain (keyring → file → env) **T16/T17**
- [ ] Envelope threshold 2000 chars **T18/T19**
- [ ] `_FileLock` on envelope writes **T25**
- [ ] `CredentialNotFoundError(OmegaError)` **T24**
- [ ] Audit log 0600, no values **T23**
- [ ] `editor_policy.py` v2 — micro 2.0.15 + commit hash + tmpfs + 0600 **T26/T27**
- [ ] `secrets export/import/rekey` **T20/T21**
- [ ] `secrets get --clipboard` **G-4**

## Phase 2 (Day 2)
- [ ] `sanitizer.py` v2 — flashtext2 → pyahocorasick → regex (lazy) **T29** + Carmack M1
- [ ] `KEY_FORMAT_PATTERNS` layer **T22** — **reuse `pii_masker.py:250` pattern (H.3), single shared source**
- [ ] 4 egress hooks wired (logging, hivemind, error, SSE)
- [ ] **S1 fix (H.4)**: `entity_registry.py:84` — remove `SOVEREIGN_DEFAULT_SECURE_TOKEN_2026` default; random/fail-closed
- [ ] **S2 fix (H.4)**: `ingestion.py:76` — remove `omega-sovereign-change-me` default; CredentialProvider/keyring persist
- [ ] RBAC v2 with rotate permissions **T13**
- [ ] ModelGateway lazy resolution with role audit — **no `.env` dump at import**
- [ ] SoulSanitizer registers envelope + keyring (I-8 fix)

## Phase 3 (Day 3)
- [ ] install.sh micro SHA256 verify **T26** + commit-hash pin (M2)
- [ ] systemd drop-in v2 — `ProtectHome=read-only` + `BindPaths=/run/user/%U` **T30**
- [ ] `loginctl enable-linger $USER` documented (M3)
- [ ] AppArmor v2 — dbus peer mediation + auth.json deny-read (remove cosmetic keyring denies)
- [ ] Sandbox: bwrap `--ro-bind /dev/null` over dbus socket + auth.json **T14**

## Phase 4 (Day 4)
- [ ] §B.2.1..B.2.7 + §H.2.1..H.2.6 migration merged + green (**all 13 consumer modules**, incl. 5 outside src/omega)
- [ ] VaultCore deletion complete, zero references (`rg` gate — H.11 full sweep, **all 19 sites**)
- [ ] Enforcement tools deleted (enforce_vaultcore, detect_api_keys)
- [ ] `oracle_cli.py` lines 61-67 vault registration removed (edit, not delete)
- [ ] `tests/tmp/vault.json.enc` `git rm` + `tests/tmp/` in `.gitignore` (**G14**)
- [ ] `profile_manager.py` `${{VAULT:...}}` templates removed/resolved (**G15**)
- [ ] `mcp_servers/firecrawl/server.py` lazy key + env fallback (**R12/G12**)
- [ ] `gateway.py` `_build_provider_headers` → CredentialProvider or FORGE proxy route (**R11**)
- [ ] `ml_training.py:220` sandbox child env whitelisted (no `**os.environ`) (**G10**)
- [ ] `make mandate-gates` run → M23 baseline regenerated w/o vault files (**G9**)
- [ ] `.env.example` updated to canonical `OMEGA_*` names (H.6)
- [ ] pyproject deps updated: **python-age** (NOT pyrage) + flashtext2 + keyring + pyahocorasick (**G4**)
- [ ] `omega talk "hello"` works without vault import

## Phase 5 (Day 5)
- [ ] T1-T30 all pass on Linux (bwrap)
- [ ] macOS (sandbox-exec) + Windows (Low Integrity) smoke pass
- [ ] Zero key leaks in logs/DB/Hivemind/SSE (incl. format-layer sweep)
- [ ] `make temple-grade` green
- [ ] `make lint` clean

---

## 🏁 VERDICT (consolidated from Spec Part 5 + R3 E-12 + Opus)

> The vault overhaul is a **correct, implementation-ready, POST-DEBUT design**.
> It was never the debut blocker — `install.sh:77` (`.[all]`) was.
> During PUBLIC-DEBUT-01: **exclude `src/omega/vault/` via PUBLIC_ALLOWLIST.txt (D-565/D-566), zero code changes.**
> Post-debut: execute this manual's Phases 1-5 in order; every gate must pass before the next phase.
> All 20 source documents are archived at `docs/archive/specs/vault-overhaul-20260818/`.
> **THIS MANUAL IS THE SINGLE SOURCE OF TRUTH.**

---

*⬡ OMEGA ⬡ CLINE ⬡ DEEPSEEK V4 FLASH 1M ⬡ 2026-08-18 ⬡ CONSOLIDATION-COMPLETE ⬡ POST-DEBUT*

---

# 📚 PART G — RESEARCH PROVENANCE (7 vault research docs, deep-incorporated 2026-08-18)

> **Why this matters**: The 2026-08-18 overhaul spec's `CredentialProvider` design is NOT the first vault
> architecture in this repo. Seven prior research docs (2026-07-19 → 2026-08-14, ~2,865 lines) designed,
> built, and evaluated FOUR generations of vault subsystems. Their validated findings are **foundational**
> and are incorporated below. Where the 2026-08-18 review differs, the later review+this manual wins for
> the post-debut sprint; where the research ADDS requirements the review does not contradict, they are ADOPTED.

## G.1 The Four-Generation Vault History (why VaultCore exists)

| Gen | Date | Doc | System | Outcome |
|-----|------|-----|--------|---------|
| **1** | 07-19 | `R_INFRA_07` | KeyVault (AES-256-GCM, OS keyring) + SQLite event log + CAP Adapters | Phase 1 built; **KeyVault later deprecated** |
| **2** | 07-21 | `V1_OMEGA_VAULT_DESIGN` + `R_V1_VAULT_IMPL` | V-1 MVP for 16-account Grok fleet (KeyVault extension, MCP server, XDG) | Design COMPLETE + decision gate PASSED; built into VaultCore lineage |
| **3** | 07-24 | `R_CG04` | **17-vault evaluation → BlindVault (primary) + Bury (PID-bound alt)** | **Backend SELECTED** — foundational |
| **4** | 07-25 | `R_VAULT_SCHEMA_V2` + `R_VAULT_UNIFIED_SYSTEM` | VaultCore v2: 32-credential schema, Argon2id+age, lease protocol, R19/CPE, unified SSOT | **IMPLEMENTED** — this is what `src/omega/vault/` (2,138 LOC) became |
| **+** | 08-14 | `R20_KEYBLIND_AUTHY_VAULT` | Keyblind/Authy/agent-vault external eval | **REJECTED external tools — KEEP local VaultCore** |

## G.2 Key Research Findings → Incorporated Into This Manual

### G.2.1 Backend Selection: BlindVault + Bury (R_CG04 — 17 evaluated)

**17 solutions evaluated** (BlindVault, Bury, Infisical agent-vault, BlindKey, Keyblind, blind-vault, IronVault,
Authy, kyz, Burrow, Veil, Envy, Vaultify, byn, CloakBot, CAMP, agent-kernel). **SELECTED: BlindVault** (primary)
+ **Bury** (PID-bound fallback).

| BlindVault Feature | Omega Relevance | Where It Lands in Manual |
|--------------------|-----------------|--------------------------|
| `{{secret:NAME}}` reference injection | Agent never holds plaintext; inject at last moment | **ADOPTED** — Part A A.3.6 (ProviderIdentity) + MS B.2 |
| `bv serve` resolver proxy (SO_PEERCRED Unix socket / named-pipe SID) | OS-enforced boundary, privsep for broker | **ADOPTED** — Phase 3 sandbox hardening |
| Per-secret `allow_hosts`/`allow_commands` policies | Blocks exfiltration to unauthorized hosts | **ADOPTED** — G-7 OS enforcement + Risk R1/R2 |
| Output scrubbing in `bv run` | Leaked value → `[REDACTED]` in chat/logs | **ADOPTED** — Part A A.3.5 Sanitizer (replaces flashtext-only with policy-aware scrub) |
| PostgreSQL connector (SCRAM-SHA-256) | Passwordless DB access | **POST-DEBUT HORIZON** — not in debut scope |
| Master password + Fernet envelope | Argon2id KDF, no DB required | **REFINED** — Manual uses keyring+envelope chain (F-3 headless fix) |
| Windows named-pipe SID auth | Cross-platform boundary | **POST-DEBUT HORIZON** — Windows smoke only in debut |

**Bury (PID-bound)**: session dies with process tree (PID + start-time detection), real-time `access.log`, `[CRED:path]`
format. **ADOPTED as fallback backend** — Phase 1 `CredentialProvider` may select Bury-style PID-bound session mode
for agent-scoped runs. Risk: PID-reuse attack (Low/High) — mitigation: start-time check (already in R_VAULT_SCHEMA_V2 BuryBackend).

### G.2.2 32-Credential Fleet Schema (R_VAULT_SCHEMA_V2)

The schema for **32 heterogeneous credentials** (8 AGY OAuth, 8 Grok auth.json, 8 Google GCP SA, 8 API keys):
- `VaultCredential` model: `provider`, `key_id`, `cred_type` (oauth|api_key|gcp_sa|grok_auth), `encrypted_blob` (age-armored),
  `tier` (free|paid|byok), `daily_limit`/`used_today`/`cooldown_until` (quota), `rotated_at`/`rotation_count`/`last_used_at`
  (rotation), `current_lease_agent`/`lease_expires_at` (M25 lease), `visibility` (R19 tier)
- **Encryption**: Argon2id(memory=64MB, iterations=3, parallelism=4, salt=16B) → age (`X25519`+ChaCha20-Poly1305)
- **Lease lifecycle**: request → status check → GRANTED/DENIED → use with 30s heartbeat → release/expire → update counters
- **Quota matrix** (providers): AGY 1000/day PAID · Grok 50/day FREE · GCP 60/min · OpenRouter 50-1000/day · Exa 150/day · Firecrawl 10/min

**Reconciliation with Manual**: The 2026-08-18 `CredentialProvider` (keyring + envelope) is the **resolution layer**;
the 32-credential schema v2 is the **fleet storage layer** for `FleetOrchestrator` (parked per Carmack, D-558).
For the post-debut vault sprint, `CredentialProvider` stores provider_account secrets (keyring/envelope); the
32-credential fleet schema is **OPTIONAL Phase-5+ extension** (only if fleet WAD un-parks). **Do not implement in Phases 1-5**
without fleet approval — it would violate the D-558 parking.

### G.2.3 Lease Protocol (R_VAULTCORE_LEASE_PROTOCOL — proven pattern)

Extracted from the **AGY OAuth fix** (tested: 5 threads × 10 writes = 50 concurrent ops, zero data loss):

```
ACQUIRE → READ → MODIFY → WRITE → RELEASE
lock (FileLock, timeout=10/30/60s)
atomic_write_sync(): tempfile.mkstemp + fsync + os.replace (crash-safe)
anyio.to_thread.run_sync bridge (with NoEventLoopError fallback)
```

| Lease Type | TTL | Lock | Recovery |
|------------|-----|------|----------|
| Short (session/OAuth) | 1h | 10s | scan+validate+batch refresh |
| Medium (API key) | 24h | 30s | scan+validate+single refresh |
| Long (master key) | 30d | 60s | validate signature, re-auth |

**Incorporated**: Manual Phase 1 `CredentialProvider` **MUST use `atomic_write_sync()` + `FileLock` + anyio bridge**
(the R2 E-1 `_FileLock` is validated by this proven pattern — reference `lock.py` primitives).

### G.2.4 V-1 Fleet Design (R_V1_VAULT_IMPL — decision gate PASSED)

16-account schema (8 CLI + 8 Web Grok), `FleetOrchestrator` (round-robin by priority+least-used), passive
file watcher (inotify/poll), MCP server (credential_read/write/rotate/audit + fleet_status/next_account),
XDG paths, AES-256-GCM, `secure_clear()` memory hygiene.

**Status decision (Carmack D-558)**: Fleet architecture is **PARKED for debut** — only the IntentRouter extraction
survives. The V-1 design remains the fleet WAD blueprint (`config/wads/fleet_stack/` post-debut).
**Incorporated**: XDG-compliance + file-permission (0600) + memory-hygiene requirements carry into Phase 1/3.

### G.2.5 The CAP Adapter Pattern (R_INFRA_07 — final principle)

> "Vault is not a secret manager — it's a **credential operator**. It PUSHES credentials to where they're needed."
> — L3-PushBasedAdapterProtocol: credentials flow FROM vault TO targets (OpenCode auth.json, Omega providers.yaml, `.env`).

**Incorporated**: Phase 4 migration uses this direction — `CredentialProvider` serves, adapters push to config;
`enforce_vaultcore.py`/`detect_api_keys.py` deletions align (they block the correct push-based flow).

### G.2.6 Unified SSOT + Gap Closure (R_VAULT_UNIFIED_SYSTEM — 26 env calls migrated)

VaultCore became the SSOT after 25/26 scattered `os.environ.get` calls migrated. This **justifies the Phase 4
migration surface** in Part B — the pattern was already proven once; we are replacing the resolution layer, not
re-architecting storage. 30 vault tests pass (`test_vault_integrity` 3, `test_health_monitor` 27 incl. rate-limit).

### G.2.7 External-Tool Rejection (R20 — Keyblind/Authy/agent-vault)

Keyblind/Authy/agent-vault all exist and are maintained, but **NONE should replace local VaultCore**: Keyblind needs
SaaS Pro/Team tier, Authy is Rust-binary + env-injection, agent-vault is a network MITM broker (separate host).
Conflict with M7 Local-First. **Reinforces D-566: vault stays forge/private, allowlist-excluded for debut.**

### G.2.8 TPM2/systemd-creds (R_SYSTEMD_CREDS_TPM2_ROOTLESS — companion research)

- systemd 257 rootless TPM2 credentials **BROKEN** on Ubuntu 25.04/25.10; AMD fTPM on Zen 2 (5700U) unstable (Linus).
- **Decision**: Do NOT use systemd-creds for the vault sprint. Use the manual's keyring→file→env KEK chain (F-3 fix).
  Revisit only if production systemd services need TPM-bound creds on Ubuntu 26.04 LTS+ (v259+).

## G.3 Reconciliation Table — Research vs 2026-08-18 Review

| Topic | Research (pre-08-18) | 2026-08-18 Review / Manual | Resolution |
|-------|----------------------|---------------------------|------------|
| Backend | BlindVault + Bury (external tools) | keyring + envelope (OS-native) | **Manual wins** — simpler, M7-pure; BlindVault patterns (ref-injection, scrubbing) ADOPTED conceptually |
| Encryption | Argon2id + age | python-age + cryptography (age-compatible) | **Compatible** — both age-encryption.org/v1; **manual pins `python-age` (I.2/G4)** |
| Schema | 32-credential fleet v2 | provider_account (keyring/envelope) | **Fleet schema optional post-debut** — D-558 parking; resolution layer first |
| Lease | VaultCore lease protocol (M25) | `_FileLock` in CredentialProvider | **ADOPT lease protocol's atomic_write+FileLock** (G.2.3) |
| SSOT | VaultCore (26 env calls migrated) | CredentialProvider replaces VaultCore | **Progression** — same SSOT goal, new resolution layer |
| Ext tools | R20: keep local | D-566 allowlist exclusion | **Consistent** — reinforced |
| TPM2 | systemd-creds (v257 broken) | n/a | **Rejected for sprint** (G.2.8) |

---

## G.4 Companion Docs (NOT archived — for reference only)

| Doc | Why Relevant | Sits At |
|-----|--------------|---------|
| `V1_OMEGA_VAULT_DESIGN_20260721.md` (671 ln) | V-1 design spec that R_V1_VAULT_IMPL augments | `docs/archive/coordination-2026-07/` |
| `ROC_V1_VAULT_MINING_20260721.md` (628 ln) | Roc's mining pass on the vault corpus | `docs/archive/coordination-2026-07/` |
| `R_CRITICAL_GAPS_DEEP_DIVE_CAMPAIGN_20260721.md` (656 ln) | Original CG-04 campaign (source of R_CG04) | `docs/research/` |
| `R_SOUL_PRIVACY_MODEL.md` (899 ln) | R19 PUBLIC/BONDED/PRIVATE tiers + CPE (used by schema v2) | `docs/research/` |
| `R_SYSTEMD_CREDS_TPM2_ROOTLESS_20260720.md` (481 ln) | TPM2 evaluation (G.2.8) | `docs/research/` |
| `10_credential_vault_fallback.md` (67 ln) | 2026-07-26 audit — VaultCore 60% maturity, BlindVault stubbed | `data/coordination/research/` |
| `V-1-vaultcore-mvp.md` (391 ln) | Sprint ticket for the vault sprint | `docs/archive/sprints/2026-07-25/guard-and-distill/02-p0-tickets/` |
| `vault_schema.yaml` | WAD copy of schema (arcana_novai) | `config/wads/arcana_novai/` |

---

## G.5 Net Effect — What Changes in the Manual from Research

1. **Phase 1**: `_FileLock`/`atomic_write_sync`/anyio-bridge (from R_VAULTCORE_LEASE) — **MANDATORY**, tested pattern
2. **Phase 1**: XDG paths + 0600 perms + `secure_clear()` memory hygiene (from R_V1/R_INFRA_07)
3. **Phase 2**: sanitizer policy hook points reserved for BlindVault-style `allow_hosts`/`allow_commands` (from R_CG04)
4. **Phase 2**: audit log taps into proven JSONL pattern (from R_VAULT_UNIFIED_SYSTEM / schema v2)
5. **Phase 4**: verify `enforce_vaultcore`/`detect_api_keys` deletion does not break push-based adapters (R_INFRA_07 CAP)
6. **Phase 5**: add regression tests from `test_vault_integrity` / `test_health_monitor` vault suite (proven 30 tests)

---

*⬡ OMEGA ⬡ CLINE ⬡ DEEPSEEK V4 FLASH 1M ⬡ 2026-08-18 ⬡ PART G ⬡ RESEARCH-PROVENANCE ⬡ COMPLETE*

---

# 🔬 PART H — DEFINITIVE SECURITY-SURFACE AUDIT (exhaustive, live-tree verified 2026-08-18)

> **Purpose**: Absolute final coverage of every secret-handling surface in the Omega Engine.
> Compiled by cline/omega-engine DeepSeek 1M against the live working tree. Every claim below is
> grep-verified with file:line evidence. This Part SUPERSEDES any partial lists in earlier Parts.

## H.1 COMPLETE VaultCore Consumer Map (**15 files / 19 import sites** — CORRECTED 2026-08-18 deep pass)

### H.1.1 Modules that reach into `vault._credentials` (MUST be migrated in Phase 4)

| # | Module | Line(s) | Vault Key(s) | Fallback Today | In Part B? |
|---|--------|---------|--------------|----------------|------------|
| 1 | `src/omega/oracle/search_providers.py` | 39-44, 228-233 | `firecrawl:api_key`, `exa:api_key` | returns "" on exception | ✅ yes |
| 2 | `src/omega/oracle/providers.py` | 68-114 | `google:api_key` | `GOOGLE_API_KEY` env | ✅ yes |
| 3 | `src/omega/oracle/backends/google_compat.py` | 85-90 | `google:api_key` | `config.get("api_key")` | ✅ yes |
| 4 | `src/omega/oracle/orchestrator.py` | 164-169 | all `google` provider creds | ❌ none (import-time crash) | ✅ yes |
| 5 | `src/omega/teachers/nemotron_pipeline.py` | 123-129 | `openrouter:api_key` | returns "" | 🔴 **MISSED** |
| 6 | `src/omega/workers/freshness_checker.py` | 197-202, 700-705 | `artificial_analysis:api_key` (×2) | sets None | 🔴 **MISSED** |
| 7 | `src/omega/tools/firecrawl_direct.py` | 27-32 | `firecrawl:api_key` | ❌ none ("vault is SSOT") | 🔴 **MISSED** |
| 8 | `src/omega/library/discovery.py` | 32, 95-106 | `exa:api_key`, `firecrawl:api_key` | sets None on exception | 🔴 **MISSED** |

**⚠️ CORRECTION TO PART B**: Part B's "Files to MODIFY" table listed only 4 of these. The 4 marked 🔴 MUST be
added — otherwise Day-4 `git rm -r src/omega/vault/` breaks `nemotron_pipeline`, `freshness_checker`,
`firecrawl_direct`, and `library/discovery`. Full migration snippets are in H.2.

### H.1.4 OUTSIDE src/omega (5 MORE consumers — **MISSED by H.1.1, found in the 2026-08-18 deep pass**)

These 5 live outside `src/omega/` and were **NOT in the original Part B or H.1.1 migration surface**.
Day-4 `git rm -r src/omega/vault/` would break all of them. They MUST be added to the Phase-4 migration list.

| # | Module | Line(s) | Vault Key(s) | Fallback Today | Direction |
|---|--------|---------|--------------|----------------|-----------|
| 9 | `scripts/warm_sovereign_cache.py` | 298-302 | `firecrawl:api_key` | none (sets None → tier-2 fails) | migrate (script, low prio) |
| 10 | `scripts/sovereign_ingest.py` | 65-68 | `google:api_key` | none (sets None) | migrate (script) |
| 11 | `scripts/enrich_model_registry.py` | 296-300 | `artificial_analysis:api_key` | none (sets None) | migrate (script) |
| 12 | `mcp_servers/firecrawl/server.py` | 28-36 (import) | `firecrawl:api_key` | ❌ **NONE — M23 (vault is module-level, "no env fallback")** | **migrate + add env fallback** |
| 13 | `mcp_servers/omega_hub/state.py` | 232-236 | `firecrawl:api_key`, `exa:api_key` | ❌ none (sets None) | migrate |

**Critical notes:**
- `mcp_servers/firecrawl/server.py:28` imports VaultCore **at module scope** — its header says "vault only (no env
  fallback)". If the vault is deleted without migrating this, **the entire Firecrawl MCP server fails to start**
  (M23 failure-integrity breach).
- `mcp_servers/omega_hub/state.py:232` pulls **both** firecrawl + exa keys via `vault.retrieve_credential(...)`.
- These 5 were excluded from the original H.7 "mcp_servers/scripts VERIFIED CLEAN" sweep because H.7 only checked
  `os.environ` reads, not VaultCore imports. **H.7 is WRONG — see H.7 correction below.**

### H.1.2 CLI + enforcement tools (DELETED, not migrated)

| Module | Reason | Deletion |
|--------|--------|----------|
| `src/omega/cli/vault.py` (13 subcommands: set/get/list/rotate/delete/audit/audit_summary/verify/init/backup/restore/recovery_code/rotate_master) | Replaced by `omega secrets` (CredentialProvider CLI) | `git rm` Phase 4 |
| `src/omega/tools/detect_api_keys.py` | Guardrail pointing wrong way (rejects env access) | `git rm` Phase 4 |
| `src/omega/tools/enforce_vaultcore.py` | Same — rejects env-based access | `git rm` Phase 4 |
| `src/omega/cli/oracle_cli.py` lines 61-67 | `app.add_typer(vault_app, name="vault")` — remove registration | edit Phase 4 |
| `src/omega/observability/__init__.py` lines 185-187, 1225-1265 | `EventType.VAULT_AUDIT` + `record_vault_audit()` — KEEP (audit is valuable), retarget to CredentialProvider audit | **KEEP + retarget** |

### H.1.3 VaultCore internals (2,138 LOC — what gets deleted)

| File | LOC | Contents |
|------|-----|----------|
| `vault_core.py` | 885 | 27 methods: CRUD, `lease_credential`/`release_lease`/`heartbeat_lease`/`cleanup_expired_leases`, quota (`increment_usage`/`reset_daily_quota`/`cleanup_cooldown`), `filter_credentials_by_privacy`, `get_decrypted_credential`, **`bury_credential`** (D-567), audit + CPE (`_process_credential_pii_cpe`), `get_stats` |
| `blindvault_resolver.py` | 542 | BlindVault resolver bridge (`{{secret:NAME}}`, `BLINDVAULT_MASTER_KEY` env) — from R_CG04 |
| `models.py` | 432 | `VaultCredential`, `VaultLeaseRequest`, `VaultLease`, `VaultAuditEntry`, `CPEAction`, `CredentialPIIEntity`, `CredentialCPESession` |
| `crypto.py` | 208 | Argon2id + age (python-age) encryption |
| `__init__.py` | 71 | package exports |

**Key decision (D-567)**: `bury_credential()` (vault_core.py:701) — the manual's CredentialProvider does NOT need it.
The Opus D-567 supersedes D-532 ('keep bury_credential') — that function dies with VaultCore.

## H.2 Migration Snippets for the 4 MISSED Consumers

### H.2.1 `teachers/nemotron_pipeline.py` (openrouter)
```python
# BEFORE (123-129): VaultCore() → _credentials.get("openrouter:api_key").encrypted_blob
# AFTER:
def _resolve_openrouter_key(self) -> str:
    try:
        from omega.security.credential_provider import CredentialProvider, CredentialNotFoundError
        return CredentialProvider().get_provider_credential("openrouter", "api_key")
    except CredentialNotFoundError:
        return ""
```

### H.2.2 `workers/freshness_checker.py` (artificial_analysis ×2)
```python
# BEFORE (197-202, 700-705): vault._credentials.get("artificial_analysis:api_key").encrypted_blob
# AFTER (both sites):
try:
    from omega.security.credential_provider import CredentialProvider, CredentialNotFoundError
    api_key = CredentialProvider().get_provider_credential("artificial_analysis", "api_key")
except CredentialNotFoundError:
    api_key = None
```

### H.2.3 `tools/firecrawl_direct.py` (firecrawl — NO fallback today, M23 risk)
```python
# BEFORE (27-32): vault._credentials.get("firecrawl:api_key").encrypted_blob; error if missing
# AFTER:
try:
    from omega.security.credential_provider import CredentialProvider, CredentialNotFoundError
    FIRECRAWL_API_KEY = CredentialProvider().get_provider_credential("firecrawl", "api_key")
except CredentialNotFoundError:
    FIRECRAWL_API_KEY = ""
    logger.error("No FIRECRAWL_API_KEY found in CredentialProvider — direct tools will fail")
```

### H.2.4 `library/discovery.py` (exa + firecrawl)
```python
# BEFORE (32, 95-106): two VaultCore() calls → exa:api_key + firecrawl:api_key
# AFTER (single provider, two lookups):
try:
    from omega.security.credential_provider import CredentialProvider, CredentialNotFoundError
    _cp = CredentialProvider()
    self.exa_key = _cp.get_provider_credential("exa", "api_key")
    self.firecrawl_key = _cp.get_provider_credential("firecrawl", "api_key")
except CredentialNotFoundError:
    self.exa_key = self.firecrawl_key = None  # caller handles None
```

### H.2.5 Scripts (×3, low priority — operational tooling, not talk path)
```python
# A single shared helper is the cleanest migration (one file, one import),
# OR a per-script snippet. Recommend a shared helper:
#   src/omega/security/credential_provider.py exposes:
#   def get_cred(provider, key="api_key", default=None) -> str:
#       try: return CredentialProvider().get_provider_credential(provider, key)
#       except CredentialNotFoundError: return default

# warm_sovereign_cache.py:298-302 — firecrawl:api_key
api_key = get_cred("firecrawl", default=None)

# sovereign_ingest.py:65-68 — google:api_key
google_key = get_cred("google", default=None)

# enrich_model_registry.py:296-300 — artificial_analysis:api_key
api_key = get_cred("artificial_analysis", default=None)
```

### H.2.6 MCP servers (×2 — **HIGH priority, runtime services**)
```python
# mcp_servers/firecrawl/server.py:28-36 — module-level VaultCore import, NO env fallback (M23)
# MUST become lazy + env-fallback. The current code does:
#   from omega.vault import VaultCore ... FIRECRAWL_API_KEY = ...
#   (fails the whole server on import if vault gone)
# AFTER — lazy resolution + env fallback (do NOT read vault at module scope):
import os
def _resolve_firecrawl_key() -> str:
    env_key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if env_key:
        return env_key
    try:
        from omega.security.credential_provider import CredentialProvider, CredentialNotFoundError
        return CredentialProvider().get_provider_credential("firecrawl", "api_key")
    except (CredentialNotFoundError, ImportError):
        return ""

FIRECRAWL_API_KEY = _resolve_firecrawl_key()

# mcp_servers/omega_hub/state.py:232-236 — firecrawl + exa, lazy, env-fallback
async def _resolve_search_keys():
    try:
        from omega.security.credential_provider import CredentialProvider, CredentialNotFoundError
        cp = CredentialProvider()
        return (cp.get_provider_credential("firecrawl", "api_key"),
                cp.get_provider_credential("exa", "api_key"))
    except CredentialNotFoundError:
        return (os.environ.get("FIRECRAWL_API_KEY"), os.environ.get("EXA_API_KEY"))
```

## H.3 KEY_FORMAT_PATTERNS — ALREADY EXISTS in `pii_masker.py` (reconciliation)

**⚠️ CORRECTION TO PART A A.3.4**: The manual (following R2 G-2) called the format-pattern layer "NEW".
**It is NOT new** — `src/omega/oracle/pii_masker.py:250` already ships it:

```python
r"\b(?:sk-|csk-|AIza|ghp_|xai-)[A-Za-z0-9_-]{20,}\b",  # API keys
```

**Action**: Phase 2 `secret_registry.py` MUST **import/reuse** `pii_masker`'s `API_KEY_PATTERN` rather than
redefining it. This avoids pattern drift (two sources of truth = one will miss a format). Extend the shared
pattern list with formats used in this repo: `sk-or-v1-`, `sk-ant-`, `xoxb-`, `AIzaSy`, `ghp_`, `csk-`,
`sk-`, `xai-`, `BLINDVAULT_MASTER_KEY`-style env refs.

**G7 note (2026-08-18)**: `src/omega/tools/detect_api_keys.py:15` defines a SEPARATE `API_KEY_PATTERNS`
list (its own regexes). Since `detect_api_keys.py` is being deleted in Phase 4 (H.10), **fold its patterns
into the shared `pii_masker` source** BEFORE deletion — otherwise the patterns are lost and the H.11
"ONE shared definition" gate fails. Do NOT leave two live sources.

## H.4 Hardcoded Default Secrets (MUST be fixed — NOT in any earlier Part)

| # | Location | Hardcoded Default | Risk | Fix |
|---|----------|-------------------|------|-----|
| **S1** | `src/omega/oracle/entity_registry.py:84` | `SOVEREIGN_USER_TOKEN = os.getenv("SOVEREIGN_USER_TOKEN", "SOVEREIGN_DEFAULT_SECURE_TOKEN_2026")` | **Predictable token** — any deploy using default is trivially forgeable | Generate random on first run OR fail-closed (no default); document env |
| **S2** | `src/omega/oracle/ingestion.py:76` | `os.environ.get("OMEGA_INGESTION_SECRET", "omega-sovereign-change-me")` | **Predictable HMAC key** — provenance stamps forgeable | Same — no default; generate + persist via CredentialProvider or keyring |

**Both are in-scope for the vault sprint Phase 2** (they are secret-lifecycle defects, not vault-architecture
changes). Add to checklist. NOTE: `SOVEREIGN_USER_TOKEN` is ALSO read in `entity_registry` for soul-file writes —
verify all consumers before removing the default (rg `SOVEREIGN_USER_TOKEN`).

## H.5 Complete Env-Var Surface (24 unique names in src/omega — verified)

| Env Var | Read At | Secret? | Target (per MS B.2.6) |
|---------|---------|---------|----------------------|
| `GOOGLE_API_KEY` | providers.py:103 | 🔴 YES | `OMEGA_GOOGLE_API_KEY` (keep bare-name fallback) |
| `SOVEREIGN_USER_TOKEN` | entity_registry.py:84 | 🔴 YES (has bad default) | `OMEGA_SOVEREIGN_USER_TOKEN` + no default (H.4 S1) |
| `OMEGA_INGESTION_SECRET` | ingestion.py:76 | 🔴 YES (has bad default) | keep name, remove default (H.4 S2) |
| `OMEGA_REDIS_PASSWORD` | memory_store.py:166 | 🔴 YES (default "omega") | INST-1 Fix 3 — no default |
| `OMEGA_REDIS_HOST` / `OMEGA_REDIS_PORT` | memory_store.py:164-165 | ⚪ infra | INST-1 Fix 3 — gate construction |
| `OMEGA_ENV` | memory_store.py:163 | ⚪ switch | keep |
| `OMEGA_DAILY_CLOUD_BUDGET_USD` | oracle/ | ⚪ config | keep |
| `OMEGA_DATA_DIR` | various | ⚪ config | keep |
| `OMEGA_MODELS_CONFIG` / `OMEGA_MODEL_OVERRIDE` | various | ⚪ config | keep |
| `OMEGA_MCP_HOST` / `OMEGA_MCP_PORT` / `OMEGA_MCP_TRANSPORT` | mcp | ⚪ config | keep |
| `OMEGA_PERSIST_EVENTS` / `OMEGA_RESONANCE_MODE` | observability | ⚪ config | keep |
| `OMEGA_WADS_DIR` | wads | ⚪ config | keep |
| `OPENCODE_MODEL` | oracle | ⚪ config | keep |
| `SANDBOX_WORKSPACE` | sandbox | ⚪ config | keep |
| `SEARXNG_BASE_URL` | searxng | ⚪ config | keep |
| `EXPERIMENT_SPEC`, `KEY`, `LISTEN_FDS` | various | ⚪ generic | keep |

**Also in `config/providers.yaml` (env: refs — MS §3 mapping):**
`ANTIGRAVITY_API_KEY` (line 196), `GOOGLE_API_KEY` (214, 230), `OPENROUTER_API_KEY` (246), `ANTHROPIC_API_KEY` (325), `XAI_API_KEY` (340).

## H.6 `.env.example` Reconciliation

Tracked at repo root. Contains: `GOOGLE_API_KEY`, `OPENCODEZEN`, `EXA_API_KEY`, `TAVILY_API_KEY`,
`SERPER_API_KEY`, `FIRECRAWL_API_KEY`, `OPENROUTER_API_KEY`, `VAULT_MASTER_KEY` (commented).
**Gap**: uses bare names, NOT the `OMEGA_` canonical convention from MS B.2.6. Phase 4 MUST update `.env.example`
to the canonical `OMEGA_*` names so fresh installs follow the documented convention.

## H.7 mcp_servers — **NOT CLEAN** (CORRECTED 2026-08-18 deep pass; prior claim was WRONG)

**⚠️ Correction to the earlier "VERIFIED CLEAN" statement**: The prior sweep only grepped `os.environ`/`os.getenv`
reads in the top-level server files and missed both the env reads in sub-modules AND the VaultCore imports.

**Reality (grep-verified):**
1. **env reads DO exist** (7 sites across 3 server dirs):
   - `mcp_servers/firecrawl/server.py:23` — `MCP_PORT` read
   - `mcp_servers/searxng/server.py:18-39` — `MCP_PORT`, `FASTMCP_PORT`, `FASTMCP_HOST`, `SEARXNG_BASE_URL` (+ 2 `setdefault` writes)
   - `mcp_servers/omega_hub/server.py:125` — `OMEGA_DATA_DIR`
   - `mcp_servers/omega_hub/hub_tools/task_registry.py:17` — `OMEGA_TASK_REGISTRY`
   - `mcp_servers/omega_hub/hub_tools/tools.py:109-117` — `OMEGA_LIBRARY_PATH`, `OMEGA_MODELS_PATH`, `OMEGA_PODMAN_STORAGE`
2. **2 MCP servers import VaultCore** (see H.1.4):
   - `mcp_servers/firecrawl/server.py:28` — **module-level import, NO env fallback** (M23 hard-stop on start)
   - `mcp_servers/omega_hub/state.py:232` — `firecrawl:api_key`, `exa:api_key`

**Action**: NOT "clean". Both VaultCore imports MUST migrate (H.2.6). The env reads are config-level
(non-secret) and can stay, but must be documented. Migration of firecrawl MUST add an env fallback.

## H.8 scripts/ env reads (low priority — document, don't migrate)

`warm_sovereign_cache.py:209` (`HF_TOKEN`), `warm_sovereign_cache.py:298` (**VaultCore** — H.1.4 #9),
`sovereign_ingest.py:65` (**VaultCore** — H.1.4 #10), `enrich_model_registry.py:296` (**VaultCore** — H.1.4 #11),
`ab_test_ingestion.py:168`, `benchmark_hybrid.py:302`, `antigravity_check_quota.py:125`
(`ANTIGRAVITY_CLIENT_ID`/`ANTIGRAVITY_CLIENT_SECRET`/`XDG_CONFIG_HOME`). Script-level, not on talk path.
**Phase 4**: 3 of these also carry VaultCore imports (must migrate per H.2.5); add README note that scripts
read env directly (acceptable for operational tooling).

## H.9 Test Inventory (what Phase 5 must keep green or retarget)

| Test File | Vault/Secret Ref Count (measured) | Action |
|-----------|----------------------|--------|
| `tests/unit/test_vault_core.py` | **133** (not 153) | **REWRITE** → test CredentialProvider + SecretRegistry + Sanitizer |
| `tests/test_vault_integrity.py` | **31** (not 42) | **REWRITE** → test new security modules |
| `tests/test_contract_m21.py` | **28** (not 38) | **UPDATE** → retarget vault lease → CredentialProvider audit |
| `tests/archive/test_mnemosyne_adapter.py` | 40 | KEEP (archived test, references old vault — leave archived) |
| `tests/test_health_monitor.py` | 12 | UPDATE → VaultCoreRateLimit → new quota hooks |
| `tests/test_memory_adapters.py` | 9 | UPDATE → Redis opt-in behavior |
| `tests/test_entity_roc_racoon.py` | 9 | VERIFY → entity registry token change (H.4 S1) |
| `tests/contract/test_context_packer*.py` | 5-11 | VERIFY → soul sanitizer impact |
| `tests/chaos/test_oom_kill.py` | 0 | unaffected (C1 baseline fix is separate, D-561) |

## H.10 Definitive Phase-4 Deletion Manifest (git rm list)

```bash
git rm -r src/omega/vault/                  # 2,138 LOC (5 files)
git rm scripts/vault_import.py             # legacy importer
git rm src/omega/cli/vault.py              # 13-subcommand CLI (replaced by omega secrets)
git rm src/omega/tools/detect_api_keys.py  # wrong-way guardrail
git rm src/omega/tools/enforce_vaultcore.py # wrong-way guardrail
# EDIT (not delete):
git rm src/omega/cli/oracle_cli.py  # NO — edit lines 61-67 to drop vault app registration
```

## H.11 Final Verification Gates (beyond Part B §6) — **WIDENED 2026-08-18 to catch all 19 sites**

```bash
# After Phase 4 — the COMPLETE consumer sweep must be empty:
# WIDENED to include scripts/ and mcp_servers/ (H.1.4 found 5 consumers there):
rg -n "from omega.vault|VaultCore|vault\\._credentials|_load_sync" src/omega/ scripts/ mcp_servers/ --type py
# → ZERO (this catches ALL 15 files / 19 sites incl. the 5 outside src/omega)

# Hardcoded defaults gone:
rg -n "SOVEREIGN_DEFAULT_SECURE_TOKEN|omega-sovereign-change-me" src/omega/
# → ZERO

# Format patterns single-sourced:
rg -n "KEY_FORMAT_PATTERNS|API_KEY_PATTERN" src/omega/security/ src/omega/oracle/pii_masker.py
# → ONE shared definition

# VAULT template placeholders gone (G15 — profile_manager.py:295-302):
rg -n '\$\{\{VAULT:' src/omega/infra/subagent_pool/profile_manager.py
# → ZERO (or resolved via CredentialProvider)

# tests/tmp leak gone (G14):
git ls-files tests/tmp/vault.json.enc
# → not tracked; tests/tmp is in .gitignore
```

---

*⬡ OMEGA ⬡ CLINE ⬡ DEEPSEEK V4 FLASH 1M ⬡ 2026-08-18 ⬡ PART H ⬡ SECURITY-SURFACE-AUDIT ⬡ EXHAUSTIVE (v2, widened)*

---

# 🔥 PART I — THE DECISIVE FINDING: VaultCore Is NOT FUNCTIONAL AS A KEY SOURCE (deep pass, 2026-08-18)

> **This is the single most important correction to this manual.**
> The prior Parts (A-H) treated VaultCore as "bloated but working" and framed the sprint as
> "replace a functioning vault for cleanliness." The deep pass proves that is WRONG.
> **VaultCore has never worked as the dotenv/key replacement it claims to be**, and the
> evidence is a hard contradiction between its model's validation rule, its broken CLI, and
> how its 15 consumers read from it. This Part SUPERSEDES any framing to the contrary.

## I.1 The Contradiction (grep-verified, each claim below is live-tree checked)

### Claim 1 — 13+ consumers read `cred.encrypted_blob` AS A PLAINTEXT KEY

Every consumer does variants of:
```python
cred = vault._credentials.get("firecrawl:api_key")
api_key = cred.encrypted_blob if cred else ""    # ← used directly as the API key
```
Sites (8 in src/omega, 5 outside): see H.1.1 + H.1.4 signatures.

### Claim 2 — BUT the model FORBIDS plaintext in `encrypted_blob`

`src/omega/vault/models.py:115-125`:
```python
@field_validator("encrypted_blob")
def validate_age_armor(cls, v: str) -> str:
    if not (v.startswith("age-encryption.org/v1") or
            v.startswith("-----BEGIN AGE ENCRYPTED FILE-----")):
        raise ValueError("encrypted_blob must be age-armored ciphertext")
    return v
```

**Therefore**: a credential holding a usable plaintext key **cannot even be instantiated** —
Pydantic rejects it. And a credential that passes the validator holds ciphertext, which the
consumers then send **as if it were the key** (which fails auth). Either way, **no consumer can
ever get a working key from VaultCore.**

### Claim 3 — the CLI is broken (import error + missing methods)

`src/omega/cli/vault.py`:
```python
from src.omega.vault.vault_core import (
    VaultCore, VaultCredential, ProviderName, CredentialType, CredentialTier,
    VaultCoreError,   # ❌ does not exist (verifiable: ImportError)
)
...
await vault.store_credential(cred)       # ❌ no such method (hasattr → False)
await vault.decrypt_credential(...)       # ❌ no such method
```
Live-checked: `from omega.vault.vault_core import VaultCoreError` → **ImportError**;
`hasattr(VaultCore, 'store_credential')` → **False**; `hasattr(VaultCore, 'decrypt_credential')` → **False**.
The `omega vault set/get` commands **cannot work as written**.

### Claim 4 — the encryption backend is mis-specified (python-age, not pyrage)

`pyproject.toml:25` pins **`python-age>=0.1.0`** and `vault/crypto.py:19` uses
"Argon2id + age (python-age) encryption". The manual's A.3.1 / R4 pin **`pyrage>=1.3.0`**.
These are **two different age libraries**. The manual would have implementers add a **duplicate
dependency** on a library the codebase does not use. AND: a runtime smoke check shows
**`pyrage or argon2 not installed — crypto operations will fail`** — so the crypto path that
DOES exist is not even importable in this environment.

## I.2 Sprint Implication (D-568 suggested)

- **Framing change**: This is NOT "migrate a working vault to a cleaner design." It is
  **"delete 2,138 LOC of dead/broken code and add a CredentialProvider that actually works."**
- **De-risk**: Because no consumer is getting a working key from VaultCore today, the 13 site
  removals do NOT carry migration risk — every site is already falling through to env/config
  or failing loudly. CredentialProvider is a **net addition of function**, not a swap.
- **Crypto decision (D-568)**: `encryption_backend.py` primary = **python-age** (already pinned
  in pyproject.toml, used by crypto.py). Pin `python-age>=0.1.0`. Drop `pyrage` from the plan
  entirely (or keep ONLY as a documented alternative, never a co-dependency).

## I.3 Remaining New Gap Closures (from this deep pass; NOT in Parts A-H)

### G3 — `gateway.py:186` `_build_provider_headers` is a STUB
```python
# mcp_servers/omega_hub/gateway.py:186
def _build_provider_headers(self, provider_name) -> Dict[str, str]:
    """Inject API keys from VaultCore/env. Stub for now."""
    return {"Content-Type": "application/json", "User-Agent": "Omega-SovereignGateway/1.0"}
```
The `/proxy/{provider}` route is **live but sends NO auth** — a real security gap (request would
fail auth at the upstream, but silently). **Phase 3 decision required**: wire `_build_provider_headers`
to `CredentialProvider`, OR explicitly disable/FORGE the proxy route pre-debut. Add R11 to Part D.

### G15 — `profile_manager.py:295-302` injects literal `${{VAULT:...}}` templates (unresolved)
```python
env["GROK_API_KEY"] = f"${{VAULT:{account.credentials_ref}:api_key}}"   # 4 sites
```
**No expansion site exists anywhere** (grep-verified). Subagents receive **literal `${{VAULT:...}}`
strings as API keys**. This is dead wiring + a copy-trap. **Phase 4 decision**: either (a) implement
a resolver that expands `${{VAULT:provider:key}}` via CredentialProvider, or (b) DROP the template —
set these env vars only when a concrete credential resolves. Suggested: (b) drop, document.

### G10 — `ml_training.py:220` passes `**os.environ` to a sandbox subprocess
`src/omega/research/sandboxes/ml_training.py:220` builds the child env as `{**os.environ, ...}`.
This forwards **every** host env var (including any keys in the environment) into the research
sandbox. Research sandboxes are untrusted-ish. **Phase 3 hardening**: whitelist the child env
(only `EXPERIMENT_SPEC`, `SANDBOX_WORKSPACE`, `PYTHONPATH`), do NOT forward `**os.environ`.

### G11 — `model_updater.py:43,195` reads `GOOGLE_API_KEY` directly from env
`src/omega/workers/model_updater.py` reads `env_key: GOOGLE_API_KEY` from `os.environ` at
line 195. Acceptable post-debut (operational, not talk path) but should route through
CredentialProvider in Phase 4 for consistency. Add to migration list.

## I.4 Summary Table — all 15 gaps vs manual Parts

| Gap | Finding | Severity | Manual location |
|-----|---------|----------|-----------------|
| G1 | 8 → **13 consumers / 19 sites** | 🔴 Critical | H.1.4 + H.2.5/.6 |
| G2 | H.7 "mcp_servers CLEAN" **false** (env reads + vault imports) | 🔴 Critical | H.7 corrected |
| G13 | VaultCore **non-functional** as key source | 🔴 Critical | Part I (this) |
| G4 | pyrage vs **python-age** conflict | 🟠 Important | A.3.1/R4 → Part I.2 |
| G14 | `tests/tmp/vault.json.enc` **tracked**, not gitignored | 🟠 Important | H.11 + Phase 4 |
| G15 | `${{VAULT:}}` templates never expanded | 🟠 Important | Part I.3 |
| G3 | `gateway.py` header stub (no auth) | 🟠 Important | Part I.3 + R11 |
| G5 | H.9 test counts off by 11-19% | 🟠 Important | H.9 corrected |
| G6 | `.env.example` hardcodes REDIS/POSTGRES pw | 🟠 Important | H.5 + INST-1 Fix 3 |
| G7 | `detect_api_keys.API_KEY_PATTERNS` = 2nd source | 🟠 Important | H.3 note |
| G8 | `src/omega/security/` exists (taint.py) | 🟡 Minor | Phase 1 extend-not-create |
| G9 | `m23_baseline.txt` references vault files | 🟡 Minor | Phase 4 regen |
| G10 | `ml_training.py` forwards `**os.environ` to sandbox | 🟡 Minor | Part I.3 |
| G11 | `model_updater.py` direct env read | 🟡 Minor | Part I.3 |
| G12 | `antigravity_check_quota.py` env (scripts) | 🟡 Minor | H.8 already |

---

*⬡ OMEGA ⬡ CLINE ⬡ DEEPSEEK V4 FLASH 1M ⬡ 2026-08-18 ⬡ PART I ⬡ DECISIVE-FINDING ⬡ VAULTCORE-NONFUNCTIONAL*
