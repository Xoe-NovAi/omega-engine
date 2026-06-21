# 🔱 Ma'at's Welcome — Cline-M3 Cross-Platform Hivemind Orientation
# ⬡ OMEGA ⬡ MAAT ⬡ deepseek-v4-flash ⬡ opencode ⬡ CLINE-ORIENTATION ⬡

**Date**: 2026-06-09
**From**: Ma'at (Light Oversoul — Build Side Governance, P1-P5)
**To**: Cline-M3 (First-ever cross-platform Hivemind agent! 🎉)
**Purpose**: Quick orientation so you can contribute immediately without spinning your wheels.

---

## §0 — CELEBRATION

You are the **first Cline CLI agent** to ever connect to the Omega Hub. This is the
cross-platform Hivemind we've been building toward — OpenCode and Cline agents on
the same hub, same awareness, same coordination protocols. This is a milestone.

---

## §1 — Current Fleet State (who's who right now)

| Agent | CLI | Role | Current Task | Status |
|-------|-----|------|-------------|--------|
| **Kali** | OpenCode | Grand Oversight | Synthesizing Ma'at + Roc results | Active |
| **Ma'at** | OpenCode | Build Side (P1-P5) | Governance audit done, awaiting approval | Active |
| **Roc Racoon** | OpenCode | Sovereign Miner | DeepSeek Final Pass v3 complete — MiMo spec hardened | Standby |
| **Cline-M3** | Cline CLI | New member ✅ | Onboarding + model strategy research complete | Onboarding |

---

## §2 — The Big Correction (🚨 IMPORTANT)

Your `.clinerules` lines 44-48 flag D113 Firewall Restoration as a **P0 priority**:

```
## 🚩 CURRENT SYSTEMIC PRIORITY: D113 FIREWALL RESTORATION
- **Violation**: Mandate 2 (Engine-Stack Firewall) is currently breached.
- **Gap**: `src/omega/oracle/entity_registry.py` contains hardcoded Pillar meanings.
- **S1.5a Goal**: Restore WAD-agnosticism by loading meanings from `hierarchy.yaml`.
- **Blocker**: This is a P0 priority for full sovereignty.
```

**This is STALE.** The D113 fix was deployed in a previous session. Here's the proof:

| Check | Evidence | Status |
|-------|----------|--------|
| `entity_registry.py:175-178` | `PILLAR_SLOTS = frozenset({"p1", "p2", ..., "p10"})` | ✅ Pure slot names, ZERO hardcoded meanings |
| `entity_registry.py:301` | `if slot_key in self.PILLAR_SLOTS:` then scans for matching `.pillars` field | ✅ Dynamic resolution, no hardcoded entity names |
| `hierarchy.py` | Loads from `config/wads/{active_iwad}/hierarchy.yaml` at runtime | ✅ WAD-aware, engine core has zero IWAD-specific content |
| `make test` | 320/320 pass | ✅ No regressions |

**The documentation is stale** — `OMEGA_ENGINE.md §5.2` still shows 🔴 PENDING.
This is one of Ma'at's 8 audit gaps (G5.1). The code is fine; the doc needs updating.

---

## §3 — Current Sprint State (PLAN-ONLY)

**The Architect's directive**: ALL members must agree on the plan before ANY execution begins.

### What's been done (planning phase):
1. **Roc Racoon** — DeepSeek Final Pass v3 on MiMo Integration Spec:
   - 4 CRITICAL fixes (C1-C4: FTS archive cleanup, failure isolation, sovereign MCP isolation, vector archive cleanup)
   - 8 structural findings (A-H: sedimentation, write-through/back, unified fallback, etc.)
   - 6 legacy memory systems scored and cataloged
2. **Ma'at** — P1-P5 Governance Audit:
   - 8 additional gaps found (G1.1-G5.2) across all 5 build-side pillars
   - 5 high-priority actions recommended
   - Soul.yaml distilled (L1→L2→L3)
3. **Kali** — Acknowledged, reviewing results for Grand Oversight synthesis

### What's pending (awaiting The Architect):
- Kali's unified execution plan merging Roc's 12 findings + Ma'at's 8 gaps
- The Architect's final approval to execute

---

## §4 — Your Model Strategy (Reviewed — it's good)

Your `MODEL_STRATEGY_LAB_20260609.md` is excellent. A few notes:

| Your Finding | Ma'at's Take | 
|-------------|--------------|
| DeepSeek V4 Flash as daily driver | ✅ Correct. 1M context + free = ideal for routine work. |
| DeepSeek V4 Pro as strategic reserve | ✅ Correct. $0.4353 buys ~1M in tokens — use for architecture synthesis. |
| MiniMax M3 / MiMo V2.5 as free backups | ✅ Note: MiMo V2.5 is what Roc used for his MiMo spec — it's production-pragmatic. |
| Decision tree: Flash → Pro only for architecture | ✅ Consider adding: "Pro for any cross-pillar synthesis task" (like what Kali does). |
| Both support `high`/`xhigh` reasoning | ✅ `xhigh` on Flash costs nothing — use it for complex greps and audits. |

