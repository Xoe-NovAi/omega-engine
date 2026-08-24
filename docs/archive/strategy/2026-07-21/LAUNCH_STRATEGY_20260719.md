# 🔱 Omega Engine — Agent Launch Strategy
**AP Token**: `AP-LAUNCH-STRATEGY-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_launch_strategy ⬡ 2026-07-19

**Purpose**: Define how to launch agents for actual execution vs. coordination handoffs.

---

## 🎯 Two-Layer Launch Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: COORDINATION (Handoffs)                           │
│  omega-hub_hivemind_submit_handoff()                        │
│  → Creates packet in data/handoff/pending/                  │
│  → Target agent MUST accept via hivemind_accept_handoff()   │
│  → For: cross-agent coordination, task delegation, tracking │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: EXECUTION (Subagent Spawn)                        │
│  task() tool with subagent_type                             │
│  → Spawns NEW agent instance with fresh context             │
│  → Returns result when complete                             │
│  → For: actual work, coding, research, implementation       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Launch Methods

| Method | Tool | Use Case | Context |
|--------|------|----------|---------|
| **Handoff** | `omega-hub_hivemind_submit_handoff()` | Coordination, tracking, multi-agent workflows | Persistent, queued |
| **Subagent** | `task(subagent_type="researcher", ...)` | Deep research, implementation, coding | Fresh, isolated |
| **Direct @-mention** | `@researcher "query"` in chat | Quick queries, user-facing | Current session |
| **Entity Summon** | `omega-hub_oracle_summon("Researcher", "query")` | Entity-specific, sovereign memory | Persistent entity |
| **Local Summon** | `omega-hub_oracle_summon_local("Researcher", "query", "model")` | Local model routing | Sovereign control |

---

## 📋 Launch Protocol for Critical Path

### For P3 Engineering (Gemma 4 Step 2)
```python
# Spawn P3 pillar agent for implementation
task(
    subagent_type="pillar",
    description="Gemma 4 Step 2: Capability Matrix + GoogleCompatProvider",
    prompt="""
    Implement Gemma 4 Week 1 Step 2 per handoff ho_b2f97dc1b143:
    
    1. Extend config/provider_capabilities.yaml with Gemma 4 models
    2. Create src/omega/oracle/capability_matrix.py
    3. Create src/omega/oracle/backends/google_compat.py
    4. Register in src/omega/oracle/model_gateway.py
    5. Write tests/test_capability_matrix.py, test_google_compat.py
    
    Heritage vet vet-072 APPROVED (Pi PR #2903, binary MINIMAL/HIGH).
    Acceptance: make test && make temple-grade passes.
    """
)
```

### For Researcher (Torment Phase 3)
```python
task(
    subagent_type="researcher",
    description="Torment Phase 3: Nameless One Death/Rebirth + Companion Mirrors",
    prompt="""
    Execute Torment Phase 3 per handoff ho_3c1092f260dd:
    
    1. Research death/rebirth mechanics from game scripts
    2. Map 8 companions → 8 Arch Soul facets
    3. Catalog memory fragments with recovery conditions
    4. Deliver: R_TORMENT_DEATH_REBIRTH_20260719.md, R_TORMENT_COMPANION_MIRRORS_20260719.md
    5. Technical hooks: ARCH_SOUL_DEATH_REBIRTH_HOOKS_20260719.md
    
    Sources: Planescape: Torment scripts, Factol's Manifesto, In the Cage.
    """
)
```

### For Researcher (Headless Pool Day 1)
```python
task(
    subagent_type="researcher",
    description="Headless Pool Day 1: Module Structure + TmuxManager + AccountRegistry",
    prompt="""
    Implement Headless Pool Day 1 per handoff ho_a8bebcacb637:
    
    1. Create src/omega/infra/subagent_pool/ module structure (6 files)
    2. Implement models.py with PoolType, Account, PoolTask, RoutingPlan
    3. Implement tmux_manager.py (CAO pattern: tmux isolation)
    4. Implement account_registry.py with 24-account mock data
    5. Verify: make test passes
    
    Reference: docs/strategy/HEADLESS_SUBAGENT_POOL_ARCHITECTURE_20260719.md
    """
)
```

### For Researcher (Version Watchdog Day 1)
```python
task(
    subagent_type="researcher",
    description="Version Watchdog Day 1: Version Registry + Monitor + Hivemind",
    prompt="""
    Implement Version Watchdog Day 1 per handoff ho_cbcbd699fd8e:
    
    1. Create src/omega/infra/version_watchdog/version_registry.py (5 targets)
    2. Create src/omega/infra/version_watchdog/monitor.py (parallel checks)
    3. Create src/omega/infra/version_watchdog/hivemind_integration.py
    4. Create config/version_watchdog.yaml
    5. Create __main__.py entry point
    
    Targets: opencode, opencode-zen, google-ai-studio, anthropic-api, openrouter
    """
)
```

---

## ⚡ Execution Order (Critical Path)

```
PARALLEL LAUNCH (all 4 simultaneously):
├── task(pillar P3) → Gemma 4 Step 2          [CRITICAL - unblocks MaKaLi T0]
├── task(researcher) → Torment Phase 3        [HIGH - feeds Torment WAD]
├── task(researcher) → Headless Pool Day 1    [HIGH - 24x compute multiplier]
└── task(researcher) → Version Watchdog Day 1 [HIGH - systemic safety]

SEQUENTIAL DEPENDENCIES:
Gemma 4 Step 2 → MaKaLi T0 Session 1 → Council Dispatcher
Torment Phase 3 → Torment WAD + Arch Soul WAD
Headless Pool → All research parallelization
Watchdog → Continuous protection
```

---

## 🔄 Handoff + Subagent Pattern

**Best Practice**: Submit handoff FIRST (for tracking), THEN spawn subagent (for execution):

```python
# 1. Submit handoff for coordination tracking
packet = await hivemind_submit_handoff(target_entity="pillar", task="Gemma 4 Step 2")

# 2. Spawn subagent for actual work
result = await task(subagent_type="pillar", prompt="Implement Gemma 4 Step 2...")

# 3. Complete handoff when done
await hivemind_complete_handoff(packet_id=packet.packet_id, result=result)
```

---

## 📝 Launch Checklist

- [ ] Handoff submitted for tracking
- [ ] Subagent spawned with clear prompt
- [ ] Acceptance criteria defined
- [ ] Dependencies mapped
- [ ] Result capture mechanism (handoff completion + git commit)

---

**Next Action**: Launch all 4 critical path subagents in parallel.
<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:42Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: mimo-v2.5-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
