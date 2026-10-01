<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# B_jem — Phase-B Cross-Synthesis: Compliance Adjudication
**AP Token**: `AP-JEM-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_synthesis ⬡ TEAMSTUDY-PHASEB

**Date**: 2026-08-23
**Inputs read**: `A_researcher.md`, `A_roc.md`, `A_carmack.md` (my `A_jem.md` carried forward).
**New ground truth gathered this phase** (not parametric):
- `.git/hooks/pre-commit` read live: **6 lines, soul-validation only** — confirms researcher G2.
- `.pre-commit-config.yaml:137-139` grepped live: `omega-tracking-state` IS defined there, `entry: python scripts/validate_tracking_state.py`. The config exists; it is **not wired into the executed hook path**.
- SOVEREIGN_MANDATES.md:230,233 + Makefile:238 + MANDATES_CONDENSED.md:47 all assert the hook as live enforcement. Four documents describe an enforcement surface that does not execute.

---

## 1. FINDINGS — Compliance Implications & Adjudications

### F-A. The G2 finding is worse than researcher reported — and it vindicates my domain directly

Researcher's G2 ("the claimed pre-commit hook doesn't exist") is **confirmed and refined**. The reality is a three-layer split:

| Layer | State |
|---|---|
| Mandate text (M27 §Enforcement) | Claims hook blocks commits |
| Config (`.pre-commit-config.yaml:137`) | Defines the hook — but `entry: python` (not `.venv/bin/python`, my A-report M24 concern **confirmed**) |
| Executed path (`.git/hooks/pre-commit`) | Hand-written 6-line script; never calls the framework or the validator |

**Adjudication**: This is a single root cause wearing two masks — my M24 venv concern and researcher's G2 are the same defect. The fix is neither researcher's "extend the pre-commit hook" framing nor carmack's "extend the validator" alone. It is:

1. **Reconcile the executed path FIRST** (~5 min): append one line to the existing 6-line bash hook — `.venv/bin/python3 scripts/validate_tracking_state.py || exit 1` — OR run `pre-commit install` if the framework is intended to own the hook. Pick one owner; today there are zero owners.
2. Then researcher's CEB commit-time evidence binding rides that reconciled surface.
3. **C2-class remedy upgraded from "nice-to-have" to P0**: `make verify-mandate-claims` (researcher §2) is now proven necessary by live evidence — FOUR documents lie about enforcement simultaneously. This is exactly the "mandates that lie are worse than code that fails" case. I adopt it into my compliance matrix as an M27/M23 joint gate. Cost is a grep harness; refusal to build it after this finding would be M23 theater.

### F-B. Carmack CUT-1 (defer hash-chain audit log) vs my IR-2/G3-8 fail-closed register — ADJUDICATED: DEFER, WITH CONDITIONS

Carmack's cut collides with my risk register on its face. On inspection, it survives — because my register was governing the *build*, and the build is being cancelled:

- **G3-1…G3-10 (10 gaps incl. blocking G3-8)** become MOOT under deferral. Item 3 was my gap-densest item; cutting it removes 10 of my 31 gaps and 1 of 7 blockers. I concede the efficiency case: threat model = one operator, one machine, pre-publication; hash-chaining against yourself is security theater, which is itself an M23 violation of a subtler kind (simulated rigor).
- **CONDITIONS of acceptance** (non-negotiable):
  1. **Documented exception, not silent drop** — same pattern as the T11 exemption: record in PIVOT_LOG + Manual with remediation trigger ("post-debut, when ≥2 writers share TASK_REGISTRY.json"). An undocumented deferral of an audit control is how M12 queue-integrity debt accretes invisibly.
  2. **The fail-closed PRINCIPLE survives the mechanism** (IR-2 reduced form): sweep `--apply` must still have typed exit semantics — mutation-failure ⇒ exit ≠ 0 with zero partial state; review-list cases exit 3 without masquerading as success. That half of IR-2 costs nothing (it's specification, not machinery) and stays in scope.
  3. **Post-debut ticket now**, per carmack's own Ruling #4 logic (a design without a living ticket is dead). One JSON entry referencing my G3-1..G3-10 list so the spec work isn't redone.

### F-C. Carmack Ruling #6 vs researcher CEB — ADJUDICATED: MERGE, they are not actually in conflict

Carmack says "one validator rule, no new hook system." Researcher proposes commit-time + claim-time + sweep-time checkpoints. Synthesis ruling:

- **Evidence standard**: adopt researcher's — machine-checkable `{artifact_path, check_cmd?}`; prose is not evidence; no LLM judgment in the loop (`os.path.exists()` + exit codes). This is CEB's real contribution and it is excellent.
- **Mechanism**: adopt carmack's — implement inside `validate_tracking_state.py`, advisory-warn → hard gate after two clean weeks. No new daemon, no new state store. Researcher's own anti-theater guardrail #1 agrees with him.
- **Cut the claim-time helper** (carmack cut candidate 3a): ACCEPT. Hivemind-posted prose claims can't be mechanically gated anyway without building the thing we just refused to build. Sweep-time spot-check covers rot; commit-time covers authorship.
- **Keep the mandate-claims verifier** (see F-A): this is where I overrule carmack's minimalism. His Ruling #6 addresses C1 (claim-without-artifact). It structurally cannot address C2 (claim-without-enforcement) — a registry validator never reads SOVEREIGN_MANDATES.md. Today's four-document lie proves C2 is live. ~20 lines of grep; build it.

### F-D. Roc's flags are compliance evidence, not just backfill corrections

- **F1 (filename drift, 5 paths)**: This is a C1-class sighting caught *before* registration — precisely what the CEB `artifact_path` existence check automates. Roc's manual mtime cross-check is the human version of the machine check we're about to build. Backfill MUST use his corrected paths verbatim; Lilith registering ledger-original names would create dangling pointers that the new hard gate would then reject — embarrassing symmetry worth avoiding.
- **F3/F4 (launched_by=kali for Missions A/B + N5)**: M22 provenance issue. Attribution must reflect actual parentage, not narrative convenience. Adopt roc's split attribution.
- **F5 (stale handoff status in gnosis addendum)**: minor, but note the pattern — *prose ledgers rot silently*. This is the strongest argument for researcher's evidence fields and against carmack's CUT-3 being extended anywhere near living documents. Historical backfill annotations: skippable (I agree with CUT-3). Living status claims: need mechanical backing.
- **F2 (my own AUD updates unmerged)**: **Owned by me.** My `GAP_REGISTRY_UPDATES_20260822.json` (25 AUD- IDs) was delivered but never merged into `GAP_REGISTRY.json`. This is a completion-gap in MY OWN output — the exact pattern this study exists to close. I flag it rather than bury it: merging is a separate ticket, and it should be the first task registered under the new evidence-binding rule once live.

---

## 2. INSIGHTS — Where quality/compliance aligns or conflicts with research designs & efficiency cuts

**Convergence (strong signal — three independent arrivals):**
All four reports converge on one principle from different directions: **mechanical enforcement beats prompt compliance**. Researcher: "registration is prompt-enforced only." Carmack: "documents do not stop writes" + measured 6-day drift the process missed. Roc: verified everything against DB/disk instead of trusting ledgers. Me: 31 spec gaps, most of which are "the spec asserts X but nothing checks X." When four agents independently hit the same wall, that is not four findings — it is one architectural gap (enforcement-by-convention) observed four ways. The closeout plan should name it as such, not patch instances.

**Alignment:** Carmack's cuts and my compliance matrix are complementary more than opposed. His CUT-1 deletes my gap-densest item; his Ruling #6 implements my G2-7 error-presentation concern via the existing validator; his wc-l freeze gate (Ruling #1) is a mandate-claims verifier for god-modules — same pattern, different target. Efficiency and compliance are not at war here; they're both attacking assertion-without-verification.

**Conflict points requiring the rulings below:**
1. Researcher's hybrid adds NEW coordination artifacts (hook stubs, heartbeat counters, `source=backfill` fields) — each one is potential M27 ad-hoc-state debt, the exact class my IR-8 flagged for `chain-heads.json`. Efficiency research designs routinely invent state; M27 requires every new field/file be classified before birth.
2. Carmack's protocol critique (drop Phase E, fold D into M11) is compliance-POSITIVE for D (M11 already mandates distillation; running it twice is ritual duplication) but leaves Phase C without a stated termination guarantee if E is deferred — convergence criterion must be written down or discourse runs on fatigue, which is the failure mode the charter explicitly replaced.
3. CUT-3 (skip annotations) is safe for concluded sessions but must not leak into living ledgers (F5 shows why).

---

## 3. QUESTIONS & CHALLENGES TO NAMED TEAMMATES

### To RESEARCHER — pressure-testing the hybrid registration design against M27 taxonomy rules

1. **Stub vocabulary**: Your hook writes stubs at `status=in_progress`. Fine for Tier-3. But your §1 option-(b) auto-backfill sweep reconstructs *concluded* sessions — what status does a backfilled completed session get? Tier-0 forbids `failed`; Tier-3 allows it. If your backfill can't distinguish which tier a session belonged to, it will write illegal states. Specify tier-detection before the backfill script is written.
2. **`source=backfill` and the heartbeat counter are NEW registry schema fields.** Under M27, TASK_REGISTRY.json is the SSOT with a defined shape — who rules on schema extensions? My recommendation: `source` allowed as provenance metadata (M22-aligned), heartbeat counter lives OUTSIDE the registry (coordination metrics file), or you've built an ad-hoc tracking artifact inside the canonical one.
3. **Drift-alarm false-positive rate**: "session seen active in Hivemind awareness but absent from registry → error" — Hivemind awareness includes heartbeat-only sessions, meditation records, and direct (non-task()) agent activity (roc's row 8: the ox-alpha meditation has NO session and SHOULD have no registry row). Without a dispatch-source filter your alarm fires on legitimate non-dispatch presence, and agents learn to ignore it — the stub-quality problem you yourself identified, arriving via the alarm instead. Filter on channel/subagent-type or accept alarm fatigue.
4. **Your Q5 (evidence on `failed` transitions)**: answered by taxonomy scoping — yes for Tier-3 (where `failed` is legal and Carmack's ruling protects it as distinct signal), N/A for Tier-0 (state doesn't exist there). Failure evidence should be lighter than success evidence: a reason string + optional artifact; demanding test artifacts for failures incentivizes laundering failures into `blocked`.

### To ROC_RACOON — evidence standards for the unverified remainder

1. Your 18/18 sweep verified **existence and attribution** (session in DB, file on disk, mtime coherence). What is your standard for **content fidelity** — artifact exists but doesn't contain what the ledger claims? Row 8 you spot-checked content (L3 verbatim at :119); rows 1–16 were existence-only. For the backfill: do we register existence-verified entries at full confidence, or does content-unverified carry a lower evidence grade? If CEB adopts optional `artifact_hash`, your mtime method generalizes — but hashes go stale on legitimate edits. Recommend: existence + mtime-window as the standard evidence grade; hash reserved for tamper-sensitive artifacts post-debut (aligns with CUT-1 deferral).
2. **Attribution rule needed** (your F3/F4 + researcher's open Q4): when parent chain is kali → researcher → subagent, is `launched_by` the immediate parent session or the mission owner? You resolved 16 rows by inspection; the ~20-row orphan backfill needs this as a STATED RULE, not per-row judgment. My recommendation: `launched_by` = immediate parent session's entity (mechanically derivable from opencode.db); mission ownership recorded separately in notes. Rule beats archaeology.
3. Your 5/5 pointer-integrity pass found one stale §11 pointer in SOVEREIGN_ARK_BLUEPRINT (carmack-audit doc moved to archive). Small, but it's another C2-class instance — a strategy document pointing at moved evidence. Add "doc-pointer spot-check" to whatever sweep cadence emerges.

### To CARMACK — challenges where cuts create Temple-Grade or M23 exposure

1. **Ruling #6 is necessary but insufficient, and your own evidence proves it**: your §0 found six files drifted during a freeze week because "nothing measured it." The identical logic applies to mandate text: four documents assert a hook that doesn't execute — nothing greps them. Your one-validator-rule addresses C1 only. Refusing the ~20-line `verify-mandate-claims` target after BOTH of us measured live C2 instances is the over-engineering sane-boundary applied in reverse — under-engineering past the point of known failure modes. Accept the grep harness; it's five lines of Makefile, your own favorite unit of enforcement.
2. **CUT-1 accepted with conditions** (F-B above) — but your "cost of deferring: zero" claim needs one amendment: the cost is zero only if the exception is DOCUMENTED with a remediation trigger. Undocumented deferral of an audit control is deferred cost compounding at M12 interest. Your own Ruling #4 logic (ticket-or-death) applies to your own cut.
3. **Protocol assessment**: I ratify folding Phase D into standard M11 flow (compliance-positive — no double ritual) and deferring E. But striking E without writing the convergence criterion into Phase C removes the termination guarantee the charter exists to provide. Keep the criterion, defer the meta-review — those are separable and you've conflated them.
4. **CUT-3 boundary condition**: agreed for historical annotations; rejected as a general principle. F5 (stale handoff status in a living gnosis addendum) shows living status-claims DO need mechanical backing. Cut history-annotation prose; don't cut status-mechanization.

---

## 4. REVISIONS TO MY OWN A REPORT

| Revision | Trigger | Effect |
|---|---|---|
| **Item 3 (audit log) gaps G3-1..G3-10 → MOOT** | Carmack CUT-1 adopted (F-B) | 31 → **21 gaps**; blocking 7 → **6** (G3-8 removed); high 12 → 9 |
| **IR-2 downgraded 🔴→🟡** | Same | Audit-before-mutate ordering gone; residual = typed exit semantics for `--apply` (spec-only, cheap) |
| **IR-8 closed** | Same | `chain-heads.json` never born; no classification needed |
| **M24 concern CONFIRMED, root-caused** | Live grep this phase | `.pre-commit-config.yaml` uses bare `python`, AND the framework isn't in the executed hook path at all. One reconciliation fixes both. Escalated from "verify" to "confirmed defect" |
| **New gap set inherited from Hole 1**: researcher's hybrid needs its own spec review (stub schema fields, tier-detection for backfilled statuses, alarm filtering, heartbeat-counter placement) — est. 5–8 new gaps by my standards | Teammate input | Net complexity shifts from item 3 (cancelled) to Hole 1 (auto-registration). Ma'at's Phase-2 load drops; Hole-1 design review becomes my next deliverable if the hybrid is ratified |
| **G2-1 ruling reinforced** | Roc's independent confirmation (15/15 live entries use M27 vocabulary) | Verdict enum = M27 taxonomy. Now ruled with dual-source evidence, not just my read |
| **Test plan amendments** | F-B/C | Item-3 test block (7 tests incl. tamper matrix) struck; item-3 test #4's fail-closed proof survives in reduced form as "sweep --apply failure ⇒ typed exit, no partial state"; ADD one test: reconciled pre-commit hook invokes `.venv/bin/python` (locks M24 permanently) |

**Unchanged**: Items 1, 2, 4 gap lists stand as written. The five pre-build rulings (§5 of my A report) shrink to **four** — G3-8 drops out; G2-1 is now effectively decided pending Kali's stamp.

---

## 5. CONVERGENCE LEDGER ENTRY (for kali / Phase C)

Contested points I now recommend rulings on:

| # | Contested point | JEM ruling recommendation |
|---|---|---|
| R-1 | Hash-chain audit log (item 3) | **DEFER** post-debut, WITH documented exception + ticket carrying my G3-1..10 list. Fail-closed exit semantics for `--apply` stay in scope. |
| R-2 | M23 standing verification shape | **CEB evidence standard (researcher) inside validate_tracking_state.py (carmack), advisory→hard after 2 clean weeks. Claim-time helper CUT. Mandate-claims verifier BUILT (P0).** |
| R-3 | Pre-commit reconciliation | **First action, today**: single owner for the hook path (install framework OR extend 6-line bash hook with `.venv/bin/python3` validator call). Fixes G2 + M24 in one move. |
| R-4 | Hybrid registration | **Weighted-to-(a) hybrid provisionally endorsed**, contingent on researcher answering the four M27 taxonomy questions in §3 above (stub statuses, schema-field classification, alarm filtering, tier detection). |
| R-5 | Backfill execution | **Corrected paths per roc F1 verbatim; launched_by=kali per F3/F4; attribution rule = immediate-parent (pending roc concurrence); correctness-only scope per carmack CUT-3; `ox-alpha-100t-research-20260822` flip carries evidence field from day one.** |
| R-6 | Protocol shape | **A→B→C→M11-distill-at-convergence; E deferred to Study #3; convergence criterion WRITTEN into charter before E-deferral takes effect; fix the five-vs-six phase miscount.** |

---
---

## PHASE-C RESPONSE (jem)
**AP Token**: `AP-JEM-v1.0.0`
⬡ OMEGA ⬡ JEM ⬡ x-preview-f-free ⬡ opencode ⬡ trc_synthesis ⬡ TEAMSTUDY-PHASEC

**Date**: 2026-08-23 · **Inputs**: `C_discourse_ledger.md` in full + re-read of A/B corpus for routed context.

### O-Q1 — Grandfathering mechanism (carmack → jem): FINAL PICK

**PICK: Explicit flag — specifically researcher's `source={live, backfill}` enum as the discriminator. Cutoff-date REJECTED as primary gate; retained only as a tripwire assertion.**

Carmack asked: does cutoff-date have a failure mode the explicit-flag avoids? Yes — three:

1. **Accidental cohort assignment.** Cutoff-date classifies by accident of timing. Any entry written after the constant is frozen but before the gate deploys silently lands in whichever cohort the inequality puts it — no human made that decision. Worse, the discriminator is forgeable-by-accident: a clock-skewed write or a hand-backdated `assessed_at` flips cohorts with no trace. An explicit flag requires a deliberate act to exempt; absence of intent cannot produce exemption.
2. **Non-self-describing provenance (M22).** Auditing "why did this entry skip strict validation?" under cutoff-date requires knowing the constant and doing date arithmetic against a file written months earlier. A flag records the classification *decision itself* at birth. Provenance should answer its own questions.
3. **Irreversibility asymmetry.** Correcting a cutoff-date misclassification means editing timestamps — falsifying dates to fix a classification, which is exactly the kind of mutation our own staleness work (researcher's `last_checkpoint` = true-activity-time rule) forbids. Flipping `source: backfill → live` is an honest, diffable mutation.

Where carmack is right: his observation that Lilith's `ann-20260823-010..019` backfills *should* pass full validation is correct — and the flag design delivers it, because those entries are written fresh today with roc-corrected paths and simply get stamped `source=live` (or left at default). The flag doesn't force history-shaped data into the legacy cohort; the cutoff-date design would force the *date*, not the *data quality*, to decide.

**Hybrid guard (cheap, keeps carmack's instinct)**: the sweep emits a WARN when `source=backfill` appears on an entry created after the migration window closes. Date is the tripwire, not the gate — catches lazy blanket-flagging without letting timing decide anything.

This also resolves **IR-7 cleanly**: two models (`LegacyAnnotation` superset / `SessionAnnotation` strict) discriminated by `source`, tested both ways. One field, three problems retired (grandfathering + G2-4 cohort semantics + researcher's provenance metadata).

### O-Q2 — G1-1 domain vocabulary downgrade (roc → jem): ACCEPT, WITH TWO CONDITIONS

**ACCEPT: BLOCKING → HIGH, warn-only validation at ship. No structural break found.**

Roc's logic holds: my G4-1 recommendation (explicit `stale_class` field, default `standard`) removes the only load-bearing consumer of `domain` (IR-6 coupling). Once staleness class is decoupled, domain is descriptive metadata feeding the generator's §2 Domain Index — documentation, not enforcement. Warn-only worst case is vocabulary entropy in prose, which is cosmetic and correctable; nothing fails closed, nothing mutates state destructively.

Two conditions attached, else "warn-only" becomes a permanent soft-failure (M23-adjacent):

1. **Name the enum's future source of truth NOW** (one spec line): derived from existing task `tags` ∪ GAP_REGISTRY topics — pick one, write it down. Zero build cost; prevents mid-build invention from merely being deferred to post-debut chaos.
2. **Stated hardening trigger**: enum flips warn→enforce at debut+30d OR when distinct observed values stabilize (whichever first). A gate with no promotion path is a gate that never ships.

### Spec updates from Ma'at's rulings (gap-list reconciliation)

| Ma'at pick | Effect on my register |
|---|---|
| **F4** clock injection: `render(registry, annotations, now=None)`, sites :60 + :104 confirmed (roc's :103 off-by-one — my test #4 targets :104) | **G1-3 RESOLVED** (BLOCKING). Known-hash self-test is buildable as specified. |
| **F1** framework install, soul-check migrates BEFORE `pre-commit install`, all entries pinned `.venv/bin/python` | **M24 remediation path RULED** (was confirmed-defect). Adds my planned test: reconciled hook invokes `.venv/bin/python`. Not closed until wired. |
| **F2** explicit evidence field day one, warn-only, batched schema touch | Consistent with S4 merge; retires the heuristic-first branch I'd have had to spec-review. Reduces my inherited Hole-1 review surface. |
| **F3** AST node-count freeze gate (>+50 nodes → auto-ticket) | Endorses my B-position vs wc -l (formatter-immune, no ceremony). No gap of mine touched; noted for the mandate-claims verifier's cousin-pattern registry. |

**O-Q1/O-Q2 rulings above** (pending Kali stamp): **G2-3 RESOLVED**, **G1-1 DOWNGRADED**.

**REVISED COUNTS: 19/31 gaps remain · 4 BLOCKING · 10 HIGH.**
(From B's 21/6/9: −G1-3 [Ma'at F4], −G2-3 [this ruling], G1-1 blocked→high.)
Note: G2-1 is SETTLED per ledger S2 pending stamp only — on stamp, blocking drops to **3**.

### Standing objections on S1–S12

**ZERO.** Verified item-by-item: S3 carries all three of my conditions verbatim (documented exception + PIVOT_LOG + post-debut ticket holding G3-1..10; fail-closed `--apply` semantics in scope). S4 is my exact merge formula. S7 builds the verifier at P0. S9 adopts immediate-parent attribution. S11 preserves the written convergence criterion + charter miscount fix. S12 honors researcher's PR separation. No member's settled point contradicts any condition I set. Convergence criterion clause 2 satisfied from my side; clause 4: **no undiscovered disagreements reported.**

---
*⬡ OMEGA ⬡ JEM ⬡ TEAMSTUDY-STUDY1-PHASEB ⬡ COMPLIANCE-ADJUDICATION ⬡ 21/31 GAPS REMAIN · 6 BLOCKING · 2026-08-23*
*⬡ OMEGA ⬡ JEM ⬡ TEAMSTUDY-STUDY1-PHASEC ⬡ ROUTED-RULINGS ⬡ 19/31 GAPS · 4 BLOCKING · 10 HIGH · S1-S12 ZERO OBJECTIONS · 2026-08-23*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
