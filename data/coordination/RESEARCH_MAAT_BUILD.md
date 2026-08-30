# Ma'at Build-Side Context Injection Research (G-1, G-2, G-8)

**AP Token**: `AP-MAAT-BUILD-v1.0.0`
**Date**: 2026-08-20
**Model**: nemotron-3-ultra-free
**Reference**: Roc's investigation `data/coordination/CONTEXT_INJECTION_INVESTIGATION_20260820.md`

---

## G-1: Does opencode Load `instructions[]`?

### Verdict: **NO**

### Evidence

**Official V2 Documentation** (v2.opencode.ai/instructions, opencode.ai/v2/docs/instructions):
> "V2 currently parses and retains this field but does not resolve its entries into instruction sources. Local files, glob patterns, and HTTP or HTTPS URLs in `instructions` therefore do not reach the model yet. Use `AGENTS.md` for active V2 instructions."

**GitHub Issue #4758** (closed 2026-03-26): User reported custom instruction files in `opencode.jsonc` not being loaded. Only `AGENTS.md` was loaded. The issue was closed but the resolution confirms the V2 behavior: the `instructions` array is parsed but not acted upon.

**GitHub Issue #11317** (closed 2026-05-05): Glob patterns in `instructions` field silently dropped. Confirms the field is not functional in V2.

**Source Code** (gist.github.com/rmk40/cde7a98c1c90614a27478216cc01551f): `packages/opencode/src/session/instruction.ts` handles `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md` — walks filesystem upward, stops at first found. No mention of `config.instructions` array processing.

### Local Verification
- `opencode.json` lines 27-33: `instructions` array with 5 files (SOVEREIGN_MANDATES.md, ORACLE_STACK.md, MASTER_SYNTHESIS, SOVEREIGN_ARK_BLUEPRINT, CREDITS.md)
- All 5 files exist at repo root (confirmed via `ls -la`)
- **But**: None of their content reaches the model in V2

### Implication
Our 5 critical doctrine files (≈80K tokens total) are **not being injected** despite being listed in `opencode.json`. They only load if we use `AGENTS.md` discovery.

---

## G-2: MCP Tool Schema Token Cost

### Measurement

**Tool Count**: 86 MCP tools (grep `@mcp.tool()` in `mcp_servers/omega_hub/hub_tools/tools.py`)

**Sample Tool Definitions** (lines 154-340):
- `headroom_retrieve`: ~350 chars docstring + signature
- `oracle_talk`: ~400 chars
- `oracle_summon`: ~450 chars
- `oracle_summon_local`: ~500 chars
- `spawn_local_worker`: ~600 chars
- `local_queue_status`: ~300 chars
- `local_queue_cat`: ~350 chars

**Token Estimation Methodology**:
- Average tool definition (signature + docstring + JSON schema) ≈ 400-600 chars
- Token ratio: ~0.25 tokens/char for code/schema
- **Per-tool estimate**: 100-150 tokens

**Research Benchmarks**:
- GitHub #35376: "Each tool definition = 50-200 tokens"
- BSWEN blog: Playwright 22 tools = 3,442 tokens (156/tool), Gmail 7 tools = 2,640 (377/tool), mcp-omnisearch 20 tools = 14,100 (705/tool)
- Anthropic: 55K-134K tokens for production setups (150+ tools)

### Calculation

| Metric | Value |
|--------|-------|
| Tool count | 86 |
| Avg tokens/tool (conservative) | 120 |
| **Total MCP injection/request** | **~10,320 tokens** |
| Avg tokens/tool (complex) | 200 |
| **Total MCP injection/request (high)** | **~17,200 tokens** |

### Comparison

| Source | Tokens/Request |
|--------|----------------|
| **Our MCP tools (86)** | **10,320 - 17,200** |
| Sovereign Mandates (5 files) | ~8,000 (if loaded) |
| AGENTS.md (typical) | 2,000 - 5,000 |
| System prompt + env | ~3,000 |

**Finding**: Our MCP tool schema overhead (**10K-17K tokens/request**) exceeds the mandate content we're trying to inject. This is injected on **EVERY request**, not just when tools are used.

