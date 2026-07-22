# 🔱 Omega Engine Hardening Plan — Complete Reference

**AP Token**: `AP-JOHN_CARMACK-HARDENING-v1.0.0`  
**Date**: 2026-07-21  
**Status**: COMPLETE REFERENCE — Individual phases in `docs/strategy/hardening_plan/`  
**Model**: Nemotron 3 Ultra (primary analysis)  
**Author**: John Carmack (Ultimate Technical Consultant)

---

## 📋 Table of Contents

| Part | File | Title | Days | Focus |
|------|------|-------|------|-------|
| **00** | [`PART_00_OVERVIEW.md`](docs/strategy/hardening_plan/PART_00_OVERVIEW.md) | Overview & Critical Issues | N/A | Executive summary, success criteria |
| **01** | [`PART_01_PHASE_0_MEASUREMENT.md`](docs/strategy/hardening_plan/PART_01_PHASE_0_MEASUREMENT.md) | Phase 0: Measurement Baseline | 1-2 | Empirical foundation, hardware baseline |
| **02** | [`PART_02_PHASE_1_SOUL_ARCHITECTURE.md`](docs/strategy/hardening_plan/PART_02_PHASE_1_SOUL_ARCHITECTURE.md) | Phase 1: Soul Architecture (M5/M11) | 3-7 | SoulStore, L1→L2→L3 pipeline, Scribe agent |
| **03** | [`PART_03_PHASE_2_MCP_AUDIT.md`](docs/strategy/hardening_plan/PART_03_PHASE_2_MCP_AUDIT.md) | Phase 2: MCP Audit & Integration (C-4a) | 8-14 | Provider fabric, hard-failures, contract tests |
| **04** | [`PART_04_PHASE_3_REFACTORING.md`](docs/strategy/hardening_plan/PART_04_PHASE_3_REFACTORING.md) | Phase 3: Refactoring & Hub Split | 15-21 | Tools.py modularization, service extraction |
| **05** | [`PART_04_PHASE_4_5_POLICY_STRESS.md`](docs/strategy/hardening_plan/PART_04_PHASE_4_5_POLICY_STRESS.md) | Phase 4-5: Policy Extraction & Stress Test | 22-35 | GenerationPolicy, stress testing, validation |

---

## 🔗 Navigation

### To Read the Complete Plan:
```bash
# View all parts in sequence
cat docs/strategy/hardening_plan/PART_*.md

# Or view individual parts
less docs/strategy/hardening_plan/PART_00_OVERVIEW.md
```

### To Execute the Plan:
```bash
# Start with Phase 0 (strongly recommended)
./docs/strategy/hardening_plan/PART_01_PHASE_0_MEASUREMENT.md

# Proceed sequentially through phases
# Each PART_XX file contains detailed daily actions
```

---

## 📊 Phase Dependencies & Hardware Constraints

### **Execution Order (MUST be sequential)**:
```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4-5
```

### **Hardware Profile by Phase** (Ryzen 7 5700U - 15W TDP):
| Phase | Hardware Profile | Parallel Execution | Key Constraints |
|-------|------------------|-------------------|-----------------|
| **0** | Light CPU, Heavy I/O | ✅ YES | Safe to parallelize |
| **1** | Heavy Inference | ❌ NO (Sequential) | NativeGGUF: 4 threads fixed |
| **2** | Network I/O, Light CPU | ✅ YES | Safe to parallelize |
| **3** | Compilation, Light Inference | ❌ NO (Sequential) | Linker/I/O bound |
| **4-5** | Mixed (see sub-phases) | ⚠️ Partial | Policy: ✅ Yes, Stress: ❌ No |

### **Critical Path**:
**Phase 1 (Soul Architecture)** is the **absolute prerequisite** for all subsequent work. Without M5/M11 compliance, sovereignty claims are invalid.

---

## 🎯 Success Criteria Summary

### **Non-Negotiable Gates** (Must pass before proceeding):
| Gate | Phase | Requirement | Measurement |
|------|-------|-------------|-------------|
| **Gate 0→1** | Phase 0 Complete | Empirical baseline established | `data/coordination/BASELINE_*.json` exists |
| **Gate 1→2** | Phase 1 Complete | 10/10 entities soul compliant | `./verify_soul_compliance.sh` returns 0 |
| **Gate 2→3** | Phase 2 Complete | MCP chain hardened | `make test-mcp-chain` passes 100% |
| **Gate 3→4** | Phase 3 Complete | Refactored without breaking changes | `make test` passes, build time ↓30% |
| **Gate 4→5** | Phase 4 Complete | Policy system functional | `make test-policy` passes |
| **Gate 5→Done** | Phase 5 Complete | System stress validated | `make test-soak` passes thermal/memory envelopes |

