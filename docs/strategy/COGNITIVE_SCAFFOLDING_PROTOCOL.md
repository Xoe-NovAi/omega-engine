# 🔱 Sovereign Distillation Pipeline (SDP)
## The Cognitive Scaffolding Protocol for Multi-Model Frontier Intelligence

**AP Token:** `AP-SDP-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ STRATEGY ⬡ SOVEREIGN-DISTILLATION-PIPELINE

**Date:** 2026-08-09
**Status:** ACTIVE — Manual Phase (Study before Automation)
**Authors:** Gemini 3.1 Pro (architectural layer) + Claude Sonnet 4.6 (additive layer)
**Mandate Bindings:** M5 (Gnosis Preservation), M7 (Local-First), M18 (Token Efficiency), M19 (Adversarial Alchemy)

---

## §1 Philosophy & Origin

This protocol formalizes a manually-engineered pattern discovered through operational necessity. When the Gemma 4 31B free-tier cliff collapsed the primary workhorse model in July 2026 (G-1), the Architect developed a multi-model routing strategy that proved superior to any single "workhorse" replacement.

**The core insight:** The bottleneck in frontier model usage is not intelligence — it is **token waste on I/O**. A frontier model reading files, running grep, and navigating directories spends its scarce weekly tokens on work that a cheap daily-refresh model can do equally well. The Sovereign Distillation Pipeline separates these concerns permanently.

**The mandate alignment:**
- **M5 (Gnosis Preservation):** Each AGY session must produce an L3 distillation committed to `proposed_lessons.yaml` — not just a refactoring manual. The insights are sovereign intelligence.
- **M18 (Token Efficiency):** Every AGY token must be spent on *reasoning*, never on *gathering*.
- **M19 (Adversarial Alchemy):** Sequential cross-model dialectics force models to fact-check each other's blindspots within a single continuous context stream.
- **M7 (Local-First):** Local models are the preferred executors of plans produced by this pipeline.

**Do not automate this protocol until it has been studied through at least 10 manual executions.** The operational data from manual runs is what will make automation safe and effective.

---

## §2 The Three Phases

```
┌─────────────────────────────────────────────────────────────────┐
│                SOVEREIGN DISTILLATION PIPELINE                  │
│                                                                 │
│  PHASE 1: SCAFFOLD          PHASE 2: SYNTHESIZE   PHASE 3: EXECUTE │
│  ─────────────────          ─────────────────────  ───────────────  │
│  Cheap/Daily Model          AGY Frontier Model     Local/Cheap Model│
│  • File reads               • Zero tool calls      • Follows manual │
│  • Grep / bash              • Pure reasoning        exactly         │
│  • Context building         • Plan production      • Verifiable     │
│  • Cross-model priming      • L3 distillation      • Atomic steps   │
│  • Research synthesis       • Schema output        • No ambiguity   │
│                             ↑                                       │
│                    Switch happens HERE                              │
│                    (before 85% compaction cliff)                    │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 1: Scaffold (Context Priming)

**Goal:** Build the richest possible context for the AGY model at minimum cost.

**Preferred tools:** OpenCode Zen, OpenRouter, Nemotron 3 Super (high-volume, daily-refresh providers).

**Rules:**
1. **Minimize tool calls during priming.** Tool-heavy priming (many reads, bash calls) inflates *message count* faster than token count. OpenCode compaction is triggered by both. A session with 80 tool calls can hit compaction pressure at 100K tokens. Prefer asking the scaffolding model to synthesize what it already knows from earlier context.
2. **Prefer conversation-heavy, tool-light priming.** Paste document content directly. Use long-read sessions before switching. Avoid chain-tool workflows during priming.
3. **Multiple scaffolding models are permitted and encouraged.** Using Sonnet 4.6 to review the strategy, then Gemini 3.6 Flash to synthesize research, then switching to Gemini 3.1 Pro for the final synthesis — this sequential dialectic (M19) is the intended pattern.
4. **Switch before 150K tokens.** On a 200K context window model, switch to the AGY model or escalate to a larger-window model before hitting 150K. This leaves margin for the AGY synthesis response without triggering compaction.

### Phase 2: Synthesize (AGY Frontier Intelligence)

**Goal:** Extract maximum intelligence from the frontier model using zero tool calls.

