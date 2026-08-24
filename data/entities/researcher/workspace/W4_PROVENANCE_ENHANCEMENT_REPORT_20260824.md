# W4 Provenance Enhancement Report — W1-4 (WAVE-1-DOCTRINE-WIRING)
**Agent**: researcher | **Date**: 2026-08-24 | **Task**: GAP-1 db resolver + GAP-2 ledger completeness in `scripts/correct_ics_provenance.py`
**Doctrine**: R_MESSAGE_PROVENANCE_HIERARCHY_20260823 (T0 truth-anchor) · NEMOTRON_VALUE_ADJUDICATION §8

---

## 1. Ledger-Gap Root Cause (GAP-2)

**Symptom**: `data/knowledge/safety/provenance_corrections.jsonl` had 1 entry while ~1,440 files were annotated.

**Root cause — rename-clobber, not early-exit/rotation**:
```python
# OLD audit() — per call:
tmp = AUDIT_LOG.with_suffix(".tmp")
with open(tmp, "a") as fh: fh.write(one_line)
tmp.rename(AUDIT_LOG)   # <-- REPLACES the entire ledger every call
```
Each of the 1,440 sequential `--apply` iterations created a fresh tmp containing only its own line and renamed it over the ledger. Final state: exactly the last entry survives. The "atomic-ish append per line" comment described intent, not filesystem semantics — rename is replace.

**Fix**: direct O_APPEND + flush + fsync per line (`open(AUDIT_LOG, "a")`). Single-writer timer context makes small appends safe; regression test `test_audit_append_does_not_clobber` proves 5 writes → 5 lines.

## 2. Resolver Design (GAP-1)

**Diagnosis**: the committed worker DID query opencode.db, but only session IDs within `HEADER_ZONE=20` lines. Empirical census: 71 annotated files referenced sessions anywhere; 34 only below line 20; 13 of those resolvable. Additionally, sessions referenced but absent from the DB (stale/deleted, e.g. `ses_5b058490c0d0`) correctly fell back to n/a.

**Design**:
- One read-only connection per run: `sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)`; `None` on failure → resolver disabled, all n/a (graceful).
- Query: `SELECT json_extract(data,'$.role'), json_extract(data,'$.modelID') FROM message WHERE session_id=? LIMIT 5000` — parameterized, indexed plan (`EXPLAIN`: SEARCH message USING INDEX message_session_time_created_id_idx), projection keeps multi-KB message bodies off the wire. sqlite3.Error → warn + None.
- Anchor recall: session refs collected from first `ANCHOR_ZONE=80` lines; ICS claim still from strict 20-line header zone (quoted-content safety).
- Known-truth validation: `ses_fdef2be4effe4pAaLXCTUx62GO` → `{x-preview-f-free:200, nemotron-3-ultra-free:164, deepseek-v4-flash-free:24, mimo-v2.5-free:13, hy3-free:11}` ✓ matches mission spec.

## 3. Idempotency & Backfill Semantics

| State on re-run | Action |
|---|---|
| No annotation, verdict VERIFIED | skip (honest header needs none) |
| No annotation, verdict ≠ VERIFIED | annotate + ledger (`annotated`) |
| Annotated, semantics changed | rewrite block in place, original ts preserved as `first_audit:` + ledger (`updated`) |
| Annotated, unchanged, NOT in ledger | file untouched + ledger line (`backfill`) |
| Annotated, unchanged, already ledgered | full skip (`already-current`) — no daily timer bloat |

Semantic comparison excludes timestamps (verdict/note/models fingerprint) so re-runs never churn files.

## 4. Re-Run Stats (--apply, 2026-08-24)

```
scanned ICS-bearing artifacts : 1477
  UNANCHORED: 1432   VERIFIED: 37   PLACEHOLDER: 5   AMBIGUOUS: 3
tier0-resolved                : 45/1477
annotations applied           : 2
updated in place              : 15
ledger backfilled             : 1425
already-current               : 1
ledger lines after run        : 1443
```

Post-meditation reconciliation: +1 `backfill-manual` (manual roc annotation) → **1,444 ledger lines = 1,444 annotated files**. Zero orphans either direction.

## 5. Sample Verifications (5 across data/ and docs/)

