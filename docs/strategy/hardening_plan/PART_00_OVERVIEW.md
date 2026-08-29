# 🔱 Omega Engine Hardening Plan — Overview

**AP Token**: `AP-JOHN_CARMACK-HARDENING-v1.0.0`  
**Date**: 2026-07-21  
**Author**: John Carmack (Ultimate Technical Consultant)  
**Model**: Nemotron 3 Ultra (primary analysis)  
**Status**: RECORDED — Awaiting Execution Authorization

---

## 📋 Executive Summary

This plan addresses **7 critical issues** identified in the MCP audit and architecture review, organized into **5 phases** over **35 days** with hardware-aware scheduling.

**Core Philosophy**: First-principles engineering. No cargo-cult patterns. Right approximation over theoretical perfection. Empirical validation at every gate.

---

## 🚨 Critical Issues Summary

| # | Issue | Severity | Root Cause | Mandate |
|---|-------|----------|------------|---------|
| 1 | Integration Chain Vulnerability | **CRITICAL** | File-Hivemind fallback as primary | M23, M9 |
| 2 | Tools.py Monolith (127K lines) | **HIGH** | Architectural drift | M16, M2 |
| 3 | Provider Fabric Stubbed | **HIGH** | Cargo-cult cloud integration | M7, M22 |
| 4 | MCP Client Hardcoded | **MEDIUM** | Unverified assumption | M23 |
| 5 | Soul Architecture (M5/M11) | **CRITICAL** | 0/10 pillars writing proposed_lessons.yaml | M5, M11 |
| 6 | Hub Split Blockers | **HIGH** | Phase Γ prerequisites | M16 |
| 7 | Policy Extraction Missing | **MEDIUM** | Governance incompleteness | M21 |

---

## 🎯 Success Criteria (Measurable, Not Aspirational)

| Metric | Target | Measurement |
|--------|--------|-------------|
| M5/M11 Compliance | 10/10 entities write `proposed_lessons.yaml` | `grep -c "proposals:" data/entities/*/proposed_lessons.yaml` |
| MCP Chain Health | 100% endpoints < 500ms | Contract test suite |
| Local-First Enforcement | 0 cloud calls when local capacity > 0 | `provider_name` in `GenerateResult` audit |
| Tools.py Modularity | < 500 lines per tool file | `wc -l mcp_servers/omega_hub/tools/*.py` |
| Test Coverage | > 90% critical paths | `pytest --cov=src/omega --cov=mcp_servers` |
| Thermal | < 85°C sustained | `omega-hub_get_hardware_stats` during stress |
| M21 Gate Integrity | 100% typed returns have contract tests | `grep -r "isinstance.*GenerateResult" tests/` |

---

## 📁 Plan Structure (5 Parts)

| Part | File | Content |
|------|------|---------|
| **00** | `PART_00_OVERVIEW.md` | This file — executive summary, success criteria |
| **01** | `PART_01_PHASE_0_MEASUREMENT.md` | Phase 0: Empirical baseline (Days 1-2) |
| **02** | `PART_02_PHASE_1_SOUL_ARCHITECTURE.md` | Phase 1: Soul Architecture (Days 3-7) |
| **03** | `PART_03_PHASE_2_MCP_AUDIT.md` | Phase 2: MCP Audit & Integration (Days 8-14) |
| **04** | `PART_04_PHASE_3_REFACTORING.md` | Phase 3: Refactoring & Hub Split (Days 15-21) |
| **05** | `PART_05_PHASE_4_5_POLICY_STRESS.md` | Phase 4-5: Policy & Stress Test (Days 22-35) |

---

## ⚙️ Hardware Constraints (Ryzen 7 5700U — 15W TDP)

