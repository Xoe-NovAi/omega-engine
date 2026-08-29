# 🔱 Context Injection System & Hydration Protocol — Deep Investigation

**AP Token**: `AP-CONTEXT-INJECTION-INVESTIGATION-v1.0.0`
⬡ OMEGA ⬡ ROC_RACOON ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_context_injection ⬡ ACTIVE

**Date**: 2026-08-20
**Mission**: Map the entire context injection pipeline for Omega Engine agents. Identify what gets injected, how, where it's configured, and how to optimize it.

---

## 📋 Executive Summary

The Omega Engine's context injection system operates through **four distinct layers** that combine to create a massive context payload (estimated **60,000-100,000+ tokens**) injected into every agent at session start. This investigation maps the complete pipeline and proposes a tiered/lazy-loading optimization architecture.

### Key Finding: The "Global Injection" Problem

**opencode.json** defines 6 global instruction files that are injected into **EVERY agent** regardless of role:
- `SOVEREIGN_MANDATES.md` (239 lines, ~8,000 tokens)
- `ORACLE_STACK.md` (10 lines, ~300 tokens)
- `MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md` (420 lines, ~14,000 tokens)
- `SOVEREIGN_ARK_BLUEPRINT.md` (315 lines, ~10,500 tokens)
- `CREDITS.md` (24 lines, ~800 tokens)
- **Agent-specific file** (e.g., `.opencode/agents/roc_racoon.md` — 100 lines, ~3,500 tokens)

**Plus**: OMEGA_CODEX.md (411 lines, ~14,000 tokens) — read via mandatory hydration sequence
**Plus**: AGENTS.md discovery (if present in project root)
**Plus**: Skills metadata (22 skills, injected via SystemPrompt.skills())
**Plus**: MCP instructions (from 5 MCP servers)
**Plus**: Environment context (working directory, git status, platform, date)

---

## 🗺️ Injection Map — Visual Flow

```mermaid
flowchart TD
    subgraph "CONFIG LAYER"
        OC[opencode.json]
        OC -->|instructions: []| GLOBAL[6 Global Instruction Files]
        OC -->|agent.*.instructions| AGENT_SPEC[Agent-Specific File]
    end

    subgraph "DISCOVERY LAYER"
        AGENTS_MD[AGENTS.md Discovery<br/>Upward scan from CWD]
        CLAUDE_MD[CLAUDE.md Fallback<br/>~/.claude/CLAUDE.md]
        GLOBAL_CFG[~/.config/opencode/AGENTS.md]
    end

    subgraph "RUNTIME ASSEMBLY (SystemPrompt.Service)"
        BASE[Base Provider Prompt<br/>anthropic.txt / beast.txt / qwen.txt]
        ENV[Environment Context<br/>dir, git, platform, date, refs]
        SKILLS[Skills Metadata<br/>22 skills → verbose descriptions]
        MCP[MCP Instructions<br/>5 servers → filtered by permissions]
        AGENT_PROMPT[Agent Custom Prompt<br/>from .opencode/agents/*.md]
    end

    subgraph "HYDRATION PROTOCOL (Post-Startup)"
        CODEX[OMEGA_CODEX.md<br/>MANDATORY read - 411 lines]
        ANCHORED[.opencode/anchored-summary.md<br/>Post-compaction recovery]
        AWARENESS[omega-hub_hivemind_get_awareness()<br/>Who is here?]
        GIT[git status + log --oneline -5]
    end

    subgraph "SESSION LIFECYCLE"
        WRAPPER[.opencode/wrapper.sh<br/>Session wrapper]
        HOOK[session_end.py<br/>Timestamp + Codex refresh]
    end

    GLOBAL --> RUNTIME
    AGENT_SPEC --> RUNTIME
    AGENTS_MD --> RUNTIME
    CLAUDE_MD --> RUNTIME
    GLOBAL_CFG --> RUNTIME
    
    BASE --> ASSEMBLY[Final System Prompt]
    ENV --> ASSEMBLY
    SKILLS --> ASSEMBLY
    MCP --> ASSEMBLY
    AGENT_PROMPT --> ASSEMBLY
    
    ASSEMBLY --> LLM[LLM.stream()]
    
    LLM --> HYDRATION
    HYDRATION --> CODEX
    HYDRATION --> ANCHORED
    HYDRATION --> AWARENESS
    HYDRATION --> GIT
    
    WRAPPER --> HOOK
    HOOK --> CODEX_REGEN[Regenerate OMEGA_CODEX.md]
```

