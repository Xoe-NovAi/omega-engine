# Researcher Session Gnosis — 2026-08-24 (W1-4 Provenance Resolver)

## L1 — Narrative
Executed sprint task W1-4 (WAVE-1-DOCTRINE-WIRING): enhanced the deployed, timer-active
provenance worker `scripts/correct_ics_provenance.py` to close two verified gaps.
GAP-2 root cause found: the old `audit()` renamed a per-call tmp file OVER the ledger,
so 1,440 sequential annotations left exactly 1 surviving line (rename-clobber).
GAP-1 refined: the db query worked; the real defect was anchor recall (HEADER_ZONE=20
missed session refs deeper in files). Implemented: single ro-mode connection with
SQL-side json_extract modelID projection over the covering index, ANCHOR_ZONE=80,
O_APPEND+fsync ledger, update-in-place idempotency preserving original timestamps as
`first_audit:`, and a backfill path so every on-disk annotation is ledger-backed.
Full --apply re-run: 2 annotated / 15 updated / 1,425 backfilled / 1 already-current;
ledger = 1,443 lines. Pre-commit meditation then caught a 1,444th manual annotation
(roc's NEMOTRON_VALUE_ADJUDICATION) invisible to the scanner → closed with a disclosed
backfill-manual entry. Final invariant: 1,444 annotations = 1,444 ledger lines.

## L2 — Insight
1. **Count the disk, not the tool's log**: the worker believed itself complete because it
   only counted its own outputs. An independent census of artifacts found the manual
   annotation it could never see. Reconciliation beats self-reporting (L3-Registry-Gravity recurrence).
2. **Root causes hide in write mechanics**: "ledger incompleteness" looked like an
   early-exit or rotation bug; it was actually last-writer-wins via rename-over-target.
   Trace the exact syscall pattern of append paths before hypothesizing about code paths.
3. **ro-mode must be proven, not promised**: SQLite's `mode=ro` rejects writes at the
   engine level ("attempt to write a readonly database") — codify this as a test, not a comment.

## L3 — Universal Principles (staged for proposed_lessons.yaml)
- **[R-AA] L3-Audit-The-Auditor**: every completeness claim made by a correction pipeline
  must be verified by an independent census of the artifacts themselves; a pipeline that
  only counts its own outputs will forever believe itself complete.
- **[R-WM] L3-Append-Is-A-Contract**: any "append-only" store implemented via
  write-tmp-then-rename is actually replace-semantics; append-only requires O_APPEND (+fsync)
  or single-shot batch rename. Audit the final filesystem operation, not the intent comment.

## Handoff Notes
- Timer (Aug 25 00:03 ADT) runs the new code safely: idempotent, dry-run-equivalent for current corpus.
- Redis publish to maat failed (auth required) — T0 query pattern shared via script docstring + tests + this gnosis instead.
- Residual: 1,432 files UNANCHORED (no session IDs in headers) — inherent limit, honestly labeled.
- Commit pending at report time; paths listed in W4_PROVENANCE_ENHANCEMENT_REPORT_20260824.md.
