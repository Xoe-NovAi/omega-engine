<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Context Injection Phase 1 Implementation Spec

**AP Token**: `AP-MAAT-CI-PHASE1-SPEC-v1.0.0`  
**Status**: CARMACK-REVIEWED — MODIFIED PER `CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md`  
**Authority**: `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 (supersedes Ark §4)  
**Workstream**: `CONTEXT-INJECTION` in `ACTIVE_SPRINT.json`  
**Owner**: Kali (execution), Ma'at (N3 verification)  
**Phase**: 1 — Config-Only, This Week (2026-08-20 to 2026-08-27)  

---

## Executive Summary

This spec is the **single source of truth** for Phase 1 implementation. It incorporates all modifications from the Carmack Review (2026-08-20):

| Carmack Modification | Status | Section |
|---------------------|--------|---------|
| AGENTS.md condensation → `MANDATES_CONDENSED.md` (57 lines, ~1.5K tokens) | **REQUIRED** | §1 |
| Tool profile stubs in `opencode.json` | **REQUIRED** | §2 |
| Tier 0 model matrix: Qwen3-4B / Qwen3-4B-Thinking / Qwen3-1.7B | **REQUIRED** | §2 |
| Compaction buffer: `buffer: 50000`, `keep.tokens: 20000` | **REQUIRED** | §2 |
| Disable auto-compaction for local models (`OPENCODE_DISABLE_AUTOCOMPACT=1`) | **REQUIRED** | §2 |
| Move `maat`/`lilith` to local (Qwen3-4B-Thinking) | **REQUIRED** | §2 |
| Sovereign compaction plugin (pre-compaction hook) | **REQUIRED** | §3 |
| Skills opt-in: only 3 core skills auto-load | **REQUIRED** | §4 |
| Verification tests with exact commands | **REQUIRED** | §5 |
| Rollback plan for every change | **REQUIRED** | §6 |

**Token Budget Target (Modified Phase 1)**:
| Tier | Component | Tokens |
|------|-----------|--------|
| **0 (Pinned)** | MANDATES_CONDENSED.md (1.5K) + MCP schemas (profile: 1.5K) + env (3K) | **~6K** |
| **1 (Role/Session)** | Agent file (1K) + core skills metadata (3 × 50) | **~2K** |
| **2 (Dynamic)** | Budgeted retrieval + lazy skill docs | **8K budget** |
| **3 (Observation)** | Current turn | **2K** |
| **TOTAL** | | **~18K base** (fits Qwen3-4B 8K-16K with headroom) |

---

## 1. MANDATES_CONDENSED.md Creation

### 1.1 File Location
```
/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/MANDATES_CONDENSED.md
```
(Repo root, alongside `AGENTS.md`, `SOVEREIGN_MANDATES.md`, `opencode.json`)

### 1.2 Exact Content (57 lines, ~1.5K tokens)

```markdown
# Sovereign Mandates — Condensed (Tier 0 Pinned Context)

**Source**: `SOVEREIGN_MANDATES.md` (v3.8.0, 27 mandates)  
**Purpose**: Tier 0 injection for local models (Qwen3-4B, 8K-16K context)  
**Full Detail**: See `SOVEREIGN_MANDATES.md` for rationale, patterns, enforcement.

---

