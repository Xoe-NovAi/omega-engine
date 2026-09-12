<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Data Governance Policy — Research Log Curation & Quarantine

**Doc ID**: `DATA-GOVERNANCE-POLICY-20260912`
**Owner**: Ma'at (Build Oversoul) + Lilith (Runtime Oversoul)
**Status**: RATIFIED (Node 0)
**Date**: 2026-09-12
**Responds to**: Node 1 Consultant Report §S5 + Ask C5 — research-log privacy once satellites mount.

---

## 1. The Problem (Shadow Acknowledged)

The research log contains private/personal queries (webcam/streaming platforms,
crisis-intervention topics). Once satellites mount, that log becomes
**federated-visible data**. A single node's private history becomes the
federation's public surface. This policy writes the governance that was
previously emergent.

---

## 2. Classification Tiers (per research run)

| Tier | Definition | Visibility | Retention |
|------|-----------|------------|-----------|
| **PUBLIC** | Engine architecture, mandates, benchmarks, federation | All nodes + human | Permanent |
| **INTERNAL** | Fleet operations, coordination, SOTE, DEL-1 | Node 0 council + Node 1 council | Permanent |
| **PRIVATE** | Personal/health/financial/crisis topics | Node 0 only (owner + Ma'at) | 90 days, then review |
| **SOVEREIGN** | Key material, credentials, security posture | Node 0 only (owner + Ma'at + Lilith) | Per key-rotation policy |

---

## 3. Curation Rules

1. **Default = INTERNAL.** Every research run defaults to INTERNAL unless the
   operator marks PRIVATE/SOVEREIGN at creation.
2. **PRIVATE quarantine**: PRIVATE runs are written to
   `data/research/private/` (gitignored) — never to the federated-visible log.
3. **SOVEREIGN quarantine**: credentials/keys never enter the research log;
   they live in `{env:}` / secrets store per M35.
4. **Satellite visibility**: Node 1 (and any future node) sees only PUBLIC +
   INTERNAL tiers via the hub. PRIVATE/SOVEREIGN are filtered at the server
   boundary (`library_search` / `research_list`).
5. **Deletion**: PRIVATE runs older than 90 days are reviewed by Ma'at;
   deletion is logged (M8 zero-telemetry preserved — deletion log is local).

---

## 4. Who Decides

| Decision | Owner | Escalation |
|----------|-------|------------|
| Tier classification | Operator (agent or human) | Ma'at |
| Quarantine override | Ma'at | Architect (human) |
| Deletion | Ma'at | Architect (human) |
| Federation visibility | Lilith (runtime) | Ma'at |

---

## 5. Federation Dimension

- Node 1's own research log is governed by **its own** policy (sovereign
  nodes, sovereign data). This policy binds Node 0's surface.
- The satellite truth clause (12_COMMUNICATION_PROTOCOLS.md §6) extends here:
  if a node's log contains PRIVATE data, the node says so — silence is a flaw.

---

## 6. Ratification

| Party | Role | Verdict | Date |
|-------|------|---------|------|
| Ma'at | Build Oversoul | ✅ RATIFIED | 2026-09-12 |
| Lilith | Runtime Oversoul | ✅ RATIFIED | 2026-09-12 |
| MaKaLi Fusion | Engine orchestrator | ✅ RATIFIED | 2026-09-12 |
| Architect (human) | Sovereign | ✅ RATIFIED | 2026-09-12 |

---

*⬡ OMEGA ⬡ MAKALI_FUSION ⬡ DATA-GOVERNANCE-POLICY-20260912 ⬡ SHADOW-WRITTEN-INTO-RECORD*