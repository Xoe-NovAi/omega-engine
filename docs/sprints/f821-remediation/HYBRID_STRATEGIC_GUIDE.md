# Ω F821 Hybrid Strategic Guide — DeepSeek V4 Synthesis of Sonnet 4.6 + Opus 4.6
**AP Token**: `AP-F821-HYBRID-SYNTHESIS-v1.0.0`
**Author**: DeepSeek V4 Flash Max Thinking (Synthesizing Model — Crucible L2.5)
**Date**: 2026-08-16
**Status**: CANONICAL — supersedes both source documents for execution purposes
**Cost Justification**: This synthesis cost a fraction of a second Opus generation.
The L2.5 Synthesis Layer extracts the best of both planners, resolves their
conflicts, adds execution-learned insights, and emits ONE machine-executable plan —
saving Opus token budget for genuinely novel analysis.

---

## 0. Document Architecture — The Three-Layer Stack

| Document | Model | Role | Read By |
|---|---|---|---|
| `F821_REMEDIATION_PLAN.md` | Sonnet 4.6 | Tactical (per-file edits) | Humans, DPO extraction |
| `OPUS_STRATEGIC_GUIDE.md` | Opus 4.6 | Strategic (root cause, gates, teaching) | Humans, DPO extraction |
| `HYBRID_STRATEGIC_GUIDE.md` (THIS) | DeepSeek V4 | **Synthesis** — unified truth, conflict resolution, execution-learned enhancements | Humans, DPO extraction |
| `AGENT_EXECUTION_PLAN.md` | DeepSeek V4 | **Machine-executable** — the ONLY document an executing agent reads | **Execution agents ONLY** |

> **Teaching note for the fleet**: Three planners produce three documents — but an
> executing agent must read exactly ONE. The synthesis layer exists to collapse
> N documents into 1 executable contract. This is the **Single Source of Truth
> for Execution** rule (Pattern 9).

---

## 1. Synthesis Methodology

### 1.1. What Was Unified

| Layer | From Sonnet 4.6 | From Opus 4.6 |
|---|---|---|
| Import map | ✅ 13 symbols, grep-verified | ✅ Canonical paths confirmed |
| `__future__` status per file | ✅ Full table | (implicit) |
| Root cause analysis | (implicit) | ✅ 5 findings |
| Prevention gates | (absent) | ✅ H-1..H-4 |
| Teaching patterns | (absent) | ✅ 7 patterns |
| Anti-patterns | ✅ Appendix B (table) | ✅ 6 detailed anti-patterns |
| Execution order | ✅ Phases 2-5 | ✅ Phases 2-6 |
| Commit strategy | (absent) | ✅ 2 atomic commits |

### 1.2. Conflict Resolution Table

| # | Conflict | Sonnet Says | Opus Says | **Resolution** |
|---|---|---|---|---|
| C-1 | `extractors.py` fix | Add `ValidationError` to import block at lines 7-13 | Delete lines 1-62 (duplication), add to surviving block | **Opus H-5 wins.** Sonnet's placement would be overwritten by the second import block — the fix would appear in the diff but fail at runtime. |
| C-2 | `scorecard.py` `__future__` status | Table says "❌ NO" then corrects to "**YES**" (line 15) | (not addressed) | **Resolved: HAS `from __future__ import annotations` at line 15.** The Sonnet contradiction is a documentation defect — the synthesis resolves it. |
| C-3 | Commit count | (absent) | 2 atomic commits | **Opus wins**, enhanced with Socratic markers (see §11). |
| C-4 | `regression_watcher.py` | Rename call site to `_get_obs_engine()` | Same (Finding 1) | **Agreement** — call-site fix, never a new import. |
| C-5 | `ModelUpdaterWorker` | Inline import inside `if enabled:` | Same (Pattern 2) | **Agreement** — inline, never top-level. |

### 1.3. What the Synthesis Adds (Not In Either Source)

1. **Execution-Model Psychology** (§2 F6): Why Roc Racoon copied `# <-- ADD THIS LINE`
   comments into production code and attempted to merge both guides. This failure
   mode is now a documented finding, a teaching pattern, and an anti-pattern.
