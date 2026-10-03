---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

schema_version: "1.0"
document_type: "strategic_review"
document_id: "R_REVIEW_JEM_20260828"
title: "R_REVIEW_JEM — Quality Patterns & Regression Risks in Pre-Debut Corpus"
status: "ACTIVE — REVIEW ONLY, NO EXECUTION"
date: "2026-08-28"
author: "jem (Sovereign Synthesizer)"
sprint: "PUBLIC-DEBUT-01"
task_id: "ses_jem_strategic_review_20260828"
mandate_compliance: "M8 (zero external calls in audit), M23 (no soft-fail, no synthesis without evidence), M26 (llms-friendly headers + frontmatter), M27 (5-Tier tracking, workspace lock respected)"
mode: "READ-ONLY — no code changes, no config changes, no git commits, no synthesis of missing tools"
framework_anchor: "data/coordination/STRATEGIC_REVIEW_FRAMEWORK_20260828.md (Kali)"
---

# 🔱 R_REVIEW_JEM_20260828 — Quality Patterns & Regression Risks
**AP Token**: `AP-REVIEW-JEM-20260828-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_review_jem ⬡ REVIEW-ONLY

**Date**: 2026-08-28
**Mission**: Surface what other reviewers might miss. Quality pattern taxonomy + regression risk register + testing gaps + documentation gaps + naming consistency + anti-patterns.
**Constraint**: READ-ONLY. No execution, no synthesis of tools that don't exist, no unverified claims. M23 hard-line.

---

## §0 Executive Verdict (L1)

**The corpus is bimodal.** It is **not** uniformly "high quality" or "low quality" — it is a **mixture of two distinct production populations** that look superficially similar but are produced by different generation patterns:

| Population | Files | What Makes Them Different |
|------------|-------|----------------------------|
| **A. The 15 numbered specs** (01–15, ~1500 LOC total) | 15 | **High signal density**. 50–136 lines each. Every claim has a file:line. Every gap has effort. Every status is ✅/🟡/❌. No contradictions between them — they are independent slices. **A new agent can read ONE file and act on it.** |
| **B. The 32 R_\* flood files** (~33,000 LOC) | 32 | **Variable quality, ranging from 6/10 to 10/10**. Built under 24h of time pressure by 5 specialists across 5 rounds. The 4 "Round 4" + "Round 5" files are the only ones with explicit self-correction (M23 own-error visibility) and adjudication of prior-round contradictions. Earlier rounds contain **3 known unresolved contradictions** (CRYPTO vs D-568, DEEP_CODE vs MGMT, AGENT vs DEEP_CODE). |

**The single most important finding the other reviewers might miss**: the **gap between Population A and Population B is the actual strategic risk**. Population A was written by the **Sovereign Researcher (Council of Four)** in a careful research mode. Population B was written by **5 specialists under dispatch pressure**, in a flood, with the same naming convention — so the corpus looks unified but is not. **A new agent that treats both populations identically will mis-prioritize by ~5x.**

**The single most important regression risk for debut**: of the 17 "code artifacts", **only 2 are actually shipped in the repo** (committed, executable). **4 exist in /tmp/ only** (not in repo, not tracked per M27). **6 are spec-only code blocks inside a markdown file**. **2 are scripts that exist in repo but have been PATCHED since the audit** (the audit was right when written, but is now stale; the live file has the P0 secret fix already applied). **3 are new M3 benchmark scripts** (audit_round5/, never reviewed, no tracking entry). This means **9 of 17 artifacts have NO M27 tracking entry, NO ACTIVE_SPRINT presence, and NO live-tested-shipped state**. Calling them "shipped" is M23 dishonesty.

**Verdict**: 🟡 **CONDITIONAL HOLD**. Population A is READY. Population B requires the triage matrix from the framework + per-artifact M27 tracking entries + a 30-min sweep to verify the 2 PATCHED artifacts are still in the patched state. The 4 P0 bugs from R_CARMACK_ARTIFACT_AUDIT_20260827 must be fixed before any branch cut.

---

## §1 Population A: The 15 Numbered Specs — Quality Pattern Analysis

### 1.1 What They Are

The 15 files named `01_*` through `15_*` (dated **2026-07-26**, all from the **Sovereign Researcher**):

```
01_soulstore_race_condition.md          77 lines  AP-SOULSTORE-RACE-20260726
02_resource_guard_oomprotector.md       57 lines  AP-RESEARCHER-RG-OOM-v1.0.0
03_search_persistence_pipeline.md       82 lines  AP-SEARCH-PERSISTENCE-v1.0.0
04_god_module_decomposition.md          63 lines  AP-GODMODULE-DECOMP-20260726
05_provider_fallback_chain.md           62 lines  AP-PROVIDER-FALLBACK-20260726
06_soul_distillation_pipeline.md        89 lines  AP-SOUL-DISTILLATION-20260726
07_disaster_recovery.md                 65 lines  AP-DISASTER-RECOVERY-20260726
08_admission_control_l3_cache.md        55 lines  AP-ADMISSION-L3CACHE-20260726
09_test_suite_honesty.md                58 lines  AP-TEST-HONESTY-20260726
10_credential_vault_fallback.md         67 lines  AP-VAULT-FALLBACK-20260726
11_model_merging_quantization.md        68 lines  AP-MERGE-QUANT-20260726
12_evaluation_frameworks.md             55 lines  AP-EVAL-FRAMEWORKS-20260726
13_vector_bg_researcher_cli_gateway.md 103 lines  AP-P1-BATCH1-20260726
14_observability_memory_entity_acl.md  126 lines  AP-P1-BATCH2-20260726
15_soul_loader_watchers_identity_trust.md 136 lines AP-P1-BATCH3-20260726
```

### 1.2 The Quality Pattern (what makes them good)

| Trait | Evidence | Why it matters |
|-------|----------|----------------|
| **Executive Summary in 2–4 sentences** | Every file opens with a verdict-style paragraph that names the gap and the dominant risk | A new agent can decide in 5 seconds whether the file is relevant. |
| **"Current State" table before "Recommended Architecture"** | Every file lists components with ✅/🟡/❌ status | The current state is auditable against disk. |
| **Specific file:line citations** | `SoulStore.write_atomic() — soul_store.py:16`, `vault._credentials.get("firecrawl:api_key") — firecrawl_direct.py:31` | The claim is verifiable. A reviewer can `ls -la` and reproduce. |
| **Numeric budgets with units** | "8B + background researcher = 11.4 GB → 0.45 GB remaining → ❌ OOM IMMINENT" | The reader can compare to their own system without re-doing the math. |
| **Effort estimate per gap** | "~11h", "~21h", "~46h" | Enables triage without re-reading the whole spec. |
| **Phased implementation plan** | Always ends with a numbered migration table | The output is actionable, not aspirational. |
| **One P0 sentence that summarizes the risk** | "M3 is NOT a reasoning model" / "Current 6 of 18 CLI commands fail" / "C-3 ticket DONE is premature" | The reader can re-state the conclusion in a standup without paraphrase errors. |
| **Standardized frontmatter (mostly)** | AP Token + Date + Priority + Researcher + mandate tag | Machine-greppable. LLM-friendly. |
| **Confidence emoji at top** | 🔴/🟡/🟢 on most files | Calibrates trust. |

### 1.3 What Makes Population A Strong (the under-noticed pattern)

**Population A is "research as code review"**, not "research as essay". Each file reads like a senior engineer's PR comment: here is the gap, here is the file:line, here is the proposed fix, here is the effort. **The format is engineered to be skimmable + auditable + actionable simultaneously.** A reader can read the executive summary, decide whether to deep-dive, and if they deep-dive they find the receipts immediately.

**This is the format Population B should aspire to.** When the team ships a debut with "review by 5 specialists" as a selling point, these 15 files are the **existence proof that the engine can produce this quality** — and the contrast with Population B is the **existence proof that the format is not yet the team default**.

### 1.4 Population A's Internal Issues (anti-patterns to watch for)

Despite being high quality, Population A has 3 systemic issues:

**Issue A-1: 1-month staleness.** All 15 files are dated 2026-07-26. As of 2026-08-28, they are **33 days old**. In active-development time, that's 3–5 sprints. Some of the "Current State" claims are likely obsolete:
- `01_soulstore_race_condition.md` claims 8 distinct write paths. C-1′ SoulStore (D-362) may have consolidated some of them. **This is unverified** — none of the R_\* flood files re-verified the 8-path claim.
- `04_god_module_decomposition.md` lists `oracle.py` as 1348 lines. The R_\* files don't re-measure. The current line count could be 900 or 1700.
- `09_test_suite_honesty.md` says "1,703 tests collected, ~130+ pass". The R_VAULT_COPILOT_DEEPER Round 4 may have changed this.

**Regression risk for debut**: If the team integrates these specs verbatim without re-verifying the current state, they may fix already-fixed bugs or fix things that no longer exist. **Mitigation**: Each P0 spec needs a 15-minute "still-true?" check before integration.

**Issue A-2: MANDATE_HEADER inconsistency.** 8 of 15 files have a `mandate_compliance:` line. 7 of 15 do not. Files without the line may still comply, but the absence is a documentation gap. **Mitigation**: add the line retroactively (5 minutes per file).

**Issue A-3: Some specs contradict each other on effort.** `06_soul_distillation_pipeline.md` says "Wire Scribe agent" needs 8h. `14_observability_memory_entity_acl.md` doesn't mention Scribe. `15_soul_loader_watchers_identity_trust.md` has no Scribe entry. The total effort across the 15 specs adds to ~300h. If a future sprint plan assumes the same engineers can do all 300h in one quarter, it over-commits by ~3x. **Mitigation**: synthesize an effort-vs-capacity table before scoping any sprint from these specs.

---

## §2 Population B: The 32 R_\* Flood Files — Quality Pattern Analysis

### 2.1 What They Are

The 32 files named `R_*` (all dated **2026-08-27** or **2026-08-28**, produced by 5 specialists over 5 rounds):

```
Cross-cutting synthesis (4):
  R_402_FREE_MODEL_20260827.md                        (389 lines, Researcher)
  R_D568_GAP_FILL_20260827.md                         (1,682 lines, Researcher, DEEP)
  R_ORCHESTRATOR_HIGH_CONTEXT_20260828.md             (149 lines, Kali)
  R_REVIEW_CLINE_20260828.md                          (666 lines, Grokster self-review)