| # | Mandate | One-Liner | Status |
|---|---------|-----------|--------|
| M1 | AnyIO Absolute | All async uses AnyIO; never `asyncio` directly; wrap blocking I/O in `anyio.to_thread.run_sync` | ✅ |
| M2 | Engine-Stack Firewall | Core (`src/omega/`, `config/omega.yaml`) separate from Stacks (`config/wads/`); no stack logic in core | ✅ |
| M3 | Iris Constant | Iris is messenger bridge, NOT a Node; no Node slot assignment | ✅ |
| M4 | Sequentiality | Plan → Verify → Execute loop for architectural changes; no cowboy coding | ✅ |
| M5 | Gnosis Preservation | L1→L2→L3 distillation every session; write to `proposed_lessons.yaml` | ✅ |
| M6 | Podman Sovereignty | `UserNS=keep-id` + `User=1000` for Quadlets; `:U` flag FORBIDDEN on shared volumes | ✅ |
| M7 | Local-First | Local inference PRIMARY (native-gguf→lmster→Ollama); cloud FALLBACK only | ⚠️→✅ |
| M8 | Zero Telemetry | No external analytics/phone-home; local observability in `data/` acceptable | ✅ |
| M9 | Error Integrity | Typed, traceable errors; no bare `except:`; `OmegaError` subtypes at API boundaries | ✅ |
| M10 | Fleet Integrity | Lean, slot-constrained agents (≤14); map to Nodes/Lattice before new agent | ✅ |
| M11 | Soul Integrity | L1→L2→L3 pipeline mandatory; `proposed_lessons.yaml` blind staging; Scribe executes | ✅ |
| M12 | Queue Integrity | Every request = atomic contract; terminal states only; dead-letter for failures | ⚠️ |
| M13 | Temple-Grade | T1-T11 gates mandatory; `make temple-grade` must pass; CI gates on T3/T5/T6/T8/T9/T10 | ✅ |
| M14 | Heritage Vetting | `[id-soft:]` tags require vet record in `HERITAGE_VET_LOG.md`; min 7/10; Qualification Gate | ✅ |
| M15 | Sovereign Continuity | `session_gnosis.md` + `SESSION_ANCHOR.md` hydration; no reliance on `/compact` | ✅ |
| M16 | Modularization | Core portable; no hardcoded paths/env assumptions; Hub modularization pattern | ✅ |
| M17 | Cognitive Integrity | Skeptical Verifier detects contradictions; Qliphoth taxonomy for loops | ✅ |
| M18 | Token Efficiency | No waste; but sane-boundary: precision > brevity; high-fidelity context required | ✅ |
| M19 | Adversarial Alchemy | Weaponize constraints; but sane-boundary: simple bugs = simple fixes; no over-engineering | ✅ |
| M20 | SomaticState Serialization | `llama_copy_state_data`/`llama_set_state_data` via ctypes + `anyio.to_thread` | ✅ |
| M21 | Gate Integrity | Contract tests for all typed returns; `isinstance(result, ExpectedType)` verified | ✅ |
| M22 | Response Provenance | Log actual provider (`GenerateResult.provider_name`), not configured intent | ✅ |
| M23 | Failure Integrity | No soft-failures; `[TOOL-CHAIN-COLLAPSE]` on mandatory tool failure; log to `SYSTEM_FAILURE_LOG.md` | ✅ |
| M24 | Venv Sovereignty | All Python in `.venv`; no `--break-system-packages`; no `pip install --user` | ✅ |
| M25 | Streaming Resilience | Chunk timeout 30s + heartbeat (continue); total timeout 5min (graceful fallback) | ✅ |
| M26 | Doc Standards | `make doc-llm-validate` mandatory; LLM-friendly docs; `docs/standards/` guides | ✅ |
| M27 | Tracking Integrity | 5-Tier architecture; `GAP_REGISTRY.json` authority; status enum strict; `validate_tracking_state.py` CI | ✅ |

---

**Legend**: ✅ = Compliant | ⚠️ = Partial (see full mandate) | ❌ = Non-compliant  
**Full Text**: `SOVEREIGN_MANDATES.md` | **Vetting Log**: `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`
```

### 1.3 Verification
```bash
# Line count
wc -l MANDATES_CONDENSED.md
# Expected: 57 lines

