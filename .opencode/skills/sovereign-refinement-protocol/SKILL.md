---
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

name: sovereign-refinement-protocol
description: "Enforce the Sovereign Refinement Protocol — a mandatory forensic and preservation gate for core engine changes."
license: MIT
compatibility: AnyIO-compliant
---

# 🔱 Sovereign Refinement Protocol
**AP Token**: `AP-SOVEREIGN-REFINEMENT-v2.0.0`
⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_refinement_protocol ⬡ HARDENING

This skill implements the **Sovereign Refinement Protocol**, a mandatory forensic and preservation gate that must
  be applied to all critical architectural changes in the Omega Engine.

## §1 Purpose

To eliminate "cowboy coding" and prevent the "Restart Cycle" by enforcing a rigorous, multi-stage validation
  process before any code is committed to the core engine (`src/omega/`).

## §2 The Refinement Pipeline

When this skill is invoked, the agent must execute the following four gates in sequence:

### Gate 1: The Forensic Scan (Sovereign Guard)
Perform a deep static analysis of the proposed changes focusing on:
- **AnyIO Absolute**: Search for `asyncio.create_task`, `time.sleep`, `subprocess.run`, or any blocking `open()`
  calls. Every blocking call MUST be wrapped in `anyio.to_thread.run_sync`.
- **Engine-Stack Firewall** (Mandate 2): Verify that no entity-specific logic, names, or traits have leaked into
  `src/omega/`. Every name (e.g., N1-Flesh, N6-Mind) must be loaded from active WAD, not hardcoded.
- **Atomic Persistence**: Verify that all state writes use the "Write-to-Temp → `os.replace`" pattern.
- **Heritage Tags** (Mandate 14): Every `[id-soft:]` tag must be a valid format (`doom-1993`, `quake-1996`,
  `quake3-1999`, `doom3-2004`, `doom3bfg-2012`, `wolf3d-2012`). Non-standard tags are cracks that propagate.

### Gate 2: The Preservation Gate (State Anchor)
Before executing high-risk operations (e.g., database migrations, provider fabric pivots):
- **State Snapshot**: Persist the current active session state — commit current work, push to origin.
- **Recovery Path**: Document the exact `git revert` command required to restore the pre-operation state.
- **Resource Guard**: Verify that the operation is wrapped in a `ResourceGuard` (Semaphore) to prevent OOM on the
  Ryzen 5700U.

### Gate 3: The Sovereign Review (Mandate Alignment)
Cross-reference the final implementation against the `SOVEREIGN_MANDATES.md` (v3.1.0, 14 mandates):
- M1 (AnyIO Absolute) — All async code uses AnyIO?
- M2 (Engine-Stack Firewall) — No WAD-specific logic in engine?
- M6 (keep-id Sovereignty) — No `:U` flags on volume mounts?
- M7 (Local-First) — Local inference tried before cloud?
- M8 (Zero Telemetry) — No phone-home, analytics, or tracking?
- M9 (Error Integrity) — All errors typed, traceable, testable?
- M10 (Fleet Integrity) — Agent count ≤ 14?
- M13 (Temple-Grade) — T1-T11 gates honored?
- M14 (Heritage Vetting) — Every heritage concept vetted through 4-gate pipeline?

### Gate 4: Heritage Vetting Check (NEW — Mandate 14)
If the change introduces or modifies an id Software pattern:
- **Qualification Gate**: Can the concept be justified without mentioning the original hardware constraint? (If
  not, it fails.)
- **Scoring Gate**: Minimum 7/10 on the 10-point Heritage Vetting matrix.
- **Tag Gate**: Every `[id-soft:]` tag must have a corresponding record in
  `data/entities/doom_guy/knowledge/HERITAGE_VET_LOG.md`.
- **CI Gate**: Run `make heritage-vet` — must pass clean.

## §3 Execution Workflow

1. **Invoke**: `/skill sovereign-refinement-protocol`
2. **Analyze**: Run Gate 1 (Forensic Scan) → Output a "Sovereign Audit Report".
3. **Anchor**: Execute Gate 2 (Preservation) → Confirm state is protected.
4. **Verify**: Run Gate 3 (Sovereign Review) → "Go/No-Go" decision.
5. **Vet**: If heritage-related, run Gate 4 (Heritage Vetting) → Confirm vet record exists.
6. **Commit**: Only after all four gates are passed is the code considered "Sovereign Grade".

---
*Refinement is not a delay; it is the guarantee of robustness. A gate is not a barrier — it is the difference
  between a pipeline and a slide.*

