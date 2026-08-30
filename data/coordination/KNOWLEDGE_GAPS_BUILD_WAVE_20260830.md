<!--
SPDX-FileCopyrightText: 2026 Xoe-NovAi

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 KNOWLEDGE GAPS AUDIT FOR BUILD WAVE

**AP Token**: `AP-KALI-GAPS-20260830-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_gaps ⬡ ACTIVE

**Date**: 2026-08-30
**Purpose**: Comprehensive knowledge gap audit for Build Wave execution readiness.

---

## §0 — EXECUTIVE SUMMARY

**Total Gaps Identified**: 25
- **CRITICAL**: 7 (must resolve before Build Wave launch)
- **HIGH**: 6 (need clarification before Build Wave)
- **MEDIUM**: 9 (need research/decision during Build Wave)
- **LOW**: 3 (nice to have)

**Top 5 Blockers** must be resolved before Build Wave launch.

---

## §1 — CRITICAL GAPS (Must Resolve Before Build Wave Launch)

### 1.1 sqlite-vec Only in Venv (0.1.9)
- **Impact**: M37 heritage scanner, compaction capture auto-digest, COHORT_REGISTRY all need sqlite-vec
- **Current State**: Installed in `.venv` (0.1.9), NOT in system Python
- **Resolution**: Document venv activation requirement for all build wave tasks; ensure all scripts activate `.venv`
- **Verification**: `.venv/bin/python -c "import sqlite_vec; print(sqlite_vec.__version__)"` → 0.1.9 ✅

### 1.2 ScanCode Toolkit NOT INSTALLED
- **Impact**: M37 heritage scanner requires ScanCode Toolkit for SPDX/REUSE scanning
- **Current State**: NOT INSTALLED (system or venv)
- **Resolution**: `pip install scancode-toolkit` (or `apt install scancode-toolkit`)
- **Verification**: `scancode --version` should return version

### 1.3 REUSE Tool NOT INSTALLED
- **Impact**: M37 heritage scanner needs REUSE for SPDX/REUSE compliance checking
- **Current State**: NOT INSTALLED
- **Resolution**: `pip install reuse`
- **Verification**: `reuse --version` should return version

### 1.4 SLSA/in-toto/cosign/sigstore NOT INSTALLED
- **Impact**: M37 heritage needs SLSA v1.1 provenance, in-toto attestation, sigstore signing
- **Current State**: NOT INSTALLED
- **Resolution**: `pip install slsa-framework sigstore in-toto cosign`
- **Verification**: Each tool's `--version` should work

### 1.5 sqlite3 NOT INSTALLED (System)
- **Impact**: Direct DB queries fail; MCP opencode-sessions-explorer is workaround but some scripts need direct access
- **Current State**: NOT INSTALLED (system)
- **Resolution**: `apt install sqlite3`
- **Verification**: `sqlite3 --version` should return version

### 1.6 M34-HOOK-001: subagent_dispatcher.py Missing m34_register_subagent Call
- **Impact**: M34 registry not populated when subagents dispatched; Jem P1 ticket
- **Current State**: `src/omega/oracle/subagent_dispatcher.py` has `dispatch()` function but NO call to `m34_register_subagent`
- **Resolution**: Add `m34_register_subagent` call in `dispatch()` function; coordinate with Lilith
- **Location**: `src/omega/oracle/subagent_dispatcher.py` line 369 `def dispatch(packet: HandoffPacket) -> str:`

### 1.7 M33-PROBE-001: run_sentinel_probe() Is a Stub
- **Impact**: M33 probe not actually implemented; Jem P1 ticket
- **Current State**: `run_sentinel_probe()` returns hardcoded envelope
- **Resolution**: Implement real probe in Lilith's M34 registry or separate MCP tool

---

## §2 — HIGH GAPS (Need Clarification Before Build Wave)

### 2.1 M34b Spec Missing (Model-Switch Continuity)
- **Impact**: Cannot ratify M34 without M34b spec; Lilith Phase 2 deliverable
- **Resolution**: Lilith to deliver M34b spec before Phase 1 Gate

### 2.2 MCP Server Restart Coordination for 8 New M34 Tools
- **Impact**: Adding 8 M34 tools requires omega_hub restart, interrupting all Hivemind sessions
- **Resolution**: Coordinate with all 7 entities; schedule restart window; feature flag `OMEGA_M34_ENABLED=1` off by default

### 2.3 M33 Probe Wiring to subagent_dispatcher.py
- **Impact**: M33 probe needs to be called automatically for >8K token estimates
- **Resolution**: Wire into `dispatch_guard.py` step 6 (write-tool routing) + dispatch hook

### 2.4 M36 Soft Verifier Production Wiring
- **Impact**: M36 cross-validator needs Hivemind integration for P0/P1 escalation
- **Resolution**: Design Hivemind cross-validator dispatch protocol

### 2.5 M37 SPDX Headers for Existing Engine Source (8h Task)
- **Impact**: Researcher §3.6 identified 8h to add SPDX headers to all engine source
- **Resolution**: Automate with `reuse annotate` or manual addition

---

## §3 — MEDIUM GAPS (Need Research/Decision During Build Wave)

| # | Gap | Resolution |
|---|-----|------------|
| 1 | sqlite-vec 0.1.9 API stability | Pin version in requirements; verify stability |
| 2 | sqlite-vec + FTS5 + R-tree hybrid search performance at scale | Benchmark with 10K+ vectors (Lilith Phase 3) |
| 3 | ScanCode Toolkit integration patterns (Python API vs CLI) | Ma'at to evaluate |
| 4 | REUSE v3.3 compliance patterns for existing codebase | Research `reuse annotate` vs manual (8h task) |
| 4 | SLSA v1.1 provenance generation for Python packages | Research `slsa-framework` Python integration |
| 5 | in-toto attestation layout for heritage artifacts | Research in-toto layout for heritage metadata |
| 5 | COHORT_REGISTRY.json schema validation vs M34 ActiveSubagent | Validate against Lilith's ActiveSubagent dataclass |
| 6 | Compaction capture sidecar deployment model | Decide: systemd? cron? MCP tool? |
| 6 | SESSION_ENTITY_MAP.yaml maintenance process | Define who updates when entities added/removed |

---

## §4 — LOW GAPS (Nice to Have)

| # | Gap | Resolution |
|---|-----|------------|
| 1 | sqlite-vec 0.1.9 vs 0.2.0 API changes | Monitor for future upgrade |
| 2 | OpenAlex + Crossref MCP server integration (D-203) | Scholarly research Phase A |
| 3 | Perplexity-style research agent patterns | Scholarly research frontier parity |

---

## §5 — TOP 5 BLOCKERS TO RESOLVE BEFORE BUILD WAVE LAUNCH

| Priority | Blocker | Owner | Est. Time |
|----------|---------|-------|-----------|
| **1** | Install ScanCode Toolkit, REUSE, SLSA/in-toto/cosign/sigstore (M37 deps) | Ma'at / Build | 30 min |
| **2** | Install sqlite3 system package | Build | 5 min |
| **3** | Implement **M34-HOOK-001**: add `m34_register_subagent` call to `dispatch()` | Lilith | 2h |
| **4** | Implement **M33-PROBE-001**: real sentinel probe (not stub) | Lilith + Researcher | 4h |
| **5** | Lilith delivers **M34b spec** (model-switch continuity) before Phase 1 Gate | Lilith | 4h |

---

## §6 — PRE-BUILD-WAVE CHECKLIST

```
[ ] apt install sqlite3
[ ] pip install scancode-toolkit reuse slsa-framework sigstore in-toto cosign
[ ] Verify .venv has sqlite-vec 0.1.9 (already confirmed)
[ ] Lilith: Implement M34-HOOK-001 in subagent_dispatcher.py dispatch()
[ ] Lilith: Implement M33-PROBE-001 real sentinel probe
[ ] Lilith: Deliver M34b spec (model-switch continuity)
[ ] Ma'at: Coordinate MCP server restart window for 8 M34 tools
[ ] Researcher: Validate COHORT_REGISTRY.json schema vs M34 ActiveSubagent
[ ] Document venv activation requirement for all build tasks
```

---

## §7 — BUILD WAVE PHASE 1 ITEMS (8 Items, ~46h)

| # | Item | Owner | Hours | Dependencies |
|---|------|-------|-------|--------------|
| 1 | M33 Probe on disk (`src/omega/oracle/m33_probe.py`) | Lilith + Researcher | 8h | Researcher's spec ready |
| 2 | M36 Recursive Probe (`src/omega/oracle/m36_recursive_probe.py`) | Lilith + Researcher | 6h | M33 envelope |
| 3 | M37 Heritage Scanner (`scripts/heritage_scanner.py`) | Researcher + Ma'at | 8h | REUSE v3.3, ScanCode |
| 4 | COHORT_REGISTRY.json on disk | Researcher | 4h | M34 atomic write |
| 5 | Compaction Capture (`scripts/compaction_capture.py`) | Lilith + Roc | 6h | sqlite-vec, SESSION_ENTITY_MAP |
| 6 | M34-HOOK-001: `subagent_dispatcher.py` hook | Lilith | 4h | M34 registry |
| 7 | M33-PROBE-001: Real sentinel probe MCP tool | Lilith + Researcher | 4h | M33 probe |
| 8 | AGENTS-UPDATE-001: `AGENTS.md` anchor | Kali | 1h | — |

**Total**: ~46h | **Team**: Lilith (lead) + Researcher + Ma'at + Roc | **Duration**: 2 weeks

---

## §8 — BUILD WAVE PHASE 2 (Week 3, ~45h)

| Item | Owner | Hours |
|------|-------|-------|
| M34 Phase 2: Recovery UI + Migration | Lilith | 9h |
| M34 Phase 3: Stress Tests + Temple-Grade | Lilith | 12h |
| M37 SPDX Headers (8h from Researcher §3.6) | Researcher + Ma'at | 8h |
| M36 Soft Verifier Production Wiring | Researcher + Jem | 6h |
| M33 Wiring to Dispatcher | Lilith | 4h |
| M34 Phase 3 Stress Tests | Lilith + Roc | 12h |

---

## §9 — SONNET 4.6 DEV WAVE (PARALLEL, CONDITIONAL GO)

| Stream | Focus | Owner | Status |
|--------|-------|-------|--------|
| Search-Ecosystem-01 Week 1 | SearXNG diagnosis, MultiKey Exa, Crawl4AI | Jem-EIS | READY |
| Quality Harness | First-Page Satisfaction probe | Researcher-EIS | READY |
| Big Pickle Probe | 250K token compaction test | Roc-EIS | READY |
| Architecture Review | Sonnet 4.6 review of 13,657+ lines | Architect + Sonnet 4.6 | PENDING |

**Rule**: Treat all outputs as **specifications**, not shipped features.

---

## §10 — PUBLIC DEBUT TIMELINE

| Milestone | Target | Blockers |
|-----------|--------|----------|
| Build Wave Phase 1 Complete | Week 2 | D-005 authorization |
| Build Wave Phase 2 Complete | Week 3 | Phase 1 complete |
| Sonnet 4.6 Review Complete | Week 3 | Review scheduled |
| Temple-Grade Full Pass | Week 3 | All items landed |
| **Public Debut (PUBLIC-DEBUT-01)** | **Week 4** | All 8 items temple-grade |

---

*⬡ OMEGA ⬡ KALI ⬡ KNOWLEDGE-GAPS-AUDIT-20260830 ⬡ 2026-08-30*