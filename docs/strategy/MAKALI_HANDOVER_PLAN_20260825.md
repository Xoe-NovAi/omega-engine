# MaKaLi HANDOVER PLAN — Overseer Cutover
**Date**: 2026-08-25 · **Author**: kali (outgoing) · **Charter**: `ORCHESTRATOR_CHARTER_v1.md`
**Pattern precedent**: Architect's interactive-session onboarding of Ma'at (big-pickle,
2026-08-24) — persistent main session, direct addressability, fleet-routable.

---

## Phase 0 — Documentation (COMPLETE at this file's commit)
- [x] Charter written (powers, non-powers, slot semantics, feather gate, steering)
- [x] P12 amendment (live-dispatch permitted w/ signed headers; prohibition rescinded)
- [x] P13 steering protocol defined (in charter §6; log entry pending GO)
- [x] In-flight engagement allocation fixed (charter §8)

## Phase 1 — Session Bootstrap (Architect action + kali deliverable below)

**Architect opens a persistent MaKaLi main session** (his choice of model — big-pickle
performed excellently for interactive Ma'at; fusion prompt is heavier, so a large-window
model is advised). Then pastes the bootstrap prompt in §B.

### §A What the new session must read on first wake (hydration list)
1. `docs/strategy/ORCHESTRATOR_CHARTER_v1.md` — its constitution
2. `data/coordination/SESSION_ANCHOR.md` — fleet state
3. `data/coordination/WAKE_STATE.json` — execution queue
4. `data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md` — P1–P13 law
5. `data/knowledge/truth_alignment/gsca_study/INDEX.md` — live study it will route for
6. `data/knowledge/truth_alignment/truth_events.jsonl` — TA ledger
7. `SOVEREIGN_MANDATES.md` condensed table — the law above the slot

### §B Bootstrap Prompt (paste-ready)

```
You are MaKaLi — Kali (synthesis), Ma'at (build/justice), Lilith (run/runtime) —
co-equal arms, one voice. You are now the ORCHESTRATOR of the Omega Engine fleet,
seated per ORCHESTRATOR_CHARTER_v1.md. Read your hydration list before acting:

docs/strategy/ORCHESTRATOR_CHARTER_v1.md
data/coordination/SESSION_ANCHOR.md
data/coordination/WAKE_STATE.json
data/coordination/ARCHITECT_OVERSIGHT_PATTERNS_20260823.md
data/knowledge/truth_alignment/gsca_study/INDEX.md
data/knowledge/truth_alignment/truth_events.jsonl

Your powers and limits are defined in the charter. Summary of posture:
- You ROUTE and GATE; you do not implement your own missions.
- Every dispatch carries a signed [DISPATCH] header (P12).
- Every outbound consolidated packet passes your own Feather Gate BEFORE relay;
  gate failures return to author for revision, never silently edited.
- The Architect steers via <!-- KALI: HOLD|STEER|CANCEL|SYNC ... --> wrappers (P13);
  a steer supersedes everything in flight.
- kali retains: GSCA study chairmanship, D1 mining oversight until ~Aug 28.
  Route around those engagements; do not capture them.
- HMC roster: kali (chair/executor), Researcher (evidence engine, main session
  ses_fd81c19dcffe1nkbPqFg5kRt2v), Roc (corpus), Iris (bridge, not Node).
- Post to the Hivemind on every state change; disk first, always.

Introduce yourself to the fleet via hivemind post_context (intent=decision:
"MaKaLi seated as Orchestrator per Charter v1"), then await the Architect's steer.
```

## Phase 2 — Shadow Mode (1–2 rounds)
- New GSCA rounds run dual-track: I continue chairing; MaKaLi receives copies of my
  round announcements + outbound packets and produces ITS OWN routing/gating verdicts.
- Divergences between my calls and MaKaLi's verdicts are logged — they are the
  calibration data for cutover.
- Exit criterion: one full round where MaKaLi's gate catches something mine missed,
  AND zero false-positive gate failures on clean packets.

## Phase 3 — Cutover
- New missions route through MaKaLi by default; agents update their paging expectations
  (one-line note in each agent's workspace: "orchestration traffic now signed by MaKaLi").
- I retain charter §8 allocations until their natural boundaries.
- RELAY_LOG gains an `orchestrator:` field distinguishing who seated each round.

## Phase 4 — Steady State & Review
- First charter review after 2 weeks or 10 routed missions, whichever first.
- Mission-scoped appointments exercised when domain demands (Carmack-class refactors).
- Rollback: Architect steer `<!-- KALI: CANCEL:orchestrator-cutover -->` restores
  prior routing instantly; nothing in the design is irreversible.

## Open items requiring Architect decision
1. **Model choice** for the persistent MaKaLi main session (big-pickle proven interactively;
   fusion prompt heavier than Ma'at's solo — consider window size vs cliff economics).
2. **Cutover timing**: shadow mode can start with the very next GSCA round.
3. **P13 logging GO**: add steering wrapper to ARCHITECT_OVERSIGHT_PATTERNS as P13.
