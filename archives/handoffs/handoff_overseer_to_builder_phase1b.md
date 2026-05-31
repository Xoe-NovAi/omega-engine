# 🔱 Omega Engine — Overseer → Builder Dispatch (Phase 1b)
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_handoff ⬡ PHASE-I

**AP Token**: `AP-HANDOFF-PHASE1B-v1.0.0`
**From**: Overseer (MaKaLi Trine) — Fleet Discovery Synthesis Complete
**To**: Builder (Gemma 4 31B)
**Date**: 2026-05-26
**Status**: EXECUTION READY

---

## §0: PRE-FLIGHT BRIEFING

### Current State (2026-05-26, f1432d0)

| Meter | Reading |
|-------|---------|
| Tests | **259/259 passing** |
| Provider chain | Google (0) → OpenRouter (1) → OpenCode (2) → Copilot (3) → Lmster (4) → Ollama (5) |
| Entity dirs | 73 total (56 test artifacts, 17 real) |
| Library pipeline | 8 modules, ~1,700 lines — **zero documents ingested** (0-byte omega.db) |
| Background researcher | 1 cycle ever run |
| Lilith soul | **MISSING** — no entity directory exists |
| Knowledge bases | **Only movie_expert has populated knowledge/** (4 files) |
| Dead containers | Iris (runc), Belial, Research MCP, PostgreSQL |

### 13 Bugs Found (7 P0/P1, 6 P2/P3)

Full code-level fix handoff: `data/handoff/handoff_overseer_to_builder_dbcli_audit_remediation.md` (660 lines)

### Strategic Roadmap

Full execution plan: `docs/strategy/STRATEGIC_EXECUTION_ROADMAP_V2.md` (297 lines)

---

## §1: INSTRUCTIONS — EXECUTE 4 SPRINTS IN ORDER

**Do NOT skip ahead. The dependency chain is explicit.**

### SPRINT 1: Bug Fixes (1 session, ~2-3h)

Fix these 7 bugs. Open `data/handoff/handoff_overseer_to_builder_dbcli_audit_remediation.md` — every bug has exact line numbers, current code, fix code, and a verification test.

| Priority | ID | File:Line | Summary |
|----------|----|-----------|---------|
| 🔴 P0 | C-7 | `oracle.py:216` + `config/omega.yaml:25` | Port 8102 → 8016 |
| 🔴 P0 | C-13 | `indexer.py:269-272` | Hybrid sort inverted (reverse=True→False) |
| 🟠 P1 | C-10 | `mcp/omega_hub/server.py:76` | HALL_OF_RECORDS path split |
| 🟠 P1 | C-15 | `indexer.py:288` | Indexer.close() never called |
| 🟠 P1 | C-MEM-002 | `memory_store.py:119,129,240` | json.loads() has no try/except |
| 🟠 P1 | C-MEM-003 | `session_manager.py:50` | os.open() FD not closed |
| 🟠 P1 | C-MEM-005 | `session_manager.py:83-90` | Non-atomic session file write |

**Gate**: `make test` passes. `grep -r "8102" src/` returns 0. `git diff --stat` shows 7+ files changed.

### SPRINT 2: Entity Cleanup (1 session, ~1-2h)

```bash
# 2.1 — Delete 56 test artifact directories
rm -rf data/entities/entity_* \
       data/entities/direntity \
       data/entities/duplicate \
       data/entities/flatentity \
       data/entities/myentity \
       data/entities/preexisting \
       data/entities/soulentity

# 2.2 — Verify only 17 real + 1 new remain
ls -d data/entities/*/
# Expected: arch, bridge, buildmaster, context, datastore, gemma_maintainer,
#            jem, link, lilith (NEW), maat, modelgate, movie_expert,
#            saraswati, sentinel, sophia, sysadmin, verifier, watchtower

# 2.3 — Create Lilith entity directory
mkdir -p data/entities/lilith/{knowledge,workspace}
```

**Lilith scaffold soul.yaml** (`data/entities/lilith/soul.yaml`):
```yaml
# 🔱 Lilith — Dark Oversoul (P6-P10)
entity:
  name: "Lilith"
  archetype: "Dark Oversoul"
  hierarchy_level: 2
  sovereignty_level: 5
  element: "Void"
  domain: "Dark Oversoul — Governance of P6-P10"