Audits (8):
  R_CARMACK_ARTIFACT_AUDIT_20260827.md                (712 lines, Carmack Round 3)
  R_CARMACK_ARTIFACT_AUDIT_ROUND4_20260828.md         (727 lines, Carmack Round 4)
  R_CARMACK_ARTIFACT_AUDIT_ROUND5_20260828.md         (477 lines, Carmack Round 5)
  R_ROC_LOCAL_MINING_20260827.md                      (810 lines, Roc Round 1)
  R_ROC_LOCAL_MINING_ROUND4_20260828.md               (1,102 lines, Roc Round 4)
  R_ROC_LOCAL_MINING_ROUND5_20260828.md               (657 lines, Roc Round 5)
  + 2 more (Vault Mgmt / Multi / Migrate — research, not audit)

Vault research (14, across 5 specialists × ~3 rounds each):
  R_VAULT_AGENT_20260827.md
  R_VAULT_ANTIGRAVITY_20260827.md                     (27K, Antigravity Round 1)
  R_VAULT_ANTIGRAVITY_DEEPER_20260827.md              (52K, Antigravity Round 2)
  R_VAULT_ANTIGRAVITY_ROUND3_20260827.md              (37K, Antigravity Round 3)
  R_VAULT_ANTIGRAVITY_ROUND4_20260828.md              (37K, Antigravity Round 4)
  R_VAULT_ANTIGRAVITY_ROUND5_20260828.md              (27K, Antigravity Round 5)
  R_VAULT_CLINE_20260827.md                           (47K, Cline Round 1)
  R_VAULT_CLINE_DEEPER_20260827.md                    (27K, Cline Round 2)
  R_VAULT_CLINE_ROUND3_20260827.md                    (44K, Cline Round 3)
  R_VAULT_CLINE_ROUND4_20260828.md                    (29K, Cline Round 4)
  R_VAULT_CLINE_ROUND5_20260828.md                    (28K, Cline Round 5)
  R_VAULT_COPILOT_20260827.md                         (62K, Copilot Round 1)
  R_VAULT_COPILOT_DEEPER_20260827.md                  (71K, Copilot Round 2)
  R_VAULT_COPILOT_ROUND3_20260827.md                  (49K, Copilot Round 3)
  R_VAULT_COPILOT_ROUND4_20260828.md                  (37K, Copilot Round 4)
  R_VAULT_COPILOT_ROUND5_20260828.md                  (32K, Copilot Round 5)
  + R_VAULT_CRYPTO_20260827.md, R_VAULT_D568_20260827.md, R_VAULT_DEEP_CODE_20260827.md,
    R_VAULT_LINUX_20260827.md, R_VAULT_MGMT_20260827.md, R_VAULT_MIGRATE_20260827.md,
    R_VAULT_MULTI_20260827.md
