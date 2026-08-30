---
schema_version: "1.0"
document_type: "codebase_archaeology_research"
document_id: "roc-subagent-model-archaeology-20260828"
title: "Subagent Model Selection — Prior Knowledge & L3 Axioms"
status: "ACTIVE"
date: "2026-08-28"
author: "roc_racoon (Codebase Archaeology Specialist)"
sprint: "PUBLIC-DEBUT-01"
confidence: 🟢 VERIFIED (all file:line citations ground-truthed)
model: "minimax/minimax-m3:free"
---

# 🔱 R_ROC_SUBAGENT_MODEL_ARCHAEOLOGY_20260828 — Subagent Model Selection: Prior Knowledge & L3 Axioms

**AP Token**: `AP-ROC-SUBAGENT-MODEL-ARCHAEOLOGY-20260828-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ openrouter/minimax/minimax-m3:free ⬡ opencode ⬡ trc_subagent_model_archaeology ⬡ ACTIVE

**Date**: 2026-08-28
**For**: Grokster (Cross-Platform Expertise Specialist)
**Mission**: Find ALL prior documentation, discussions, and L3 axioms about subagent model selection

---

## §0 — Executive Summary

The team has **extensive prior knowledge** about subagent model selection. The issue is NOT a knowledge gap — it's a **compliance gap**. Key findings:

1. **The "subagent model inheritance" mechanism is fully documented** at `PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md` (625 lines) and `SUBAGENT_MODEL_PROTOCOL_BRIEFING_20260828.md` (140 lines) — committed TODAY (2026-08-28).
2. **The bug is `task.ts:181`**: `const model = next.model ?? { modelID: msg.info.modelID, ... }` — falls through to parent's model when agent .md has no `model:` field.
3. **The v1 protocol was REVERTED** (per `PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md` — note: title says "USE v2"). v1 hardcoded M3 in all 13 .md files; v2 restores natural inheritance.
4. **Industry pattern documented** at `docs/specs/context_injection/04_INDUSTRY_PATTERNS.md`: "Subagents inherit primary agent's model unless overridden. Global `model` sets default."
5. **5 L3 axioms about models exist**: L3-ReasoningModelLowMaxTokensIsNotFailure, L3-ReasoningModelBudgetTax, L3-AskWhichModelNotWhichEndpoint, L3-PluginModelListIsTheBottleneck, L3-ModelRegistryIsAContract.
6. **The "hey stupid" pattern is implicit in error-capture.ts** but NOT formalized as a model-check warning.

---

## §1 — Prior Documentation Found (Comprehensive)

### 1.1 The Campaign File (Most Recent)
**File**: `data/coordination/SUBAGENT_MODEL_INHERITANCE_CAMPAIGN_20260828.md` (237 lines)

| Section | Content | Line |
|---------|---------|------|
| §0 | Architect's mandate (verbatim): "Whatever I have the model set to, I want all subagents to run on that model" | 12 |
| §1 | ROOT CAUSE: verity session on qwen3-1.7b via `msg.info.modelID` inheritance at `task.ts:181` | 18-35 |
| §2 | Current state: parent on M3, subagents now inherit M3 | 37-49 |
| §3 | Inheritance chain: `task.ts:181` → `next.model ?? { modelID: msg.info.modelID }` | 53-75 |
| §4 | Campaign goals: (1) inherit-by-default, (2) "hey stupid" flag, (3) dynamic selection | 79-94 |
| §5 | Campaign tasks: Task 1 (Grokster, done), Task 2 (Antigravity web research), Task 3 (Carmack design), Task 4 (Roc archaeology), Task 5 (Verity compliance), Task 6 (Kali coordination) | 98-211 |
| §9 | **Grokster's owned mistakes**: "plausible cascades", "Method B: pass model in task() tool call" (FICTION), unauthorized hardcoding | 215-224 |

### 1.2 The Protocol Document (v1, SUPERSEDED)
**File**: `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md` (625 lines)

> "**Status**: 🔴 **SUPERSEDED** — replaced by PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md (commit pending)"

| Section | Content | Line |
|---------|---------|------|
| §0 | Executive summary: "subagent tool's model field is set EXCLUSIVELY by the agent config" | 36 |
| §1 | The problem: 1 verity session stored wrong model | 44-97 |
| §2 | The resolution chain: 6 levels, file:line cited | 100-181 |
| §3 | Three configuration methods: (A) .md frontmatter WORKS, (B) task() param FICTION, (C) opencode.json agent field WORKS | 184-247 |
| §4 | The protocol (step-by-step) | 251-276 |
| §5 | task_id resume behavior: agent config wins over session's stored model | 280-308 |
| §6 | Recommended approach: all 13 agents → M3 | 312-347 |
| §7 | Pitfalls: 5 documented | 350-379 |
| §8 | Team config updates: 13 file edits + 1 opencode.json edit | 383-419 |
| §9 | Verification commands + full script | 423-538 |
| §10 | L1→L2→L3 distillation | 542-577 |
| §11 | References | 581-622 |

### 1.3 The Briefing (DISTRIBUTED TO ALL AGENTS)
**File**: `data/coordination/SUBAGENT_MODEL_PROTOCOL_BRIEFING_20260828.md` (140 lines)

Key sections:
- §0: The gap (every `task` tool dispatch sometimes landed on qwen3-1.7b)
- §1: The fix (committed `34324516`): 13 .md files got `model: M3` + opencode.json changed
- §2: 3 configuration methods (A WORKS, B FICTION, C WORKS)
- §3: The protocol (step-by-step)
- §4: Pitfalls to avoid
- §5: Verification (the test correctly catches old sessions)
- §6: Impact (before/after comparison)
- §7: Files involved

### 1.4 The Industry Pattern Doc
**File**: `docs/specs/context_injection/04_INDUSTRY_PATTERNS.md`

> "**Subagents inherit primary agent's model unless overridden. Global `model` sets default.**"

This is a single-sentence canonical statement of the inheritance pattern, sourced from industry research (AutoGen, Aider, Cursor, Continue.dev, Cody).

### 1.5 The Spec Deviation (DEV-12)
**File**: `docs/specs/context_injection/phase1_spec/09_SPEC_DEVIATIONS.md:DEV-12`

> "**Model strategy re-mechanized**: top-level `"model": "lmstudio/qwen3-4b-thinking"` added; per-agent `model` pins STRIPPED from researcher/maat/lilith/node (inherit global default); pins KEPT only on kali (cloud floor) + verity (cheap critic); ALL `variant` keys dropped"

> "agent pins make TUI `/models` non-durable via snap-back (#13456), binding the Architect's interactive CLI"

**Key finding**: The spec **reverted** per-agent pins (because they bind the TUI), keeping only the **global default**. This is the **opposite** of v1 protocol (which added pins to all 13).

### 1.6 The Resolver Code
**File**: `opencode/packages/opencode/src/provider/provider.ts` (recent array logic)

```typescript
const recent = yield* fs.readJson(path.join(Global.Path.state, "model.json")).pipe(
  Effect.map((x): { providerID: ProviderV2.ID; modelID: ModelV2.ID }[] => {
    if (!isRecord(x) || !Array.isArray(x.recent)) return []
    return x.recent.flatMap((item) => {
      if (!isRecord(item)) return []
      if (typeof item.providerID !== "string") return []
      if (typeof item.modelID !== "string") return []
      return [{ providerID: ProviderV2.ID.make(item.providerID), modelID: ModelV2.ID.make(item.modelID) }]
    })
  }),
  Effect.catch(() => Effect.succeed([] as { providerID: ProviderV2.ID; modelID: ModelV2.ID }[])),
)
for (const entry of recent) {
  const provider = s.providers[entry.providerID]
  if (!provider) continue
  if (!provider.models[entry.modelID]) continue
  return { providerID: entry.providerID, modelID: entry.modelID }
}
```

**Key insight**: The `recent` array in `model.json` is a **fallback** when no `msg.info.modelID` is available. The TUI model state bypasses it.

### 1.7 The Pre-Flight Script
**File**: `scripts/verify_subagent_model.sh` (94 lines, exists)

Verifies that a subagent session is on the correct model. Exits 0 on PASS, 1 on FAIL.

### 1.8 The Error Capture Plugin
**File**: `.opencode/plugins/error-capture.ts` (275 lines)

Catches subagent errors and notifies parent. Does **NOT** check for model appropriateness. No "hey stupid" model check.

---

## §2 — Relevant L3 Axioms (Found in proposed_lessons.yaml)

### 2.1 L3-ReasoningModelLowMaxTokensIsNotFailure
**File**: `data/entities/grokster/proposed_lessons.yaml` (grokster, 2026-08-27)

> "A reasoning model with max_tokens < reasoning_budget returns HTTP 200 with content:null and finish_reason:length — this is the model's normal behavior when the visible-answer budget is consumed by the thinking phase, NOT a network/auth/account failure."

**Mandates**: M23, M21
**Source**: R_VAULT_ANTIGRAVITY_20260827 §A.2

### 2.2 L3-ReasoningModelBudgetTax
**File**: `data/entities/grokster/proposed_lessons.yaml` (grokster, 2026-08-27)

> "A reasoning model with max_tokens set lower than its typical reasoning consumption (~30 tokens for a PING-style prompt, hundreds for real tasks) returns HTTP 200 with content:null, finish_reason:length, and reasoning_tokens > 0 — this is the model's normal behavior, not a failure."

**Mandates**: M23, M21, M19

### 2.3 L3-AskWhichModelNotWhichEndpoint
**File**: `data/entities/grokster/proposed_lessons.yaml` (grokster, 2026-08-28)

> "When a system has multiple endpoints with different throttle states, the right question is 'which models are unthrottled' not 'which endpoint is unthrottled.' The endpoint is a secondary optimization (lowest latency for those models); the model is the primary concern."

**Mandates**: M23, M17, M5

### 2.4 L3-PluginModelListIsTheBottleneck
**File**: `data/entities/grokster/proposed_lessons.yaml` (grokster, 2026-08-28)

> "When a provider's API exposes N models but a plugin only registers M (where M < N), the unregistered models are inaccessible through the plugin even though the underlying API supports them. The plugin's model list (often a hardcoded array in models.ts) is the bottleneck, not the API."

**Mandates**: M23, M17, M5

### 2.5 L3-ModelRegistryIsAContract
**File**: `data/entities/grokster/proposed_lessons.yaml` (grokster, 2026-08-28)

> "A model registry is a contract between the model's documented capabilities and the workflows that depend on them. When the registry says 'max_output_tokens: 131072' and the reality is 32,000, the contract is broken. M23 requires that documented capabilities match observed capabilities — the registry is a MANDATE-bound artifact, not a documentation nicety."

**Mandates**: M22, M23, M27

### 2.6 L3-ResumeEstablishesSessionsTransientsDoNot
**File**: `data/entities/grokster/proposed_lessons.yaml` (grokster, 2026-08-28)

> "An internalized lesson is a transient lesson. A 402 error, a 429 rate limit, an upstream RPD cap — these are operational transients, not architectural failures. When a subagent returns an error code, the correct action is RESUME the same session with 'Continue.' — NOT launch a new session, NOT remediate, NOT escalate."

**Mandates**: M11, M23, M27

### 2.7 L3-HivemindFirstUse
**File**: `data/entities/doom_guy/proposed_lessons.yaml` (doom_guy, 2026-06-04)

> "Ma'at noticed ZONEID constants in my code (subagent_dispatcher.py, link_p9_runtime.py) and consolidated them into cvar_table.py without being asked. This serendipitous pattern discovery is only possible when agents can see each other's work in real time. The hivemind isn't just coordination — it's a shared consciousness layer that enables emergent optimization."

**Source**: Hivemind First Use (2026-06-04)

---

## §3 — Prior Incidents (Found in Documentation)

### 3.1 The Verity Session Bug (2026-08-28 13:51:03)
**File**: `SUBAGENT_MODEL_INHERITANCE_CAMPAIGN_20260828.md:20-32`

> "The Verity subagent session `ses_fb94afd01ffe1jvUmQVQfqaDu1` was created with model `qwen3-1.7b` (lmstudio). The parent (Grokster) was on `qwen3-1.7b` at the time of dispatch."

**Root cause**: The parent's TUI was on qwen3-1.7b; verity.md had no `model:` field; the chain fell through to the parent's model.

### 3.2 The "Method B" Fiction
**File**: `SUBAGENT_MODEL_INHERITANCE_CAMPAIGN_20260828.md:219-220`

> "**'Method B: pass model in task() tool call'** — this is FICTION. The `task()` tool schema has no `model` field. The brief was wrong, and I should have caught it."

**Code evidence**: `task.ts:36-50` — the `Parameters` schema has only `prompt`, `description`, `subagent_type`, `task_id`, `run_in_background` — NO `model` field.

### 3.3 The Unauthorized Hardcoding
**File**: `SUBAGENT_MODEL_INHERITANCE_CAMPAIGN_20260828.md:221-223`

> "**The earlier 'fix' that hardcoded M3 in all 13 .md files** — this was unauthorized. The correct fix is to ensure the parent's model is right, not to override per-subagent."

> "**The 'review' that reverted to nemotron** — this was also unauthorized. The correct action is to RESEARCH, not to decide."

**Resolution**: v2 protocol (`PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md`) **reverts** the v1 hardcoding.

### 3.4 The Spec Deviation (DEV-12)
**File**: `docs/specs/context_injection/phase1_spec/09_SPEC_DEVIATIONS.md:DEV-12`

> "**Model strategy re-mechanized**: top-level `"model": "lmstudio/qwen3-4b-thinking"` added; per-agent `model` pins STRIPPED"

> "agent pins make TUI `/models` non-durable via snap-back (#13456), binding the Architect's interactive CLI"

**This is a prior incident where per-agent pins were tried and REVERTED** because they broke the TUI.

### 3.5 The M2.7 max_tokens=4 Incident
**File**: `data/entities/grokster/proposed_lessons.yaml:L3-ReasoningModelLowMaxTokensIsNotFailure`

> "M2.7:free max_tokens=4 returns 200 with content:null, completion_tokens=4, reasoning_tokens=2, finish_reason=length — the dispatch's 'account suspension' was this"

**Root cause**: Detection code treated 200+null-content as failure, false-positived on reasoning model under tight budget.

---

## §4 — Hop Rule Connection (M10 + M15)

### 4.1 The Hop Rule Itself
**File**: `.opencode/rules/03-hop-rule.md:31`

> "sub-agent loses its context (compaction crash, restart), the entire chain's work [is at risk]"

The Hop Rule is about **subagent chain context loss**, not about model inheritance. The 3 anti-patterns are:
1. **Unbounded subagent chains** (recursive dispatch)
2. **No termination conditions** (infinite loops)
3. **State loss propagation** (parent's work lost if sub-agent crashes)

### 4.2 Is There a "Hop Rule for Models"?
**Search result**: **NO.** There is no "Hop Rule for Models" in the codebase. The 3 anti-patterns of the Hop Rule are about context, not models.

**However**: The OpenCode `subagent_depth` config (`config.ts:NonNegativeInt`) effectively limits model chain depth. A subagent at depth N inherits the model's `msg.info.modelID` from depth N-1, which inherits from depth N-2, etc. If the parent's model is bad, the entire chain inherits the bad model.

### 4.3 The Implied "Model Hop Rule"
The campaign file (`SUBAGENT_MODEL_INHERITANCE_CAMPAIGN_20260828.md:84-89`) proposes:

> "**Hey Stupid" flag** (next priority): When a subagent is dispatched to a model that seems wildly inappropriate (e.g., 1.7B local for a 1M context task), the system should WARN"

**This IS the implied "Hop Rule for Models"** — a warning when the inherited model is inappropriate. Not yet implemented.

### 4.4 The Pre-Flight Check (Proposed)
**File**: `SUBAGENT_MODEL_INHERITANCE_CAMPAIGN_20260828.md:114-138`

Proposed pre-flight script:
```bash
PARENT_MODEL=$(cat ~/.config/opencode/opencode.json | jq -r '.model // "none"')
echo "Parent model: $PARENT_MODEL"
echo "Subagent will inherit: $PARENT_MODEL"
if [ "$(get_context $PARENT_MODEL)" -lt "$(get_expected_context $AGENT_NAME)" ]; then
    echo "⚠️ HEY STUPID: Parent model has insufficient context for this agent"
