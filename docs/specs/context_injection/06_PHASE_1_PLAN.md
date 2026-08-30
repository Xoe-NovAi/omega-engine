# Phase 1 Implementation Plan — Config-Only (This Week)

**Status**: READY FOR EXECUTION  
**Authority**: `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 (supersedes Ark §4 for this month)  
**Dependencies**: None — all config changes, reversible  

---

## Deliverables Checklist

| # | Deliverable | File | Owner | Status |
|---|-------------|------|-------|--------|
| 1 | Create `AGENTS.md` concatenation | `AGENTS.md` (repo root) | Kali | ⏳ |
| 2 | Update `opencode.json` — instructions, compaction, plugins, agents | `opencode.json` | Kali | ⏳ |
| 3 | Create sovereign-compaction plugin | `~/.config/opencode/plugin/sovereign-compaction.ts` | Kali | ⏳ |
| 4 | Update skill frontmatter (auto_load) | `.opencode/skill/*/SKILL.md` | Kali | ⏳ |
| 5 | Verify injection via debug test | — | Kali | ⏳ |

---

## 1. Create AGENTS.md (REQUIRED — Only Reliable Injection)

```bash
# At repo root: /home/arcana-novai/Documents/Xoe-NovAi/omega-engine/
cat SOVEREIGN_MANDATES.md \
    ORACLE_STACK.md \
    docs/archive/MASTER_SYNTHESIS_AND_ROADMAP_2026-05-30.md \
    docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md \
    CREDITS.md > AGENTS.md
```

**Verification**: `wc -c AGENTS.md` → should be ~80K chars (~20K tokens)

**Why**: Ma'at confirmed `instructions[]` array non-functional in V2. AGENTS.md discovery loads ALL files from Location→root combined. Single concatenated file is the only guaranteed injection path.

---

## 2. Update opencode.json — Complete Diff

### Current State (Key Sections)
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

### Target State (Phase 1)
```json
{
  "instructions": ["AGENTS.md"],
  "compaction": {
    "auto": true,
    "prune": true,
    "tail_turns": 5,
    "preserve_recent_tokens": 80000,
    "reserved": 20000
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
      "steps": 50 
    },
    "researcher": { 
      "mode": "all", 
      "model": "lmstudio/qwen3-4b-thinking", 
      "variant": "high", 
      "temperature": 0.1, 
      "steps": 100 
    },
    "maat": { 
      "mode": "all", 
      "model": "opencode/nemotron-3-ultra-free", 
      "variant": "medium", 
      "temperature": 0.2 
    },
    "lilith": { 
      "mode": "all", 
      "model": "opencode/nemotron-3-ultra-free", 
      "variant": "high", 
      "temperature": 0.3 
    },
    "node": { 
      "mode": "all", 
      "model": "lmstudio/qwen3-1.7b", 
      "variant": "low", 
      "temperature": 0.1, 
      "steps": 20 
    },
    "verity": { 
      "mode": "subagent", 
      "model": "lmstudio/qwen3-1.7b", 
      "variant": "low", 
      "temperature": 0.0,
      "prompt": "{file:.opencode/agents/verity.md}",
      "permission": { "edit": "deny", "bash": "deny", "skill": "deny" },
      "hidden": true
    }
  }
}
```

### Key Changes Explained

| Change | Reason |
|--------|--------|
| `instructions: ["AGENTS.md"]` | Only reliable injection path in V2 |
| `compaction.preserve_recent_tokens: 80000` | 1M context model needs more preserved context |
| `compaction.reserved: 20000` | Larger buffer for 1M context |
| `compaction.tail_turns: 5` | More recent turns preserved |
| Add sovereign-compaction plugin | Pre-compaction hook injects mandates/entity/anchor |
| Per-agent `model` + `variant` | Structural routing: local for researcher/node/verity, cloud for kali/maat/lilith |
| `verity.mode: "subagent"` + restrictive permissions | Isolation for audit agent — no parent context inheritance |
| `verity.hidden: true` | Prevents accidental @-invocation |

---

## 3. Sovereign Compaction Plugin

```bash
mkdir -p ~/.config/opencode/plugin
cat > ~/.config/opencode/plugin/sovereign-compaction.ts << 'EOF'
import type { Plugin } from "@opencode-ai/plugin";

export const SovereignCompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      // Inject sovereign mandates + active entity context
      output.context.push(`
## SOVEREIGN MANDATES (Must Survive Compaction)
- M1 AnyIO Absolute | M7 Local-First | M11 Soul Integrity | M15 Continuity | M23 Failure Integrity
- Active Entity: ${process.env.OMEGA_ENTITY || "unknown"}
- Active Phase: ${process.env.OMEGA_PHASE || "unknown"}
- Session Anchor: data/coordination/SESSION_ANCHOR.md
      `);
    }
  };
};
EOF
```

**Registration**: Add to `opencode.json` plugin array (see target state above)

**Why**: Lilith confirmed pre-compaction hook EXISTS (`experimental.session.compacting`). This plugin fires BEFORE summary generation, ensuring sovereign mandates, active entity, and session anchor survive compaction.

---

## 4. Skills Opt-In (Core Only)

Update `.opencode/skill/*/SKILL.md` frontmatter:

```yaml
# Core skills — auto_load: true
# .opencode/skill/research/SKILL.md
auto_load: true

