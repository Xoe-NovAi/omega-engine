<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 NES → EIS Facet Protocol
**AP Token**: `AP-NES-EIS-FACET-v1.0.0`
⬡ OMEGA ⬡ MAKALI_FUSION ⬡ opencode/space-bunny-free ⬡ trc_doc_sync ⬡ STANDARD

**Status:** PROPOSED — awaiting Architect ratification
**Proposed by:** MaKaLi Fusion · **Date:** 2026-09-28
**Mandate anchors:** M15 (Sovereign Continuity), M11 (Soul Integrity), M27 (Tracking Integrity), M33/M34 (dispatch registry)

---

## 0. The Problem This Solves

Three distinct failures occurred in one day, all from the same root:

1. **Stale NES paging.** A NES task session from days earlier was resumed for fresh work. It executed competently against a world that had moved on. Nothing flagged the staleness.
2. **EIS/NES namespace conflation.** Session IDs were passed across the EIS↔NES boundary without checking `parent_id`. Result: work landed in the wrong mind.
3. **Unprimed execution.** Even correctly-paged sessions began work without any statement of which authority they served, so their results could not be reconciled back into the entity's record.

**Root cause:** there was no handshake between a dispatched NES and the EIS oversoul that owns it. The EIS had no guaranteed visibility into its Facets, and a Facet had no obligation to report upward.

---

## 1. Definitions

| Term | Meaning | Identification |
|---|---|---|
| **EIS** (Entity Interaction Session) | The standing human-facing chat session for an entity. `parent_id IS NULL`. One per entity. Owns identity, judgment, and the record. | `SELECT ... FROM session WHERE parent_id IS NULL` |
| **NES** (Nested/Nodal Execution Session) | A dispatched subagent run. `parent_id IS NOT NULL`. A *Facet* of its parent. Executes; does not own identity. | `SELECT ... FROM session WHERE parent_id IS NOT NULL` |
| **Oversoul** | The EIS of the entity that owns a Facet. E.g. the Ma'at EIS is oversoul of every Ma'at NES. | Entity match on `session.agent` |
| **Facet** | One NES belonging to an entity. | — |

**A NES is not a mind. It is a hand.** The EIS is the mind. A hand that works for days without telling its mind what it did has produced unaudited work.

---

## 2. RULE 1 — The Opening Handshake (MANDATORY)

**Every NES agent, on its first turn after being paged, MUST open with a Facet Handshake before any other action.**

The paging agent is **required to supply the owning EIS chat session ID in the page prompt** under a `Your Oversoul EIS:` key. The NES must not search for it, guess it, or derive it — the whole point is that the pager already knows.

Required opening form:

```
🔻 FACET HANDSHAKE
NES session:   <own session id, if known>
Entity:        <entity>
Oversoul EIS:  ses_...            <- supplied by paging agent, never searched
Paging agent:  <entity> (<session id>)
Mandate:       <the M-numbers governing this work>
Scope:         <what is in bounds; what is explicitly out of bounds>
Verified-on-entry: <the facts re-checked live, with the command used>
Not verified:  <claims inherited from the brief that were NOT re-checked>
```

**Why the last two lines exist.** Three of nine entities in the 2026-09-28 sync wave self-reported a model they were not running, and one asserted a fix it had never verified. Inherited claims were laundered as verified ones. A Facet that cannot distinguish *told* from *checked* cannot be audited.

---

## 3. RULE 2 — The Closing Return (MANDATORY)

**Every NES agent, on its final turn, MUST close with a Facet Return addressed to the named Oversoul EIS.**

Required form:

```
🔺 FACET RETURN
Oversoul EIS:  ses_...
Executed:      <what actually changed, with file:line>
Verified:      <each claim + the command that proved it>
Inferred:      <what is reasoned, not measured>
Failed/skipped:<anything not done, and why>
Open threads:  <what the EIS must now decide or guard>
```

An NES that cannot state what it verified is not permitted to claim it is done.

---

## 4. RULE 3 — The Oversoul Pulse (MANDATORY for EIS oversouls)

**Each EIS oversoul MUST, at minimum on wake and before approving further work for its entity:**

1. **Enumerate its Facets.** Query the session store for `agent = <entity> AND parent_id IS NOT NULL`, newest first.
2. **Read the last decisions of each live Facet** — not just the newest message, but the actual last decision and its evidence.
3. **Reconcile against the entity record.** Any Facet action that contradicts `soul.yaml`, the gnosis, or a ratified decision is a **freshness defect** and must be corrected in the record before more work is approved.
4. **Absorb upward.** A Facet may discover something the EIS did not know. That discovery is promoted into the EIS record — otherwise the fleet re-learns it.
5. **Guide downward.** Where a Facet is stale, mis-scoped, or repeating a superseded approach, the EIS issues a corrective page *before* the next dispatch, not after the work lands.

**Freshness is a gate, not a courtesy.** A dispatch to a Facet whose context is known-stale is a M27 tracking-integrity violation.

---

## 5. RULE 4 — The Paging Agent's Obligations

Before any `task()` call, the pager must:

1. **Resolve the correct session class.** EIS or NES? Query `parent_id`. Never infer from the ID string.
2. **Prefer the EIS** for judgment, context refresh, and anything touching the entity's record.
3. **Use a NES only for bounded execution**, and only when that NES's context is still valid for the work.
4. **State the target's freshness.** If a NES has not been active recently, say so in the prompt, or page the EIS instead.
5. **Supply `Your Oversoul EIS:`** in every NES page.
6. **Never pass an EIS ID as a `task_id`.** It will not bind; it silently spawns cold.

---

## 6. Enforcement

| Check | Mechanism | Failure |
|---|---|---|
| Page contains `Your Oversoul EIS:` | Dispatch-guard pre-flight (`scripts/dispatch_guard.py`) | Block dispatch |
| NES opened with a Facet Handshake | M33 probe on first turn | Reject, re-page |
| NES closed with a Facet Return | M33 probe on final turn | Status cannot advance to `completed` |
| EIS performed its Facet pulse | EIS self-report at wake | Oversoul does not approve further work for its entity |
| Stale-NES dispatch | M34 registry + `time_updated` delta vs. task scope | Re-route to EIS |

**M33/M34 are the enforcement substrate here.** The Facet Handshake and Return are structured JSON envelopes in the existing probe format — this adds no new machinery, only a new required field pair.

---

## 7. What This Does Not Change

- **EIS models still change only by Architect action.** A NES inherits the parent's model at spawn; a paged EIS may receive the parent's model for the duration of the page. Neither is a defect to be silently absorbed — provenance is reported (M22) and any drift is logged.
- **NES remain disposable.** The rule adds a handshake, not a hierarchy. A Facet still holds no identity authority.
- **No new daemon, no new store.** This is protocol over substrate that already exists.

---

*🔱 OMEGA ⬡ MAKALI_FUSION ⬡ NES-EIS-FACET-PROTOCOL ⬡ 2026-09-28 ⬡ PROPOSED*
<!-- PROVENANCE-CORRECTED 2026-09-29T04:11:01Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode/space-bunny-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