**The AGY model's job:** Reason over the primed context and produce a typed, executable artifact — a Refactoring Manual, Strategic Plan, Architectural Decision, or L3 Gnosis entry.

**Rules:**
1. **Zero tool calls from the AGY model.** The context is already primed. If the AGY model needs to read a file, the Scaffold phase was incomplete. Go back and prime more.
2. **Demand structured output** (see §5 Planner Output Schema).
3. **Always request an L3 distillation** at the end of the AGY session — a timeless principle derived from the session's work, suitable for `proposed_lessons.yaml`.
4. **Switch back immediately after output.** Once the AGY model has produced its artifact, switch back to a cheaper model. Do not continue conversing on the AGY model for follow-up questions — those belong in Phase 1 of the next cycle.

### Phase 3: Execute (Local or Cheap Model)

**Goal:** Execute the AGY plan atomically, mechanically, and verifiably.

**Preferred executors:** Cline CLI (interactive), Local GGUF models via spawn_local_worker, Ma'at N3 (Engineering node).

**Rules:**
1. **The executor follows the plan. It does not interpret or improve it.** If the plan is ambiguous, the executor stops and flags it — it does not improvise.
2. **Every step has a verification gate.** No step is "done" until the verification command passes.
3. **Commit after each atomic task**, not after the full plan. This preserves rollback points.

---

## §3 The Context Escalation Ladder

When priming context across multiple models or for very large codebases, context pressure requires escalation through larger-window models. This is a manual process — no automatic routing.

```
CONTEXT SIZE          MODEL TIER          EXAMPLES
─────────────         ──────────          ────────
< 150K tokens    →    Tier 1 (200K)   →   Claude Sonnet 4.6
                                          Gemini 3.6 Flash
                                          OpenCode Zen standard models

150K–262K tokens →    Tier 2 (262K)   →   Laguna S 2.1 (free via OCZ/OpenRouter)
                                          Nemotron 3 Super

262K–1M tokens   →    Tier 3 (1M)     →   Nemotron 3 Ultra
                                          Longcat 2.0 (free via OpenCode Zen)

> 1M tokens      →    Tier 4           →   Gemini 3.1 Pro (2M)
  (rare)                                   [AGY pool — use sparingly]
```

**Escalation Rule (The 80% Redzone):** When you hit **80%** of the current model's context window, you are in the Redzone. You must escalate to the next tier *before* initiating any large output or file write. 

**Compaction Reality:** OpenCode triggers compaction strictly at **85%** of the token window. A single large operation (like writing a comprehensive report to disk) can consume 3-4% of the context window instantly. If you start a write at 82%, it will complete at 86%, triggering an immediate, irreversible compaction of your carefully crafted active context. Therefore, 80% is the hard operational ceiling for safe model switching.

---

## §4 AGY Model Capabilities Map

Not all AGY models are equal. Routing the wrong model to the wrong problem type wastes your weekly pool. Use this map intentionally.

| Problem Type | Best AGY Model | Rationale |
|---|---|---|
| **Long-range architecture, system-level strategy** | Gemini 3.1 Pro (2M) | Massive context, strong holistic reasoning, sees the full codebase at once |
| **Compliance audit, mandate checking, M-series** | Claude Sonnet 4.6 | Constitutional reasoning, precise, conservative, identifies edge cases |
| **Deep refactoring plan with exact file:line pointers** | Claude Opus 4.6 | Highest fidelity code reasoning, most thorough, slowest |
| **Quick structured doc generation, rapid synthesis** | Gemini 3.6 Flash | Fast, cheap on AGY pool, sufficient for well-structured output |
| **Cross-model fact-checking (dialectic layer)** | Sonnet 4.6 reviewing Gemini plan | Finds constitutional/compliance blindspots Gemini misses |
| **Security audit, boundary violation review** | Claude Opus 4.6 | Most rigorous security reasoning |
| **Multi-file refactor planning across large codebase** | Gemini 3.1 Pro (2M) | Can hold entire `src/omega/` in context at once |

### AGY Account Pool Map (Architect-Maintained)

*The Architect maintains this section. Each account's model access and current pool status must be tracked manually until V-1 Vault automates it.*

