<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# MEDITATION RECORD — maat — 2026-08-24 — D-602 Torch-Free Compliance

**AP Token**: AP-MEDITATION-MAAT-D602-v1.0.0
**Trigger**: PIVOT_LOG D-602 (Architect decree) — torch/transformers/sklearn banned at module level in src/
**Target**: `src/omega_youtube_research/faithfulness.py`
**Protocol**: Meditate-v1.1 (Skeptic → Builder)

---

## Skeptic — "Does lazy-import change NLI behavior when libs ARE present?"

**Verdict: NO behavioral change on the happy path.**

1. **NLIEntailmentScorer**: torch/transformers now imported inside `__init__` instead of at module top.
   Same classes (`AutoTokenizer`, `AutoModelForSequenceClassification`), same model load, same
   `eval()` call. `score_entailment` binds `torch` from `self._torch` — identical tensor ops,
   identical return value. Failure mode unchanged: absent libs → `RuntimeError("transformers not
   installed...")`, now chained `from exc` (strict improvement for traceability, M9).

2. **CalibratedJudge.fit_cv**: sklearn imported inside method; same `IsotonicRegression(out_of_bounds="clip")`
   construction and fit sequence. Absent libs → same RuntimeError message.

3. **predict / predict_oof**: replaced `float(np.clip(x, 0.0, 1.0))` with `_clip01(x)` =
   `max(0.0, min(1.0, float(x)))`. Mathematically identical for scalar floats (np.clip on a scalar
   returns a numpy scalar; original code immediately called float() on it). Zero-dependency hot path.

4. **save() edge case (documented deviation)**: old guard was `if not SKLEARN_AVAILABLE: return`.
   New guard: `if self.global_calibrator is None: return`. Rationale: `fit_cv` raises RuntimeError
   without sklearn, so a judge with a fitted global calibrator NECESSARILY had sklearn importable.
   The only observable difference: an UNFITTED judge WITH sklearn installed previously wrote a JSON
   of default metadata; now it writes nothing. That write was content-free boilerplate (the file
   itself notes IsotonicRegression isn't serializable). Degradation semantics preserved: no crash
   without libs, no partial writes.

5. **verify_provenance**: unchanged. Default `nli_scorer=None` path constructs NLIEntailmentScorer()
   which raises RuntimeError without transformers at RUNTIME — exactly as before.

## Builder — "Is the pattern consistent with how omega handles optional deps elsewhere?"

**Verdict: YES — canonical pattern.**

- `src/omega/oracle/model_gateway.py` uses the identical combo: module-level
  `if TYPE_CHECKING:` block for static annotations + runtime ImportError guards at use sites (line 1512).
- The WAD-isolated `omega_youtube_research` package already used guarded imports in chunker.py /
  cas_archiver.py / transcriber.py — this fix extends the same discipline from "guarded presence"
  to "lazy presence" where the guarded cost (~484MB RSS per xdist worker) was prohibitive.
- `from __future__ import annotations` (already present) stringifies all annotations incl. variable
  annotations, so `Optional[IsotonicRegression]` attribute annotations never evaluate at runtime.
  TYPE_CHECKING import keeps LSP/pyright clean.

## Residual Findings (report-only, per mission scope)

| File | Import | Cost | Risk |
|------|--------|------|------|
| chunker.py:25 | numpy (module-level try/except) | ~35MB | LOW — numpy only |
| cas_archiver.py:35 | numpy + datasketch (module-level) | ~35MB | LOW |

These explain residual collection floor (~93MB vs ~60MB bare). Candidate for follow-up if xdist
worker count grows; NOT part of D-602 scope (torch/transformers/sklearn are the banned set).

## Evidence

- Probe A: `import omega_youtube_research.faithfulness` → torch/sklearn/transformers all False ✓
- Probe D: builtins.__import__ blocked for torch/transformers/sklearn → exit 0 ✓
- Collection RSS: **495,360 KB → 94,900 KB** (−81%, ~484MB → ~93MB)
- Tests: tests/test_youtube_research_v2.py + tests/test_cli_smoke.py = 19 items, 18 ok, 1 skip
  (faster-whisper absent, pre-existing). M21 contract tests green.

## L3 (Universal Principle)

Import cost is paid at import site, not use site — therefore availability guards must live at the
use site too. A try/except at module level converts an optional dependency into a mandatory
collection-time tax for every importer, every worker, every run.
