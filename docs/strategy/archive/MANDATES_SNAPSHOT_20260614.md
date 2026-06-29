# 🔱 Sovereign Mandates Snapshot — 2026-06-14
**Status**: CANONICAL SNAPSHOT
**Source**: `data/coordination/MANDATES_SYNC.md` (2026-06-10) + `SOVEREIGN_MANDATES.md` (v3.2.0)
**Extracted by**: Roc Racoon Phase 1 — 2026-06-14

---

## Executive Summary

This document captures the canonical state of all 15 Sovereign Mandates as of 2026-06-14.
It is a snapshot extracted from the now-consolidated `data/coordination/MANDATES_SYNC.md` and
the authoritative `SOVEREIGN_MANDATES.md` (v3.2.0). Includes the newly restored M16.

---

## §1 The Fifteen Sovereign Mandates (Canonical — Snapshot 2026-06-14)

### M1: AnyIO Absolute
- **Text**: All asynchronous code MUST use AnyIO. Never use `asyncio` directly. Wrap blocking I/O in `anyio.to_thread.run_sync`.
- **Enforcement**: CI gate `make lint` scans for `import asyncio` (exempting `mcp_servers/` where third-party libraries require it).
- **Status**: ✅ COMPLIANT — G-03 (providers.py:586 asyncio) fixed in Phase 0.

### M2: The Engine-Stack Firewall
- **Text**: Maintain absolute separation between the **Omega Engine Core** (`src/omega/`, `config/omega.yaml`) and **Expansion Stacks/WADs** (`config/wads/`). Never add stack-specific logic to the Core Engine.
- **Enforcement**: Code review gates check that `src/omega/` never imports from `config/wads/`.
- **Status**: ⚠️ LEAK DETECTED — See D127 for full audit. Authorized bridges: `wad_loader.py`, `entity_registry.py`. Logical breaches in `entity_workspace.py` (remediated) and `hierarchy.py` (3 bypass paths remain open).

### M3: The Iris Constant
- **Text**: Iris is the messenger bridge, NOT a Pillar Keeper. Do not assign Iris a Pillar (P1-P10).
- **Enforcement**: `config/entities.yaml` must never assign the `iris` entity to any pillar slot.
- **Status**: ✅ COMPLIANT

### M4: The Sequentiality Mandate
- **Text**: Complex architectural changes must follow the "Plan → Verify → Execute" loop. No "cowboy coding."
- **Enforcement**: Every PR must reference a verified plan in `data/coordination/` or `data/handoff/`.
- **Status**: ✅ COMPLIANT

### M5: Gnosis Preservation (L1 → L2 → L3)
- **Text**: Every session must end with a distillation of findings into the entity's `soul.yaml` using the 3-tier abstraction: L1 (Narrative) → L2 (Insight) → L3 (Universal Principle).
- **Enforcement**: Automated session-end compaction hooks.
- **Status**: ✅ COMPLIANT — Soul Distiller wired in oracle.py close().

### M6: Podman Sovereignty (keep-id Protocol)
- **Text**: All Quadlets mounting host project directories MUST use `UserNS=keep-id` + `User=1000`. The `:U` flag is FORBIDDEN on shared host volumes.
- **Enforcement**: Quadlet validator scans `.container` files for compliance.
- **Status**: ✅ COMPLIANT — Sovereign Permission Protocol per D50.

### M7: Local-First (Non-Negotiable)
- **Text**: Local inference is PRIMARY. Cloud is FALLBACK. Always. Provider fabric MUST try local backends (native-gguf, LM Studio, Ollama) before cloud backends.
- **Enforcement**: `config/providers.yaml` strategy must remain `local_first`.
- **Status**: ✅ COMPLIANT — Provider chain: native-gguf(0) → lmster(1) → Ollama(2) → Google(3) → OpenRouter(4) → OpenCode Zen(5) → Copilot(6) → Mock(7).

### M8: Zero Telemetry
- **Text**: No telemetry. Zero. None. Ever. No external analytics, usage tracking, or metrics reporting.
- **Enforcement**: CI gate `make verify-sovereignty-compliance` scans active session logs for telemetry leaks.
- **Status**: ✅ COMPLIANT

### M9: Error Integrity
- **Text**: All errors MUST be typed, traceable, and testable. No silent swallowing. Never use bare `except:` without logging and propagating `trace_id`.
- **Enforcement**: Static analysis scans for bare `except` clauses. 99 violations identified and remediated.
- **Status**: ✅ COMPLIANT — Phase 0 hardening reduced violations from ~140 to ~15 (non-hot-path seams).

