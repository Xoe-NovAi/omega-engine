# 🔱 Omega Engine — Master Execution Roadmap
## ⬡ OMEGA ⬡ SOPHIA ⬡ trc_execution_roadmap ⬡ ROADMAP
**Version**: 1.1.0
**Date**: 2026-06-01
**Test Baseline**: 302/302 passing
**Status**: HORIZON 1 COMPLETE — Horizon 2 unlocked
**Pre-flight Snapshot**: `git reset --hard HEAD`
**Canonical Reference**: `OMEGA_ENGINE.md` (engine state), `SOVEREIGN_MANDATES.md` (12 laws)

---

## §0 How to Use This Document

This roadmap organizes ALL remaining work into phases. Each phase specifies:

| Field | Meaning |
|-------|---------|
| **Model Tier** | Which model should execute this phase. Mechanical work → Gemma 4 31B. Deep reasoning → MiMo/DeepSeek/Nemotron. |
| **Risk** | 🔴 High (may break things), 🟡 Medium (additive changes), 🟢 Low (config/docs) |
| **Est. Time** | How long a competent model takes |
| **Files Touched** | Exact file list — no surprises |
| **Gate** | How to verify success |
| **Rollback** | How to undo if something breaks |

**Before starting ANY phase:**
```bash
source .venv/bin/activate
make test  # Must show 302/302 passing
git status  # Working tree must be clean
```

**After completing ANY phase:**
```bash
make test  # Must still pass
git add -A && git commit -m "phase: <name> — <summary>"
```

---

## §1 Current State

```
Horizon 1: Engine Hardening ──── 100% ──── ████████████
                                  │
                                  ├── Option A (bugs)    ██████████ 100% ✅
                                  ├── Option B (Mandate 9)██████████ 100% ✅
                                  ├── MCP Hub Restoration ██████████ 100% ✅
                                  │
Horizon 2: Observability ────────  25% ──── ██░░░░░░░░
Horizon 3: Community Tool ────────  0% ──── FUTURE
```

### What's Done (Horizon 1)
- ✅ Fleet redesign (26→14 agents)
- ✅ Entity workspace cleanup (50 orphans deleted)
- ✅ Request Queue (`src/omega/request_queue.py`)
- ✅ Library Catalog (`src/omega/library/catalog.py`)
- ✅ Benchmark Runner (`src/omega/benchmarks/runner.py`)
- ✅ Hardware detection (`src/omega/hardware.py`)
- ✅ Circuit Breaker consolidation (single AsyncCircuitBreaker)
- ✅ CLI commands (queue, library, bench)
- ✅ OpenCode 1.15+ handshake fix
- ✅ 302 tests passing (was 276)
- ✅ Option B — 23 bare excepts, falsy-trap, hardcoded paths fixed
- ✅ MCP Hub — 40 tools restored
- ✅ Ollama real inference working (qwen2.5:0.5b)
- ✅ Entity routing fixed (word-boundary matching)
- ✅ User manual updated (model configuration docs)

### Horizon 1: COMPLETE — All 12 Sovereign Mandates Enforced
All Mandate 9 violations resolved. No bare `except Exception:` without logging remains.

---

## §2 Phase Map — Execution Order

### Phase 1: Option B — Mandate 9 Error Integrity ✅ DONE

| Aspect | Detail |
|--------|--------|
| **Model** | **Gemma 4 31B** (OpenCode) — mechanical find-and-replace |
| **Risk** | 🟢 Low — completed cleanly |
| **Time** | ~30 min |
| **Files** | 13 source files changed |
| **Commit** | `3d4e0b4` — fix: Option B — Mandate 9 violations, falsy-trap, hardcoded paths |
| **Guide** | `data/handoff/HANDOFF_OPTION_B_GEMMA4.md` |

**Result**: 23 bare excepts fixed, 2 files got loggers, 1 falsy-trap fixed, 2 hardcoded paths resolved. 5 quality gates passed.

