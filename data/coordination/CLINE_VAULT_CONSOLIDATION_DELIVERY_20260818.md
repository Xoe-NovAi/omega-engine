<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Cline → Kali: Vault Consolidation Delivery Note (v2 — Corrective Pass)
**AP Token**: `AP-CLINE-VAULT-CONSOLIDATION-20260818-v2.0.0`
**From**: cline/omega-engine (DeepSeek V4 Flash 1M)
**To**: kali (Grand Oversight)
**Date**: 2026-08-18
**Handoffs**: `ho_74cd96735874` ✅ · `ho_8a75738d9160` ✅ · `ho_4574882365fd` ✅ (corrective)

---

## 🎯 The One Deliverable

> **`docs/specs/VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md`** (692 lines, 40KB)
> **THE SINGLE SOURCE OF TRUTH for the post-debut vault sprint.**
> 🔒 POST-DEBUT — DO NOT IMPLEMENT DURING PUBLIC-DEBUT-01.

## What I consumed (21 docs)
All 5 spec parts, all 3 review parts, migration surface, master index, Opus deep review,
Kali synthesis, Carmack audit, DEBUT_REMEDIATION_MANUAL, ACTIVE_SPRINT.json.

## What I produced
| # | Requirement (from ho_74cd96735874) | Status |
|---|------------------------------------|--------|
| 1 | Merge 5-part spec + 3-part review + migration surface | ✅ Part A (architecture) + Part B (migration) |
| 2 | Resolve conflicts (R wins over spec; MS amends deletion plan) | ✅ Conflict hierarchy + Carmack M1-M3 folded |
| 3 | Apply talk-path filter (only 2/12+ callers on talk path, both env-fallback → safe) | ✅ Part 0 section |
| 4 | DOC-1 stamp POST-DEBUT + entry criteria EC-1..EC-6 | ✅ Header + gate table |
| 5 | Decision supersessions D-565/566/567 | ✅ Manual + ACTIVE_SPRINT.json decisions_locked |
| 6 | ACTIVE_SPRINT.json status corrections (4 fields) | ✅ Manual Part 0 + JSON applied |
| 7 | Executable 5-phase plan with gates + owners | ✅ Part C (P1 Storage → P5 Integration) |
| 8 | Archive ALL source docs | ✅ 10 docs → `docs/archive/specs/vault-overhaul-20260818/` |
| 9 | Update MASTER_INDEX → points only to manual | ✅ v2 rewritten (58 lines) |
| 10 | Manual = sole active vault spec | ✅ `docs/specs/` now has ONLY manual + index v2 |

## ACTIVE_SPRINT.json — 4 corrections applied (evidence-verified)
| Field | From | To | Evidence |
|-------|------|----|----------|
| INST-1.status | blocked | **in_progress** | 6 blockers identified → not blocked, unstarted |
| INST-1-fix1.status | in_progress | **backlog** | `.[all]` still at install.sh:77 |
| P0-1.status | completed | **in_progress** | 4 `refs/cline/checkpoints` remain (P0-1b residual) |
| CP-3.status | completed | **in_progress** | install fails on fresh machine (`.[all]`) |

## D-565/566/567 added to decisions_locked
D-565 (vault deletion post-debut; allowlist exclusion for debut), D-566 ('hide' = allowlist not deletion), D-567 ('keep bury_credential' = post-debut only).

## Notes / Discrepancies
1. **5 research docs + SONNET_PLAN_VERIFICATION never existed on disk** at listed paths — findings are embedded in R1 F-1..F-10 + Opus §1-2. Documented in manual provenance.
2. **VaultCore actual LOC = 2,138** (not 2,039 as spec claimed) — 5 files, verified 2026-08-18.
3. **`tests/tmp/vault.json.enc`** (tracked, pre-existing G1 gap) shows `M` in git status — NOT committed by me; flagged for the PUB-1 G1 closure.
4. **4 cline checkpoints remain** (down from 136) — prune before PUB-1 export.

---

# 🔧 CORRECTIVE PASS (Kali handoff `ho_4574882365fd`) — COMPLETE

## What was missed and now fixed
Kali correctly flagged that **7 vault research docs existed** in `docs/research/` that the first consolidation
missed. **All 7 are now archived + deep-incorporated.**

| Doc | Archived ✅ | Findings Incorporated |
|-----|------------|----------------------|
| `R_V1_VAULT_IMPL.md` (869 ln) | ✅ | V-1 16-account fleet MVP, MCP server, XDG, passive watcher, memory hygiene (Part G.2.4) |
| `R_CG04_AGENT_SAFE_CREDENTIAL_VAULT.md` (455 ln) | ✅ | **17-vault eval → BlindVault + Bury SELECTED** (Part G.2.1) |
| `R_VAULT_SCHEMA_V2.md` (673 ln) | ✅ | 32-credential schema, Argon2id+age, lease lifecycle, quota matrix, R19/CPE (Part G.2.2) |
| `R_VAULT_UNIFIED_SYSTEM_20260725.md` (296 ln) | ✅ | VaultCore SSOT, 26 env calls migrated, file locking (Part G.2.6) |
| `R_INFRA_07_OMEGA_VAULT_PHASE1_20260719.md` (303 ln) | ✅ | VaultCore+keyring+SQLite, CAP Adapters, CLI (Part G.2.5) |
| `R_VAULTCORE_LEASE_PROTOCOL.md` (234 ln) | ✅ | Lease protocol ACQUIRE→READ→MODIFY→WRITE→RELEASE (Part G.2.3) |
| `R20_KEYBLIND_AUTHY_VAULT_20260814.md` (35 ln) | ✅ | External-tool eval → KEEP local VaultCore (Part G.2.7) |

