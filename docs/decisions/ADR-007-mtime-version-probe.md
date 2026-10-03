<!-- SPDX-FileCopyrightText: 2026 Xoe-NovAi / SPDX-License-Identifier: Apache-2.0 -->
# ADR-007: mtime Version Probe

**Status:** Accepted — 2026-10-02 · Hub observability (incident P0-3)

## Context
The hub ran **pre-fix code for hours** because its uptime was green: a
healthcheck proves the process is alive, not that the code it is running is
current. Nothing compared the loaded code against what was on disk, so stale
execution was invisible until behaviour gave it away (P0-3).

## Decision
At process startup, **stamp the mtimes of the source files loaded**. On
demand, re-stat those paths and **compare**: any file newer than its startup
stamp is reported **STALE**. Expose the result as a probe so CI and operators
can query it.

## Consequences
- Stale code becomes **catchable in CI** — a restart-without-reload (or a
  edit-during-run) fails a checkable condition instead of lingering green.
- Cheap: no hashing, no git dependency, works for uncommitted working-tree
  edits (which a git-SHA stamp would miss).
- Cost: **mtime-only fidelity** — a same-mtime edit (copy preserving mtime,
  clock-resolution edge) evades the probe. It is a tripwire, not a proof of
  content identity.

## Alternatives Considered
- **Uptime/health checks**: the failure itself — green uptime said nothing
  about code freshness.
- **Git SHA stamping**: precise for committed state, but blind to uncommitted
  dev-tree edits, which is the common local failure mode; also fails when
  running outside a git checkout.
- **Full content hashing**: strongest fidelity, but pays I/O on every probe
  and still needs a baseline; overkill for the P0-3 detection job.