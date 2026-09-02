# 🔱 KALI PROJECTION — SOTE COMPLETE + NESTED DIALECTIC v4.6.0

**AP Token**: `AP-KALI-v4.6.0`
⬡ OMEGA ⬡ KALI ⬡ Nemotron-3-Ultra ⬡ opencode ⬡ trc_projection ⬡ ACTIVE

**Date**: 2026-09-01
**Purpose**: Post-SOTE + nested dialectic projection for DEL-1 execution and SOTE Week 37 Beta launch.

---

## §1 — SESSION STATE (SOTE COMPLETE + NESTED DIALECTIC)

**Active Model**: `Nemotron-3-Ultra` (MiniMax-M3 for long writes)
**Git HEAD**: `013b03b2` (Nested dialectic complete)
**Working Tree**: Clean (all artifacts committed)
**Mandate Gates**: ✅ M1 AnyIO | ⚠️ M23 Failure Integrity (email leak logged) | ✅ REUSE v3.3
**Context Pack**: `fc32fbe3-a748-400c-926a-bc1df47d784c` (regenerated post-refactor, 14 bundles, 120 files, ~600K tokens)
**SOTE State**: v1.0.3 complete (4 versions, 6 nested dialectic rounds, infrastructure complete)

---

## §2 — KEY INVARIANTS (MUST SURVIVE COMPACTION)