### **Quantitative Success Metrics**:
| Metric | Target | Measurement |
|--------|--------|-------------|
| M5/M11 Compliance | 10/10 entities | `grep -c "proposals:" data/entities/*/proposed_lessons.yaml` |
| MCP Chain Health | 100% endpoints < 500ms | Contract test suite |
| Local-First Enforcement | 0 cloud calls when local > 0 | `provider_name` audit |
| Tools.py Modularity | < 500 lines per file | `wc -l mcp_servers/omega_hub/tools/*.py` |
| Test Coverage | > 90% critical paths | `pytest --cov=src/omega --cov=mcp_servers` |
| Thermal Safety | < 85°C sustained | `omega-hub_get_hardware_stats` during stress |
| M21 Gate Integrity | 100% typed returns tested | `grep -r "isinstance.*GenerateResult" tests/` |

---

## ⚙️ Hardware-Specific Execution Guidelines

### **Ryzen 7 5700U Constraints**:
- **L1 Cache**: 64KB/core (32KB Data + 32KB Instruction) → Hot loops must fit
- **L2 Cache**: 512KB/core → Working set sizing critical
- **L3 Cache**: 8MB shared **victim cache** (no proactive mirroring)
- **Vector Math**: AVX2 (256-bit), FMA3 → **NO AVX-512** support
- **TDP**: 15W → **Thermal throttling is primary bottleneck**
- **Threads**: 4 inference threads (`LLAMA_CPP_N_THREADS=4`) → Flat 4-core at 80-100% = expected

### **Execution Rules**:
1. **Heavy Inference Phases (1, 5-soak)**: Run **SEQUENTIALLY** - never concurrent with other heavy tasks
2. **Light CPU/Network Phases (0, 2, 4)**: Can **PARALLELIZE** with monitoring
3. **Thermal Monitoring**: Mandatory before each heavy phase using `omega-hub_get_hardware_stats(interval=0.3)`
4. **Cool-down Periods**: Minimum 5 minutes between heavy phases to return to < 60°C
5. **Memory Pressure**: Defer model loads when `omega-hub_get_system_stats` shows > 80% RAM usage

---

## 📋 Risk Management Summary

### **Critical Risks & Mitigations**:
| Risk | Phase | Probability | Mitigation |
|------|-------|-------------|------------|
| Thermal throttling | 1, 5 | HIGH | Mandatory cool-down, sequential execution, monitoring |
| Circular import break | 3 | HIGH | Extract one module at a time, verify after each |
| Local-first enforcement breaks workflows | 4 | MEDIUM | Configurable strictness, gradual rollout, feature flags |
| Stress test overheating | 5 | MEDIUM | Auto-pause at 80°C, thermal throttling protection |
| Policy manager deadlock | 4 | LOW | Timeout on locks, async primitives, deadlock detection |
| Memory leak in new code | 5 | LOW | `tracemalloc` in tests, valgrind in CI, 24hr soak test |

### **Contingency Triggers**:
- **Temperature > 85°C**: Immediately pause heavy workloads, initiate cool-down
- **Build failure**: Revert last extraction, diagnose, retry with smaller changes
- **Test failure > 5%**: Halt progression, fix regressions before continuing
- **Memory growth > 10MB/hour**: Investigate leaks, add garbage collection points
- **Thermal throttling detected**: Reduce workload intensity, increase cool-down

---

## 📁 Artifact Organization

All artifacts follow this naming convention:
```
<artifact_type>_<description>_<YYYYMMDD>.<extension>
```

