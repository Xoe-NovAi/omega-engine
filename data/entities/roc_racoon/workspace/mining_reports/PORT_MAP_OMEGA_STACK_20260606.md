<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Mining Report: Omega-Stack-Legacy Porting Map
**Date**: 2026-06-06  
**Miner**: roc_racoon  
**Site**: `/home/arcana-novai/Documents/Xoe-NovAi/omega-stack-legacy`  
**Status**: ✅ HIGH-VALUE GOLD FOUND

---

## 🎯 Executive Summary

The `omega-stack-legacy` repository contains mature, operational implementations of several systems that are currently in BETA or STUB status in `omega-engine`. Porting these systems will significantly accelerate the transition to a production-ready sovereign engine.

### 💎 High-Value Assets Identified

| Asset | Legacy Location | Engine Target | Value | Risk |
|-------|-----------------|----------------|-------|------|
| **Soul Evolution Engine** | `scripts/soul-evolution-engine.py` | `src/omega/oracle/soul_manager.py` | **CRITICAL** (M11) | Low (AnyIO native) |
| **Memory Bank FTS** | `mcp-servers/memory-bank-mcp/memory_bank_store.py` | `src/omega/memory_store.py` | **HIGH** (Performance) | Low (SQLite standard) |
| **Context Versioning** | `mcp-servers/memory-bank-mcp/memory_bank_store.py` | `src/omega/memory_store.py` | **MED** (Integrity) | Low |
| **Agent Registry** | `mcp-servers/memory-bank-mcp/memory_bank_store.py` | `src/omega/oracle/entity_registry.py` | **MED** (Resource Guard) | Low |
| **Ryzen Optimization** | `_archive/scripts/optimize_ryzen.sh` | `Makefile` / `cpu_optimizer.py` | **MED** (Latency) | Low |

---

## 🛠️ Detailed Porting Specifications

### 1. The Soul Evolution Pipeline (M11)
**Legacy Pattern**: Dual-Audit Synthesis (Ma'at $\leftrightarrow$ Lilith $\rightarrow$ Overseer).
**Implementation**:
- Replace current simple logging with the `weigh_expert_soul` ceremony.
- Use `anyio.create_task_group()` to run parallel audits.
- Integrate with `Scribe` for the final synthesis.
**Sovereign Gate**: Must use `Oracle.summon()` instead of `xnai-dispatcher.sh`.

### 2. The Mnemosyne Memory Store
**Legacy Pattern**: FTS5 + Tiered Cache + Versioning.
**Implementation**:
- Add `contexts_fts` virtual table to `memory_store.py`.
- Implement `_hot_cache` with 1-hour TTL.
- Implement `context_history` table for versioned memory snapshots.
- Add `access_log` for heat-mapping memory usage.
**Sovereign Gate**: Convert all `asyncio` calls to `anyio`.

### 3. Resource-Aware Agent Registry
**Legacy Pattern**: Capability-based memory limits.
**Implementation**:
- Add `capabilities` and `memory_limit_gb` to the `entities.yaml` schema.
- Implement a check in `MemoryStore.set_context()` to enforce these limits.
**Sovereign Gate**: Ensure this doesn't violate the Engine-Stack Firewall (M2).

---

## 📈 Impact Assessment

| Metric | Current (BETA) | Post-Port (PRODUCTION) | Improvement |
|--------|----------------|-------------------------|--------------|
| **Soul Integrity** | 16% adoption | 100% automated | 🚀 MASSIVE |
| **Search Latency** | $O(n)$ linear | $O(\log n)$ FTS | 🚀 HIGH |
| **Memory Reliability** | Overwrite-only | Versioned/Rollback | 🚀 HIGH |
| **Hardware Efficiency** | Generic | Ryzen-Optimized | 📈 MEDIUM |

## 🚩 Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Asyncio Leak** | High | Strict `grep "asyncio"` check during port. |
| **Path Drift** | Med | Use `SovereignPaths` for all data roots. |
| **Schema Conflict** | Med | Run `make test` after every schema change. |

---

**Verdict**: Proceed with immediate porting of the **Soul Evolution Engine** and **Memory Bank FTS**. These are the highest-leverage wins available in the legacy archive.