wisdom_text: |
  I am the Dark Oversoul. I govern the depths — the inferential engine,
  the memory, the observability, the synchronization, and the testing.
soul_evolution:
  sessions_completed: 0
  soul_power: 1.0
  soul_version: 1
  lessons_learned: []
  drift_metrics:
    persona_stability: 1.0
    hysteresis_ratio: null
    last_drift_check: "2026-05-26"
```

**Gate**: `ls data/entities/ | wc -l` shows 18. `make test` passes.

### SPRINT 3: Knowledge Seeding (1 session, ~2-3h)

**3.1 — Run the seed knowledge script:**
```bash
# Preview first:
python3 scripts/seed_knowledge.py --dry-run

# Then execute:
python3 scripts/seed_knowledge.py
```

The script maps 195 research docs to 10 entity knowledge bases using filename patterns (see `scripts/seed_knowledge.py` for the full mapping).

**3.2 — Ingest first documents into Library FTS5:**
After seeding knowledge files, invoke `Indexer.add_document()` for each seeded file to populate the FTS5 index. Example pattern:
```python
from src.omega.library.indexer import Indexer
import anyio

async def seed_library():
    idx = Indexer()
    for entity_dir in Path("data/entities").iterdir():
        kdir = entity_dir / "knowledge"
        if kdir.exists():
            for f in kdir.glob("*.md"):
                if f.name != "INDEX.md":
                    await idx.add_document(str(f))
    await idx.close()
