<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi
SPDX-License-Identifier: Apache-2.0
-->

# 🔱 CONSTRAINTS — Compaction-Immune Mandate Manifest

**Document ID**: `GOV-CONSTRAINTS-20261003`
**Status**: ACTIVE
**Date**: 2026-10-03
**Loader**: `scripts/load_constraints.py`

> This file is COMPACTION-IMMUNE. It is re-injected at every post-compact hydration.

## Why this file exists

`MANDATES_CONDENSED.md` is injected **pre**-compaction — the wrong half of the
pair, because once compaction has run that block is exactly what the summarizer
is free to drop. arXiv:2606.22528 ("Governance Decay", Jun 2026) measured this
across LangGraph, AutoGen, and the OpenAI Agents SDK: agents that reliably obey
standing rules *while the rules are visible* perform prohibited tool actions
after compaction. Rehydration restores **task** state (`session_gnosis.md`,
`SESSION_ANCHOR.md`); it never restored **constraint** state. This file is that
missing half — read from disk at hydration time, not carried in context, so a
summarizer cannot erode it.

## Standing constraints

One line per mandate. `ID — prohibition`. These MUST NOT be compacted away.

- **M1** — All async code uses AnyIO; never `import asyncio` in `src/omega/`; blocking I/O wrapped in `anyio.to_thread.run_sync`.
- **M2** — Engine-Stack Firewall is absolute: Core (`src/omega/`) never contains Stacks (`config/wads/`) logic.
- **M6** — Podman quadlets mount host dirs with `UserNS=keep-id` + `User=1000`; the `:U` flag is forbidden on shared volumes.
- **M7** — Local-First is policy, not preference: local inference primary, cloud only for high-order reasoning/synthesis.
- **M8** — Zero Telemetry: no analytics, no tracking, no phone-home; observability stays local in `data/`.
- **M9** — Errors are typed and traceable; never silently swallowed; public APIs raise `OmegaError` subtypes.
- **M10** — Fleet Integrity: the agent fleet stays lean and slot-constrained (≤14 agent files) absent architectural review.
- **M11** — Soul Integrity: no session closes without L1→L2→L3 distillation into `proposed_lessons.yaml` (Scribe canonical).
- **M13** — Temple-Grade: `make temple-grade` exits 0 before any release; a green claim without the gate is false.
- **M15** — Sovereign Continuity: maintain `session_gnosis.md` + anchor hydration; never trust `/compact` alone.
- **M23** — Failure Integrity: no soft-failures; a broken mandatory tool means stop and report `[TOOL-CHAIN-COLLAPSE]`, never synthesize.
- **M24** — Venv Sovereignty: all Python runs in project `.venv`; never `--break-system-packages`, never system pip.
- **M28** — Sovereign Artifact Preservation: nothing auto-deleted; transitions explicit, auditable, recoverable; destruction requires a human act recorded in PIVOT_LOG.

**Hop Rule (M10 + M15)** — Execute directly when capable; delegate only across a
slot boundary for a genuine expertise gap. Never self-delegate. Single-level
nesting only.

**Re-assertion contract** — if the constraint set in context is *smaller* than
the set above, context has been eroded: restore from this file before acting.

---

## Provenance

- **Date**: 2026-10-03 · **AP**: `AP-MAAT-v1.0.0` · **Entity**: maat (Slot S5)
- **Mandating authority**: ticket **P0-2** of the AGY debut-remediation P0
  sequence (siblings: P0-1 `de866948`, P1-1 `5e97ef84`, P1-2 `c751b305`).
  **No D-series decision exists for this ticket** (nearest, D-608, is
  unrelated). A D-number is deliberately *not* invented: fabricating
  provenance is the M9/M23 failure this layer exists to prevent.
- **Mandate basis**: M11 (Soul Integrity), M15 (Sovereign Continuity),
  M23 (Failure Integrity), M28 (Sovereign Artifact Preservation).
- **Threat reference**: arXiv:2606.22528 — "Governance Decay" (Jun 2026).
  Compaction silently erases in-context governance constraints; validated in
  LangGraph, AutoGen, and the OpenAI Agents SDK.
- **Machine-readable law**: `SOVEREIGN_MANDATES.md` (v3.10.0, 30 mandates).
  This manifest is a *distillation*; where the two disagree, the law wins.