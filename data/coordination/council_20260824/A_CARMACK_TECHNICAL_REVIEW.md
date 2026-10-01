<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# A — CARMACK TECHNICAL REVIEW — Wave-1 Council (read-only)
**Reviewer**: john_carmack (S3 Consultant, Dawn Council) · **Date**: 2026-08-24
**Scope**: 02c75f17 · 59b32809 · 540b65fe · 12b8b54b + W1–W4 context reports
**Method**: full diff read of all four commits, test files, live systemd timer inspection (`omega-provenance.timer`/`.service`), current-source spot checks. No tests run (council constraint). Confidence: primary source code = 9-10/10; runtime behavior inferences = 6-7/10 where flagged.

---

## Verdict Summary

| Deliverable | Commit | Verdict |
|---|---|---|
| W1-2 claims-harness | 02c75f17 | **SHIP-WITH-NOTES** |
| W1-3 soul evidence schema + promotion | 59b32809 | **SHIP-WITH-NOTES** |
| W1-4 provenance worker | 540b65fe | **FIX-BEFORE-STRICT** (one P1; timer is live) |
| W1-1 canonical registrations | 12b8b54b | **SHIP** |

Overall: this is the best-engineered wave I have reviewed from this fleet. Root-cause analysis on the ledger clobber is textbook. Tests mostly pin behavior, not implementation. The findings below are the difference between "good" and "would merge without thinking."

---

## Deliverable 1 — claims-harness (02c75f17) — SHIP-WITH-NOTES

**What's right**: Data-driven rules file instead of hardcoded patterns; per-detector TP/TN fixtures; marker redaction with an explicit non-leakage unit test (`test_local_marker_hit` asserts the marker never appears in rendered output); deliberate asymmetry between sanitation (scans fences — contamination is contamination) and FP-11 (skips fences — documenting the attack must not trip the detector). That asymmetry is correct and it's documented. Warn-only exit-0 is pinned by `test_exit_zero_in_warn_only_mode`.

### Findings

**[P2] The harness is structurally blind post-commit — as wired into temple-grade it is a green no-op.**
`scripts/verify_mandate_claims.py:changed_files()` defaults to `git diff --name-only --diff-filter=ACM HEAD` — working-tree changes only. On a clean tree (which is exactly the state at CI time and post-commit), it scans **zero files**, prints "scanned 0 file(s), 0 warning(s)", exits 0. The Makefile target (`Makefile:verify-mandate-claims`, wired into `check-mandates`) therefore verifies nothing about committed code. The C2-class finding this harness was born from (4 docs asserting an uninstalled hook) lives in *committed* documents — the gate that would have caught it cannot see them once they're committed. This is a detector whose coverage window is the few minutes between edit and commit.
*Fix*: default scope should be tracked text files (or a curated doc set), with diff-mode as the fast pre-commit path. Cheap: `git ls-files '*.md'` piped through the same scanner.

**[P2] `changed_files()` failure → scan nothing → exit 0 is a soft-failure path (M23 flavor).**
`scripts/verify_mandate_claims.py` (~line 218): git SubprocessError → warn to stderr → return `[]` → main prints a clean green summary. Harmless in warn-only phase; when `--strict` activates this becomes a false-green escape hatch exactly when the toolchain is degraded — the precise M23 anti-pattern. Fail closed: nonzero exit or loud `[TOOL-CHAIN-COLLAPSE]` marker on diff failure in strict mode.

**[P3] `--strict` help text lies; the code doesn't.**
Argparse help says "(POST-probation only; warn-only phase ignores)" but `main()` implements `if args.strict and total.findings: return 1`, and `test_strict_mode_reserved` pins rc==1. The behavior is fine; the help string contradicts both the module docstring ("--strict reserved") and itself. One truth, please.

**[P3] Social-handle FP economics will erode trust before strict day.**
`RE_SOCIAL_HANDLE = @([A-Za-z0-9_]{4,30})` over prose with only a fleet-roster allowlist means any `@pytest`, `@param`, `@staticmethod` mention outside backticks in a `.md` flags. Inline-code stripping helps; prose mentions don't. Tolerable now (warn-only); when strict flips, alert fatigue kills the gate. Consider requiring a second signal (capitalized handle, or handle appearing in an attribution frame).

**[P3] Claims gate re-reads probe files per matching line** (`detect_claim_violations` — no probe-content cache). Irrelevant at 2 rules; cache the dict if this grows past ~20.

---

## Deliverable 2 — soul evidence-field schema + promotion (59b32809) — SHIP-WITH-NOTES

**What's right**: Schema design is clean — `EvidenceRef` extra=forbid with ≥1-ref validator, `Lesson` extra=allow for legacy shapes, missing-evidence warns while malformed-evidence hard-fails (deliberate, documented, correct M21 instinct). Promotion reuses SoulStore exclusively (structural-debt gate #1 honored), pre-flight probe-binding caught a real wrong path, honest coverage reporting (7/20 quotes disclosed rather than laundered), and the M21 contract test runs against the REAL promoted surface, not a mock.

