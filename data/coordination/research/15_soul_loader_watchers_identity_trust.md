<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Soul Loader, Filesystem Watchers, Identity Fluidity, Anti-Spiral, Lattice Trust — Deep Research
**AP Token**: `AP-P1-BATCH3-20260726`
**Date**: 2026-07-26 | **Priority**: P1
**Researcher**: Sovereign Researcher

---

## Gap 1: Soul Loader (R22)

### Executive Summary

SoulLoader exists (509 lines) with PUBLIC/BONDED/PRIVATE split. SoulValidator enforces v6.1 schema. SoulEditHistory provides audit trail. Duplicate loader paths exist in soul_utils.py and entity_workspace.py bypassing SoulLoader.

### Components

| Component | Status |
|-----------|--------|
| SoulLoader | ✅ Implemented (509 lines) |
| SoulValidator | ✅ Implemented |
| SoulEditHistory | ✅ Implemented |
| SoulHistoryManager | ✅ SHA-256 hash-chained |
| Auto-migration v6.0→v6.1 | ❌ Not wired |

### Issues

1. No deep merge strategy (public/private loaded separately)
2. Duplicate loader paths bypass SoulLoader
3. No schema version auto-migration
4. Validator skips strict checks for legacy souls

### Effort: ~12h

---

## Gap 2: Filesystem Watchers (R12)

### Executive Summary

No config hot-reload. No soul.yaml file watcher. HMCWatcher exists for coordination events but not for config/soul. Final Inspection Report flags "inotify Portability" as High risk.

### Existing Watchers

| Watcher | Scope |
|---------|-------|
| HMCWatcher | data/coordination/ (anyio.Path.watch()) |
| RegressionWatcher | MetricsDB polling (5min) |
| MCP Watchdog | MCP health endpoint polling |

### Missing

- No config hot-reload
- No soul.yaml file watcher
- No WAD hot-reload
- No inotify/watchdog/polling for config changes

### Effort: ~16h

---

## Gap 3: Identity Fluidity Temporal (R_CG01)

### Executive Summary

Audit trail exists (SoulEditHistory, SoulHistoryManager) but no temporal identity queries. No persona versioning. E-0 Identity Fluidity not started (depends on C-1' SoulStore).

### Existing

| Component | Status |
|-----------|--------|
| SoulEditHistory | ✅ Field-level audit trail |
| SoulHistoryManager | ✅ SHA-256 hash-chained |
| evolution.incarnation | ✅ In soul.yaml |
| Temporal identity queries | ❌ Not implemented |
| Persona versioning | ❌ Not implemented |
| Identity Fluidity Engine (E-0) | ❌ Not started |

### Effort: ~24h

---

## Gap 4: Research Loop Anti-Spiral (R24)

### Executive Summary

ConvergenceDetector implemented with 4 conditions. IterativeRAG has MAX_ITERATIONS=3. IterativeResearcher has max_iterations=3 + confidence_threshold=0.8. No token budget limit. No duplicate detection.

### Convergence Conditions

| Condition | Status |
|-----------|--------|
| Multi-source verification | ✅ Working |
| Claim exhaustion | ✅ Working |
| Contradiction flagging | ✅ Working |
| Depth ceiling | ✅ Working |

### Missing

- No token budget limit
- No duplicate detection
- No query similarity check
- Depth ceiling hardcoded (not configurable)

### Effort: ~8h

---

## Gap 5: Lattice Trust (R_CG13)

### Executive Summary

SPIFFE identity exists but no trust scoring. CapabilityRegistry uses self-reported confidence_score (not earned trust). No reputation system. No trust propagation or decay.

### Existing

| Component | Status |
|-----------|--------|
| SPIFFEID / AgentCredential | ✅ Identity only |
| A2ABridge | ✅ SPIFFE domain check |
| CapabilityRegistry | ⚠️ Self-reported confidence |
| TaintedData / TDPGate | ✅ Data trust classification |
| Trust scores | ❌ Not implemented |
| Reputation system | ❌ Not implemented |

### Effort: ~24h

---

## Summary

| Gap | Status | Effort |
|-----|--------|--------|
| Soul Loader | Implemented, fragmented | 12h |
| Filesystem Watchers | No config/soul watching | 16h |
| Identity Fluidity | Audit trail only | 24h |
| Anti-Spiral | Implemented, solid | 8h |
| Lattice Trust | SPIFFE identity only | 24h |
