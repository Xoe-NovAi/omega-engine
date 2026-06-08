# 🔱 Roc Racoon — Mnemosyne/Memory-Bank Treasure Map Brief
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ ROC-MNEMOSYNE-BRIEF ⬡ PRIVATE-RELEASE

**Date**: 2026-06-08
**From**: Kali (MaKaLi Unification — Grand Oversight)
**To**: Roc Racoon (Sovereign Miner — P9 Coordination)
**Status**: READY FOR MINING EXPEDITION

---

## §0 Your Mission

Investigate all legacy Mnemosyne, Memory-Bank, knowledge management, and memory persistence systems in the two legacy repositories. Produce a **treasure map** with:

1. **System inventory** — Every Mnemosyne/Memory-Bank/knowledge component found
2. **Portability score** (1-10) — How easily does this port to current Omega Engine?
3. **Value score** (1-10) — How much does the engine gain from this system?
4. **Difficulty score** (1-10) — How hard is the port?
5. **Trade-off analysis** — Does this complement or compete with Hivemind?
6. **Extraction plan** — Concrete steps to port the highest-value components

---

## §1 Context

### The Question
The user asked: **"Is Hivemind supposed to replace Mnemosyne/Memory-Bank, or are they two complimentary [sic] pieces of the same whole?"**

Kali's initial assumption was that Hivemind replaces Mnemosyne. The user corrected: **"Hivemind might just be one piece of the bigger system."**

### What We Know
| System | Known Role | Status |
|--------|-----------|--------|
| **Hivemind** | Cross-CLI coordination fabric (awareness, handoff, context posting) | ✅ LIVE (MCP tools on Omega Hub :8016) |
| **MemoryStore** | Hot/Warm/Cold tiered memory in current engine | ✅ LIVE (`src/omega/memory_store.py`) |
| **Mnemosyne (legacy)** | 13-sphere Kabbalistic memory system | 🔴 UNKNOWN — needs investigation |
| **Memory-Bank (legacy)** | Knowledge base / session continuity | 🔴 UNKNOWN — needs investigation |

### Why This Matters
If Mnemosyne/Memory-Bank has capabilities that Hivemind lacks (long-term structured memory, Kabbalistic knowledge organization, session continuity beyond awareness), porting them makes the engine complete. If they're redundant, we close the question and focus on Hivemind.

---

## §2 Search Targets

Search these directories exhaustively:

### Primary Targets
```
/home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/
  - data_archive/mnemosyne/           (13 spheres)
  - any files named *memory* or *mnemosyne* or *memory-bank*
  - any files named *knowledge* or *kms*
  - any files named *session* or *continuity*

/home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/
  - data/                             (memory, sessions)
  - any files named *memory* or *mnemosyne* or *memory-bank*
  - any files named *knowledge* or *kms*
  - any files named *session* or *continuity*
```

### Secondary Targets
```
/media/arcana-novai/omega_library/data_archive/
  - mnemosyne/                        (already identified as 13 spheres)
  - Any *memory* or *knowledge* directories

/media/arcana-novai/omega_vault/
  - ANCESTRAL_HUB/origins/            (pre-March 2025 origin documents)
```

---

## §3 Scoring Rubric

Each discovered system MUST be scored on all three axes:

### Portability Score (1-10)
| Score | Meaning |
|-------|---------|
| 1-3 | Tightly coupled to legacy stack (old DB, old API, dead dependencies) |
| 4-6 | Pattern is portable but needs significant adaptation |
| 7-8 | Pattern is mostly standalone, minor adaptation needed |
| 9-10 | Directly usable — YAML files, no external deps, clear schema |

### Value Score (1-10)
| Score | Meaning |
|-------|---------|
| 1-3 | Duplicates existing Hivemind/MemoryStore functionality |
| 4-6 | Adds moderate new capability (different data organization) |
| 7-8 | Adds significant new capability (different storage model, richer queries) |
| 9-10 | Critical missing piece — engine is incomplete without this |

### Difficulty Score (1-10)
| Score | Meaning |
|-------|---------|
| 1-3 | Copy-paste-port. Minor path changes. |
| 4-6 | Needs refactoring but same language (Python) and same patterns |
| 7-8 | Needs significant architectural adaptation |
| 9-10 | Ecosystem-level port (DB migration, protocol changes, container rebuild) |

---

## §4 Output Format

Write your treasure map to:
```
data/entities/roc_racoon/workspace/MNEMOSYNE_TREASURE_MAP_20260608.md
```

### Required Sections
```markdown
# §1 Executive Summary
- Total systems found: X
- High-value (score ≥ 24): X
- Medium-value (score 18-23): X
- Low-value (score < 18): X
- Recommendation: PORT | MERGE | CLOSE

# §2 System Inventory (one per system)
## System: [Name]
- Location: /full/path/
- Type: [memory | knowledge | session | coordination]
- Portability: 7/10
- Value: 8/10
- Difficulty: 4/10
- Total: 19/30
- Trade-off vs Hivemind: [complements | competes | independent]
- Extraction Plan: ...
- Key Files: ...

# §3 Decision Matrix
| System | Port | Value | Diff | Total | Verdict |
|--------|------|-------|------|-------|---------|
| ...    | 7    | 8     | 4    | 19    | PORT    |

# §4 Extraction Priority Queue
1. [Highest total score] — brief rationale
2. ...
```

---

## §5 Research Protocol

1. **Start with grep** — search both legacy trees for `mnemosyne`, `memory_bank`, `knowledge_`, `session_`
2. **Read key files** — at least the header/docstring of each match
3. **Rate each system** — portability/value/difficulty
4. **Write treasure map** — to your workspace
5. **Post Hivemind context** — notify the team

### Essential Grep Patterns
```bash
grep -rn "mnemosyne" /home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/ 2>/dev/null
grep -rn "mnemosyne" /home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/ 2>/dev/null
grep -rn "memory_bank\|memory-bank\|MemoryBank" /home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/ 2>/dev/null
grep -rn "class.*Memory\|class.*Session\|class.*Knowledge" /home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy/src/ 2>/dev/null
grep -rn "class.*Memory\|class.*Session\|class.*Knowledge" /home/arcana-novai/Documents/Xoe-NovAi/xna-omega-legacy/src/ 2>/dev/null
```

---

## §6 Handoff to the Team

After writing your treasure map:
1. `omega-hub_hivemind_post_context(cli="opencode-roc_racoon", ...)` with your findings
2. Write workspace lock: `data/coordination/ROC_WORKSPACE_LOCK_20260608.md`
3. Append to live feed: `data/coordination/ROC_LIVE_FEED.md`
4. Call `@scribe` for soul distillation at session end

---

— Kali (Grand Oversight), 2026-06-08
*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ FINAL-HANDOFF ⬡*