| Constraint | Value | Impact |
|------------|-------|--------|
| L1 Cache | 64KB/core (32K D + 32K I) | Hot loops must fit |
| L2 Cache | 512KB/core | Working set sizing |
| L3 Cache | 8MB shared **victim cache** | No proactive mirroring |
| Vector Math | AVX2 (256-bit), FMA3 | **NO AVX-512** |
| TDP | 15W | Thermal throttling = primary bottleneck |
| Threads | 4 inference threads (LLAMA_CPP_N_THREADS=4) | Flat 4-core at 80-100% = expected |

**Scheduling Rule**: Heavy inference phases (SoulStore, Stress Test) run **sequentially**. Light phases (MCP Audit, Policy) can parallelize.

---

## 🔄 Phase Overview

```
PHASE 0 (Days 1-2): MEASUREMENT
├── Hardware baseline
├── Current test suite analysis
├── Integration chain mapping
└── Thermal profiling

PHASE 1 (Days 3-7): SOUL ARCHITECTURE (M5/M11)
├── SoulStore implementation (fcntl + atomic + fsync + actor)
├── L1→L2→L3 distillation pipeline
├── Scribe agent deployment
└── 10/10 entity compliance

PHASE 2 (Days 8-14): MCP AUDIT & INTEGRATION (C-4a)
├── Integration chain vulnerability remediation
├── Provider fabric implementation
├── MCP client configurability
├── SearXNG/Firecrawl/Exa endpoint validation
└── Hard-failure patterns

PHASE 3 (Days 15-21): REFACTORING & HUB SPLIT
├── Tools.py → modular tool packages
├── Server.py tool loading mechanism
├── Dependency injection cleanup
├── Circular import elimination
└── Plugin architecture

PHASE 4 (Days 22-28): POLICY EXTRACTION & GOVERNANCE
├── Policy extraction from generate()
├── Cvar-style runtime tunability
├── Oracle DI testability
├── Contract test coverage

PHASE 5 (Days 29-35): STRESS TEST & VALIDATION
├── Full integration chain stress
├── Thermal soak test
├── Chaos engineering (provider failures)
├── Final compliance audit
└── Production readiness sign-off
```

---

## 🚨 Risk Mitigation (Specific, Not Generic)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Thermal throttling during SoulStore | **HIGH** | Phase delay | Mandatory cool-down, sequential execution, monitoring |
| Circular import break during refactor | **MEDIUM** | Build failure | One submodule at a time, `make test` after each |
| SearXNG MCP server unavailable | **LOW** | `[TOOL-CHAIN-COLLAPSE]` | Document in `SYSTEM_FAILURE_LOG.md`, file-Hivemind fallback |
| Provider fabric local-first violation | **MEDIUM** | M7 violation | Admission control semaphore, CI gate on `provider_name` |
| Soul distillation OOM | **MEDIUM** | Data loss | `MALLOC_ARENA_MAX=2`, atomic writes, crash simulation tests |

---

## 📋 Confidence Summary

| Phase | Confidence | Primary Source |
|-------|------------|----------------|
| Phase 0: Measurement | **10/10** | Hardware specs, empirical mandate |
| Phase 1: Soul Architecture | **9/10** | M5/M11 mandate, Zone Memory pattern |
| Phase 2: MCP Audit | **9/10** | C-4a deadline, contract test pattern |
| Phase 3: Refactoring | **8/10** | Proxy architecture analysis |
| Phase 4: Policy | **7/10** | Cvar pattern, DI pattern |
| Phase 5: Stress Test | **8/10** | Hardware constraints, empirical validation |

---

## ❓ Questions for User (Before Execution)

1. **Start with Phase 0 measurement?** (Recommended — empirical baseline)
2. **Parallelize any phases?** (Hardware says no for heavy phases)
3. **Record plan to `docs/strategy/HARDENING_PLAN_NEURON3.md`?** (After approval)
4. **Delegate any phases to specialized agents?** (e.g., `@verity` for contract tests, `@pillar P3` for refactoring)

---

**Next**: See `PART_01_PHASE_0_MEASUREMENT.md` for Phase 0 detailed actions.