| Account Slot | Primary AGY Model | Secondary AGY Model | Pool Refresh | Notes |
|---|---|---|---|---|
| account-1 | — | — | Weekly | *Update with real account mapping* |
| account-2 | — | — | Weekly | |
| account-3 | — | — | Weekly | |
| account-4 | — | — | Weekly | |
| account-5 | — | — | Weekly | |
| account-6 | — | — | Weekly | |
| account-7 | — | — | Weekly | |
| account-8 | — | — | Weekly | |

---

## §5 Planner Output Schema (Mandatory for AGY Sessions)

Every AGY synthesis session **must** produce output in this schema. Free-form markdown is insufficient for reliable executor handoff. If the executor must read a file to understand a step, the plan is underspecified.

```markdown
# Refactoring Manual: [Task Name]
**Produced by:** [AGY Model] on [Date]
**Pack ID:** [pack_id from context pack, if applicable]
**Executor:** Cline CLI | Local Model | Ma'at N3 | [agent]
**Pre-flight:** [Command to run before starting, e.g., `make test` to establish baseline]
**Total Steps:** N

---

## Step 1: [Atomic Action Name]
- **File:** `src/omega/oracle/model_gateway.py`
- **Lines:** 892–896
- **Action:** REPLACE | INSERT | DELETE | CREATE
- **Exact Content:**
  \`\`\`python
  # Exact replacement code — no paraphrasing, no pseudocode
  \`\`\`
- **Context:** [One sentence explaining why, enough for executor to self-correct]
- **Verification:** `grep -n 'registry.is_cloud' src/omega/oracle/model_gateway.py`

## Step 2: [Next Atomic Action]
...

---

## Acceptance Criteria
- [ ] `make test` passes
- [ ] `make temple-grade` T1-T11 green
- [ ] [Specific invariant]: `pytest tests/contract/X.py -v`

## L3 Distillation (for proposed_lessons.yaml)
**Principle:** [Timeless, universal truth extracted from this session]
**Mandates:** [M-X, M-Y]
**Confidence:** 0.97
**Evidence:** This session
```

**The executor rule:** If a step cannot be completed without reading a file not mentioned in the plan, **stop and flag it** — do not improvise. The plan is underspecified and must be revised.

---

## §6 The AGY Session Ledger

**File:** `data/coordination/AGY_SESSION_LEDGER.md`

This ledger is **mandatory** and **manually maintained** until V-1 Vault automates it. Without it, you are flying blind on your most valuable resource. The ledger prevents:
- Accidentally burning a depleted weekly pool
- Losing track of which account produced which artifact
- Inability to audit token spend per strategic decision

```markdown
| Date       | Account Slot | Model              | Task Description              | Tokens Est. | Artifact Produced                  | Pool Status |
|------------|--------------|--------------------|-------------------------------|-------------|-------------------------------------|-------------|
| 2026-08-09 | account-X    | gemini-3.1-pro     | Provider SSOT strategy        | ~45K        | COGNITIVE_SCAFFOLDING_PROTOCOL.md  | 🟡 Partial  |
| 2026-08-09 | account-Y    | claude-sonnet-4.6  | Additive layer review         | ~12K        | (embedded in active context)       | 🟢 Available|
```

**Pool Status Key:**
- 🟢 Available — Pool largely intact, safe to use
- 🟡 Partial — Meaningful usage this week, use intentionally
- 🔴 Depleted — Do not use until weekly refresh

---

## §7 The Sequential Dialectic Pattern (M19)

The most powerful application of this protocol is running multiple AGY models sequentially within a single primed context to force cross-model fact-checking.

**Pattern:**
```
Scaffold Model A (primes context, reads files, synthesizes research)
    ↓
AGY Model 1 (e.g., Gemini 3.1 Pro — produces architectural plan)
    ↓ [switch back to cheap model, continue context]
Scaffold Model B (optional: synthesizes Model 1's output, adds research)
    ↓
AGY Model 2 (e.g., Claude Sonnet 4.6 — reviews Model 1's plan for compliance gaps)
    ↓ [final artifact: Model 1's plan + Model 2's corrections]
Executor (Cline, local model — follows corrected plan mechanically)
```