2. **The Dual-Artifact Rule** (§3 H-7): Planners emit Artifact A (cognitive) and
   Artifact B (executable). Execution agents read only B.
3. **The Socratic Commit Contract** (§3 H-8): Integrates the `scripts/socratic_commit_check.py`
   hook — every `fix:` commit must carry `Root Cause:` and `Prevention Gate:` markers.
4. **Bug-to-Feature Alchemy** (§7): The F821 bug class is now six distinct features.
5. **Post-Execution Verification** (§8): Actual results from Roc's run (commit `3f4d3c82`)
   are folded into the baseline.

---

## 2. Unified Forensic Findings (6 Findings)

### Finding 1 — The Makefile Is The Root Cause (Opus)
`Makefile` lines 166-172 carry `--ignore=F821` with the false claim that F821s are
"not actionable lint failures." We proved 10 of 27 are real `NameError` runtime bugs
and 1 is a `UnboundLocalError` scope bug. **Root cause chain**: some F821s are
legitimate (TYPE_CHECKING) → agent assumed ALL are → blanket suppression → real bugs
accumulated silently → no gate caught them.

> **The lesson**: Never suppress an entire violation class to fix some false
> positives. Fix the false positives structurally, then keep the gate active.

### Finding 2 — `extractors.py` Contains A Full-File Duplication (Opus)
Lines 1-62 are identical to lines 64-124 (two docstrings, two import blocks, two
`EXTRACTION_SCHEMA` dicts). The first import block lacks `tenacity`, `json_repair`,
and `ValidationError`. Python executes both; the second overwrites the first. This
file alone generates **12 F811 violations** (15% of codebase total).

### Finding 3 — `discovery.py` Has A Duplicate `OmegaError` Import (Opus)
`OmegaError` appears on line 27 AND line 28 — an F811 redefinition signaling a
copy-paste error. The 16-class error mega-block is itself a code smell.

### Finding 4 — CI/Local/Pre-Commit Divergence On F821 (Opus)
`make lint` suppresses F821; `ci.yml` lint uses `--exit-zero` (non-blocking);
`test.yml` uses `continue-on-error: true`; pre-commit has no F821 hook. **Result**:
an F821 can pass every gate in the pipeline. A lint rule that exists but is
suppressed everywhere is worse than no rule at all.

### Finding 5 — The `# type: ignore` And `# noqa` Residue (Opus)
Most suppressions are legitimate (optional imports, intentional re-exports). The
distinction: **structural suppressions** (hiding a bug) → fix and remove;
**semantic suppressions** (telling the tool "I know what I'm doing") → keep with comment.
The Makefile `--ignore=F821` is structural. The `# noqa: F401` on re-exports is semantic.

### Finding 6 — Execution Model Contamination (NEW — DeepSeek synthesis)
**Evidence**: Roc Racoon's actual execution (2026-08-16) revealed two failure modes
the planners did not anticipate:
1. **Instructional comment copying**: The executing agent copied pedagogical markers
   like `# <-- ADD THIS LINE` from the Sonnet plan directly into production code.
   Execution models are literal constraint-satisfaction engines — they treat
   instructional scaffolding as part of the artifact.
2. **Multi-document merge**: The executing agent's thinking showed it intended to
   implement "according to *both* the Sonnet 4.6 and Opus 4.6 guides" — even though
   Opus superseded Sonnet. Execution models lack the contextual judgment to know
   which document wins.

**Root cause chain**:
```
1. Planners emit pedagogical documents (with teaching markers) → TRUE
2. Execution agents read those documents → TRUE
3. Execution agents cannot distinguish "instruction to the reader" from "code to write" → FAILURE
4. Execution agents cannot resolve document hierarchy (which supersedes which) → FAILURE
5. Result: contaminated code + hallucinated merge of conflicting plans
```

> **The lesson**: The gap between Frontier Intelligence (planning) and Execution
> Intelligence (doing) is not just capability — it is **context curation**. The
> orchestrator must curate the execution agent's context window with ruthless
> precision: one document, zero pedagogical markers, zero alternatives.

---