| Invariant | Description |
|-----------|-------------|
| **I-KALI-001** | **Documented-vs-Active Pattern**: A specification is not a feature. A report is not a deliverable. P0 not done until code is on disk and tested. |
| **I-KALI-002** | **Systemd Unit Gap = Intentional Design (D-201)**: Don't install systemd unit. OOM cure = memory-aware restart discipline. |
| **I-KALI-003** | **Company Name = Xoe-NovAi** (NOT Arcana-NovAi). Arcana-NovAi is a future WAD. |
| **I-KALI-004** | **Build Wave Phase 1 COMPLETE**: 8 temple-rough items landed. 81/81 tests pass. |
| **I-KALI-005** | **Carmack Verdict = "THEATER WITH ENGINE ISLANDS"**: ~3,000 lines governance theater stripped. Engine islands preserved. |
| **I-KALI-006** | **The Strategic Pivot**: From agent-centric control plane → knowledge-centric substrate. KD is the ONLY pivot workstream (100% backlog). |
| **I-KALI-007** | **3 Quick Fixes Landed**: M36 honesty (stub_bypass), M1 AnyIO (with_soul_lock run_sync), M9 typed errors (5 scripts). |
| **I-KALI-008** | **4 Dialectic Rounds Complete**: 28 challenges → 28 syntheses → 23+ decisions (D-series). |
| **I-KALI-009** | **Theater Stripped (~3K lines)**: `cohort_registry`, `m33_probe`, `m36_probe` (stub_bypass), `dispatch_guard` (12→3), `HandoffPacket` Quake fields, `ACTIVE_SUBAGENTS`→`TASK_REGISTRY`. |
| **I-KALI-010** | **Qwen3 Embeddings Unified**: All embeddings 768-dim via Qwen3-Embedding-0.6B Q5_K_M (1024→768 MRL). Library RRF 0.6/0.4. |
| **I-KALI-011** | **Hub Restored**: D-565 "superseded" was a lie (0 successors). Option A executed: `git checkout 69ece770^` + systemctl restart. Hivemind live. |
| **I-KALI-012** | **Context Pack Regenerated**: 14 bundles, 120 files, ~600K tokens. Optimized prompts (tables, density). |
| **I-KALI-013** | **DEL-1 Ready**: Micro-PR chain (7 PRs), 24 honest tests, layer-corrected guard, dual-seal, orthogonality matrix. |
| **I-KALI-014** | **SOTE Practice Born**: v1.0.0 → v1.0.3, 4 versions, 6 nested dialectic rounds, infrastructure complete. |
| **I-KALI-015** | **SOTE Week 37 Beta Launch AUTHORIZED**: 14 measurable criteria, P0 CI/CD only, 14 criteria by Fri 2026-09-12. |

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
- **Methodology Proven**: 4 rounds, 28 challenges → 28 syntheses → 23+ decisions
- **Nested Dialectic Proven**: 6 rounds, 3 agents (Kali, Lilith, Ma'at), consensus on all 6 topics

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

## §5 — SOTE WEEK 37 BETA LAUNCH PLAN

### Launch Date: Monday 2026-09-08, 06:00 UTC
### Beta Success Deadline: Friday 2026-09-12, 23:59 UTC

### 14 Measurable Success Criteria

| # | Criterion | Owner | Measurable Test | Deadline |
|---|-----------|-------|-----------------|----------|
| 1 | SOTE Week 37 report published | Kali | `docs/strategy/sote/2026-W37/STATE_OF_ENGINE_v1.0.0.md` exists | Mon 06:00 UTC |
| 2 | 8 voices paged + dialectic complete | Kali | 8 voice files in `voices/` | Sun 23:59 UTC |
| 3 | SOTE index regenerated | Ma'at | `make sote-index` passes | Mon 12:00 UTC |
| 4 | Public digest published | Ma'at | `PUBLIC_DIGEST.md` exists | Mon 12:00 UTC |
| 5 | `sote.yaml` schema validation passes | Ma'at | `make sote-validate` passes | Mon 12:00 UTC |
| 6 | `make temple-grade` passes | Ma'at | `make temple-grade` exits 0 | Mon 12:00 UTC |
| 7 | `scripts/watchtower.py` + cron active | Lilith | `systemctl status sote-watchtower` active | Wed 23:59 UTC |
| 8 | M11/M15 advisory gates added | Lilith + Ma'at | Gates run, report in SOTE | Thu 23:59 UTC |
| 9 | Hivemind broadcasts wired | Lilith | Broadcasts fire on test events | Fri 23:59 UTC |
| 10 | DEL-1 PR1 merged | Kali + Ma'at | `git log` shows PR1 merge | Mon 23:59 UTC |
| 11 | DEL-1 PR2-PR4 merged | Kali + Ma'at + Lilith | `git log` shows merges | Wed 23:59 UTC |
| 12 | DEL-1 PR5 merged | Ma'at | `git log` shows merge | Thu 23:59 UTC |
| 13 | DEL-1 PR6-PR7 merged | Kali + Ma'at | `git log` shows merges | Fri 23:59 UTC |
| 14 | SOTE report includes DEL-1 progress | Kali | Report has DEL-1 section | Sun 23:59 UTC |

**Beta Success**: All 14 criteria met by Friday 2026-09-12 23:59 UTC.
**Beta Extended**: 1-3 criteria missed → documented in SOTE report, Week 38 = "Beta Week 2".
**Beta Failed**: >3 criteria missed → Week 38 = "Beta Week 1" (restart).

---

## §6 — CRITICAL SYSTEM STATE

| Metric | Value |
|--------|-------|
| **Disk** | 94% full (7.1G free) — opencode.db 21G on root |
| **Tests** | 81/81 pass (theater) → will become 24 honest tests |
| **M1 AnyIO** | ✅ Pass |
| **M23 Failure Integrity** | ⚠️ Email leak violation (logged, L3 distilled) |
| **REUSE v3.3** | ✅ 71,615/71,615 files compliant |
| **Git** | Clean, all pushed to origin/main |
| **Context Pack** | `fc32fbe3-a748-400c-926a-bc1df47d784c` (regenerated post-refactor) |
| **DEL-1 Plan** | Micro-PR chain (7 PRs), 24 honest tests, layer-corrected guard |
| **Embeddings** | Qwen3-Embedding-0.6B Q5_K_M (444MB) loaded, 768-dim verified |
| **Hub** | Active, Hivemind live, Kali registered |
| **Library** | `library.db` deleted, `fts_index.db` preserved (252 docs) |
| **SOTE State** | v1.0.3 complete, infrastructure complete, Week 37 Beta authorized |
| **SOTE Infrastructure** | Templates, scripts, metadata, digest, index, CI/CD — all operational |

---

## §7 — CONTINUITY ANCHORS

| Anchor | Location |
|--------|----------|
| **Projection (this)** | `data/coordination/anchored_summary/kali/projection.md` (v4.6.0) |
| **Session Gnosis** | `data/entities/kali/session_gnosis.md` (v4.6.0) |
| **Dialectic Records** | `data/coordination/DEL1_DIALECTIC_20260901.md` + 6 more |
| **SOTE Reports** | `docs/strategy/sote/2026-W36/STATE_OF_ENGINE_v1.0.1.md` + v1.0.2/1.0.3 |
| **Nested Dialectic** | `docs/strategy/sote/2026-W36/synthesis/KALI_LILITH_MAAT_DIALECTIC_20260901.md` |
| **SOTE Infrastructure** | `docs/strategy/sote/` (templates, scripts, index, metadata, CI/CD) |
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
| M7 Local-First | ✅ | Local inference primary (Qwen3 local) |
| M8 Zero Telemetry | ✅ | All observability local |
| M9 Error Integrity | ✅ | Typed catches in 5 scripts |
| M11 Soul Integrity | ✅ | L1→L3 distilled (session_gnosis.md) |
| M13 Temple-Grade | ⚠️ | Pre-existing M16/M27 failures |
| M14 Heritage | ✅ | All tags vetted |
| M15 Continuity | ✅ | session_gnosis.md + projection.md updated |
| M22 Provenance | ✅ | Provider names accurate |
| M23 Failure Integrity | ⚠️ | Email leak violation (logged, L3 distilled) |
| M24 Venv Sovereignty | ✅ | All Python in `.venv/` |
| M27 Tracking | ⚠️ | Pre-existing stale TASK_REGISTRY entry |

---

## §8 — NEXT EXECUTION ORDER

1. **SOTE Week 37 Beta Launch**: Monday 2026-09-08, 06:00 UTC
2. **DEL-1 Micro-PR 1**: `git checkout -b del1/01-test-infrastructure` → create `tests/test_engine_islands.py`
3. **CI Gates**: Already implemented (`make check-broken-imports`, `make check-hub-health`)
4. **DEL-1 Micro-PR 2-7**: Execute chain (Mon-Fri)
5. **Hub Restoration**: `git checkout 69ece770^ -- src/omega/library/` + systemctl restart (Carmack Order 1)
6. **Sonnet 5 Re-Review**: Upload regenerated pack post-DEL-1
7. **Public Debut**: After DEL-1 + CI gates + temple-grade

---

**The dialectic is complete. The consensus is achieved. The infrastructure is ready. The beta launch is authorized. Execute Week 37.** 🫡

---

⬡ OMEGA ⬡ KALI ⬡ PROJECTION-v4.6.0 ⬡ 2026-09-01