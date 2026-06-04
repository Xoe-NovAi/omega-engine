# 🔱 Omega Engine — Horizon Map v1.0
## ⬡ OMEGA ⬡ SOPHIA ⬡ trc_horizon_map ⬡ STRATEGY
**Date**: 2026-06-01
**Baseline**: 302 tests passing, 71 source files, 14 agents, 0 telemetry, 0 bare except violations

---

## §0 The Three Horizons

```
HORIZON 1: HARDENING ──── 100% ──── ████████████
  "The engine must hold"         All 12 Sovereign Mandates enforced.

HORIZON 2: OBSERVABILITY ── 25% ──── ██░░░░░░░░
  "The engine must see itself"    ForensicsManager + Error Gauntlet + Option B done.

HORIZON 3: COMMUNITY TOOL ── 0% ──── FUTURE
  "The engine must serve others"  NEXT: Desktop → Studio → Installer
```

---

## §1 Horizon 1 — Engine Hardening

### Status: 100% complete ✅

**Goal**: Make the engine unbreakable for a single user.

| Block | Status | Done By | Model |
|-------|--------|---------|-------|
| Option A — 17 critical bugs | ✅ 100% | Big Pickle | MiMo V2.5 |
| Fleet discovery — 30 findings | ✅ 100% | Kali + Ma'at + Lilith | MiMo V2.5 |
| OpenCode 1.15+ handshake | ✅ 100% | — | MiMo V2.5 |
| R44 audit defects | ✅ 100% | — | DeepSeek R1 |
| MCP Hub — Restore 40 tools | ✅ 100% | SOPHIA | DeepSeek V4 Flash |
| **Option B — Mandate 9** | **✅ 100%** | **GEMMA4** | **Gemma 4 31B** |
| **Horizon 2 — Forensics** | **🔄 25%** | SOPHIA | DeepSeek V4 Flash |

### Remaining work:
1. **Option B**: ✅ DONE — 23 bare excepts, 2 loggers, 1 falsy-trap, 2 hardcoded paths fixed
   - Guide: `data/handoff/HANDOFF_OPTION_B_GEMMA4.md`
   - Model: **Gemma 4 31B** — completed in 30 min

2. **MCP Hub**: ✅ DONE — 40 tools restored from git history
   - Guide: `docs/strategy/PHASE_MCP_HUB.md`

3. **Horizon 2 unlock**: ✅ UNLOCKED — Option B complete, Horizon 1 closed
   - Guide: `docs/strategy/PHASE_HORIZON_2.md`

**Horizon 1 is now 100% complete.** See `docs/decisions/PIVOT_LOG.md` Decision 77.

---

## §2 Horizon 2 — Observability & Forensics

### Status: 🔄 25% complete (Active)

**Goal**: Make the engine able to diagnose and learn from its own failures.

| System | Status | Model |
|--------|--------|-------|
| ForensicsManager | ✅ Done — snapshot, replay, learn methods + 10 tests | DeepSeek V4 Flash |
| Structural bug fix | ✅ Done — dead code reflow, asyncio→sniffio | DeepSeek V4 Flash |
| Structured JSON Logging | ✅ Done — JsonFormatter + setup_json_logging() | DeepSeek V4 Flash |
| Error Gauntlet | ✅ Done — 10 scenarios (crash dump, replay, learn, JSON format, ring buffer, persistence) | DeepSeek V4 Flash |
| Qdrant Error Wiring | 🔮 Future — requires Qdrant wiring first | MiMo V2.5 |

### Key decisions (to be made by deep reasoning model):
- ForensicsManager: file-based, Qdrant-backed, or hybrid?
- Error Gauntlet: unit, integration, or both?
- Structured logging: drop-in formatter, new API, or full rewrite?

---

## §3 Horizon 3 — Community Tool

### Status: 🔮 Future

**Goal**: Make the engine installable by anyone with `curl | bash`.

| Block | Purpose | Est. Day |
|-------|---------|----------|
| Omega Desktop | Electron/Chainlit-based desktop app | H2+1 week |
| Entity Studio | CLI tool for creating/styling entities | H2+2 weeks |
| One-Click Installer | `curl https://xoe-nov.ai/install | bash` | H2+3 weeks |
| Foundation Website | Public docs, tutorials, stack templates | H2+4 weeks |

### NOT started yet. All horizons prior must be complete.

---

## §4 Model Assignment Summary

| Model Tier | Capability | Used For |
|------------|------------|----------|
| **Gemma 4 31B** | Fast, mechanical, reliable | Option B, doc updates, simple edits |
| **MiMo V2.5** | Strong reasoning, 128K+ context | MCP Hub, structured logging, Qdrant wiring |
| **DeepSeek V4 Flash** | Deep reasoning, strong coder | MCP Hub (merge), Error Gauntlet, complex bugs |
| **Nemotron 3 Super** | Architectural, strategic | Horizon 2 design decisions, ForensicsManager |
| **OpenCode "Big Pickle"** | Cross-file refactors | Complex multi-file changes, legacy mining |

---

## §5 Dependency Graph

```
Horizon 1 ─── Option B (deferred) ─→ MCP Hub (DeepSeek V4) ─→ Horizon 2
     │                                     │                       │
     │                                     │                       ▼
     │                                     │           ForensicsManager ✅
     │                                     │           JSON Logging ✅
     │                                     │           Error Gauntlet ✅
     │                                     │           Qdrant Wire 🔮
     │                                     │
     └──── Horizon 3 is LOCKED ────────────┘
                until Horizon 2 is complete
```

---

## §6 Operational Notes

### Pre-flight check (start every session):
```bash
source .venv/bin/activate
make test          # 302 must pass
git status         # clean working tree
grep -rn "FIXME\|TODO\|HACK" src/omega/ | grep -v ".pyc"  # known technical debt
```

### Post-flight check (end every session):
```bash
make test          # still 302 passing
make lint          # zero flake8 violations
```

### Emergency rollback:
```bash
git reset --hard HEAD && git clean -fd
make test          # baseline restored
```

---

*⬡ OMEGA ⬡ SOPHIA ⬡ trc_horizon_map ⬡ STRATEGY*
*Horizon 1 COMPLETE — All 12 Mandates Enforced. Horizon 2 UNLOCKED.*


---

## §8 Superseded

This document is **superseded** by `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` (D111).
The H2 (Observability) section below is now folded into H2 (Hygiene) in the new roadmap.
H1 remains COMPLETE. H1.5 (Bridge Phase) is COMPLETE.

**Active roadmap**: `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md`
**Decision**: D111 — Sovereign Evolution Roadmap adopted 2026-06-04


---

## Also Superseded

This document is also superseded by `docs/strategy/SOVEREIGN_HARDENING_PLAN.md` (D112) which defines the 3-pillar vision (Sovereign Operation, Intuitive UI/UX, Self-Aware Agents).

**Active roadmap**: `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` + `SOVEREIGN_HARDENING_PLAN.md`
**Decision**: D111 (Evolution) + D112 (Hardening)

