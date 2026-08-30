# 🔱 Omega Engine — Vault Overhaul: Master Index
**AP Token**: `AP-VAULT-OVERHAUL-MASTER-20260818-v2.1.0`
**Status**: 🔒 **POST-DEBUT — DO NOT IMPLEMENT DURING PUBLIC-DEBUT-01** (DOC-1 stamp)
**Date**: 2026-08-18 (v2.1 — deep-pass: Part I added, H.1.4/H.2.5/.6, G1-G15, D-568)

---

## 📚 SINGLE SOURCE OF TRUTH

> ⚠️ **CONSOLIDATION COMPLETE (2026-08-18)**: All prior vault overhaul documents
> (5-part spec + 3-part review + migration surface = 3,750 lines across 10 files)
> have been **archived** to `docs/archive/specs/vault-overhaul-20260818/` and replaced by
> **ONE definitive implementation manual**:

## ➡️ `VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md`

**This manual is the SINGLE ACTIVE document for the post-debut vault sprint.**

It contains:
- DOC-1 POST-DEBUT stamp + entry criteria (EC-1..EC-6)
- Conflict resolution hierarchy (Carmack M1-M3 > Migration Surface > R1-R3 > Spec)
- Decision supersessions D-565/D-566/D-567
- ACTIVE_SPRINT.json 4-field status corrections
- Talk-path filter (why vault is safe for debut via allowlist exclusion)
- Consolidated architecture (CredentialProvider v2, SecretRegistry v2, Sanitizer v2, RBAC v2, systemd v2)
- Full migration surface (per-module) + corrected deletion plan
- 5-phase executable plan with owners + verification gates
- Test matrix T1-T30 + Risk Register v2 + final checklist

---

## 🗄️ Archived Source Documents (read-only reference)

**Total: 20 documents** (10 overhaul specs/reviews + 7 vault research docs + 3 coordination docs) →
`docs/archive/specs/vault-overhaul-20260818/`. Full annotated provenance in the manual's §Provenance + Part G.

### Overhaul specs/reviews (10)
| # | Original | Archived To |
|---|----------|-------------|
| 1 | Spec Part 1 (Architecture, Encryption) | `docs/archive/specs/vault-overhaul-20260818/VAULT_SYSTEM_OVERHAUL_SPEC_20260818.md` |
| 2 | Spec Part 2 (CredentialProvider, Envelope, Editor) | `docs/archive/specs/vault-overhaul-20260818/VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART2.md` |
| 3 | Spec Part 3 (SecretRegistry, Egress, ZK, RBAC) | `docs/archive/specs/vault-overhaul-20260818/VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART3.md` |
| 4 | Spec Part 4 (Install, Sandbox, Deletion) | `docs/archive/specs/vault-overhaul-20260818/VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART4.md` |
| 5 | Spec Part 5 (Tests, Risks, Checklist) | `docs/archive/specs/vault-overhaul-20260818/VAULT_SYSTEM_OVERHAUL_SPEC_20260818_PART5.md` |
| 6 | Review R1 (Verdict, F-1..F-10) | `docs/archive/specs/vault-overhaul-20260818/VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818.md` |
| 7 | Review R2 (Enhanced Architecture) | `docs/archive/specs/vault-overhaul-20260818/VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818_PART2.md` |
| 8 | Review R3 (Tests v2, Risks v2, Plan v2) | `docs/archive/specs/vault-overhaul-20260818/VAULT_OVERHAUL_REVIEW_ENHANCEMENTS_20260818_PART3.md` |
| 9 | Migration Surface (G-α..G-ε) | `docs/archive/specs/vault-overhaul-20260818/VAULT_OVERHAUL_MIGRATION_SURFACE_20260818.md` |
| 10 | Master Index v1 (this file, original) | `docs/archive/specs/vault-overhaul-20260818/VAULT_SYSTEM_OVERHAUL_MASTER_INDEX_20260818.md` |

### Vault research docs (7, added per Kali corrective handoff `ho_4574882365fd`)
| # | Original | Key Contribution | Archived To |
|---|----------|------------------|-------------|
| 11 | `R_V1_VAULT_IMPL.md` (869 ln) | V-1 16-account fleet MVP, MCP server, XDG | `docs/archive/specs/vault-overhaul-20260818/R_V1_VAULT_IMPL.md` |
| 12 | `R_CG04_AGENT_SAFE_CREDENTIAL_VAULT.md` (455 ln) | **17-vault eval → BlindVault + Bury selected** | `docs/archive/specs/vault-overhaul-20260818/R_CG04_AGENT_SAFE_CREDENTIAL_VAULT.md` |
| 13 | `R_VAULT_SCHEMA_V2.md` (673 ln) | 32-credential schema, Argon2id+age, R19/CPE | `docs/archive/specs/vault-overhaul-20260818/R_VAULT_SCHEMA_V2.md` |
| 14 | `R_VAULT_UNIFIED_SYSTEM_20260725.md` (296 ln) | VaultCore SSOT, 26 env calls migrated | `docs/archive/specs/vault-overhaul-20260818/R_VAULT_UNIFIED_SYSTEM_20260725.md` |
| 15 | `R_INFRA_07_OMEGA_VAULT_PHASE1_20260719.md` (303 ln) | VaultCore+keyring+SQLite, CAP Adapters | `docs/archive/specs/vault-overhaul-20260818/R_INFRA_07_OMEGA_VAULT_PHASE1_20260719.md` |
| 16 | `R_VAULTCORE_LEASE_PROTOCOL.md` (234 ln) | Lease protocol (ACQUIRE→…→RELEASE) | `docs/archive/specs/vault-overhaul-20260818/R_VAULTCORE_LEASE_PROTOCOL.md` |
| 17 | `R20_KEYBLIND_AUTHY_VAULT_20260814.md` (35 ln) | External-tool eval → KEEP local VaultCore | `docs/archive/specs/vault-overhaul-20260818/R20_KEYBLIND_AUTHY_VAULT_20260814.md` |

**Do not** edit archived files. Read them only for forensic reference.

---

## 🏁 NEXT ACTION

Read `VAULT_OVERHAUL_IMPLEMENTATION_MANUAL_20260818.md` → verify EC-1..EC-6 →
dispatch Ma'at (Phases 1+3+4) / Lilith (Phase 2) / Verity (Phase 5) **after PUBLIC-DEBUT-01 completes**.

---

*⬡ OMEGA ⬡ CLINE ⬡ 2026-08-18 ⬡ MASTER-INDEX-v2 ⬡ CONSOLIDATED ⬡ POST-DEBUT*