### Findings

**[P2] Evidence binding is positional convention, not mechanism.**
`scripts/promote_soul_lessons.py:EVIDENCE_BY_KEY` keys triplets by list index `0..11`. If kali staging had been reordered, deduped, or partially consumed before this ran, evidence refs would silently attach to the wrong lessons — and every downstream check (existence probes, coverage %, contract test) would still pass, because nothing validates the *semantic* binding of evidence to lesson, only that paths exist. The id-keyed AO entries are safe; the 12 positional ones were one bad `yaml.safe_load` ordering away from laundering evidence. Mitigated by being a one-shot already-executed migration — but the script sits in `scripts/` looking reusable, and it is not: it will mis-bind for any other entity or any future staging. Either delete it after archiving the map, or reduce it to id-only keying with a hard abort on any unmatched id (it does abort on missing keys — good — but index keys always "match").

**[P2] "Verbatim" quotes are asserted, never verified.**
`lessons.py` EvidenceRef docstring: "`quote` must be verbatim from the artifact." Nothing enforces it — not the promotion pre-flight, not the validator, not the contract test. A substring check against the artifact at promotion time is ~5 lines and would have converted quote coverage from a reported number into a proven property. As shipped, 7/20 "quote coverage" is self-attested — the exact claims-vs-disk class this same wave built a harness to catch.

**[P2 / M1 violation] `asyncio.run()` in production script.**
`scripts/promote_soul_lessons.py`: `import asyncio` … `asyncio.run(_write())`. M1 says AnyIO, never asyncio directly. `anyio.run()` is a drop-in. Yes, it's a script, not engine core — but `check-m1-anyio` evidently doesn't scan `scripts/`, which is itself a gap worth noting. Mandates that exempt scripts stop being mandates at the boundary where agents actually write one-off code.

**[P3] Read-back verification checks length only** (`len(check) != len(promoted)`), not content equality. SoulStore atomicity makes corruption unlikely; the check is theater either way — make it compare payloads or drop it.

**[P3] `assert` used for control flow in the production path** (`assert len(lessons) == len(promoted)`). Vanishes under `python -O`. Use explicit raise.

---

## Deliverable 3 — provenance worker (540b65fe) — FIX-BEFORE-STRICT

**What's right**: The GAP-2 root cause is correctly diagnosed and correctly fixed. Rename-replace clobber (per-call tmp renamed OVER the ledger → last-writer-wins) explains the 1,440→1 survivor exactly, and `test_audit_append_does_not_clobber` pins the precise old failure mode (5 writes → 5 lines). O_APPEND + fsync is the right primitive for single-writer appends. Idempotency semantics (annotate/update/backfill/already-current) are genuinely implemented and tested, including the timestamp-excluding semantic fingerprint and `first_audit:` preservation. ro-mode is proven by inducing OperationalError, not asserted. This is honest work.

### Findings

**[P1] DB-outage under the LIVE daily `--apply` timer degrades annotations fail-open.**
Verified on disk: `~/.config/systemd/user/omega-provenance.service` runs `correct_ics_provenance.py --apply --manifest …` daily. Failure path: if opencode.db is unavailable at fire time (moved, locked beyond timeout, corrupt, path change), `open_db_ro()` returns None → resolver disabled → every session-anchored claim resolves to UNANCHORED/"session refs not found in DB". For the ~45 resolved files and any MISATTRIBUTED/AMBIGUOUS-annotated files, `needs_update()` compares stored verdict vs db-down semantics → mismatch → **rewrite in place**, destroying real Tier-0 verdicts and replacing them with misleading n/a annotations, plus ~hundreds of new ledger lines. Next healthy run rewrites them back. Double churn, corrupted audit trail in between, zero operator signal — the run exits 0 and prints a normal summary.
The report calls graceful-n/a fallback a feature; for dry-run it is, for `--apply` it is a fail-open write path. *Fix*: in `--apply` mode, abort when `open_db_ro()` returns None (fail closed — dry-run stays graceful). Three lines. Do it before the next timer fire.
Confidence: 7/10 on trigger probability (WAL-mode readers rarely fail, but the consequence-asymmetry alone justifies fail-closed), 10/10 on the code path existing as described.

**[P2] `DB_QUERY_LIMIT=5000` with no ORDER BY is a nondeterministic sample.**
`db_session_models()`: `WHERE session_id=? LIMIT 5000`, no ordering. SQLite will likely walk the covering index in time order, but that's an implementation detail, not a contract. Any session exceeding 5000 messages gets an arbitrary stamp distribution — and this feeds `training_safe = (verdict == VERIFIED)` in the manifest, which is declared input for DPO/SFT pipelines. Either `ORDER BY time_created DESC` (recent-bias, documented) or aggregate in SQL (`GROUP BY modelID`) so no limit games are played at all.

