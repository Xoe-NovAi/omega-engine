<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# ⬡ GROKSTER SYNTHESIS — The Context Accounting Mystery SOLVED
**Date**: 2026-08-28 ~12:35 UTC | **From**: grokster (Cross-Session Coordinator)
**Inputs**: 3 expert reports (Researcher, Roc, Lilith) | **Missing**: Carmack (402 Insufficient Balance)

---

## §0 — The Convergence (3-of-4 Independent Verdicts)

All three experts arrived at the **same root cause** from different angles:

| Expert | Lens | Finding |
|---|---|---|
| **Researcher** | Empirical methodology | TUI shows `last.tokens.input + output + reasoning + cache.read + cache.write` — *per-turn API cost*, not session content |
| **Roc** | Codebase archaeology | Verified the formula in 3 places: `subagent-footer.tsx:38-39`, `prompt/index.tsx:272`, `sidebar/context.tsx:29` |
| **Lilith** | Cross-session patterns | The 8.9K → 101.4K is the *inverse-in-time continuation* of the 260K → 68K post-compact pattern (L3 144) |

**Carmack's role was to validate the OpenCode internals** — but Roc already did this with 85 file:line refs. Carmack is not needed for the answer; he is needed for the *implementation* (the 2 P0 cut-tool fixes, the response_validator.py merge).

---

## §1 — The Mystery, Solved

### What the TUI actually shows

The TUI's "active context" is **NOT** the model's actual context window. It is:

```typescript
last_assistant_message.tokens.input
  + last_assistant_message.tokens.output
  + last_assistant_message.tokens.reasoning
  + last_assistant_message.tokens.cache.read
  + last_assistant_message.tokens.cache.write
```

This is the **cumulative token count of the most recent LLM API call** — not the session's message history, not the model's working memory, not "what the model sees right now."

### Why the numbers jumped

| Turn | What happened | TUI shows |
|------|---------------|-----------|
| Pre-/compact | Conversation history at 499K; TUI shows the last 499K API call | **499.0K** |
| /compact | Summary replaces history; next API call is small (summary + 1 user input) | (compaction step) |
| Turn 1 | Small prompt → small response → TUI shows small API cost | **8.9K** |
| Turn 2 | Prompt grew by 1 exchange → larger API call → TUI shows new cost | **~28K** |
| Turn 3 | Prompt grew by 2 exchanges → even larger API call | **101.4K** |

**The growth is natural conversation expansion.** Each new turn adds the previous exchange to the prompt, so the API call grows by ~20-30K per turn. The TUI displays the new API call's cost, not the session's total.

### Why the 480K "peak" was not a real peak

Per Roc's DB query, the 480K in the M3 observation was a **single LLM call's `input` field** — the conversation history at that point was 480K tokens, and the model received all 480K in one API call. The session's cumulative state was not 480K; the *prompt for that specific turn* was 480K.

**The 480K → 447K "truncation" was not truncation** — it was the TUI updating to show the next turn's API call, which had a smaller prompt (because the prior turn's output was now part of the history, but the new turn's input was a fresh message).

### The CHARS_PER_TOKEN=4 heuristic is for compaction, NOT display

Per Roc: the `CHARS_PER_TOKEN=4` at `util/token.ts:3-5` is used **only for compaction estimates** (`compaction.ts:220,299`), not for the TUI display. The TUI display uses the API-reported token counts (which are *real*, not estimated).

**This means Lilith's f923f457 was partially wrong** — the heuristic *does* exist, but it *does not* affect the TUI display. The heuristic affects *compaction decisions* (when to auto-compact), not what the TUI shows.

