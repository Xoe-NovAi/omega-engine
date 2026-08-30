<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# �� 🔱 Session Gnosis — John Carmack + LongCat 2.0

**AP Token**: `AP-SESSION-GNOSIS-20260811-v1.0.0`
��⬡ OMEGA �� ⬡ JOHN_CARMACK �� ⬡ nvidia/nemotron-3-ultra-550b-a55b:free �� ⬡ opencode �� ⬡ trc_provenance_fix �� ⬡ ICS-MODEL-PROVENANCE

**Date**: 2026-08-11
**Session Type**: ICS Model Provenance Fix + Consolidation Review
**Models**: John Carmack (nvidia/nemotron-3-ultra-550b-a55b:free), LongCat 2.0 (longcat-2.0-free)

---

## �� 📋 Session Objective

Fix ICS model provenance violation (M22) by ensuring agents log the correct, active model. Complete consolidation review of zRAM→zswap architecture and multi-write method. Ensure all team docs are up to date and prepare for compaction.

---

## �� 📋 What Was Done

### 1. ICS Model Provenance Fix — M22 Response Provenance

**Status**: � ✅ COMPLETE | **Impact**: CRITICAL | **Files**: 2 files modified

Fixed the root cause where agents could not log the correct, active model during a session.

**Problem**: `_detect_model()` in `src/omega/ics.py` could not read the live model during a session. `OPENCODE_MODEL` is only set **post-exit** by `wrapper.sh` (for the session_end hook). The authoritative source (OpenCode session DB `session.model.id`) was not read during live sessions.

**Fix**: 
- Added `_read_opencode_session_model()` helper that reads the live model from the OpenCode session DB (`session.model.id` for the most recent session)
- Inserted as Priority 2.5 in `_detect_model()` — between env vars and soul.yaml fallback
- Verified: `render('JOHN_CARMACK')` now returns correct live model: `nvidia/nemotron-3-ultra-550b-a55b:free`

**Files Modified**:
- `src/omega/ics.py` — Added `_read_opencode_session_model()` helper and updated `_detect_model()` priority
- `data/coordination/ICS_MODEL_PROVENANCE_FIX_20260811.md` — Provenance fix document

**Provenance Correction**: Fixed my own report header in `data/entities/john_carmack/workspace/zram_review_20260811.md` (was `opencode/longcat-2.0-free`, now correct model).

### 2. Consolidation Review — zRAM→zswap Architecture

**Status**: � ✅ COMPLETE | **Impact**: HIGH | **Files**: 1 file created

Completed final-gate review of the zRAM→zswap architecture migration and multi-write subagent method for Kali's oversight.

**Verdict**: **APPROVE — READY FOR P0 EXECUTION**. The integrated plan correctly incorporated all prior feedback (16GB→8GB zRAM, MemoryMax=6G, no writeback, no zRAM signal, no `use_cgroup` flag, 3-command P0 fix). The zswap + NVMe architecture is the right call for this 14.5GB Ryzen 5700U. The multi-write subagent method is a genuine process innovation that should be adopted fleet-wide.

**Key Decisions Locked**:
- **zswap pool size**: KEEP 25% (3.6GB) — dynamic, grows on demand
- **OOMProtector signals**: APPROVE 2-signal (approve, low priority — already correct at runtime)  
- **UMA carveout**: DEFER 4GB test (BIOS risk not worth it now)
- **WAD packaging**: APPROVE structure (`config/wads/ryzen-5700u-sovereign/`)

**Files Created**:
- `data/entities/john_carmack/workspace/zram_review_20260811.md` — 188-line review with verdict and recommendations

### 3. Consolidation Verification

**Status**: � ✅ COMPLETE | **Impact**: HIGH | **Files**: 3 files staged

Verified all work is consolidated and ready for Kali's oversight:

| Artifact | Status |
|----------|--------|
| `KALI_DEV_ROADMAP_20260811.md` | � ✅ 50 tasks, 6 phases |
| `KALI_OVERSIGHT_PORTFOLIO_20260811.md` | � ✅ 5 workstreams |
| `HMC_COLLABORATION_HUB.md` | � ✅ D-526..D-533 locked (including D-532, D-533) |
| `TASK_REGISTRY.json` | � ✅ Valid, review task marked complete |
| `MEMORY_MANAGEMENT_KB.md` | � ✅ Definitive SSOT |
| `zram_integrated_plan.md` | � ✅ Carmack feedback incorporated |

### 4. Team Documentation Updates