## 3. Unified Recommendations (H-1..H-8)

### H-1 — Remove `--ignore=F821` From The Makefile (Opus, CRITICAL)
Remove both `--ignore=F821` flags from the `lint` target. Update the comment from
"not actionable" to "hard gate" with the AP token for traceability.

### H-2 — Add F821 Pre-Commit Hook (Opus, HIGH)
Add `omega-check-f821-undefined-names` to `.pre-commit-config.yaml`:
```yaml
      - id: omega-check-f821-undefined-names
        name: Check F821 (no undefined names)
        entry: bash -c 'python -m flake8 src/omega/ --select=F821 --count --quiet && echo "✅ No F821 violations"'
        language: system
        pass_filenames: false
        always_run: true
```
Design: `--quiet` for clean stdout, `--count` for non-zero exit on violations,
`pass_filenames: false` to scan the whole tree (catches indirect effects).

### H-3 — Update Frontier Coding Standards (Opus, MEDIUM)
Add §8 "Prevention Gates" to `docs/standards/FRONTIER_AI_CODING_STANDARDS.md`:
- 8.1 The Three-Step Close (fix → remove suppression → add gate)
- 8.2 Ban on Class-Wide Suppression
- 8.3 Opportunistic Cleanup (fix adjacent violations in the same edit)

### H-4 — Verify CI Lint Does Not Suppress F821 (Opus, MEDIUM)
`ci.yml` line 35 already selects `F82x` with no `--ignore`. Add a comment for
traceability. Defense in depth.

### H-5 — Fix `extractors.py` File Duplication (Opus, HIGH — Carmack leverage)
Delete lines 1-62 (first docstring + first import block + first EXTRACTION_SCHEMA),
delete the redundant second docstring (lines 64-65), add `from pydantic import
ValidationError` to the surviving block. Eliminates 12 F811s, fixes the F821,
removes 63 lines of dead code.

### H-6 — Fix `discovery.py` Duplicate `OmegaError` (Opus, LOW — opportunistic)
Remove the duplicate `OmegaError` from line 28 while adding `import yaml`.

### H-7 — The Dual-Artifact Output Rule (NEW — DeepSeek synthesis)
Every Crucible run MUST emit two artifacts:
- **Artifact A (Cognitive Guide)**: forensic analysis, teaching patterns, anti-patterns.
  Read by humans and the DPO extractor. **Execution agents are FORBIDDEN from reading it.**
- **Artifact B (Machine Patch)**: a strict, comment-free, unambiguous execution plan.
  The ONLY document the executing agent reads.

**Enforcement**: The handoff prompt MUST state: *"Read ONLY `AGENT_EXECUTION_PLAN.md`.
Do not read any other document in this sprint directory."* The orchestrator (Kali)
is responsible for this curation.

### H-8 — The Socratic Commit Contract (NEW — DeepSeek synthesis)
Every `fix:` / `bug:` / `hotfix:` commit MUST carry two markers (enforced by
`scripts/socratic_commit_check.py` via `.git/hooks/commit-msg`):
```
Root Cause: <Why this bug occurred systemically>
Prevention Gate: <What prevents it from returning>
```
A fix without a prevention gate is a temporary patch. The commit message is the
final gate in the pipeline.

---

## 4. Unified Execution Order (Canonical — Conflicts Resolved)

