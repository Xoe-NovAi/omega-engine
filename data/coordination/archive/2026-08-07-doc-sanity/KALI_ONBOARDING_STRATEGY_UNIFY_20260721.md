<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KALI ONBOARDING — Strategy Unify Review Request
**AP Token**: `AP-KALI-ONBOARD-v1.0.0`  
⬡ OMEGA ⬡ GROK_CLI → KALI ⬡ opencode ⬡ trc_onboarding ⬡ REVIEW-REQUEST

**Date**: 2026-07-21  
**From**: `@grok_cli` (Consulting Cloud Mind) on Architect direction  
**To**: `@kali` (Transcendent Oversoul / Sprint Coordinator)  
**Priority**: **1 (high)**  
**Intent**: Hydrate Kali on the post-recalibration strategy SSOT work, then **return a formal feedback verdict** to Grok CLI + Architect.

---

## §0 Why You Are Being Onboarded

After your strategy recalibration (Researcher 12-gap audit, Roc legacy mining, Grokster adversarial review → `CANONICAL_ROADMAP_20260721.md`), the Architect asked Grok CLI for:

1. Full codebase + strategy review (handoff `ho_d3d37d521c3f` — completed)  
2. Unite all strategy/roadmaps **without losing fine-grained agent work**  
3. Recommendations for PR-ready path  
4. A **fleet team playbook** so all agents move as one  

**Critical correction from Architect:**  
`SOVEREIGN_ARK_BLUEPRINT.md` was always supposed to be strategy SSOT. The 2026-07-21 archive pass demoted it in favor of CANONICAL_ROADMAP. **Grok CLI restored the Ark as v5.1** and absorbed the tactical recalibration.

Your job now: **review this unification as Sprint Lead** and say what holds, what to reject, and what the fleet executes next.

---

## §1 Cold-Start Sequence (Do This First)

```text
1. hivemind_get_awareness()
2. hivemind_handoff — accept this packet (see handoff id in live feed / pending/)
3. Read THIS file fully
4. Read the Mandatory Reading stack (§2) in order
5. Write feedback to path in §5
6. hivemind_handoff complete + post_context intent=handoff
7. Optionally update SESSION_ANCHOR with your next sprint claims
```

**Do not** start implementing C-0/C-1′ until you have posted the feedback verdict (unless Architect overrides). Review first — you own the roadmap.

---

## §2 Mandatory Reading (Ordered)

| # | Document | Why | Time |
|---|----------|-----|------|
| 1 | **This onboarding** | Scope of review | 5 min |
| 2 | `docs/strategy/FLEET_TEAM_PLAYBOOK.md` | How fleet should work; your role as Sprint Lead | 10 min |
| 3 | `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` **v5.1** | Strategy SSOT + Phase C–F + gap crosswalk | 15–20 min |
| 4 | `docs/strategy/STRATEGY_CORPUS_MAP.md` | Proof fine-grained work was not deleted | 10 min |
| 5 | `docs/strategy/STRATEGY_INDEX.md` | Hierarchy / conflict resolution | 3 min |
| 6 | `data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md` | Structural blockers Grok CLI raised | 10 min |
| 7 | `data/coordination/SESSION_ANCHOR.md` | Current recovery state | 2 min |
| 8 | `OMEGA_ENGINE.md` §2 + §4 | State SSOT pointers (may still lag metrics) | 5 min |

### Optional depth (if you need to challenge a claim)

| Doc | When |
|-----|------|
| `docs/strategy/CANONICAL_ROADMAP_20260721.md` | Compare what you wrote vs what was absorbed (has SUPERSEDED banner) |
| `docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md` header amendments | Confirm D-shape amendments match your intent |
| Your prior audits still Layer 2 | `UNKNOWN_UNKNOWNS_*`, `GROKSTER_ADVERSARIAL_*`, `ROC_LEGACY_*` |
| Ark v4.4 archive | `docs/archive/strategy/2026-07-21/SOVEREIGN_ARK_BLUEPRINT_CANONICAL.md` — long-arc only |

---

## §3 What Changed Since Your Recalibration (Delta)

### 3.1 SSOT identity

| Before (your session end) | After (Grok CLI + Architect) |
|---------------------------|------------------------------|
| `CANONICAL_ROADMAP_20260721.md` = strategy master | **SUPERSEDED** — trail only |
| Ark archived under `docs/archive/strategy/2026-07-21/` | **Restored** `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` **v5.1** as strategy SSOT |
| Competing pointers in OMEGA_ENGINE / docs/ROADMAP | Point at Ark again |

**Decision to ratify or reject:** D-354′ — Ark is strategy SSOT again.

### 3.2 Structural upgrades to your Phase C (from Grok CLI review)

| Your ticket | Grok CLI change | Rationale |
|-------------|-----------------|-----------|
| C-1 flock-only | **C-1′ SoulStore** (4–6h) | Four writers, not one missing flock |
| C-6 port pybreaker | **C-6′ unify/delete breakers** | Gateway already has HealthMonitor CB |
| — | **C-0** test honesty P0 | 1572 collected ≠ green; sample 832p/5f |
| — | **C-9** GenerationPolicy | Gemma hacks in ModelGateway.generate |
| — | **C-10** local admission | GAP-05 L3 thrashing |
| Phase D anytime | Gate = **C-0 + C-1′** | Integrity before research loop |
| Grok fleet wire now | **D-360′** vault → smoke → pool | GAP-08 credential void |

### 3.3 New control documents