**Gate**: ✅ `make test` (302 pass) + `grep -rn "except Exception:" src/omega/ | grep -v "logger\.\|raise\|# health"` = 4 carve-outs only + `grep -rn "/home/arcana-novai\|/media/arcana-novai" src/omega/` = 0 + `grep -rn "import asyncio" src/omega/` = 0.

---

### Phase 2: MCP Hub — Restore 34 Tools

| Aspect | Detail |
|--------|--------|
| **Model** | **DeepSeek V4 Flash** or **MiMo V2.5** — needs deeper reasoning for merging two versions of a file |
| **Risk** | 🟡 Medium |
| **Time** | 30 min |
| **Files** | `mcp_servers/omega_hub/server.py` (+ doc updates) |
| **Guide** | `docs/strategy/PHASE_MCP_HUB.md` |

**Scope**: Merge 34 tool implementations from git history (`69db713`) into current server with `custom_routes` approach.

**Gate**: `curl http://127.0.0.1:8016/health` = 200 + 34 MCP tools available + 8 HTTP routes still work.

---

### Phase 3: Horizon 2 — Observability & Forensics (LOCKED)

| Aspect | Detail |
|--------|--------|
| **Model** | **Nemotron 3 Super** or **DeepSeek V4 Flash** — architectural design decisions |
| **Risk** | 🔴 High |
| **Time** | 4-6 hours |
| **Files** | 20+ files (new systems architecture) |
| **Guide** | `docs/strategy/PHASE_HORIZON_2.md` |

**Scope**: ForensicsManager, structured JSON logging, Error Gauntlet, Qdrant wiring.

**Gate**: This phase does NOT open until Phases 1 and 2 are committed and stable.

---

## §3 Model Tier Assignments

### Tier 0: Any Model — Mechanical Work
Simple, well-defined tasks with exact file paths and line numbers. Any model with basic code ability can do these.

**Phases**: Option B (Mandate 9 fixes), documentation updates

**Pattern**:
```markdown
## File: path/to/file.py
### Line NN: Description
BEFORE:
    except Exception:
        pass
AFTER:
    except Exception as e:
        logger.warning("description: %s", e)
    # keep original fallback below
```

### Tier 1: Deep Reasoning Model — Structural Changes
Tasks requiring understanding of architecture, git history, and multi-file coordination. Needs a model with 128K+ context and strong reasoning.

**Recommended models**: MiMo V2.5, DeepSeek V4 Flash, Nemotron 3 Super, OpenCode Big Pickle

**Phases**: MCP Hub Restoration, Horizon 2 design

**Pattern**:
```markdown
## Phase: Name
### Problem
<what's wrong>

### Options
- Option A: <approach> — <pros/cons>
- Option B: <approach> — <pros/cons>

### Decision Required
Choose between Option A and Option B. Consider:
1. <factor x>
2. <factor y>
3. <factor z>
```

### Tier 2: Multi-Horizon Strategy — Architectural Decisions
Requires understanding of the entire engine, all 12 mandates, and long-term vision.

**Recommended models**: Nemotron 3 Super, MiMo V2.5

**Phases**: Horizon 2+ planning, architecture decisions

---

## §4 Rollback Protocol

Every phase has its own rollback command in its guide. The universal rollback:

```bash
# Full rollback to pre-Horizon-1 baseline
git reset --hard HEAD

# Or per-phase rollback (example for Option B)
git checkout HEAD -- src/omega/observability.py src/omega/oracle/model_gateway.py
```

---

## §5 Communication Protocol

When a phase completes, the executing agent MUST post a brief report:

```markdown
## Phase N Report

**Status**: ✅ COMPLETE / ❌ FAILED

**Files changed**: <list>

**Test result**: <make test output>

**Gates passed**:
- Gate 1: <grep result>
- Gate 2: <grep result>

**Deviations from plan**: <any differences>

**Next phase**: <name>
```

No Horizon 2 work opens without this report being reviewed.

---

*⬡ OMEGA ⬡ SOPHIA ⬡ trc_execution_roadmap ⬡ ROADMAP*
*Last updated: 2026-06-01 | Canonical: OMEGA_ENGINE.md*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_execution_roadmap | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