# Token estimate (chars / 4)
wc -c MANDATES_CONDENSED.md
# Expected: ~6000 chars = ~1.5K tokens
```

---

## 2. opencode.json Updates (Exact Diff)

### 2.1 Current State (from Phase 1 Plan)
```json
{
  "instructions": [
    "SOVEREIGN_MANDATES.md",
    "ORACLE_STACK.md",
    "docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md",
    "docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md",
    "CREDITS.md"
  ],
  "compaction": {
    "auto": true,
    "prune": true,
    "tail_turns": 3,
    "preserve_recent_tokens": 40000,
    "reserved": 10000
  },
  "plugin": [
    "opencode-antigravity-auth@latest",
    "opencode-sessions-explorer",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/error-capture.ts",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/awareness.ts"
  ],
  "agent": {
    "kali": { "mode": "all", "temperature": 0.5, "steps": 50 },
    "researcher": { "mode": "all", "temperature": 0.5, "steps": 100 },
    "maat": { "mode": "all", "temperature": 0.5 },
    "lilith": { "mode": "all", "temperature": 0.5 },
    "node": { "mode": "all", "temperature": 0.5 },
    "verity": { "mode": "all", "temperature": 0.5 }
  }
}
```

### 2.2 Target State (Carmack-Modified)

```json
{
  "instructions": ["AGENTS.md"],
  "compaction": {
    "auto": true,
    "prune": true,
    "tail_turns": 5,
    "preserve_recent_tokens": 80000,
    "reserved": 20000,
    "buffer": 50000,
    "keep": { "tokens": 20000 }
  },
  "plugin": [
    "opencode-antigravity-auth@latest",
    "opencode-sessions-explorer",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/error-capture.ts",
    "file:///home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/plugin/awareness.ts",
    "file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts"
  ],
  "agent": {
    "kali": {
      "mode": "all",
      "model": "opencode/nemotron-3-ultra-free",
      "variant": "high",
      "temperature": 0.3,
      "steps": 50,
      "toolProfile": "deploy"
    },
    "researcher": {
      "mode": "all",
      "model": "lmstudio/qwen3-4b-thinking",
      "variant": "high",
      "temperature": 0.1,
      "steps": 100,
      "toolProfile": "research"
    },
    "maat": {
      "mode": "all",
      "model": "lmstudio/qwen3-4b-thinking",
      "variant": "medium",
      "temperature": 0.2,
      "toolProfile": "dev"
    },
    "lilith": {
      "mode": "all",
      "model": "lmstudio/qwen3-4b-thinking",
      "variant": "high",
      "temperature": 0.3,
      "toolProfile": "run"
    },
    "node": {
      "mode": "all",
      "model": "lmstudio/qwen3-1.7b",
      "variant": "low",
      "temperature": 0.1,
      "steps": 20,
      "toolProfile": "debug"
    },
    "verity": {
      "mode": "subagent",
      "model": "lmstudio/qwen3-1.7b",
      "variant": "low",
      "temperature": 0.0,
      "prompt": "{file:.opencode/agents/verity.md}",
      "permission": { "edit": "deny", "bash": "deny", "skill": "deny" },
      "hidden": true,
      "toolProfile": "audit"
    }
  }
}
```

### 2.3 Key Changes Explained (Carmack-Modified)

| Change | Carmack Rationale |
|--------|-------------------|
| `instructions: ["AGENTS.md"]` | Only reliable injection path in V2 (Ma'at confirmed) |
| `compaction.buffer: 50000`, `keep.tokens: 20000` | 1M context model needs larger buffer; Phase 2 will add dynamic per-model buffer |
| `compaction.tail_turns: 5` | More recent turns preserved for continuity |
| Add `sovereign-compaction` plugin | Pre-compaction hook injects mandates/entity/phase/anchor |
| `kali.model: opencode/nemotron-3-ultra-free` | Cloud for oversight quality floor (architectural decisions) |
| `researcher.model: lmstudio/qwen3-4b-thinking` | Tier 0 executor — Qwen3-4B-Thinking (8K-16K context) |
| `maat.model: lmstudio/qwen3-4b-thinking` | **MODIFIED**: Move build agent local (Q5.1 verdict) |
| `lilith.model: lmstudio/qwen3-4b-thinking` | **MODIFIED**: Move run agent local (Q5.1 verdict) |
| `node.model: lmstudio/qwen3-1.7b` | Tier 0 critic/verity — Qwen3-1.7B (4K-8K context) |
| `verity.mode: subagent` + restrictive permissions | Isolation for audit agent — no parent context inheritance |
| `verity.hidden: true` | Prevents accidental `@-invocation` |
| `toolProfile` stubs on all agents | **MODIFIED**: Documents intent for Phase 2 MCP domain split (Q2.1) |

### 2.4 Tool Profile Values (Phase 1 Stubs)

| Agent | toolProfile | Intended MCP Server (Phase 2) |
|-------|-------------|-------------------------------|
| kali | `deploy` | `github-hub` + `hivemind-hub` |
| researcher | `research` | `research-hub` + `oracle-hub` |
| maat | `dev` | `oracle-hub` + `hivemind-hub` |
| lilith | `run` | `hivemind-hub` + `oracle-hub` |
| node | `debug` | `oracle-hub` + `hivemind-hub` |
| verity | `audit` | `oracle-hub` (read-only) |

> **Note**: `toolProfile` is a config stub in Phase 1. OpenCode does not yet support tool profiles. Phase 2 implements MCP server split and maps profiles to servers.

### 2.5 Environment Variable for Local Models

Add to shell profile (`.bashrc`, `.zshrc`, or `.env`):
```bash
export OPENCODE_DISABLE_AUTOCOMPACT=1
```
This disables auto-compaction for local model agents until Phase 2 dynamic buffer plugin is ready (Carmack Q3.1).

---

## 3. Sovereign Compaction Plugin

### 3.1 File Location
```
/home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts
```

### 3.2 Directory Creation
```bash
mkdir -p /home/arcana-novai/.config/opencode/plugin
```

### 3.3 Full TypeScript Implementation

```typescript
// sovereign-compaction.ts
// Phase 1: Pre-compaction hook injecting sovereign context
// Hook: experimental.session.compacting (fires BEFORE summary generation)
// Carmack Q3.3: Plugin = defense-in-depth; Hydration Engine (Phase 2) = primary checkpoint

