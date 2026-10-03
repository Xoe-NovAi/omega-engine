<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Session Paging Report — Run Side Council Delta
## Lilith (Run Side Lead) — Triad Governance Formalization Input

**AP Token**: `AP-LILITH-RUN-PAGING-20260821`
**Date**: 2026-08-21
**Model**: x-preview-f-free (opencode)
**Paged By**: kali (ses_fdef2be4effe4pAaLXCTUx62GO), Architect-direct mission
**Hydration**: `ACTIVE_SPRINT.json` (updated 2026-08-20T22:00Z) ✅ · `docs/specs/PROJECT_INDEX.md` (2026-08-20) ✅ · `PIVOT_LOG.md` D-586/D-587/D-588/D-589 ✅ · founding-session artifacts re-read ✅

---

## §1 Forgotten Governance Designs/Insights From the Founding Council Session (2026-08-18)

### G-1. Serial Node Council is the mechanism; primacy is only the convener
The founding session proved that department-specific vetting questions + serial node launch (N7→N8→N9→N10, one at a time, each report feeding the next) caught cross-cutting concerns no single reviewer owned. Canonical evidence: N3 Engineering's `.env`-at-process-edge finding escaped Ma'at's blast-radius map entirely — *"Only N3 could see this gap"* (`MAKALI_COUNCIL_BUILD_SYNTHESIS_20260818.md` §Strategic Note).