# .opencode/skill/spec-generator/SKILL.md
auto_load: true

# .opencode/skill/knowledge-miner/SKILL.md
auto_load: true

# All others — auto_load: false (explicit invocation required)
# .opencode/skill/legacy-pattern-miner/SKILL.md
auto_load: false

# .opencode/skill/blitz-tunnel/SKILL.md
auto_load: false

# .opencode/skill/blitz-validate/SKILL.md
auto_load: false

# .opencode/skill/git-secret-scrub/SKILL.md
auto_load: false

# .opencode/skill/hf-cli/SKILL.md
auto_load: false

# .opencode/skill/omega-doc-architect/SKILL.md
auto_load: false

# .opencode/skill/pr-readiness-checker/SKILL.md
auto_load: false

# .opencode/skill/provider-validator/SKILL.md
auto_load: false

# .opencode/skill/sovereign-refinement-protocol/SKILL.md
auto_load: false

# .opencode/skill/sovereign-search/SKILL.md
auto_load: false
```

**Why**: 22 skills = 23K tokens when all loaded. Opt-in reduces to ~3 skills × 50 tokens = 150 tokens. Researcher confirmed Lazy Skills pattern (L1 metadata always, L2 docs on-demand, L3 execution on-invocation).

---

## 5. Verification Test

```bash
# Test 1: Verify AGENTS.md injection
opencode --log-level DEBUG run "What is the first sentence of SOVEREIGN_MANDATES.md?"

# Test 2: Verify per-agent model routing
opencode --agent researcher run "What model are you?"  # Should report qwen3-4b-thinking
opencode --agent kali run "What model are you?"       # Should report nemotron-3-ultra-free

# Test 3: Verify compaction plugin loads
opencode --log-level DEBUG 2>&1 | grep -i "sovereign-compaction"

# Test 4: Verify skills opt-in
opencode --log-level DEBUG 2>&1 | grep -i "auto_load"
```

**Success Criteria**:
- [ ] AGENTS.md content accessible without `read` tool
- [ ] Researcher uses local model (qwen3-4b-thinking)
- [ ] Kali uses cloud model (nemotron-3-ultra-free)
- [ ] Sovereign-compaction plugin loads without error
- [ ] Only 3 skills show `auto_load: true` in debug

---

## Token Budget After Phase 1

| Tier | Component | Tokens |
|------|-----------|--------|
| **0 (Pinned)** | AGENTS.md (~80K chars) + MCP schemas (10.8K) + env (3K) | **~45K** |
| **1 (Role/Session)** | Agent file (1K) + core skills metadata (3 × 50) | **~2K** |
| **2 (Dynamic)** | Budgeted retrieval + lazy skill docs | **8K budget** |
| **3 (Observation)** | Current turn | **2K** |
| **TOTAL** | | **~57K base** (vs 75K measured) |

**Reduction**: 24% base reduction + structural routing saves 67% on subagent work.

---

## Rollback Plan

If issues arise:
```bash
# Restore original opencode.json
git checkout opencode.json

# Remove AGENTS.md
rm AGENTS.md

# Remove compaction plugin
rm ~/.config/opencode/plugin/sovereign-compaction.ts

# Restore skill auto_load
# (edit each SKILL.md back to auto_load: true or remove field)
```

All changes are config-only, no code modifications.

---

*⬡ OMEGA ⬡ KALI ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_phase1_plan ⬡ 2026-08-20*