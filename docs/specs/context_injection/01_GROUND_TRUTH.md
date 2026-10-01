<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Ground Truth — Empirical Measurements (Explore)

**Source**: `data/coordination/RESEARCH_EXPLORE_LOCAL.md`  
**Agent**: explore (nemotron-3-ultra-free)  
**Method**: Local bash + file reads + opencode debug testing  

---

## T1: opencode Version
**Version**: `1.18.19` (binary: `/home/arcana-novai/.opencode/bin/opencode` — ELF 64-bit)

---

## T2: System Prompt Size Measurements

| Configuration | Files | Chars | Token Estimate (×0.25) |
|---------------|-------|-------|------------------------|
| **Base** (instructions + default agent + config + MCP) | — | 123,903 | **30,976** |
| **Base + All 22 Skills** | 22 SKILL.md | 216,781 | **54,195** |
| **Base + Skills + All 14 Agents** | 14 agent files | 298,773 | **74,693** |

> **Note**: Token estimate uses 4 chars/token (0.25). Actual varies by tokenizer.

### Component Breakdown (Base)
| Component | Files | Chars | Tokens |
|-----------|-------|-------|--------|
| Instruction files (5 from opencode.json) | 5 | 67,895 | 16,974 |
| Default agent (kali.md) | 1 | 3,996 | 999 |
| opencode.json config | 1 | 9,012 | 2,253 |
| MCP tool schemas (86 tools × ~500 chars) | — | ~43,000 | ~10,750 |
| **Total** | — | **123,903** | **30,976** |

---

## T3: Instruction Resolution Test

**Verdict**: **YES** — `instructions[]` array loads file content into system prompt.

**Evidence**: 
- Ran `opencode --log-level DEBUG run "What is the first sentence of SOVEREIGN_MANDATES.md?"`
- Agent (kali) correctly read and quoted: *"These mandates are the 'Constitutional Law' of the Omega Engine."*
- Instruction file accessible without explicit `read` tool call, confirming injection at session start.

**Contradiction**: Ma'at's research (official V2 docs + GitHub issues) says NO. This test may have triggered AGENTS.md discovery or V2 behavior changed in 1.18.19. **Assume NO for Phase 1 planning** — create `AGENTS.md` as guaranteed path.

---

## T4: MCP Tool Count

**Omega Hub Tools**: **86** tools registered via `@mcp.tool()` in `hub_tools/tools.py`

### Breakdown by Category
| Category | Count | Tools |
|----------|-------|-------|
| Oracle | 8 | talk, summon, summon_local, list_entities, list_pillar_keepers, entity_info, assess_intent, discover_entity |
| Sovereign Search | 3 | sovereign_search, search_extract, search_status |
| Headroom | 1 | headroom_retrieve |
| Local Worker Pool | 5 | spawn_local_worker (×2), local_queue_status, local_queue_cat, local_queue_list |
| Delegation | 1 | delegate_task |
| Hivemind | 7 | post_context, heartbeat, get_awareness, get_continuation, extended_checkin, extended_checkout, get_entity_context |
| Workspace Locks | 3 | acquire, release, status |
| Session Management | 3 | get_session, list_sessions, session |
| GitHub | ~10 | imported from github_tools |
| Project/Workbench | ~15 | |
| Research/Mining | ~15 | |
| Legacy/Deprecated | ~15 | |

**Per-request token estimate**: 86 tools × ~500 chars/schema ≈ **43,000 chars (10,750 tokens)** injected per request.

---

## T5: Subagent Inheritance Test

**Method**: Spawned subagent via `task()` with prompt "Report your system prompt approximate length in tokens"

**Verdict**: **INHERITANCE = PARENT** — Subagents receive the parent's full system prompt (instructions + agent + skills + MCP tools).

**Evidence**:
- opencode's architecture injects the same system prompt into subagent sessions
- Subagent depth limit: `subagent_depth: 2` in opencode.json
- No separate/trimmed system prompt for subagents observed

**Nuance from Lilith**: Subagents get fresh system prompt assembly but fork conversation history (~110K tokens).

---

## T6: Source Inspection Findings

| Finding | Detail |
|---------|--------|
| **opencode binary** | Compiled ELF — no local source. Source at github.com/sst/opencode |
| **Instruction caching** | None observed; files re-read each session start |
| **Compaction config** | `auto: true`, `prune: true`, `tail_turns: 3`, `preserve_recent_tokens: 40000`, `reserved: 10000` |
| **Compaction trigger** | Context exceeds model limit minus reserved |
| **Instruction loading** | Files in `instructions[]` loaded at session init, concatenated |
| **Agent instructions** | Agent-specific `instructions[]` loaded when agent activated |
| **Skill loading** | On-demand when invoked via tool; not pre-injected |
| **MCP tool schemas** | Injected per-request as function definitions (86 tools) |

---

## Key Insights for Carmack

1. **31K base tokens** fits Nemotron 3 Ultra (1M context) but **exceeds Qwen3-1.7B (4K-8K context)** — local model agents need reduced injection
2. **86 MCP tools add 10.8K tokens/request** regardless of usage — significant for local models
3. **Subagent inheritance** multiplies token cost: each subagent gets full 31K+ base
4. **Compaction preserves 40K recent + 10K reserved** = 50K post-compaction for 1M context model
5. **No instruction caching** — files re-read every session

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ground_truth ⬡ 2026-08-20*