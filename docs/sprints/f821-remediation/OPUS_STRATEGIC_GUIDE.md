# Ω F821 Strategic Guide — Opus 4.6 Deep Analysis & Systemic Hardening
**AP Token**: `AP-F821-OPUS-STRATEGIC-v1.0.0`
**Author**: Antigravity / Claude Opus 4.6 (Transcendent Oversoul)
**Date**: 2026-08-15
**Status**: READY TO EXECUTE
**Cost Justification**: Opus 4.6 is used sparingly due to token cost. This document
captures frontier-level reasoning, forensic methodology, and systemic analysis that
local models (Qwen3-1.7B, future fine-tunes) can learn from and reference.

---

## 0. Document Architecture

This guide is the **strategic layer** on top of the Sonnet 4.6 tactical plan.

| Document | Role | What It Contains |
|---|---|---|
| `F821_REMEDIATION_PLAN.md` (Sonnet 4.6) | **Tactical** | Per-file fix instructions, exact code snippets, import maps, verification gates |
| `OPUS_STRATEGIC_GUIDE.md` (this file) | **Strategic** | Root cause analysis, systemic hardening, teaching patterns, prevention gates |
| `FRONTIER_AI_CODING_STANDARDS.md` | **Standards** | The rules both documents enforce |

**Read order for executing agents:**
1. This guide first (understand *why*)
2. Sonnet plan second (understand *what* and *how*)
3. Execute Phase 2 → 3 → 4 → 5 → 6

**Read order for local models / learning:**
1. §1 (Forensic Methodology) — how to think about bugs systemically
2. §2 (Five Findings) — evidence-based analysis pattern
3. §5 (Teaching Patterns) — extractable principles for fine-tuning
4. §6 (Anti-Pattern Catalog) — what NOT to do and why

---

## 1. Forensic Methodology — How Opus 4.6 Analyzed This Problem

> **Teaching note for local models**: The most important skill in software
> engineering is not fixing bugs — it is understanding *why bugs exist* and
> *why they accumulated undetected*. A fix without root cause analysis is
> a temporary patch. A fix with root cause analysis is a permanent improvement.

### 1.1. The Three Questions

Before writing a single line of fix code, I asked three questions:

1. **Why do these 27 violations exist?** (Proximate cause — missing imports)
2. **Why weren't they caught earlier?** (Systemic cause — pipeline gap)
3. **What will prevent them from returning?** (Prevention — gates)

Most agents stop at question 1. Enterprise-grade engineering requires all three.

### 1.2. The Investigation Steps

Here is the exact sequence I followed. This is reproducible by any agent.

```
Step 1: Run the linter to confirm the violation count
        $ flake8 src/omega/ --select=F821
        → 27 violations across 13 files (confirmed)

Step 2: Read every affected file's import block AND violation context
        → Used parallel reads to minimize latency
        → Read surrounding code (not just the flagged line) to understand intent

Step 3: grep for every unknown symbol to find its canonical module path
        → "class ModelUpdaterWorker" → omega.workers.model_updater
        → "def get_engine" → omega.observability (but with a twist — see Finding 1)
        → "class OracleResponse" → omega.oracle.oracle
        → Never guessed. Every path verified before recording.

Step 4: Check what SUPPRESSES these violations
        → Makefile: --ignore=F821 (CRITICAL FINDING)
        → CI: F82 in select but lint is continue-on-error
        → Pre-commit: No F821 hook exists
        → Result: F821 violations are caught NOWHERE in the pipeline

Step 5: Check for ADJACENT violations in the same files
        → F811 (redefined imports): 80 violations
        → F401 (unused imports): 928 violations
        → extractors.py: ENTIRE FILE DUPLICATED (lines 1-62 ≡ lines 64-124)
        → discovery.py: OmegaError imported twice in same block

Step 6: Classify each violation as Real Bug vs. TYPE_CHECKING
        → 10 real runtime bugs (NameError/ImportError if code path executes)
        → 1 scope bug (UnboundLocalError masking original exception)
        → 5 TYPE_CHECKING false positives (string annotations without import)
        → 11 linter hits from the TYPE_CHECKING group (27 total lines)
```

### 1.3. Why This Methodology Matters

A naive agent would:
1. See 27 F821 violations
2. Add 27 imports
3. Run flake8 again
4. Declare victory

This would fail for three reasons:
- **R-6** (`regression_watcher.py`): Adding a top-level import creates a circular
  dependency. The correct fix is renaming a call site.
