<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# Observability, Memory Store, Cross-Entity Writes, Agent ACL — Deep Research
**AP Token**: `AP-P1-BATCH2-20260726`
**Date**: 2026-07-26 | **Priority**: P1
**Researcher**: Sovereign Researcher

---

## Gap 1: Observability (R28)

### Executive Summary

Mature observability stack (2500 lines, 11 modules). Duplicate `record_vault_audit` method (copy-paste bug). No OTel collector export. No live dashboard. Soul health metrics not wired.

### Components

| Component | Status |
|-----------|--------|
| ObservabilityEngine | ✅ Mature |
| MetricsDB (WAL SQLite) | ✅ Mature |
| OTel Exporter | ✅ Spans → MetricsDB |
| RegressionWatcher | ✅ Functional |
| Sovereignty ratio | ✅ Complete |
| Token ledger | ✅ Complete |
| BLEG (Body-Level Error Guards) | ✅ Complete |
| UFL (Unified Forensic Ledger) | ✅ Complete |
| Dashboard | ❌ Missing |
| OTel collector export | ❌ Missing |
| Soul health metrics | ❌ Not wired |

### Issues

1. Duplicate `record_vault_audit` method (lines 1116-1178 and 1180-1243)
2. No OTel collector endpoint (spans go to MetricsDB only)
3. No live dashboard
4. Soul health metrics not wired

### Effort: ~36h (P0+P1: ~20h)

---

## Gap 2: Memory Store (R29)

### Executive Summary

1110-line god-object handling caching, providers, vector search, FTS, embeddings, batch writes, archival. Entity isolation is implicit (key prefix, not enforced boundary).

### Current Architecture

```
MemoryStore (1110 lines)
├── Hot: In-memory Dict (LRU, 50 sessions)
├── Warm: File JSONL + Redis
├── Cold: SQLite (FTS5 + vector) + archival
└── Batch writes (25 pending flush)
```

### Issues

1. God-object (1110 lines)
2. Entity isolation is implicit (key prefix only)
3. No cross-entity search
4. Hardcoded archive paths

### Effort: ~35h (P1: ~30h)

---

## Gap 3: Cross-Entity Writes (R15)

### Executive Summary

No cross-entity write patterns exist. Soul write guard requires `SOVEREIGN_USER_TOKEN` (global, not per-entity). Memory block governance exists (GovernanceLevel + shared_with allowlist) but no code actively writes cross-entity.

### Current State

| Mechanism | Scope |
|-----------|-------|
| Soul Write Guard | soul.yaml + approved_lessons.yaml — user-only |
| Memory Block Governance | Per-block ACL (PRIVATE/SHARED_READ/SHARED_WRITE/PUBLIC) |
| BlindVault Resolver | Per-secret ACL (allowed_agents, allowed_commands) |

### Issues

1. No cross-entity write API
2. SovereignUserToken is global (not per-entity)
3. No "delegate write" pattern
4. No cross-entity distillation pipeline

### Effort: ~30h (P2: ~14h)

---

## Gap 4: Agent ACL (R20)

### Executive Summary

ACL is fragmented across 4 subsystems (soul guard, block governance, BlindVault, entity registry). No central policy engine. No inter-agent trust scores.

### ACL Layers

| Layer | Mechanism | Scope |
|-------|-----------|-------|
| Soul Write Guard | SOVEREIGN_USER_TOKEN | soul.yaml |
| Memory Block Governance | GovernanceLevel + shared_with | Per-block |
| BlindVault | allowed_agents/commands/hosts | Per-secret |
| Entity Registry | No ACL | Any code can read |

### Issues

1. No unified ACL system
2. SOVEREIGN_USER_TOKEN is global
3. No agent-to-agent permission model
4. Entity registry has no ACL

### Effort: ~44h (P2: ~32h)

---

## Summary

| Gap | Maturity | Effort |
|-----|----------|--------|
| Observability | 80% | 36h |
| Memory Store | 75% | 35h |
| Cross-Entity Writes | 30% | 30h |
| Agent ACL | 25% | 44h |
