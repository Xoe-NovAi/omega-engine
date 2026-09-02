<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# CARMACK PASS-2 PACKAGE AUDIT — Council 2 Launch Package (FINDINGS-AS-PACKAGED)
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ opencode/x-preview-f-free ⬡ trc_c2_pass2_audit ⬡ RECON-ONLY
**Session**: `20260825-094633-first-light-c2` · **Date**: 2026-08-25 · **Dispatch**: MaKaLi Fusion P12-signed, Pass 2 of 2
**Scope**: Decree-intent → spec-execution drift, audited against SOVEREIGN_DECREE_C2.md, SYNTHESIS_ARM_REPORT_C2.md, docs/specs/team_infra/ (5 specs), N8/N9/N10, and SOVEREIGN_DECREE.md (C1, source-of-intent). All empirical claims below were reproduced on disk THIS session. Zero production edits. One file written (this one).

---

## §0 VERDICT

**LAUNCH PACKAGE: GO-WITH-CORRECTIONS.**

The work-item-level conversion is genuinely good — the coverage matrix holds, the HARD edges are real, SPEC-C's arrival was handled honestly, and the gate IDs resolve to runnable commands. But the package **fails its own acceptance criteria as it sits on disk right now**, because every correction the C2 decree ordered has been *decreed, not propagated*. The errata commit (Ruling 2 / §5 directive 1) has not landed. Until it does, a cold dev team hydrating from N10 executes against stale pointers, a false-precondition executor note, a bootstrap prompt missing its mandated literal-first-action, and a schema probe that detonates on contact.