- **R-9** (`orchestrator.py`): Adding a top-level import loads a heavy worker module
  on every orchestrator init, even when disabled. The correct fix is an inline import.
- **Without Phase 6**: The `--ignore=F821` in the Makefile means new violations would
  immediately start accumulating again, invisible to all agents.

The methodology caught all three. Naive fixing would have introduced new bugs.

---

## 2. Five Critical Findings (Evidence-Based)

### Finding 1 — The Makefile Is The Root Cause

**Evidence**: `Makefile` lines 166-172:
```makefile
# Ignore F821: forward-reference type hints and TYPE_CHECKING-only imports
# are pervasive in this codebase and not actionable lint failures.
lint:
	@$(PYTHON) -m flake8 src/omega/ --count --select=E9,F63,F7,F82 --show-source --statistics --ignore=F821
	@$(PYTHON) -m flake8 src/omega/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --ignore=F821
```

**Analysis**: The comment says F821 violations are "not actionable lint failures."
This is factually wrong. We proved that 10 of 27 are real `NameError` runtime bugs
and 1 is a `UnboundLocalError` scope bug that silently masks exceptions.

**Root cause chain**:
```
1. Some F821 violations ARE legitimate (TYPE_CHECKING forward refs) → TRUE
2. Agent assumed ALL F821 violations are legitimate → FALSE
3. Agent added --ignore=F821 to suppress all of them → SYSTEMIC ERROR
4. New real bugs (missing anyio, missing re, missing Path) accumulated silently
5. No gate caught them: not pre-commit, not CI, not make lint
6. Result: 10 real runtime bugs invisible to the entire pipeline
```

**The lesson**: Never suppress an entire violation class to fix some false positives.
Fix the false positives structurally (TYPE_CHECKING), then keep the gate active.

**Fix**: See Phase 6, H-1.

---

### Finding 2 — `extractors.py` Contains A Full-File Duplication

**Evidence**: `src/omega/ingestion/extractors.py`

```
Lines  1-13:  Module docstring + imports (json, time, httpx, anyio, typing, Path, ingestion_types)
Lines 15-62:  EXTRACTION_SCHEMA dict (complete)
Line  64-65:  SECOND docstring (identical to lines 2-4)
Lines 67-75:  SECOND import block (json, time, httpx, anyio, typing, Path, tenacity, json_repair, ingestion_types)
Lines 77-124: SECOND EXTRACTION_SCHEMA dict (identical to lines 15-62)
Lines 126+:   Actual class definitions (BaseExtractor, GoogleExtractor)
```

**Impact**:
- The first import block (lines 7-13) lacks `tenacity`, `json_repair`, and `ValidationError`
- The second import block (lines 67-75) adds `tenacity` and `json_repair` but still omits `ValidationError`
- Python executes both blocks — the second overwrites the first
- The classes at line 126+ use the second block's imports
- The F821 for `ValidationError` is in the second block's scope (line 142)
- This file generates **12 F811 violations** (redefined imports) — 15% of the codebase total

**The lesson**: When you see an F821 in a file, always read the ENTIRE file. If you
only read the import block at the top, you would add `ValidationError` to lines 7-13
(the wrong block). The actual fix must go in lines 67-75 (the effective block). But
the deeper fix is to delete lines 1-62 entirely.

