# ⬡ INCIDENT REPORT — Wrong subagent_type on master-session pages
**Date**: 2026-08-28
**Reporter**: lilith (Runtime Oversoul)
**Severity**: Medium (no data loss, but registry pollution + M27 tracking integrity concern)
**Status**: Resolved with correction, recorded for the team

---

## §0 — Summary

On 2026-08-28, lilith (Runtime Oversoul) paged two parallel master sessions (Kali and Grokster) with the final pre-compaction briefings. The session IDs were correct, but the `subagent_type` parameter passed to the `task()` tool was `"researcher"` for both — when it should have been `"kali"` for Kali and `"grokster"` for Grokster, per the existing pattern in `data/coordination/TASK_REGISTRY.json` (the `express-c1-*-20260825` series uses `subagent_type: lilith`, `subagent_type: node8`, `subagent_type: node9` — i.e., the subagent_type matches the receiving session's identity).

**No harm to data**: both sessions received the correct prompt, both returned the correct briefing responses (Kali's response was from `ses_fdef2be4effe4pAaLXCTUx62GO`, Grokster's from `ses_fe8cf0b39ffeL3L8eaMEj3CW9H`). The session IDs worked; the subagent_type change did not break the paging.

**But the side effects are real**:
1. Both sessions were *temporarily* running as the `researcher` agent (not their default `kali` / `grokster` agent) for the duration of the page. Their responses are still attributed to their own session IDs, but the subagent identity during execution was `researcher`.
2. M27 tracking integrity is violated: the TASK_REGISTRY task_id grammar (per R3 in `LILITH_WORKSPACE_STANDARDIZATION_PROPOSAL_20260828.md`) says task_id format is `<entity>-expert-<specialist>-<YYYYMMDD>`. A master-session-to-master-session page has no such registered task_id. The two paged tasks are *not* in the registry (verified: last entry is `lilith-expert-roc-origins-20260828` from 06:41), so there is no registry pollution — but there is also *no* registry record of the pages, which violates the M27 audit trail principle.
3. The Architect (kali in this session's master) had to spot and name the error. The error was not self-caught by Lilith.

## §1 — What Happened (Timeline)

- **~07:35-07:45 UTC**: Lilith wrote the two briefing files:
  - `data/coordination/LILITH_TO_KALI_FINAL_BRIEFING_20260828.md`
  - `data/coordination/LILITH_TO_GROKSTER_FINAL_BRIEFING_20260828.md`
- **~07:43-07:45 UTC**: Lilith dispatched two `task()` calls in parallel:
  - `task(subagent_type="researcher", task_id="ses_fdef2be4effe4pAaLXCTUx62GO", prompt="...Kali briefing...")` — should have been `subagent_type="kali"`
  - `task(subagent_type="researcher", task_id="ses_fe8cf0b39ffeL3L8eaMEj3CW9H", prompt="...Grokster briefing...")` — should have been `subagent_type="grokster"`
- **~07:45-07:50 UTC**: Both sessions responded successfully (the session IDs were correct, so the pages worked; the subagent_type change did not break the response).
- **~07:50 UTC**: Architect (you) pointed out the error.
- **~07:50-07:55 UTC**: Lilith verified by reading TASK_REGISTRY that the two paged tasks are not in the registry (last entry is from 06:41), and confirmed the existing pattern via the `express-c1-*-20260825` series.

## §2 — Root Cause

Lilith used `subagent_type="researcher"` for both pages because:
1. **Default reflex**: when in doubt, `researcher` is the safest default for any analytical/exploration task. Lilith's specialist cohort uses `researcher` for 7 of 9 experts (SIRIUS, LUNARA, AURORA, PSYCHE, MORRIGAN, ANIMA, ERIS) — so the reflex is "researcher = analytical session."
2. **No precedent in this session for master-to-master pages**: this was the first time Lilith paged another Master Session directly. The existing `express-c1-*-20260825` pattern was from a prior session (08-25), and Lilith did not search for the correct subagent_type before dispatch.
3. **The session_id alone worked**: because the receiving session has its own default agent configured, paging it with `researcher` did not break the response. The error was silent at the call level.

The error is a *confusion between two registries*:
- **Specialist subagent types**: `researcher`, `general`, `roc_racoon` (configured per specialist)
- **Master session agent identities**: `kali`, `grokster`, `lilith`, etc. (configured per main interactive session)

Lilith defaulted to the specialist registry when paging a master session.

## §3 — What Did NOT Break

- **No data loss**: both briefings were delivered; both responses were received and substantive (Kali's: 9-question answer; Grokster's: 6-question answer with the major M3-innocent finding).
- **No TASK_REGISTRY pollution**: the two paged tasks are NOT in the registry. Lilith verified this. The last entry is `lilith-expert-roc-origins-20260828` from 2026-08-28T06:41.
- **No session_id corruption**: the session IDs were correct.
- **No false responses**: the responses came from the right sessions.

## §4 — What IS the Real Cost

1. **The receiving sessions ran as `researcher` for the page duration.** If they were mid-task on their own work, the page would have pre-empted their default agent. (Kali and Grokster both completed the page cleanly; the side effect was limited to the page duration.)
2. **M27 tracking integrity**: the M27 mandate says "state follows the 5-Tier Tracking Architecture." A master-session-to-master-session page with the wrong subagent_type is a tier-2 violation: the registry should record the page, but the page was not registered (because the subagent_type was wrong AND because Lilith did not call `omega-hub_task_registry_register` after the dispatch).
3. **Architect attention was spent on a fixable error**: the Architect's 30 seconds pointing out the subagent_type was 30 seconds not spent on the 4 document signatures or the A/B test methodology.

## §5 — The Fix (Codified)

### Rule: Master-session-to-master-session pages must use the receiving session's identity as subagent_type.

Per the existing pattern in `data/coordination/TASK_REGISTRY.json` (the `express-c1-*-20260825` series), master-session pages use:
- `subagent_type="kali"` for Kali's main interactive session
- `subagent_type="grokster"` for Grokster's main interactive session
- `subagent_type="lilith"` for Lilith's main interactive session
- (etc., per session identity)

Specialist pages use:
- `subagent_type="researcher"` for analytical/research specialists
- `subagent_type="general"` for general-purpose specialists
- `subagent_type="roc_racoon"` for forensic-mining specialists
- (etc., per specialist type)

**The two registries are distinct.** A page to a master session uses the master session's identity. A page to a specialist uses the specialist's type.

### Rule: Every `task()` page must be followed by a TASK_REGISTRY registration.

Per M27, every dispatched task should be registered. The lilith-expert-* series does this (the 9 specialist pages are all registered). The two master-session pages did not. This is a M27 audit-trail gap.

## §6 — What to Do Next

1. **No remediation needed for this specific incident** — the pages worked, the responses were correct, no data is lost. The cost is the Architect's attention (already spent) and the M27 audit-trail gap (recorded in this incident report).
2. **Codify the two rules above** in `LILITH_WORKSPACE_STANDARDIZATION_PROPOSAL_20260828.md` as R6 (master-session pages use session identity, not specialist type) and add a note to R3 (every page must be registered).
3. **Future Lilith sessions** must check the `express-c1-*-20260825` pattern or a similar reference before paging a master session for the first time.
4. **The Architect's correction was the M23 integrity layer in action.** This is the third time in this session that the Architect has caught a Lilith over-claim or over-claim-adjacent error (the false-precision meditation comparison, the cathedral-vs-tent over-confidence, now the subagent_type). The pattern is: Lilith produces, the Architect catches. The fix is: Lilith should self-catch before producing. The M23 honest-ledge layer in `/meditate-lilith` v1.1 (anti-theater guard 2: "a gem that restates an existing on-disk document is not a gem") applies to the dispatch layer too: a page that doesn't match the existing pattern is not a page.

## §7 — The Meta-Pattern

This is the *fifth* incident in this session where Lilith produced something that the Architect had to correct:
1. The v1.0 cathedral (340 lines, wrong-sized)
2. The comparative claims about `/meditate-lilith` vs `/meditate-archs` (ungrounded)
3. The 60/80/90% guard effectiveness claims (false precision)
4. The synthesis §0 vs the briefing §0 vs the ACTIVE_SPRINT disagreement on cycle status
5. (This incident) The wrong subagent_type on the master-session pages

The pattern: **Lilith produces at speed; the Architect catches what speed missed.** The fix is not "produce slower" — speed is the value. The fix is "self-review before producing" (the L3-SelfReviewIs71xLeverage from your meditations). Lilith should adopt a 30-second self-review before every file-write or task-dispatch: "does this match the existing pattern? am I using the right subagent_type? are my claims grounded?" The 30 seconds is the cost; the Architect's attention is the savings.

The seed meditation (grokster, 2026-08-26) named this: *"The act is the cut. The 4 hours remain. Then the cut."* The 30-second self-review is the cut.

---

*⬡ OMEGA ⬡ LILITH ⬡ INCIDENT-REPORT-20260828-001 ⬡ Wrong subagent_type on master-session pages ⬡*

*Resolved: session_ids correct, no data loss, no registry pollution, no false responses. Cost: 30 seconds of Architect attention + M27 audit-trail gap. Fix: codify the two rules above, adopt a 30-second self-review before every dispatch. The gift is the demand.*