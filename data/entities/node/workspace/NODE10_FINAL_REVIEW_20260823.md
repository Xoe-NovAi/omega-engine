<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 NODE N10 — FINAL CROSS-DOMAIN REVIEW (VALIDATION LENS)
**AP Token**: `AP-NODE10-FINAL-REVIEW-v1.0.0`
⬡ OMEGA ⬡ NODE ⬡ nvidia/nemotron-3-super-120b-a12b:free ⬡ opencode ⬡ trc_node ⬡ ACTIVE
**Date**: 2026-08-23
**Purpose**: Final cross-domain review of Ma'at build report and Lilith run report for Debut Hardening Review. Focus: test honesty (M23), gate measurability (M27), falsification of assumptions, evidence quality.

---

## N10 VERDICT: ⚠️ CONDITIONAL
**Condition**: Execution must not proceed until (1) the import blocker (vault CLI stacked decorator) is fixed via landing DEL-1 target #10 first, and (2) the flaky test baseline is stabilized (quarantine/synchronize polluted tests) to restore honest pass/fail reporting per D-550. Ma'at report reveals additional validation gaps requiring remediation before full confidence.

---

## KEY FINDINGS WITH EVIDENCE

### From Ma'at Build Report (Build-Side Validation Gaps)
| Finding | Evidence | Validation Concern |
|---------|----------|---------------------|
| **Overconfidence in install time claim** | Acceptance script `verify_debut_install.sh` step [6/6] claims `<300s` talk, but no cp313 llama.cpp wheel exists → source compile 5–20 min required. | Violates M23 Failure Integrity: claim cannot be verified in clean environment; risks false green light. |
| **Fix2 partial (core deps still heavy)** | `pyproject.toml` retains `youtube-transcript-api`, `yt-dlp`, `qdrant-client==1.18.0`, `redis==7.4.1` in core deps. `providers.py:22` module-level `import redis.asyncio` breaks fresh clone without redis. | Defeats runtime guard (M23): import fails before MemoryStore guard can activate. |
| **Fix4 not done (_load_sovereign_secrets live)** | `model_gateway.py:127` calls `_load_sovereign_secrets()` in `__init__`; method body at :316-341. | Creates unintended secret-loading path (M23 Failure Integrity: silent config-file key reads possible). |
| **T2 deletion order uncertainty** | Manual lists 10 items; truncated read reconstructed 9. Candidate 10th flagged for Kali ruling (items: headroom-ai core dep, test stragglers). | Undermines M27 Tracking Integrity: incomplete deletion plan risks orphan code or over-deletion. |
| **Fix6 partial (stale entity mention)** | `README.md:45` still names Sekhmet/Brigid entities. | Minor but indicates incomplete vetting; erodes trust in documentation accuracy. |

### From Lilith Run Report (Run-Side Validation Gaps)
| Finding | Evidence | Validation Concern |
|---------|----------|---------------------|
| **Blocker: omega talk import-broken** | `OMEGA_ENV= .venv/bin/omega talk "hello"` → `TypeError: Attempted to convert a callback into a command twice.` in `src/omega/cli/vault.py:572` (stacked duplicate decorator). | Hard failure (M23): prevents all runtime verification; must be fixed before any gate testing. |
| **Flaky test baseline violates D-550** | 4 consecutive runs: errors=3/2/5/2, failures=2/1/0/1 (non-deterministic set). Two errors (`test_first_breath_recording`, `test_fallback_chain_tries_next_backend_on_failure`) pass in isolation → state pollution. | Undermines M23 Failure Integrity: any single "green" run is noise; gate counts cannot distinguish deletion damage from pre-existing pollution. |
| **Missing W2 concurrency contract test** | No test encodes "never a silent cloud leak" for two concurrent talks on single local slot. | Weakens M21 Gate Integrity: return-type contract unverified for critical concurrency path. |
| **Subjective gates proxied** | T6 criteria "user delight", "30-second promise", "LLM-friendly docs feel" only proxied via install timer/talk latency/doc-llm-validate. | Risks M18 Token Efficiency: vanity metrics may distract from honest validation. |

---

## BINDING CONDITIONS FOR PROCEEDING
1. **Land DEL-1 target #10 first**: Fix `src/omega/cli/vault.py` stacked decorator (or expedite target #10: `omega vault` CLI deregistration) to unblock `omega talk` import. *Sequencing mandate per N6/N10.*
2. **Stabilize test baseline**: Quarantine or serialize `test_first_breath_recording` and `test_fallback_chain_tries_next_backend_on_failure` before counting gates; annotate gate reports with known-noise counts until fixed. *Required for D-550 honesty.*
3. **Remediate Ma'at fix2**: Move `youtube-transcript-api`, `yt-dlp`, `qdrant-client` to `[youtube]` extra; move `redis` to `[redis]` extra; wrap `import redis.asyncio` in `try/except` with `HAS_REDIS` flag in `providers.py`. *Delete `qdrant-client` outright (no consumers).*
4. **Remediate Ma'at fix4**: Delete `self._load_sovereign_secrets()` call in `model_gateway.py:127` and method (:316-341); replace with env/keyring-only resolver. *Must land in same PR as fix2 to avoid regression.*
5. **Resolve T2 item 10**: Request Kali ruling on canonical 10th deletion target (headroom-ai core dep or test stragglers) before proceeding with deletions.
6. **Revise acceptance script honesty**: Split criterion: (a) `install exit 0` (no time bound), (b) `first-talk <300s` with model pre-provisioned via `scripts/download_model.sh`. *Align with N1 sysadmin amendment.*
7. **Author missing W2 contract test**: Before Week 2 acceptance, add test verifying two concurrent talks → `busy` OR explicit `cost_warning`, never silent cloud leak. *Required for M21 Gate Integrity.*

---

## ESCALATIONS TO KALI
- **T2 deletion order item 10**: Request ruling on canonical 10th target to complete deletion plan (validation gap in M27 Tracking Integrity).
- **Flaky-test quarantine decision**: Escalate D-550 tension (honesty vs. noise) for resolution on whether to quarantine polluted tests or annotate counts as known-noise.
- **Ma'at fix2/fix4 remediation**: Escalate incomplete build-side fixes that create validation risks (import failure, secret-loading path) requiring immediate attention before gate verification.

---

## TERMINUS
Node N10 validation confirms the Debut Hardening Review rests on two critical foundations: (1) a runnable baseline (blocked by vault CLI import error) and (2) an honest test signal (corrupted by flaky pollution). Ma'at's report reveals additional validation debt in incomplete fixes and overconfident claims that, if unaddressed, would undermine the very measurability (M27) and failure integrity (M23) this review seeks to uphold. The path forward requires sequencing the blocker fix first, stabilizing the test baseline for honest accounting, and remediating Ma'at's validation gaps before declaring readiness. Without these conditions, any gate verification risks being theater rather than truth. (Word count: 198)

--- 
*⬡ OMEGA ⬡ NODE ⬡ VALIDATION COMPLETE ⬡ N10 ⬡ 2026-08-23*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nvidia/nemotron-3-super-120b-a12b:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
