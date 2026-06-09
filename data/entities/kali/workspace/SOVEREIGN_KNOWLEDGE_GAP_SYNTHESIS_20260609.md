# 🔱 Sovereign Knowledge Gap Synthesis — Deep Discovery Report
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ trc_gap_synthesis ⬡ PHASE-II

**Date**: 2026-06-09
**Engine Version**: 2.2.0 | **Hub Version**: 2.2.0
**Baseline**: 320 tests passing · 72 source files · 19,376 LOC
**Models Used**: DeepSeek V4 Flash (primary), Gemma 4 31B (prior session), 5 parallel research subagents

---

## Executive Summary

A 5-agent parallel deep-dive discovered that the Omega Engine is **structurally sound** but has a systemic **documentation-vs-reality gap**. The most critical finding: the **BSP-style circuit breaker culling pattern** (CREDITS.md §1.2, §1.26) is documented as live but is **never wired in production** — all 5 `ModelGateway()` instantiation sites omit the `health_monitor` parameter.

---

## §1 Critical Findings (Actionable < 10 lines each)

### C1-C2: BSP Culling is Mapped, NOT Live [CRITICAL]

The `_precheck_provider()` breaker check at `model_gateway.py:552` is the heart of the id Software BSP culling pattern (O(1) check skips dead providers). However, **`self._health_monitor` is `None` in all production paths** because:

| Site | File | Line | Issue |
|------|------|------|-------|
| Oracle | `oracle.py` | 83-84 | `ModelGateway()` receives NO `health_monitor`. Orphan `HealthMonitor()` created but never passed. |
| Gateway server | `gateway/server.py` | 68 | Same |
| Observability | `observability.py` | 305 | Same |
| Orchestrator | `orchestrator.py` | 368 | Same |
| Discovery | `library/discovery.py` | 82 | Same |

**Tests prove the logic correct** — they manually wire `gateway._health_monitor = hm` — but production never does. **Fix**: 8 lines across 5 files.

**Cascading impact**: The TriageRouter's latency-based routing, availability checks, and quota tracking are also non-functional because `HealthMonitor` providers dict is empty even if wired.

### C3: BSP Inline Tag Missing [MEDIUM]

`model_gateway.py:538-569` — `_precheck_provider()` has extensive BSP-pattern comments but NO `[id-soft: doom-1993] Lattice-Culling` inline tag. Technical M14 violation.

### C4: Memory Architecture Documentation Falsified [HIGH]

CREDITS.md §1.14 claims:
- SQLite warm tier → **Reality**: JSON files
- YAML cold tier → **Reality**: gzipped JSON
- `HOT_TTL=300`, `WARM_TTL=3600`, `COLD_TTL=86400` → **Fabricated**: zero references in any file
- TTL-based promotion/demotion → **Missing**: no lifecycle management
- Temp "not yet implemented" → **Code exists** (50 lines) but is dead code (zero callers)
- `trace_exchange()` → **M12 violation**: direct write, no atomic tmp+rename

### C5: Soul Distillation Session-End Hook is Empty [MEDIUM]

`oracle.py:597-602` — `_track_soul_evolution()` is an empty stub. The full 280-line `SoulDistiller.distill_and_save()` pipeline exists but is NEVER triggered at session end. M5/M11 gap.

---

## §2 M2 Firewall Audit — 6 Cracks, No Breach

| # | Severity | File | Line | Description |
|---|----------|------|------|-------------|
| V1 | MED | `oracle.py` | 81 | Hardcoded `"kali"` entity name as fallback |
| V2 | LOW | `entity_workspace.py` | 268 | Hardcoded `"arcana_novai"` IWAD name |
| V3 | LOW | `feed_utils.py` | 242 | Agent-specific bypass for `"kali"` |
| V4 | LOW | `entity_registry.py` | 187,191 | Hardcoded `"_omega_default"` fallback |
| V5 | LOW | `hierarchy.py` | 39,43,46 | Same fallback |
| V6 | LOW | `oracle_cli.py` | 69,89 | CLI help text mentions IWAD name |

**Ratio**: 86% config-driven (31 YAML entities : 6 hardcoded references)  
**Directionality**: ✅ Unidirectional — no reverse imports from `config/` to `src/omega/`

---

## §3 Mandate Enforcement Matrix

| Grade | Count | Mandates |
|-------|-------|----------|
| **A** (CI-enforced) | 4 | M1 (AnyIO), M8 (Telemetry), M9 (Errors), M14 (Heritage) |
| **B** (Code+Makefile, no CI) | 4 | M6 (Podman), M7 (Local-First), M12 (Queue), M13 (Temple-Grade) |
| **C** (Compliant, no enforcement) | 3 | M2 (Firewall), M3 (Iris), M10 (Fleet) |
| **D** (Infra exists, stub trigger) | 2 | M5 (Gnosis), M11 (Soul) |
| **F** (No enforcement) | 1 | M4 (Sequentiality) |

---

## §4 Test Coverage — 68% Untested

49 of 72 source files have zero tests. Critical uncovered infrastructure:

| File | LOC | Why Critical |
|------|-----|--------------|
| `errors.py` | 151 | Every OmegaError subtype — zero tests |
| `cvar_table.py` | 490 | All ZONEID constants + cvar_get/set — zero tests |
| `soul_distiller.py` | 384 | L1→L2→L3 distillation (M11 mandate) — zero tests |
| `subagent_dispatcher.py` | 350 | HandoffPacket + CAPABILITY_REGISTRY — zero tests |
| `link_p9_runtime.py` | 398 | Agent presence + handoff queue — zero tests |
| `cli/oracle_cli.py` | 672 | All `omega` CLI commands — zero tests |

Infrastructure issues: `test_gateway_server.py` uses `@pytest.mark.asyncio` (M1 violation), no `.coveragerc`, no coverage threshold in CI.

---

## §5 Priority Fix Queue

| Rank | Fix | Effort | Impact | Status |
|------|-----|--------|--------|--------|
| 1 | Wire `health_monitor` to `ModelGateway` | 8 lines | Unlocks BSP culling + circuit breakers | 🔴 OPEN |
| 2 | Correct CREDITS.md §1.14 | 15 lines | Fix 5 factual errors | 🔴 OPEN |
| 3 | Add `[id-soft:]` tag to `_precheck_provider()` | 1 line | Close M14 inline-tag gap | 🟡 OPEN |
| 4 | Un-stub `_track_soul_evolution()` | 10 lines | Activate M5/M11 session-end distillation | 🟡 OPEN |
| 5 | Add `make temple-grade` to CI | 1 line | Close M13 CI gap | 🟡 OPEN |
| 6 | Fix V1 — hardcoded "kali" in oracle.py | 2 lines | Close largest M2 crack | 🟡 OPEN |
| 7 | Fix `test_gateway_server.py` asyncio→anyio | 1 line | Clean M1 test violation | 🟢 OPEN |

---

*⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ trc_gap_synthesis ⬡ PHASE-II*
