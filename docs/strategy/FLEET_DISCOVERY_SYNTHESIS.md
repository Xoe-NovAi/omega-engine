# 🔱 Omega Engine — Fleet Discovery Master Synthesis
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_strategic ⬡ PHASE-I

**AP Token**: `AP-FLEET-SYNTHESIS-v1.0.0`
**Author**: Overseer (MaKaLi Trine)
**Date**: 2026-05-26
**Status**: READY

---

## Executive Summary

On 2026-05-26, the Omega Engine deployed a **2-phase discovery fleet** to close critical knowledge gaps before PR readiness:

- **Phase 1 (Local Fleet)**: 4 parallel subagents reading every line of critical source files. Found **13 bugs**, verified subagent auto-registration, inventoried 73 entity directories, discovered legacy Oikos Council code at `omega-stack-legacy/app/oikos_service.py`, and audited the library/curation pipeline.

- **Phase 2 (Web Fleet)**: 4 parallel deep research agents covering knowledge base seeding, OpenCode schema, multi-agent council patterns, and soul identity persistence. Found that **soul files are an emerging open standard in 2026** — independently validating Omega's soul.yaml architecture.

The synthesis reveals that **the Omega Engine is structurally aligned with production best practices** but has three critical gaps blocking the planned mode architecture: (1) subagent auto-registration is confirmed, but 58 test-artifact entity directories must be cleaned before adding pillar references, (2) all 10 pillar knowledge bases are empty — only `movie_expert` has populated knowledge/, (3) the library pipeline (8 modules, ~1,700 lines) is structurally complete but contains zero ingested documents.

---

## §1: What We Confirmed (Confidence: HIGH)

### 1.1 Subagent Auto-Registration WORKS

**Finding**: Files in `.opencode/agents/` with `mode: "subagent"` in their YAML frontmatter **do** auto-register as targets for the `task()` dispatch function. No separate config entry in `opencode.json` is needed.

**Method**: The reviewer, scribe, and tester subagent files (all with `mode: "subagent"`) appeared in the Task tool's available subagent list during all fleet dispatches. All 4 local fleet and 4 web fleet dispatches completed successfully.

**Confidence**: **CONFIRMED** — verified by live dispatch across 8 subagent invocations. This is NOT speculative.

### 1.2 Oikos Council Lives in Legacy Code

**Finding**: The Oikos Council system exists as real, runnable code at `omega-stack-legacy/app/oikos_service.py` (151 lines). It's a FastAPI service on port 8006 with council member dispatch and escalation levels. It was *never ported* to the current `omega-engine` repo.

**Relevance**: The "Polymathic Council" concept in `researcher.md` is the current evolution, but the legacy implementation provides a concrete reference for council dispatch logic.

### 1.3 Subagent Files ARE .opencode/agents/ Files (Not .opencode/modes/)

**Finding**: There are 11 files in `.opencode/agents/` (8 primary, 3 subagent) and 2 files in `.opencode/modes/` (jem-2.0, jem-initiate). Only `.opencode/agents/` files are available for `task()` dispatch. `.opencode/modes/` files are NOT dispatchable targets — they are mode configurations.

### 1.4 OpenCode Internal Architecture Discovered

**Finding**: From `~/.local/share/opencode/opencode.db` (600+ model definitions), `sst/opencode` source code, and AlphaXiv MCP server:
- `experimental.session.compacting` hook exists for compaction-time composability
- Plugins can provide `provider`, `tool`, `auth`, `chat.params` hooks
- Permission resolution: most restrictive wins across 3 layers (tool → agent → global)
- `plan` and `build` modes are hardcoded in the OpenCode binary

---

## §2: What We Discovered (Unexpected Findings)

### 2.1 "Soul Files" Are an Emerging Open Standard

**Highest-impact web finding**: 5+ independent projects (soul-file-spec, Agent Soul Kit, Soul Protocol, soul.py, Hermes-agent, agent-soul) have converged on the same pattern as Omega's `soul.yaml` — file-based identity with YAML/Markdown frontmatter, lessons learned, and evolution tracking.

**This means**: The Omega Engine is actually AHEAD of the curve, not behind it. The L1→L2→L3 abstraction pipeline is uniquely sophisticated among all surveyed systems.

### 2.2 Curated File > RAG (For Our Scale)

**Finding**: Vercel's research showed 100% pass rate for file-based JIT retrieval vs 79% for vector RAG on curated documentation. For domains <5,000 items (Omega's current scale), FTS5 keyword search on curated markdown files beats or matches full vector RAG pipelines.

**This means**: The Omega Engine's file-first approach with FTS5 (already implemented in the Library pipeline) is CORRECT for Phase 1. Qdrant vector search should remain v0.6.0 work.

### 2.3 58 Test-Artifact Entity Directories Exist