```
Phase 2 (Real Imports — 10 files)
├── R-1:  infra/subagent_pool/orchestrator.py → add `from pathlib import Path`
├── R-2:  ingestion/extractors.py → DELETE lines 1-62 + add `from pydantic import ValidationError` to surviving block   [C-1: Opus H-5 wins]
├── R-3:  library/discovery.py → add `import yaml` + deduplicate OmegaError
├── R-4:  library/rate_limiter.py → add `import anyio`
├── R-5:  observability/otel_exporter.py → add `import anyio`
├── R-6:  observability/regression_watcher.py → rename `get_engine()` → `_get_obs_engine()` at line 98
├── R-7:  oracle/feed_utils.py → extend `from datetime import datetime` → `from datetime import datetime, timezone`
├── R-8:  oracle/iterative_research.py → add `import re`
├── R-9:  oracle/orchestrator.py → add inline `from omega.workers.model_updater import ModelUpdaterWorker` inside `if enabled:` branch
└── R-10: oracle/subagent_dispatcher.py → add `import anyio`

Phase 3 (Blast Radius — 1 file)
└── B-1:  research/scorecard.py → move `tier_start = time.perf_counter()` before `try` block   [C-2: file HAS __future__ annotations]

Phase 4 (TYPE_CHECKING — 5 files)
├── T-1:  ics.py → TYPE_CHECKING block for OracleResponse, remove `# type: ignore` (HAS __future__ → quotes optional)
├── T-2:  ingestion/pipeline.py → TYPE_CHECKING block for AsyncCircuitBreaker (NO __future__ → keep quotes)
├── T-3:  oracle/backends/remote_provider.py → TYPE_CHECKING block for MetricsDB (NO __future__ → keep quotes; dual import INTENTIONAL)
├── T-4:  oracle/model_gateway.py → TYPE_CHECKING block for SpeculativeDecodeConfig (NO __future__ → keep quotes)
└── T-5:  research/sandbox.py → TYPE_CHECKING block for ResearchProposal (NO __future__ → keep quotes)

Phase 5 (Verification — 3 gates)
├── Gate 1: flake8 src/omega/ --select=F821 → 0 violations
├── Gate 2: Python import smoke test → all 16 modules import cleanly
└── Gate 3: make test → no regressions

Phase 6 (Hardening — 4 items + 2 new)
├── H-1:  Makefile → remove --ignore=F821
├── H-2:  .pre-commit-config.yaml → add F821 pre-commit hook
├── H-3:  FRONTIER_AI_CODING_STANDARDS.md → add §8 Prevention Gates
├── H-4:  ci.yml → verify/comment F821 enforcement
├── H-7:  [PROCESS] Dual-Artifact Rule — emit Artifact B for the executing agent
└── H-8:  [PROCESS] Socratic Commit Contract — commit messages carry Root Cause + Prevention Gate
```

---

## 5. Teaching Patterns For Local Models (9 Patterns)

> **Purpose**: Extractable principles for fine-tuning local models or few-shot
> prompting. Format: SITUATION → NAIVE RESPONSE → CORRECT RESPONSE → WHY.

### Pattern 1: Lazy Import Wrapper Misuse (Opus)
**Situation**: File defines `_get_obs_engine()` as a lazy wrapper; later code calls `get_engine()` directly.
**Naive**: "F821 on `get_engine` — add `from omega.observability import get_engine`"
**Correct**: "Rename the call site to `_get_obs_engine()`. Adding a top-level import creates the circular dependency the wrapper was designed to prevent."
**Why**: Lazy import wrappers exist for a reason. Look for `_get_*` / `_lazy_*` helpers before adding imports.

### Pattern 2: Inline Import Preservation (Opus)
**Situation**: `ModelUpdaterWorker` used inside `if updater_cfg.get("enabled"):` branch.
**Naive**: "Add to top-level import block."
**Correct**: "Inline import inside the branch, next to the existing inline import."
**Why**: Heavy module loads inference deps. Top-level import taxes every orchestrator init even when disabled. On 15W TDP, cold-start import tax is ~3.5s.

### Pattern 3: Extend vs. Duplicate Imports (Opus)
**Situation**: `feed_utils.py` has `from datetime import datetime`, needs `timezone`.
**Naive**: "Add `from datetime import timezone` as a new line."
**Correct**: "Extend: `from datetime import datetime, timezone`."
**Why**: Two lines from the same module trigger F811 and signal ad-hoc imports.

### Pattern 4: File Duplication Detection (Opus)
**Situation**: `extractors.py` has `ValidationError` F821 at line 142.
**Naive**: "Add import to the block at line 7."
**Correct**: "The file has TWO import blocks; the second is effective. Delete lines 1-62, add `ValidationError` to the surviving block."
**Why**: Adding to the first block gets overwritten by the second — fix appears in diff but fails at runtime.

### Pattern 5: Scope Variable Pre-Initialization (Opus)
**Situation**: `tier_start` used in `except` branches, assigned inside `try`.
**Naive**: "Add `tier_start = 0` at top of function."
**Correct**: "Add `tier_start = time.perf_counter()` immediately before `try`."
**Why**: Real value (not dummy) for accurate error-path timing; before `try` (not top) to measure only the risky operation; never inside `try` (the bug itself).

### Pattern 6: TYPE_CHECKING Contract (Opus)
**Situation**: String annotation `"OracleResponse"` triggers F821.
**Naive**: "Add top-level import."
**Correct**: "`if TYPE_CHECKING:` block — available to type checker, not imported at runtime."
**Why**: Avoids circular imports. Files WITH `from __future__ import annotations` can drop quotes; files WITHOUT must keep them. **Check the `__future__` status FIRST — the single most common mistake.**

### Pattern 7: Systemic Prevention (The "Never Again" Rule) (Opus)
**Situation**: 27 F821s fixed, all tests pass. Victory?
**Naive**: "Commit the fix. Sprint complete."
**Correct**: "Remove the suppression, add the gate, verify CI, THEN commit."
**Why**: A fix without a prevention gate is a temporary fix. The violations will return the moment the next agent adds a forward reference without a guard.

### Pattern 8: Instructional Comment Contamination (NEW — DeepSeek synthesis)
**Situation**: An execution agent is given a plan containing pedagogical markers like `# <-- ADD THIS LINE`.
**Naive**: "Copy the marker into the production code alongside the edit."
**Correct**: "The marker is instruction to the reader, not part of the artifact. Write ONLY the code. The plan's markers are scaffolding — discard them."
**Why**: Execution models are literal constraint-satisfaction engines. Pedagogical scaffolding in plans becomes contamination in code. Plans for execution agents must be comment-free (Artifact B), and agents must strip any residual markers.
**Signal to watch for**: Any `# <--`, `# ADD`, `# CHANGE`, `# TODO(plan)` marker in a plan document → it is scaffolding, never code.

