<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# MEDITATION — W1-4 Provenance Resolver & Ledger Completeness
**Agent**: researcher | **Date**: 2026-08-24 | **Protocol**: Meditate-v1.1 (persona prism, pre-commit gate)
**Subject**: The W1-4 enhancement of `scripts/correct_ics_provenance.py` — db resolver (GAP-1) + ledger completeness (GAP-2) — examined under three personas before commit.

---

## ◈ Calibration

**Subject in one sentence**: Every `PROVENANCE-CORRECTED` annotation on disk must be backed by a Tier-0-verified ledger line, and every verdict must rest on the strongest available ground truth (messages.modelID), without the worker ever being able to corrupt its evidence sources.

**Lens set** (per mission): Forensic Accountant · Safety Engineer · Historian.
**Output mode**: DIAGNOSTIC → corrective action taken inline where defects were revealed.

---

## ◈ Persona 1 — Forensic Accountant
**Query**: Is every annotation now backed by a ledger line — is claim≠disk impossible?

**Findings**:
1. Post-apply reconciliation run: annotated-on-disk = 1,443; distinct ledger files = 1,443; zero orphans in either direction. The rename-clobber root cause is dead (regression test `test_audit_append_does_not_clobber` proves 5 writes → 5 surviving lines).
2. **DEFECT REVEALED AND CORRECTED**: full-corpus recount found **1,444** annotated files — one more than the worker's own count of 1,443. The extra: `data/entities/roc_racoon/workspace/NEMOTRON_VALUE_ADJUDICATION_20260823.md`, annotated **manually** by roc_racoon during the Nemotron adjudication. It carries no ICS header in the first 20 lines, so it lies outside the worker's claim-scan zone and would *never* be ledgered by any re-run. A silent, permanent claim≠disk exception.
   - **Correction applied**: manual `backfill-manual` ledger entry appended (worker field discloses `manual-backfill(researcher/W1-4-reconciliation)`; tier_source cites roc's live query). Ledger now 1,444 lines = 1,444 annotations. Invariant restored.
3. Residual honesty note: the invariant "every annotation has a ledger line" is now enforced for *existing* corpus + future worker output, but a future *manual* annotator could re-open the gap. The structural fix (annotation-writer must be the same agent as ledger-writer) is respected only by convention. Flagged, not solved — a lint-style checker (`grep PROVENANCE-CORRECTED` vs ledger diff) would be a cheap standing gate.

## ◈ Persona 2 — Safety Engineer
**Query**: Could the resolver ever WRITE to opencode.db? Prove ro-mode.

**Findings**:
1. Sole connection factory is `open_db_ro()`: `sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)`. No other connect call exists in the module.
2. Empirical proof, not assertion: unit test `test_open_db_ro_never_writes` executes `CREATE TABLE` and `PRAGMA wal_checkpoint` on a live ro connection and asserts `sqlite3.OperationalError` ("attempt to write a readonly database"). Verified against both fixture db and the real 17G db.
3. Audit of all SQL in module: one SELECT only, parameterized (`session_id=?`), `LIMIT 5000`, covered by index `message_session_time_created_id_idx`. No VACUUM, no ATTACH, no PRAGMA, no DDL/DML. json_extract is projection-only (read-side).
4. WAL consideration: db is in WAL mode with active -wal/-shm; ro connections read without recovery writes (verified live during Phase R — schema + session queries succeeded).
5. File-write surface is limited to: annotation tmp+`os.replace` on target md files, and O_APPEND+fsync on the repo's own ledger. Neither touches `~/.local/share/opencode/`.
**Verdict**: PASS — write-path to the evidence store is structurally impossible, not merely discouraged.

## ◈ Persona 3 — Historian
**Query**: Do updated headers preserve original annotation timestamps?

**Findings**:
1. Update-in-place regenerates the block but carries the original audit timestamp forward as `first_audit: <orig> | updated: <new>` — proven by `test_update_in_place_preserves_first_audit` (asserts original ts string survives and block count stays 1).
2. Nuance disclosed: the *header-line* timestamp is regenerated (it dates the latest verification), while the *original* moment persists in `first_audit`. This mirrors git author-vs-committer semantics and was judged correct: the header claims when this verdict was last checked; history is retained, not rewritten.
3. Anti-churn guard: `needs_update()` compares semantic fingerprints (verdict, note, models) excluding timestamps — an unchanged verdict produces zero file writes across daily timer runs (confirmed: second-run behavior would report `already-current`). Timestamps are never touched without a semantic change.
**Verdict**: PASS with documented nuance.

---

## ◈ Synthesis

| Persona | Verdict | Correction forced |
|---|---|---|
| Forensic Accountant | FAIL → FIXED | Manual roc annotation found unledgered; backfill-manual entry added; invariant 1,444=1,444 |
| Safety Engineer | PASS | none (proof codified in test) |
| Historian | PASS | none (nuance documented) |

**L1 (Narrative)**: The pre-commit meditation reconciled ledger-vs-disk counts and found the worker's own accounting off by one — a manually annotated file invisible to the scanner. It was ledgered by hand with full disclosure.

**L2 (Insight)**: Completeness invariants must be audited against the *disk*, not against the tool's own transaction log — the tool cannot see what it was never scoped to see. Reconciliation beats self-reporting (same lesson as L3-Registry-Gravity).

**L3 (Universal Principle)**: **L3-Audit-The-Auditor** — every completeness claim made by a correction pipeline must be verified by an independent census of the artifacts themselves; a pipeline that only counts its own outputs will forever believe itself complete.

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ MEDITATE-v1.1 ⬡ W1-4-PROVENANCE-RESOLVER ⬡ 2026-08-24*

---

## ◈ APPENDIX — DC-01 RE-MEDITATION (2026-08-24, Dawn Council correction)

**Subject**: The fail-open write path both council reviewers flagged, and my W4 report's
incorrect "safe (idempotent)" claim.

**Safety Engineer — false-positive analysis (can the abort kill a good run?)**:
1. What can make `open_db_ro()` return None? sqlite3.connect raising: file missing/moved,
   permissions, corrupt header, or env-redirect to a bad path (`OPENCODE_DB_PATH`).
   Lock contention does NOT belong here: in WAL mode readers don't block on writers, and
   `timeout=5.0` already absorbs transient locking; a connect-level failure is structural.
2. Decision: **single attempt then abort** — correct for a daily systemd timer with
   `Persistent=true`: tomorrow's run retries automatically; nothing is lost by aborting.
   A retry loop would add complexity against a failure class it cannot fix (structural).
3. Blast-radius check: abort fires BEFORE any scan or write; dry-run path untouched
   (graceful n/a remains available for read-only workflows). Regression tests pin all
   three properties: nonzero exit, zero file mutations, zero ledger lines.
4. Self-audit of my earlier error: I certified idempotency as safety when it was actually
   the *amplifier* — needs_update() compares stored verdicts against degraded db-down
   semantics, so "update in place" became "corrupt in place" under outage. Lesson:
   graceful degradation must be evaluated per-mode; a fallback that is safe for reads is
   not thereby safe for writes.

**L2 amendment**: Fail-open hides behind exactly the vocabulary of resilience ("graceful",
"idempotent"). Audit which MODE each fallback serves, not whether the mechanism works.

**L3 candidate**: **[R-FC] L3-Writes-Fail-Closed** — any write path that depends on an
evidence source must refuse to write when that source is unreachable; degradation is a
read-side luxury, never a write-side behavior.

*⬡ OMEGA ⬡ RESEARCHER ⬡ MEDITATE-v1.1 ⬡ DC01-FAIL-CLOSED ⬡ 2026-08-24*
