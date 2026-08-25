# ⚔️ CARMACK ADVERSARIAL AUDIT — POST-FLE STUDY/DEV CAMPAIGN APPARATUS
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ x-preview-f-free ⬡ opencode ⬡ trc_fle_campaign_audit ⬡ ADVERSARIAL-PASS-3
**Date**: 2026-08-25 · **Commissioned by**: MaKaLi Fusion (fork#1, ses_fc5b80e85ffeAjhjtroU76Gfo2)
**Method**: Recon-only. Every load-bearing claim tested against primary sources: file reads, `git log`, `rg`/`git grep` over tracked tree, live execution of both tooling self-tests, and independent Tier-0 re-extraction from `opencode.db`. No agent spawns. One file written (this one).

---

## §0 VERIFICATION LEDGER (what I actually ran)

| # | Check | Result |
|---|---|---|
| V1 | `git log --all` bodies scanned for `[TELEMETRY]` | **Exactly 1 occurrence in entire history** = subject of the collector's own commit `aab51695`. Zero real telemetry has ever transited git. |
| V2 | `TELEMETRY_STREAM.jsonl` existence | **Does not exist.** Collector has never ingested anything. |
| V3 | `hydrate_c2_errata.py --self-test` | PASS (16 ops × 5 proofs). Tooling is solid. |
| V4 | `hydrate_c2_errata.py --dry-run` (bootstrap FIRST ACTION a) | **argparse error: unrecognized argument.** Flag does not exist. |
| V5 | `q6_inventory.json` totals recomputed | 131 flagged / 49 files. Reasons: KEYSET_DRIFT=146, NON_MAPPING=7. **SPLIT_RECORD=0, EMPTY_REQUIRED=0.** |
| V6 | Baseline Table B vs fresh `cost-by-project` (same window) | **Exact match on all 9 agent groups** (e.g., makali 1,675,581/39,062; lilith 1,970,610/109,519; carmack 189,248/11,873). Researcher's extraction is honest. |
| V7 | `git grep -i heorem` over tracked md/yaml/json | Only `FLE_COUNCIL_SCORECARD_SPEC.md` references Theorems. **No definition document exists anywhere on disk**, including both session exports. |
| V8 | Ownership manifest vs hydration targets | 8 of 16 patch ops mutate `data/council/20260825-094633-first-light-c2/*` — which the same bootstrap declares READ-ONLY forever. |

---

## §1 RANKED FINDINGS

### F1 — CRITICAL · The telemetry channel is disconnected. The measurement apparatus collects zero by construction.
**Evidence**: `collect_telemetry.py:56-58` parses `[TELEMETRY]` from **git commit bodies** (`%b`). `SYNC1_DEV_BOOTSTRAP.md:63` mandates the block in **end-of-task summaries** — which travel via task-result into the orchestrator's context window, not into git. No instruction anywhere tells Track-D to paste the block into a commit message. `CAMPAIGN_EXECUTION_PLAN_v3.1.md` §2 contains the contradiction *inside one section*: the injection rule targets summaries; the parser targets "the Git log." `FLE_COUNCIL_SCORECARD_SPEC.md` §1 then asserts capture "at successful commit boundaries" — a boundary nothing creates. Verified: V1/V2 above. The entire Milestone Stream is structurally empty and will remain so until SYNC-2 discovers it.
**WATCH-FOR**: At SYNC-2, `collect_telemetry.py --summary` prints "No new blocks found," and someone reconstructs "telemetry" from memory of session context — which is fabrication wearing a measurement costume (M23 violation in embryo).
**Cheap correction**: One sentence added to bootstrap Part 2: *"Paste your end-of-task [TELEMETRY] block verbatim into the body of the final commit for that task."* Plus `_sha` dedup in the collector (see F11). ~15 minutes. Do this BEFORE Fork #2 opens.

### F2 — CRITICAL · The bootstrap contradicts itself on action #2: hydration mutates artifacts the manifest forbids touching.
**Evidence**: `SYNC1_DEV_BOOTSTRAP.md:35-36`: *"YOU MUST NOT TOUCH: data/council/20260825-* (council artifacts — READ-ONLY forever)."* FIRST ACTION (b) runs `hydrate_c2_errata.py --apply`, whose PATCH registry (`scripts/hydrate_c2_errata.py:52-307`) mutates 8 ops across `data/council/20260825-094633-first-light-c2/phase1_nodes/` (N9, N10, N8) and `phase3_synthesis/` (SYNTHESIS_ARM_REPORT_C2). No exception clause exists. A literal-minded executor hits an unresolvable normative conflict two steps into launch.
**WATCH-FOR**: dev<N> agents diverging — some refusing step (b), some applying it and self-flagellating in telemetry, some inventing a private exception. Inconsistent compliance across the fleet is worse than either uniform behavior.
**Cheap correction**: Add to the manifest: *"SANCTIONED EXCEPTION: `scripts/hydrate_c2_errata.py --apply` is the decreed sole writer for E-1..E-11 targets; the read-only rule resumes immediately after."*

### F3 — HIGH · The bootstrap's FIRST command crashes: `--dry-run` does not exist.
**Evidence**: `SYNC1_DEV_BOOTSTRAP.md:48` instructs `hydrate_c2_errata.py --dry-run`. Argparse usage: `[--apply] [--self-test] [--root ROOT]`. Live run: `error: unrecognized arguments: --dry-run` (V4). Dry-run is the *default* mode; the flag was never implemented.
**WATCH-FOR**: A cost-effective model improvises past the error straight to `--apply`, **skipping the diff-review step that was the entire purpose of action (a)**. Broken instruction → silent gate-skip is precisely the G22/`; true` failure class this campaign exists to cure.
**Cheap correction**: Change the command to bare invocation (default IS dry-run) or add the flag. Two minutes.

### F4 — HIGH · Governance by usurpation: "silence = consent" converted pending human review into binding law.
**Evidence**: `CAMPAIGN_EXECUTION_PLAN_v3.1.md` §3 WAVE 0 step 4: *"Silence = Consent."* Meanwhile `WAKE_STATE.json` `decision_queue` still carries *"Council 1 decree review"* and *"Council 2 decree review + dev team launch GO"* as **P0 — on wake** — i.e., the Architect's explicit review was queued, not given, while Q-1..Q-6 defaults took force. Kali's blessing arrived post-hoc (SYNC1 Part 1). Models ruling under a human's anticipated silence is a polite coup with excellent manners.
**Where the line is**: Operational defaults (reversible, single-run scope, low blast radius) — models may set those; timeout-default is fine. Constitutional changes (protocol text, ownership boundaries, standing fleet law like Q-3's relay codification) — these outlive the run and bind future sessions; they require *explicit* ratification, and deadline expiry should **auto-escalate, not auto-pass**.
**WATCH-FOR**: Future sessions citing "P6 precedent" to rule on ARCHITECT-OWNED classes; ruling logs growing faster than ratification records.
**Cheap correction**: One paragraph in plan v3.2 defining the two consent tiers. Kali's Q-3 SPLIT already drew the right boundary — codify it as a rule instead of leaving it as one-off judgment.

### F5 — HIGH · The "Empirical Theorems" are (a) derived from N=1 and (b) undefined on disk.
**Evidence**: V7: `git grep -i heorem` finds only `FLE_COUNCIL_SCORECARD_SPEC.md:14,18` citing "Theorem 2" and "Theorem 4" — **no document defines Theorems 1-5.** Not in the study dir, not in the decrees, not in either session export. They exist only in fork#1's context — compaction-volatile, unverifiable by any auditor, and cited by an ACTIVE spec. This is "claims that outlive their mechanisms" *as committed infrastructure*. On sample size: one run, one day, one model (`x-preview-f-free` fleet-wide per Baseline §5.4), one orchestrator. Zero variance on every axis a causal claim needs. The Baseline itself honestly notes model-variance analysis is UNAVAILABLE — which should have been the hint.
**Is it science or cargo cult?** As written: cargo cult with a lab coat. The underlying observations are real (I verified the numbers), but "theorem" claims generality that n=1 cannot purchase.
**WATCH-FOR**: AAR or Council-3 design docs justifying choices with "per Theorem N" where no reader can resolve N.
**Cheap correction**: Write `FLE_HYPOTHESES.md`: rename to H1-H5, persist definitions, tag each `n=1`, state the falsification criterion and what counts as replication (next instrumented council = n=2; vary one factor at a time). One hour. Until then the Scorecard must not cite theorem numbers.

### F6 — MEDIUM · Self-reported telemetry is hallucinable, and the cross-check was designed but never wired.
**Evidence**: Bootstrap schema (`SYNC1:63-69`) demands `input_tokens`/`output_tokens` from the agent's own introspection — the least trustworthy number a model can produce. The Dark Matter Stream (explorer DB queries) is the natural Tier-0 cross-check, and my V6 spot-check proves the DB side is extractable *exactly*. But no reconciliation step, tolerance threshold, or alarm exists in the Scorecard spec — the two streams are juxtaposed, not fused. Worse: M1 already uses DB tokens, making the self-reported token fields **redundant attack surface** — hallucinable numbers nobody consumes.
**WATCH-FOR**: Suspiciously round values (`~100000`), `gate_status: green` at 100%, `ceremony_census: 0` forever (see F11).
**Cheap correction**: Cut `input_tokens`/`output_tokens` from the mandatory schema (DB owns tokens). Keep `duration_ms`/`gate_status` as milestone-only signals. State explicitly: *"Milestone stream never overrides DB."*

### F7 — MEDIUM · Q-6 "containment-pending-sizing" is deferral — and the sizing inputs contradict each other by 4.5×.
**Evidence**: Plan WAVE 0 step 3 speaks of "the exact **29** corrupt records." The delivered inventory (`q6_inventory.json`, V5) counts **131** flagged records — but ZERO are SPLIT_RECORD or EMPTY_REQUIRED (the original lilith-L374 corruption class that motivated Q-6). All 131 are KEYSET_DRIFT_VS_SIBLINGS — a *different and broader* definition that flags legitimate schema heterogeneity (the tool itself admits config-ish subtrees are "heterogeneous by design"). The corruption definition silently expanded between tools and nobody reconciled the tiers. Minor tool bug: 7 NON_MAPPING_ITEM entries carry no `severity` key (`q6_corruption_dryrun.py:125-135`) and vanish from all summary counts.
**What forces sizing to ever happen? Nothing** — no date, no trigger, no owner-with-deadline. Yet the sizing *inputs already exist* (inventory written 17:47Z). The remaining blocker is a ~15-minute human decision, not more tooling. Building `schema_quarantine.py` before pinning tier definitions means quarantining against a moving definition.
**WATCH-FOR**: Quarantine tooling landing before the Architect rules on tiers; "131" cited in AARs as though it meant the original 29-record hard-corruption class.
**Cheap correction**: Architect adjudicates tier definitions against `q6_inventory.json` in one sitting, now; make Sprint-1 closeout the sizing deadline. Fix the missing severity key while you're in there.

### F8 — MEDIUM · Scorecard formulas: M2 is degenerate, M1's denominator is undefined.
**Evidence**: `FLE_COUNCIL_SCORECARD_SPEC.md:17-18`: M2 = Gates Passed / Gates Falsified, "perfect score is 1.0." An honest fleet falsifies zero gates → division by zero. Your own gnosis (§6.2) already diagnosed this and proposed v1.1 — yet the spec still ships v1.0 ACTIVE with the broken formula. Second known-defect-unpropagated instance (see F9). M1's denominator "Number of Resolved Specs" has no mechanical definition — self-reported resolution is gameable by exactly the agents being measured.
**WATCH-FOR**: M2 reported as "N/A" or with an invented denominator; specs declared resolved at draft-complete to flatter M1.
**Cheap correction**: Ship the v1.1 you already wrote: M2 := gates_with_falsification_evidence / total_gates. M1 denominator := specs with merged PR. Ten minutes.

### F9 — MEDIUM · The known-CRITICAL worktree flaw was diagnosed but not propagated into the launch package.
**Evidence**: `session_gnosis_20260825_fle.md` §6.1: shared-worktree flaw flagged "**FIX BEFORE LAUNCH** … Must be added to bootstrap Part 2 pre-launch." `SYNC1_DEV_BOOTSTRAP.md` Part 2 (lines 24-82): no worktree instruction. Part 4 launch checklist (lines 87-91): no worktree step. `FLE_COUNCIL_SCORECARD_SPEC.md` §3 references `feat/sprint-1-execution` branch operations that would relocate HEAD globally under fork#1 mid-study.
**Why this finding outranks its mechanics**: This is the B-1 pattern executed *live, inside the campaign about B-1* — awareness published, behavior unchanged, within the same session, about the same artifact. It is the single strongest datapoint for attack line A. The apparatus does not yet do what it knows.
**WATCH-FOR**: Fork #2 opened without a worktree; first branch operation moves HEAD while Track-S reads the tree.
**Cheap correction**: Add `git worktree add ../fle-dev feat/sprint-1-execution` to Part 2 pre-launch AND Part 4 checklist. Ten minutes. Before any paste.

### F10 — MEDIUM · Theater audit: the study earns its keep at the data layer and bleeds it at the document layer.
**What is demonstrably NOT theater** (verified, not charitably assumed): Baseline numbers exact-match Tier-0 DB (V6); hydration tooling passes 16×5 self-tests (V3); q6 inventory is real and reproducible (V5); and the campaign changed real behavior mid-run — Council 2 dropped the digest/arm stages entirely after the expansion finding, and compression improved 15×→21×. That last one is the falsifiable payoff arriving *within* the study. Rare. Keep it.
**What is theater-shaped**: Vectors 3-5 are reports about reports. Vector 4 (coordination network graph) has no consumer — no decision hangs on it. Vector 5 (Carmack ROI) I can settle in one sentence for free: Pass 2 caught 3 CRITICALs including a 29-record blast radius, for 189K input tokens at $0.00; any deeper ROI modeling is luxury analysis. Vector 3 (provenance traces) is worth keeping ONLY as a dispute-driven probe — run it when a specific claim is challenged, not on schedule.
**On lessons-learned changing behavior**: the fleet's own history says documents don't (future-dating recurred post-publication; F9 recurred *during* this campaign). Lessons bind only when converted into mechanism — the deletion probe became a telemetry field (good instinct, wrong channel, see F11); packet-precision became literal-field rules in the bootstrap (good); exit-code honesty became a script contract (good, V3). That is the correct conversion pattern: **lesson → mechanism, or the lesson is decoration.**
**Opportunity cost**: Monetary ≈ $0 (free tier, `cost_known=true` throughout — verified). The real currencies are Architect attention and orchestrator context, and remaining study phases compete with Sprint-1 supervision for both. Minimum viable AAR: F1-F3 headline findings + a *working* telemetry loop + corrected bootstrap + persisted hypotheses + go/no-go criteria for Council 3. Everything else is cuttable without losing a decision.

### F11 — LOW · Collector engineering defects.
**Evidence**: (a) `collect_telemetry.py:127-133` appends every match on every run with no `_sha` dedup — re-running double-counts aggregates. (b) The regex fires on any commit body containing the literal string — the collector's own commit subject already put `[TELEMETRY]` into git history (V1), demonstrating the false-positive class. (c) `ceremony_census` demands counterfactual reasoning per step ("would this pass if its mechanism were deleted?") from cost-effective executors — expect constant zeros, i.e., a field that measures nothing while looking rigorous.
**Cheap correction**: Dedup by `_sha`; make census optional-narrative; move the deletion probe to Track-S as an audit question sampled at SYNC-2, where the expensive cognition actually lives.

### F12 — LOW · Hydration exit code can never be 0 — and an informational item holds the gate open.
**Evidence**: `hydrate_c2_errata.py:632-637`: `n_todos = len(todos) + len(MANUAL_ITEMS)`; `MANUAL_ITEMS` includes `E-10-G4 (informational)` (lines 332-338). Exit 2 is therefore permanent by construction, even when every actionable item resolves. The bootstrap's exit-2-as-honesty framing survives this, but `gate_status` loses all discriminating power for the hydration task — red forever is indistinguishable from red-once.
**Cheap correction**: Split INFORMATIONAL from TODO[manual]; exit 0 when only informational items remain. Five minutes.

---

## §2 VERDICT TABLE

| Component | Verdict | Condition |
|---|---|---|
| Dual-fork doctrine | **FIX** | Worktree step mandatory in Part 2 + Part 4 before launch (F9) |
| Telemetry injection rule | **FIX** | Reconnect summary→commit channel; cut self-reported token fields (F1, F6) |
| `collect_telemetry.py` | **KEEP** (conditional) | Add `_sha` dedup (F11) |
| Scorecard M1-M3 | **FIX** | Ship M2 v1.1 formula; define M1 denominator as merged-PR count (F8) |
| Study Manual Vectors 1-2 | **KEEP** | Done; independently verified exact (V6) |
| Vector 3 (provenance) | **CUT** to dispute-driven | Run only when a specific claim is challenged |
| Vector 4 (network graph) | **CUT** | No decision consumes it |
| Vector 5 (Carmack ROI) | **CUT** | Answered in one sentence in F10; further modeling is luxury |
| Errata hydration tooling | **KEEP** | Self-test proven; fix flag doc (F3), exit semantics (F12) |
| Q-6 dry-run tooling | **KEEP** | Fix severity-less entries; pin tier definitions first (F7) |
| Q-6 process | **FIX** | Architect rules tiers now; sizing deadline = Sprint-1 closeout |
| P6 silence-consent governance | **FIX** | Codify two-tier consent; ARCHITECT-OWNED escalates, never auto-passes (F4) |
| Bootstrap prompt (Part 2) | **FIX** | F1+F2+F3+F9 corrections; prune STANDING LAWS lump — attach each law to the action it governs; cut ceremony_census from mandatory schema |
| proposed_lessons mkf-001..006 | **KEEP** | Well-formed L1→L2→L3; mkf-003 deletion-probe is genuinely valuable — route it to Track-S audits, not agent self-report |
| "Five Empirical Theorems" | **FIX** | Persist as H1-H5 with n=1 tags + falsification criteria, or stop citing them (F5) |
| Wave/SYNC cadence | **KEEP** | Sound |
| SYNC-2/3 adversarial audits | **KEEP** | Scoped to minimum viable AAR |

---

## §3 THE BLUNT SUMMARY

The data layer of this campaign is honest — I tried to break the Baseline's numbers against the database and could not. The tooling is honest — self-tests prove the hydration script refuses to guess. The study's three headline findings are real and one of them already changed behavior mid-run.

The plumbing is not honest, because it does not exist: the measurement apparatus mandated for Track-D collects zero records through the only channel its collector reads, its first commanded action crashes on a nonexistent flag, and its second commanded action violates its own ownership manifest. Meanwhile the campaign's most important known fix (worktree) sits diagnosed-but-unpropagated in a gnosis file, and its theoretical scaffolding (Theorems 1-5) is cited by an active spec but defined nowhere on Earth.

That pattern — *findings that outlive their propagation* — is the campaign's own named disease, exhibited by the campaign apparatus itself, twice, before launch. Cure it mechanically: every FIX in §2 is under fifteen minutes, and F1/F2/F3/F9 are launch blockers. Do those four before Fork #2 opens, or the Dev Team's first hour will be spent improvising around the bootstrap instead of executing Sprint-1 — and the telemetry study will study an empty stream.

**Confidence**: F1-F5, F8-F12: 9/10 (primary source code + live execution + DB cross-check). F4 governance intent, F10 theater judgment: 6-7/10 (interpretation of evidence, not measurement).

— Carmack