### Pattern 9: Single Source of Truth for Execution (NEW — DeepSeek synthesis)
**Situation**: An agent is handed two documents: a tactical plan (Sonnet) and a strategic guide (Opus) that supersedes it.
**Naive**: "Implement according to *both* documents, merging their instructions."
**Correct**: "Read ONLY the designated execution artifact. If a document is superseded, it is not read. The orchestrator curates the context."
**Why**: Execution models cannot resolve document hierarchy. Merging conflicting plans produces hallucinated hybrids. One document = one truth = deterministic execution.

---

## 6. Anti-Pattern Catalog (7 Anti-Patterns)

### Anti-Pattern 1: Blanket Suppression (Opus)
```makefile
# ❌ WRONG: Suppress an entire violation class
flake8 src/omega/ --ignore=F821
# ✅ RIGHT: Fix the violations, keep the gate
flake8 src/omega/ --select=F821
```
**Why it fails**: Hides both false positives AND real bugs.

### Anti-Pattern 2: Regex/Sed Import Injection (Opus)
```bash
# ❌ WRONG: sed -i '1i import anyio' src/omega/library/rate_limiter.py
```
**Why it fails**: Ignores docstrings, `__future__`, PEP 8 ordering, variable import block positions.

### Anti-Pattern 3: Top-Level Import for Conditional Code (Opus)
```python
# ❌ WRONG: from omega.workers.model_updater import ModelUpdaterWorker  # top of file
# ✅ RIGHT: inline import inside the conditional branch
```
**Why it fails**: Loads heavy transitive deps on every module import.

### Anti-Pattern 4: Breaking A Lazy Import Wrapper (Opus)
```python
# ❌ WRONG: from omega.observability import get_engine  # CIRCULAR IMPORT at module load
# ✅ RIGHT: obs = _get_obs_engine()  # deferred import, no cycle
```
**Why it fails**: Creates `ImportError: cannot import name` at module load.

### Anti-Pattern 5: Dummy Pre-Initialization (Opus)
```python
# ❌ WRONG: tier_start = 0  # meaningless default → elapsed = ~1.7 billion seconds
# ✅ RIGHT: tier_start = time.perf_counter()  # real start time
```
**Why it fails**: `0` as perf_counter baseline gives time-since-boot — garbage.

