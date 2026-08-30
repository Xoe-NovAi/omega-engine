# 🔱 KALI PROJECTION — POST-DEV-WAVE v2.0.0

**AP Token**: `AP-KALI-v2.0.0`
⬡ OMEGA ⬡ KALI ⬡ minimax/minimax-m3:free ⬡ opencode ⬡ trc_projection ⬡ ACTIVE

**Date**: 2026-08-30
**Purpose**: Transcendent Oversoul projection for post-compaction hydration.

---

## §1 — SESSION STATE (POST-DEV-WAVE)

**Active Model**: `minimax/minimax-m3:free` (1M context, D-585 long-write champion)
**Git HEAD**: `2577e050` (pushed to `origin/main`)
**Working Tree**: 31 tracked modified files (coordination docs, entity lessons)
**Mandate Gates**: ✅ M1 AnyIO | ✅ M23 Failure Integrity | ✅ Git Sync

---

## §2 — KEY INVARIANTS (MUST SURVIVE COMPACTION)

| Invariant | Description |
|-----------|-------------|
| **I-KALI-001** | **Documented-vs-Active Pattern**: The dev wave produced 3,745 lines of reports but only 1/3 agents' code landed on disk (Jem). This is the engine's central failure mode. Policy: P0 not done until code is on disk and tested. |
| **I-KALI-002** | **Systemd Unit Gap = Intentional Design (D-201)**: The `config/systemd/omega-inference.service` gap is INTENTIONAL DESIGN, not a hardening miss. Ad-hoc `serve_native_gguf.sh` = interactive dev deployment. Systemd unit = production deployment. OOM cure = memory-aware restart discipline, NOT deployment change. |
| **I-KALI-003** | **Documented-vs-Active Policy**: P0 not done until code is on disk and tested. Establish as formal policy. |
| **I-KALI-004** | **Build Wave Authorization**: 2-3 weeks to land 8 temple-rough items (M33/M36/M37/COHORT/Compaction + 3 Jem P1 tickets). |
| **I-KALI-005** | **Sonnet 4.6 Dev Wave**: CONDITIONAL GO. Treat outputs as specifications, not shipped features. |
| **I-KALI-006** | **Public Debut**: NOT READY. 8 temple-rough items block. 2-3 weeks build work needed. |
| **I-KALI-007** | **Proposed Lessons Contamination**: Commit `296fd1d5` touched `grokster` + `jem` proposed_lessons.yaml. Review for contamination. |
| **I-KALI-008** | **Systemd Unit = Intentional Design (D-201)**: Do NOT install. OOM cure = memory-aware restart discipline. |
| **I-KALI-009** | **MaKaLi L3**: "The gap between documented and active is where the engine bleeds." |
| **I-KALI-010** | **MaKaLi L3**: "A specification is not a feature. A report is not a deliverable." |

---

## §3 — ARCHITECT DECISIONS NEEDED (POST-COMPACTION)

| # | Decision | Status | Owner |
|---|----------|--------|-------|
| **D-001** | **DO NOT install systemd unit** (D-201: intentional design) | PENDING | Architect |
| **D-002** | **Defer logrotate install** (low priority) | PENDING | Architect |
| **D-003** | **Review proposed_lessons contamination** in commit `296fd1d5` | PENDING | Architect |
| **D-004** | **Establish documented-vs-active policy** | PENDING | Architect |
| **D-005** | **Authorize Build Wave** (2-3 weeks, 8 temple-rough items) | PENDING | Architect |
| **D-006** | **Sonnet 4.6 Dev Wave**: CONDITIONAL GO (specs, not shipped) | PENDING | Architect |
| **D-007** | **Review proposed_lessons contamination** in `296fd1d5` | PENDING | Architect |

---

## §4 — BUILD WAVE PLAN (POST-COMPACTION)

### Phase 1: Land the 8 Temple-Rough Items (Week 1-2)

