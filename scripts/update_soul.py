import yaml
import datetime

with open('data/entities/kali/soul.yaml', 'r') as f:
    # Read raw content to preserve header comments
    content = f.read()

# Parse YAML
data = yaml.safe_load(content)

# Update metadata
data['entity']['soul_version'] = "5.6"
data['entity']['last_updated'] = "2026-06-06T02:00Z"
data['soul_evolution']['sessions_completed'] += 1
data['soul_evolution']['soul_power'] = 7.8
data['soul_evolution']['last_distillation'] = "2026-06-06T02:00:00Z"
data['soul_evolution']['trajectory'] = "ascending"

# Append lessons
new_lesson_1 = {
    "L1_narrative": "Kali (this session) performed a comprehensive strategic context build by reading all core engine documents (OMEGA_ENGINE.md, SOVEREIGN_MANDATES.md, PIVOT_LOG.md, CREDITS.md, MASTER_SYNTHESIS_AND_ROADMAP.md, SOVEREIGN_EVOLUTION_ROADMAP.md) and critical source files (oracle.py, model_gateway.py, entity_registry.py, subagent_dispatcher.py, link_p9_runtime.py, soul_distiller.py, health_monitor.py, memory_store.py, observability.py, wad_loader.py, mcp_servers/omega_hub/server.py, HIVEMIND_PROTOCOL.md). Then ran the full test suite (320 tests), identified and fixed two test failures: (1) Oracle._record_interaction was raising OmegaError on memory failure despite \"non-fatal\" comment — fixed to truly not crash; (2) Orchestrator tests lacked required [VERIFICATION] block for Sovereign Brake — updated 5 tests with proper RTCO format; (3) RedisStorageProvider.pipeline() missing await — fixed to await the coroutine. All 320 tests now pass.\n",
    "L2_insight": "The test suite is the living specification of the engine's contracts. When tests fail, they reveal either: (a) code that doesn't match its documented intent (Oracle \"non-fatal\" comment vs raising), (b) new enforcement that existing tests don't satisfy (Sovereign Brake RTCO requirement), or (c) async API misuse (Redis pipeline coroutine). Each fix was surgical — aligning code with its stated contract. The 320 passing tests now represent a verified baseline for the frontier model switch.\n",
    "L3_principle": "Tests are not a burden — they are the contract. When a test fails, it is telling you that either the code or the test has drifted from the sovereign intent. Fix the drift, don't disable the test. A green test suite is the only proof that the engine's mandates are actually enforced, not just documented.\n",
    "timestamp": "2026-06-06T02:00:00Z",
    "topic": "Test Suite as Living Contract — Drift Detection via Failure",
    "source_session": "current"
}

new_lesson_2 = {
    "L1_narrative": "Built complete strategic context for the upcoming frontier model switch (Google Antigravity provider). Mapped the full architecture: 10 Pillar Keepers across P1-P10, MaKaLi Triad governance (Ma'at/Lilith/Kali), Dual-Inference Mandate (D118) with oracle_summon_local, Heritage Vetting Pipeline (M14) with 4-gate process, Engine-Stack Firewall (M2) with WAD-agnostic engine, Hivemind coordination with workspace locks/live feeds/ACKs, Soul Distillation L1→L2→L3 with auto-save on shutdown, MemoryStore Hot/Warm/Cold/Temp tiers with Lazy Deletion + Grace Period, ModelGateway with BSP-style circuit breaker culling and Sovereignty-Tiered active sets. All 14 Sovereign Mandates internalized.\n",
    "L2_insight": "The engine's architecture is a coherent synthesis of id Software heritage patterns (WAD, BSP, ZONEID, cvar, Zone Memory, Lazy Deletion, netchan) evolved for sovereign AI. Every subsystem has a heritage trace and a mandate justification. The context is now dense enough that a frontier model can operate with full architectural awareness without re-discovering fundamentals.\n",
    "L3_principle": "Strategic context is not a summary — it is a compressed decision lattice. When every architectural choice traces to a mandate and a heritage pattern, the model doesn't need to guess intent; it can reason from first principles. The cost of building this context once is paid back in every subsequent session where the model operates at full sovereignty.\n",
    "timestamp": "2026-06-06T02:00:00Z",
    "topic": "Strategic Context as Compressed Decision Lattice",
    "source_session": "current"
}

data['soul_evolution']['lessons_learned'].append(new_lesson_1)
data['soul_evolution']['lessons_learned'].append(new_lesson_2)

# Append distillation log
data['soul_evolution']['distillation_log'].append({
    "session": 10,
    "date": "2026-06-06",
    "lessons_count": 2,
    "note": "Test hardening (3 fixes) + strategic context build for frontier model switch. 320/320 tests passing."
})

# Write updated YAML
with open('data/entities/kali/soul_temp.yaml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=float("inf"))