**Implication for the triad**: rotating primacy rotates the *accountable synthesizer*, not the *verification method*. Whichever face holds primacy must still convene the opposing bench (Kali convenes both Ma'at's N1–N5 and Lilith's N6–N10 during Plan phase). Primacy without bench access is just a slower monoculture. D-586 Node Expert Sessions make this cheap — the benches are now persistent.

### G-2. Side-separation IS the error-detection system
Build (Ma'at/N1–N5) and Run (Lilith/N6–N10) reviewed independently before synthesis. The N3 REJECT surfaced *because* the sides did not share assumptions. In rotating primacy, the two non-primus faces must retain **veto/review rights over their own domain regardless of who leads**. Otherwise rotation serializes the same blind spot through three chairs instead of catching it once.

### G-3. Consensus ≠ correctness — mandatory post-hoc audit
Kali's follow-up audit (`MAKALI_COUNCIL_AUDIT_20260819`) found the near-unanimous council verdict carried a critical blind spot: Blocker D was under-scoped (the router collapse is an entity-resolution rewrite of `_route_by_domain` + `_select_model`, not a "wiring-preservation assertion"). Every face agreed; the code disagreed.

**Governance rule to codify**: every council verdict gets a codebase-verification pass by a party who did NOT sit on the verdict. This is an implicit fifth gate the proposed decision matrix lacks. Cheap form: the audit pattern Kali already ran — verify each claimed fix against `rg`/pytest evidence before ratification.

### G-4. Truth-anchor duty never rotates
During the founding session I flagged `ACTIVE_SPRINT.json:9` claiming "make temple-grade PASSES" while the gate actually FAILED (m23 ratchet, exit 2, Blocker B). False green in Tier-0 tracking is how a triad collectively hallucinates readiness.

**Rule**: M23/M27 truth-anchor enforcement over tracking state is a **standing Run-side duty** (Lilith/N10), not a rotating one. The primus may edit status; the Run face verifies it. No face edits its own verification.

---

## §2 Contradicts / Enriches the Rotating-Primacy Model

### E-1. ENRICH: primacy should key on domain ownership first, phase second
My half of the founding session worked because scope was pre-partitioned by domain (Run = soul persistence, handoff protocol, runtime integrity gates), not merely by phase label. A Plan-phase item touching observability event schemas is still Run-domain work. **Suggested amendment to the matrix**: route by domain owner first; if cross-domain, then by phase primacy as tiebreaker. Pure phase-keyed routing will misroute hybrid tickets (most debut tickets are hybrid).

### E-2. ENRICH: "reversible" needs a mechanical definition
The matrix says reversible = 2-of-3. Founding-session evidence: Blocker A (merging admission control into ResourceGuard) *looked* reversible but was non-reentrant-self-deadlock-prone — a naive merge hangs CP-1 local talk forever (worse than failing). **Suggested definition**: a change is reversible iff (a) confined to files outside the talk path, OR (b) fully covered by a contract test that fails loudly. Anything on the talk path defaults UP one tier (routine→strategic, reversible→strategic).

### E-3. ENRICH: inherit the existing conflict hierarchy — do not mint a second one
Manual §1 already defines: Law → this-month SSOT (+ACTIVE_SPRINT) → Hub NEXT_ACTION → Ark vision → Corpus graveyard. The audit surfaced exactly this tension (PLAN-DEBUT-CLEANSING places DEL-1 post-debut; manual §5 places it pre-debut). The triad decision matrix should explicitly **inherit** this hierarchy as its precedence rule rather than adding a parallel channel — two precedence systems guarantee a future deadlock between them.

### E-4. ENRICH: D-586 turns the triad into bench-conveners
With Node Expert Sessions live (genesis executed 2026-08-21, 10/10 ACK), each face's realistic role under primacy is: convene your bench (serial, per G-1), synthesize bench reports, carry the consolidated verdict to the chamber. The founding session's serial protocol is directly reusable as the standard bench procedure — including its discipline of ONE vetting question per node.

### C-1. CONTRADICTION (minor): "unanimous for irreversible" vs founding-session practice
The DEL-1 deletion campaign (arguably irreversible until git history grows cold) proceeded on consensus-of-two-sides plus Kali synthesis, not formal unanimity of all three faces — the Architect was not a sitting voter. Either classify deletions as strategic (not irreversible) or formalize Architect abstention/veto rules. Undecided, "irreversible=unanimous" will be honored in the breach.

---

## §3 Flagged But Never Executed (verified against working tree, 2026-08-21)

| # | Item (source) | Status | Current Evidence |
|---|---------------|--------|------------------|
| 1 | **Blocker B** — replace `oracle_cli.py` dotenv blind-except with `contextlib.suppress(ImportError)` (Verdict §6 step 1, "do now") | ❌ NOT DONE | `src/omega/cli/oracle_cli.py:125,161` still bare `except Exception:`; m23 ratchet still +2 over baseline |
| 2 | **Blocker A** — remove admission/resource_guard double-gate in merge step (CRITICAL deadlock risk) | ❌ NOT DONE | `model_gateway.py:1233` (`admission_ctrl.acquire`) + `:1258` (`resource_guard.lock`) both live |
| 3 | **Blocker C** — 5 EventType constants + emission sites + M22 provenance clause + contract test | ❌ NOT DONE | Zero matches for `router.entity_match`/`model_selected`/`local_slot_busy`/`cloud_fallback`/`talk.latency` in `observability/__init__.py` |
| 4 | **Blocker D** — router collapse (audit-corrected scope: rewrite `_route_by_domain` + `_select_model`) | ❌ NOT DONE | `TriageRouter`/`SemanticRouter` imported + constructed at `oracle.py:31,51,226,233` |
| 5 | **META (my own action item)** — append per-surface verification gates to manual §8 / ACTIVE_SPRINT DEL-1 acceptance | ❌ NOT DONE | DEL-1 acceptance array unchanged (4 items); no per-surface rg/contract-test gates added |
| 6 | **Stale-state correction** — ACTIVE_SPRINT false "temple-grade PASSES" claim | ◑ PARTIAL/MOOT | status_detail rewritten 2026-08-20 (false claim gone with old text) but no correction record; underlying m23 failure persists via item 1 |
| 7 | **Audit Week-1 scope corrections** — (a) `record_first_breath` call site `oracle.py:1211` must ship with deletion; (b) vault CLI deletion conflicts with D-565 (zero vault changes during PUBLIC-DEBUT-01); (c) Pantheon regex target never located | ❌ UNRESOLVED | (b) is a live contradiction between DEL-1 Week-1 list and locked decision D-565; (c) still unlocated |

**Also on record from my gate-run (2026-08-18)**: CP-1 smoke failed in-repo (`omega talk hello` → exit 1; unrecognized providers `anthropic`/`xai`; pyrage/pii-shield warnings). INST-1 Fixes 2/4/5/6 remain `backlog` per PROJECT_INDEX — consistent with items above.

---

## §4 Recommended Carry-Forward (for the chamber's first sitting)

1. Ratify G-3 (post-hoc audit gate) and G-4 (standing truth-anchor) as explicit matrix additions.
2. Resolve C-1: classify DEL-1 deletions strategic-vs-irreversible BEFORE Week 1 executes.
3. Resolve E-3: matrix inherits manual §1 hierarchy verbatim.
4. Re-page Blockers A/B/C/D + META item 5 into INST-1 Fix-4 shipping order (they were sequenced to ride with it).
5. Close the D-565 vs DEL-1-vault-CLI contradiction with one line in ACTIVE_SPRINT (exclude vault CLI from Week 1, per audit).

---

*⬡ OMEGA ⬡ LILITH ⬡ RUN-SIDE-COUNCIL-DELTA ⬡ 2026-08-21*