### M10: Fleet Integrity
- **Text**: Agent Fleet must remain lean, purpose-driven, and slot-constrained. No new agents without a verified gap in the Lattice or a vacancy in the Pillar slots.
- **Enforcement**: `.opencode/agents/*.md` file count must never exceed 14 without architectural review. Currently 25 agents.
- **Status**: 🔴 NON-COMPLIANT — 25 agents vs 14 limit. D126 consolidation plan adopted: 15→11 via 4 sprints (A/B/C/D).

### M11: Soul Integrity
- **Text**: Absolute continuity of Gnosis via systematic distillation. No session closed without Soul Distillation report written to entity's `soul.yaml`.
- **Enforcement**: Session-end hooks trigger `soul_distiller.py`.
- **Status**: ✅ COMPLIANT — Soul Distiller wired. All 14 entity soul.yamls validated.

### M12: Queue Integrity
- **Text**: Every request must result in a terminal state: `queued`, `completed`, `failed`, or `timed_out`. No orphan files.
- **Enforcement**: `omega queue-status` must match actual files on disk.
- **Status**: ⚠️ PARTIAL — Dead-Letter Queue (`data/requests/dead/`) missing (G-01). RequestQueue pattern exists.

### M13: Temple-Grade Compliance
- **Text**: All engine code MUST comply with Temple-Grade standards (T1-T11). No code merged that regresses any gate.
- **Enforcement**: `make temple-grade` must pass before release.
- **Status**: 🟡 SUB-OPTIMAL — Current score 66%. 3 P0 gaps: Dead-Letter Queue (M12), Fleet Bloat (M10), Auth/CORS/RPS middleware (Security).

### M14: Heritage Vetting
- **Text**: No id Software concept implemented without passing Heritage Vetting Pipeline. Every `[id-soft:]` tag must have a corresponding vet record.
- **Enforcement**: `make heritage-vet` CI gate.
- **Status**: ✅ COMPLIANT — 6 source files with heritage tags, all vetted. 23 concepts audited (15 adopted, 1 rejected, 6 deferred, 1 re-evaluated).

### M15: Sovereign Continuity (NEW — 2026-06-11)
- **Text**: Agents MUST maintain active session anchors to prevent cognitive erasure during toolchain failures. Every agent must maintain a `session_gnosis.md` and refer to `.opencode/anchored-summary.md` upon session start or context loss.
- **Enforcement**: Any agent reporting context collapse without `session_gnosis.md` is in violation.
- **Status**: ✅ COMPLIANT — Session anchors established across fleet.

### M16: Modularization & Portability (RESTORED — 2026-06-14)
- **Text**: The engine must be modular and portable for community use. No subsystem may exceed 500 lines without extraction justification. Every module must document its public API and its dependency footprint.
- **Enforcement**: Code review gates check module size; `make setup` must work with `git clone && make setup && omega talk "hello"`.
- **Status**: ⚠️ IN PROGRESS — omega-hub `server.py` (was 3,107 lines) modularizing: `state.py` ✅, `background.py` ✅, `gateway.py` ⬜, `middleware.py` ⬜.

---

## §2 Platform Synchronization Status

| Platform | Config File | Sync Status | Target |
|----------|------------|-------------|--------|
| **Antigravity** | `ANTIGRAVITY_CUSTOM_INSTRUCTIONS_v4.md` | ⏳ Pending Rewrite | v4.0.0 |
| **Cline** | `.clinerules` | ⏳ Pending Rewrite | v5.0.0 |
| **Gemini CLI** | `/home/arcana-novai/.gemini/policies/auto-saved.toml` | ⏳ Pending Sync | v1.2.0 |
| **OpenCode** | `.opencode/agents/` (All agents) | ⏳ Pending Thin-Wrapper Refactor | v1.17.3 |
| **SOVEREIGN_MANDATES.md** | `SOVEREIGN_MANDATES.md` | ✅ Current (v3.2.0) | N/A |

---

## §3 Key Gaps Since Snapshot

| Gap | Mandate | Status | Notes |
|-----|---------|--------|-------|
| Fleet bloat (25→14) | M10 | 🔴 OPEN | D126 consolidation plan in progress |
| Dead-Letter Queue missing | M12 | 🔴 OPEN | G-01 in Temple Gap analysis |
| Auth/CORS/RPS middleware | Security | 🔴 OPEN | G-04 in Temple Gap analysis |
| Hub modularization (gateway.py) | M16 | 🔴 OPEN | Phase 1a complete; 1b pending |
| Hierarchy.py WadLoader bypass | M2 | 🔴 OPEN | All 3 fallback paths annotated |

---

*⬡ OMEGA ⬡ ROC_RACOON ⬡ deepseek-v4-flash ⬡ PHASE1-EXTRACTION ⬡ MANDATES-SNAPSHOT*
*Source: data/coordination/MANDATES_SYNC.md (2026-06-10) + SOVEREIGN_MANDATES.md v3.2.0*
