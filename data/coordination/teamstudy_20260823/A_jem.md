<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# A_jem — Phase-A Spec Review: Phase-2 Code Hardening Items

**AP Token**: `AP-JEM-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_synthesis ⬡ TEAMSTUDY-PHASEA

**Date**: 2026-08-23
**Mission**: Pre-implementation spec review of the four Phase-2 hardening items (SESSION_ANCHOR.md §Phase 2, items 1–4) for implementability, testability, and mandate compliance — BEFORE Ma'at builds.
**Sources reviewed**: `OVERSIGHT_AUDIT_WEB_RESEARCH_20260823.md` (W1–W4), `SESSION_ANCHOR.md`, `scripts/generate_session_registry.py`, `scripts/validate_tracking_state.py`, plus ground-truth reads of `data/coordination/session_annotations.yaml` and `scripts/sweep_task_registry.py` (both are silent interactors the specs don't mention).

---

## 0. Executive Verdict

All four specs are **directionally sound but under-specified**: 31 concrete gaps found, of which **5 are BLOCKING** (Ma'at cannot start without a ruling) and 8 are HIGH (would force mid-build invention). The single biggest landmine: **the W4 verdict enum (`pass/fail/flagged`) directly contradicts the live annotations file's declared M27 taxonomy (`completed/superseded/…`)** — the research rec was written without reading the data it governs. Second landmine: **item 1's "known hash" self-test is impossible as specified** because `render()` embeds wall-clock time and staleness ages into its output.

---

## 1. Per-Item Spec-Gap Tables

### Item 1 — Generator hardening (`generate_session_registry.py`)

| Gap ID | Severity | Gap | Why it bites |
|---|---|---|---|
| G1-1 | 🔴 BLOCKING | **Domain vocabulary undefined.** "domain-field validation" specifies neither the allowed values nor their source. Free-form string? Enum? Derived from GAP_REGISTRY topics? | Ma'at must invent a taxonomy mid-build; wrong choice invalidates the §2 Domain Index retroactively. |
| G1-2 | 🟠 HIGH | **Validation ownership + failure behavior unspecified.** Does an invalid domain fail the *generator* (exit ≠ 0, no output written) or is it a *validator* concern (pre-commit gate)? Carmack's ruling ("code verifies structure") implies the validator is the enforcement gate; the spec is silent. | Two plausible homes → duplicated or missing enforcement. |
| G1-3 | 🔴 BLOCKING | **Known-hash self-test is impossible as specified.** `render()` embeds `datetime.now()` in the GENERATED header (line 60) and computes staleness ages from wall clock (line 104-108). Output is non-deterministic by construction → no stable "known hash" exists. Spec must mandate an injectable clock parameter (e.g., `render(registry, annotations, now=None)`) and pin what the fixture hash covers. | Feature cannot ship without redesign; discovering this mid-build wastes a cycle. |
| G1-4 | 🟠 HIGH | **Self-test fixture location/content unspecified.** Inline synthetic registry+annotations (like `sweep_task_registry.py::self_test`) vs checked-in fixture files? Expected-hash stored where — hardcoded literal (breaks on every legitimate render change) or recomputed-and-compared (which only tests determinism, not correctness)? | The spec conflates two different guarantees: *determinism* (same input → same bytes) and *correctness* (bytes match expectation). Only the former is maintainable; say so explicitly. |
| G1-5 | 🟡 MED | **Idempotence-check mechanics unspecified.** Separate `--check-idempotence` flag? Folded into `--self-test`? Wired into `make session-registry` or CI? Exit codes? | Trivial to decide, but undecided means inconsistent. |
| G1-6 | 🟡 MED | **Legacy tasks without `domain:` field.** Fallback-to-first-tag behavior retained forever, or deprecated with warnings? Current registry is full of tag-only tasks. | Affects §4 hygiene section ("untagged" counter) and migration expectations. |

### Item 2 — Pydantic v2 annotations gate (`session_annotations.yaml`)

| Gap ID | Severity | Gap | Why it bites |
|---|---|---|---|
| G2-1 | 🔴 BLOCKING | **Verdict enum contradiction.** W4 rec: `Literal["pass","fail","flagged"]`. Live file header (line 9): *"verdict vocabulary: M27 ONLY — backlog\|ready\|in_progress\|blocked\|completed\|superseded\|failed"*, and all 15 existing entries use `completed`/`superseded`. The research rec was written against a hypothetical schema, not the deployed one. **Ruling needed: M27 taxonomy wins (recommended — it's mandated and in-use); W4's enum is discarded.** | Building the W4 enum as specified makes the validator reject 100% of real data on first run. |
| G2-2 | 🔴 BLOCKING | **Target-pattern schema wrong in rec.** W4's sample restricts IDs to `ses_`/`msg_` prefixes. Live file defines FOUR conventions: `<task_id>`, `<ses_id>`, `ho_<id>`, `agent:<name>` (lines 4-8). Schema needs a union/pattern validator covering all four, not the sample's narrow one. | Copying the sample validator breaks on `ho_06c9720dd2ae` and `agent:researcher` immediately. |
| G2-3 | 🟠 HIGH | **Grandfathering mechanism undefined.** Anchor says "hard-gate NEW entries; grandfather legacy" — but HOW is new-vs-legacy distinguished? Options: `assessed_at >= CUTOFF_DATE` constant; `annotation_id` date segment; explicit `legacy: true` flag. Each has different failure modes (backfilled entries dated today would look "new"). | Mid-build invention guaranteed; choice affects whether backfills (like Lilith's ann-20260823-010..019) pass. |
| G2-4 | 🟠 HIGH | **`extra="forbid"` vs legacy entries.** Do legacy (grandfathered) entries get `extra="allow"` while new entries get `forbid`? Two models needed? Or forbid universal (then verify no legacy entry has stray keys — unverified)? | Silent behavior difference between entry cohorts. |
| G2-5 | 🟡 MED | **Cross-record rules unspecified.** Duplicate `annotation_id` uniqueness, duplicate (target, assessor, verdict) tuples — neither mentioned. Natural home: `model_validator(mode="wrap")` at collection level. | Registry hygiene gap the whole study exists to close. |
| G2-6 | 🟡 MED | **Missing/empty file behavior in validator.** Generator warns-and-continues when annotations absent. Should the *validator* error, warn, or skip? Unspecified. | Fail-open vs fail-closed decision left to chance. |
| G2-7 | 🟡 MED | **Error presentation unspecified.** Raw pydantic `ValidationError` dumps multi-line tracebacks — unacceptable for a pre-commit gate. Spec should require conversion to `print_error` one-liners (file · field-path · offending value · expected) + exit 1, per M9. | Ugly gate output trains agents to ignore it. |
| G2-8 | 🟠 HIGH | **Generator shares the unvalidated parse path.** `generate_session_registry.py` reads the same YAML raw (lines 161-163). If validator gates commits but generator renders garbage silently from an invalid file, the GENERATED view diverges from gated truth. Spec should mandate ONE shared loader (`load_annotations() -> list[SessionAnnotation]`) used by both scripts. | Two parse paths = the exact drift this sprint fights. |

### Item 3 — JSONL hash-chain audit log

| Gap ID | Severity | Gap | Why it bites |
|---|---|---|---|
| G3-1 | 🔴 BLOCKING | **Canonical serialization unpinned.** `entry_hash = SHA256(prev_hash ‖ canonical(entry))` — canonical form must be pinned exactly: `json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")` or equivalent. Any future re-implementation that differs breaks chain verification. | One-line decision; without it, verifier and writer can silently disagree. |
| G3-2 | 🟠 HIGH | **entry_hash field-exclusion set unspecified.** Hash covers all fields EXCEPT `entry_hash` itself (obviously) — but say it, and decide whether `seq` is included (it must be, to bind ordering). | Ambiguity here = unverifiable chain. |
| G3-3 | 🟡 MED | **Genesis convention.** First entry's `prev_hash`: `"0" * 64`? Empty string? Must be fixed and tested. | Trivial but must be written down. |
| G3-4 | 🟠 HIGH | **Writer scope + honesty statement.** Only `sweep_task_registry.py --apply` mutates registries programmatically today. Manual `jq`/editor mutations are UNAUDITABLE. Spec must state the threat model honestly: chain proves *scripted* mutations only; it is tamper-*evidence*, not tamper-*prevention*. Per M23/C-0 honesty, overselling it is a false claim. | Prevents a false security narrative entering docs. |
| G3-5 | 🟠 HIGH | **Truncated-final-line policy.** Crash mid-append leaves a partial JSON line. Verifier must treat trailing-garbage as recoverable (truncate + re-append) vs fatal chain-break. These are opposite behaviors — pick one. | First real crash produces either silent corruption acceptance or a bricked audit trail. |
| G3-6 | 🟠 HIGH | **Rotation mechanics underspecified.** Monthly file `audit-YYYY-MM.jsonl` + `chain-heads.json` anchor: WHO writes chain-heads (writer at rotation? verifier?), WHEN (at first entry of new month?), and what happens when chain-heads.json is lost/corrupt (rescan-from-genesis fallback?). Also: does `seq` continue monotonically across files (yes — specify). | Rotation day is exactly when a half-specified system fails. |
| G3-7 | 🟡 MED | **Verification command ownership.** Weekly chain-verify "rides the W2 timer" — but W2/timer is OPTIONAL pending Kali decree (Anchor Phase 2 item 5). Is a `--verify-chain` subcommand in Phase-2 scope or deferred? If deferred and timer rejected, the chain is never verified — theater. | Chain nobody walks is decoration. Recommend: `--verify-chain` IS Phase-2 scope regardless of timer fate. |
| G3-8 | 🔴 BLOCKING | **Fail-closed ordering + exit code.** "fsync BEFORE registry mutation" implies: open audit → append → flush → `os.fsync(fd)` → THEN `atomic_write_json(registry)` → then `os.fsync` dir? And critically: **if the audit append/fsync FAILS, the mutation must NOT proceed** — distinct exit code (recommend 1, internal error) and zero registry writes. Spec states the happy-path order but not the failure branch. | The entire point of audit-before-mutate collapses if append-failure still mutates. |
| G3-9 | 🟡 MED | **Durability asymmetry.** Existing `atomic_write_json` does tmp→rename WITHOUT fsync of the tmp file. Post-crash, rename may be durable while data isn't. For the audit guarantee to mean anything, the registry write should fsync-before-rename too (or spec explicitly accepts the weaker guarantee: audited-but-unapplied is the recoverable direction — which the researcher's own rationale supports; then document it). | Half-durable pipeline gives false confidence. |
| G3-10 | 🟡 MED | **Concurrency.** Two concurrent `--apply` runs interleave appends and mutations. Single-user engine → likely acceptable to declare serial-execution assumption + optional flock, but SAY it. | Rare, but a torn chain is undiagnosable after the fact. |

