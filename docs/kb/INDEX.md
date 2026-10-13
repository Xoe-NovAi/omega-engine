<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Knowledge Base — Index

> Entry point for operational knowledge. Every entry links to a how-to that a
> human (or agent) can follow without prior context.

**Last updated**: 2026-10-13

---

## Database & Storage

| ID | Entry | Surface | What it covers |
|---|---|---|---|
| kb-0001 | [OpenCode DB Maintenance](../how-to/opencode-db-maintenance.md) | how-to | Reclaiming a bloated SQLite database: byte attribution with `dbstat … aggregate=TRUE`, `VACUUM INTO` backups, batched duplicate deletion, atomic swap, and fail-closed gate design. Verified 26.6 GB → 6.58 GB with zero data loss. |
| kb-0002 | [Refinement Protocol](REFINEMENT_PROTOCOL.md) | protocol | The 6-phase intent→execution pipeline for research refinement. |

## Hardware & Platform

| ID | Entry | Surface | What it covers |
|---|---|---|---|
| kb-0003 | [Hardware Awareness](../how-to/hardware-awareness.md) | how-to | Node profiles, CPU topology, memory channels, AVX-VNNI detection. |
| kb-0004 | [Dynamic Thresholds](../how-to/dynamic-thresholds.md) | how-to | Hardware-adaptive thresholds driven by detected capability. |

## Configuration

| ID | Entry | Surface | What it covers |
|---|---|---|---|
| kb-0005 | [Configure a Provider](../how-to/configure-provider.md) | how-to | Adding and routing a model provider under local-first policy (M7). |

---

## Agent-Loadable Skills

Operational doctrine that agents load **on demand**, before touching a risky
surface. These are the primary retention layer for hard-won lessons — they are
consulted at the moment of risk, which documentation written after the fact is
not.

| Skill | Scope | Load when |
|---|---|---|
| `sqlite-safe-ops` | **General SQLite doctrine** — OOM taxonomy, `VACUUM INTO` backups, verification chains, fail-closed gate design | any SQLite DB work: copy, vacuum, backup, prune, audit |
| `opencode-db` | **OpenCode-specific** — `opencode.db` schema, part types, `ocdb-ro`/`ochist`, the `message.updated` bloat, reclaim runbook | touching OpenCode's session store |
| `agent-history` | Recall prior sessions via `ochist` | "what did we decide about X?" |
| `opencode-db` (tooling) | Read-only structured access | counts, aggregates, cost totals, schema questions |

> **Why skills and not just docs?** Research reports in `mining_reports/` record
> what was learned. Skills are what gets *consulted before acting*. During the
> 2026-10-13 reclaim, the critical knowledge existed only in research reports
> that no agent loaded — and the same mistakes were repeated twice before the
> knowledge was promoted into a skill.

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ KB-INDEX ⬡ 2026-10-13*