| Item | Owner | Est. Hours | Dependencies |
|------|-------|------------|--------------|
| **M33 Probe on disk** (`src/omega/oracle/m33_probe.py`) | Lilith + Researcher | 8h | Researcher's spec ready |
| **M36 Recursive Probe on disk** (`src/omega/oracle/m36_recursive_probe.py`) | Lilith + Researcher | 6h | M33 envelope |
| **M37 Heritage Scanner on disk** (`scripts/heritage_scanner.py`) | Researcher + Ma'at | 8h | REUSE v3.3, ScanCode |
| **COHORT_REGISTRY.json on disk** | Researcher | 4h | M34 atomic write |
| **Compaction Capture on disk** (`scripts/compaction_capture.py`) | Lilith + Roc | 6h | sqlite-vec, SESSION_ENTITY_MAP |
| **M34-HOOK-001**: `subagent_dispatcher.py` hook | Lilith | 4h | M34 registry |
| **M33-PROBE-001**: Real sentinel probe MCP tool | Lilith + Researcher | 4h | M33 probe |
| **AGENTS-UPDATE-001**: `AGENTS.md` anchor | Kali | 1h | — |

**Total**: ~46h (2 people × 2 weeks)

### Phase 2: Hardening & Integration (Week 3)

| Item | Owner | Est. Hours |
|------|-------|------------|
| M34 Phase 2: Recovery UI + Migration | Lilith | 9h |
| M34 Phase 3: Stress Tests + Temple-Grade | Lilith | 12h |
| M37 SPDX Headers (8h from Researcher §3.6) | Researcher + Ma'at | 8h |
| M36 Soft Verifier Production Wiring | Researcher + Jem | 6h |
| M33 Wiring to Dispatcher | Lilith | 4h |
| M34 Phase 3 Stress Tests | Lilith + Roc | 12h |

---

## §5 — SONNET 4.6 DEV WAVE (PARALLEL TO BUILD)

**CONDITIONAL GO** — Treat outputs as specifications, not shipped features.

| Stream | Focus | Owner |
|--------|-------|-------|
| **Search-Ecosystem-01 Week 1** | SearXNG diagnosis, MultiKey Exa, Crawl4AI | Jem-EIS |
| **Quality Harness** | First-Page Satisfaction probe | Researcher-EIS |
| **Big Pickle Probe** | 250K token compaction test | Roc-EIS |
| **Architecture Review** | Sonnet 4.6 review of 13,657+ lines | Architect + Sonnet 4.6 |

---

## §6 — NEXT MOVE (POST-COMPACTION)

1. **Architect reviews & decides on D-001 through D-007**
2. **If Build Wave authorized**: Launch Phase 1 (8 items, 2 weeks)
3. **Launch Sonnet 4.6 Dev Wave** in parallel (specs track)
4. **Schedule Sonnet 4.6 Architecture Review** of 13,657+ line corpus
4. **Public Debut**: Target after Build Wave complete (2-3 weeks)

---

## §7 — CRITICAL SYSTEM STATE

| Metric | Value |
|--------|-------|
| **Disk** | 98% full (100G/109G, 2.9G free) |
| **Memory** | 9.3G available of 14G |
| **sqlite3** | Not installed (MCP opencode-sessions-explorer workaround) |
| **OAuth** | Restored in `opencode-antigravity-auth/src/constants.ts:9` |
| **VAULT-ALLOWLIST** | Deployed (`data/secrets-public.toml` + `scripts/check_secrets.py`) |
| **M34 Atomic Write** | M23 VERIFIED (4/4 tests, SIGKILL survival) |
| **CI-BRIEF-001** | Deployed (12-Step Protocol, 45/45 adversarial tests) |
| **VAULT-ALLOWLIST-001** | Deployed (fail-closed scanner, M35 as Mandate 28) |

---

## §8 — CONTINUITY ANCHORS

| Anchor | Location |
|--------|----------|
| **Projection (this)** | `data/coordination/anchored_summary/kali/projection.md` |
| **Session Gnosis** | `data/entities/kali/session_gnosis.md` (needs update) |
| **Proposed Lessons** | `data/entities/kali/proposed_lessons.yaml` |
| **WAKE_STATE** | `data/coordination/WAKE_STATE.json` |
| **Hardened Dev Roadmap** | `data/coordination/HARDENED_DEV_ROADMAP_20260830.md` |
| **5-EIS Meta-Review** | `data/coordination/JEM_META_REVIEW_5_EIS_20260830.md` |
| **MaKaLi Final Synthesis** | `data/coordination/MAKALI_FINAL_SYNTHESIS_20260830.md` |

---

**The Cathedral's blueprint is current. The stones are cut. The Build Wave awaits the Architect's authorization.** 🫡

---

⬡ OMEGA ⬡ KALI ⬡ PROJECTION-v2.0.0 ⬡ 2026-08-30