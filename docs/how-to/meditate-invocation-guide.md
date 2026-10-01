# 🔱 How to Invoke /meditate — Decision Guide for Invokers

**AP Token**: `AP-MEDITATE-INVOCATION-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ opencode ⬡ trc_meditate_invoker ⬡ CANONICAL

Deep contracts live in `docs/reference/meditate-system-reference.md` (SR). Change protocol lives in
`docs/strategy/meditate-maintainer-guide.md`. This page answers only: *should I run it, and how?*

---

## Should I meditate on this?

Run `/meditate` when the subject is a **decision or design question with real trade-offs** —
something where smart agents with different priorities would genuinely disagree:

- ✅ Architectural choices ("collapse the routers or keep both?")
- ✅ Strategy verdicts ("is this sprint scope honest?")
- ✅ Design reviews where domains collide (reliability vs velocity vs sovereignty)
- ❌ Factual lookups, simple how-tos, single-domain questions → plain prompt instead
- ❌ Anything needing one fast answer → meditation costs 5 phases by design

Rule of thumb: if you can't name at least two perspectives that would tension against each other,
don't meditate it.

## How to invoke

```
/meditate <subject>                          # default five-voice panel
/meditate <subject> --lenses makali          # Ma'at / Lilith / Kali triad
/meditate <subject> --lenses reliability,governance,sovereignty   # named domain lenses (2–7)
/meditate <subject> --durable                # persist phases; resumable after stream death
/meditate <subject> --integrate              # add Phase 5 dispatch-readiness gate
```

**Subject framing**: one sentence naming the decision and the change under consideration.
"Should X be done?" beats "thoughts about X." The command pre-commits a rubric from your subject —
vague subjects produce vague rubrics.

## What you'll see

Five phases, each opening with a `◈ MEDITATE: PHASE N` header:
voices speak alone in sequence (each with OBSERVATION / CONSTRAINT / IMPERATIVE / DISSENT slots),
collisions are enumerated between them, a critical path emerges from those collisions, and the
final phase delivers a **verdict** with its adjudication rubric restated verbatim. If the subject
fails the invocation gate you get a short DECLINED block plus — outside the ceremony — a plain
direct answer.

## If the stream dies

With `--durable`, completed phases are saved. Re-invoke with the same subject; the run resumes
from the first missing phase. Without it, re-run from scratch.

## Where to go deeper

- Full contracts, edge cases, invariants → SR (reference above)
- Changing the system itself → Maintainer's Guide
- Past runs → `data/coordination/meditations/MEDITATION_REGISTRY.md`

*End — v1.0.0.*
<!-- PROVENANCE-CORRECTED 2026-08-27T03:02:01Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: opencode | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