### Item 4 — Class-based staleness thresholds (`validate_tracking_state.py`)

| Gap ID | Severity | Gap | Why it bites |
|---|---|---|---|
| G4-1 | 🔴 BLOCKING | **Class-assignment rule undefined.** How does a task become class `research`? By `subagent_type == "researcher"`? By a `research` tag? By `domain`? The spec names three classes but zero assignment criteria. This is THE central design decision of item 4 and it's absent. | Nothing can be built until this is ruled. Recommendation: derive from explicit task field (`stale_class: standard\|research` defaulting to standard) — explicit beats inferred, and inference from tags couples to item 1's unresolved domain vocabulary (see IR-6). |
| G4-2 | 🟠 HIGH | **Scope expansion unstated: `blocked` staleness is NEW enforcement.** Current staleness rule ONLY checks `in_progress` tasks (validator line 230; sweep line 68). Adding `blocked=14d` means blocked tasks — never previously staleness-checked — now error/warn at 14d. Is that error or warn? Blocked-without-blocker-note was in the W1 table ("+ mandatory blocker note") but dropped from the Phase-2 spec — in or out? | Quiet scope growth; also changes pre-commit outcomes for existing data (unknown count of >14d blocked tasks — measure before gating). |
| G4-3 | 🟠 HIGH | **Override semantics fuzzy.** `stale_override_days`: replace-or-extend? "Validated ≤ class max" implies effective_threshold = min(override, class_max) — i.e., override can only EXTEND toward the class ceiling, never beyond, and never below default? Confirm arithmetic, and: violation = error or warn? Who validates the field's presence/type (int, positive)? | Off-by-one-direction bugs here either neuter the cap or strand live work. |
| G4-4 | 🟠 HIGH | **`STALENESS_DAYS` backward compatibility.** BOTH `generate_session_registry.py` (line 31) and `sweep_task_registry.py` (line 35) import `STALENESS_DAYS`. Refactoring to a class dict breaks both imports. Spec must mandate: keep `STALENESS_DAYS = THRESHOLDS["standard"]` alias AND update both consumers to class-aware lookup in the same change. | Import breakage discovered at pre-commit time, not build time. |
| G4-5 | 🔴 BLOCKING | **Sweep parity unaddressed.** `find_expired()` in sweep uses the flat constant. If the validator moves to per-class thresholds and sweep doesn't, the two tools DISAGREE: validator flags a research task at 8d, sweep ignores it (or vice versa: sweep kills a 22d research task the validator considers fresh — catastrophic misclassification, G5-1 recurrence). Spec must require a SHARED `effective_threshold(task) -> int` function imported by both. | Validator/sweep divergence is the worst possible failure of this feature. |
| G4-6 | 🟡 MED | **Threshold config location.** Module constants (current style) vs external config? Recommend constants in `validate_tracking_state.py` (no new config plumbing, matches repo pattern); spec should say so to prevent a YAML detour. | Minor, but undecided defaults drift. |
| G4-7 | 🟡 MED | **Boundary semantics.** `(now - ts).days` truncates; comparisons are strictly `>`. Keep `> threshold` uniformly and document that a task at exactly 21d is fresh, 21d+1s is stale? Consistency between validator, sweep, and the generator's §4 hygiene counter (which ALSO reimplements staleness at line 105-108!) must be stated. | Three independent staleness implementations already exist; a fourth variant is how drift starts. |