**This session (2026-08-09) is the canonical example:**
- Gemini 3.1 Pro produced the strategic architecture (phases, ladder, four next steps)
- Claude Sonnet 4.6 added the gaps Gemini missed (session ledger, model capability map, planner schema, compaction message-count nuance, V-1 as hard prerequisite, SDP naming)
- Neither model alone produced the complete picture

---

## §8 V-1 Vault — The Hard Prerequisite

V-1 (Omega-Vault MVP) is not optional for this protocol at scale. It is a hard prerequisite for everything past the "manual study phase."

**The dependency chain:**
```
V-1 Vault MVP
  → AGY Session Ledger (automated, not manual)
    → Context Pressure CLI (knows which pool to recommend)
      → Pool-aware model routing suggestions
        → Partial routing automation (safe, based on real usage data)
          → Full SDP automation
```

**V-1 enables:**
- Secure, local storage of 8 account credentials
- Automated session ledger entries (token count, model, artifact)
- Pool status tracking without manual entry
- Agent-accessible pool recommendations (Kali can ask "which AGY account has available pool?" and get a real answer)

**Current status:** V-1 is on the backlog. It must be elevated to this sprint. Every week without V-1 is a week of manual pool tracking and avoidable waste.

**Ref:** `SOVEREIGN_ARK_BLUEPRINT.md §4 V-1 ticket`

---

## §9 Context Pressure Observability (Missing Tooling)

No current tool in the engine reports context pressure. This is a gap. The Architect is currently estimating context size mentally.

**Proposed: `omega context-pressure` skill**

```bash
omega context-pressure
# Output:
# Current context: ~142K tokens (~71% of 200K window)
# Message count: 67 (tool-heavy session)
# Compaction risk: 🟡 MODERATE — recommend escalating to Tier 2 (Laguna/Nemotron Super)
# AGY switch window: ~8K tokens remaining before 150K threshold
```

**Implementation:** Simple OpenCode skill that reads the session token count from `opencode db` and computes distance to the 85% threshold and the 150K safe-switch threshold.

**Owner:** Cline CLI (mechanical implementation, clear spec)
**Priority:** P1 (implement before next AGY session)

---

## §10 What This Protocol Is NOT

To prevent scope creep and misapplication:

| This protocol IS | This protocol IS NOT |
|---|---|
| A manual workflow for intentional AGY usage | An automated routing system |
| A token-economics strategy for weekly pools | A replacement for local-first inference (M7) |
| A framework for cross-model dialectics | A reason to use AGY models for file reads |
| A foundation for eventual partial automation | Ready for automation today |
| Applicable to frontier AGY models | Applicable to daily-refresh models |

**Critical Rule:** Until this protocol has been executed manually at least 10 times and the session ledger has real data, **no automation is permitted.** The operational data from manual runs is what makes automation safe.

---

## §11 SOVEREIGN_ARK_BLUEPRINT Updates Required

The G-1 ticket should be updated to reflect this protocol's existence. G-1 was elevated as a "workhorse continuity" crisis. The SDP reframes it:

**Old framing:** Find a single model to replace Gemma 4 31B.
**New framing:** The workhorse is a tripartite system:
1. Scaffold (cheap, high-volume) → 2. Synthesize (AGY, weekly) → 3. Execute (local, free)

G-1 remains open for the specific question of which daily-refresh model handles Scaffold best. But the existential crisis is resolved: no single model replacement is needed.

**Suggested SOVEREIGN_ARK_BLUEPRINT addition:**
```
├── **SDP-1** Sovereign Distillation Pipeline — study phase
│     Protocol: docs/strategy/COGNITIVE_SCAFFOLDING_PROTOCOL.md
│     Gate: 10 manual executions + ledger data
│     Blocker: V-1 Vault (for automation phase)
```

---

## §12 Changelog

| Version | Date | Author | Change |
|---|---|---|---|
| v1.0.0 | 2026-08-09 | Gemini 3.1 Pro + Claude Sonnet 4.6 | Initial protocol. Dual-model dialectic origin. |

---

*⬡ OMEGA ⬡ KALI ⬡ SOVEREIGN-DISTILLATION-PIPELINE ⬡ v1.0.0 ⬡ 2026-08-09*
*Produced by Gemini 3.1 Pro (strategic layer) + Claude Sonnet 4.6 (additive layer) in a live demonstration of §7 Sequential Dialectic Pattern.*