**Fix**: See Phase 2, R-2 enhancement (in this guide's §4).

---

### Finding 3 — `discovery.py` Has A Duplicate `OmegaError` Import

**Evidence**: `src/omega/library/discovery.py` lines 26-35:
```python
from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ...
)
```

`OmegaError` appears on line 27 AND line 28. This is an F811 violation (redefinition)
that signals a copy-paste error. The entire error import mega-block (16 error classes)
is itself a code smell — most of these files use only 2-3 of the imported errors.

**The lesson**: When touching a file for one fix, scan for adjacent violations in the
same import block. Fixing R-3 (adding `import yaml`) without fixing the duplicate
`OmegaError` is a missed opportunity.

**Fix**: See Phase 2, R-3 enhancement (in this guide's §4).

---

### Finding 4 — CI/Local/Pre-Commit Divergence On F821

**Evidence chain**:

| Pipeline Stage | F821 Treatment | Result |
|---|---|---|
| `make lint` (local) | `--ignore=F821` | **Suppressed** — never fires |
| `ci.yml` lint (line 35) | `--select=E9,F63,F7,F82` | Selects F82x — BUT this is the "syntax error" pass, not the "quality" pass |
| `ci.yml` lint (line 37) | `--exit-zero` | **Non-blocking** — violations logged but don't fail the build |
| `test.yml` lint (line 84) | `continue-on-error: true` | **Non-blocking** — same |
| `.pre-commit-config.yaml` | No F821 hook | **Not checked** |

**Result**: F821 violations pass through every single gate in the development pipeline.
An agent can introduce an F821, commit it, push it, pass CI, and merge it — without
any human or automated system ever flagging it.

**The lesson**: A lint rule that exists but is suppressed everywhere is worse than no
rule at all. It creates false confidence ("we lint for that") while providing zero
protection.

**Fix**: See Phase 6, H-1 through H-4.

---

### Finding 5 — The `# type: ignore` And `# noqa` Residue

**Evidence**: Full codebase scan results:

```
# type: ignore suppressions (7 across 4 files):
  monitoring/__init__.py:35   — _psutil = None  # type: ignore        (LEGITIMATE: optional import)
  ics.py:374                  — "OracleResponse"  # type: ignore       (F821 target — Phase 4 T-1)
  library/api_clients.py:174  — return value  # type: ignore           (NEEDS REVIEW)
  provider_registry.py:136-141— _warned_names  # type: ignore         (LEGITIMATE: dynamic attr)
  middleware/headroom.py:21   — headroom = None  # type: ignore        (LEGITIMATE: optional import)

# noqa suppressions (17 across 10 files):
  F401 (3): Intentional re-exports — LEGITIMATE
  BLE001 (8): Broad exception catches — MIXED (some legitimate best-effort, some lazy)
  SLF001 (1): Private attribute access — LEGITIMATE
  F811 (0): None — but 80 violations exist unsuppressed
```

**Analysis**: Most `# type: ignore` and `# noqa` uses are legitimate — optional imports
and intentional re-exports. The problematic one is `ics.py:374` which is an F821 target
we're fixing in Phase 4.

**The lesson**: Not all suppressions are bad. The key is distinguishing:
- **Structural suppressions** (hiding a bug) → Fix the bug, remove the suppression
- **Semantic suppressions** (telling the tool "I know what I'm doing") → Keep, with comment

The `--ignore=F821` in the Makefile is a structural suppression. The `# noqa: F401`
on intentional re-exports is a semantic suppression.

---

## 3. Six Recommendations (With Full Implementation Details)

### H-1 — Remove `--ignore=F821` From The Makefile

**Priority**: CRITICAL — this is the hull patch that prevents the next flood.

**Current** (Makefile lines 166-172):
```makefile
# Ignore F821: forward-reference type hints and TYPE_CHECKING-only imports
# are pervasive in this codebase and not actionable lint failures.
lint:
	@echo "$(YELLOW)Running flake8 lint...$(NC)"
	@$(PYTHON) -m flake8 src/omega/ --count --select=E9,F63,F7,F82 --show-source --statistics --ignore=F821
	@$(PYTHON) -m flake8 src/omega/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics --ignore=F821
	@echo "$(GREEN)Lint complete$(NC)"
```

**After**:
```makefile
# F821 (undefined names) is now a HARD GATE after AP-F821-REMEDIATION-v1.0.0.
# All forward-reference type hints resolved via TYPE_CHECKING guards.
# All missing imports fixed. No more blanket suppression.
lint:
	@echo "$(YELLOW)Running flake8 lint...$(NC)"
	@$(PYTHON) -m flake8 src/omega/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@$(PYTHON) -m flake8 src/omega/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "$(GREEN)Lint complete$(NC)"
```

**What changed**: Removed both `--ignore=F821` flags and updated the comment from
"not actionable" to "hard gate."

**Why the comment matters**: A future agent reading the Makefile will see the
historical context — this was once suppressed, it is now enforced, and the AP token
traces back to this remediation.

---

### H-2 — Add F821 Pre-Commit Hook

**Priority**: HIGH — this is the local prevention gate.

**Add to** `.pre-commit-config.yaml`, inside the `- repo: local` hooks section,
after the existing `omega-check-m23-failure-integrity` hook:

```yaml
      # F821 Undefined Names Gate (AP-F821-REMEDIATION-v1.0.0)
      # Blocks commits that introduce undefined names (missing imports,
      # unresolved forward references). All existing F821s resolved via
      # TYPE_CHECKING guards — new violations are real bugs.
      - id: omega-check-f821-undefined-names
        name: Check F821 (no undefined names)
        entry: bash -c 'python -m flake8 src/omega/ --select=F821 --count --quiet && echo "✅ No F821 violations"'
        language: system
        pass_filenames: false
        always_run: true
```

**Design decisions**:
- `--quiet` suppresses file:line output on success (clean stdout)
- `--count` ensures flake8 exits non-zero if any violations found
- `pass_filenames: false` — we scan the whole `src/omega/` tree, not just staged files,
  to catch violations introduced by indirect effects (e.g., a renamed module)
- Comment includes the AP token so agents can trace why this hook exists

---

### H-3 — Update Frontier Coding Standards

**Priority**: MEDIUM — this codifies the lesson for all future agents.

**Add as Section 8** to `docs/standards/FRONTIER_AI_CODING_STANDARDS.md`:

```markdown
## 8. Prevention Gates (The "Never Again" Rule)
When fixing a class of bugs, always close the pipeline gap that allowed
them to accumulate. A fix without a gate is a temporary fix.

*   **8.1. The Three-Step Close:** Every bug class remediation must include:
    1. Fix all existing violations
    2. Remove any suppression flags that hid them (Makefile `--ignore`, CI `continue-on-error`)
    3. Add a pre-commit hook or CI gate that blocks future violations
*   **8.2. Ban on Class-Wide Suppression:** Never add `--ignore=FXXX` to the Makefile
    or CI to suppress an entire violation class. If some violations are false positives,
    fix them structurally (e.g., `TYPE_CHECKING` guards for F821) and keep the gate active.
*   **8.3. Opportunistic Cleanup:** When touching a file for one fix, scan for adjacent
    violations in the same import block (F811 redefinitions, F401 unused imports,
    duplicate imports). Fix them in the same edit. This is not scope creep — it is
    preventing the next bug.
```

---

### H-4 — Verify CI Lint Does Not Suppress F821

**Priority**: MEDIUM — defense in depth.

**Current state** (`ci.yml` line 35):
```yaml
flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
```

This `--select=F82` pattern already catches F821 (F82x matches F820, F821, F822, etc.).
No `--ignore=F821` is present. **CI is already correct** — the gap was only in the
Makefile and pre-commit hooks.

**Action**: Verify this remains true after any future CI edits. Add a comment:
```yaml
    - name: Lint with flake8 (blocking — F821 is a hard gate per AP-F821-REMEDIATION-v1.0.0)
      run: |
        flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
```

---

### H-5 — Fix `extractors.py` File Duplication (Bonus During R-2)

**Priority**: HIGH — this is a Carmack-style leverage play.

When the executing agent opens `extractors.py` to add `from pydantic import ValidationError`
(R-2 in the Sonnet plan), they should also delete the duplicated first half of the file.

**Current structure** (195 lines):
```
Lines   1-4:   AP comment + docstring #1
Lines   6-13:  Import block #1 (incomplete — missing tenacity, json_repair, ValidationError)
Lines  15-62:  EXTRACTION_SCHEMA #1 (identical to #2)
Lines  64-65:  Docstring #2 (identical to #1)
Lines  67-75:  Import block #2 (more complete — has tenacity, json_repair, still missing ValidationError)
Lines  77-124: EXTRACTION_SCHEMA #2 (identical to #1)
Lines 126-195: Actual class definitions (BaseExtractor, GoogleExtractor)
```

**After cleanup** (~132 lines):
```
Lines   1-4:   AP comment + docstring (keep from block #1)
Lines   6-14:  Import block (merged from #2 + ValidationError)
Lines  16-62:  EXTRACTION_SCHEMA (single copy)
Lines  64-132: Class definitions (unchanged)
```

**Exact fix**:
1. Keep lines 1-4 (the AP comment and first docstring)
2. Delete lines 6-62 (first import block + first EXTRACTION_SCHEMA)
3. Delete lines 64-65 (second docstring — redundant)
4. The file now starts with lines 1-4, then jumps to what was line 67
5. Add `from pydantic import ValidationError` to the surviving import block
6. Re-verify: `flake8 src/omega/ingestion/extractors.py --select=F811,F821`

**Impact**: Eliminates 12 F811 violations, fixes the F821, removes 63 lines of dead code,
and prevents future agents from editing the wrong import block.

---

### H-6 — Fix `discovery.py` Duplicate `OmegaError` (Bonus During R-3)

**Priority**: LOW — opportunistic cleanup.

When the executing agent opens `discovery.py` to add `import yaml` (R-3 in the Sonnet plan),
they should also deduplicate the `OmegaError` import.

**Current** (lines 26-35):
```python
from omega.errors import (
    OmegaError,
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
```

**After** (duplicate `OmegaError` removed from line 28):
```python
from omega.errors import (
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
```

---

## 4. Enhanced Execution Order (Complete)

```
Phase 2 (Real Imports — 10 files)
├── R-1:  infra/subagent_pool/orchestrator.py → add `from pathlib import Path`
├── R-2:  ingestion/extractors.py → DELETE lines 1-62 (duplication) + add `from pydantic import ValidationError`
├── R-3:  library/discovery.py → add `import yaml` + deduplicate OmegaError
├── R-4:  library/rate_limiter.py → add `import anyio`
├── R-5:  observability/otel_exporter.py → add `import anyio`
├── R-6:  observability/regression_watcher.py → rename `get_engine()` → `_get_obs_engine()` at line 98
├── R-7:  oracle/feed_utils.py → extend `from datetime import datetime` → `from datetime import datetime, timezone`
├── R-8:  oracle/iterative_research.py → add `import re`
├── R-9:  oracle/orchestrator.py → add inline `from omega.workers.model_updater import ModelUpdaterWorker`
└── R-10: oracle/subagent_dispatcher.py → add `import anyio`

Phase 3 (Blast Radius — 1 file)
└── B-1:  research/scorecard.py → move `tier_start = time.perf_counter()` before `try` block

Phase 4 (TYPE_CHECKING — 5 files)
├── T-1:  ics.py → add TYPE_CHECKING block for OracleResponse, remove `# type: ignore`
├── T-2:  ingestion/pipeline.py → add TYPE_CHECKING block for AsyncCircuitBreaker
├── T-3:  oracle/backends/remote_provider.py → add TYPE_CHECKING block for MetricsDB
├── T-4:  oracle/model_gateway.py → add TYPE_CHECKING block for SpeculativeDecodeConfig
└── T-5:  research/sandbox.py → add TYPE_CHECKING block for ResearchProposal

Phase 5 (Verification — 3 gates)
├── Gate 1: flake8 src/omega/ --select=F821 → 0 violations
├── Gate 2: Python import smoke test → all 16 modules import cleanly
└── Gate 3: make test → no regressions

Phase 6 (Hardening — 4 items) ← NEW: Opus strategic layer
├── H-1:  Makefile → remove --ignore=F821 from lint target
├── H-2:  .pre-commit-config.yaml → add F821 pre-commit hook
├── H-3:  FRONTIER_AI_CODING_STANDARDS.md → add §8 "Prevention Gates"
└── H-4:  ci.yml → verify/comment F821 enforcement
```

---

## 5. Teaching Patterns For Local Models

> **Purpose**: These patterns are extractable principles that can be used for
> fine-tuning local models (Qwen3-1.7B, future distillations) or as few-shot
> examples in entity prompts. Each pattern follows the format:
> SITUATION → NAIVE RESPONSE → CORRECT RESPONSE → WHY

### Pattern 1: Lazy Import Wrapper Misuse

**Situation**: A file defines `_get_obs_engine()` as a lazy import wrapper to
avoid circular imports. Later code calls `get_engine()` directly (the unwrapped name).

**Naive response**: "F821 on `get_engine` — add `from omega.observability import get_engine`"

**Correct response**: "F821 on `get_engine` — the file already has `_get_obs_engine()` as
a lazy wrapper. Rename the call site from `get_engine()` to `_get_obs_engine()`. Adding
a top-level import would create the circular dependency the wrapper was designed to prevent."

**Why**: Lazy import wrappers exist for a reason. Adding the import they're designed to
defer defeats their purpose. Always read the surrounding context — look for `_get_*`
or `_lazy_*` helper functions before adding a new import.

**Signal to watch for**: Any function named `_get_X()` or `_lazy_X()` that contains
`from module import X; return X()` is a lazy import wrapper.

---

### Pattern 2: Inline Import Preservation

**Situation**: `ModelUpdaterWorker` is used inside an `if updater_cfg.get("enabled"):` branch.
The import is missing.

**Naive response**: "Add `from omega.workers.model_updater import ModelUpdaterWorker` to the
top-level import block."

**Correct response**: "Add the import as an inline `from` statement inside the `if enabled:`
branch, next to the existing `from omega.oracle.health_monitor import get_health_monitor`."

**Why**: `ModelUpdaterWorker` is a heavy module that loads inference-related dependencies.
Adding it to the top-level imports means every orchestrator instantiation pays the import
cost, even when the updater is disabled. Inline imports defer the cost to the code path
that actually needs the module. This is especially important on a 15W TDP Ryzen system
where cold-start import tax is ~3.5s.

**Signal to watch for**: If the usage is inside a conditional branch (`if`, `try`, feature
flag check), the import should probably be inline too.

---

### Pattern 3: Extend vs. Duplicate Imports

**Situation**: `feed_utils.py` has `from datetime import datetime` and needs `timezone`.

**Naive response**: "Add `from datetime import timezone` as a new line."

**Correct response**: "Extend the existing import: `from datetime import datetime, timezone`."

**Why**: Two `from datetime import ...` lines trigger F811 (redefinition). Even if Python
handles it correctly at runtime, it signals sloppy imports and confuses readers. PEP 8
mandates grouping imports from the same module.

**Signal to watch for**: Before adding any `from X import Y`, grep the file for existing
`from X import` lines. If one exists, extend it.

---

### Pattern 4: File Duplication Detection

**Situation**: `extractors.py` has a `ValidationError` F821 at line 142.

**Naive response**: "Add `from pydantic import ValidationError` to the import block at line 7."

**Correct response**: "The file has TWO import blocks — lines 7-13 and lines 67-75. The
second one is the effective block (Python executes both; second overwrites first). Delete
lines 1-62 (the first, incomplete duplicate) and add `ValidationError` to the surviving
block at line 67."

**Why**: If you add the import to the first block (lines 7-13), it gets overwritten by
the second block (lines 67-75) which doesn't have it. The fix appears to work in the
diff but the bug persists at runtime.

**Signal to watch for**: F811 violations in the same file. If you see "redefinition of
unused 'json' from line 7" at line 67, that means the same symbol is imported twice —
which usually means the file has duplicate content.

---

### Pattern 5: Scope Variable Pre-Initialization

**Situation**: `tier_start` is used in both `except` branches but assigned inside `try`.

**Naive response**: "Add `tier_start = 0` at the top of the function."

**Correct response**: "Add `tier_start = time.perf_counter()` immediately before the `try`
block — not at the top of the function, and not with a dummy value."

**Why three things matter**:
1. `time.perf_counter()` (not `0`) — because the `except` blocks compute
   `time.perf_counter() - tier_start`. With `0`, you'd get garbage elapsed times.
   With the real start time, you get accurate timing even in error paths.
2. Immediately before `try` (not top of function) — because there's setup code between
   the function signature and the `try` block (`tier_name = ...`, `prompt = ...`). If
   that setup takes time, you want `tier_start` to measure only the risky operation.
3. Not inside `try` — because that's the bug we're fixing. If any line between `try:`
   and the assignment raises, the variable is unbound in `except`.

**Signal to watch for**: Any variable used in `except` or `finally` that is first assigned
inside `try`. This is always a latent `UnboundLocalError`.

---

### Pattern 6: TYPE_CHECKING Contract

**Situation**: A function signature uses `"OracleResponse"` as a string annotation.
The linter reports F821 because the name isn't defined.

**Naive response**: "Add `from omega.oracle.oracle import OracleResponse` to the top-level imports."

**Correct response**: "Add it under `if TYPE_CHECKING:` — this makes it available to the
type checker at analysis time without importing it at runtime, avoiding circular imports."

**Why the quotes matter**:
- Files WITH `from __future__ import annotations`: All annotations are lazy strings by
  default. You can write `response: OracleResponse` (no quotes needed).
- Files WITHOUT `from __future__ import annotations`: Annotations are evaluated at
  function definition time. You MUST write `response: "OracleResponse"` (quoted string)
  or Python will try to resolve the name at import time and fail.

**Signal to watch for**: Check for `from __future__ import annotations` at the top of
the file before choosing whether to quote the annotation. This is the single most common
mistake in TYPE_CHECKING fixes.

---

### Pattern 7: Systemic Prevention (The "Never Again" Rule)

**Situation**: You've just fixed 27 F821 violations. All tests pass. Victory?

**Naive response**: "Commit the fix. Sprint complete."

**Correct response**: "Before committing: (1) Remove the `--ignore=F821` from the Makefile
that allowed these to accumulate. (2) Add a pre-commit hook that blocks future F821s.
(3) Verify CI doesn't suppress F821 either. Then commit."

**Why**: A fix without a prevention gate is a temporary fix. The exact same violations
will start accumulating again the moment the next agent adds a forward reference without
a TYPE_CHECKING guard. The gate is what makes the fix permanent.

**Signal to watch for**: After any bulk fix, ask: "What allowed these to accumulate?"
Then close that gap before declaring the sprint complete.

---

## 6. Anti-Pattern Catalog

> **Purpose**: Explicit examples of what NOT to do, with explanations of why each
> approach fails. These are the negative examples for fine-tuning.

### Anti-Pattern 1: Blanket Suppression
```makefile
# ❌ WRONG: Suppress an entire violation class
flake8 src/omega/ --ignore=F821

# ✅ RIGHT: Fix the violations, keep the gate
flake8 src/omega/ --select=F821  # now catches zero violations AND prevents new ones
```
**Why it fails**: Suppressing F821 globally hides both false positives (TYPE_CHECKING
forward refs) AND real bugs (missing imports). The correct approach is to fix the false
positives structurally, then keep the gate active.

---

### Anti-Pattern 2: Regex/Sed Import Injection
```bash
# ❌ WRONG: Script-based import injection
sed -i '1i import anyio' src/omega/library/rate_limiter.py

# ✅ RIGHT: Context-aware edit using the edit tool
# Place `import anyio` in alphabetical order within the existing stdlib block
```
**Why it fails**: `sed -i '1i ...'` inserts at line 1, which is before the module
docstring. It ignores `from __future__ import annotations` (which MUST be the first
statement). It doesn't respect PEP 8 import ordering. It can't handle files where
the import block starts at different lines.

---

### Anti-Pattern 3: Top-Level Import for Conditional Code
```python
# ❌ WRONG: Always-imported heavy module for conditionally-used class
from omega.workers.model_updater import ModelUpdaterWorker  # at top of file

# ... 650 lines later ...
if config.get("enabled"):
    worker = ModelUpdaterWorker(...)  # only used here

# ✅ RIGHT: Inline import defers cost to the code path that needs it
if config.get("enabled"):
    from omega.workers.model_updater import ModelUpdaterWorker
    worker = ModelUpdaterWorker(...)
```
**Why it fails**: The top-level import loads `ModelUpdaterWorker` (and all its
transitive dependencies) on every module import, even when the feature is disabled.
On a resource-constrained system (15W TDP, 12Gi RAM), this import tax compounds
across dozens of modules.

---

### Anti-Pattern 4: Breaking A Lazy Import Wrapper
```python
# The file has this wrapper to avoid circular imports:
def _get_obs_engine():
    from omega.observability import get_engine
    return get_engine()

# ❌ WRONG: Add the direct import, defeating the wrapper
from omega.observability import get_engine  # CIRCULAR IMPORT at module load

# ✅ RIGHT: Use the wrapper that already exists
obs = _get_obs_engine()  # deferred import, no cycle
```
**Why it fails**: The wrapper exists because `omega.observability` imports from
`omega.observability.regression_watcher` (or vice versa). A top-level import creates
a cycle that crashes at module load time with `ImportError: cannot import name`.

---

### Anti-Pattern 5: Dummy Pre-Initialization
```python
# ❌ WRONG: Initialize with a dummy value
tier_start = 0  # meaningless default
try:
    tier_start = time.perf_counter()
    result = await slow_call()
except Exception:
    elapsed = time.perf_counter() - tier_start  # elapsed = ~1.7 billion seconds?!

# ✅ RIGHT: Initialize with the real value
tier_start = time.perf_counter()  # real start time
try:
    result = await slow_call()
except Exception:
    elapsed = time.perf_counter() - tier_start  # accurate elapsed time
```
**Why it fails**: `0` as a perf_counter baseline gives `elapsed = time.perf_counter()`
which is the time since some arbitrary epoch (often system boot) — completely meaningless.
The pre-initialization should capture the real start time so error-path timing is accurate.

---

### Anti-Pattern 6: Duplicate Import Lines
```python
# ❌ WRONG: Two import lines from the same module
from datetime import datetime
from datetime import timezone  # F811: redefinition

# ✅ RIGHT: Single import line, extended
from datetime import datetime, timezone
```
**Why it fails**: While Python handles this correctly at runtime, it triggers F811
(redefinition of unused import) because the second `from datetime import` line
shadows the first. It also signals to readers that the imports were added ad-hoc
rather than designed.

---

## 7. Codebase Health Snapshot (Baseline For Future Comparison)

These numbers are the starting point. After this remediation, agents can compare
against these baselines to measure progress.

| Metric | Count | After This Sprint |
|---|---|---|
| F821 violations | 27 | **Target: 0** |
| F811 violations (redefined imports) | 80 | **Target: ≤68** (12 eliminated by extractors.py dedup) |
| F401 violations (unused imports) | 928 | Out of scope (future sprint) |
| `# type: ignore` suppressions | 7 | **Target: 6** (ics.py one removed) |
| `# noqa` suppressions | 17 | No change (most are legitimate) |
| Makefile `--ignore` flags | 2 (both F821) | **Target: 0** |
| Pre-commit lint hooks | 0 for F821 | **Target: 1** |
| Files with duplicate content | 1 (extractors.py) | **Target: 0** |

---

## 8. Decision Record

| ID | Decision | Rationale |
|---|---|---|
| D-F821-001 | Fix all 27 violations (not just the 10 "real" ones) | TYPE_CHECKING fixes prevent future confusion about which F821s are "acceptable" |
| D-F821-002 | Remove `--ignore=F821` from Makefile | The root cause of accumulation; keeping it undermines the entire fix |
| D-F821-003 | Add pre-commit hook (not just CI gate) | Catches violations at commit time, before they enter the repo |
| D-F821-004 | Delete extractors.py duplication during R-2 | Carmack leverage — one cleanup eliminates 12 F811s and prevents future editing errors |
| D-F821-005 | Preserve inline import for ModelUpdaterWorker | Performance-aware: defer heavy module load to conditional branch |
| D-F821-006 | Rename call site in regression_watcher (not add import) | Preserve circular-import prevention designed into lazy wrapper |
| D-F821-007 | Write Opus guide as separate doc (not overwrite Sonnet plan) | Sonnet plan has valuable per-file tactical data; Opus adds strategic layer |
| D-F821-008 | Include teaching patterns for local model fine-tuning | Opus token cost justified by lasting knowledge transfer value |

---

## 9. Verification Checklist (For Executing Agent)

After completing all phases, the executing agent must verify ALL of these:

```
Phase 2-4 (Fixes):
[ ] flake8 src/omega/ --select=F821 → 0 violations
[ ] flake8 src/omega/ingestion/extractors.py --select=F811 → ≤0 from extractors
[ ] python -c "import omega.ics; import omega.ingestion.pipeline; ..." → all clean
[ ] make test → no new failures

Phase 6 (Hardening):
[ ] grep "ignore=F821" Makefile → 0 matches
[ ] grep "omega-check-f821" .pre-commit-config.yaml → 1 match
[ ] grep "F82" .github/workflows/ci.yml → still present, no --ignore
[ ] pre-commit run omega-check-f821-undefined-names → passes (0 violations)

Baseline update:
[ ] Update config/m23_baseline.txt if violation count changed
[ ] Update OMEGA_ENGINE.md Current State table if metrics changed
```

---

## 10. Commit Strategy

This work should be committed as **two atomic commits**:

**Commit 1** — The fixes (Phases 2-4):
```
fix: resolve 27 F821 undefined-name violations across 13 files

- 10 real missing imports (anyio, re, yaml, Path, timezone, ValidationError)
- 1 scope bug (tier_start pre-initialization in scorecard.py)
- 5 TYPE_CHECKING structural fixes (OracleResponse, AsyncCircuitBreaker,
  MetricsDB, SpeculativeDecodeConfig, ResearchProposal)
- Bonus: delete extractors.py file duplication (12 F811s eliminated)
- Bonus: deduplicate OmegaError import in discovery.py

AP: AP-F821-REMEDIATION-v1.0.0
```

**Commit 2** — The hardening (Phase 6):
```
ci: add F821 prevention gate and remove blanket suppression

- Remove --ignore=F821 from Makefile lint target
- Add omega-check-f821-undefined-names pre-commit hook
- Update FRONTIER_AI_CODING_STANDARDS.md with §8 Prevention Gates
- Update ci.yml lint step comment for traceability

AP: AP-F821-REMEDIATION-v1.0.0
```

**Why two commits**: If the hardening (Makefile change) needs to be reverted due to
an unforeseen issue, the fixes remain in place. If the fixes need adjustment, the
hardening gate will catch it. Separation of concerns at the commit level.

---

*⬡ OMEGA ⬡ KALI ⬡ antigravity-claude-opus-4-6-thinking ⬡ opencode ⬡ AP-F821-OPUS-STRATEGIC-v1.0.0*