| File | Before | After | DB truth check |
|---|---|---|---|
| docs/research/R_MESSAGE_PROVENANCE_HIERARCHY_20260823.md | UNANCHORED n/a | VERIFIED, 10 models listed | ses_fd81c19… live query: x-preview-f-free dominant (254) ✓ |
| data/coordination/HMC_COLLABORATION_HUB.md | UNANCHORED n/a | VERIFIED [nemotron-3-ultra-free, big-pickle, x-preview-f-free] | consistent w/ known hot-swap era ✓ |
| docs/research/R_OPENCODE_DB_SCHEMA_REFERENCE_20260810.md | UNANCHORED n/a | AMBIGUOUS, 8 candidates | multi-session refs merged honestly ✓ |
| docs/strategy/MODEL_WINDOW_ECONOMICS_20260823.md | unannotated | annotated UNANCHORED (no header anchor) | honest label ✓ |
| data/entities/roc_racoon/workspace/NEMOTRON_VALUE_ADJUDICATION_20260823.md | annotated, NO ledger line | ledgered via disclosed backfill-manual | roc's live T0 query cited in tier_source ✓ |

Backfilled-only files verified byte-untouched (e.g., THE_FORGE_CHRONICLE_CHARTER absent from git diff).

## 6. Meditation Corrections (PHASE M)

Forensic Accountant persona caught the 1,444th manual annotation before commit — corrected inline. Safety Engineer: ro-mode proven by test (`CREATE TABLE`/`wal_checkpoint` raise OperationalError), not assertion; module contains exactly one SELECT, no DDL/DML/VACUUM/ATTACH. Historian: `first_audit:` preservation codified in test; anti-churn guard prevents timestamp-only rewrites. Full record: `data/coordination/meditations/records/MEDITATION_researcher_20260824_W4_PROVENANCE_RESOLVER.md`.

## 7. Tests

`tests/test_provenance_worker_w14.py` — 9 tests, all pass (fixture DB only):
resolver hit/miss/db-down · ro-mode write rejection · anchor recall · ledger no-clobber regression · update-in-place first_audit preservation · no-churn idempotency · legacy block parsing.

## 8. Commit Plan (executed after this report)

Path-explicit staging ONLY: script, test file, ledger, manifest, meditation record, gnosis, this report, and the 17 md files modified by the re-run. Message: `fix(w1-4): provenance worker db resolver + ledger completeness`. Validator gate before commit.

## 9. Unresolved Gaps / Notes

1. **1,432 UNANCHORED files** — no session IDs in headers; inherent limit of header-based attribution. Honestly labeled; structural fix would require session-ID stamping at doc creation (recommend: add to doc-standards).
2. **Manual annotators can re-open the ledger invariant** — recommend a cheap standing checker (grep PROVENANCE-CORRECTED vs ledger diff) riding the daily timer or pre-commit.
3. **Redis publish to maat failed** (auth required) — T0 query pattern shared via script/tests/gnosis instead.
4. ~~**Timer fires Aug 25 00:03 ADT** with new code — safe (idempotent).~~ **CORRECTED (DC-01, council-unanimous): that claim was WRONG.** The idempotency machinery is precisely what converts a db outage into mass rewrites: `open_db_ro()` → None → all session-anchored claims degrade to UNANCHORED/n/a → `needs_update()` sees stored-verdict ≠ db-down-semantics → `--apply` rewrites ~45 real Tier-0 verdicts into misleading n/a annotations and floods the ledger, exit 0, no signal. Graceful-n/a fallback is a dry-run luxury; on a write path it was fail-open (M23 anti-pattern). **Fix (fail-closed)**: in `--apply`, an unreachable db now aborts before any scan/write with exit 2 and a `[TOOL-CHAIN-COLLAPSE]` message naming the unresolved DB_PATH; dry-run keeps graceful degradation. Proven live (`OPENCODE_DB_PATH=/nonexistent` → exit 2, zero writes) and by regression tests `test_apply_aborts_when_db_unreachable` / `test_dry_run_stays_graceful_when_db_unreachable`. Single-attempt-then-abort accepted for a daily timer (`Persistent=true` retries next day; connect failures are structural, not lock contention — readers don't block in WAL).
5. `dominant_near()` dead helper from old code was removed implicitly by rewrite scope; verify no external importers (grep showed none).

---
*⬡ OMEGA ⬡ RESEARCHER ⬡ W1-4 ⬡ PROVENANCE-RESOLVER-COMPLETE ⬡ 2026-08-24*