---

## 🔍 Layer-by-Layer Analysis

### Layer 1: opencode.json Global Instructions (STATIC, ALWAYS INJECTED)

**Location**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json` lines 27-33

```json
"instructions": [
  "SOVEREIGN_MANDATES.md",
  "ORACLE_STACK.md",
  "docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md",
  "docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md",
  "CREDITS.md"
]
```

**Behavior** (per opencode V2 docs):
- Loaded once at session start
- Applied to **ALL agents** (primary + subagents)
- Combined with AGENTS.md discovery (not overridden)
- **Arrays are NOT merged** — highest-precedence config wins entirely
- V2 currently **does not resolve** these entries into instruction sources (WARNING in docs)

**Token Cost**: ~33,600 tokens (estimated)

### Layer 2: Agent-Specific Instructions (PER-AGENT)

**Location**: `opencode.json` → `agent.<name>.instructions[]`

| Agent | Instruction Files | Lines | Est. Tokens |
|-------|-------------------|-------|-------------|
| `makali` | `.opencode/agents/plan.md` | ? | ~2,000 |
| `jem` | `.opencode/agents/jem.md` | 165 | ~5,500 |
| `doom_guy` | `.opencode/agents/doom_guy.md`, `CREDITS.md` | 74+24 | ~3,300 |
| `roc_racoon` | `.opencode/agents/roc_racoon.md` | 100 | ~3,500 |
| `researcher` | `.opencode/agents/researcher.md` | 195 | ~6,500 |
| `kali` | `.opencode/agents/kali.md` | 81 | ~2,700 |
| `maat` | `.opencode/agents/maat.md` | ~80 | ~2,700 |
| `lilith` | `.opencode/agents/lilith.md` | ~80 | ~2,700 |
| `verity` | `.opencode/agents/verity.md` | 220 | ~7,300 |
| `node` | `.opencode/agents/node.md` | 120 | ~4,000 |
| `john_carmack` | `.opencode/agents/john_carmack.md`, `CREDITS.md` | 340+24 | ~12,000 |
| `grok_cli` | `.opencode/agents/grok_cli.md` | ? | ~2,000 |

**Critical Issue**: `doom_guy` and `john_carmack` **duplicate** `CREDITS.md` — already in global instructions!

### Layer 3: AGENTS.md Discovery (DYNAMIC, PROJECT-SCOPED)

**Mechanism** (per opencode V2):
1. Global: `~/.config/opencode/AGENTS.md`
2. Project: Upward scan from CWD to project root
3. **Combined** (not overridden) — global first, then project files toward root
4. Nested AGENTS.md discovered during `read`/`list` tool calls — injected chronologically

**Current State**: No AGENTS.md in project root (omega-engine/). The `.agents/AGENTS.md` is for Antigravity IDE only.

### Layer 4: SystemPrompt.Service Assembly (RUNTIME, PER-REQUEST)

**Source**: `packages/opencode/src/session/system.ts` (from websearch)

The final system prompt is assembled **per LLM request** with this structure:

```typescript
system = [
  // 1. Agent custom prompt OR Provider default prompt
  agent.prompt ? [agent.prompt] : SystemPrompt.provider(model),
  
  // 2. Additional system prompts (from caller)
  ...input.system,
  
  // 3. User message system prompt
  ...(input.user.system ? [input.user.system] : []),
].filter(x => x).join("\n")

// Plugin transformation (can modify/empty the array)
// Safety fallback: if empty, restore original