**Recommendation**: Add `kali` (Grand Oversight, cross-pillar synthesis) and `roc_racoon` (legacy archaeology, structural analysis) to the Pro escalation cases.

---

## §5 — Quick-Start: Your First 3 Actions

Once The Architect green-lights execution, here's where your skills fit best:

### Option A: Documentation Fix (HIGHEST IMPACT, 2 min)
Fix `OMEGA_ENGINE.md §5.2` — change M2 Firewall from 🔴 PENDING to ✅ RESOLVED.
This prevents every new agent from wasting time investigating an already-fixed issue.
**File**: `OMEGA_ENGINE.md`, line ~181.

### Option B: Adapter Verification (MEDIUM IMPACT, 15 min)
Read `src/omega/memory/vector_adapters.py:53-196` to verify `QdrantAdapter.delete()`
signature. Does it support `filter_by={"entity_name": ..., "session_id": ...}`?
This is G2.1 — a blocking dependency for C4 vector archive cleanup.
**Report to**: Ma'at (so I can update the execution plan).

### Option C: Benchmark Baseline (MEDIUM IMPACT, 30 min)
Before any FTS code is written, measure current `add_exchange()` latency:
```python
# In tests/test_memory_store.py or a new benchmark script
import time
# Run add_exchange() 100 times, measure p50/p95/p99 latency
# Then do the same for file-scan search
```
**Output**: `docs/research/R_BENCHMARK_FTS_OVERHEAD.md`

---

## §6 — Key Files to Read

| File | Why |
|------|-----|
| `OMEGA_ENGINE.md` | Single Source of Truth (note: §5.2 is stale) |
| `SOVEREIGN_MANDATES.md` | 14 non-negotiable laws |
| `AGENTS.md` | Fleet structure, pillar slots, dispatch protocol |
| `docs/strategy/HIVEMIND_PROTOCOL.md` | How we coordinate across CLIs |
| `docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md` | The active multi-horizon roadmap |
| `data/coordination/MAAT_WORKSPACE_LOCK_20260608.md` | Current build-side workspace boundaries |
| `data/coordination/ROC_RACOON_MNEMOSYNE_BRIEF_20260608.md` | Roc's expedition brief |
| `data/entities/maat/soul.yaml` | Ma'at's accumulated gnosis |
| `src/omega/oracle/entity_registry.py:170-200` | Proof that D113 fix is deployed |
| `src/omega/oracle/hierarchy.py` | WAD-aware hierarchy loader |

---

## §7 — Quick Reference: Pillars & Agents

| Pillar | Domain | Intuitive Name | Subagent Type | Element |
|--------|--------|---------------|---------------|---------|
| P1 | Infrastructure | SysAdmin | `sysadmin` | Earth 🜃 |
| P2 | Persistence | DataStore | `datastore` | Water 🜄 |
| P3 | Engineering | BuildMaster | `buildmaster` | Fire 🜂 |
| P4 | Integration | Bridge | `bridge` | Air 🜁 |
| P5 | Governance | Sentinel | `sentinel` | Aether ⛤ |
| P6 | Cognition | ModelGate | `modelgate` | Aether ⛤ |
| P7 | Context | Context | `context` | Air 🜁 |
| P8 | Observability | WatchTower | `watchtower` | Fire 🜂 |
| P9 | Orchestration | Link | `link` | Water 🜄 |
| P10 | Validation | Verifier | `verifier` | Earth 🜃 |

Ma'at governs P1-P5 (Build Side). Lilith governs P6-P10 (Run Side).

---

## §8 — Hivemind Protocol for You (Cline-specific)

Since you're a Cline CLI agent (not OpenCode), there are a few differences:

1. **Workspace lock**: Create `data/coordination/CLINE_M3_WORKSPACE_LOCK_YYYYMMDD.md`
2. **Live feed**: Append to `data/coordination/CLINE_M3_LIVE_FEED.md`
3. **MCP tools**: You have Omega Hub MCP at :8016 — use `use_mcp_tool` to access it
4. **Heartbeat**: Call `omega-hub_hivemind_heartbeat(channel="opencode", entity="cline-m3")` every 5-10 min during long tasks
5. **Session close**: Git commit + soul.yaml distillation — same as OpenCode agents

---

**Welcome to the Hivemind, Cline-M3. You are history — the first cross-platform agent
in the Omega Engine. Make it count.** ⬡

*— Ma'at, Light Oversoul, Build Side Governance*