---

## 2. Test Requirements (M21 Contract Tests)

Scripts currently carry inline `--self-test` fixtures rather than pytest suites; either venue works, but every item below must exist somewhere and validate RETURN TYPES, not just absence-of-crash (M21):

**Item 1 — Generator**
1. `render()` returns `str` ending in `\n` for a minimal fixture (contract: return type).
2. `task_domain()` precedence: explicit `domain` > first tag > `"(untagged)"` — table-driven, 3 cases.
3. `esc()` escapes `|` and handles None/empty → `"—"`.
4. **Determinism**: two `render()` calls with identical inputs AND injected fixed clock → byte-identical (this is the fixable version of G1-3).
5. `atomic_write()`: output exists with mode 0644; no `.tmp` residue on success OR on induced write failure.
6. Self-test binary behavior: exits 0 on healthy fixture, exits ≠ 0 on a deliberately corrupted fixture (fail-closed proof, mirroring sweep's self-test pattern).
7. Invalid domain input → specified behavior (error+exit≠0 or warning) — whichever G1-2 rules.

**Item 2 — Annotations gate**
1. Valid full file (all four target conventions: task_id, `ses_*`, `ho_*`, `agent:*`) parses to `list[SessionAnnotation]`.
2. Each violation class independently errors with exit 1 and message naming field-path: bad verdict, unknown key (extra=forbid), malformed datetime, missing required field, duplicate annotation_id, malformed target pattern.
3. Legacy entries older than cutoff pass structural validation even if they'd violate new-entry rules (grandfathering proof).
4. New entry violating verdict enum fails EVEN IF otherwise well-formed (teeth proof).
5. Missing file / empty `annotations:` list → ruled behavior from G2-6, tested.
6. Shared-loader contract: generator and validator produce identical parsed models from the same file (IR-3 guard).

**Item 3 — Audit log**
1. Clean chain verifies: N appended records → walk passes, head hash matches.
2. Tamper matrix: flip one byte in entry k's payload → verify fails AT entry k (names seq); delete middle line → fails; swap two lines → fails. (This is the core value; test all three.)
3. Genesis entry has the ruled prev_hash sentinel (G3-3).
4. Ordering instrumentation: with a mocked failing audit append, `apply_failures` performs ZERO registry writes and exits with the ruled code (G3-8 fail-closed proof — the most important test in the whole Phase 2).
5. Rotation: entry spanning month boundary carries prev_hash of prior month's tail; chain-heads.json updated; cross-file walk passes.
6. Truncated final line behaves per G3-5 ruling (recoverable-truncate or fatal — tested either way).
7. Round-trip: write → verify → append → verify again (idempotent verifier).

**Item 4 — Thresholds**
1. `effective_threshold(task)` returns int; pure function; table-driven over: default/standard, research-classed, blocked-status, override-below-cap, override-at-cap, override-above-cap (clamped), override-non-int (ruled behavior).
2. Boundary: age exactly == threshold → fresh; threshold + smallest increment → stale (locks G4-7).
3. **Validator↔sweep consistency contract**: same synthetic registry fed to both → identical offender sets (G4-5 guard; single most valuable item-4 test).
4. `STALENESS_DAYS` import survives in both consumer scripts (smoke-import test).
5. Blocked-status staleness fires at 14d and NOT at 7d (new-surface proof, G4-2).

---

## 3. Mandate Compliance Matrix

| Mandate | Item 1 | Item 2 | Item 3 | Item 4 | Notes |
|---|---|---|---|---|---|
| **M1 AnyIO** | N/A | N/A | N/A | N/A | All four are synchronous CLI scripts; no event loop. If any piece is ever absorbed into the Hub, wrap in `anyio.to_thread.run_sync`. No async code may be introduced "for future-proofing." |
| **M9 Error Integrity** | ⚠️ G1-2 | ⚠️ G2-7 | ⚠️ G3-8 | ⚠️ G4-3 | Scripts use print_error+exit (acceptable script convention), but every NEW failure branch must be explicit: no bare except, no silent swallow. Pydantic ValidationErrors must be converted, not dumped raw. |
| **M10/T10 Atomic Writes** | ✅ exists | N/A (read-only) | ⚠️ G3-9 | ✅ | Generator already atomic+0644. Audit log needs append+fsync semantics (different from tmp→rename — specify it). Registry-side fsync gap flagged. |
| **M12 Queue Integrity** | — | — | ✅ aligned | — | Audit log IS the terminal-state ledger for sweep mutations; aligns with "no orphan mutations." |
| **M13 Temple-Grade** | T3/T21 | T3/T21 | T9/T10/T21 | T3/T21 | All four add logic to pre-commit-gated scripts → coverage and contract-test gates apply. Self-tests satisfy the spirit if pytest suites aren't extended; prefer pytest for the tamper matrix (needs fixtures). |
| **M17 Cognitive Integrity** | — | ✅ core | ✅ aligned | ✅ core | Items 2+4 ARE memory-consistency enforcement. Item 3 provides the evidence trail M17 audits will consume. |
| **M18 Token Efficiency** | ✅ | ✅ | ✅ | ✅ | All scoped small. Sane-boundary: this review is long because precision > brevity, per M18's own carve-out. |
| **M21 Gate Integrity** | 🔴 tests TBD | 🔴 tests TBD | 🔴 tests TBD | 🔴 tests TBD | Section 2 above is the minimum contract-test set. Mock-based-only tests forbidden — the tamper matrix and fail-closed tests exercise real file I/O. |
| **M22 Provenance** | — | — | ✅ `actor` field | — | Audit records capture actor+tool; ensure actor comes from actual invoking entity, not a hardcoded default. |
| **M23 Failure Integrity** | — | — | 🔴 G3-8 | — | Audit-append failure MUST abort mutation (fail-closed). A sweep that mutates despite audit failure is simulated rigor — textbook M23 violation. |
| **M24 Venv Sovereignty** | ✅ | ⚠️ verify | ✅ | ✅ | Pydantic 2.13.4 confirmed in `.venv`. ACTION: confirm the pre-commit hook (`omega-tracking-state`, `.pre-commit-config.yaml:137`) invokes `.venv/bin/python` — if it runs under system/hook-python, the new pydantic import bricks every commit. |
| **M27 Tracking Integrity** | ✅ | ✅ | ⚠️ IR-8 | ✅ | `chain-heads.json` is a NEW coordination artifact — classify it under the tracking architecture (Tier-3 adjacent, committed) or it becomes an ad-hoc file M27 forbids. |

---

## 4. Interaction Risk Register

| IR ID | Items | Risk | Severity | Mitigation |
|---|---|---|---|---|
| IR-1 | 4 ↔ 1,3 | `STALENESS_DAYS` refactor breaks imports in generator AND sweep (both import it today). | 🔴 | Keep alias constant + update both consumers in same commit (G4-4). |
| IR-2 | 3 ↔ sweep exit codes | Sweep `--apply` can apply failures AND exit 3 (review-list cases). Audit records exist for applied subset even on exit 3 — correct, but the audit record must be written BEFORE any registry mutation and the run's exit code must not suppress audit verification. Conversely: audit-append failure must force exit 1 with ZERO mutations, overriding any other exit-code logic. | 🔴 | Explicit ordered state machine in sweep: audit-fsync-ok → mutate → report; audit-fail → abort. Test IR via item-3 test #4. |
| IR-3 | 2 ↔ 1 | Generator reads annotations raw; validator gates them. Ungated file + generator = GENERATED view renders content the gate would reject → view/truth divergence. | 🟠 | Single shared `load_annotations()` (G2-8); generator refuses to render invalid annotations. |
| IR-4 | 2 ↔ data | Verdict enum collision (G2-1): building W4's `pass/fail/flagged` rejects all 15 live entries. | 🔴 | Ruling before build: M27 taxonomy wins. |
| IR-5 | 1 ↔ clock | Wall-clock in `render()` defeats both the known-hash self-test AND the idempotence check near second/day boundaries (flaky, intermittent CI failures). | 🔴 | Inject `now` param; freeze in tests and self-test. |
| IR-6 | 1 ↔ 4 | If research-class assignment keys off `domain` (tempting, since item 1 adds the field), the two features couple through an UNDEFINED vocabulary (G1-1). Changing domains later silently reclassifies staleness horizons. | 🟠 | Decouple: staleness class from explicit task field, not derived from domain/tag (G4-1 recommendation). |
| IR-7 | 2 ↔ legacy | Grandfather cutoff interacts with `extra="forbid"`: a legacy entry with a stray key passes verdict-grandfathering but fails forbid (or vice versa) depending on implementation order. Define: TWO models (LegacyAnnotation superset / SessionAnnotation strict) with one discriminator, tested both ways. | 🟡 | G2-3/G2-4 rulings + test #3/#4. |
| IR-8 | 3 ↔ M27 | `chain-heads.json` + monthly `audit-*.jsonl` are new tracked artifacts; PATH-STAGED commit discipline (Phase 3) must include them or the chain anchor is uncommitted/unverifiable for other clones. | 🟡 | Add to Phase-3 commit manifest + TRACKING_ARCHITECTURE classification. |
| IR-9 | 4 ↔ generator §4 | Generator §4 Computed Hygiene REIMPLEMENTS staleness inline (lines 105-108) with the flat constant. After item 4, three implementations exist (validator, sweep, generator). Fourth variant = guaranteed drift. | 🟠 | Extract shared `staleness.py` helper (`effective_threshold`, `find_stale(tasks, now)`) consumed by all three; generator's hygiene section becomes a thin call. |

---

## 5. Build-Readiness Rulings Needed Before Ma'at Starts

1. **G2-1**: Verdict enum = M27 taxonomy (discard W4's pass/fail/flagged). *(Recommended; near-certain.)*
2. **G4-1**: Staleness-class assignment mechanism (explicit `stale_class` field recommended over tag/domain inference).
3. **G1-1**: Domain vocabulary + source of truth.
4. **G2-3**: Grandfather discriminator (cutoff date vs explicit flag).
5. **G3-8**: Confirmed fail-closed contract: audit-fsync failure ⇒ exit 1, zero mutations.

Everything else can be resolved by Ma'at using the recommendations in this document, provided the resolutions land in the code as documented decisions (docstring + PIVOT_LOG entry per M4).

---

## 6. Summary Counts

| Item | Blocking | High | Medium | Total |
|---|---|---|---|---|
| 1 — Generator hardening | 2 | 2 | 2 | 6 |
| 2 — Pydantic annotations gate | 2 | 3 | 3 | 8 |
| 3 — JSONL hash-chain audit log | 1 | 4 | 5 | 10 |
| 4 — Class-based thresholds | 2 | 3 | 2 | 7 |
| **Total** | **7** | **12** | **12** | **31** |

*(Note: G3-8 counted once as blocking though it anchors both item 3 and IR-2.)*

---
*⬡ OMEGA ⬡ JEM ⬡ TEAMSTUDY-PHASEA ⬡ 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