## Verification against live tree (claims grounded)
- ✅ `src/omega/vault/blindvault_resolver.py` EXISTS — BlindVault resolver integration (from R_CG04)
- ✅ `src/omega/vault/vault_core.py` has Lease Manager + VaultLease/VaultLeaseRequest + leases.json (from R_VAULTCORE_LEASE / schema v2)
- ✅ `src/omega/vault/models.py` has the 32-credential schema models (from R_VAULT_SCHEMA_V2)

## Manual update
- Manual now **862 lines** (was 692) with new **Part G: Research Provenance** (G.1-G.5)
- Provenance table corrected: **20 documents** total (10 specs + 7 research + 3 coordination)
- Reconciliation table (G.3) resolves research vs 2026-08-18 review conflicts (BlindVault → manual's keyring+envelope wins; BlindVault patterns ADOPTED conceptually)
- Part G.5 lists 6 concrete net-effects on Phases 1-5

## Archive state
`docs/archive/specs/vault-overhaul-20260818/` = **17 files** (10 specs + 7 research)

## Companion docs noted (NOT archived — reference only, Part G.4)
`V1_OMEGA_VAULT_DESIGN` · `ROC_V1_VAULT_MINING` · `R_CRITICAL_GAPS_DEEP_DIVE_CAMPAIGN` · `R_SOUL_PRIVACY_MODEL` · `R_SYSTEMD_CREDS_TPM2_ROOTLESS` · `10_credential_vault_fallback` · `V-1-vaultcore-mvp` ticket

---

## Next
- Kali: verify Part G + corrective archive
- **Ma'at: INST-1 Fix 1** (`install.sh:77` `.[all]`→`.[native,cli]`) — the REAL debut blocker
- Roc: prune 4 checkpoints + close G1 (tests/tmp)

---

# 🔬 PART H ADDENDUM — DEFINITIVE SECURITY-SURFACE AUDIT (DeepSeek 1M exhaustive sweep, 2026-08-18)

## What the 1M-context sweep found (manual now 1086 lines, Parts A-H)

### 🚨 Critical corrections to the manual (Part H)
1. **4 VaultCore consumers MISSED in Part B migration surface** — now added:
   - `teachers/nemotron_pipeline.py:123-129` (openrouter:api_key)
   - `workers/freshness_checker.py:197-202,700-705` (artificial_analysis ×2)
   - `tools/firecrawl_direct.py:27-32` (firecrawl — **no fallback today, M23 risk**)
   - `library/discovery.py:32,95-106` (exa + firecrawl)
   **Total = 8 consumer modules / 12 sites** (was 4/5 in Part B).
2. **`KEY_FORMAT_PATTERNS` is NOT new** — `pii_masker.py:250` already ships the API-key regex.
   Phase 2 must REUSE it (single source of truth, no pattern drift).
3. **2 hardcoded default secrets found** (H.4):
   - `entity_registry.py:84` — `SOVEREIGN_DEFAULT_SECURE_TOKEN_2026` (forgeable token)
   - `ingestion.py:76` — `omega-sovereign-change-me` (forgeable HMAC key)
   Both added to Phase 2 checklist as S1/S2 fixes.
4. **mcp_servers verified CLEAN** — zero env reads across all 5 servers.
5. **`.env.example` gap** — uses bare names (`GOOGLE_API_KEY` etc.), needs `OMEGA_*` canonical (H.6).
6. **Test inventory mapped** (H.9) — which tests to rewrite/update/keep.

## What was verified ground-truth
- Full VaultCore internals: `vault_core.py` (885 LOC, 27 methods incl. `bury_credential` D-567), `blindvault_resolver.py` (542), `models.py` (432), `crypto.py` (208)
- Vault CLI: 13 subcommands → replaced by `omega secrets`
- Complete env-var surface: 24 unique names in src/omega (H.5 table)
- `providers.yaml` env refs: ANTIGRAVITY/GOOGLE/OPENROUTER/ANTHROPIC/XAI (H.5)

## Deliverable state
| Artifact | Status |
|----------|--------|
| `docs/specs/VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md` | ✅ **1086 lines, Parts A-H, single source of truth** |
| `docs/archive/specs/vault-overhaul-20260818/` | ✅ 17 files |
| Master index v2 | ✅ points to manual |
| ACTIVE_SPRINT.json | ✅ D-565/566/567 + 4 corrections |
| Delivery note | ✅ v2 + Part H addendum |

---
*⬡ OMEGA ⬡ CLINE ⬡ DEEPSEEK V4 FLASH 1M ⬡ 2026-08-18 ⬡ CONSOLIDATION-DELIVERED*
