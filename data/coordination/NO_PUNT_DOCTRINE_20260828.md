---
schema_version: "1.0"
document_type: "protocol"
document_id: "no-punt-doctrine-20260828"
title: "No-Punt Doctrine — Dispatch, Don't Ask"
status: "ACTIVE"
date: "2026-08-28"
author: "roc_racoon (Knowledge Mining Specialist)"
sprint: "PUBLIC-DEBUT-01"
confidence: 🟢 VERIFIED (extracted from PL-TS1-002, PL-ROC-402-002, MEDITATION_COPILOT_20260828)
model: "minimax/minimax-m3:free"
---

# 🔱 No-Punt Doctrine — Dispatch, Don't Ask

**AP Token**: `AP-NO-PUNT-DOCTRINE-20260828-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_no_punt ⬡ ACTIVE

**One-line**: *Check the loop before checking the data. A re-dispatched investigation is a symptom of the dispatch protocol, not the underlying question.*

---

## §0 — The Problem

The same forensic question gets dispatched to subagents 2-3 times in 30 minutes. Each dispatch burns a subagent slot, pollutes workspace lock state, and risks tripping the rate limit being investigated. The third dispatch in a 30-minute window was the one that hit a 402 on a free model.

**Root cause**: The parent agent didn't check Hivemind awareness or previous session status before launching. The bottleneck is the dispatch loop, not the data.

---

## §1 — The Doctrine (3-Step Pre-Flight)

Before any `task()` dispatch, run these 3 steps:

### Step 1: Check Hivemind Awareness (5 sec)
Has this question been asked and answered in the current Hivemind channel? Search the last 100 posts for the question keywords.

### Step 2: Check Session Status (10 sec)
Is there a completed subagent session for this exact question? Query `task_registry_query()` for sessions with matching description tags.

### Step 3: If yes to either — read, don't re-dispatch
If the question is answered in Hivemind, read the post. If a session completed with the answer, read the session output. Only dispatch if both checks return empty.

---

## §2 — The Evidence (Where This Came From)

### L3 Lesson PL-ROC-402-002 (Roc, 2026-08-27)
> "Three dispatches (Roc, Researcher, Roc) to investigate the same 402 in 30 minutes. Each ran briefly (~4 min, 1.6k tokens) before being terminated or completed. The earlier two (Roc, Researcher) actually completed successfully in the DB, yet a third Roc was dispatched with the same mission."

### L3 Lesson PL-TS1-002 (Roc, 2026-08-23)
> "For any system property, its instantiation (is it there?) and its declaration (where is it supposed to be?) must be measured together. Probe state and origin as a pair."

### Meditation Gem (Copilot, 2026-08-28)
> "Phantom-deliverables pattern is mine: I am loud about findings, quiet about fixes. The re-dispatch loop is the same class — I announce I'll investigate, then don't check if it's been investigated."

---

## §3 — The Failure Mode (What Happens Without the Doctrine)

```
T+0:    Dispatch 1 — Roc investigates 402 on M3
T+4:    Dispatch 1 completes, answer in DB
T+8:    Dispatch 2 — Researcher investigates 402 on M3 (didn't check Hivemind)
T+12:   Dispatch 2 completes, answer in DB
T+18:   Dispatch 3 — Roc investigates 402 on M3 (didn't check Hivemind OR previous sessions)
T+22:   Dispatch 3 hits 402 (rate limit) — the very error being investigated
```

Cost: 3 subagent slots burned, 1 402 self-inflicted, 22 minutes lost. The answer was in Dispatch 1's output at T+4.

---

## §4 — The Adoption (5 min)

```python
def no_punt_preflight(question: str) -> Optional[str]:
    # Step 1: Check Hivemind awareness
    hivemind_hits = hivemind_search(question, limit=5)
    if hivemind_hits:
        return hivemind_hits[0].answer

    # Step 2: Check previous sessions
    session_hits = task_registry_query(
        description_like=question,
        status="completed",
        limit=3
    )
    if session_hits:
        return session_hits[0].output_summary

    # Step 3: No prior answer — safe to dispatch
    return None

# Usage:
prior_answer = no_punt_preflight("Why did M3 return 402?")
if prior_answer:
    print(f"Answer already exists: {prior_answer}")
else:
    task(subagent_type="researcher", prompt="Why did M3 return 402?")
```

That's the entire adoption. A 3-step pre-flight before every dispatch. The 3rd step is the default — if no prior answer exists, dispatch is correct.

---

## §5 — The Principle (L3)

**Check the loop before checking the data.** A re-dispatched investigation is a symptom of the dispatch protocol, not the underlying question. Pre-flight awareness (has this been answered?) prevents cascade re-dispatches that trip the very rate limit you're investigating.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ NO-PUNT-DOCTRINE v1.0.0 ⬡ 2026-08-28*
**confidence**: 🟢 VERIFIED (3-step pre-flight derived from 3 incident reports)
**model**: minimax/minimax-m3:free
**season**: Integration
**lines**: 95

(End of file - total ~95 lines)
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