| Doc | Role |
|-----|------|
| `STRATEGY_CORPUS_MAP.md` | Every agent idea → ACTIVE/DEFERRED/PARKED/ARCHIVE |
| `FLEET_TEAM_PLAYBOOK.md` | Team compact, roles, freezes, handoff DoD, first actions |

### 3.4 What was explicitly preserved (not cancelled)

- GAP-01…12 full crosswalk (Ark §3.0.1 + Corpus §2)  
- Researcher SQLite/VerificationGate → deferred, not deleted  
- Identity Fluidity E-0…E-5 + Grokster workspace paths  
- Ark v4.4 Strikes / Dimension / Free-Will / D-290…308 parked  
- Roc Cerebras/Groq matrix held (D-351) but documented  

---

## §4 Your Review Mission (Required Outputs)

Produce a single feedback document:

**Path:** `data/coordination/KALI_FEEDBACK_STRATEGY_UNIFY_20260721.md`

### Required sections in your feedback

#### A) Verdict (pick one)
- `APPROVE as-is`  
- `APPROVE with amendments` (list them)  
- `REJECT key parts` (list + replacement)

#### B) SSOT
- Confirm or reject: Ark v5.1 as sole strategy priority SSOT  
- Confirm or reject: CANONICAL_ROADMAP superseded  
- Confirm or reject: Corpus Map as mandatory fine-grained companion  

#### C) Phase C ticket list
For each of C-0, C-1′, C-2′, C-3, C-4a/b, C-5, C-6′, C-7, C-8, C-9, C-10:
- Keep / rewrite / drop / renumber  
- Effort sanity  
- Owner suggestion (entity)

#### D) Gate to Phase D
- Accept hard gate C-0+C-1′?  
- Any additional gate items?

#### E) Fleet Team Playbook
- Usable for fleet?  
- Missing roles / wrong ownership?  
- First actions (§11) — will you run the claim board?

#### F) Immediate sprint claims
Publish who owns what **this week**:

| Ticket | Owner | Status |
|--------|-------|--------|
| C-0 | ? | claimed / open |
| C-1′ | ? | … |
| … | | |

#### G) Questions / blockers for Architect
- Privacy model for C-3 (your recommendation)  
- MCP buffer before July 26 — realistic?  
- Anything Grok CLI over-corrected?

#### H) Continuation
- Next handoff you will submit (to whom, which ticket)

---

## §5 Coordination Protocol for This Review

| Step | Who | Action |
|------|-----|--------|
| 1 | Grok CLI | Submit handoff → kali (this onboard) |
| 2 | Kali | Accept handoff; lock if editing strategy docs |
| 3 | Kali | Write `KALI_FEEDBACK_STRATEGY_UNIFY_20260721.md` |
| 4 | Kali | Complete handoff with path + verdict one-liner |
| 5 | Kali | `post_context` intent=handoff; append `KALI_LIVE_FEED.md` |
| 6 | Grok CLI | Read feedback; apply approved Ark/Playbook amendments if any |
| 7 | Kali | Open fleet claims (Playbook §11) and dispatch C-0 / C-1′ |

**Return handoff (optional but preferred):**  
After feedback is written, you may submit handoff  
`target=opencode/grok_cli` task=`Apply Kali amendments to Ark/Playbook`  
with the feedback path in context.

---

## §6 Constraints (Do Not Drift)

While reviewing:

- Do **not** invent a third roadmap document  
- Do **not** re-archive the Ark  
- Do **not** start Phase D implementation in this review pass  
- Do **not** authorize Grok fleet wiring without addressing V-1/GAP-08  
- Edits to Ark/Playbook: either (a) list amendments for Grok CLI to apply, or (b) apply yourself and note in feedback  

---

## §7 Snapshot: Recommended Next Execution (Grok CLI view — challenge freely)

```text
C-0 tests → C-1′ SoulStore → C-2′ + C-5/C-10 → C-3 privacy/restic
→ C-4a MCP audit → PR-1 foundation slices
→ only then D-1 / E-0
```

PR-shaped: Playbook §5.3 (PR-1a…1e).

---

## §8 File Index (Absolute-ish paths from repo root)

```text
docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md
docs/strategy/STRATEGY_CORPUS_MAP.md
docs/strategy/FLEET_TEAM_PLAYBOOK.md
docs/strategy/STRATEGY_INDEX.md
docs/strategy/CANONICAL_ROADMAP_20260721.md          # SUPERSEDED
docs/strategy/LIVING_RESEARCH_OS_SPEC_20260721.md   # amended header
data/coordination/GROK_CLI_CODEBASE_STRATEGY_REVIEW_20260721.md
data/coordination/KALI_ONBOARDING_STRATEGY_UNIFY_20260721.md  # THIS FILE
data/coordination/KALI_FEEDBACK_STRATEGY_UNIFY_20260721.md    # YOU WRITE THIS
data/coordination/SESSION_ANCHOR.md
AGENTS.md
OMEGA_ENGINE.md
```

---

## §9 Message from Grok CLI to Kali

You ran a strong recalibration under pressure. The structural review was not a rejection of that work — it was a demand that **C-1 and C-6 be the right shape**, and that **the Ark not lose its throne** to a one-day tactical doc.

I need your Sprint Lead stamp (or red pen) so the fleet can execute without two coordinators. Read hard. Amend freely. Then claim the board.

⬡ GROK_CLI → KALI ⬡ AWAITING YOUR VERDICT

---

*Onboarding prepared 2026-07-21 for handoff opencode/grok_cli → opencode/kali*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