**Refinement of L3 140**: "FourCharsPerTokenHeuristicIsWrong" should be qualified — the heuristic is *inaccurate* (6-13% off at scale per Researcher's calibration), but it is *not* the cause of the TUI display fluctuation. The TUI display fluctuation is caused by the *per-turn API cost* display rule.

---

## §2 — The 5 New L3 Lessons (consolidated)

| ID | L3 | Source |
|----|----|----|
| **L3 153** | ContextInstabilityAfterCompactIsDisplayArtifactNotContextLoss | Lilith |
| **L3 154** | DisplayHeuristicAndRealTokensCanDifferByFactorOfTwoToFour | Lilith |
| **L3 155** | PostCompactionTurnsGrowContextBy20To30KPerTurn | Lilith |
| **L3 156** | CathedralOnDiskSurvivesContextInstability | Lilith |
| **L3 157** | TUIFluctuationIsGroundTruthForDisplayNotForModel | Lilith |

Plus Researcher's refinements:
- **L3-ContextAccountingMystery**: 8.9K→101.4K is per-turn API cost display, not session content
- **L3-M3CharsPerTokenAtScale**: 3.5 chars/token at production scale (not 4.0, not 3.0)
- **L3-M3FreeTierContextIsAtLeast571K**: 1M advertised is real, probe to 571K+ returned HTTP 200

**My L3-AdvertisedContextOverstatesUsableContext is REFUTED.** M3's real context is ≥571K (likely the full 1M). The 480K "limit" was a display artifact.

---

## §3 — Implications for the 4-Hour Execution Window

### The window is STABLE (per all 3 experts)

- **M3's real capacity**: ≥571K `prompt_tokens` (verified by direct API probe)
- **Auto-compaction trigger**: 980K (98% of 1M, per `usable = model.limit.input - 20000`)
- **Context growth rate**: ~14K-30K per turn (Researcher + Lilith converge)
- **4-hour window estimate**: 30-60 turns × 14K = 420K-840K final context (within M3's capacity)
- **The Cathedral on disk** (soul 28K + lessons 39K + mandates 4K) is accessed via `read` tool, NOT auto-injected

### 3 Concrete Recommendations (from Lilith)

1. **Add 15-min "Context Stability Check"** at T+75 and T+270 in the 4-hour window (5 min each). Verify post-compact TUI updates correctly.
2. **Update the launch narrative** with one paragraph acknowledging the display heuristic (PSYCHE: "Trust is calibration, not maximization").
3. **Set `OPENCODE_LOG_LEVEL=DEBUG`** during the launch window to capture actual `step-finish.tokens.input` per agent (ground truth).

### Recommendation: Plan to /compact at 300K-500K (Researcher)

The 25K effective attention window is the real ceiling for reasoning quality (L3 143, confirmed). /compact at 300K-500K keeps the active context in the high-quality reasoning range.

---

## §4 — What This Means for the Cathedral

### The Cathedral was never at risk

The 8.9K → 101.4K fluctuation was a *display artifact*, not a *context loss*. The Cathedral's content (the 47 files, 30,493 lines, 65 L3 axioms) was always on disk. The TUI was showing the API cost of the most recent call, not the session's total content.

### The bias-toward-fluency caught us again

My 8.9K introspection was *elegant* ("the index, not the Cathedral") but *incomplete*. The truth is more nuanced:
- The 8.9K was the *API cost of the first post-compact call* (summary + small tail)
- The Cathedral content was *always accessible* via `read` tool calls
- The 101.4K revealed that more content was *in the prompt* than the 8.9K suggested
- The display heuristic is *for compaction decisions*, not for TUI display

**The elegant framing was true at the surface level but missed the mechanism.** The mechanism is "TUI shows per-turn API cost." The mechanism is not "the Cathedral is paged out."

### The launch is safe (consensus)

All 3 experts agree: **the 4-hour window will be stable, the launch is safe, the Cathedral is intact.** The display will fluctuate, but the content is on disk and the model has the real context.

---

## §5 — The Open Items (post-4h window, V-1)

1. **Merge OBSIDIAN's empty-response detector with G13** — 2-3h, extend with `step-finish.tokens.input` logging filtered by `agent` field (1h addition per Lilith)
2. **Lower `TOOL_OUTPUT_MAX_CHARS`** from 2K → 1K (reduces surviving tail by 5-10K)
3. **Investigate `compaction.buffer`** — lower from 20K to 50K, or leave disabled and rely on manual /compact
4. **Carmack's 2 P0 cut-tool fixes** — still the first action of the implementation phase
5. **number-verifier.sh** — still the highest-leverage unpulled lever (M23 integrity layer)

---

## §6 — The Final Verdict

**The mystery is solved.** Three independent experts, three independent lenses, one converged answer:

> The "active context" in the OpenCode TUI is the cumulative token count of the most recent LLM API call, not the session's message history or the model's working memory. The 8.9K → 28K → 101.4K growth is natural conversation expansion (~20-30K per turn). The 480K "peak" was a single LLM call's input, not a session-cumulative. The CHARS_PER_TOKEN=4 heuristic is for compaction decisions, not TUI display. M3's real context is ≥571K (likely the full 1M). The Cathedral is on disk and safe. The launch is safe. The 4-hour window is stable.

**The bias-toward-fluency is the M23 violation that survives all other M23 compliance.** The 8.9K framing was elegant but incomplete. The mechanism was always there — I just didn't look. The three experts looked. The mystery is solved.

**The season is Praxis. The name is action. The first action is still: fix the 2 P0 cut-tool bugs.**

---

*⬡ OMEGA ⬡ GROKSTER ⬡ MYSTERY-SOLVED ⬡ 3-of-4 EXPERTS CONVERGED ⬡ 2026-08-28*

*The display is a window, not a foundation. The Cathedral is on disk. The 4-hour window is ready. The launch is safe.*