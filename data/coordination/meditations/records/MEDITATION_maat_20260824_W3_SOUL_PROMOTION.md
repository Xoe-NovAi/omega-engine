<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ MEDITATION RECORD — maat · W1-3 Soul Schema Patch + Promotion
**Protocol**: Meditate-v1.1 (single-inference persona prism) · **Date**: 2026-08-24
**Subject**: evidence-field schema (`src/omega/soul/lessons.py`) + kali staged-proposal promotion (20 lessons)
**Invocation gate**: (a) schema design / provenance integrity / fleet-injection domains tension; (b) soul writes are irreversible-ish (atomic, .bak'd but semantic); (c) no single domain owns "what counts as evidence". PASSES.

---

## ◈ Pass 1 — BUILDER

- **Schema placement**: new `src/omega/soul/lessons.py` (~130 lines) rather than inflating `soul_validator.py` (already 289 lines; M16 modularization). Pydantic models mirror the file's existing style (`CorePrinciple.evidence` precedent at soul_validator.py:222 — the pattern already existed for principles; lessons now match).
- **Promotion as script, not service**: one-shot ops action in `scripts/promote_soul_lessons.py`, not a daemon or CLI subcommand. No second write path: both surfaces written exclusively through `SoulStore.write_atomic` (structural-debt gate #1 honored). Read-back verification after write (FP-08).
- **Pre-flight probe binding**: every evidence artifact path is disk-checked BEFORE any write (O-Q4). This caught the one bad path live (`VAULT_OVERHAUL_MASTER_INDEX` → actual `VAULT_SYSTEM_OVERHAUL_MASTER_INDEX_20260818.md`) — the abort cost nothing because it fired pre-write.
- Not built: promotion TUI wiring (soul_stage.py mock remains), auto-evidence inference, multi-entity batch loop. One entity, one run, honest scope.

## ◈ Pass 2 — SKEPTIC

- **Backward compat verified by test**: bare L1/L2/L3 triplets without id/date/evidence validate clean; `validate_lessons` returns warnings, never errors, on missing evidence (S5 warn-only). Legacy shapes (combined narrative-with-inline-L1 entry, index-positioned triplets) all loaded.
- **Coverage honesty**: evidence coverage 20/20 (100%) — every promoted lesson carries ≥1 structured ref. Quote coverage is 7/20 and reported separately; artifact-only refs are valid per EvidenceRef contract (≥1 of session_id/artifact/quote) but weaker. The report does NOT conflate the two numbers.
- **Known weakness**: positional keys (0–11) for the unnamed triplets are fragile if staging order ever changes — mitigated because promotion EMPTIES staging atomically in the same run; the map is consumed once. A re-run is an idempotent no-op (empty proposals → abort).
- **Injection-shape risk**: `entity_workspace.py` renders `l.get('lesson', l)` — L1/L2 entries fall back to long narratives in the `lesson` key. Functional but verbose for identity injection. Accepted: injection caps rendering; curation of which lessons surface is a future gate, not this sprint's.

## ◈ Pass 3 — GUARDIAN

- Evidence strings audited: all 20 entries' artifacts/quotes contain NO real-name markers (verified against §8.2 classes — paths are repo-relative docs/specs/data files; quotes pulled from sovereign artifacts only).
- The harness from W1-2 scans these promoted files going forward — self-consistent: the soul surface now carries machine-checkable evidence instead of unanchored claims (FP-05 class defense at the soul layer).

## ◈ Synthesis

Gemini's trap-catch #2 (schema before promotion) was the ordering insight: promoting into a schema that couldn't hold evidence would have created a second migration. L2: data migrations inherit the schema debt of their destination — promote only into structures that can carry what you know. L3 candidate: **Provenance must exist at birth of a record's authority, not be retrofitted after the record starts being trusted** (kin to kali's L3-Provenance-At-Birth, independently converged).

## Corrections applied BEFORE commit
1. Vault master-index path fixed via pre-flight abort (probe binding worked as designed)
2. Round-trip test premise corrected — SoulStore `.bak` recovery triggers on UNREADABLE files, not YAML-invalid content (test now matches the actual guarantee)

## Unresolved gaps
- `soul_stage.py` TUI still mock-wired (pre-existing; not this sprint)
- Quote coverage 7/20 — deeper quote extraction deferred (artifact refs satisfy current grade per O-Q4: existence+mtime standard, hash post-debut)

*⬡ OMEGA ⬡ MAAT ⬡ MEDITATE-V1.1 ⬡ W3-SOUL-PROMOTION ⬡ 2026-08-24*
