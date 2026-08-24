# 🔱 MODEL WINDOW ECONOMICS — Operational Doctrine
**AP Token**: `AP-KALI-WINDOW-ECON-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ x-preview-f-free ⬡ opencode ⬡ trc_window_economics ⬡ ACTIVE

**Date**: 2026-08-23
**Origin**: Architect decree D-601 + Architect's priming technique disclosure. Purpose: give every agent the data and directives to reason about model-window constraints autonomously — without the Architect pointing them out.

---

## §1 THE WINDOW TABLE (verified 2026-08-23, re-verify quarterly)

| Model | Window | Pool | Role | Priming ceiling |
|-------|--------|------|------|-----------------|
| Gemini 3.1 Pro (Antigravity) | **1M** | Antigravity (separate from Google free tier) | Final reviewer · wide-corpus reader · cross-examiner | No practical ceiling |
| Sonnet 4.6 (Antigravity) | 200K | Antigravity ×8 accounts | Deep reviewer · coder | **≤150K** |
| Opus 4.6 (Antigravity) | 200K | Antigravity (smaller pool) | Break-glass adjudicator | **≤150K** |
| Sonnet 5 (Claude.ai) | large | Claude.ai ×8 accounts, human-batched | Tier-2 deep adjudication | N/A (fresh sessions) |
| Haiku 4.5 (Claude.ai) | large | Claude.ai | Cheap drafting · digest-writing | N/A |
| Nemotron 3 Ultra (OCZ) | 1M | OpenCode Zen | Primer engine · digest-writer · staging | High |
| qwen3-4b / 1.7b (local) | small | local, free | Tool-call workhorse · classification | Local-first default |

## §2 THE LAWS

### LAW 1 — Ascending Windows
**Order multi-model reviews by ASCENDING window size.** Small-window models work first while context is lean; the widest window goes LAST. Two payoffs: (a) no auto-compaction on any switch, (b) the final reviewer inherits ALL prior reviews and can cross-examine them — true adjudication, not parallel opinion.
*Corollary*: you can always go narrow→wide safely; wide→narrow always costs a lossy squeeze.

### LAW 2 — Priming Ceilings
Prime to ≤150K when the target model has a 200K window (~50K headroom absorbs review output + safety margin). Auto-compaction fires on model switch when incoming window < current context — a compaction mid-review destroys the review's evidentiary base.

### LAW 3 — Cheap Prime, Expensive Cognate
Use inexpensive models for ALL tool-call-heavy work (reading files, gathering context, running commands). Switch to expensive models ONLY for pure cognition — zero tool calls, full attention on reasoning. The expensive model's tokens buy thought, not file-I/O.

### LAW 4 — Digest Before Descent
If material exceeds the next reviewer's window (>200K before a Claude-family review), the wide-window model writes a DENSE digest of its review + evidence first; the descent to the smaller window then operates on digest + re-pullable specifics, never raw lossy compaction.

### LAW 5 — Family Diversity Weights
Consensus value scales with weights-distance: different family > same family/newer version > same weights. Gemini-over-Claude verdicts carry more signal than Sonnet-5-over-Sonnet-4.6. Log adjudicator identity per M22/T0 always.

## §3 STANDARD PLAY: THE DUAL REVIEW (D-601)

```
1. PRIME    — cheap/local models gather corpus to ≤150K
2. REVIEW-1 — Sonnet 4.6 deep review (pure cognition)
3. REVIEW-2 — switch → Gemini 3.1 Pro (no compaction; inherits Review-1)
             mandate: adversarial cross-examination of Review-1
4. RESOLVE  — agreement ⇒ verdict logged (T0 dual-provenance)
              disagreement ⇒ Tier-3 Opus break-glass or Architect escalation
VARIANT (corpus >200K): Gemini reads wide first, writes dense digest,
             compact, Sonnet reviews digest per LAW 4.