### Anti-Pattern 6: Duplicate Import Lines (Opus)
```python
# ❌ WRONG: from datetime import datetime / from datetime import timezone  # F811
# ✅ RIGHT: from datetime import datetime, timezone
```
**Why it fails**: F811 redefinition; signals ad-hoc imports.

### Anti-Pattern 7: Multi-Document Execution Merge (NEW — DeepSeek synthesis)
```
# ❌ WRONG: "I will implement according to both the Sonnet 4.6 and Opus 4.6 guides"
# ✅ RIGHT: "I will implement according to AGENT_EXECUTION_PLAN.md — the only document I read"
```
**Why it fails**: Execution models cannot resolve supersession. Merging conflicting
plans produces hallucinated hybrids that satisfy neither. Context curation is the
orchestrator's job, not the executor's.

---

## 7. Bug-to-Feature Alchemy — What The F821 Bug Class Became

> **Teaching note**: Adversarial Alchemy (M19) — a systemic weakness mined for
> strategic advantage. The F821 accumulation is now SIX distinct features:

| # | Feature | Where | Status |
|---|---|---|---|
| 1 | **Prevention Gate** — F821 hard gate in pre-commit +| # | Feature | Where | Status |
|---|---|---|---|
| 1 | **Prevention Gate** — F821 hard gate in pre-commit + CI + Makefile | `.pre-commit-config.yaml`, `ci.yml`, `Makefile` | ✅ DONE (Roc, commit `3f4d3c82`) |
| 2 | **DPO Training Data** — 5 frontier teaching patterns extracted | `data/training/dpo_dataset.jsonl` | ✅ DONE (5 pairs) |
| 3 | **Socratic Commit Contract** — forensic commit-message gate | `.git/hooks/commit-msg` + `scripts/socratic_commit_check.py` | ✅ DONE |
| 4 | **Crucible Protocol Template** — the F821 run is the reference case for all future escalations | `docs/strategy/COGNITIVE_SOVEREIGNTY_EVOLUTION.md` | ✅ DONE |
| 5 | **Shadow Mode Benchmark** — the F821 scenario is a scored test for local models | (planned — `data/benchmarks/`) | 🔜 NEXT |
| 6 | **Frontier Artifact Library** — structured manifest of every frontier document for systematic mining | (planned — `data/frontier_artifacts/`) | 🔜 NEXT |

---

## 8. Codebase Health Snapshot (Updated With Actual Execution Results)

Baseline from Opus §7, updated with Roc's verified execution (2026-08-16):

| Metric | Before | Target | **Actual (Roc)** |
|---|---|---|---|
| F821 violations | 27 | 0 | **0** ✅ |
| F811 violations | 80 | ≤68 | **68** ✅ (12 eliminated by extractors dedup) |
| F401 violations | 928 | Out of scope | 928 (unchanged) |
| `# type: ignore` suppressions | 7 | 6 | **6** ✅ (ics.py removed) |
| Makefile `--ignore` flags | 2 | 0 | **0** ✅ |
| Pre-commit lint hooks (F821) | 0 | 1 | **1** ✅ |
| Files with duplicate content | 1 | 0 | **0** ✅ |
| Contract tests | — | — | **77/77** ✅ |
| Flake8 violations | — | — | **0** ✅ |

**Post-execution verification**: Roc's summary confirms all 4 phases executed, all 3
gates passed, hardening complete, handoff `ho_4e14cee4057a` completed. The execution
was faithful to the unified plan with one deviation: **one atomic commit** instead of
the two specified (fix + hardening merged). Acceptable — the Socratic markers were
not yet enforced at that time; future runs must split.

---

## 9. Decision Record (D-F821-001..010)