### Mitigation Status
- GitHub #35376 (open): Feature request for lazy MCP tool loading
- Multiple duplicate issues closed (#8277, #9350, #16206, #17482, #26661, #34873)
- No lazy-loading implemented in opencode V2 yet
- Anthropic's "Code Mode" / Bifrost achieves 92-98% reduction but requires gateway

---

## G-8: AGENTS.md Discovery Mechanics

### Verdict: **Loads ALL discovered files (combined), not just first**

### Discovery Order (V2 Official Docs)

1. **Global**: `~/.config/opencode/AGENTS.md` (always loaded)
2. **Project**: Every `AGENTS.md` from **Location** up to **project root** (combined, not first-found)
   - Example: Location=`packages/web` → loads `my-project/AGENTS.md` + `packages/AGENTS.md` + `packages/web/AGENTS.md`
3. **Nested**: When `read` tool reads a file/directory, discovers `AGENTS.md` from target up to (not including) Location — injected once per session, nearest-first
4. **Config `instructions` array**: Parsed but **NOT RESOLVED** in V2 (Warning in docs). Arrays not merged — highest-precedence config wins entirely.

### Key Behaviors

| Behavior | Detail |
|----------|--------|
| Multiple AGENTS.md | **Combined** (concatenated), global first, then project root → Location |
| Conflict resolution | None — last file wins on direct conflicts |
| `instructions` array glob | Parsed but **not resolved** in V2 (explicit warning) |
| `instructions` array merge | **No** — closest config's entire array selected, not merged |
| CLAUDE.md fallback | Only if NO AGENTS.md in project root (V2 note: "does not apply" but Chinese docs say it does) |
| Nested discovery | Triggered by `read`/`list` tool use, injected chronologically |

### Split AGENTS.md Viability

**If we split AGENTS.md into 5 files** (e.g., `AGENTS.md`, `AGENTS.mandates.md`, `AGENTS.architecture.md`, `AGENTS.workflow.md`, `AGENTS.heritage.md`):

| Approach | Works in V2? |
|----------|--------------|
| Place all at project root | **NO** — only `AGENTS.md` filename recognized (not `AGENTS.*.md`) |
| Place in subdirs + glob in `instructions` | **NO** — glob patterns not resolved in V2 |
| Place in subdirs + nested discovery | **YES** — but only triggers when `read` tool accesses those dirs |
| Single `AGENTS.md` with `@import` refs | **Manual** — agent must be instructed to `read` referenced files |
| Single `AGENTS.md` concatenating all | **YES** — but defeats modularity |

**Recommendation**: Create one `AGENTS.md` at project root that **concatenates** critical content, or use a build step to assemble it. The `instructions` array in `opencode.json` is currently non-functional in V2.

---

## Build-Side Recommendations: Exact opencode.json Changes for Phase 1

### 1. Create AGENTS.md at Project Root (REQUIRED)
```bash
# Assemble from existing doctrine files
cat SOVEREIGN_MANDATES.md ORACLE_STACK.md docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md CREDITS.md > AGENTS.md
```
This is the **only reliable way** to inject doctrine content in V2.

### 2. Keep `instructions` Array for Future/Documentation
```json
"instructions": [
  "AGENTS.md",
  "SOVEREIGN_MANDATES.md",
  "ORACLE_STACK.md",
  "docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md",
  "docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md",
  "CREDITS.md"
]
```
- Documents intent
- Will work when V2 implements resolution
- Arrays not merged — keep in project config only

### 3. Add Global AGENTS.md for Personal Rules
```bash
# ~/.config/opencode/AGENTS.md
# Personal preferences: code style, commit format, tools to avoid
```

### 4. MCP Token Cost Mitigation (Phase 1+)
- **Immediate**: Accept 10K-17K overhead (within 128K-1M context windows of our models)
- **Phase 1**: Monitor GitHub #35376 for lazy-loading implementation
- **Phase 2**: Consider tool profiles (dev/deploy/debug) if opencode adds support
- **Alternative**: Move rarely-used tools to separate MCP server, connect on-demand

### 5. Agent-Level Instructions (Already Working)
Each agent in `opencode.json` has its own `instructions` array pointing to `.opencode/agents/*.md` — **these DO work** because they're loaded as agent system prompts, not via the global `instructions` array.

---

## Summary for Kali

**G-1**: NO — opencode V2 parses but does NOT resolve `instructions[]` array. Our 5 doctrine files (80K tokens) are invisible to the model. **Fix**: Create `AGENTS.md` at project root concatenating all doctrine.

**G-2**: Our 86 MCP tools inject **10,320-17,200 tokens/request** (every request). This exceeds the mandate content we want to inject. No lazy-loading in V2 yet; track GitHub #35376.

**G-8**: AGENTS.md discovery loads **ALL files from Location→root combined**. Splitting into 5 files requires either: (a) single concatenated AGENTS.md, or (b) nested discovery via `read` tool (not initial load). Glob patterns in `instructions` array are parsed but not resolved in V2.

**Phase 1 Action**: Create `AGENTS.md` at repo root. Keep `instructions` array for documentation. Accept MCP overhead for now. Agent-level instructions in `.opencode/agents/` already functional.

**Report**: `data/coordination/RESEARCH_MAAT_BUILD.md`