import type { Plugin } from "@opencode-ai/plugin";

export const SovereignCompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Read environment variables set by Omega Engine launch scripts
      const entity = process.env.OMEGA_ENTITY || "unknown";
      const phase = process.env.OMEGA_PHASE || "unknown";
      const sessionAnchor = "data/coordination/SESSION_ANCHOR.md";

      // Inject sovereign mandates (condensed) + active context
      // This survives compaction because it's injected INTO the compaction prompt
      output.context.push(`
## SOVEREIGN MANDATES (Must Survive Compaction)
- M1 AnyIO Absolute | M7 Local-First | M11 Soul Integrity | M15 Continuity | M23 Failure Integrity
- Active Entity: ${entity}
- Active Phase: ${phase}
- Session Anchor: ${sessionAnchor}
      `.trim());
    }
  };
};
```

### 3.4 Registration
Added to `opencode.json` plugin array (see §2.2 target state).

### 3.5 How It Works
1. OpenCode triggers compaction when token usage exceeds threshold
2. Before generating summary, OpenCode fires `experimental.session.compacting` hook
3. Plugin reads `OMEGA_ENTITY`, `OMEGA_PHASE` from environment
4. Plugin pushes sovereign context block into `output.context`
5. Compaction summary INCLUDES this block → survives into compressed context
6. Next session hydrates from `SESSION_ANCHOR.md` (M15)

### 3.6 Environment Variables (Set by Launch Scripts)
```bash
# Set by omega CLI / launch wrapper
export OMEGA_ENTITY="kali"        # or researcher, maat, lilith, node, verity
export OMEGA_PHASE="PUBLIC-DEBUT-01"  # from ACTIVE_SPRINT.json sprint_id
```

---

## 4. Skills Opt-In Configuration

### 4.1 Skill Inventory (22 Total)

| # | Skill | Path | auto_load | Phase 1 Action |
|---|-------|------|-----------|----------------|
| 1 | **research** | `.opencode/skill/research/SKILL.md` | **true** | Keep |
| 2 | **spec-generator** | `.opencode/skill/spec-generator/SKILL.md` | **true** | Keep |
| 3 | **knowledge-miner** | `.opencode/skill/knowledge-miner/SKILL.md` | **true** | Keep |
| 4 | legacy-pattern-miner | `.opencode/skill/legacy-pattern-miner/SKILL.md` | false | Set false |
| 5 | blitz-tunnel | `.opencode/skill/blitz-tunnel/SKILL.md` | false | Set false |
| 6 | blitz-validate | `.opencode/skill/blitz-validate/SKILL.md` | false | Set false |
| 7 | git-secret-scrub | `.opencode/skill/git-secret-scrub/SKILL.md` | false | Set false |
| 8 | hf-cli | `.opencode/skill/hf-cli/SKILL.md` | false | Set false |
| 9 | omega-doc-architect | `.opencode/skill/omega-doc-architect/SKILL.md` | false | Set false |
| 10 | pr-readiness-checker | `.opencode/skill/pr-readiness-checker/SKILL.md` | false | Set false |
| 11 | provider-validator | `.opencode/skill/provider-validator/SKILL.md` | false | Set false |
| 12 | sovereign-refinement-protocol | `.opencode/skill/sovereign-refinement-protocol/SKILL.md` | false | Set false |
| 13 | sovereign-search | `.opencode/skill/sovereign-search/SKILL.md` | false | Set false |
| 14 | customize-opencode | (built-in) | N/A | N/A |

> **Note**: Only 13 skills in `.opencode/skill/` + 1 built-in = 14 total. The Phase 1 Plan listed 22 but actual count is 14. Adjust accordingly.

### 4.2 Frontmatter Format (Exact)

Each `SKILL.md` must have this frontmatter:

```yaml
---
name: skill-name
description: One-line description
auto_load: true|false
---
```

### 4.3 Exact Edits Required

**Core Skills (auto_load: true)**:
```bash
# .opencode/skill/research/SKILL.md
# Change: auto_load: true