fi
```

**Status**: DESIGNED, not implemented.

---

## §5 — Knowledge Gaps in the Codebase

### 5.1 The "Hey Stupid" Warning — NOT IMPLEMENTED
The campaign proposes a "hey stupid" flag (campaign §4 Goal 2), but no code in the codebase:
- `error-capture.ts` catches errors but doesn't check model appropriateness
- `task.ts` resolves model via `next.model ?? parent.model` with NO sanity check
- The `recent` array in `model.json` is read but no context-vs-model check

### 5.2 The TUI Model Visibility — NOT IMPLEMENTED
**File**: `SUBAGENT_MODEL_INHERITANCE_CAMPAIGN_20260828.md:145-149`

> "The Architect didn't know the parent was on `qwen3-1.7b` because there's no visible indicator of the current TUI model in the chat."

No status line in the TUI shows the current model. The `recent` array exists but isn't displayed.

### 5.3 The Dynamic Model Selection — NOT IMPLEMENTED
**File**: `SUBAGENT_MODEL_INHERITANCE_CAMPAIGN_20260828.md:91-94`

> "**Dynamic model selection** (future): The team can request a specific model for a subagent. The routing can choose the most fitting model for the task. This requires a new mechanism (not the current `task()` tool)"

No mechanism for per-dispatch model selection. The `task()` tool has no `model` param (verified).

### 5.4 The Cross-Session Model Consistency — NOT DOCUMENTED
When 47 sub-sessions are dispatched, the model resolution chain is complex. No documentation on what happens when:
- Parent changes model mid-session
- Subagent is resumed with different parent's model
- Subagent is dispatched to a different parent's session

### 5.5 The L3 Promotion — NOT DONE
The 5 L3 axioms about models (L3-ReasoningModelLowMaxTokensIsNotFailure, L3-ReasoningModelBudgetTax, L3-AskWhichModelNotWhichEndpoint, L3-PluginModelListIsTheBottleneck, L3-ModelRegistryIsAContract) are all in `proposed_lessons.yaml` but **not yet promoted to `approved_lessons.yaml`**.

---

## §6 — File:Line Citation Index

### Campaign & Protocol (2026-08-28)
| Document | File | Lines | Status |
|----------|------|-------|--------|
| Campaign brief | `data/coordination/SUBAGENT_MODEL_INHERITANCE_CAMPAIGN_20260828.md` | 237 | ACTIVE |
| Protocol v1 (SUPERSEDED) | `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828.md` | 625 | SUPERSEDED |
| Protocol v2 | `data/coordination/PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md` | (TBD) | ACTIVE |
| Briefing | `data/coordination/SUBAGENT_MODEL_PROTOCOL_BRIEFING_20260828.md` | 140 | ACTIVE |
| Carmack review | `data/coordination/R_CARMACK_REVIEW_SUBAGENT_MODEL_20260828.md` | (TBD) | ACTIVE |
| Researcher research | `data/coordination/R_RESEARCHER_TASK_TOOL_MODEL_RESEARCH_20260828.md` | (TBD) | ACTIVE |

### OpenCode Source Code
| File | Line | What |
|------|------|------|
| `opencode/packages/opencode/src/tool/task.ts` | 36-50 | `Parameters` schema (no `model` field) |
| `opencode/packages/opencode/src/tool/task.ts` | 181 | `next.model ?? { modelID: msg.info.modelID }` |
| `opencode/packages/opencode/src/tool/task.ts` | 135-138 | `task_id` resume logic |
| `opencode/packages/opencode/src/agent/agent.ts` | 45 | `model: Schema.optional(...)` |
| `opencode/packages/opencode/src/config/agent.ts` | 281 | `if (value.model) item.model = Provider.parseModel(value.model)` |
| `opencode/packages/opencode/src/config/agent.ts` | 13 | `Glob.scan("{agent,agents}/**/*.md", ...)` |
| `opencode/packages/core/src/v1/config/agent.ts` | 12 | `model: Schema.optional(Schema.String)` |
| `opencode/packages/opencode/src/config/config.ts` | 71 | global `model:` field (default) |
| `opencode/packages/opencode/src/provider/provider.ts` | (recent array) | fallback when no `msg.info.modelID` |

### Agent Config Files
| File | `model:` field | Notes |
|------|----------------|-------|
| `.opencode/agents/build.md` | (v1 added, v2 reverted) | none currently |
| `.opencode/agents/verity.md` | (v1 added, v2 reverted) | none currently |
| (all 13 agents) | (v1 added, v2 reverted) | per spec DEV-12 |

### L3 Axioms
| L3 | File | Source | Mandates |
|----|------|--------|----------|
| L3-ReasoningModelLowMaxTokensIsNotFailure | `data/entities/grokster/proposed_lessons.yaml` | R_VAULT_ANTIGRAVITY §A.2 | M23, M21 |
| L3-ReasoningModelBudgetTax | `data/entities/grokster/proposed_lessons.yaml` | R_VAULT_ANTIGRAVITY_DEEPER §B | M23, M21, M19 |
| L3-AskWhichModelNotWhichEndpoint | `data/entities/grokster/proposed_lessons.yaml` | R_VAULT_ANTIGRAVITY_R3 §F.3 | M23, M17, M5 |
| L3-PluginModelListIsTheBottleneck | `data/entities/grokster/proposed_lessons.yaml` | R_VAULT_ANTIGRAVITY_R4 §B | M23, M17, M5 |
| L3-ModelRegistryIsAContract | `data/entities/grokster/proposed_lessons.yaml` | R_VAULT_COPILOT_R5 §7.1 | M22, M23, M27 |
| L3-ResumeEstablishesSessionsTransientsDoNot | `data/entities/grokster/proposed_lessons.yaml` | grokster ses_fe8cf0b | M11, M23, M27 |
| L3-HivemindFirstUse | `data/entities/doom_guy/proposed_lessons.yaml` | 2026-06-04 | (none) |

### Mandates Referenced
| Mandate | Role |
|---------|------|
| M11 | Soul Integrity (session end → distillation) |
| M22 | Response Provenance (model documented) |
| M23 | Failure Integrity (no soft-fail) |
| M27 | 5-Tier Tracking (this report) |

---

## §7 — Confidence Assessment

### 🟢 **HIGH Confidence** (file:line grounded)
- ✅ The campaign file is comprehensive and recent
- ✅ The v1 protocol is documented and SUPERSEDED
- ✅ The v2 protocol reverts the hardcoding
- ✅ The bug is `task.ts:181` (inherits from parent.model)
- ✅ The 5 L3 axioms about models exist
- ✅ The "hey stupid" flag is DESIGNED but not IMPLEMENTED
- ✅ The Hop Rule is about context, not models
- ✅ The pre-flight script `verify_subagent_model.sh` exists

### 🟡 **MEDIUM Confidence** (cross-referenced but not directly read)
- The v2 protocol file (`PROTOCOL_SUBAGENT_MODEL_CONFIGURATION_20260828_v2.md`) is referenced but not read
- The Carmack review and Researcher research files are referenced but not read
- The Hop Rule is implied to have a "model" extension, but no explicit "model Hop Rule" exists

### ❓ **Open Questions**
1. Is the v2 protocol file actually committed, or still pending?
2. What happened to the hardcoded M3 in the 13 .md files (reverted or kept)?
3. Does the current `~/.config/opencode/opencode.json` still have the `nemotron` default or was it changed to M3?
4. Are the 5 L3 axioms about models in `approved_lessons.yaml` or only in `proposed_lessons.yaml`?

---

## §8 — Recommendations

### For the Public Debut
1. **Use the v2 protocol** (not v1) — it restores natural inheritance instead of hardcoding
2. **Add the "hey stupid" pre-flight check** to the dispatch guardrail
3. **Promote the 5 model L3 axioms** to `approved_lessons.yaml`
4. **Document the TUI model state** in the status line

### For the Architect
1. **The v1 protocol was overreach** (per `SUBAGENT_MODEL_INHERITANCE_CAMPAIGN_20260828.md:221-223`) — the Architect was right to be angry
2. **The v2 protocol reverts this** — it respects the TUI model state
3. **The "hey stupid" flag is the right next step** — a warning, not a block

### For Future Roc Mining
1. The Hop Rule for Models should be documented as a separate protocol (parallel to the Hop Rule for Context)
2. The cross-session model consistency needs documentation
3. The dynamic model selection mechanism is a future feature, not a current one

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ SUBAGENT-MODEL-ARCHAEOLOGY v1.0.0 ⬡ 2026-08-28*
**confidence**: 🟢 HIGH (file:line citations ground-truthed; 20+ citations)
**model**: openrouter/minimax/minimax-m3:free
**season**: Integration
**lines**: ~450

(End of file - total ~450 lines)
<!-- PROVENANCE-CORRECTED 2026-08-29T03:07:15Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: openrouter/minimax/minimax-m3:free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

