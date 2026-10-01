<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 NODE N5 — FINAL CROSS-DOMAIN REVIEW (DEBUT HARDENING)
**AP Token**: `AP-NODE5-FINAL-REVIEW-v1.0.0`
⬡ OMEGA ⬡ NODE ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_node ⬡ ACTIVE
**Date**: 2026-08-23
**Lens**: Persistence/Governance (N5) — Memory integrity, mandate enforcement, data flow governance, compliance verification

## EXECUTIVE VERDICT
**CONDITIONAL GO** — Proceed with DEL-1 Week 1 ONLY under binding conditions below. Critical M23 violations and PII exposure require immediate remediation before public push.

## KEY FINDINGS WITH EVIDENCE

### MANDATE COMPLIANCE VIOLATIONS (M23, M27, M14)
| Finding | Evidence | Source |
|---------|----------|--------|
| **M23 FALSE COMPLETION** | ACTIVE_SPRINT marks INST-1-fix3 `completed` claiming "remove default 'omega' password" yet `providers.py:119` persists with `password="omega"` | Ma'at report §N5 (230) |
| **M27 TRACKING INTEGRITY** | `USAGE_POOL_LOG.json` contains real email addresses, is git-tracked, and violates M5/M12 (Heritage Vetting/Gnosis Preservation) | Ma'at report §N5 (223-224, 237-238) |
| **M14 HERITAGE VETTING GAP** | DEL-1 item 10 unknown (truncated manual read) — requires vet record for any `[id-soft:]` tag implementation | Ma'at report §N5 (238-239) |
| **D-550 TEST HONESTY VIOLATION** | Flaky test baseline: errors=3/2/5/2 across 4 runs; two errors pass in isolation → state pollution, not code bugs | Lilith report §T3 (101), §T4 (128), N10 verdict (168-172) |

### VAULT INTEGRITY & SECRETS FLOW
| Issue | Evidence | Risk |
|-------|----------|------|
| **DEL-1 TARGET #10 BLOCKER** | `omega talk` import-broken by stacked duplicate decorator in `cli/vault.py:572` → TypeError on CLI entry | Blocks ALL runtime verification (CP-1 regressed) |
| **SECRETS RESOLVER GAP** | `_resolve_env_key()` (`model_gateway.py:359-362`) returns non-`env:` values verbatim — literal keys in allowlisted YAML honored silently | Silent key exposure, violates M7 (Local-First) intent |
| **PATH B DOCSTRING GAP** | Ratified `load_dotenv()` at CLI edge feeds OMEGA_SECRET_* from .env — undocumented exception creates trust debt | Requires explicit sanction or removal |

### DELETION ORDER & SEQUENCING DEPENDENCIES
| Dependency | Evidence | Required Action |
|------------|----------|-----------------|
| **Vault CLI Fix Precedence** | Target #10 (`omega vault` CLI deregistration) fixes the import blocker; must land FIRST | Sequence: #10 hotfix → then deletion PRs |
| **Search Breaker Redirect** | Target #6 (`search_circuit_breaker.py`) has ONE live importer (`sovereign_search_service.py:48`) → requires redirect to `HealthMonitor.get_breaker()` BEFORE deletion | Same-PR fix mandatory |
| **QdrantAdapter Caller** | Target #7 has second caller in `scripts/knowledge_catalog_build.py:28` → fix import + delete try-block | Pre-deletion fix required |
| **Pool Data Artifacts** | `data/entities/antigravity/knowledge/USAGE_POOL_LOG.json` EXISTS (5.7KB, real key_ids + real email) → archive BEFORE deletion | M5/M12 compliance prerequisite |