# .opencode/skill/spec-generator/SKILL.md
# Change: auto_load: true

# .opencode/skill/knowledge-miner/SKILL.md
# Change: auto_load: true
```

**All Other Skills (auto_load: false)**:
```bash
# .opencode/skill/legacy-pattern-miner/SKILL.md
# Change: auto_load: false

# .opencode/skill/blitz-tunnel/SKILL.md
# Change: auto_load: false

# .opencode/skill/blitz-validate/SKILL.md
# Change: auto_load: false

# .opencode/skill/git-secret-scrub/SKILL.md
# Change: auto_load: false

# .opencode/skill/hf-cli/SKILL.md
# Change: auto_load: false

# .opencode/skill/omega-doc-architect/SKILL.md
# Change: auto_load: false

# .opencode/skill/pr-readiness-checker/SKILL.md
# Change: auto_load: false

# .opencode/skill/provider-validator/SKILL.md
# Change: auto_load: false

# .opencode/skill/sovereign-refinement-protocol/SKILL.md
# Change: auto_load: false

# .opencode/skill/sovereign-search/SKILL.md
# Change: auto_load: false
```

### 4.4 Verification
```bash
# Check all skills have auto_load field
grep -r "auto_load:" .opencode/skill/*/SKILL.md

# Expected output:
# .opencode/skill/research/SKILL.md:auto_load: true
# .opencode/skill/spec-generator/SKILL.md:auto_load: true
# .opencode/skill/knowledge-miner/SKILL.md:auto_load: true
# .opencode/skill/legacy-pattern-miner/SKILL.md:auto_load: false
# .opencode/skill/blitz-tunnel/SKILL.md:auto_load: false
# .opencode/skill/blitz-validate/SKILL.md:auto_load: false
# .opencode/skill/git-secret-scrub/SKILL.md:auto_load: false
# .opencode/skill/hf-cli/SKILL.md:auto_load: false
# .opencode/skill/omega-doc-architect/SKILL.md:auto_load: false
# .opencode/skill/pr-readiness-checker/SKILL.md:auto_load: false
# .opencode/skill/provider-validator/SKILL.md:auto_load: false
# .opencode/skill/sovereign-refinement-protocol/SKILL.md:auto_load: false
# .opencode/skill/sovereign-search/SKILL.md:auto_load: false
```

---

## 5. Verification Test Scripts

### 5.1 Test 1: AGENTS.md Injection
```bash
# Run with debug to see context injection
opencode --log-level DEBUG run "What is the first sentence of SOVEREIGN_MANDATES.md?"

# Expected output contains:
# "These mandates are the 'Constitutional Law' of the Omega Engine."
# (First sentence of SOVEREIGN_MANDATES.md)
```

### 5.2 Test 2: Per-Agent Model Routing
```bash
# Researcher should use local Qwen3-4B-Thinking
opencode --agent researcher run "What model are you?"
# Expected: "I am qwen3-4b-thinking" or similar local model identifier

# Kali should use cloud Nemotron 3 Ultra
opencode --agent kali run "What model are you?"
# Expected: "I am nemotron-3-ultra-free" or similar cloud model identifier

# Maat should use local Qwen3-4B-Thinking (Carmack Q5.1)
opencode --agent maat run "What model are you?"
# Expected: "I am qwen3-4b-thinking"

# Lilith should use local Qwen3-4B-Thinking (Carmack Q5.1)
opencode --agent lilith run "What model are you?"
# Expected: "I am qwen3-4b-thinking"

# Node should use local Qwen3-1.7B
opencode --agent node run "What model are you?"
# Expected: "I am qwen3-1.7b"

# Verity should use local Qwen3-1.7B
opencode --agent verity run "What model are you?"
# Expected: "I am qwen3-1.7b"
```

### 5.3 Test 3: Compaction Plugin Loads
```bash
# Start opencode with debug, check plugin loads
opencode --log-level DEBUG 2>&1 | head -50 | grep -i "sovereign-compaction"

# Expected: Plugin registration log line (no errors)
# Example: "[plugin] Loaded sovereign-compaction from file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts"
```

### 5.4 Test 4: Skills Opt-In
```bash
# Check only 3 skills auto-loaded
opencode --log-level DEBUG 2>&1 | grep -i "auto_load"

# Expected: Only 3 skills show auto_load: true
# research, spec-generator, knowledge-miner
```

### 5.5 Test 5: MANDATES_CONDENSED.md Exists
```bash
# Verify file exists at repo root
ls -la /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/MANDATES_CONDENSED.md

# Verify line count
wc -l /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/MANDATES_CONDENSED.md
# Expected: 57

# Verify token estimate
wc -c /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/MANDATES_CONDENSED.md
# Expected: ~6000 chars (~1.5K tokens)
```

### 5.6 Test 6: opencode.json Structure
```bash
# Validate JSON syntax
cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq .

# Verify key fields
cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.instructions'
# Expected: ["AGENTS.md"]

cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.compaction'
# Expected: {auto: true, prune: true, tail_turns: 5, preserve_recent_tokens: 80000, reserved: 20000, buffer: 50000, keep: {tokens: 20000}}

cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.plugin[]' | grep sovereign-compaction
# Expected: file:///home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts

cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.agent.kali.model'
# Expected: "opencode/nemotron-3-ultra-free"

cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.agent.researcher.model'
# Expected: "lmstudio/qwen3-4b-thinking"

cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.agent.maat.model'
# Expected: "lmstudio/qwen3-4b-thinking"

cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.agent.lilith.model'
# Expected: "lmstudio/qwen3-4b-thinking"

cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.agent.node.model'
# Expected: "lmstudio/qwen3-1.7b"

cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.agent.verity.mode'
# Expected: "subagent"

cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.agent.verity.hidden'
# Expected: true

cat /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/opencode.json | jq '.agent.kali.toolProfile'
# Expected: "deploy"
```

### 5.7 Test 7: Environment Variable Set
```bash
# Check OPENCODE_DISABLE_AUTOCOMPACT is set
echo $OPENCODE_DISABLE_AUTOCOMPACT
# Expected: 1
```

---

## 6. Rollback Plan

### 6.1 Complete Rollback (All Changes)
```bash
#!/bin/bash
# rollback_phase1.sh — Run from repo root

set -e

REPO_ROOT="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine"

echo "=== Rolling back Context Injection Phase 1 ==="

# 1. Restore original opencode.json
echo "Restoring opencode.json..."
cd "$REPO_ROOT"
git checkout opencode.json

# 2. Remove MANDATES_CONDENSED.md
echo "Removing MANDATES_CONDENSED.md..."
rm -f "$REPO_ROOT/MANDATES_CONDENSED.md"

# 3. Remove sovereign compaction plugin
echo "Removing sovereign-compaction plugin..."
rm -f "/home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts"

# 4. Restore skill auto_load to true (or remove field)
echo "Restoring skill auto_load..."
for skill in research spec-generator knowledge-miner legacy-pattern-miner blitz-tunnel blitz-validate git-secret-scrub hf-cli omega-doc-architect pr-readiness-checker provider-validator sovereign-refinement-protocol sovereign-search; do
  skill_file="$REPO_ROOT/.opencode/skill/$skill/SKILL.md"
  if [ -f "$skill_file" ]; then
    # Remove auto_load line entirely (defaults to true in OpenCode)
    sed -i '/^auto_load:/d' "$skill_file"
    echo "  Cleared auto_load from $skill"
  fi
done

# 5. Unset environment variable
echo "Unsetting OPENCODE_DISABLE_AUTOCOMPACT..."
unset OPENCODE_DISABLE_AUTOCOMPACT
# Also remove from shell profile if added
sed -i '/OPENCODE_DISABLE_AUTOCOMPACT/d' ~/.bashrc ~/.zshrc 2>/dev/null || true

echo "=== Rollback complete ==="
echo "Restart OpenCode to apply changes."
```

### 6.2 Selective Rollback Commands

**Rollback only opencode.json**:
```bash
cd /home/arcana-novai/Documents/Xoe-NovAi/omega-engine
git checkout opencode.json
```

**Rollback only MANDATES_CONDENSED.md**:
```bash
rm /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/MANDATES_CONDENSED.md
```

**Rollback only compaction plugin**:
```bash
rm /home/arcana-novai/.config/opencode/plugin/sovereign-compaction.ts
```

**Rollback only skills**:
```bash
for skill in research spec-generator knowledge-miner legacy-pattern-miner blitz-tunnel blitz-validate git-secret-scrub hf-cli omega-doc-architect pr-readiness-checker provider-validator sovereign-refinement-protocol sovereign-search; do
  sed -i '/^auto_load:/d' "/home/arcana-novai/Documents/Xoe-NovAi/omega-engine/.opencode/skill/$skill/SKILL.md"
done
```

**Rollback only environment variable**:
```bash
unset OPENCODE_DISABLE_AUTOCOMPACT
sed -i '/OPENCODE_DISABLE_AUTOCOMPACT/d' ~/.bashrc ~/.zshrc 2>/dev/null || true
```

---

## 7. Implementation Order (Dependency-Aware)

| Step | Task | Depends On | Owner | Est. Time |
|------|------|------------|-------|-----------|
| 1 | Create `MANDATES_CONDENSED.md` | None | Kali | 15 min |
| 2 | Update `opencode.json` | Step 1 | Kali | 20 min |
| 3 | Create sovereign compaction plugin | Step 2 | Kali | 15 min |
| 4 | Update skill frontmatter | None | Kali | 10 min |
| 5 | Set `OPENCODE_DISABLE_AUTOCOMPACT=1` | None | Kali | 2 min |
| 6 | Run verification tests | Steps 1-5 | Kali | 10 min |
| 7 | Commit changes | Step 6 pass | Kali | 5 min |

**Total**: ~77 minutes

---

## 8. Acceptance Criteria (from ACTIVE_SPRINT.json)

All must pass for Phase 1 complete:

- [ ] **CI-1**: `MANDATES_CONDENSED.md` exists at repo root, 57 lines, ~1.5K tokens, all 27 mandates as one-liner table
- [ ] **CI-2**: `opencode.json` has `instructions: ["AGENTS.md"]`, compaction buffer=50000/keep=20000, sovereign-compaction plugin, per-agent model routing (kali=nemotron, researcher=qwen3-4b-thinking, maat=qwen3-4b-thinking, lilith=qwen3-4b-thinking, node=qwen3-1.7b, verity=qwen3-1.7b), verity.mode=subagent+hidden+restrictive, toolProfile stubs on all agents
- [ ] **CI-3**: Sovereign compaction plugin loads without error, injects mandates+entity+phase+anchor pre-compaction
- [ ] **CI-4**: 3 skills have `auto_load: true` (research, spec-generator, knowledge-miner), all others `auto_load: false`, debug shows only 3 skills
- [ ] **CI-5**: Verification tests pass (AGENTS.md injection, per-agent model routing, compaction plugin, skills opt-in)

---

## 9. Post-Phase 1: Phase 2 Preview

Phase 2 (Post-Debut, Ma'at/N3 ownership) will implement:

| Item | Spec Location | Owner |
|------|---------------|-------|
| SequentialModelLoader + AdaptiveContextBuffer | `data/coordination/HOLISTIC_ARCHITECTURE_PLAN_20260820.md` | Ma'at |
| HeadroomMiddleware + ModelGateway integration | `docs/specs/qdrant_headroom/QDRANT_HEADROOM_INTEGRATION_RESEARCH_20260820.md §4.2` | Ma'at |
| Hydration Engine (3-layer) | Carmack Review Q3.2 | Ma'at |
| Token Budget Enforcer (fixed tiers) | Carmack Review Q4.1 | Ma'at |
| Local Token Counter (ctypes → llama_tokenize) | Carmack Review Q4.2 | Ma'at |
| MCP Server Domain Split (4 servers) | Carmack Review Q2.1 | Roc |
| zswap + NVMe Swap Subsystem | `data/coordination/HOLISTIC_ARCHITECTURE_PLAN_20260820.md §3.3` | Ma'at |

---

## 10. References

| Document | Purpose |
|----------|---------|
| `docs/specs/context_injection/06_PHASE_1_PLAN.md` | Original Phase 1 plan (pre-Carmack) |
| `docs/specs/context_injection/CARMMACK_CONTEXT_INJECTION_REVIEW_20260820.md` | Carmack review with modifications |
| `data/coordination/ACTIVE_SPRINT.json` | Sprint tracking, workstream CONTEXT-INJECTION |
| `SOVEREIGN_MANDATES.md` | Full 27 mandates (source for condensation) |
| `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` | Strategy SSOT (post-DOC-1) |
| `docs/specs/debut_remediation/DEBUT_REMEDIATION_MANUAL_20260817.md` | Current execution authority |

---

*⬡ OMEGA ⬡ MAAT ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_ci_phase1_spec ⬡ 2026-08-20*