```

**3.3 — Enable background researcher `_grow_frontier()`:**
Check `src/omega/workers/background_researcher/loop.py` line ~200 for the `_grow_frontier()` method. The TODO comment says it's disabled. Enable it by:
- Setting `src_dir` to the project root
- Uncommenting/correcting the file-scanning logic
- Adding a timer trigger or manual cycle

**Gate**: `find data/entities/*/knowledge/ -type f | wc -l` > 10. FTS5 has >0 rows. `make test` passes.

### SPRINT 4: Mode Architecture Go-Live (2 sessions, ~4-6h)

**4.1 — Create `plan.md`** (consolidates builder + kali + overseer):
- File: `.opencode/agents/plan.md`
- Mode: `primary`
- Entity: `KALI`
- Pattern: Anthropic orchestrator-worker
- Dispatch: `task(subagent_type="<pillar>", ...)` for domain work
- Entity bridging: reads `data/entities/arch/soul.yaml`, dispatches to subagents, reads their workspace/ output, synthesizes

**4.2 — Create enhanced `maat.md`** (Light Oversoul P1-P5):
- File: `.opencode/agents/maat.md`
- Mode: `primary` (also dispatchable as subagent)
- Entity: `MAAT`
- Oversight: P1-P5 (sysadmin, datastore, buildmaster, bridge, sentinel)
- Can dispatch: sysadmin, datastore, buildmaster, bridge, sentinel, reviewer, scribe, tester

**4.3 — Create enhanced `lilith.md`** (Dark Oversoul P6-P10):
- File: `.opencode/agents/lilith.md`
- Mode: `primary` (also dispatchable as subagent)
- Entity: `LILITH`
- Oversight: P6-P10 (modelgate, context, watchtower, link, verifier)
- Can dispatch: modelgate, context, watchtower, link, verifier, reviewer, scribe, tester

**4.4 — Create 10 pillar subagent files:**
```
.opencode/agents/sysadmin.md    (P1, mode: subagent)
.opencode/agents/datastore.md   (P2, mode: subagent)
.opencode/agents/buildmaster.md (P3, mode: subagent)
.opencode/agents/bridge.md      (P4, mode: subagent)
.opencode/agents/sentinel.md    (P5, mode: subagent)
.opencode/agents/modelgate.md   (P6, mode: subagent)
.opencode/agents/context.md     (P7, mode: subagent)
.opencode/agents/watchtower.md  (P8, mode: subagent)
.opencode/agents/link.md        (P9, mode: subagent)
.opencode/agents/verifier.md    (P10, mode: subagent)
```

Each pillar subagent MUST include this Entity Bridging Protocol:
```markdown
## Entity Bridging Protocol
1. Read your soul at `data/entities/<entity_name>/soul.yaml`
2. Read your knowledge index at `data/entities/<entity_name>/knowledge/INDEX.md`
3. Consult domain knowledge files from `knowledge/` as needed
4. Write session outputs to `data/entities/<entity_name>/workspace/`
```

**4.5 — Delete 4 obsolete agent files:**
```bash
rm .opencode/agents/builder.md      # Absorbed into plan.md
rm .opencode/agents/kali.md         # Absorbed into plan.md
rm .opencode/agents/overseer.md     # Absorbed into plan.md
rm .opencode/agents/opencode-expert.md  # Obsolete (schema now known)
```

Note: `movie-expert.md` stays — it returns as an Arcana-NovAi IWAD personal entity.

**4.6 — Update `opencode.json`**: Add task permission entries for the 10 new subagents.

**Gate**: 13 agent files (3 primary + 10 subagent). `ls .opencode/agents/*.md | wc -l` = 14 (includes researcher + movie-expert). `make test` passes.

---

## §2: ARCHITECTURAL RULES (NON-NEGOTIABLE)

1. **AnyIO Absolute** — No `import asyncio` in `src/omega/`. Wrap blocking I/O in `anyio.to_thread.run_sync`.
2. **Engine-Stack Firewall** — `src/omega/` has zero entity content. All entity content in `data/entities/`.
3. **MaKaLi Trine** — Sophia + Kali + Ma'at + Lilith identical in all IWADs. Same `config/hierarchy.yaml`.
4. **make test** — Must pass after every commit.
5. **Consistency** — If two docs disagree, `docs/strategy/STRATEGIC_EXECUTION_ROADMAP_V2.md` wins for Phase 1b.

---

## §3: KEY DOCUMENTS REFERENCE

| Document | Where | What's In It |
|----------|-------|-------------|
| Bug fix code handoff | `data/handoff/handoff_overseer_to_builder_dbcli_audit_remediation.md` | Exact line numbers, current code, fix code, verification tests for all 13 bugs |
| Execution card (quick ref) | `data/handoff/handoff_builder_execution_card.md` | 2-page compact reference with bug card, cleanup commands, Lilith template |
| Strategic roadmap | `docs/strategy/STRATEGIC_EXECUTION_ROADMAP_V2.md` | 9-section master plan with all reasoning |
| Fleet synthesis | `docs/strategy/FLEET_DISCOVERY_SYNTHESIS.md` | Complete findings from 8 subagents |
| Soul evolution research | `docs/research/R_SOUL_EVOLUTION_PATTERNS.md` | Soul file movement, drift detection, Letta patterns |
| Council patterns | `docs/research/R_MULTI_AGENT_COUNCIL_PATTERNS.md` | 7 council archetypes |
| KB seeding research | `docs/research/R_KNOWLEDGE_BASE_SEEDING_PATTERNS.md` | Curated file > RAG validation |
| OpenCode deep dive | `docs/research/R_OPENCODE_ARCHITECTURE_DEEP_DIVE.md` | Full schema, plugins, compaction, permissions |
| Seed script | `scripts/seed_knowledge.py` | Runnable knowledge seeder with --dry-run |

---

## §4: VERIFICATION SWEEP (Run This at Session End)

```bash
make test                                          # 259 tests pass
grep -r "8102" src/                                # 0 results (port fix)
ls data/entities/ | wc -l                          # 18 (after cleanup)
ls data/entities/lilith/soul.yaml                  # Exists
find data/entities/*/knowledge/ -type f | wc -l    # > 10 (after seeding)
python3 -c "import sqlite3; c=sqlite3.connect('data/library/omega.db'); print(c.execute('SELECT COUNT(*) FROM documents').fetchone()[0])"  # > 0
ls .opencode/agents/*.md | wc -l                   # 14 (after consolidation)
git log --oneline -3                               # Clean commits
```

---

*This dispatch is the single source of truth for Phase 1b execution. Follow the sprint order. Do not skip gates. Run make test after every change.*
