<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# ADR-003: File-Based Handoff Store

**Status:** Accepted — 2026-10-02 · Hivemind handoff subsystem

## Context
The handoff mechanism must survive context loss and compaction: a packet
submitted moments before a session dies must still be retrievable by the next
agent. It must also be auditable — every state transition attributable, every
packet inspectable by a human with no tooling beyond a text editor.

## Decision
Store handoff packets as **JSON envelopes on local disk** under
`data/handoff/{pending,active,completed,stale,archive}/`. One file per packet;
state is expressed by directory membership. Not SQLite.

## Consequences
- **Crash-safe**: a torn write is detectable and isolated to one packet;
  state transitions are atomic directory renames.
- **Human-readable and git-tracked**: `grep` works, diffs are meaningful,
  forensics need no database tooling.
- Cost: no ACID multi-writer guarantee — mitigated by `flock` plus `O_EXCL`
  exclusive creation.
- Cost: directory scans grow linearly with packet count (acceptable at fleet
  scale; the archive/ directory absorbs the cold tail).

## Alternatives Considered
- **SQLite**: ACID and query power, but one hot file couples all writers, is
  opaque to humans, and yields unreviewable binary diffs — and corruption
  would take down the whole handoff channel instead of one packet.
- **Redis/in-memory**: does not survive process death, which is precisely the
  context-loss case this store exists for.