# Human-Guided Learning Capture — First-Principles De-Escalation
**Doc ID**: `GNOSIS-LEARN-001` | **Date**: 2026-09-17
**Reporter**: build agent (big-pickle), Node 1
**Origin**: session `session-2026-09-16T22-34-18Z` — compaction prep, `leash_status` watchdog conflict
**Well records**: `013c6037` (correction), `a254a505` (insight) — now persisted in `gnosis/well/well.jsonl`

---

## 1. Scenario Summary

During "prepare for compaction," two tests in `tests/test_leash_status.py` failed:

1. `test_watchdog_flags_last_compaction_without_narrative` — watchdog returned exit 1 when the test expected healthy.
2. `test_last_session_id_appears_in_both_systems` — asserted `ready_for_compaction: true` on the current session manifest, which by design is `false` mid-pipeline.

The agent entered a ~30,000-token investigation loop: re-reading the same scripts
(`leash_status.py`, `pre_compaction_ritual.sh`, `test_leash_status.py`), re-running
the same tools (`make test`, `leash_status.py`, timeline dumps), and repeatedly
re-interpreting the same three facts:

- Ritual stamps manifests `ready_for_compaction: false` (line 450).
- Watchdog treats "leash taut" as `problems` → exit 1.
- Test expects `ready_for_compaction: true` on the current mid-pipeline session.

No new information was obtained across those turns. The agent was **over-observing
instead of concluding**: the loop was sustained by "let me verify what the code
actually does" — when the behavior itself was the bug and reading it more carefully
could not reveal the fix.

---

## 2. The Human Intervention (verbatim guidance)

> "Go from first principles... who cares what the leash.py is **currently** doing,
> what **should** it be doing? Do we need to completely refactor that system?"

Earlier instruction that did *not* break the loop:

> "add tracing, error handling, etc. to see what is going on"

That instruction was valid for a system where behavior was unknown-but-healthy. It
was wrong for a system where behavior was already known-and-broken. The second
instruction changed the **frame**, not the **data**.

---

## 3. Anatomy of the Breakthrough — Four Moves That Worked

| # | Move | Mechanism | Generalizable rule |
|---|------|-----------|--------------------|
| 1 | **"Who cares what it's currently doing"** | Denied the agent's grounding move ("go verify"). The loop had been justified by exactly that move every turn. | *When stuck, forbid re-verifying current behavior. If behavior were the answer you would have found it.* |
| 2 | **"What *should* it be doing?"** (normative question) | Switched mode from discovery (`is`) to design (`ought`). Produced immediately: three clean conditions (in-flight / failure / abandoned-pipeline). | *Ask the normative question first: derive the contract from purpose, then compare.* |
| 3 | **First principles** | Reframed the failing entity. The bug was not in the watched system — it was in the **watcher's exit semantics** and the **test's invariant**. | *Start from the system's reason for existing; the mismatch surfaces on its own.* |
| 4 | **"Do we need a complete refactor?"** (scope check) | Forced a judgment call before acting. Answer: *no — 36 lines in 2 files.* Prevents over-engineering while escaping the small-patch loop. | *Always ask the scope question; most fixes are smaller than the investigation was.* |

The code's own comment already stated the answer: *"A taut leash is NOT a failure
by itself (capture→reflect is the normal flow)."* The agent had read this comment
on the first pass and continued investigating anyway — treating the **runtime** as
the spec when the **intent comment** was the spec.

---

## 4. Root-Cause Fixes Applied (what "should" became)

### `scripts/compaction/leash_status.py` — exit semantics corrected
- Fresh taut leash (`captured`, **≤24h**): loud `⏳ TAUT (in-flight)` **note**, exit 0.
  *It is the human's turn to reflect — a normal, expected pipeline state.*
- Stale taut leash (`captured`, **>24h**): `❌ TAUT-STALE`, exit 1. *Reflection was
  skipped; pipeline abandoned — a true degradation.*
- Narrative-missing / dead-plugin / stale-timeline checks: **unchanged** (already correct).

### `tests/test_leash_status.py` — invariant corrected
- `ready_for_compaction` is now a **consistency** invariant:
  - `reflection_status == "reflected"` ⇒ must have `ready_for_compaction: true` AND `reflected_at`.
  - `reflection_status == "captured"` ⇒ must **not** claim readiness.
- Previously asserted absolute readiness on the current session — which by design
  fails on every compaction prep.

**Outcome**: 48/48 tests green, lint clean, watchdog healthy on in-flight capture,
and a simulated 30h-stale pack still correctly degrades (exit 1).

---

## 5. Codified Lessons for the Omega Engine

Two Well records were added (and confirmed the engine already carried near-identical
ancestor lessons from prior sessions — proving the auto-injection loop works):

### Well `013c6037` — correction
> When an agent is stuck and re-reading the same files/tool outputs without new
> information, the problem is the interpretation frame, not the data. Exit by
> reframing: ask what the system SHOULD do (first-principles normative question),
> treat the code's own stated intent/comments as the contract (not the runtime,
> not the tests), then compare behavior against intent and derive the minimal fix.

### Well `a254a505` — insight
> Tests validate invariants, not transient mid-pipeline states; and a watchdog
> that contradicts its own stated intent (comment) is the bug, not the behavior
> it reports. Assert readiness consistency (reflected ⇒ ready + reflected_at;
> captured ⇒ not-yet), never absolute readiness on the current in-flight session.

---

## 6. Recommended Codification Points (for engine/runtime)

1. **Loop-detector heuristic** (agent side): if the tool calls for a debugging task
   repeat the same file-reads / tool-runs for ≥3 turns *without* a new fact being
   established, inject a self-check: *"Am I over-observing? State the intended
   contract, then compare."*
2. **Normative-before-investigative** (scaffold rule): for any failing check, the
   first step is "what should this do?" — derive contract from purpose comments
   before reading the implementation.
3. **Watchdog hygiene** (harness rule): distinguish *normal in-flight states* from
   *failures*. A red exit must mean continuity was or will be broken — not "a human
   has a pending step."
4. **Consistency invariants over absolute invariants** (test-writing rule):
   assertions on lifecycle fields should validate internal consistency (reflected
   ⇒ ready+timestamp), never a hard value that is legitimately different at
   different pipeline stages.
5. **Scope-check before remediating** (ponytail alignment): ask "do we need to
   refactor?" as a mandatory step; the answer is usually no — the smallest root-cause
   delta wins.

---

*⬡ OMEGA ⬡ GNOSIS-LEARN-001 ⬡ CAPTURED ⬡*