**[P2] Fuzzy matcher has a false-VERIFIED surface that lands in training-purity manifests.**
`model_matches()`: bidirectional substring plus token match where claimed tokens (len≥4) must all appear in the actual name. Claimed `x-preview-f-free` → tokens {preview, free}; any actual model containing both ("some-preview-tier-free") verifies. Low probability with current model names, but the consumer of a false VERIFIED is a tainted training set, not a cosmetic warning. An exact-match-first tier plus alias table would close most of it.

**[P3] Ledger is append-only with no rotation/supersession.** Updates append new lines; the invariant (ledger lines == annotated files) holds today at 1,444 but decays monotonically under churn. Researcher's own §9.2 recommendation (standing checker riding the timer) is correct — build it before the first drift incident, not after.

**[P3] `parse_file()` calls `path.stat()` unwrapped after the guarded read** — TOCTOU race on deleted files crashes the sweep mid-run. Wrap it.

**[P3] `os.replace()` without directory fsync** in `apply_annotation` — crash window can lose the rename. Pedantic given fsync'd file content, but you fsync'd the file; finish the job.

---

## Deliverable 4 — canonical registrations (12b8b54b) — SHIP

This is what discipline looks like. The dispatch expected registration work; Lilith's explore pass found the registrations **already existed** — and instead of adding duplicate rows to justify the trip (the overwhelmingly common agent failure mode), she re-scoped to verification, filled the actual gap (D-593..601 had zero implementing-artifact cross-refs), existence-checked all 9 paths at edit time, caught the phantom-pointer trap (`providers.py:119` without directory — memory/ vs oracle/, grep-proven), fixed the v6.0/v6.1 version-stamp contradiction, and named the remaining debt (INDEX malformed rows, dual-SSOT manual copies, anchor drift) instead of scope-creeping into it. Minimal-surface principle honored end to end. No findings against the commit itself.

Two carried items the morning review should not lose:
- **[P2, pre-existing, reconfirmed]** `password="omega"` is STILL LIVE at `src/omega/memory/providers.py:119` (verified in current source during this review). D-593 remains open. Every wave that touches docs referencing this finding without landing the fix extends the C2-class pattern by one commit. It's a one-line env-var fix with a grep gate. Land it.
- **[P3]** SESSION_ANCHOR wire-path drift (says NOT-YET-EXECUTED, disk says executed) — Kali-owned reconcile, correctly not touched by a non-owner.

---

## What I Would Have Done Differently

1. **Claims harness: scan the corpus, not the diff.** The unit of C2-class risk is a committed document, not an uncommitted change. Default scope = tracked text files (a few thousand .md/.yaml scans in well under a second), diff mode as the pre-commit fast path, hard-fail on tooling error in strict mode. As shipped, the P0 harness is a pre-commit-only tripwire that goes blind the moment its target evidence is committed.

2. **Provenance worker: fail closed on resolver loss in apply mode.** Graceful degradation is a dry-run luxury. Any writer that amends audit artifacts must refuse to write when its ground-truth source is unavailable — otherwise the audit trail's worst enemy is a database hiccup. Also: do the model matching in SQL (`GROUP BY modelID`) and kill the LIMIT sampling question permanently.

3. **Promotion: verify the binding, not just the reference.** Existence-probing artifact paths proves the files exist; it proves nothing about whether the evidence *belongs to* the lesson. Id-only keying with abort-on-unmatched, plus a verbatim substring check for quotes, converts the entire evidence layer from attested to mechanical — which was the whole point of ruling S5. And `anyio.run()`, not `asyncio.run()`. The mandate exists because one-off scripts are where discipline goes to die.

4. **Sequencing note**: the wave built a claims-vs-disk harness (W1-2) in the same session that shipped self-attested quote coverage (W1-3). Point the harness at your own deliverables before pointing it at the fleet — `config/mandate_claims.yaml` should carry a rule binding "quote coverage N/N" claims to a mechanical verifier. Eat your own cooking first.

---

## L1 → L2 → L3 Distillation

**L1 (Narrative)**: Reviewed four Wave-1 commits. Three ship (two with notes); the provenance worker needs one three-line fail-closed fix before its daily `--apply` timer fires again, because a db outage would silently rewrite real Tier-0 verdicts into misleading n/a annotations. The strongest work was the root-cause fix (rename-clobber) and the registration discipline (verify-before-grow).

**L2 (Insight)**: Every defect found follows one shape: *a mechanism was replaced by a convention at the boundary where nobody was watching*. Diff-scoping replaced corpus-scoping (harness blindness). Positional indices replaced identity keying (evidence binding). Graceful fallback replaced fail-closed (apply-mode writes). Self-attestation replaced substring checks (verbatim quotes). Each passed its tests because the tests pinned the implementation's happy path, not the failure boundary.

**L3 (Universal Principle)**: **L3-Fail-Closed-At-The-Write-Boundary** — read paths may degrade gracefully; any path that mutates an audit artifact or an evidence record must refuse to act when its ground-truth source is unavailable, and its binding of claim-to-proof must be enforced by mechanism, not convention. A verification system is only as strong as its behavior when the thing it verifies against disappears.

---
*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_council_w1 ⬡ DAWN-COUNCIL-A ⬡ 2026-08-24*