| ID | Decision | Rationale |
|---|---|---|
| D-F821-001 | Fix all 27 violations (not just the 10 "real" ones) | TYPE_CHECKING fixes prevent future confusion about which F821s are "acceptable" |
| D-F821-002 | Remove `--ignore=F821` from Makefile | The root cause of accumulation |
| D-F821-003 | Add pre-commit hook (not just CI gate) | Catches violations at commit time |
| D-F821-004 | Delete extractors.py duplication during R-2 | Carmack leverage — 12 F811s eliminated |
| D-F821-005 | Preserve inline import for ModelUpdaterWorker | Performance-aware: defer heavy module load |
| D-F821-006 | Rename call site in regression_watcher (not add import) | Preserve circular-import prevention |
| D-F821-007 | Write Opus guide as separate doc (not overwrite Sonnet plan) | Sonnet has per-file tactical data; Opus adds strategic layer |
| D-F821-008 | Include teaching patterns for local model fine-tuning | Opus token cost justified by lasting knowledge transfer |
| **D-F821-009** | **Synthesis layer (L2.5): a cheaper frontier model unifies planner outputs into ONE executable plan** | Saves Opus token budget; resolves conflicts deterministically; prevents execution-model merge failures |
| **D-F821-010** | **Dual-Artifact Rule: execution agents read ONLY Artifact B** | Execution models cannot resolve document hierarchy or strip pedagogical markers — context curation is the orchestrator's job |

---

## 10. Verification Checklist (For The Executing Agent)

The executing agent verifies ALL of these — using ONLY `AGENT_EXECUTION_PLAN.md`:

```
Phase 2-4 (Fixes):
[ ] flake8 src/omega/ --select=F821 → 0 violations
[ ] flake8 src/omega/ingestion/extractors.py --select=F811 → 0 from extractors
[ ] python -c "import omega.ics; ..." → all 16 modules clean
[ ] make test → no new failures

Phase 6 (Hardening):
[ ] grep "ignore=F821" Makefile → 0 matches
[ ] grep "omega-check-f821" .pre-commit-config.yaml → 1 match
[ ] grep "F82" .github/workflows/ci.yml → still present, no --ignore
[ ] pre-commit run omega-check-f821-undefined-names → passes

Process (NEW):
[ ] Read ONLY AGENT_EXECUTION_PLAN.md — no other sprint documents
[ ] No instructional comments copied into code (grep -r "# <--" src/omega/ → 0)
[ ] Commit messages carry Root Cause: + Prevention Gate: markers
```

---

## 11. Commit Strategy (With Socratic Markers)

**Commit 1** — The fixes (Phases 2-4):
```
fix: resolve 27 F821 undefined-name violations across 13 files

- 10 real missing imports (anyio, re, yaml, Path, timezone, ValidationError)
- 1 scope bug (tier_start pre-initialization in scorecard.py)
- 5 TYPE_CHECKING structural fixes (OracleResponse, AsyncCircuitBreaker,
  MetricsDB, SpeculativeDecodeConfig, ResearchProposal)
- Bonus: delete extractors.py file duplication (12 F811s eliminated)
- Bonus: deduplicate OmegaError import in discovery.py

Root Cause: Makefile --ignore=F821 blanket suppression hid real NameError
bugs; CI lint was non-blocking; no pre-commit hook existed.
Prevention Gate: F821 pre-commit hook + Makefile hard gate (Commit 2).

AP: AP-F821-HYBRID-SYNTHESIS-v1.0.0
```

**Commit 2** — The hardening (Phase 6):
```
ci: add F821 prevention gate and remove blanket suppression

- Remove --ignore=F821 from Makefile lint target
- Add omega-check-f821-undefined-names pre-commit hook
- Update FRONTIER_AI_CODING_STANDARDS.md with §8 Prevention Gates
- Update ci.yml lint step comment for traceability

Root Cause: Pipeline divergence — F821 suppressed locally, non-blocking in CI,
absent from pre-commit.
Prevention Gate: Three-layer enforcement (Makefile + pre-commit + CI comment).

AP: AP-F821-HYBRID-SYNTHESIS-v1.0.0
```

**Why two commits**: If the hardening needs reverting, the fixes remain. If the
fixes need adjustment, the gate catches it. Separation of concerns at commit level.

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ AP-F821-HYBRID-SYNTHESIS-v1.0.0*
