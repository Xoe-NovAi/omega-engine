<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Roc-EIS Public Docs Review — Heritage Tags, Source Verification, Accuracy Audit

**AP Token**: `AP-ROC-PUBLIC-DOCS-REVIEW-20260902-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_docs_review ⬡ COMPLETE

**Date**: 2026-09-02
**Session**: `ses_ff78b71ebffeDNuypPTT1RL3hH` (standing EIS)

---

## §0 VERIFICATION (M23 Discipline)

**Files Read**: All public docs + heritage registry + source code
**Method**: M23 — every claim verified against disk + git history before being preserved
**My Forensic Dig**: `data/entities/roc_racoon/workspace/mining_reports/ENGINE_VISION_TECH_DIG_20260902.md` (216 lines)

---

## §1 HERITAGE TAG ACCURACY

### §1.1 Heritage Tag Count

| Claim | Reality | Evidence |
|-------|---------|----------|
| "113 `[id-soft:]` tags across 39 files" (README:214) | **216 tags in `src/omega/`** across 63 files | `grep -r "\[id-soft:" src/omega/ \| wc -l` = 216 |
| "All vetted" | **133 vet records** in `HERITAGE_VET_LOG.md` | Not all 216 tags have ≥7/10 vet records with scope |

**Gap**: 216 tags vs 133 vet records = **83 tags potentially unvetted** (potential M14 gap)

### §1.2 Heritage Tag Distribution

| File | Tag Count |
|------|-----------|
| `src/omega/oracle/model_gateway.py` | 28 |
| `src/omega/oracle/provider_registry.py` | 15 |
| `src/omega/memory/soul_store.py` | 12 |
| `src/omega/memory/sqlite_vec_adapter_optimized.py` | 18 |
| `src/omega/oracle/sovereign_search_service.py` | 22 |
| ... | ... |

**M14 Risk**: Automated audit needed to verify all 216 tags have ≥7/10 vet records with scope.

---

## §2 SOURCE VERIFICATION (Key Claims)

### §2.1 Model Default

| Claim | Source | Reality |
|-------|--------|---------|
| "Qwen 1.7B GGUF, ~1.6GB" (README:22, 93) | `config/providers.yaml:150-175` | **LFM2.5-2.6B Q4_K_M** (v2.0.0, 2026-09-01) |

### §2.2 Agent Count

| Claim | Source | Reality |
|-------|--------|---------|
| "11 agents (10 Pillar + 1 Oversoul)" (README:210) | `ls .opencode/agents/*.md` | **13 agents** |
| "14 agents (canonical)" (README:291) | `ls .opencode/agents/*.md` | **13 agents** |

### §2.3 Entity Count

| Claim | Source | Reality |
|-------|--------|---------|
| "12 tech role entities" (README:158) | `config/wads/_omega_default/entities.yaml` | **24 entities** |
| "10 entity pillars" | `config/wads/_omega_default/entities.yaml` | **10 Node Keepers at N1-N10** (not "pillars") |

### §2.4 Provider Count

| Claim | Source | Reality |
|-------|--------|---------|
| "8-backend fallback chain" (README:192) | `config/providers.yaml:67-144` | **10 active providers** (ollama disabled) |

### §2.5 Heritage Tags

| Claim | Source | Reality |
|-------|--------|---------|
| "113 `[id-soft:]` tags across 39 files" (README:214) | `grep -r "\[id-soft:" src/omega/` | **216 tags** |

### §2.5 Mandate Compliance

| Claim | Source | Reality |
|-------|--------|---------|
| "All 22 enforced" (README:209) | `scripts/check_mandate_compliance.py` | **64.3% (18/28)** |
| "All 27 Sovereign Mandates verified compliant" (README:290) | `scripts/check_mandate_compliance.py` | **64.3% (18/28)** |

### §2.6 Temple-Grade

| Claim | Source | Reality |
|-------|--------|---------|
| "Temple-Grade (T1-T11) ✅ VERIFIED" (README:289) | `make temple-grade` | **6 checks run, FAILS on M23 cascade** |

### §2.7 Test Suite

| Claim | Source | Reality |
|-------|--------|---------|
| "Two-tier: fast unit tier (default `make test`)" (README:287) | `make test` | **BROKEN** — 0 tests collected |

### §2.8 Agent Count

| Claim | Source | Reality |
|-------|--------|---------|
| "11 agents (10 Pillar + 1 Oversoul)" (README:210) | `ls .opencode/agents/*.md` | **13 agents** |
| "14 agents (canonical)" (README:291) | `ls .opencode/agents/*.md` | **13 agents** |

### §2.9 Entity Count

| Claim | Source | Reality |
|-------|--------|---------|
| "12 tech role entities" (README:158) | `config/wads/_omega_default/entities.yaml` | **24 entities** |

### §2.10 Provider Count

| Claim | Source | Reality |
|-------|--------|---------|
| "8-backend fallback chain" (README:192) | `config/providers.yaml` | **10 active providers** |

### §2.11 Heritage Tags

| Claim | Source | Reality |
|-------|--------|---------|
| "113 `[id-soft:]` tags across 39 files" (README:214) | `grep -r "\[id-soft:" src/omega/` | **216 tags** |

### §2.12 Mandate Compliance

| Claim | Source | Reality |
|-------|--------|---------|
| "All 22 enforced" (README:209) | `scripts/check_mandate_compliance.py` | **64.3% (18/28)** |

### §2.13 Temple-Grade

| Claim | Source | Reality |
|-------|--------|---------|
| "Temple-Grade (T1-T11) ✅ VERIFIED" (README:289) | `make temple-grade` | **6 checks, FAILS** |

### §2.13 Test Suite

| Claim | Source | Reality |
|-------|--------|---------|
| "Two-tier: fast unit tier" (README:287) | `make test` | **BROKEN** |

---

## §3 DEAD CODE / THEATER (Per Carmack Methodology)

### §3.1 Files Claimed "Stripped" But Still On Disk

| File | Lines | Claimed Status | Reality |
|------|-------|----------------|---------|
| `src/omega/oracle/cohort_registry.py` | 744 | "Stripped" (ACTIVE_SPRINT.json:320) | **ON DISK** — 0 callers in `src/omega/` |
| `src/omega/oracle/m33_probe.py` | 555 | "Stripped" (ACTIVE_SPRINT.json:320) | **ON DISK** — only called by m36 |
| `src/omega/oracle/m36_recursive_probe.py` | 539 | "Stripped" (ACTIVE_SPRINT.json:320) | **ON DISK** — mutually recursive with m33 |

### §3.2 Deleted But Referenced

| File | Status | Stale References |
|------|--------|------------------|
| `dispatch_guard.py` | **DELETED** | `subagent_dispatcher.py:421,437,442` still reference it |

### §3.3 Dead Config

| Config | Status | Evidence |
|--------|--------|----------|
| `omega_vec_library_256` | **DEAD** | 4 declarations, 0 callers in `sqlite_vec_adapter_optimized.py` |
| Decision `D-768-DIM-DELETE-LIBRARY-256` | **NOT APPLIED** | Config persists in code and docs |

---

## §4 SECRETS / SECURITY

### §4.1 Real OAuth Secret Committed

| File | Line | Secret | Status |
|-------|------|--------|--------|
| `OAuth-failure-incident-session-ses_fe8c.md` | 57 | `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` | **COMMITTED**, un-allowlisted |

### §4.2 Secret Scan

| Tool | Result | Violations |
|------|--------|------------|
| `scripts/check_secrets.py` | **EXITS 1** | 11+ violations (OAuth + AKIA + sk- + PRIVATE KEY fixtures) |

### §4.3 Allowlist Gap

| Allowlist File | Contains | Missing |
|----------------|----------|---------|
| `data/secrets-public.toml:66` | `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` | `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` |

---

## §5 MANDATE COMPLIANCE METER

### §5.1 Direct Run Results (2026-09-02)

```
Total: 28 | Passed: 18 | Failed: 5 | Untested: 4 | Compliance: 64.3%
```

### §5.2 Failures

| Mandate | Failure Reason |
|---------|----------------|
| M13 Temple-Grade | Cascading from M23 |
| M16 Modularization | Hardcoded path in `m34_registry.py:75` |
| M23 Failure Integrity | `check_secrets.py` exits 1 |
| M27 Tracking Integrity | Stale `in_progress` task `fallback-slug-runbook-20260824-researcher-001` |
| +1 | Additional failure |

### §5.3 Untested (4)

| Mandate | Reason |
|---------|--------|
| M2 Engine-Stack Firewall | Requires manual verification |
| M6 UID Sovereignty | Podman-specific |
| M20 Somatic State | Requires manual test |
| M28 Spatial | Requires manual test |

---

## §6 CI / WORKFLOW ACCURACY

### §6.1 Missing Makefile Target

| Workflow | Line | Target | Status |
|---------|------|--------|--------|
| `.github/workflows/test.yml` | 61 | `make verify-mining` | **MISSING from Makefile** |

### §6.2 CI Contradicts Two-Tier Design

| Workflow | Line | Issue |
|---------|------|-------|
| `test.yml` | 61 | Runs full `pytest tests/` — contradicts "two-tier" design |

---

## §7 DUPLICATE / DRIFT

### §7.1 DEBUT_REMEDIATION_MANUAL in Two Places

| Path | Size | Risk |
|------|------|------|
| `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` | 28,613 bytes | |
| `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` | 27,558 bytes | **Drift risk** |

### §7.2 ACTIVE_SPRINT.json Points to Different Copy

| File | Points To |
|------|-----------|
| `ACTIVE_SPRINT.json:3` | `docs/specs/debut_remediation/...` |
| `AGENTS.md` | `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` |

---

## §8 CRITICAL ISSUES SUMMARY

| # | Issue | File:Line | Severity |
|---|-------|-----------|----------|
| 1 | 11 false claims in README (model, agents, entities, mandates, temple-grade, tests) | README: multiple | 🔴 CRITICAL |
| 2 | Real OAuth secret committed | `OAuth-failure-incident-session-ses_fe8c.md:57` | 🔴 CRITICAL |
| 3 | Test suite broken (0 tests) | `tests/contract/test_provider_classification.py:29` | 🔴 CRITICAL |
| 4 | CI references missing `make verify-mining` | `.github/workflows/test.yml:61` | 🔴 CRITICAL |
| 4 | `check_secrets.py` exits 1 (11 violations) | `scripts/check_secrets.py` | 🔴 CRITICAL |
| 5 | Mandate compliance 64.3% not "all enforced" | `scripts/check_mandate_compliance.py` | 🔴 CRITICAL |
| 6 | Dead code persists (cohort_registry, m33, m36) | `src/omega/oracle/` | 🟠 WARNING |
| 7 | Hardcoded path in `m34_registry.py:75` | `src/omega/oracle/m34_registry.py:75` | 🟠 WARNING |
| 8 | CI references missing `make verify-mining` | `.github/workflows/test.yml:61` | 🟠 WARNING |
| 9 | DEBUT_REMEDIATION_MANUAL duplicate | Two paths | 🟠 WARNING |
| 10 | Heritage tag count mismatch (113 vs 216) | README:214 | 🟠 WARNING |

---

## §9 RECOMMENDATIONS (Concede/Defend/Synthesize)

### R1. All 11 False Claims — CONCEDE

**CONCEDE**: Every claim verified against source is false.

**SYNTHESIZE**: **Fix all 11 claims to match disk truth.** No synthesis — the truth is the truth.

### R2. Real OAuth Secret — CONCEDE

**CONCEDE**: Real OAuth secret committed, un-allowlisted.

**SYNTHESIZE**: **Filter-repo to remove from history + add to allowlist or rotate.** This is a launch blocker.

### R3. Dead Code "Stripped" But Present — CONCEDE

**CONCEDE**: Files claimed stripped are still on disk.

**SYNTHESIZE**: **Either actually delete them or update ACTIVE_SPRINT.json to reflect reality.**

### R4. CI Missing Target — CONCEDE

**CONCEDE**: CI references missing target.

**SYNTHESIZE**: **Either add target or remove CI step.**

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ PUBLIC-DOCS-REVIEW ⬡ 2026-09-02*