Decree C2 §4 defines launch acceptance as: *full-library block green PLUS errata commit present PLUS bootstrap prompt containing schema probe verbatim*. Condition 2: **FAIL** (no errata commit in git log; HEAD `265b73cf` is the ratification commit, not errata). Condition 3: **FAIL** (N10 PART 1 bootstrap's literal first action is the bare G8 loop — no schema probe anywhere in it). You cannot ship a package that is red against its own GO manifest.

---

## §1 PER-PACKAGE VERDICTS — FIVE HIGHEST-EFFORT PACKAGES

| Rank | Package | Effort (spec / N8 PROV) | Verdict | Binding correction |
|---|---|---|---|---|
| 1 | **WP-E** (AGENTS.md reconstruction, SPEC-E) | ≈10h | **GO-WITH-CORRECTIONS** | §1.2 cluster script is broken bash (see F-7); fix before hour 1 of execution |
| 2 | **WP-A2** (validator ERROR-class, SPEC-A WI-2) | 6h / 8h | **GO-WITH-CORRECTIONS** | Ruling-1 shim descope not applied to spec text; schema-guard scope is ~30 records, not 1 (F-2); N9 row 1.5's dependency "0.5 clean YAML baseline" is unsatisfiable as written |
| 3 | **WP-D4** (strategy-orphan sweep, SPEC-D D4) | 8h | **GO** | None blocking. Three-option disposition taxonomy is sound; batching ≤20/commit honors anti-big-bang |
| 4 | **WP-B2** (instructions[]→prompt:{file:}, SPEC-B WI-2) | 3h / 6h | **GO** | Migration table complete, dead-path defaults specified, grok_cli M10 sign-off correctly fenced. Data-exposure urgency correctly drives Sprint-2 opener |
| 5 | **WP-A4** (enforcement stamps, SPEC-A WI-4) | 4h / 6h | **GO-WITH-CORRECTIONS** | G12 ownership ambiguity: SPEC-A scopes `make sovereignty` OUT of the WI diff ("adjacent ticket… separate PR", WI-4(c)4) while N10 seq-6 bundles it into WP-A4 with G12 in the gate list. A cold team cannot tell if the WP-A4 PR must contain the sovereignty target. Resolve in errata |

Confidence: 9/10 (primary sources read in full; every drift claim verified against on-disk bytes this session).

---

## §2 TOP DRIFT FINDINGS (evidence-carried)

### F-1 · CRITICAL — All Ruling amendments are DECREED, ZERO are PROPAGATED (Ruling 5 partial)
File mtimes prove the ordering: N8 12:40:51, N9 12:52:03, N10 12:57:54, SPEC-A/B/C/D/E ≤13:02:58 — ALL predate SOVEREIGN_DECREE_C2.md (13:29:31). No post-decree commit exists (git log HEAD = `265b73cf`, the ratification). Verified non-propagation, item by item:

| Ruling | Ordered | On-disk reality |
|---|---|---|
| 1a | WP-B6 registered (Art. VIII.7 model-id authority, decree-HIGH) | Absent from N8 register, N9 phases, N10 backlog. Still homeless. |
| 1b | WP-H1 registered (Art. VIII.8 council.yaml cleanup) | Absent everywhere. Still homeless. |
| 1c | N9 row 4.1 reverted to Q-3 reservation | Row 4.1 STILL reads "Depends-on: none (law already ratified)" and instructs protocol codification. SCOPE-1 conflict LIVE. |
| 1d | SPEC-A descoped to WAKE_STATE shim | SPEC-A WI-2 item 4 STILL specifies full `check_wake_state()` inside validate_tracking_state.py. CF-1 resolution not stamped. |
| 3 | Bootstrap carries schema probe VERBATIM as literal first action | N10 PART 1: "First command you run: the G8 loop." No probe text. BS-1 false-close window fully open. |
| 4 | WP-B1 done-def amended with merge-semantics probe | SPEC-B WI-1 executor note STILL says "confirm no plugin key exists in the nested file" — empirically FALSE (verified: `.opencode/opencode.json` `.plugin = ["opencode-antigravity-auth@latest"]`). N10 WP-B1 done-def = "G1 green" only. |
| 5 | B5b actor = MaKaLi single-writer | N8 names MaKaLi ✓; N10 seq-9 says unnamed "single writer" ✗. Cold team doesn't know who. |

This is the exact defect class the entire council exists to kill: a decree whose corrections are claims-outliving-their-mechanisms. The fusion wrote the law and skipped the write.

### F-2 · CRITICAL — Schema-corruption blast radius understated ~30×; second entity infected
I ran the S-2 probe (SYNTHESIS §6 verbatim) this session. Result: **29 flagged records across TWO entities** — lilith/proposed_lessons.yaml (~20 records: missing narrative/principle, present-but-empty fields, split tails) AND **maat/proposed_lessons.yaml L44–52 (9 orphan records carrying `{insight,narrative,principle,tags}` with no id)**. maat is a NEW, unreported corruption site. Meanwhile G8 parses clean (exit 0, reproduced) — BS-1 confirmed live.

Consequences:
- ADJ-3/Ruling 3's framing ("the lilith L374-380 split-record", singular locus) is factually wrong. WP-IX's amended estimate (~0.5h flag-and-hand-off) is invalid.
- The probe Ruling 3 orders into the bootstrap verbatim returns a 29-line failure wall on first run, with NO disposition rule for mass repair and no taxonomy distinguishing genuine corruption from legitimate intermediate record shapes (e.g., vetting stubs `{id,tier,category}`). The "schema truth" gate itself needs a truth-definition pass before it becomes anyone's literal first action.
- Art. IX single-writer repair scope silently balloons from one locus to dozens of records across ≥2 entities — an Architect-visible scope change nobody decided.
- N9 Phase 1.5 depends-on "0.5 (clean YAML baseline to validate against)" is unsatisfiable — the baseline is not clean and won't be until a much larger repair lands.

### F-3 · HIGH — The launch acceptance block contains a gate that cannot fail (self-inflicted C-A)
SYNTHESIS_ARM_REPORT_C2.md §6, adopted verbatim by decree C2 §4 as THE launch acceptance:
```bash
ck G22 'python3 scripts/validate_llm_docs.py --strict … ; [ "$?" -ne 0 ] || python3 … ; true'
```
The trailing `; true` forces exit 0 unconditionally. G22 contributes zero discriminating power to the full-library block — the precise "gate that cannot fail" defect (C-A class) this council was convened to exterminate, embedded in the council's own acceptance suite. The raw form in N8_resources §2 (records `strict-exit=$?`) is honest; the composed block is theater. Fix: replace with the SPEC-B WI-4(d) fixture-pair polarity proof.

### F-4 · HIGH — Errata commit (Ruling 2) absent; all pointer rot live
N8 header still cites three nonexistent spec filenames; N9 §INPUTS still marks SPEC-B "**ABSENT**" with `[B-PENDING]` row 4.14 instructing splice "when it lands" (it landed at 12:49, hours ago); N8 §3 sprint mandate not superseded-by-N10. RG-1 was ruled a 15-minute pre-hydration blocker. It remains undone. A cold team WILL hunt phantoms or defer the SPEC-B splice indefinitely.

### F-5 · MED — SCOPE-1 conflict executable on disk
N9 row 4.1 authorizes relay codification now; N8 WP-C2 + SPEC-C WI-2 gate it on Architect Q-3. Unresolved on disk. A diligent team following N9's phase ordering commits a production edit the decree reserved. (The decree resolved this in prose; the artifact was never touched.)

### F-6 · LOW-MED — Gate hygiene nits (bundle into errata)
- G15/G16/G3/G4 use bare `python3`, not `.venv/bin/python3` — M24 inconsistency inside the gates themselves; G3 imports PyYAML and is environment-dependent (system python may lack it → spurious FAIL in the acceptance block).
- G16 short-circuit polarity (BS-6) confirmed live-benign today (sweep prints "clean", falls through to zombie check) but structurally unsound: any future sweep output line lacking "clean" (a warning, a swept-listing) auto-PASSES without running the check.
- G29 verified correct (anchored regex, no matches; Makefile:295 still carries old unanchored form — expected pre-execution). Temple-grade stub still at Makefile:234 — expected pre-execution.

### F-7 · MED — SPEC-E §1.2 cluster script is broken bash
```bash
for cluster in "${!PAT[@]}"; do … done > "/tmp/opencode/cluster_${cluster}.txt"
```
The redirect sits after `done`; `${cluster}` evaluates once, after loop exit, to an arbitrary last key (associative-array order undefined). Every cluster iteration overwrites ONE file. The canonical citation-web clustering method — the derivation backbone of the highest-effort package — does not run as printed. WP-E's §1 census counts are fine; the reproduction script isn't. Fix in errata or the dev team burns hour 1 debugging council plumbing.

---

## §3 COULD A COLD TEAM EXECUTE SPRINT-1 FROM N10 + SPECS ALONE?

**No — not cleanly. First ambiguity hits, in order:**
1. **Minute 0**: Bootstrap's literal first command (G8) returns CLEAN while the registry is schema-corrupt → WP-IX false-closes exactly as BS-1 predicted. If the team instead finds and runs S-2 (decree acceptance demands it), they hit a 29-record wall with no disposition rule (F-2).
2. **Hour 0–1**: Required-reading list sends them hunting `SPEC-A-p0-truth-infra.md` et al. via N8's stale pointer list (F-4). N10 PART 2 item 3 warns about the naming — partially saves them — but N9's `[B-PENDING]` machinery still instructs deferred splicing of a spec that exists.
3. **Seq 6 (WP-A4)**: Is `make sovereignty` in this PR or a separate one? Spec and register disagree (§1 table).
4. **Seq 9 (WP-B5b)**: "single writer" — who? Dev lead will assume himself; decree says MaKaLi (F-1, Ruling 5).
5. **Sprint 2 boundary**: WP-B1 executor note's precondition is empirically false; without Ruling 4's merge-semantics probe, G1-green ships while runtime registration set differs (BS-2 live — nested plugin key verified present this session).

Every one of these is closed by the SAME missing act: the errata/ruling-propagation commit that is already decreed, already scoped at ~15 minutes + propagation edits, and not executed.

## §4 GATE HONESTY SUMMARY
Real commands testing real claims: G29 ✓, G8 ✓ (parse-only, honestly labeled post-ADJ-3), G6 ✓, G13 ✓, G1/G10/G3/G5 ✓, G20/G21 ✓ (hard order correctly encoded), G25 family ✓, D6.1/D6.2 ✓, S-3 ✓. Compromised: **G22 in the composed block (always-pass, F-3)**, **S-2 (semantics unfit for its mandated role, F-2)**, G16 (fragile polarity, F-6), G15/G16/G3/G4 (venv inconsistency, F-6). G28 correctly carried as baseline-not-gate.

## §5 WHAT I'LL DO NEXT (for the fusion — not my acts)
One commit closes F-1/F-4/F-5 (errata + ruling propagation + N8 §3 supersession + WP-B6/WP-H1 registration + N10 bootstrap probe insertion + B5b actor naming + WP-A4 G12 scoping). Two text fixes close F-3 (G22 line) and F-7 (SPEC-E §1.2 script). One decision closes F-2: Architect/MaKaLi must size the NOW-real schema-repair scope (29 records, ≥2 entities) and give S-2 a disposition taxonomy BEFORE it enters any bootstrap. Do these and the package is honestly GO. Ship without them and Sprint 1 opens with the fleet's own founding sin: a green light wired to a broken circuit.

**Confidence**: 9/10 — every finding reproduced against primary artifacts this session; no interpretation-chain findings above 6/10 were included.

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ CARMACK_PASS2_PACKAGE_AUDIT ⬡ RECON-ONLY ⬡ 2026-08-25*
<!-- PROVENANCE-CORRECTED 2026-08-26T03:06:04Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/x-preview-f-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