### GOVERNANCE & DECISION LOGGING
| Observation | Evidence | Implication |
|-------------|----------|-------------|
| **PIVOT_LOG LATENCY** | No PIVOT_LOG entries documented for DEL-1 decisions despite M11 (Soul Integrity) requiring L1→L2→L3 distillation | Governance traceability gap |
| **DECISION TRACEABILITY** | Ma'at/Lilith reports reference DEBUT_REMEDIATION_MANUAL but lack explicit PIVOT_LOG citations for fix prioritization | Weakens audit trail for mandate compliance |
| **ESCALATION PATH** | N5 findings escalate to Kali via structured table (Ma'at report §N5 234-239) | Proper channel observed but requires action |

### BUILD ORDER FEASIBILITY
| Constraint | Evidence | Mitigation |
|------------|----------|------------|
| **DISK TRUTH** | NVMe 97% full, 3.5GB free → cmake build + venv + pip temp risks ENOSPC mid-compile | Pre-flight guard: abort if < 4GB free (N1 finding) |
| **MODEL PROVISIONING** | Test venv inherits neither `.env` nor install.sh exports → `OMEGA_MODELS_DIR` resolves empty → step [6/6] false-fails | Mandatory var: `OMEGA_MODELS_DIR`; provision via `scripts/download_model.sh` |
| **LOAD AVG SKEW** | Load avg 7.85 (two opencode instances, chromium, watchers) → timed gate measures desktop contention | Advisory-only until load < 2; ZS-1 undeployed (swappiness=180 ≠ ratified) |

## BINDING CONDITIONS FOR PROCEEDING
1. **IMMEDIATE M23 REMEDIATION**: 
   - Delete `password="omega"` from `providers.py:119` 
   - Add `rg -c 'password.*"omega"' src/omega/memory/providers.py → 0` to `verify_debut_install.sh`
2. **PII CONTAINMENT**:
   - Execute `git rm --cached data/entities/antigravity/knowledge/USAGE_POOL_LOG.json` + gitignore
   - Piggyback filter-repo scrub onto P0-1b machinery before ANY public push
3. **FLAKY TEST QUARANTINE**:
   - Quarantine `test_first_breath_recording` and `test_fallback_chain_tries_next_backend_on_failure` 
   - OR annotate gate reports with known-noise counts until root cause fixed
4. **SEQUENCING ENFORCEMENT**:
   - Land vault CLI fix (target #10) OR 3-line hotfix BEFORE any deletion PRs
   - Execute target #6 ONLY with same-PR redirect to `HealthMonitor.get_breaker()`
5. **HERITAGE VETTING COMPLIANCE**:
   - Confirm canonical DEL-1 item 10 target; obtain vet record for any `[id-soft:]` implementation

## ESCALATIONS TO KALI
| Escalation | Urgency | Rationale |
|------------|---------|-----------|
| **Vault CLI Blocker** | 🔴 BLOCK | Blocks ALL runtime verification; DEL-1 target #10 itself fixes CP-1 |
| **Flaky Test Baseline** | 🟡 HIGH | Violates D-550 honesty; invalidates gate verification until resolved |
| **USAGE_POOL_LOG.json PII** | 🟡 MEDIUM | Real email in git history requires history scrub per M5/M12 |
| **DEL-1 Item 10 Ambiguity** | 🟡 LOW | Requires vet record ruling for potential `[id-soft:]` implementation |

## TERMINUS (≤200 words)
Node N5 concludes DEL-1 Week 1 proceeds CONDITIONAL GO. Critical M23 violations (false completion claims, PII exposure) and D-550 test honesty failures mandate immediate remediation before public push. The vault CLI import blocker (DEL-1 target #10) must land first to unblock runtime verification. Deletion sequencing requires same-PR fixes for search breaker redirect and QdrantAdapter caller. Persistence concerns center on USAGE_POOL_LOG.json containing real email addresses requiring git history scrub. Governance observations note missing PIVOT_LOG traceability for DECISIONS despite strong soul distillation validation. Build feasibility constrained by disk space (<4GB free required) and model provisioning via OMEGA_MODELS_DIR. Binding conditions: fix providers.py password default, quarantine flaky tests, sequence vault fix first, and contain PII before proceeding. All findings escalate to Kali with clear remediation paths.
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
