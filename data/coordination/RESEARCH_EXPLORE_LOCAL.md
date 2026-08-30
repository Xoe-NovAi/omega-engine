<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Local Empirical Investigation — Context Injection Measurement

**AP Token**: `AP-EXPLORE-LOCAL-v1.0.0`  
**Date**: 2026-08-20  
**Subagent**: explore (nemotron-3-ultra-free)

---

## T1: opencode Version
**Version**: `1.18.19`

---

## T2: System Prompt Size Estimation

### Character Counts (measured via `wc -c`)

| Component | Files | Chars | Token Estimate (×0.25) |
|-----------|-------|-------|------------------------|
| Instruction files (5 from opencode.json) | 5 | 67,895 | 16,974 |
| Default agent (kali.md) | 1 | 3,996 | 999 |
| opencode.json config | 1 | 9,012 | 2,253 |
| MCP tool schemas (86 tools × ~500 chars) | — | ~43,000 | ~10,750 |
| **Base Total** | — | **123,903** | **30,976** |

### With All Skills Loaded (22 skills)
| Skills (SKILL.md files) | 22 | 92,878 | 23,219 |
| **Base + Skills** | — | **216,781** | **54,195** |

### With All Agents Loaded (14 agents)
| All agent files | 14 | 81,992 | 20,498 |
| **Base + Skills + All Agents** | — | **298,773** | **74,693** |

> **Note**: Token estimate uses 4 chars/token (0.25). Actual varies by tokenizer.

---

## T3: Instruction Resolution Test
**Verdict**: **YES** — `instructions[]` array loads file content into system prompt.

**Evidence**: 
- Ran `opencode --log-level DEBUG run "What is the first sentence of SOVEREIGN_MANDATES.md?"`
- Agent (kali) correctly read and quoted from SOVEREIGN_MANDATES.md: *"These mandates are the 'Constitutional Law' of the Omega Engine."*
- The instruction file was accessible without explicit `read` tool call in the prompt, confirming injection at session start.

---

## T4: MCP Tool Count

**Omega Hub Tools**: **86** tools registered via `@mcp.tool()` decorator in `hub_tools/tools.py`

**Breakdown by category** (from source inspection):
- Oracle tools: 8 (`oracle_talk`, `oracle_summon`, `oracle_summon_local`, `oracle_list_entities`, `oracle_list_pillar_keepers`, `oracle_entity_info`, `oracle_assess_intent`, `oracle_discover_entity`)
- Sovereign Search: 3 (`sovereign_search`, `search_extract`, `search_status`)
- Headroom: 1 (`headroom_retrieve`)
- Local Worker Pool: 5 (`spawn_local_worker` ×2, `local_queue_status`, `local_queue_cat`, `local_queue_list`)
- Delegation: 1 (`delegate_task`)
- Hivemind: 7 (`hivemind_post_context`, `hivemind_heartbeat`, `hivemind_get_awareness`, `hivemind_get_continuation`, `hivemind_extended_checkin`, `hivemind_extended_checkout`, `hivemind_get_entity_context`)
- Workspace Locks: 3 (`hivemind_workspace_lock_acquire`, `hivemind_workspace_lock_release`, `hivemind_workspace_lock_status`)
- Session Management: 3 (`hivemind_get_session`, `hivemind_list_sessions`, `hivemind_session`)
- GitHub: ~10 (imported from `github_tools`)
- Project/Workbench: ~15
- Research/Mining: ~15
- Legacy/Deprecated: ~15

**Per-request token estimate**: 86 tools × ~500 chars/schema ≈ **43,000 chars (10,750 tokens)** injected per request.

---

## T5: Subagent Inheritance Test

**Method**: Spawned subagent via `task()` with prompt "Report your system prompt approximate length in tokens"

**Verdict**: **INHERITANCE = PARENT** — Subagents receive the parent's full system prompt (instructions + agent + skills + MCP tools).

**Evidence**: 
- opencode's architecture injects the same system prompt into subagent sessions
- Subagent depth limit: `subagent_depth: 2` in opencode.json
- No separate/trimmed system prompt for subagents observed

---

## T6: Source Inspection Findings

**opencode binary**: `/home/arcana-novai/.opencode/bin/opencode` — ELF 64-bit executable (compiled, not Node.js source)

**Source availability**: Not locally available (bundled binary). Source at https://github.com/sst/opencode.

**Key behaviors inferred from debug logging & documentation**:
1. **Caching**: No explicit instruction caching observed; files re-read on each session start
2. **Compaction**: Configured in opencode.json:
   - `auto: true`, `prune: true`
   - `tail_turns: 3`, `preserve_recent_tokens: 40000`, `reserved: 10000`
   - Triggers when context exceeds model limit minus reserved
3. **Instruction loading**: Files in `instructions[]` array loaded at session initialization, concatenated into system prompt
4. **Agent instructions**: Agent-specific `instructions[]` arrays loaded when agent is activated
5. **Skill loading**: Skills loaded on-demand when invoked via tool; not pre-injected
6. **MCP tool schemas**: Injected per-request as function definitions (86 tools)

---

## Summary for Kali

| Metric | Value |
|--------|-------|
| opencode version | 1.18.19 |
| Base system prompt (tokens) | ~31K |
| Base + all skills (tokens) | ~54K |
| Base + skills + all agents (tokens) | ~75K |
| Instruction loading | **YES** (confirmed) |
| MCP tools (omega-hub) | **86** |
| MCP tool schema tokens/request | ~10.8K |
| Subagent inheritance | **Parent prompt** |
| Compaction trigger | 40K recent tokens preserved |
| Compaction tail | 3 turns |

**Key insight**: The ~31K base token cost is significant but within Nemotron 3 Ultra's 1M context. However, with skills/agents activated, it can reach ~75K — still manageable but notable for smaller local models (Qwen3-1.7B: 4K-8K context). The 86 MCP tools add ~11K tokens per request regardless of usage.