// Cache optimization: maintain [header, rest] 2-part structure
```

**Injected Components**:
1. **Environment Context** (always): Working directory, workspace root, git repo status, platform, date, project references
2. **Skills Metadata** (always, if skill permission allowed): 22 skills with verbose descriptions
3. **MCP Instructions** (always, filtered by permissions): 5 MCP servers → instructions
4. **Agent Custom Prompt** (from `.opencode/agents/*.md` frontmatter `prompt` field — NOT USED currently)

---

## 💧 Hydration Protocol (AGENTS.md §Session Startup)

**Mandatory Sequence** (from `OMEGA_CODEX.md` → `hydration_header.md`):

```
1. omega-hub_hivemind_get_awareness()     — Who is here?
2. git status && git log --oneline -5     — What is committed?
3. Read OMEGA_CODEX.md — FULL file        — You are doing this now
4. Read .opencode/anchored-summary.md     — What was I doing?
5. Present a rehydration report. Pause. Await user direction.
```

**Enforcement**: 
- `kali.md` line 39: "Before any other action, you MUST read OMEGA_CODEX.md"
- `roc_racoon.md` references `AGENTS.md §Search Tool Protocol` but AGENTS.md doesn't exist
- **No automatic execution** — agent must self-initiate

**OMEGA_CODEX.md Generation** (Stack-Cat Protocol):
- `scripts/codex_cat.py` reads `scripts/groups.json`
- Concatenates 6 condensed reference files:
  1. `scripts/codex/ENGINE_CONDENSED.md` (109 lines)
  2. `scripts/codex/MANDATES_CONDENSED.md` (57 lines)
  3. `scripts/codex/AGENTS_CONDENSED.md` (114 lines)
  4. `ORACLE_STACK.md` (10 lines)
  5. `CREDITS.md` (24 lines)
  6. `docs/kb/REFINEMENT_PROTOCOL.md` (21 lines)
- **Total**: ~335 lines, ~11,000 tokens
- Auto-refreshed by `session_end.py` hook after every session
- Staleness check: `make check-codex-stale` (24h threshold)

---

## 📊 Token Audit — Exact Breakdown

| Source | Lines | Est. Tokens | Injected By | Scope |
|--------|-------|-------------|-------------|-------|
| **Global Instructions (opencode.json)** | | | | |
| SOVEREIGN_MANDATES.md | 239 | ~8,000 | opencode.json instructions[] | ALL agents |
| ORACLE_STACK.md | 10 | ~300 | opencode.json instructions[] | ALL agents |
| MASTER_SYNTHESIS... | 420 | ~14,000 | opencode.json instructions[] | ALL agents |
| SOVEREIGN_ARK_BLUEPRINT.md | 315 | ~10,500 | opencode.json instructions[] | ALL agents |
| CREDITS.md | 24 | ~800 | opencode.json instructions[] | ALL agents |
| **Agent-Specific** | | | | |
| roc_racoon.md | 100 | ~3,500 | agent.roc_racoon.instructions[] | roc_racoon only |
| kali.md | 81 | ~2,700 | agent.kali.instructions[] | kali only |
| researcher.md | 195 | ~6,500 | agent.researcher.instructions[] | researcher only |
| doom_guy.md | 74 | ~2,500 | agent.doom_guy.instructions[] | doom_guy only |
| john_carmack.md | 340 | ~11,300 | agent.john_carmack.instructions[] | john_carmack only |
| verity.md | 220 | ~7,300 | agent.verity.instructions[] | verity only |
| **Hydration Protocol** | | | | |
| OMEGA_CODEX.md | 411 | ~14,000 | Mandatory read (agent responsibility) | ALL agents |
| .opencode/anchored-summary.md | ~50 | ~1,700 | Mandatory read | ALL agents |
| **Runtime Assembly (per request)** | | | | |
| Environment context | ~30 | ~1,000 | SystemPrompt.environment() | ALL requests |
| Skills metadata (22 skills) | ~500 | ~17,000 | SystemPrompt.skills() | ALL requests |
| MCP instructions (5 servers) | ~200 | ~6,500 | SystemPrompt.mcp() | ALL requests |
| **TOTAL PER SESSION START** | **~3,300** | **~110,000** | | |

### Duplication Analysis

| Duplicated Content | Locations | Waste |
|-------------------|-----------|-------|
| CREDITS.md | Global instructions + doom_guy + john_carmack | 3x injection |
| Sovereign Mandates summary | MANDATES_CONDENSED (in Codex) + SOVEREIGN_MANDATES (global) | 2x |
| Agent fleet table | AGENTS_CONDENSED (in Codex) + individual agent files | 2x |
| Search protocol | AGENTS_CONDENSED + every agent file | 13x |
| Hivemind protocol | AGENTS_CONDENSED + every agent file | 13x |
| Delegation protocol | AGENTS_CONDENSED + every agent file | 13x |
| Response Provenance (M22) | AGENTS_CONDENSED + every agent file | 13x |

---

## 🎯 Optimization Targets

### Problem 1: Global Instructions = One Size Fits All
**Current**: 6 files (33,600 tokens) injected into **every** agent
**Reality**: 
- `roc_racoon` needs: Mandates (M14, M18, M19, M23), Mining patterns, Hivemind protocol
- `kali` needs: Mandates (M1, M2, M4, M7, M13, M14, M23), Sprint coordination, PIVOT_LOG
- `researcher` needs: Mandates (M1, M2, M4, M7, M13, M14, M23), Research protocol, HF integration
- `doom_guy` needs: Mandates (M14, M13, M18, M23), CREDITS.md, Heritage vetting
- `john_carmack` needs: Mandates, CREDITS.md, Architecture review patterns

### Problem 2: OMEGA_CODEX.md as Mandatory Read
**Current**: 411 lines (14,000 tokens) — every agent reads full file
**Reality**: 
- Condensed references already exist (ENGINE_CONDENSED, MANDATES_CONDENSED, AGENTS_CONDENSED)
- Agent only needs relevant sections
- Could be a **reference file** accessed via `read` tool on demand

### Problem 3: Skills Metadata Injected Every Request
**Current**: 22 skills × verbose descriptions = ~17,000 tokens per LLM call
**Reality**: 
- Skills are **tools** — should be loaded via `skill` tool when task matches description
- SystemPrompt.skills() injects ALL skills regardless of relevance
- opencode V2: "Skills provide specialized instructions... Use the skill tool to load a skill when a task matches its description"

### Problem 4: Agent Files Duplicate Codex Content
**Current**: Every agent file repeats Hivemind protocol, Search protocol, Delegation protocol, M22
**Reality**: 
- AGENTS_CONDENSED.md in Codex already has condensed versions
- Agent files should reference, not duplicate

---

## 🏗️ Optimization Proposal — Tiered/Lazy Loading Architecture

### Tier 0: Constitutional Core (ALWAYS INJECTED — ~2,000 tokens)
```
┌─────────────────────────────────────────────────────────────┐
│  SOVEREIGN_MANDATES_CONDENSED.md (57 lines)                │
│  - 25 laws as one-liner table with status                  │
│  - Links to full SOVEREIGN_MANDATES.md for details         │
│  - M1, M2, M4, M7, M9, M10, M11, M13, M14, M15, M18, M19, │
│    M22, M23, M24, M25 as non-negotiable baseline           │
└─────────────────────────────────────────────────────────────┘
```

### Tier 1: Role-Specific Context (INJECTED PER AGENT — ~3,000 tokens)
```
┌─────────────────────────────────────────────────────────────┐
│  Agent Definition File (.opencode/agents/<name>.md)        │
│  - ONLY agent-specific purpose, key mandates, heuristics   │
│  - NO duplicated protocols (reference Codex instead)       │
│  - NO full mandate text (reference Tier 0)                 │
└─────────────────────────────────────────────────────────────┘
```

### Tier 2: Lazy-Loaded References (ON-DEMAND via Tools)
```
┌─────────────────────────────────────────────────────────────┐
│  OMEGA_CODEX.md — Reference file, NOT injected             │
│  - Read via `read` tool when needed                        │
│  - Sections: Engine State, Mandates Status, Fleet, Mission │
│                                                                       │
│  SOVEREIGN_MANDATES.md — Full text, read on demand         │
│  MASTER_SYNTHESIS... — Historical context, read on demand  │
│  SOVEREIGN_ARK_BLUEPRINT.md — Roadmap, read on demand      │
│  CREDITS.md — Heritage registry, read on demand            │
│  AGENTS.md (if created) — Workflow protocols, read on demand│
└─────────────────────────────────────────────────────────────┘
```

### Tier 3: Skills & MCP (LAZY via Tool Invocation)
```
┌─────────────────────────────────────────────────────────────┐
│  Skills: Loaded via `skill` tool when task matches desc    │
│  - SystemPrompt.skills() → return MINIMAL list (name + desc)│
│  - Full instructions loaded only when `skill` tool called  │
│                                                                       │
│  MCP: Instructions filtered by permission, loaded on demand│
│  - Current: all MCP instructions injected every request    │
│  - Target: only relevant MCP tools' instructions           │
└─────────────────────────────────────────────────────────────┘
```

### Projected Token Savings

| Scenario | Current | Optimized | Savings |
|----------|---------|-----------|---------|
| **roc_racoon session start** | ~65,000 | ~8,000 | **88%** |
| **kali session start** | ~62,000 | ~7,500 | **88%** |
| **researcher session start** | ~68,000 | ~8,500 | **87%** |
| **Per-request overhead (skills+MCP)** | ~23,500 | ~2,000 | **91%** |

---

## 🛠️ Implementation Plan

### Phase 1: Restructure opencode.json (IMMEDIATE)

**File**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json`

```json
{
  "instructions": [
    "scripts/codex/MANDATES_CONDENSED.md"
  ],
  "agent": {
    "roc_racoon": {
      "instructions": [
        ".opencode/agents/roc_racoon.md"
      ]
    },
    "kali": {
      "instructions": [
        ".opencode/agents/kali.md"
      ]
    },
    // ... other agents with ONLY their specific file
  }
}
```

**Changes**:
1. Replace 5 global instruction files with `MANDATES_CONDENSED.md` only
2. Remove `CREDITS.md` from global (already in Codex)
3. Remove `CREDITS.md` from `doom_guy` and `john_carmack` agent instructions
4. Each agent gets ONLY their specific agent file

### Phase 2: Create AGENTS.md for Workflow Protocols (IMMEDIATE)

**File**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/AGENTS.md`

Create a project-root AGENTS.md containing:
- Hivemind-First Communication Protocol
- Sovereign Search Protocol (SR-V1)
- Delegation & Execution Protocol
- Response Provenance (M22)
- Session Startup Hydration Sequence
- **Reference** to OMEGA_CODEX.md for full details

This replaces duplicated protocol text in every agent file.

### Phase 3: Slim Agent Definition Files (IMMEDIATE)

**Pattern for each `.opencode/agents/<name>.md`**:

```markdown
---
description: "Sovereign Agent: <name>"
mode: "all"
temperature: 0.5
permission: { ... }
steps: 50
---

# 🔱 <name> — <Role Title>
**AP Token**: `AP-<NAME>-v1.0.0`
⬡ OMEGA ⬡ <NAME> ⬡ {session_model} ⬡ opencode ⬡ trc_<domain> ⬡ ACTIVE

**Purpose**: <One-line purpose>

## Role
- <Specific responsibilities>

## Key Mandates
- M<X> (<Name>): <Why relevant to this agent>
- M<Y> (<Name>): <Why relevant to this agent>

## Protocol References
- **Hydration**: Read `OMEGA_CODEX.md` → `hydration_header.md` sequence
- **Hivemind**: See `AGENTS.md` §Hivemind-First Communication
- **Search**: See `AGENTS.md` §Sovereign Search Protocol (SR-V1)
- **Delegation**: See `AGENTS.md` §Delegation & Execution
- **Provenance**: See `AGENTS.md` §Response Provenance (M22)

## Heuristic
<One-line guiding principle>
```

**Target**: ~40 lines per agent file (vs current 80-340 lines)

### Phase 4: Modify SystemPrompt.skills() for Lazy Loading (REQUIRES OPENCODE CORE CHANGE)

**Current** (packages/opencode/src/session/system.ts:105-117):
```typescript
skills: Effect.fn("SystemPrompt.skills")(function* (agent: Agent.Info) {
  if (Permission.disabled(["skill"], agent.permission).has("skill")) return
  const list = yield* skill.available(agent)
  return [
    "Skills provide specialized instructions...",
    Skill.fmt(list, { verbose: true }),  // FULL verbose descriptions
  ].join("\n")
})
```

**Proposed**: Minimal skill index in system prompt, full load via `skill` tool
```typescript
skills: Effect.fn("SystemPrompt.skills")(function* (agent: Agent.Info) {
  if (Permission.disabled(["skill"], agent.permission).has("skill")) return
  const list = yield* skill.available(agent)
  return [
    "Skills provide specialized instructions for specific tasks.",
    "Use the `skill` tool to load a skill when a task matches its description.",
    "Available skills: " + list.map(s => s.name).join(", "),
  ].join("\n")
})
```

**Note**: This requires opencode core modification. Workaround: Accept current behavior, optimize other layers first.

### Phase 5: Hydration Protocol Automation (OPTIONAL)

**Option A**: Add to agent definition frontmatter a `startup` hook (if opencode supports)
**Option B**: Create a `hydration` skill that agents load first
**Option C**: Document as mandatory manual step (current state)

**Recommendation**: Option C — keep explicit, sovereign control. The hydration sequence IS the agent's first sovereign act.

### Phase 6: Create Condensed Reference Files (DONE — Already Exist)

The `scripts/codex/*.md` condensed files already exist and are used by Codex. Ensure they stay current.

---

## 📋 Implementation Checklist

| Step | Action | File(s) | Effort | Priority |
|------|--------|---------|--------|----------|
| 1 | Create `AGENTS.md` at project root with shared protocols | `AGENTS.md` | 30 min | P0 |
| 2 | Update `opencode.json` global instructions → `MANDATES_CONDENSED.md` only | `opencode.json` | 5 min | P0 |
| 3 | Remove `CREDITS.md` from `doom_guy` and `john_carmack` agent instructions | `opencode.json` | 5 min | P0 |
| 4 | Slim `roc_racoon.md` to ~40 lines (reference protocols) | `.opencode/agents/roc_racoon.md` | 15 min | P0 |
| 5 | Slim `kali.md` to ~40 lines | `.opencode/agents/kali.md` | 15 min | P0 |
| 6 | Slim `researcher.md` to ~40 lines | `.opencode/agents/researcher.md` | 15 min | P0 |
| 7 | Slim `doom_guy.md` to ~40 lines | `.opencode/agents/doom_guy.md` | 15 min | P0 |
| 8 | Slim `john_carmack.md` to ~40 lines | `.opencode/agents/john_carmack.md` | 15 min | P0 |
| 9 | Slim `verity.md` to ~40 lines | `.opencode/agents/verity.md` | 15 min | P0 |
| 10 | Slim `maat.md`, `lilith.md`, `node.md`, `makali.md`, `jem.md`, `grok_cli.md` | respective files | 2 hr | P1 |
| 11 | Verify token reduction via session test | — | 30 min | P0 |
| 12 | Document new architecture in `docs/strategy/CONTEXT_INJECTION_ARCHITECTURE.md` | new file | 1 hr | P1 |

---

## 🔬 Validation Method

```bash
# Test 1: Measure tokens injected at session start
# (Use opencode's debug logging or count chars in system prompt)

# Test 2: Verify all agents can still function
# - roc_racoon: legacy mining + idea intake
# - kali: sprint coordination + oversight
# - researcher: deep research + HF integration
# - doom_guy: heritage vetting
# - verity: compliance audit + soul distillation

# Test 3: Verify hydration protocol works
# - Compact session → restart → verify hydration sequence executes

# Test 4: Verify Codex still generates correctly
make codex && make check-codex-stale
```

---

## 📚 References

- **opencode V2 Instructions**: https://opencode.ai/v2/docs/instructions
- **opencode System Prompt Architecture**: https://www.opencodebook.xyz/en/chapter_06_agent_system/6.4_system_prompt_architecture
- **opencode AGENTS.md Discovery**: https://opencode.ai/docs/rules/
- **SessionPrompt Injection**: https://www.opencodebook.xyz/en/chapter_04_session_system/4.3_sessionprompt_entry_point
- **Agent-Specific Instructions Feature Request**: https://github.com/anomalyco/opencode/issues/10688

---

## 🏁 Conclusion

The current context injection system violates **M18 (Token Efficiency)** by injecting ~110,000 tokens per session start, with massive duplication across layers. The **tiered/lazy-loading architecture** reduces this to ~8,000 tokens (93% reduction) while preserving sovereign access to all reference materials via on-demand tool calls.

**Immediate wins** (Phases 1-3) require only configuration changes — no opencode core modifications. **Phase 4** (skills lazy loading) requires upstream opencode change but can be deferred.

The hydration protocol remains explicit and sovereign — agents choose when to hydrate, maintaining M15 (Sovereign Continuity) compliance.

---

*Investigation complete. Ready for implementation.*
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: nemotron-3-ultra-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
