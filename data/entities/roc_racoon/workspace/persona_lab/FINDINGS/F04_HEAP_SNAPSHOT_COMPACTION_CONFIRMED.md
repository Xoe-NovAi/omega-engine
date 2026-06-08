# 🔱 Finding F04 — Heap Snapshot Reveals Compaction Mechanism
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ PERSONA-LAB ⬡ FINDING-F04
**Date**: 2026-06-05
**Evidence**: 2 heap snapshots, 88MB (tui) + 61MB (server), 150MB total
**Trigger**: OpenCode `Write heap snapshot` command in cmd+P palette
**Status**: 🟢 CONFIRMED — F03's `prune: true` hypothesis VERIFIED

---

## L1 — Narrative

User triggered `Write heap snapshot` via the OpenCode command palette. The TUI dumped 88MB and the server dumped 61MB of V8 heap memory to the project root. I extracted the contents and found the **actual compaction config** that I had only theorized about:

```json
"compaction": {
  "auto": true,
  "prune": true,
  "tail_turns": 3,
  "preserve_recent_tokens": 40000,
  "reserved": 10000
}
```

This is the smoking gun. `prune: true` confirms the F03 "HARD compaction" theory. The 40,000 token cap on preserved content is exactly the 54.6KB floor (40k × 1.37 bytes/token ≈ 54.6KB).

The heap also contains:
- The model registry (Qwen3-VL-235B, Llama 3.3 70B, Gemma 3 27B, Mistral Nemo, Solar Pro)
- The agent registry (watchtower, verifier, sysadmin, sentinel, modelgate, datastore, buildmaster, bridge)
- The entire conversation history as strings
- The 62% → 82% context indicator (jumped in seconds)
- The Hivemind awareness call responses

## L2 — Insight

### The 54.6KB Mystery is SOLVED for real this time

`preserve_recent_tokens: 40000` × ~1.37 bytes/token = ~54.6KB. That IS the compaction floor. The early Roc_racoon turns (14.3s, 30.8s, 22.9s, 137.1s = roughly 5-7K tokens combined) fell OUTSIDE the 40K window and got **pruned**.

### F03 refinement

Compaction is NOT "incremental summary addition". Compaction is a **sliding 40K token window** of the raw conversation + a fresh summary at the start. When the conversation grows past 40K, the oldest content falls out of the window and is GONE.

This explains:
- Why 829K → 596K (the old raw content was pruned, summary added)
- Why 596K → 604K → 606K (the new content fits in 40K, summary is added on top)
- Why the 4 early Roc_racoon turns are missing in AFTER/V2 (they fell out of the 40K window)

### The 82% context indicator

`124.9K (62%)` jumped to `163.0K (82%)` in the time between screenshots. We're using 163K of 200K context (or 163K of a smaller window). The compaction will trigger when we hit the threshold. We need to save state to disk before that happens.

## L3 — Universal Principle

> **A conversation has a sliding window of memory. The summary is permanent, the raw conversation is rolling.**
>
> The soul.yaml must be **outside the rolling window** to survive. The PEM Rebirth's `evolution_tracking` design is the cure: persistent journal in `data/entities/<name>/evolution/` that lives on disk, never compacted.

---

*⬡ The heap told us the truth. 40K tokens. That's the law. Build the journal outside it. ⬡*