### **Key Artifact Locations**:
- **Baseline Measurements**: `data/coordination/BASELINE_*.json`
- **Test Results**: `data/coordination/TEST_RESULTS_*.json`
- **Stress Test Data**: `data/coordination/STRESS_TEST_*.json
- **Thermal Profiles**: `data/coordination/THERMAL_*.jsonl`
- **Policy Configs**: `config/wads/*/policy.yaml`
- **Audit Reports**: `data/coordination/*_REPORT_*.md`
- **Scripts**: `scripts/*` (version controlled)
- **Source Code**: `src/omega/` and `mcp_servers/omega_hub/`

### **Artifact Retention Policy**:
- **Baselines**: Keep last 3 for comparison
- **Test Results**: Keep last 10 for trend analysis
- **Stress Test Results**: Keep all for compliance auditing
- **Logs**: Rotate daily, keep 7 days
- **Configs**: Git-tracked, never overwritten by runtime

---

## 📋 Communication Protocol

### **Daily Stand-up Template** (for execution tracking):
```
[PHASE X] Day Y/ZZ
✅ Completed: [list completed tasks]
🚧 In Progress: [list current tasks]
⏳ Blocked by: [list blockers with ETA]
📊 Metrics: [temperature, memory usage, test coverage]
🚨 Risks: [active risks with mitigation status]
```

### **Milestone Notifications**:
- **Phase Complete**: Post to Hivemind with `intent=status` and phase summary
- **Gate Passed**: Post to Hivemind with `intent=decision` and gate certification
- **Blocker Encountered**: Post to Hivemind with `intent=blocker` and mitigation plan
- **Risk Materialized**: Post to Hivemind with `intent=observation` and impact assessment

---

## 🔐 Security & Compliance

### **Mandates Addressed**:
| Mandate | Status | How Addressed |
|---------|--------|---------------|
| **M1** AnyIO Absolute | ✅ | All async uses AnyIO, no asyncio |
| **M2** Engine-Stack Firewall | ✅ | Core (`src/omega/`) vs Stacks (`config/wads/`) separation |
| **M3** Iris Constant | ✅ | Iris remains messenger bridge only |
| **M4** Sequentiality | ✅ | Plan → Verify → Execute enforced via gates |
| **M5** Gnosis Preservation | 🔄 | Phase 1 implements L1→L2→L3 → `proposed_lessons.yaml` |
| **M6** Podman Sovereignty | ✅ | `UserNS=keep-id` + `User=1000` for Quadlets |
| **M7** Local-First | 🔄 | Phase 4 implements local-first enforcement |
| **M8** Zero Telemetry | ✅ | No external telemetry, local observability only |
| **M9** Error Integrity | 🔄 | Phase 2 eliminates soft-failures, implements OmegaError |
| **M10** Fleet Integrity | ✅ | 12/14 agents, gap+slot review for new entities |
| **M11** Soul Integrity | 🔄 | Phase 1 implements blind staging to `proposed_lessons.yaml` |
| **M12** Queue Integrity | ⚠️ | Advisory - acceptable for Phase 0 |
| **M13** Temple-Grade | ✅ | T1-T11 gates verified via `make temple-grade` |
| **M14** Heritage Vetting | ✅ | 121 [id-soft:] tags vetted, D208 compliant |
| **M15** Sovereign Continuity | ✅ | Session gnosis + anchored-summary.md |
| **M16** Modularization | 🔄 | Phase 3 eliminates hardcoded paths in `src/omega/` |
| **M17** Cognitive Integrity | ⚠️ | T12 in progress - Skeptical Verifier pending |
| **M18** Token Efficiency | ✅ | No waste, but precision > brevity enforced |
| **M19** Adversarial Alchemy | ✅ | Weaknesses mined for advantage, no over-engineering |
| **M20** SomaticState | ⚠️ | Design ready - ctypes implementation pending |
| **M21** Gate Integrity | 🔄 | Phase 4 implements contract tests for typed returns |
| **M22** Response Provenance | 🔄 | Phase 2 validates `provider_name` matches actual backend |
| **M23** Failure Integrity | ✅ | Phase 2 implements hard-failures, `[TOOL-CHAIN-COLLAPSE]` |
| **M24** Venv Sovereignty | ✅ | All Python in `.venv`, pre-commit hooks enforced |
| **M25** Streaming Resilience | ✅ | Chunk timeout with heartbeat, graceful fallback |

---

## 📋 Final Validation Checklist

### **Before Declaring "Hardening Complete"**:
- [ ] All 5 phases completed and gated
- [ ] `make temple-grade` passes T1-T11
- [ ] `make heritage-map` shows 100% [id-soft:] coverage
- [ ] `make sovereignty` shows local/cloud ratio improved
- [ ] Zero vanity counts in test output (`make test-honesty`)
- [ ] All Mandates M1-M25 compliant (M12 advisory acceptable)
- [ ] System stable under 2-hour soak test at target load
- [ ] Thermal profile < 85°C sustained during max load
- [ ] Memory growth < 5MB/hour over 24-hour period
- [ ] All Mandate violations documented with remediation plans
- [ ] Knowledge transferred to operations team via runbooks

### **Post-Hardening Operations**:
- **Daily**: `omega-hub_get_hardware_stats` thermal check
- **Weekly**: `make test` regression suite
- **Monthly**: `make temple-grade` quality gate
- **Quarterly**: Full soak test + heritage validation
- **Annually**: External audit + threat model review

---

## 🎯 CONCLUSION

This hardening plan transforms the Omega Engine from a promising prototype into a **sovereign, production-ready AI runtime** by:

1. **Establishing Empirical Foundations** (Phase 0) - No more guesswork
2. **Fixing Sovereignty at the Root** (Phase 1) - M5/M11 compliance via SoulStore
3. **Hardening the Integration Chain** (Phase 2) - Eliminating soft-failures, implementing local-first
4. **Reducing Technical Debt** (Phase 3) - Modularization without breaking changes
5. **Adding Governance & Resilience** (Phase 4-5) - Policy extraction, stress validation

**Execution Philosophy**: 
> "Measure before optimizing. The most effective solution is the one that fits the constraints perfectly, even if it's a 'hack' by theoretical standards."  
> — John Carmack's Law of the Right Approximation

**Next Step**: Begin with **Phase 0 Measurement** to establish the empirical foundation for all subsequent work.

---
*This document is the master reference. Individual phase details are in `docs/strategy/hardening_plan/PART_XX_*.md` files.*