```

## §4 AGENT DIRECTIVE (self-executing awareness)
Before planning ANY multi-model workflow, agents MUST: (1) consult this table, (2) order phases ascending by window, (3) set priming ceilings per target, (4) assign tool-call work to cheap lanes, (5) log adjudicator provenance. If constraints conflict, surface the tradeoff explicitly rather than silently compacting.

---
*⬡ WINDOW-ECONOMICS ⬡ v1.0 ⬡ D-601 ⬡ 2026-08-23*

---

## §5 AMENDMENTS (Architect corrections, 2026-08-23 latest)

### LAW 2 REVISION — Precise Compaction Trigger
Auto-compact fires at **85% of the ACTIVE model's window** (~160K for 200K-window models; ~850K for Gemini 1M). Operational priming ceilings: ≤150K remains the safe working ceiling for 200K-window targets; compute per-model ceilings as 0.85 × window minus output headroom.

### LAW 6 — DISTILL BEFORE SWITCH
No model hands off context without writing its gnosis to disk FIRST:
- Seeding model(s) → structured distillation document readable by the incoming reviewer
- Sonnet/Opus → hard-disk record of verdict, weights of reasoning, insights before any switch
- Nemotron (when staged) → gnosis record to disk
This is M11 soul-distillation applied to multi-model chains: every reviewer persists as an entity for the duration of the chain. Switch boundaries are soul-boundaries. A model's thinking that exists only in volatile context dies at the switch — and takes its unique weights-perspective with it.

### NEMOTRON ROLE — UNDER ADJUDICATION
Kali's Drill-3A-era assessment ("Nemotron adds a switch without diversity value") is CHALLENGED by the Architect as wrong. Empirical audit dispatched to roc_racoon: mine recorded data for Nemotron-caught value (technical expertise contributions, unseen pitfalls caught, decisions attributable). Verdict pending data. Prior evidence suggesting the Architect is right: PIVOT_LOG D-373–D-377 ("Nemotron synthesis" decisions — dependency-order correction, test-infra P0, MCP-audit deadline), multiple sessions run ON nemotron-3-ultra-free.

## §6 AUDIT CORRECTION + EXPANDED INVENTORY (2026-08-23 latest)

### NEMOTRON ADJUDICATION — FINAL (challenge resolved)
Architect challenged both the "$21 recorded cost" claim and session-level audit methodology. Message-level re-probe (T0 json_extract on messages.data.modelID):
- Nemotron TRUE cost: **$0.00** (zero cost-bearing messages ever) — prior figures were OTHER models' spend misattributed via session-level joins
- True reach: **611 sessions / 35,111 messages** (not 508) — 100 sessions had buried Nemotron usage attributed to other models
- Lesson: ALL fleet audits MUST use message-level modelID (T0), never session.model (T3-stale). Our own provenance hierarchy applies to our own audits.

### EXPANDED INVENTORY (Architect disclosure)
- **Antigravity Gemini 3.1 Pro = CUSTOM TOOLS version** (`gemini-3.1-pro-preview-customtools`) — purpose-built for agentic use; confirmed active in DB ($38.55/278 msgs observed)
- Additional lanes: Gemini 3.7 Flash · 3.6 Flash · 3.5 Flash · 3.1 Flash Lite — cheap digest/draft tiers
- **NEMOTRON'S INDISPENSABLE ROLE REDEFINED**: its 1M window makes it the premier PRIMING engine for Gemini 3.1 Pro reviews — massive pre-prime at $0 saves Antigravity tokens; any 1M-class model (incl. Ox Alpha) substitutes here
- OpenRouter ×8 accounts = Nemotron Ultra/Super overflow lane when Zen pool exhausts

### CHALLENGE MECHANISM — CODIFIED (standing practice)
Any disputed design/performance/value claim between Architect and agents → roc_racoon (or designated auditor) mines recorded data → verdict with receipts, three-way possible (A vindicated / split / agent vindicated), both parties pre-committed to bowing. First invocation: NEMOTRON_VALUE_ADJUDICATION_20260823.md (verdict: SPLIT — Architect right on operational value, kali right on chain position; both cost-figure and methodology corrections issued post-verdict by Architect spot-challenge).