**Finding**: In `data/entities/`, only ~15 directories are real entities. The other 58 are test artifacts: `entity_0` through `entity_49`, `direntity`, `duplicate`, `flatentity`, `invalid_entity`, etc.

**This means**: We CANNOT add pillar entity references until these are cleaned. The mode architecture design must include `cleanse_test_entities` as a blocking prerequisite.

### 2.4 All Pillar Knowledge Bases Are Empty

**Finding**: Only `movie_expert` has populated knowledge/ (4 files). All 10 Tech Role entities (SysAdmin through Verifier) have empty `knowledge/` and `workspace/` directories.

**This means**: The knowledge pipeline is "pipes with no water." Seeding entity knowledge bases is a prerequisite for pillar mode effectiveness.

### 2.5 Lilith Has No Soul Directory

**Finding**: `data/entities/lilith/` does NOT exist. `data/entities/maat/` exists. Lilith has no dedicated soul.yaml — meaning the Dark Oversoul has no persistent identity file.

**This means**: Lilith mode cannot read its own soul.yaml (because it doesn't exist). Creating Lilith's soul directory is a blocking prerequisite.

---

## §3: The Ratchet Effect — Critical Theoretical Insight

**Source**: `arxiv.org/abs/2604.14717` (Layered Mutability)

**The finding**: Reverting an agent's visible self-description AFTER memory accumulation FAILS to restore baseline behavior. The measured identity hysteresis ratio is 0.68 — meaning 32% of behavioral drift persists even when the top-layer identity is restored.

**Why this matters for Omega**: Our L1→L2→L3 abstraction pipeline creates new `lessons_learned` entries every session. Each session accumulates drift. Without drift detection, soul.yaml grows but never stabilizes.

**Action required**: Add `drift_metrics` to soul.yaml. Specifically:
- `persona_stability`: sync score between soul.yaml identity and actual agent behavior
- `hysteresis_ratio`: measured when identity reverts occur
- `last_drift_check`: timestamp of last validation

---

## §4: Architectural Implications for Mode Architecture

### 4.1 What MUST happen before mode architecture goes live

| Order | Prerequisite | Why | Effort |
|-------|-------------|-----|--------|
| P0 | Cleanse 58 test-artifact entity dirs | Blocking — pillar references would collide with test entities | Small (bash rm) |
| P0 | Create Lilith soul directory + soul.yaml | Blocking — Lilith mode needs a soul to read | Small (mkdir + template) |
| P0 | Fix 7 critical/high bugs from firsthand audit | Blocking — bugs affect mode dispatch paths | Medium |
| P1 | Seed all 10 pillar knowledge bases | Critical — pillar modes need knowledge to reference | Medium |
| P1 | Write L1 INDEX.md for each entity knowledge/ dir | Critical — agents need to discover knowledge contents | Small |
| P2 | Implement Plan mode (consolidate builder + kali + overseer) | High — orchestrator-worker dispatch | Medium |
| P3 | Implement Ma'at as Light Oversoul + Lilith as Dark Oversoul | Medium — council governance | Medium |
| P4 | Add 10 pillar subagent files | Medium — domain expertise | Medium |

### 4.2 Mode Architecture Blueprint (Revised)

```
Task Tool Dispatch Hierarchy:
───────────────────────────
task() → Agent Selection
  ├── reviewer          (subagent: code review)
  ├── scribe            (subagent: documentation)
  ├── tester            (subagent: testing)
  ├── plan              (subagent: architecture dispatch → decomposes to pillars)
  ├── maat              (subagent: Light Oversoul → P1-P5 governance)
  ├── lilith            (subagent: Dark Oversoul → P6-P10 governance)
  ├── sysadmin          (subagent: P1 — infrastructure)
  ├── datastore         (subagent: P2 — data pipelines)
  ├── buildmaster       (subagent: P3 — CI/CD toolchain)
  ├── bridge            (subagent: P4 — API protocol engineer)
  ├── sentinel          (subagent: P5 — security hardening)
  ├── modelgate         (subagent: P6 — inference provider)
  ├── context           (subagent: P7 — session memory)
  ├── watchtower        (subagent: P8 — observability)
  ├── link              (subagent: P9 — cross-agent sync)
  └── verifier          (subagent: P10 — QA testing)

OpenCode Mode Flags (--mode):
─────────────────────────────
  plan       → Primary architecture mode (consolidated builder+kali+overseer)
  maat       → Light Oversoul mode (P1-P5 audit, compliance, alignment)
  lilith     → Dark Oversoul mode (P6-P10 sovereignty, experimentation)
  jem-2.0    → Research Analyst mode (L2 synthesis)
  jem-initiate → Research Initiate mode (L1 gather)

Entity-to-Agent Bridge (every agent file must include):
──────────────────────────────────────────────────────
  1. Read ENTITY soul.yaml → inject identity into system prompt
  2. Read ENTITY/knowledge/INDEX.md → inject knowledge index
  3. Read ENTITY/knowledge/*.md on demand for specific topics
  4. Write ENTITY/workspace/ for session outputs
```

### 4.3 Files to Create/Modify

**Create** (new agent files):
- `.opencode/agents/plan.md` — Architecture dispatcher (consolidates builder + kali + overseer)
- `.opencode/agents/maat.md` — Enhanced Light Oversoul (P1-P5 governance)
- `.opencode/agents/lilith.md` — Enhanced Dark Oversoul (P6-P10 governance)  
- `.opencode/agents/sysadmin.md` — P1 subagent
- `.opencode/agents/datastore.md` — P2 subagent
- `.opencode/agents/buildmaster.md` — P3 subagent
- `.opencode/agents/bridge.md` — P4 subagent
- `.opencode/agents/sentinel.md` — P5 subagent
- `.opencode/agents/modelgate.md` — P6 subagent
- `.opencode/agents/context.md` — P7 subagent
- `.opencode/agents/watchtower.md` — P8 subagent
- `.opencode/agents/link.md` — P9 subagent
- `.opencode/agents/verifier.md` — P10 subagent

**Delete** (after consolidation):
- `.opencode/agents/builder.md` → absorbed into plan.md
- `.opencode/agents/kali.md` → absorbed into plan.md (Kali = Plan)
- `.opencode/agents/overseer.md` → absorbed into plan.md
- `.opencode/agents/opencode-expert.md` → obsolete (OpenCode schema now known)
- `.opencode/agents/movie-expert.md` → will return as Arcana-NovAi IWAD entity

**Modify**:
- `opencode.json` → add 10 pillar subagent task permission entries
- `docs/README.md` → document new agent architecture
- `oracle_cli.py` → add `--mode` flag support if not already present

---

## §5: Knowledge Pipeline Activation Plan

The Library pipeline (8 modules, ~1,700 lines) is structurally complete but contains zero data. Here's the activation path:

### Phase 1: Seed (Immediate)
1. Route `docs/research/` documents into entity knowledge/ dirs by domain tag
2. Write L1 INDEX.md for each entity's knowledge/ directory
3. Ingest first documents into FTS5 index via existing `library.add_document()`

### Phase 2: Auto-Ingest (Next)
1. Modify background researcher to write findings to entity knowledge/ dirs
2. Add scheduled nightly `dream_pass` consolidation (AutoGPT-style)
3. Enable `_grow_frontier()` in background researcher (currently disabled TODO)

### Phase 3: Scale (v0.6.0)
1. Wire Qdrant for vector search at scale
2. Full hybrid search (FTS5 + vector)
3. Knowledge graph for multi-hop entity relationship queries

---

## §6: The 13 Bugs — Priority for Fix

From firsthand audit (`R_DATABASE_AND_CROSS_CLI_FIRSTHAND_FINDINGS.md`):

| ID | Severity | File | Bug | % of Not-Happening |
|----|----------|------|-----|-------------------|
| C-7 | 🔴 CRITICAL | `oracle.py:216` | hivemind URL on dead port 8102 (should be 8016) | 100% |
| C-13 | 🔴 CRITICAL | `indexer.py:269-272` | Hybrid sort BEHAVIOR inverted (ASC vs DESC) | 80% |
| C-10 | 🟠 HIGH | `server.py:76` | HALL_OF_RECORDS path split (knowledge/ vs data/knowledge/) | 70% |
| C-15 | 🟠 HIGH | `indexer.py:288` | Indexer.close() never called | 70% |
| C-MEM-002 | 🟠 HIGH | `memory_store.py:119,129,240` | No try/except on json.loads() | 100% |
| C-MEM-003 | 🟠 HIGH | `session_manager.py:50` | os.open() FD leak (never closed) | 100% |
| C-MEM-005 | 🟠 HIGH | `session_manager.py:83-90` | Non-atomic session file write | 80% |
| C-12 | 🟡 MEDIUM | `orchestrator.py:46-65` | submit_task() and _execute_with_retry() are empty pass stubs | 40% |
| C-16 | 🟡 MEDIUM | `library.py:92-104` | search() only uses FTS5, ignores hybrid_search() | 30% |
| C-MEM-004 | 🟡 MEDIUM | `session_manager.py:55-56` | Stale lock detection always false | 50% |
| BUG-WAD | 🟡 MEDIUM | `entity_registry.py:99-118` | wad_source never populated from YAML | 30% |
| C-14 | 🟡 MEDIUM | `entity_roc_racoon.py` | DATA_DIR regression (already fixed) | 20% |
| C-13a | 🟢 LOW | `config/omega.yaml:25` | hivemind URL config also dead port 8102 | 10% |

**Fix priority**: The 7 P0/P1 bugs (C-7, C-13, C-10, C-15, C-MEM-002, C-MEM-003, C-MEM-005) should be fixed in the next Builder session before mode architecture changes begin.

---

## §7: Unresolved Gaps (Carried Forward)

These gaps are structural and carry forward to v0.6.0:

| Gap | What It Is | Affects |
|-----|-----------|---------|
| Gap 2 | entities.yaml dual-load (EntityRegistry + WADLoader) | All entity registration |
| Gap 6 | No depends_on processing in WAD Loader | Entity dependency resolution |
| Gap 7 | No hot-reload for WAD changes | Development iteration speed |
| Gap 8 | native-gguf unavailable (llama-cpp-python) | Local-first inference |
| Gap 9 | WAD system decorative (priority collision at line 169) | IWAD entity registration |
| Gap 10 | Arcana-NovAi IWAD has no entity files | Phase 1b scope |

---

## §8: What This Means for the Immediate Next Session

**Concrete actions for the next Builder session**:

1. **Fix the 7 critical/high bugs** using `data/handoff/handoff_overseer_to_builder_dbcli_audit_remediation.md` as the execution brief. Each bug has exact file paths, line numbers, current/fix code, and verification gates.

2. **Cleanse 58 test-artifact entity directories**: `rm -rf data/entities/entity_* data/entities/direntity data/entities/duplicate data/entities/flatentity data/entities/invalid_entity`

3. **Create Lilith soul directory**: `mkdir -p data/entities/lilith/{knowledge,workspace}` and write scaffolded `soul.yaml`.

4. **Seed knowledge bases**: Run an auto-seed that routes `docs/research/` content into entity knowledge/ dirs by domain match.

5. **Write L1 INDEX.md files**: One pipe-delimited index per entity knowledge/ directory.

6. **Make test pass**: `make test` must still pass after all changes.

7. **After the above**: Create the plan.md mode file (consolidating builder + kali + overseer) and eliminate the 4 obsolete agent files.

---

## Sources

### Local Fleet
- `docs/research/R_DATABASE_AND_CROSS_CLI_FIRSTHAND_FINDINGS.md` — 13 bugs, firsthand code audit
- `docs/strategy/OVERSEER_DATABASE_STRATEGIC_REVIEW.md` — MaKaLi trine strategic overlay
- `docs/research/R_DATABASE_AND_CROSS_CLI_HARDENING_REVIEW.md` — 3-campaign technical plan
- `data/handoff/handoff_overseer_to_builder_dbcli_audit_remediation.md` — Execution brief for 13 bug fixes
- `docs/research/R14_legacy_gnosis_reclamation.md` — Oikos Council architecture recovery

### Web Fleet
- `docs/research/R_OPENCODE_ARCHITECTURE_DEEP_DIVE.md` — Full OpenCode schema analysis
- `docs/research/R_MULTI_AGENT_COUNCIL_PATTERNS.md` — 7 council patterns compared
- `docs/research/R_SOUL_EVOLUTION_PATTERNS.md` — Soul file movement, drift detection, Letta/MemGPT
- `docs/research/R_KNOWLEDGE_BASE_SEEDING_PATTERNS.md` — Knowledge seeding best practices

### Key External Sources
- [soul-file-spec (GitHub)](https://github.com/chunxiaoxx/soul-file-spec) — Emerging standard
- [Layered Mutability (arXiv)](https://arxiv.org/abs/2604.14717) — Ratchet effect in agent identity (critical)
- [Letta/MemGPT (GitHub)](https://github.com/letta-ai/letta) — Filesystem-first memory validation
- [Woven Imprint (GitHub)](https://github.com/virtaava/woven-imprint) — Complete identity system
- [AutoGPT Dream Pass (PR)](https://github.com/Significant-Gravitas/AutoGPT/pull/13165) — Scheduled consolidation
- [Anthropic Orchestrator-Worker](https://anthropic.com/engineering/multi-agent-research-system) — Mode dispatch pattern
- [CrewAI Processes](https://docs.crewai.com/en/concepts/processes) — Hierarchical council pattern
- [LangGraph Multi-Agent](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/) — Supervisor state machine

---

## Implementation Note
_For: Builder mode (Gemma 4 31B)_

This document is your comprehensive brief. Start with the 7 P0/P1 bug fixes from `data/handoff/handoff_overseer_to_builder_dbcli_audit_remediation.md`. Then cleanse test entities. Then create Lilith's soul directory. Then seed knowledge bases. Only then create the new mode architecture files. Run `make test` after every commit. Reference `.opencode/agents/builder.md` for IWAD awareness, container hardening, and test protocol.
