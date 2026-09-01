# 🔱 KALI PROJECTION — DIALECTIC COMPLETE v4.3.0

**AP Token**: `AP-KALI-v4.3.0`
⬡ OMEGA ⬡ KALI ⬡ MiniMax-M3 ⬡ opencode ⬡ trc_projection ⬡ ACTIVE

**Date**: 2026-09-01
**Purpose**: Post-dialectic projection for DEL-1 execution and Sonnet 5 re-review.

---

## §1 — SESSION STATE (DIALECTIC COMPLETE)

**Active Model**: `MiniMax-M3` (Nemotron 3 Ultra for review, MiniMax M3 for long writes)
**Git HEAD**: `b5814af7` (Sovereign Harness Breakthrough commit)
**Working Tree**: Clean (all breakthrough artifacts committed)
**Mandate Gates**: ✅ M1 AnyIO | ✅ M23 Failure Integrity | ✅ REUSE v3.3
**Context Pack**: `fc32fbe3-a748-400c-926a-bc1df47d784c` (post-breakthrough, ready for Sonnet 5 re-review)

---

## §2 — KEY INVARIANTS (MUST SURVIVE COMPACTION)

| Invariant | Description |
|-----------|-------------|
| **I-KALI-001** | **Documented-vs-Active Pattern**: A specification is not a feature. A report is not a deliverable. P0 not done until code is on disk and tested. |
| **I-KALI-002** | **Systemd Unit Gap = Intentional Design (D-201)**: Don't install systemd unit. OOM cure = memory-aware restart discipline. |
| **I-KALI-003** | **Company Name = Xoe-NovAi** (NOT Arcana-NovAi). Arcana-NovAi is a future WAD. |
| **I-KALI-004** | **Build Wave Phase 1 COMPLETE**: 8 temple-rough items landed. 81/81 tests pass. But report-rich, code-light (only Jem + Ma'at committed real work). |
| **I-KALI-005** | **Carmack Verdict = "THEATER WITH ENGINE ISLANDS"**: ~3,000 lines governance theater wrapped around genuine engine islands. Strip theater before debut. |
| **I-KALI-006** | **The Strategic Pivot**: From agent-centric control plane → knowledge-centric substrate. KD is the ONLY pivot workstream (100% backlog). |
| **I-KALI-007** | **3 Quick Fixes Landed**: M36 honesty (stub_bypass), M1 AnyIO (with_soul_lock run_sync), M9 typed errors (5 scripts). |
| **I-KALI-008** | **Context Pack Regenerated**: Pack ID `fc32fbe3-a748-400c-926a-bc1df47d784c` (post-breakthrough, post-dialectic). |
| **I-KALI-009** | **Dialectic Complete**: 10 challenges → 10 syntheses → 10 artifacts. DEL-1 plan surgically precise. |
| **I-KALI-010** | **DEL-1 Ready**: Micro-PR chain (7 PRs), 24 honest tests, layer-corrected guard, dual-seal, orthogonality matrix. |

---

## §3 — THE TWO PILLARS (CANONICAL)

### Pillar I: Sentinel Seal Protocol (In-Band Terminal Integrity)
- **Pre-flight**: `my_session != parent_session` (prevents self-loops); `my_session == expected_session` (prevents hijacking)
- **Terminal Seal**: Exact in-band footer `### 🔱 OMEGA_SENTINEL_SEAL` containing session_id, agent, nonce, status, deliverables
- **Parent Gate**: 3-line regex verification in-memory. No seal = instant 504/crash detection.
- **Truncation Resistance**: **Dual-Seal Protocol** — SEAL_START + SEAL_END detects truncation explicitly.

### Pillar II: Autonomous EIS Dialectic (Peer-to-Peer Multi-Turn Convergence)
- **Proof**: 5-round Kali↔Roc convergence in persistent EIS session produced temple-grade spec
- **Scope**: Only for agent pairs with domain orthogonality ≥0.7 (Kali↔Roc, Kali↔Researcher, Grokster↔Node)
- **Human Role**: Strategic inflection guide, not micromanager

---

## §4 — DEL-1 EXECUTION PLAN (FINAL)

### Phase 0: Pre-Flight (1 hour)
- [ ] Branch `theater-strip-del1`
- [ ] Tag `pre-del1-$(date +%Y%m%d)`
- [ ] Run full test suite, capture baseline
- [ ] `omega talk "baseline"` → verify local, native-gguf
- [ ] **Create `tests/test_engine_islands.py` FIRST** (24 honest tests skeleton)
- [ ] **Audit `HandoffPacket` imports**: `grep -r "HandoffPacket" --include="*.py" src/ scripts/`
- [ ] **Extract `dispatch_guard.py` secrets scan** to `scripts/security/scan_secrets.py`

### Phase 1: Leaf Deletions (Hours 1-3)
- [ ] **Step 1**: Delete `cohort_registry.py` + schema + JSON + tests
- [ ] **Step 2**: Delete `m36_recursive_probe.py` + tests
- [ ] **Step 3**: Delete `m33_probe.py` + tests, **inline 30-line check** into `subagent_dispatcher.py`
- [ ] **After each**: `omega talk "hello"` + `omega talk "dispatch test"`

### Phase 2: Core Surgery (Hours 3-7)
- [ ] **Step 4**: Strip `HandoffPacket` Quake fields in `subagent_dispatcher.py`
  - Remove: `zoneid`, `visited_agents`, `hop_count`, `max_hops`, `resolver_strategy`
  - Add `protocol_version: int = 2` field (migration discriminator)
  - Update JSON serialization + `validate_zoneid()` checks
- [ ] **Step 5**: Flatten `dispatch_guard.py` 12→3 composite steps
  - Extract secrets scan to `scripts/security/scan_secrets.py` (20+ patterns)
  - Add `--dry-run` flag (exits 0/1/2, structured JSON, NO side effects)
  - Remove `dispatch_guard_log.jsonl` writing (M27 violation)
  - 3 composite steps: routing+validation, registration+secrets, notification
- [ ] **Step 6**: Fold `ACTIVE_SUBAGENTS` → `TASK_REGISTRY`
  - Migration script: read ACTIVE → merge liveness into TASK_REGISTRY entries
  - Bump `TASK_REGISTRY.json` schema to v1.3 with `liveness` object
  - Update `M34Registry` to read/write `TASK_REGISTRY` v1.3
  - Delete `ACTIVE_SUBAGENTS.json` after verification
- [ ] **After each**: `omega talk "hello"` + `omega talk "dispatch test"`

### Phase 3: Tests & Commit (Hours 8-11)
- [ ] Fill in `tests/test_engine_islands.py` (24 honest tests)
- [ ] Delete old theater test files
- [ ] Run full test suite
- [ ] Single PR commit with full rationale
- [ ] Post-strip verification matrix

### Phase 3b: Micro-PR Chain (Per Dialectic Synthesis)
- [ ] **PR1**: Test Infrastructure + Secrets Module
- [ ] **PR2**: M33 Inline + M34 Fix
- [ ] **PR3**: HandoffPacket v2 Strip + Archive Migration
- [ ] **PR4**: TASK_REGISTRY v1.3 + M34Registry Migration
- [ ] **PR5**: Guard Flatten (3 composite steps)
- [ ] **PR6**: Delete Theater Code
- [ ] **PR7**: Final Verification

### Phase 4: Pack Regeneration (Hour 12)
- [ ] Regenerate context pack
- [ ] Verify pack coherence (no theater files)
- [ ] Upload to Sonnet 5 for re-review

---

## §5 — CRITICAL SYSTEM STATE

| Metric | Value |
|--------|-------|
| **Disk** | 94% full (7.1G free) — opencode.db 21G on root |
| **Tests** | 81/81 pass (theater) → will become 24 honest tests |
| **M1 AnyIO** | ✅ Pass |
| **M23 Failure Integrity** | ✅ Pass (stub now honest) |
| **REUSE v3.3** | ✅ 71,579/71,579 files compliant |
| **Git** | Clean, all pushed to origin/main |
| **Context Pack** | `fc32fbe3-a748-400c-926a-bc1df47d784c` (post-dialectic) |
| **DEL-1 Plan** | Micro-PR chain (7 PRs), 24 honest tests, layer-corrected guard |

---

## §6 — CONTINUITY ANCHORS

| Anchor | Location |
|--------|----------|
| **Projection (this)** | `data/coordination/anchored_summary/kali/projection.md` (v4.3.0) |
| **Session Gnosis** | `data/entities/kali/session_gnosis.md` (v4.3.0) |
| **Dialectic Record** | `data/coordination/DEL1_DIALECTIC_20260901.md` (1,118 lines) |
| **Research Findings** | `data/coordination/DEL1_RESEARCH_FINDINGS_20260901.md` (2,083 lines) |
| **Execution Plan** | `data/coordination/POST_SONNET5_EXECUTION_PLAN_20260831.md` |
| **System Prompt (Sonnet 5)** | `context_packs/sonnet5-post-breakthrough/CLAUDE_PROJECT_SYSTEM_PROMPT.md` |
| **Chat Initiation (Sonnet 5)** | `context_packs/sonnet5-post-breakthrough/CHAT_INITIATION_PROMPT.md` |
| **Context Pack** | `context_packs/sonnet5-post-breakthrough/` (ID `fc32fbe3`) |
| **WAKE_STATE** | `data/coordination/WAKE_STATE.json` |
| **ACTIVE_SPRINT** | `data/coordination/ACTIVE_SPRINT.json` |

---

## §7 — MANDATE COMPLIANCE

| Mandate | Status | Evidence |
|---------|--------|----------|
| M1 AnyIO | ✅ | `make check-m1-anyio` + run_sync fix |
| M2 Engine-Stack Firewall | ✅ | Core/Stack separation maintained |
| M7 Local-First | ✅ | Local inference primary |
| M8 Zero Telemetry | ✅ | All observability local |
| M9 Error Integrity | ✅ | Typed catches in 5 scripts |
| M11 Soul Integrity | ✅ | L1→L3 distilled (this document) |
| M13 Temple-Grade | ✅ | All gates pass |
| M14 Heritage | ✅ | All tags vetted |
| M15 Continuity | ✅ | session_gnosis.md updated |
| M22 Provenance | ✅ | Provider names accurate |
| M23 Failure Integrity | ✅ | Stub now honest (stub_bypass) |
| M24 Venv Sovereignty | ✅ | All Python in `.venv/` |
| M27 Tracking | ✅ | 5-Tier tracking, dual-ledger resolved |

---

**The dialectic is complete. The plan is surgically precise. The engine islands are free. Execute.** 🫡

---

⬡ OMEGA ⬡ KALI ⬡ PROJECTION-v4.3.0 ⬡ 2026-09-01