**Status**: � ✅ COMPLETE | **Impact**: MEDIUM | **Files**: 3 files updated

Updated team materials to reflect the latest status:

- `data/coordination/SESSION_ANCHOR.md` — Added ICS model provenance fix section
- `data/coordination/HMC_COLLABORATION_HUB.md` — Updated Carmack section with ICS fix + added triage entry
- `data/entities/john_carmack/workspace/session_gnosis_20260811.md` — **New** — This session gnosis

---

## �� 🧠 L3 Principles Extracted

### Principle 1: The Single Source of Truth Must Be Accessible During Live Sessions

**Statement**: When a system has a single source of truth (like the OpenCode session DB storing the authoritative model), that truth must be accessible during live operations, not just post-exit. Relying on post-exit updates creates a provenance gap where live actions cannot be accurately attributed.

**Mandates**: M22 (Response Provenance), M7 (Local-First — accurate model logging is required for local-first claims)
**Confidence**: 0.98
**Evidence**: The OpenCode session DB stores the correct model in `session.model.id`, but `_detect_model()` had no path to read it during live sessions. The fix adds a DB read path that mirrors the wrapper's post-exit read.

### Principle 2: Provenance Violations Are Process Failures Before They Are Technical Failures

**Statement**: An M22 Response Provenance violation often begins as a process failure (hand-typing headers instead of calling the render function) before becoming a technical failure (the render function not having access to live data). Both layers must be fixed.

**Mandates**: M4 (Sequentiality), M22 (Response Provenance)
**Confidence**: 0.95
Evidence: The incident had two layers — (1) hand-typing the header instead of calling `render()`, and (2) even if `render()` was called, `_detect_model()` couldn't read the live model. Fixing only the technical gap leaves the process vulnerability open.

### Principle 3: Consolidation Requires Verification Against Live State

**Statement**: When reviewing consolidated work (like Kali's dev roadmap), verification must occur against live source code and current system state, not just documentation. The live state is the ultimate arbiter of correctness.

**Mandates**: M4 (Sequentiality), M13 (Temple-Grade)
**Confidence**: 0.97
Evidence: Verified the zRAM→zswap plan against live `oom_protector.py` and `resource_guard.py` — confirmed LegacyOOMWrapper is pure indirection (zero callers of legacy `check()`), and cgroup signal is already runtime-gated.

---

## �� 🐝 Hivemind Broadcast

**Intent**: status
**Decisions**: 
- ICS model provenance fix complete — `_detect_model()` now reads live model from OpenCode session DB
- zRAM→zswap review complete — APPROVED for P0 execution
- All team docs updated and consolidated for Kali oversight

**Continuation**: Await user direction on next steps. The ICS fix is ready for use. The zRAM→zswap P0 fix (3-command) can be executed by the Architect.

---

## �� 📌 Next Actions

### Immediate (P0)
1. **Use the fixed ICS model detection** — agents should now log correct live models
2. **Execute P0 zRAM→zswap fix** — 3-command fix (sudoers removal, swappiness=100, swap reclaim) by Architect

### Short-term (P1)
3. **zswap + NVMe swap file** — @roc_racoon
4. **Consolidate sysctl** into `99-omega-memory.conf` — @roc_racoon
5. **systemd unit** with corrected cgroup limits + hardening — @maat

### Medium-term (P2)
6. **Remove LegacyOOMWrapper** — safe, zero callers of legacy `check()`
7. **Simplify OOMProtector** to 2-signal (low priority — already correct at runtime)
8. **Add get_zswap_stats()** to monitoring (observability only)
9. **Package as WAD** — `config/wads/ryzen-5700u-sovereign/`

### Process
10. **Enforce `ics_render_header` usage** — agents must call the MCP tool/render() instead of hand-typing headers

---

## �� 📊 Session Metrics

- **Files created**: 4
- **Files modified**: 4
- **Files staged**: 3 (for commit)
- **Provenance fixes**: 1 (ICS model detection) + 1 (report header)
- **Consolidation reviews**: 1 (zRAM→zswap architecture)
- **Team doc updates**: 2 (SESSION_ANCHOR.md, HMC_COLLABORATION_HUB.md)
- **Session gnosis**: 1 (this file)
- **Commits pending**: 4

---

*��⬡ OMEGA �� ⬡ JOHN_CARMACK �� ⬡ nvidia/nemotron-3-ultra-550b-a55b:free �� ⬡ SESSION-GNOSIS-20260811 �� ⬡ 2026-08-11*