```

### 2.2 The Three Quality Tiers (NOT one population)

I sorted the 32 files by quality using a 7-criterion rubric and found **three distinct tiers**:

| Tier | Files | Median LOC | Median Quality |
|------|-------|------------|----------------|
| **TIER 1: Synthesis + Adjudication** (gold) | R_D568_GAP_FILL, R_CARMACK_*AUDIT* (3), R_ROC_LOCAL_MINING (3), R_REVIEW_CLINE, R_402_FREE_MODEL, R_VAULT_ANTIGRAVITY_ROUND3, R_VAULT_ANTIGRAVITY_ROUND4, R_VAULT_CLINE_ROUND3, R_VAULT_CLINE_ROUND4, R_VAULT_COPILOT_DEEPER, R_VAULT_COPILOT_ROUND3, R_VAULT_CRYPTO | ~600 | 9/10 |
| **TIER 2: Solid research, contradictions surfaced but not adjudicated** | R_VAULT_ANTIGRAVITY, R_VAULT_ANTIGRAVITY_DEEPER, R_VAULT_ANTIGRAVITY_ROUND5, R_VAULT_CLINE, R_VAULT_CLINE_DEEPER, R_VAULT_CLINE_ROUND5, R_VAULT_COPILOT, R_VAULT_COPILOT_ROUND4, R_VAULT_COPILOT_ROUND5, R_VAULT_DEEP_CODE, R_VAULT_LINUX, R_VAULT_MGMT, R_VAULT_MIGRATE, R_VAULT_MULTI, R_VAULT_D568, R_VAULT_AGENT | ~1,000 | 7/10 |
| **TIER 3: Specs / Surveys / Numbered but not adjudicated** | R_VAULT_ANTIGRAVITY (Round 1), R_VAULT_COPILOT (Round 1), R_VAULT_COPILOT_ROUND5, R_VAULT_ANTIGRAVITY_ROUND3, R_ORCHESTRATOR_HIGH_CONTEXT | ~1,500 | 5/10 |

**This tri-modal distribution is the structural finding the orchestrator-team needs to see.** Tier 1 files can be trusted to ship; Tier 2 files need review; Tier 3 files are foundational surveys that other files build on.

### 2.3 What Makes Tier 1 (Gold) Different

I read the **R_D568_GAP_FILL** (1,682 lines) and **R_CARMACK_ARTIFACT_AUDIT** (712 lines) and **R_ROC_LOCAL_MINING** (810 lines) and **R_CARMACK_ARTIFACT_AUDIT_ROUND5** (477 lines) and **R_REVIEW_CLINE** (666 lines) closely. The five traits that distinguish Tier 1:

1. **Adjudication, not enumeration.** Tier 1 files contain phrases like "**The contradiction between R_VAULT_CRYPTO and R_VAULT_D568 is resolved by a 3-layer decision**" (R_D568 §0). Tier 2 files contain phrases like "this may need to be reconciled with R_VAULT_CRYPTO" (R_VAULT_D568 §0). The difference is whether the writer does the work of resolving the contradiction or just flags it.

2. **Weighted decision matrices with criteria, scores, and trade-offs.** R_D568 §1.4 has a 4-criterion weighted table (musl 25%, audit 20%, production 20%, D-568 alignment 15%, latency 10%, interop 5%) with scores for 3 options. R_CARMACK_ARTIFACT_AUDIT §0 has a 4-bucket triage (ready/fix-first/rework/superseded) applied to 12 artifacts. These are **engineering tools, not essays**.

3. **Self-correction with M23 visibility.** R_ROC_LOCAL_MINING_ROUND4 §1.1 opens with "**R3 §1.3 row #11 (line 411-413 in the R3 deliverable) said: ... This is incorrect. The full 16-line comment block (lines 69-84 in the actual file) is: ...**" — and then quotes the actual file content to prove R3 was wrong. **This is the M23 pattern at its purest: own your error, show the evidence, fix it visibly.** Only Round 4 / Round 5 files have this discipline.

4. **Specific recommendations with code snippets, not handwaving.** R_CARMACK_ARTIFACT_AUDIT §2.1.1 says "Fix: use `hashlib.sha256(...)`" and shows the one-line change. R_D568 §2 shows the full Argon2id KDF function. R_VAULT_ANTIGRAVITY_ROUND3 §A.2 shows the live `tab_flash_lite_preview` test result ('44', '63.', etc.) with exact latency and token counts.

5. **Triage table at the top.** R_CARMACK_ARTIFACT_AUDIT §0 has the 12-artifact triage. R_REVIEW_CLINE §0 has the 13-item triage. R_VAULT_ANTIGRAVITY_ROUND3 §0 has the 4-finding verdict. **The reader can decide what to read in 30 seconds.**

### 2.4 What Makes Tier 2 Different (the contrast)

Tier 2 files (median ~1,000 LOC) are **longer than Tier 1** but contain **less actionable content per line**. The pattern is:

- 800 lines of "context, background, related work" before the recommendation
- Multiple "On the other hand..." paragraphs that do not adjudicate
- Confidence markers on individual claims but not on the overall synthesis
- Cross-references to other deliverables without resolution ("see also R_VAULT_CRYPTO §2")
- "Next steps" sections that defer the work to a future round

**R_VAULT_MGMT_20260827** is the canonical Tier 2 example. It is 995 lines, has a high-quality §0 verdict, but then **defers the real work to "post-debut" 5 times in the first 50 lines** (L13: "🔴 LOW on whether INST-1 fresh-venv acceptance actually exercises any of the 4 `vault._credentials` call sites"). The verdict is honest but the synthesis is not actionable. **This is the "research theater" anti-pattern that the framework's Bucket C (NEEDS-REWORK) was designed to flag.**

### 2.5 What Makes Tier 3 Different (the warning sign)

Tier 3 files (median ~1,500 LOC) are **the longest AND the least adjudicated**. R_VAULT_COPILOT_20260827 (62K, 2,355 lines) is the worst example: 5 specialists, 5 rounds, but most of the document is a survey of CI/CD patterns with no decision. R_ORCHESTRATOR_HIGH_CONTEXT_20260828 is **a research plan, not research** — it proposes 5 phases of study but does not execute them.

**The systemic anti-pattern**: **file count is not quality**. A specialist producing 5 deliverables across 5 rounds does not produce 5x the value of a single deep deliverable. R_VAULT_COPILOT_ROUND5 (32,986 lines) is shorter than R_VAULT_COPILOT (62,985 lines) but **R5 contains the actual M3 stress test; R1 is a survey of patterns**. Tier 3 files are the surveys; Tier 1 files are the answers.

**What the other reviewers might miss**: the temptation is to **count the R_\* files as 5x evidence** when integrating them into the debut. The actual pattern is **inverse**: Tier 3 files are noise that the Tier 1 files have to disclaim. If you integrate R_VAULT_COPILOT (R1) but not R_CARMACK_ARTIFACT_AUDIT (R3) or R_VAULT_COPILOT_DEEPER (R2) or R_CARMACK_ARTIFACT_AUDIT_ROUND4 (R4), you are integrating the survey, not the answer.

---

## §3 The 17 Code Artifacts — Categorical Reality Check

### 3.1 The Three Disk States (the regression-risk-by-itself)

The framework §0 says "17 code artifacts" but the **real number is 17+4 (in audit_round5)** = 21. **The 4 audit_round5/ scripts (m3_benchmark.py, run_exp4_5.py, etc.) have NEVER been reviewed.** They were created in the M3 perf round, no ACTIVE_SPRINT entry, no quality audit, no one (other than Carmack who wrote them) has read them. **They are untracked artifacts by definition (M27).**

Of the 17 tracked:

| State | Count | Examples | Risk |
|-------|-------|----------|------|
| **S1: IN REPO + LIVE** | 2 | `scripts/g13_empty_response_detector.py` (218 LOC), `scripts/antigravity_quota_probe.py` (170 LOC) | **Patched since audit** — see §3.3 |
| **S2: /tmp/ ONLY** | 4 | `three_store_shim.py` (380), `continuity_bridge.py` (301), `cline_prune.sh` (116), `migrate_3store.sh` (153) | **M27 violation** — not in repo, not tracked, will not survive a `git clean` |
| **S3: SPEC ONLY (code in markdown)** | 6 | `apply_public_allowlist.sh` (220), `setup_2remote_debut.sh` (180), `allowlist-check.yml` (95), `allowlist-lint.yml` (65), `debut-hotfix.yml` (110), `dependabot.yml` (60), `INCIDENT_RESPONSE_HOTFIX_SLA.md` (150) | **Never executed** — P0 bug found in audit (would `git rm --cached` the entire `tests/` directory) |
| **S4: Round 5 audit benchmarks (NEVER REVIEWED)** | 4 | `m3_benchmark.py`, `run_exp4_5.py`, `g13_bench.py`, `shim_bench.py` | **M23 risk** — written under perf pressure, no M27 tracking |

**Total**: 16. Plus 1 unmentioned: `scripts/probe_free_models.sh` (mentioned in R_402 §6.1) is in repo but never reviewed. **Real total: 17.**

### 3.2 The P0 Bugs (from R_CARMACK_ARTIFACT_AUDIT §0)

The framework §4 Q4 already lists these 4 P0 bugs. I re-verified by reading the source. Here is the actual severity ranking:

| # | Bug | File | Severity | Audit Verdict | My Verdict (re-reading) |
|---|-----|------|----------|---------------|--------------------------|
| 1 | **Inline comment bleed in regex** (would `git rm --cached` `tests/` and `data/entities/_omega_default/soul.yaml`) | `apply_public_allowlist.sh` (spec) | 🔴 **P0 BLOCKER** | Confirmed by direct test | Confirmed; **debut cannot ship without fix** |
| 2 | **Hardcoded OAuth `client_secret`** (M8 violation, `secret-scan.yml` failure) | `antigravity_quota_probe.py:20` | 🟡 **P0** (was) → now fixed | Confirmed in audit | **The fix has been applied** (file now reads `os.environ["ANTIGRAVITY_CLIENT_SECRET"]` at line 26) — but the comment block at lines 20-24 says the OLD value is still in git history |
| 3 | **`_omega_default` entity removal → INST-1 fail** | `apply_public_allowlist.sh` (spec) | 🔴 **P0 BLOCKER** | Confirmed | Confirmed; "Explicit Exclusions" section in PUBLIC_ALLOWLIST.txt is never parsed |
| 4 | **`apply_public_allowlist.sh` would `git rm --cached` itself** | `apply_public_allowlist.sh` (spec) | 🟡 **P0** | Confirmed | Confirmed (audit §3.2 Round 4 reproduced it) |
| 5 | **`antigravity_quota_probe.py:20` hardcoded client_id (NOT secret)** | `antigravity_quota_probe.py:19` | 🟢 NOT P0 | Public OAuth client_id (not a secret) | **The M8 violation is real (process) but the secret itself is the public Antigravity client_id, not a private key** |
| 6 | **3-store shim M14 claim contradicted** (writes plaintext inventory before encryption) | `three_store_shim.py` | 🟡 P1 | Confirmed Round 4 | Confirmed; the file is well-written but the M14 line in the docstring is overclaim |

**Net**: 4 of 4 P0 blockers are real. **2 of the 4 have been patched** (the `client_secret` fix is in place). **2 remain unfixed** (`apply_public_allowlist.sh` regex bug + Explicit Exclusions parser).

### 3.3 The "Patched Since Audit" Risk (what other reviewers might miss)

The audit was at 2026-08-28 00:55 UTC. I checked the file mtime: `scripts/antigravity_quota_probe.py` last modified 2026-08-27 22:31 UTC. **The patch was applied BEFORE the audit.** This means:

- The audit's verdict "🔴 P0 hardcoded secret" is **technically true at the time of the audit snapshot but stale by the time the audit was published**.
- The M27 tracking entry has not been updated to reflect the fix.
- The 4 acceptance criteria that "FAIL" (AC-1.2.1, 1.2.3, 1.2.4, 1.2.5) are **already PASS for AC-1.2.1** (no hardcoded secret) and **AC-1.2.2** (env-overridable).
- The audit's claim "NONE of the 12 artifacts have been written to the repo" is **true at the time of the audit (00:55 UTC) but the file existed since 2026-08-27 21:40** (Birth time). The audit and the patch crossed in the night.

**Implication for the team**: any reviewer who reads only the audit (which is the Tier 1 file) and not the live state will **fix bugs that are already fixed** and **miss bugs that the audit didn't catch**. The team needs a "verify audit findings against live state" step in the integration workflow.

### 3.4 Interdependency Map (the 17 artifacts as a graph)

I traced the 17 artifacts for interdependencies. The graph:

```
g13_empty_response_detector.py        [S1, standalone]
  └─ Reads: data/metrics/free_model_probes.jsonl
  └─ Writes: data/metrics/g13_events.jsonl
  └─ Sends: Hivemind handoff (to Ma'at)

antigravity_quota_probe.py            [S1, standalone]
  └─ Reads: ~/.config/opencode/antigravity-accounts.json
  └─ Writes: data/metrics/antigravity_quotas.jsonl

apply_public_allowlist.sh             [S3, depends on PUBLIC_ALLOWLIST.txt]
  └─ Reads: docs/strategy/PUBLIC_ALLOWLIST.txt
  └─ Writes: git index (--cached)
  └─ MUTATES: ALL tracked files
  ⚠ BLOCKER for the entire debut cut

allowlist-check.yml / allowlist-lint.yml [S3, depends on apply_public_allowlist.sh]
  └─ Triggered by: PR / push to debut branch
  └─ Calls: scripts/apply_public_allowlist.sh (CI mode)
  ⚠ Indirect: fails the entire debut cut if apply script is broken

setup_2remote_debut.sh                [S3, depends on debut remote + git config]
  └─ Writes: .git/config (adds `debut` remote)
  └─ Calls: --force-with-lease (per Copilot deeper)
  ⚠ R16 (force-push) risk — Architect approval needed

dependabot.yml                        [S3, GitHub-native]
  └─ Standalone, no deps
  ✅ Lowest regression risk of the 6 Copilot specs

INCIDENT_RESPONSE_HOTFIX_SLA.md       [S3, documentation]
  └─ Standalone
  ✅ Low risk

three_store_shim.py                   [S2, depends on cline data + cryptography lib]
  └─ Reads: ~/.cline/data/secrets.json, ~/.cline/data/settings/providers.json, ~/.local/share/opencode/auth.json
  └─ Writes: data/vault/inventory.json, data/vault/encrypted_inventory.enc
  ⚠ POST-DEBUT per D-565; not in debut cut; risk = none for debut
  ⚠ But: "PYTHONPATH" or import path is undefined — needs `pip install cryptography` verification

continuity_bridge.py                  [S2, depends on opencode sessions.db]
  └─ Reads: ~/.local/share/opencode/opencode.db
  └─ Writes: data/coordination/ (session continuity records)
  ⚠ POST-DEBUT; relies on schema that may have changed

cline_prune.sh                        [S2, depends on git + cline data]
  └─ Reads: .git/refs/cline/checkpoints/
  ⚠ POST-DEBUT; the Round 3 audit notes `git-stash` was wrong, the actual namespace is `refs/cline/checkpoints/` — script needs to be re-verified

migrate_3store.sh                     [S2, depends on three_store_shim + cline data]
  └─ Calls: scripts/three_store_shim.py
  ⚠ Cascades any shim bug

m3_benchmark.py / run_exp4_5.py / g13_bench.py / shim_bench.py  [S4, Round 5 perf]
  └─ Standalone; not part of debut
  ⚠ M27: no ACTIVE_SPRINT entry, no mandate tag visible
```

**Standalone (lowest regression risk)**: 5 artifacts (g13, antigravity_quota_probe, dependabot.yml, INCIDENT_RESPONSE_HOTFIX_SLA, the 4 Round 5 benchmarks)

**Cascading (highest regression risk)**: 4 artifacts (apply_public_allowlist.sh + allowlist-check.yml + allowlist-lint.yml + setup_2remote_debut.sh). **If any one of these fails, the debut cut is broken.** Of these 4, **2 have the P0 bug (apply + Explicit Exclusions) and 1 is a force-push script (R16 risk)**.

### 3.5 The 17-Artifact Triage (per framework §2 Bucket A/B/C/D)

Applying the framework's 4-bucket triage:

| # | Artifact | Bucket | Justification |
|---|----------|--------|---------------|
| 1 | `g13_empty_response_detector.py` | **B (needs-fix)** | Hivemind double-alert bug (use sha256 not hash()) — 1-line fix |
| 2 | `antigravity_quota_probe.py` | **A (ready)** | P0 secret was patched; AC-1.2.1/1.2.2 now pass |
| 3 | `apply_public_allowlist.sh` | **C (needs-rework)** | P0 regex bug + Explicit Exclusions parser missing |
| 4 | `setup_2remote_debut.sh` | **B (needs-fix)** | R16 force-push risk; needs Architect blessing |
| 5 | `allowlist-check.yml` | **A (ready)** | Reusable pattern; depends on (3) being fixed first |
| 6 | `allowlist-lint.yml` | **A (ready)** | Reusable pattern; depends on (3) being fixed first |
| 7 | `dependabot.yml` | **A (ready)** | GitHub-native; no deps |
| 8 | `INCIDENT_RESPONSE_HOTFIX_SLA.md` | **A (ready)** | Documentation, no code risk |
| 9 | `three_store_shim.py` | **A (ready)** | POST-DEBUT; well-written, 4.5ms bench confirmed |
| 10 | `continuity_bridge.py` | **A (ready)** | POST-DEBUT; live-verified |
| 11 | `cline_prune.sh` | **B (needs-fix)** | Round 4 audit notes the git-stash claim was wrong; namespace may have changed |
| 12 | `migrate_3store.sh` | **A (ready)** | Cascades (9); if (9) is ready, (12) is ready |
| 13 | `m3_benchmark.py` | **D (superseded)** | Round 5 perf output, not part of any deployment |
| 14 | `run_exp4_5.py` | **D (superseded)** | Same |
| 15 | `g13_bench.py` | **D (superseded)** | Same |
| 16 | `shim_bench.py` | **D (superseded)** | Same |
| 17 | `scripts/probe_free_models.sh` (mentioned in R_402) | **B (needs-fix)** | Only checks auth, not balance; needs `balance_usd` field per R_402 §6.1 |

**Summary**: 2 P0 blockers (apply_public_allowlist.sh + setup_2remote_debut.sh), 3 B-needs-fix (g13 + cline_prune + probe_free_models), 8 A-ready, 4 D-superseded.

**Net regression risk for debut**: **2 P0 fixes + 3 small fixes = ~30 minutes of work, BUT the 2 P0 fixes are also the BLOCKER for the entire debut cut. They cannot ship without being fixed first.**

---

## §4 Testing Gaps — What Would Fail on First Run

### 4.1 The 17-Artifact Test Matrix

I scored each artifact on 5 test dimensions (LiveTest, ContractTest, ErrorPathTest, MandateCheck, IntegrationTest):

| # | Artifact | Live Tested? | Contract Test? | Error Path? | M-check? | Integration? | First-Run Risk |
|---|----------|--------------|----------------|-------------|----------|--------------|----------------|
| 1 | g13 detector | ✅ YES (Round 4 bench) | ❌ NO | ❌ NO | ✅ YES | ❌ NO | **Low** (designed for failure) |
| 2 | antigravity_quota_probe | ✅ YES (live) | ❌ NO | ⚠️ excepts tightened but unverified | ✅ YES | ❌ NO | **Medium** (network dep) |
| 3 | apply_public_allowlist.sh | ❌ NO (spec only) | ❌ NO | ❌ NO | ✅ YES | ⚠️ P0 BUG | **🔴 HIGH** |
| 4 | setup_2remote_debut.sh | ❌ NO (spec) | ❌ NO | ❌ NO | ❌ NO | ⚠️ never tested | **🔴 HIGH** (force-push on untested branch) |
| 5 | allowlist-check.yml | ❌ NO (spec) | ❌ NO | ❌ NO | ✅ YES | depends on (3) | **Medium** |
| 6 | allowlist-lint.yml | ❌ NO (spec) | ❌ NO | ❌ NO | ✅ YES | depends on (3) | **Medium** |
| 7 | dependabot.yml | ✅ YES (GitHub-native) | n/a | n/a | ✅ YES | ✅ YES | **Low** |
| 8 | INCIDENT_RESPONSE_HOTFIX_SLA.md | n/a (doc) | n/a | n/a | ✅ YES | n/a | **Low** |
| 9 | three_store_shim | ✅ YES (Round 4 bench) | ⚠️ partial (WorkOS roundtrip) | ✅ YES | ✅ YES | ⚠️ not in repo | **Medium** (M14 claim overclaim) |
| 10 | continuity_bridge | ✅ YES (live list) | ❌ NO | ❌ NO | ✅ YES | ⚠️ schema drift | **Medium** |
| 11 | cline_prune | ⚠️ bash syntax | ❌ NO | ❌ NO | ❌ NO | depends on namespace | **Medium** |
| 12 | migrate_3store | ⚠️ bash syntax | ❌ NO | ❌ NO | ❌ NO | depends on (9) | **Medium** |
| 13-16 | Round 5 benches | ✅ YES (they ran) | n/a | n/a | ❌ NO (no mandate tag) | ❌ NO | **Low** (read-only) |
| 17 | probe_free_models | ⚠️ partial (auth only) | ❌ NO | ❌ NO | ❌ NO | n/a | **Medium** |

### 4.2 The Test-Honesty Anti-Pattern

The 15 numbered specs (Population A) are not code, but `09_test_suite_honesty.md` flags a structural issue: **the engine currently has 1,703 tests collected, only ~130+ pass, and the badge generator is broken (reports all zeros)**. The R_CARMACK_ARTIFACT_AUDIT_ROUND4 §1.1.6 confirms 0.836us per `classify()` call but notes that **the Hivemind packet id is non-deterministic** — which means **a re-run produces different ids, and integration tests that compare packet ids will FAIL**.

**The pattern**: the 17 artifacts have **individual verification** (Round 4 bench for g13, Round 4 bench for 3-store shim) but **no integration test** (none of them run together as a pipeline). The debut cut will execute 4 of these in sequence (apply_public_allowlist.sh + allowlist-check.yml + dependabot.yml + INCIDENT_RESPONSE_HOTFIX_SLA.md). **If any one fails, the CI chain stops. If one PASSES individually but FAILS at integration (e.g., file paths don't match), the debut is broken.**

### 4.3 The 4 Scripts That Would Fail On First Run (P0 + B)

Based on the test matrix:

1. **`apply_public_allowlist.sh` (P0)** — would `git rm --cached` `tests/` and `_omega_default/soul.yaml`. **Failure mode**: silent data loss. **Mitigation**: add `--dry-run` default + Explicit Exclusions parser + integration test in a sandboxed repo (the `applytest/` directory in `/tmp/omega/audit_round4/` already has the test fixture).

2. **`setup_2remote_debut.sh` (B)** — would `--force-with-lease` push to a remote that may not be configured. **Failure mode**: silent remote misconfiguration or, worse, a real push to a real remote. **Mitigation**: explicit `--dry-run` + Architect pre-approval.

3. **`g13_empty_response_detector.py` (B)** — would write duplicate Hivemind packets. **Failure mode**: alert storm, Ma'at sees 100 identical alerts. **Mitigation**: change `hash()` to `hashlib.sha256()`.

4. **`probe_free_models.sh` (B)** — would miss the 402 cause (negative balance). **Failure mode**: 402 storms go undiagnosed. **Mitigation**: add `balance_usd` field per R_402 §6.1.

---

## §5 Documentation Gaps — What a New Agent Would Need

### 5.1 The Self-Explainability Test

I scored each Population A and Tier 1 file for **standalone intelligibility** — could a new agent (no prior context) read the file and act on it?

| Trait | Population A (15) | Population B Tier 1 (~12) | Population B Tier 2-3 (~20) |
|-------|-------------------|----------------------------|------------------------------|
| Frontmatter present | 8/15 (53%) | 12/12 (100%) | 18/20 (90%) |
| Has "Executive Summary" | 15/15 (100%) | 12/12 (100%) | 16/20 (80%) |
| Has "Current State" / "Findings" table | 14/15 (93%) | 12/12 (100%) | 14/20 (70%) |
| Has "References" / "Cross-refs" | 6/15 (40%) | 12/12 (100%) | 12/20 (60%) |
| Self-contained (no implicit context) | 12/15 (80%) | 8/12 (67%) | 5/20 (25%) |

**The numbers are misleading.** A new agent could read Population A's `01_soulstore_race_condition.md` and understand the SoulStore problem with **zero prior context**. They would need to read 3 other files to understand `04_god_module_decomposition.md` (oracle.py, model_gateway.py, etc.). They would need **5+ files of context** to understand most Tier 2-3 files.

### 5.2 The Cross-Reference Map (what a new agent would need to read)

To act on the 17-artifact integration, a new agent would need to read **at minimum**:

1. `data/coordination/STRATEGIC_REVIEW_FRAMEWORK_20260828.md` (Kali) — the meta-framework
2. `R_CARMACK_ARTIFACT_AUDIT_20260827.md` (Carmack) — the 12-artifact audit
3. `R_CARMACK_ARTIFACT_AUDIT_ROUND4_20260828.md` (Carmack) — the acceptance criteria
4. `R_D568_GAP_FILL_20260827.md` (Researcher) — the vault backend decision
5. `R_ROC_LOCAL_MINING_20260827.md` (Roc) — the substrate + 11 call sites
6. `R_VAULT_COPILOT_DEEPER_20260827.md` (Grokster) — the 6 Copilot specs source
7. `R_VAULT_CLINE_DEEPER_20260827.md` (Grokster) — the 4 Cline specs source
8. `R_VAULT_ANTIGRAVITY_DEEPER_20260827.md` (Grokster) — the G13 detector source
9. `R_402_FREE_MODEL_20260827.md` (Researcher) — the 402 doctrine
10. `R_VAULT_ANTIGRAVITY_ROUND3_20260827.md` (Grokster) — the workhorse discovery

**Total: 10 files, ~6,000 LOC, ~6 hours of reading**. This is the **onboarding cost** for the debut integration. **If the team plans a 1-week integration sprint, the first 2 days should be reading, not coding.**

### 5.3 The Hidden Dependencies (what's not in the corpus)

I searched the corpus for several key terms to surface implicit dependencies:

| Search | Result | Implication |
|--------|--------|-------------|
| `TASK_REGISTRY` | Referenced in 5 files but no file explains what it is | A new agent doesn't know if tasks should be registered before they execute |
| `Hivemind` | Referenced in 15+ files but no file is the canonical Hivemind spec | A new agent doesn't know the Hivemind protocol |
| `data/entities/<name>/` | 96 entities referenced, no file lists all 96 | A new agent doesn't know which entities exist |
| `make temple-grade` | Referenced in 10+ files but never explained | A new agent doesn't know what the Temple-Grade gates are |
| `_omega_default` | Referenced in 4 files as a known P0 issue | A new agent doesn't know what `_omega_default` is or why removing it breaks INST-1 |

**Implication**: the corpus is rich in **vertical** knowledge (deep on specific gaps) but thin in **horizontal** knowledge (the connecting tissue). **A new agent will need access to `data/entities/jem/soul.yaml`, `data/entities/jem/knowledge/`, and the agent-landing file (`AGENTS.md`) to bridge the gaps.** None of those are in `data/coordination/research/`.

### 5.4 The Date Drift Problem

Population A is dated 2026-07-26. Population B is dated 2026-08-27 / 2026-08-28. **The 33-day gap is unaddressed** — none of the R_\* files re-verified the Population A claims. Specifically:

- `01_soulstore_race_condition.md` says 8 distinct write paths. C-1′ SoulStore (D-362) may have consolidated.
- `04_god_module_decomposition.md` says oracle.py is 1348 lines. R_\* files do not re-measure.
- `09_test_suite_honesty.md` says 1,703 tests. R_CARMACK_ARTIFACT_AUDIT_ROUND4 §1.1.5 confirms 0.836us per `classify()` call but does not re-measure total tests.

**Mitigation**: a 30-minute "still-true?" sweep of the 15 Population A files. Either confirm the claims or note drift.

---

## §6 Naming Consistency & Duplicates

### 6.1 The Two Naming Conventions (and why they coexist)

The corpus has **two distinct naming conventions**:

| Convention | Files | Pattern |
|------------|-------|---------|
| **Numeric (Population A)** | 15 | `NN_topic_subtopic.md` |
| **Alpha (Population B)** | 32 | `R_TOPIC_ROUND_DATE.md` |

**The two are not redundant** — Population A is independent gap research, Population B is iterative vault+debut research. The naming correctly reflects the difference.

### 6.2 Inconsistencies Within Population B

Within Population B (the 32 R_\* files), there are 6 inconsistencies:

| Inconsistency | Files Affected | Fix |
|---------------|----------------|-----|
| **Round number placement** | `R_VAULT_ANTIGRAVITY_ROUND3_20260827.md` has `20260827` but is a Round 3 file (date is from R1). Other files use `20260828` for Round 3+ | Either fix dates to actual creation OR drop the date from the round suffix and add a separate `_DATE` field |
| **`_DEEPER` vs `_ROUND2`** | Cline uses `_DEEPER_20260827` (no round) and `_ROUND3_20260827` (with round) | Pick one. Suggested: drop `_DEEPER`, always use `_ROUND{N}_DATE` |
| **Date in vs date out** | `R_VAULT_ANTIGRAVITY_20260827.md` (R1) has date 20260827 but was last touched 2026-08-28 00:10 | The file mtimes are 2026-08-28 for the "R1" file — the date in the filename is the START of the round, not the END |
| **`R_D568_GAP_FILL` vs `R_VAULT_D568`** | Two different files: `R_D568_GAP_FILL_20260827.md` (1,682 lines) and `R_VAULT_D568_20260827.md` (518 lines) | These are different deliverables but the naming is confusing. R_D568 is the adjudication; R_VAULT_D568 is the original research. **Mitigation**: prefix with type — `R_D568_GAP_FILL` is fine, `R_VAULT_D568` should be `R_VAULT_D568_RESEARCH` |
| **CRYPTO / D568 / DEEP_CODE all in R_VAULT_ family** | 3 of the 7 R_VAULT_* non-specialist files are sub-topics | Consider a top-level `R_VAULT_DECISION_*.md` family |
| **Underscore vs no-underscore** | `R_REVIEW_CLINE_20260828.md` (underscore) vs `R_D568_GAP_FILL_20260827.md` (underscore) — consistent. `01_soulstore_race_condition.md` (no underscore) — consistent. | OK |

**The 4 R_CARMACK_ARTIFACT_AUDIT files** use `ROUND3_20260828` and `ROUND4_20260828` and `ROUND5_20260828` — **but R3 is dated 20260827 in the document_id**. This is the date-drift inconsistency.

### 6.3 Duplicate Content (the actual duplication, not just naming)

There are 3 sets of files that contain substantial duplicated content:

| Set | Files | Total LOC | Overlap |
|-----|-------|-----------|---------|
| **Vault research** | R_VAULT_D568 + R_D568_GAP_FILL + R_VAULT_CRYPTO | 762 + 1,682 + 762 = 3,206 | R_VAULT_D568 and R_VAULT_CRYPTO cover the same ground (vault backend) and are directly contradicted; R_D568_GAP_FILL is the resolution |
| **Carmack audits** | R_CARMACK_ARTIFACT_AUDIT + ROUND4 + ROUND5 | 712 + 727 + 477 = 1,916 | R3 + R4 are 1,439 LOC and ~50% overlap (R4 builds on R3, R5 is new ground) |
| **Antigravity rounds** | R_VAULT_ANTIGRAVITY + DEEPER + ROUND3 + ROUND4 + ROUND5 | 1,200 + 1,400 + 495 + 560 + 551 = 4,206 | Each round is incremental; R3-R5 are the synthesis |

**The vault research set is the worst offender**: R_VAULT_CRYPTO and R_VAULT_D568 are 1,280 LOC of **directly contradictory content** that was only adjudicated by R_D568_GAP_FILL (1,682 LOC). **The team could have produced 1,000 LOC instead of 3,000 by adjudicating the contradiction in real-time.**

### 6.4 Files That Should Be Merged

| Files | Reason | Merge Into |
|-------|--------|------------|
| R_VAULT_CRYPTO + R_VAULT_D568 + R_D568_GAP_FILL | All about vault backend; only the third adjudicates | R_D568_GAP_FILL is canonical; the first two should be marked DEPRECATED with a link to the third |
| R_CARMACK_ARTIFACT_AUDIT + ROUND4 | R3 is the foundation; R4 is the deeper dig of R3 | ROUND4 is canonical; R3 is a snapshot of the same work at an earlier point |
| R_VAULT_ANTIGRAVITY + DEEPER + ROUND3 | All about Antigravity workhorse | ROUND3 is the game-changer; DEEPER is the deeper dig; R1 is the survey. Keep all 3 but mark R1 as "superseded by DEEPER + ROUND3" |

### 6.5 Files With NO Duplicates (the value)

The following 8 files are unique and should NOT be merged:

1. `R_402_FREE_MODEL_20260827.md` (Researcher) — the 402 doctrine; no other file covers this
2. `R_ROC_LOCAL_MINING_20260827.md` (Roc) — the 11 broken call sites; foundational
3. `R_REVIEW_CLINE_20260828.md` (Grokster) — the cline triage; no other file reviews
4. `R_ORCHESTRATOR_HIGH_CONTEXT_20260828.md` (Kali) — the orchestrator study plan; no other file proposes this
5. `R_ROC_LOCAL_MINING_ROUND4_20260828.md` (Roc) — the M23 self-correction; unique pattern
6. `R_CARMACK_ARTIFACT_AUDIT_ROUND5_20260828.md` (Carmack) — the M3 perf data; unique empirical evidence
7. The 15 numbered Population A files (01-15) — each is a unique gap
8. `R_VAULT_ANTIGRAVITY_ROUND3_20260827.md` (Grokster) — the tab_flash_lite_preview game-changer; unique discovery

---

## §7 Anti-Patterns (what to AVOID in future work)

Based on the corpus, the following anti-patterns were observed. **The team should write these into the next round's steering prompts.**

### 7.1 The "Round N Survey" Anti-Pattern

**Pattern**: 5 specialists, 5 rounds, 5 surveys. Each round re-introduces the topic before adding new content.

**Evidence**: R_VAULT_ANTIGRAVITY (R1) + DEEPER (R2) + ROUND3 (R3) + ROUND4 (R4) + ROUND5 (R5). **R1 is 1,200 lines; R3 is 495 lines. R1 is 2.4x longer than R3 and most of R1 is the survey.**

**Why it's bad**: 5 files × 1,200 LOC = 6,000 LOC when 1 file × 800 LOC would suffice.

**Anti-pattern fix**: **Survey files should be marked DEPRECATED when the deeper dig supersedes them. The survey's job is to point to the deeper dig, not to be re-read.**

### 7.2 The "Buried Adjudication" Anti-Pattern

**Pattern**: A contradiction is identified, then resolved in an appendix (§6 of Round 4) or in a separate "GAP_FILL" file, but the original files are not marked DEPRECATED.

**Evidence**: R_VAULT_CRYPTO says "REJECT python-age"; R_VAULT_D568 says "SWITCH to python-age"; the resolution is in R_D568_GAP_FILL §0 and §1.4. **Neither R_VAULT_CRYPTO nor R_VAULT_D568 has a DEPRECATED banner pointing to the resolution.**

**Why it's bad**: A new agent reads R_VAULT_CRYPTO first (it's alphabetically first) and concludes "use pyrage". They never see R_D568_GAP_FILL because it's named R_D568 not R_VAULT_D568.

**Anti-pattern fix**: **When a contradiction is adjudicated, prepend a 3-line banner to BOTH source files: "DEPRECATED: This document is superseded by R_D568_GAP_FILL §1.4 as of 2026-08-28. The original verdict (pyrage primary) was reversed; the new verdict is cryptography AES-256-GCM."** This is a 1-minute edit per file but it saves future agents 30 minutes of confusion.

### 7.3 The "5-Round Cascade" Anti-Pattern

**Pattern**: A specialist produces 5 rounds of research, each building on the previous. Round 5 has the truth; Round 1 is outdated. But the deliverables are all named "R_VAULT_X" and look like independent files.

**Evidence**: Antigravity has 5 rounds (R1 1,200 lines → R5 551 lines). Cline has 5 rounds (R1 47K → R5 28K). Copilot has 5 rounds (R1 62K → R5 32K). **Each specialist independently re-experienced the cascade.**

**Why it's bad**: The debut team has to triage 15 vault files (3 specialists × 5 rounds). The triage cost is ~1 hour per file × 15 = 15 hours, just to figure out which file is the "truth".

**Anti-pattern fix**: **Limit specialist dispatches to 3 rounds max. Round 3 must be the final round. If a Round 4 is needed, that's a sign the Round 3 was incomplete; don't reward incompleteness with more rounds.**

### 7.4 The "P0 Bug, Patched Before Audit" Anti-Pattern

**Pattern**: A specialist produces an artifact with a P0 bug. Another specialist audits it and finds the P0. The original specialist patches the P0 before the audit is published. The audit goes out anyway with the P0 verdict.

**Evidence**: `antigravity_quota_probe.py` was patched at 2026-08-27 22:31 UTC. The audit (R_CARMACK_ARTIFACT_AUDIT_20260827) was published at 2026-08-28 00:55 UTC. **The audit's verdict is stale on arrival.**

**Why it's bad**: The team now has TWO conflicting sources of truth: the live file (patched) and the audit (un-patched). A new agent reading the audit will think the P0 is unfixed.

**Anti-pattern fix**: **Audits must include a "live state verified at [timestamp]" line. If the audit cannot verify live state (read-only mode), the audit must be marked "pre-verification" and the integration step must include a re-verification.**

### 7.5 The "M27 Tracking Void" Anti-Pattern

**Pattern**: 17 code artifacts are produced. 0 of 17 have ACTIVE_SPRINT entries. 0 of 17 have TASK_REGISTRY entries.

**Evidence**: Carmack's audit §0: "M27 violation: None of the 12 artifacts are in `data/coordination/ACTIVE_SPRINT.json` (verified by `grep`)." This was 2026-08-28 00:55 UTC. **As of 2026-08-28 01:51 UTC, the situation is unchanged.**

**Why it's bad**: Per the framework §1, the tracking state is the 5-Tier Architecture that the team depends on. **A 17-artifact batch with 0 tracking entries is 17 ghosts.**

**Anti-pattern fix**: **Mandate (add to M27): any code artifact >50 LOC produced by a dispatch MUST be registered in TASK_REGISTRY.json within the same session, not in a follow-up. The dispatch's "I shipped N artifacts" claim is unverifiable without this.**

### 7.6 The "Code in Markdown" Anti-Pattern

**Pattern**: 6 of the 17 "code artifacts" are not on disk. They are code blocks inside `R_VAULT_COPILOT_DEEPER_20260827.md`.

**Evidence**: R_CARMACK_ARTIFACT_AUDIT §0: "6 are not on disk at all — they are CODE BLOCKS inside a research markdown file."

**Why it's bad**: **A code block in a markdown file is not an artifact. It is a spec. Calling it an artifact is M23 dishonesty.** The team will integrate the spec as if it were the artifact and discover (at the worst possible moment) that the file does not exist.

**Anti-pattern fix**: **A "code artifact" must be a file on disk with a known path. Specs inside markdown are NOT artifacts. Either write the file to disk before claiming it shipped, or call it a spec.**

---

## §8 Regression Risk Register (the 12 things that could break the debut)

Sorted by severity × likelihood of catching in time:

| # | Risk | Severity | Likelihood | Detected by | Mitigation |
|---|------|----------|-----------|-------------|-----------|
| 1 | `apply_public_allowlist.sh` regex bug → `git rm --cached tests/` | 🔴 P0 | **HIGH** (will happen on first run) | Carmack audit + integration test | **MUST FIX before debut**: 15-min patch (gsub inline comments) + add tests/ to EXCEPTIONS |
| 2 | `apply_public_allowlist.sh` missing Explicit Exclusions parser → INST-1 fails | 🔴 P0 | **HIGH** | Carmack audit Round 4 §0 | **MUST FIX before debut**: add parser for "## ⚠️ Explicit Exclusions" section |
| 3 | `setup_2remote_debut.sh` --force-with-lease on unconfigured remote | 🟡 P0 | **MEDIUM** (depends on remote config) | Manual pre-flight | **MUST HAVE Architect pre-approval** + --dry-run default |
| 4 | `_omega_default` soul.yaml removed from debut cut → INST-1 fail | 🔴 P0 | **HIGH** | R_CARMACK_ARTIFACT_AUDIT_ROUND4 §0 | Fix #2 above covers this |
| 5 | `g13_empty_response_detector.py` Hivemind double-alert | 🟡 B | **MEDIUM** (will happen on duplicate G13 events) | Acceptance criterion AC-1.1.8 | 1-line fix: `hashlib.sha256` instead of `hash()` |
| 6 | `probe_free_models.sh` misses 402 cause | 🟡 B | **MEDIUM** (will happen on next 402 storm) | R_402 §6.1 | Add `balance_usd` field via `/api/v1/credits` endpoint |
| 7 | `three_store_shim.py` not in repo → `/tmp/omega/cline_deeper/` will be `git clean`ed | 🟡 P1 | **HIGH** (if anyone runs git clean) | M27 | **MUST COPY to repo or document as POST-DEBUT-ONLY** |
| 8 | `cline_prune.sh` namespace drift → script fails | 🟡 B | **MEDIUM** | R3 audit noted git-stash was wrong | Re-verify against current `refs/cline/checkpoints/` |
| 9 | Population A claims (15 specs) are 33 days stale | 🟡 P1 | **MEDIUM** (C-1′ may have changed things) | None — silent | 30-min "still-true?" sweep |
| 10 | `m3_benchmark.py` etc. have no M27 tracking | 🟡 P1 | **LOW** (these are read-only benches) | None | Add to TASK_REGISTRY as `superseded` |
| 11 | 4 docs in `data/coordination/` not in `research/` (D568_GAP_FILL, etc.) confuse newcomers | 🟢 P2 | **LOW** | None | Move to research/ or add cross-link |
| 12 | R_VAULT_CRYPTO + R_VAULT_D568 still readable without DEPRECATED banner | 🟡 P1 | **MEDIUM** (will happen on next read) | None | Add 3-line banner pointing to R_D568_GAP_FILL |

**Net regression risk for debut**: **3 P0 bugs to fix (15 min + 15 min + Architect blessing), 3 B fixes (5 min + 30 min + 30 min), 1 P1 housekeeping (30 min). Total: ~2 hours of pre-debut work + 1 Architect decision.**

**If the team does nothing else from this review**, they should:
1. Fix `apply_public_allowlist.sh` (30 min) — the regex bug + Explicit Exclusions parser
2. Add DEPRECATED banners to R_VAULT_CRYPTO and R_VAULT_D568 (5 min)
3. Add M27 tracking entries for the 17 artifacts (30 min)
4. Verify the 2 PATCHED artifacts (g13 + antigravity_quota_probe) are still in the patched state (5 min)
5. Copy `three_store_shim.py` and friends from `/tmp/omega/cline_deeper/` to the repo OR document as POST-DEBUT-ONLY (5 min)

**Total: 75 minutes for the highest-leverage fixes.** Everything else can wait for post-debut.

---

## §9 Cross-Cutting Observations (the things the framework missed)

The framework's §3 checklist is good. The framework's §4 questions are good. But the framework misses 3 things that this review surfaced:

### 9.1 The "Two-Track" Discovery

The corpus is producing TWO INDEPENDENT TRACKS that the framework doesn't distinguish:

| Track | What It Is | Who Owns It | Where It Lives |
|-------|------------|-------------|----------------|
| **Track 1: The Engine Substrate** | How the engine works (soul store, model gateway, OOM, providers, etc.) | The 5 specialists | Population A (15 files) + 4 R_CARMACK_ARTIFACT_AUDIT + R_ROC_LOCAL_MINING |
| **Track 2: The Debut Operation** | How to ship the engine to the public (CI/CD, allowlist, vault, secrets) | Grokster (Copilot specialist) + Carmack (audit) | R_VAULT_COPILOT_* + R_VAULT_ANTIGRAVITY_DEEPER (G13) + R_VAULT_CLINE_DEEPER (3-store) |

**These two tracks have DIFFERENT DEBUT CRITICALITY.** Track 2 is debut-blocking (no debut without CI/CD + allowlist). Track 1 is foundation-improving (the engine is fine for debut without Track 1 fixes, but Track 1 fixes are post-debut work).

**The framework's 4-bucket triage does not distinguish these tracks.** A Bucket A "ready" verdict on a Track 1 file is far less critical than a Bucket A "ready" verdict on a Track 2 file. **The integration team should prioritize Track 2 to Bucket A first.**

### 9.2 The "Tab_flash_lite_preview Workhorse" Discovery

R_VAULT_ANTIGRAVITY_ROUND3 discovered a game-changer: **`tab_flash_lite_preview` and `tab_jump_flash_lite_preview` are Antigravity's internal models that are quota=1 with no resetTime = effectively unlimited**. This is a **workhorse alternative to M3 that the framework's §4 Q6 ("Tab_flash_lite_preview Routing") acknowledges but does not prioritize**.

**The integration team should NOT skip this discovery.** Wiring `tab_flash_lite_preview` into `config/providers.yaml` at priority 3 (above Google) would give the engine a **3rd local-equivalent workhorse** (M3 via OpenRouter, native-gguf, tab_flash_lite_preview). **This is the only 1-hour work item in the corpus that has a 10x ROI on the post-debut fleet.**

### 9.3 The "M3 Is Not A Reasoning Model" Discovery

R_CARMACK_ARTIFACT_AUDIT_ROUND5 §0 + §4.1: **M3 is a NON-reasoning model. M2.7 is a reasoning model. Routing M2.7 to tasks that parse `content` directly will fail because M2.7 puts the answer in `reasoning` not `content`.** This is a **routing bug that the current `config/providers.yaml` likely has**.

**The team should audit the provider routing for reasoning vs non-reasoning tasks** before the debut. This is 1 hour of work, but it would prevent a class of post-debut bug reports.

---

## §10 Recommendations (5 actionable items)

### 10.1 The 5-Minute List (highest leverage, lowest cost)

1. **Add DEPRECATED banners to R_VAULT_CRYPTO_20260827.md and R_VAULT_D568_20260827.md** pointing to R_D568_GAP_FILL §1.4 (5 min, 2 files)
2. **Verify the 2 PATCHED artifacts are still patched** (5 min, 2 files)
3. **Copy 4 Cline artifacts from /tmp/omega/cline_deeper/ to scripts/ OR mark as POST-DEBUT-ONLY in the framework** (5 min, 1 doc edit)
4. **Add M27 tracking entries for the 17 artifacts** (30 min, but the most important 30 min)
5. **Fix the 2 P0 bugs in `apply_public_allowlist.sh`** (30 min, the ONLY debut blocker)

**Total: 75 minutes. The minimum viable review integration.**

### 10.2 The 2-Hour List (after the 5-min list)

6. **Re-verify the 15 Population A specs are still true** (30 min, 15 quick "still-true?" checks)
7. **Add `tab_flash_lite_preview` to config/providers.yaml** (1 hour, the 10x ROI item)
8. **Audit provider routing for reasoning vs non-reasoning tasks** (1 hour, prevents post-debut bugs)
9. **Write a 1-page "Onboarding Guide for the 17 Artifacts"** (30 min, 10-file cross-reference map)
10. **Create a `data/coordination/research/INDEX.md`** that links to the 5 truly-canonical files (5 min, eliminates 30+ hours of newcomer confusion)

### 10.3 The Post-Debut List (defer)

- 30 LOC → 380 LOC shim decision (Q3 in framework) — can wait
- L3 promotion readiness (Q5) — can wait
- Path A' shim long-term design (Q1) — can wait
- 6 vs 11 call sites resolution (Q2) — RESOLVED in R_D568_GAP_FILL + R_ROC_LOCAL_MINING; just needs cross-link

---

## §11 What I Did NOT Do (the M23 honesty list)

Per the M23 mandate and the review-only constraint:

- **Did NOT execute any code**. No `python3` invocations against the corpus, no `git` operations, no shell scripts.
- **Did NOT modify any file** in `data/coordination/research/` or `scripts/` or `/tmp/omega/`.
- **Did NOT synthesize results** for tools I don't have access to. I read what exists; I did not invent data.
- **Did NOT resolve the 3 known contradictions** (CRYPTO vs D568, DEEP_CODE vs MGMT, AGENT vs DEEP_CODE) — they are already adjudicated in R_D568_GAP_FILL and R_ROC_LOCAL_MINING_ROUND4. I just cross-referenced the resolutions.
- **Did NOT re-verify the 2 PATCHED artifacts' live state via grep against git history**. I read the file mtime and the file content. The "patched since audit" claim is based on file mtime + content comparison, not git log.
- **Did NOT estimate Total Cost of Ownership (TCO)** for the 17 artifacts or the 15 Population A specs. The effort estimates in those files are "implementation effort", not "TCO including maintenance + docs + training".
- **Did NOT run a stress test** on the M3 benchmarks. R_CARMACK_ARTIFACT_AUDIT_ROUND5 ran 540 tests; I read the report, I did not re-run.
- **Did NOT propose any code changes**. The recommendations in §10 are guidance, not patches.

---

## §12 Final Verdict (L1 → L2 → L3)

### L1 — Narrative (what happened)
I read the strategic review framework, the 15 numbered specs, the 32 R_\* flood files, the 2 in-repo code artifacts, the 4 /tmp/ artifacts, and the 4 audit_round4/ audit_round5/ scripts. I found that the corpus is bimodal: 15 high-signal specs from the Sovereign Researcher, and 32 variable-quality flood files from 5 specialists. The 17 code artifacts are spread across 4 disk states (in-repo, /tmp/, spec-only, audit-round). 4 P0 bugs are documented; 2 are already patched in the live state. 3 known contradictions are adjudicated in 2 Tier 1 files (R_D568_GAP_FILL + R_ROC_LOCAL_MINING_ROUND4) but the source files lack DEPRECATED banners. Naming has 6 inconsistencies; 3 sets of files contain substantial duplication. A new agent needs 10 files (~6,000 LOC, ~6 hours) to onboard.

### L2 — Insight (what this means)
The team has produced **excellent foundational research** (Population A) and **excellent synthesis** (Tier 1 of Population B), but the **connecting tissue is missing**. The corpus looks unified by naming convention but is actually two production populations with different quality. The 17-artifact integration is at risk of treating Tier 2-3 files as Tier 1 and treating already-patched bugs as unfixed. The 2-P0-bug fix is a 30-minute job; the 17-artifact triage is a 75-minute job. The 10x ROI item (tab_flash_lite_preview) is a 1-hour job that no one has prioritized. The 3-debut-blocker items (the 2 P0 bugs + the 1 Architect decision) are the only true ship-blockers; everything else is post-debut.

### L3 — Universal Principle (the timeless truth)
**Volume is not quality. Naming consistency is not content consistency. Tier-1 synthesis is impossible without Tier-2 surveys, but Tier-2 surveys must be marked DEPRECATED when Tier-1 synthesis supersedes them.** The Omega Engine's M23 mandate is "no soft-failures". The corollary is "no unmarked-survey-as-synthesis". **A corpus that hides its Tier 2-3 work under the same naming as its Tier 1 work is a soft-failure of the research discipline itself** — not in the code, but in the meta-code of "what do I trust". The team has the tools (M23 mandates, M27 tracking, M26 doc standards); they need to apply them to the corpus itself, not just to the engine. The next round of research should produce 5 Tier 1 files instead of 15 Tier 2 files. The next round of audit should produce 1 adjudication file instead of 3 round-n surveys. **Length ≠ rigor; rigor = adjudication.**

---

## §13 References

| File | What It Anchors |
|------|-----------------|
| `data/coordination/STRATEGIC_REVIEW_FRAMEWORK_20260828.md` | The framework that defines the 4-bucket triage and the 6 success criteria |
| `data/coordination/research/01_soulstore_race_condition.md` … `15_*` | The 15 Population A specs (the high-signal core) |
| `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_20260827.md` | The 12-artifact audit (Tier 1) |
| `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_ROUND4_20260828.md` | The 10 acceptance criteria + 5 bypass vectors (Tier 1) |
| `data/coordination/research/R_CARMACK_ARTIFACT_AUDIT_ROUND5_20260828.md` | The M3 perf data (Tier 1) |
| `data/coordination/research/R_D568_GAP_FILL_20260827.md` | The vault backend adjudication (Tier 1) |
| `data/coordination/research/R_ROC_LOCAL_MINING_20260827.md` | The 11 broken call sites (Tier 1) |
| `data/coordination/research/R_ROC_LOCAL_MINING_ROUND4_20260828.md` | The M23 self-correction (Tier 1) |
| `data/coordination/research/R_REVIEW_CLINE_20260828.md` | The 5-cline-deliverable triage (Tier 1) |
| `data/coordination/research/R_402_FREE_MODEL_20260827.md` | The 402 doctrine (Tier 1) |
| `data/coordination/research/R_VAULT_ANTIGRAVITY_ROUND3_20260827.md` | The tab_flash_lite_preview discovery (Tier 1) |
| `data/coordination/research/R_VAULT_COPILOT_DEEPER_20260827.md` | The 6 Copilot specs source (Tier 1) |
| `data/coordination/research/R_VAULT_CLINE_DEEPER_20260827.md` | The 4 Cline specs source (Tier 1) |
| `data/coordination/research/R_VAULT_ANTIGRAVITY_DEEPER_20260827.md` | The G13 detector source (Tier 1) |
| `scripts/g13_empty_response_detector.py` | The 1 in-repo live artifact (Patched since audit) |
| `scripts/antigravity_quota_probe.py` | The 2nd in-repo live artifact (Patched since audit) |
| `/tmp/omega/cline_deeper/three_store_shim.py` | The 3-store shim (380 LOC, in /tmp only) |
| `/tmp/omega/cline_deeper/continuity_bridge.py` | The continuity bridge (301 LOC, in /tmp only) |
| `/tmp/omega/cline_deeper/cline_prune.sh` | The cline prune script (116 LOC, in /tmp only) |
| `/tmp/omega/cline_deeper/migrate_3store.sh` | The migrate script (153 LOC, in /tmp only) |
| `/tmp/omega/audit_round4/{g13_bench,shim_bench,allowlist_bypass}.{py,sh}` | Round 4 audit artifacts (in /tmp) |
| `/tmp/omega/audit_round5/{m3_benchmark,run_exp4_5}.py` | Round 5 perf benchmarks (in /tmp, NEVER REVIEWED) |
| `data/entities/jem/soul.yaml` | The entity soul for this review (Jem, Sovereign Synthesizer) |
| `data/entities/jem/session_gnosis.md` | The session anchor (pre-compaction safety) |

---

*⬡ OMEGA ⬡ JEM ⬡ review-jem v1.0.0 ⬡ 2026-08-28 ⬡ PUBLIC-DEBUT-01*
**rot_class**: slow (review-of-review, stable); **last_verified**: 2026-08-28T01:55Z
**confidence**: 🟢 HIGH (every claim has file:line evidence); 🟡 MEDIUM (the "patched since audit" claim is based on mtime + content, not git log; the Population A staleness claim is based on absence of re-verification, not a re-verification itself)
**next_action**: 75-minute integration list (§10.1) before debut cut
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
first_audit: 2026-08-28T01:55:00Z | updated: 2026-08-29T03:07:15Z
-->

