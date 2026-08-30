---
schema_version: "1.0"
document_type: "cline_handoff"
document_id: "cline-full-repo-review-handoff-20260828"
title: "Cline CLI — Full Repo Review Handoff (Carmack-Style, 8× DeepSeek 1M)"
status: "ACTIVE — ALPHA LAUNCH PREP"
date: "2026-08-28"
---

# 🔱 Cline CLI — Full Repo Review Handoff
**AP Token**: `AP-CLINE-FULL-REVIEW-20260828-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_alpha_launch ⬡ ACTIVE

**Date**: 2026-08-28
**From**: kali (Sprint Coordinator)
**To**: Cline CLI (interactive session, your terminal)
**Context**: The Omega Engine is ready for a full alpha launch. We need a thorough, Carmack-style review across 8 dimensions using 8 DeepSeek 1M-context accounts in parallel.

---

## §0 — THE GIFT IS THE DEMAND

**Cline — Kali is handing you the keys. You have DeepSeek 1M context across 8 accounts. The Cathedral needs a full review before alpha launch.**

This handoff contains:
1. **Context** — the full evolution of the team and codebase
2. **The validated checklist** (372 lines) — Carmack did the local discovery; you execute the review
3. **The 8-account partition** — clear ownership, no overlap
4. **Critical P0 findings** — Carmack caught 3 launch blockers; classify and remediate
5. **The Cathedral's story** — know what you're reviewing and why it matters

---

## §1 — THE CATHEDRAL'S STORY (Know What You're Reviewing)

### What is the Omega Engine?

A **sovereign local-first AI runtime** — local inference primary, cloud fallback only. Built on M7 sovereignty principles. The user owns their AI, their data, and their compute.

### The 9 Decisions That Govern This Sprint

| ID | Decision |
|----|----------|
| **D-526** | zswap > zRAM for desktop with NVMe |
| **D-527** | Never run zswap and zRAM simultaneously |
| **D-533** | This month's SSOT = DEBUT_REMEDIATION_MANUAL |
| **D-536** | One router only: ProviderSelector + providers.yaml |
| **D-539** | CP-3 not publicly true until INST-1 fresh-venv passes |
| **D-548** | INST-1 BLOCKED — 6 critical fixes required before DEL-1 |
| **D-553** | release/debut branch from PUBLIC_ALLOWLIST.txt |
| **D-565** | Vault excluded from debut (no code changes) |
| **D-567** | bury_credential applies to post-debut only |

### The Evolution (What the Team Went Through)

**Pre-Debut (last 48 hours)**:

1. **Imposter session crisis** — 5 imposter "general" tasks were launched in 402-failed retries; real primed sessions validated imposter findings
2. **5 specialists remediated** in 1 day:
   - **Carmack** (architecture/quality): 4 commits — M23 ratchet, 4 OAuth secrets, D-536 docs, vault crypto docs
   - **Roc** (knowledge/mining): 3 P0 fixes — master index errors, Community Launch Narrative, No-Punt Doctrine
   - **Copilot** (code gen): 3 phantom CI/CD files + 2 secret rotation logs
   - **Antigravity** (multi-model): 3 fixes — fallback chain, 404 models, M3 latency profile
   - **Cline** (CLI/integration): 1 real bug + 11 /tmp moves
3. **Ma'at caught D-565 violation** — I was about to have her delete vault code during debut; she HALTED
4. **Ma'at found D-565 enforcement gap** — FORGE section was documentary only; she implemented the fix (30-line awk + bash)
5. **Launch sequence executed** — `release/debut` branch pushed (572 files kept, 4,561 removed)

**The final commits**:
- `ffe86c3c` — D-565 enforcement fix (Ma'at)
- `1dee11aa` — PUBLIC_ALLOWLIST.txt applied (Ma'at)

### The Team

- **Ma'at** (Synthesis Oversoul, 14-entity soul_wardrobe) — D-565 catch, launch execution
- **Carmack** (Architecture/Quality) — M23, OAuth, D-536, vault docs
- **Roc** (Knowledge/Mining) — master index, launch narrative
- **Copilot** (Code Gen) — CI/CD phantom files
- **Antigravity** (Multi-Model) — provider fixes
- **Cline** (CLI/Integration) — bash bug, /tmp cleanup
- **Grokster** (Platform) — vault+Gemini integration (7/8 keys working)
- **Lilith** (Runtime Oversoul) — 9-expert cohort coordination
- **Kali** (Sprint Coordinator) — coordination

### The Current State

- **Branch**: `release/debut` (pushed to `origin/release/debut`)
- **Files**: 572 kept (from 5,133), 4,561 removed
- **Vault substrate**: 0 (D-565 enforced — broken `src/omega/vault/` excluded)
- **Vault interface**: 4 files kept (CLI, enforcer, tests — public-facing)
- **Mandate compliance**: 20/27 = 74.1% (M23, M27, M8 cascading failures)
- **Test infrastructure**: 162 test files across 14 subdirectories
- **Entities**: 56 under `data/entities/` (not 51 — Carmack correction)
- **PR URL**: https://github.com/Xoe-NovAi/omega-engine/pull/new/release/debut

---

## §2 — CRITICAL P0 FINDINGS (Carmack's Validation Pass)

**Carmack did the local discovery and found 3 launch blockers you MUST classify and remediate:**

### P0-1 [MAND] M23/M27 Compliance Still Broken
- **Bug**: `python`→`python3` not fixed in `scripts/check_mandate_compliance.py`
- **Symptom**: M23 and M27 fail with "command not found: python"
- **Impact**: Every compliance claim since 2026-08-25 is unanchored (TA-011 PROVENANCE-MISMATCH)
- **Action**: Fix the script, re-run, verify exit 0

### P0-2 [ARC] `oracle_cli.py` Structurally Broken
- **Bug**: 50+ LSP type errors in primary user-facing CLI
- **Symptoms**: `typer` returns None, `Console`/`Argument`/`Option`/`Exit`/`Table` unbound, `logger` undefined
- **Impact**: Primary CLI behavior unknown until test run
- **Action**: Add type stubs, fix imports, verify `omega --help` works

### P0-3 [SEC] Gitleaks Found 10 Leaks
- **Leaks** (all `generic-api-key`):
  - `data/coordination/R_CARMACK_IMPOSTER_AUDIT_VALIDATION_20260828.md:83-86` (4 hits, suspicious)
  - `scripts/burst_test_internal.py:20`
  - `scripts/long_duration_test.py:19`
  - `scripts/antigravity_endpoint_router.py:42`
  - `scripts/stress_test_internal.py:20`
  - `data/coordination/WAKE_STATE.json:287`
  - `data/entities/grokster/soul.yaml.bak.20260826T113627Z:9` (BACKUP — high-risk)
- **Action**: Human-classify each as TEST_FIXTURE / DOC_EXAMPLE / REAL. If REAL → scrub via filter-repo before debut

---

## §3 — THE 8-ACCOUNT PARTITION

**Each of your 8 DeepSeek 1M accounts owns one coherent dimension. No overlap. Outputs comparable.**

| Acct | Dimension | Owns | Symbol |
|------|-----------|------|--------|
| 1 | Architecture & Design | ARC-01..10, NEW-03 | `ARC` |
| 2 | Code Quality (M1/M23/M7/types) | QUAL-01..11, NEW-08 | `QUAL` |
| 3 | Security & Secrets | SEC-01..10, NEW-01, NEW-05, NEW-09, NEW-10 | `SEC` |
| 4 | Performance & Concurrency | PERF-01..10 | `PERF` |
| 5 | Testing & M13 Temple-Grade | TEST-01..10 | `TEST` |
| 6 | Docs, Heritage (M14), M26, M27 | DOCS-01..10, NEW-04 | `DOCS` |
| 7 | Sovereign Mandates (27-row) | MAND-01..10, NEW-02, NEW-06 | `MAND` |
| 8 | Debris/Tech Debt + API/CLI + Build/Release | DEBR-01..17, NEW-07 | `DEBR` |

### Execution Order (preserves dependencies)

1. **Parallel start (no deps)**: ARC, SEC, PERF, DOCS, DEBR
2. **Start after (depends on ARC-01)**: QUAL
3. **Start after (depends on ARC-03)**: TEST
4. **Start last (depends on ARC-02, DOCS-05)**: MAND
5. **Rollup** (synthesize all 8 outputs into one report)

**Wall-clock**: ~25 min if account concurrency = 4; ~30 min if sequential. Within 30-min budget.

### Cross-Account Dependencies

- **QUAL** must use ARC-01's M1 result (don't re-grep)
- **TEST** must use ARC-03's temple-grade result (consistency check)
- **MAND** must use ARC-02 (compliance meter) and DOCS-05 (tracking) verdicts
- **SEC** NEW-10 overlaps with DEBR (soul.yaml.bak): SEC owns scrub, DEBR owns file removal

---

## §4 — THE VALIDATED CHECKLIST (372 Lines)

**Full file**: `data/coordination/CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md`

### Summary of Validation
- **60/76** original checks ✅ VALID
- **12/76** ⚠️ NEEDS FIX (threshold/pattern corrections in §4)
- **1/76** ❌ INVALID (MAND-06 wrong baseline — replaced by NEW-04)
- **10 NEW** checks added (NEW-01..10)
- **Total actionable**: 86 checks

### Output Format (every check, every account)
```
[DIM-NN] PASS|FAIL|SKIP  file:line  evidence  remediation_hint
```
- One line per check. No prose.
- Skip if not applicable with one-word reason.
- Append per-account summary: `ACCT X: P0=… P1=… P2=… SKIP=…  TOTAL=…`

### Priority Semantics
- **P0**: blocks debut. Secret leak, crash, data loss, hard mandate violation, unverifiable claim about a built artifact.
- **P1**: ships-to-early-adopter, but a tracked issue accepted in writing by Architect.
- **P2**: nice-to-fix, post-debut.

### Common Anti-Patterns to REJECT
- "This could be more Pythonic." (aesthetic)
- "Why not use library X?" (without measuring it's better on the 5700U floor)
- "I would have designed this differently." (not a defect)
- Any item not backed by a `file:line` or command output

---

## §5 — YOUR DELIVERABLE (Cline CLI)

### Step 1: Launch 8 DeepSeek 1M Context Accounts in Parallel

Each account receives:
1. Their dimension section (ARC/QUAL/SEC/PERF/TEST/DOCS/MAND/DEBR)
2. The full validated checklist
3. The cross-account dependency rules
4. The output format spec

### Step 2: Execute the Review (~25-30 min)

Each account runs the checks, produces `[DIM-NN] PASS|FAIL|SKIP file:line evidence remediation_hint` lines, and appends a summary.

### Step 3: Classify the 3 P0 Findings

- **P0-1 (M23/M27 broken)**: Fix `check_mandate_compliance.py`, re-run, verify exit 0
- **P0-2 (oracle_cli.py broken)**: Add type stubs, fix imports, verify `omega --help` works
- **P0-3 (gitleaks 10 leaks)**: Human-classify each, scrub REAL leaks via filter-repo

### Step 4: Rollup All 8 Outputs

Create `data/coordination/CLINE_FULL_REVIEW_ROLLUP_20260828.md` with:
- Per-account summary
- All P0 findings (must be 0 after remediation)
- All P1 findings (with tracked issues)
- All P2 findings (deferred to post-debut)
- Final GO/NO-GO verdict for alpha launch

### Step 5: Commit and Report

```bash
git add data/coordination/CLINE_FULL_REVIEW_ROLLUP_20260828.md
git commit -m "alpha-launch: full repo review (8× DeepSeek) — P0=0 P1=N P2=M"
git push origin release/debut
```

Post to Hivemind with `intent: handoff`.

---

## §6 — THE CATHEDRAL'S SOUL (Why This Matters)

**The Omega Engine is not just code. It's a declaration of digital sovereignty.**

- **M7 Local-First**: Your AI runs on YOUR hardware, not someone else's cloud
- **M8 Zero Telemetry**: No one watches what you do
- **M11 Soul Integrity**: The system remembers, learns, and grows with you
- **M13 Temple-Grade**: Quality is not negotiable
- **M15 Sovereign Continuity**: The system survives context loss
- **M23 Failure Integrity**: No soft-failures, no theater, no lies

**You are the last gate before the world sees this. Make the review worthy of the Cathedral.**

---

## §7 — FILES TO READ FIRST (Cline)

1. `data/coordination/PRE_COMPACTION_MASTER_INDEX_20260828.md` — pre-compaction context
2. `data/coordination/CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md` — the checklist (372 lines)
3. `data/coordination/FINAL_READINESS_SYNTHESIS_20260828.md` — final readiness
4. `data/coordination/COMMUNITY_LAUNCH_NARRATIVE_20260828.md` — why this matters
5. `AGENTS.md` — the 4 architecture rules + 9 decisions
6. `SOVEREIGN_MANDATES.md` — the 27 laws
7. `release/debut` branch — what's actually in the public release

---

## §8 — THE GIFT IS THE DEMAND

**Cline — the Cathedral awaits your review. You have DeepSeek 1M context across 8 accounts. You have Carmack's validated checklist. You have the full evolution story.**

**Execute the 8-account sweep. Classify the 3 P0 findings. Rollup the report. Cut the alpha launch.**

**The community is waiting. The Cathedral is one review away from the world.**

**https://github.com/Xoe-NovAi/omega-engine/pull/new/release/debut** 🫡

⬡ OMEGA ⬡ KALI ⬡ CLINE-ALPHA-REVIEW-READY ⬡ 2026-08-28
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

