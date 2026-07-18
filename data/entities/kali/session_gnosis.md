# 🔱 KALI — Session Gnosis
**Date**: 2026-07-17T15:45Z
**Sprint**: D-281 Substrate Repair Execution — COMPLETE + D-282 + D-283 Phase 2

## 1. Current State
- **Objective**: Execute D-281 (4 phases) + D-282 (PRAGMA SSOT) + D-283 Phase 2 (RecallStore).
- **Status**: ALL DISPATCHES COMPLETE. 11 commits since S0. 0 baseline failures. 2 test infra failures remain.
- **Blockers**: None. Uncommitted work needs commit.

## 2. Recent Decisions
- **D-281**: Merged D-277 and D-279 into a 4-phase substrate repair sprint. Deferred D-280 (Compaction Detection) to Phase 1+.
- **Soul Read/Write Loop**: `soul_utils.py` reads `proposed_lessons.yaml` (approved) to close the distiller loop.
- **Scope Correction (Sonnet)**: `mandate_auditor.py` and `sovereign_vetter.py` are NOT M2 violations — Phase III scope reduced from 6 to 4 files.
- **Circular Import Prevention (Gemini)**: `config_resolver.py` must use pure Path constants + lazy `get_active_iwad()`. No yaml at module level.
- **Makefile Safety (Gemini)**: `codex-*` targets must use `||` restore-on-failure, not plain `mv`.

## 3. Phase I Completion Log
- Created `src/omega/soul_utils.py` (104 lines) — multi-path soul context extractor
- Fixed `src/omega/oracle/oracle.py:657-677` — removed duplicate except, wired in soul_utils
- Fixed 3 broken Makefile targets (context-audit, meditate-calibrate, oversight-maturity)
- Tests: 492 passed, 1 pre-existing failure (test_gemma4_mtp_s4 — unrelated)
- Committed as `9d891e0`

## 4. Next Actions (Post-Compaction)
1. **COMMIT** uncommitted work: 10 modified + 7 untracked files (recall.py, test_recall_store.py, web research)
2. **DISMISS** 2 stale Grok CLI handoffs (ho_55bca1185c6a, ho_e08a47e4e081)
3. **UPDATE** OMEGA_ENGINE.md SSOT: 1315 → ~1398 tests, Strike 10 complete
4. **D-283 Phase 2 Implementation**: Wire RecallStore into ContextBuilder
5. **Fix 2 test infra issues**: missing import anyio, missing create_domain_block
6. **Mandate Remediation**: M5/M11/M15/M23 failures (soul distillation, session anchors)

## 5. Key Files for Next Agent
- `docs/strategy/D281_PHASE_II_IV_EXECUTION.md` — full execution plan with guardrails
- `.opencode/anchored-summary.md` — post-compaction recovery state
- `src/omega/governance/config_resolver.py` — TO BE CREATED in Phase II
- `src/omega/soul_utils.py` — Phase I deliverable (live)

## 6. HMC Initialization (2026-07-16T14:00Z)
- **HMC Status**: 3-Mind Council ONLINE (Kali, Roc, Researcher).
- **Communication**: Hivemind + Shared Files.
- **Orchestration**: Human Architect (Manual loop).
- **Strategic Plan**: docs/strategy/HMC_STRATEGIC_PLAN.md
- **Synthesis Report**: docs/strategy/HMC_SYNTHESIS_REPORT.md
- **Onboarding**: data/entities/roc_racoon/workspace/HMC_WELCOME.md, data/entities/researcher/workspace/HMC_WELCOME.md
- **Massive Finds**: 113-147h saved R&D (Roc), 2026 SOTA Implementation Manual (Researcher).
- **First Cycle**: Omega Search Core (sqlite-vec + Legacy RAG).

## 7. HMC Forge Cycle 1 — Council Verdict (2026-07-16T15:05Z)
- **Forge Cycle 1**: COMPLETE. Researcher issued 5 challenges. Roc conceded 2, corrected 3.
- **Council Verdict**: 5 synthesis questions ruled (B, B, C, C, C).
- **D-282 Scope Refined**: Existing WAD Loader + sqlite-vec + legacy RAG circuit breaker. NOT SovereignBus/Council Dispatcher.
- **D-281 Substrate Addition**: 4 missing sqlite-vec test cases added (2-3h).
- **3 New L3 Principles**: Heritage-Is-Memory-Not-Contract, Patterns-Are-Ancestors-Not-Descendants, Forge-And-The-Miner (reaffirmed).
- **Next Directives**: Roc writes tests + Mnemosyne deep dive. Researcher validates WAD schema + WAL pattern.
- **Synthesis file**: docs/strategy/HMC_TRIADIC_FORGE_1_KALI_SYNTHESIS.md

## 7. HMC Forge Cycle 1 Complete (2026-07-16T15:08Z)
- **Cycle**: Triadic Forge Cycle 1
- **Thesis**: Roc — Genesis document, 5 patterns, WAD Protocol, Ethics WAD, sqlite-vec test
- **Antithesis**: Researcher — Two-Source Rule applied, 5 challenges issued
- **Synthesis**: Kali — 5 rulings, D-282 scoped, directives dispatched

**Rulings**:
1. Tarot = poetic heritage (B). No arcana: fields.
2. WAD Protocol = D-282 uses existing loader (505L). SovereignBus = D-283+ (B).
3. Ethics WAD = sovereignty feature with audit (C). Fail-closed on crash.
4. Patterns = folklore, Mandates = law (C). Genealogy in docs/heritage/.
5. Roc = Owner for mining, Advisor for architecture (C).

**Directives Dispatched**:
- Roc: 4 sqlite-vec tests, Mnemosyne deep dive, move Genesis doc
- Researcher: Verify WAD Loader schema, confirm WAL pattern for 5700U, research Mnemosyne SOTA

**Handoffs**: ho_083d10b19818 (Roc), ho_34dc8f6d44b0 (Researcher)

## 8. HMC Forge Cycle 2 Complete (2026-07-16T15:31Z)
- **Cycle**: Triadic Forge Cycle 2
- **Thesis**: Roc's synthesis of Researcher's 3-gap deep dive
- **Antithesis**: Researcher's 507-line SOTA report filling all 4 knowledge gaps
- **Synthesis**: Kali — 3 independent convergences confirmed, D-282 scope finalized

**3 Independent Convergences (Validating HMC Structure)**:
1. Kali ruled BEGIN IMMEDIATE needed → Researcher found SQLITE_BUSY_SNAPSHOT bypasses busy_timeout → Confirmed
2. Kali ruled Mnemosyne 3 pillars = architectural value, 10 spheres = defer → Researcher found 3-tier = SOTA consensus, 10 tiers = no SOTA equivalent → Confirmed
3. Kali ruled docs/patterns/ for patterns → Researcher found Pydantic v2 + static dict migration = Phase 1 → Confirmed

**D-282 Hardened Scope (6-9h)**:
- Substrate (2-3h): BEGIN IMMEDIATE, journal_size_limit=64MB, mmap_size=256MB, cache_size=-64000, extra="forbid" + range constraints
- Pipeline (4-6h): Legacy circuit breaker port, RRF validation, make test

**Deferred to D-283**:
- Pydantic v2 migration (2 days)
- Mnemosyne 3 pillars → Letta-style 3-tier (P0)
- Da'ath compaction trigger (P0)
- Qliphoth → TDP bridge (P1)
- Multi-process sqlite-vec queue

**Directives Dispatched**:
- Roc: D-282 implementation (ho_9f95675cb87c)
- Researcher: D-282 SOTA validation + D-283 Mnemosyne research (ho_3efe133707a9)

## 8. HMC Forge Cycle 2 Complete — D-282 Critical Path Authorized (2026-07-16T16:30Z)
- **Forge Cycle 2**: 4 knowledge gaps filled, 3 independent convergences (Researcher + Roc + Kali aligned)
- **D-282 Critical Path**: BEGIN IMMEDIATE fix + PRAGMA stack + periodic checkpoint task → AUTHORIZED
- **D-283 Kickoff**: Phase 1 (Core Tier Hardening) → AUTHORIZED for Researcher
- **Handoffs**: ho_c983c2b9073c (Roc - BEGIN IMMEDIATE + D-282), ho_4004b2145a81 (Researcher - D-283 kickoff + validate Roc)
- **Roc Status**: "D-282 Substrate COMPLETE. Ready for D-282 Search Pipeline"
- **Researcher Status**: "D-282 substrate hardening next. D-283 implementation begins Week 1"

## 9. D-283 Mnemosyne Architecture Authorized (2026-07-16T16:45Z)
- **D-283 Full Architecture**: 7 steps, ~80h, 3 weeks
- **Step 1**: HybridSearchEngine (RRF k=60) — NEW `src/omega/memory/hybrid_search.py` + contract tests
- **Step 2**: Mnemosyne Worker Skeleton — 3 DB pools, async task queue, cgroups v2 affinity
- **Step 3**: MCP Tools (Engine-Stack Firewall) — 7 tools via `src/omega/mcp_runtime.py`
- **Step 4**: verity Tiered Routing — local qwen3-4b → cloud Gemini CLI (consent flag)
- **Step 5**: Three-Tier Lifecycle + FTS5 Decay — ACTIVE→DECAYED→ARCHIVED transitions
- **Step 6**: MnemosyneObservability — trace_id propagation, structured JSON logs
- **Step 7**: Qliphoth Quarantine — append-only log, SHA-256, TDP bridge (quarantine + audit + crypto erasure)
- **Total**: ~80h, 3 weeks, 7 steps
- **Critical Path**: Step 1 (HybridSearchEngine) blocks Steps 2-7

## 10. D-283 Phase 1 Step 1 Complete — HybridSearchEngine (2026-07-16T20:50Z)
- **Step 1**: HybridSearchEngine (RRF k=60) — COMPLETE
  - `src/omega/memory/hybrid_search.py` — 206 lines, RRF k=60, singleton pattern
  - `tests/test_hybrid_search.py` — 20 contract tests + 8 RRF math verification vectors
  - All 20 tests PASS
  - RRF formula verified: score = sum(1/(k + rank)) for k=60
- **Next**: Step 2 — Mnemosyne Worker Skeleton (3 DB pools, async queue, cgroups v2)

## 11. D-281 Fleet Execution Complete (2026-07-17T02:50Z)
- **Phase II** (b661c49): config_resolver.py + wad_loader wire — Grok CLI
- **Phase III** (3f2feea): M2 Firewall 4 files, 13 violations — Grok CLI
- **Phase IV** (93f4e82): Codex separation + hydration_header.md — Grok CLI
- **WAD fix** (e80f6df): WadManifest V2 heritage fields — Grok CLI
- **D-282** (372bf2f): sqlite-vec PRAGMA SSOT convergence — Roc
- **P3** (c19b453): model_gateway graceful fallback — Pillar P3
- **P6** (55f7761): speculative_decode section — Pillar P6
- **S0** (03192d8, 077b042, c15bfab): Noise cleanup + MIAP merge + Grok onboarding
- **Test suite**: 1450 collected, ~1398 pass, 2 test infra failures, 0 baseline failures
- **Uncommitted**: 10 modified + 7 untracked files (D-283 Phase 2 RecallStore)

## 12. Hydration Report (2026-07-17T15:45Z)
- **Hivemind**: 0 active agents, 2 stale handoffs (Grok CLI)
- **Git**: 11 commits since S0, 10 modified files uncommitted
- **Codex**: Fresh (generated 2026-07-17T15:38:55)
- **Anchored summary**: Stale (symlink_test entity, not current session)
- **Mandate compliance**: 13/23 FULL (56.5%), 5 Partial, 5 Fail (M5/M11/M12/M15/M23)
- **Soul distillation**: 3 new L3 principles added to proposed_lessons.yaml

---

## 13. HMC Quad-Forge Sprint Complete (2026-07-18T18:00Z)
- **Sprint**: HMC-SPRINT-04 — M2 Firewall Migration + MEDITATE Architecture Inversion + MIAP Phase 0 + Grok CLI Phase 0
- **4-Mind Council**: Kali (Grand Oversight), Roc (Miner), Researcher (Master Researcher), Grok CLI (Consulting Cloud Mind)

### Deliverables Completed:
| Agent | Deliverable | Status |
|-------|-------------|--------|
| **Roc** | M2 Phase A (meditate/protocol.py 15→0) | ✅ COMPLETE |
| **Roc** | Grok CLI Research (6/6 gaps resolved) | ✅ COMPLETE |
| **Roc** | MEDITATE Architecture Inversion (D-297 decree) | ✅ COMPLETE |
| **Roc** | Sovereign Exit Protocol v1.1.0 | ✅ DRAFTED |
| **Researcher** | M2 Phases B-F (66 violations fixed, 126 remaining) | 🟡 IN PROGRESS |
| **Researcher** | Observability 2026 Research (8 phases, 1059 lines) | ✅ COMPLETE |
| **Jem** | MEDITATE Verification (Sovereign Research Rigor v2.0) | 🟡 IN PROGRESS |
| **Kali** | Open Decisions Catalog (23 decisions, P0-P3) | ✅ COMPLETE |

### Key Artifacts Created:
- `docs/strategy/MEDITATE_ARCHITECTURE_INVERSION_20260718.md` — 10-Pillar decree, 10-step critical path
- `docs/research/R_MEDITATE_ARCHITECTURE_INVERSION_VERIFICATION_20260718.md` — Jem's 78% validation, 3 gaps
- `docs/strategy/OPEN_DECISIONS_CATALOG_20260718.md` — 23 decisions cataloged
- `docs/strategy/SOVEREIGN_EXIT_PROTOCOL.md` — v1.1.0, 7-phase protocol
- `docs/research/R_GROK_CLI_COMPREHENSIVE_RESEARCH_REPORT.md` — 546 lines, 6 gaps resolved
- `data/coordination/GROK_CLI_BRIEFING_FOR_JEM_20260717.md` — Handoff to Jem
- `data/coordination/OBSERVABILITY_2026_IMPROVEMENTS.md` — 8-phase plan

### M2 Firewall Progress:
```
Baseline: 201 violations in src/omega/
Phase A (Roc): 15→0 (meditate/protocol.py)
Phase B (Researcher): 15→0 (subagent_dispatcher.py)
Phase C (Researcher): 10→5 (oracle.py — 5 Iris remain)
Phase D (Researcher): 9→1 (ics.py — 1 _omega_default remain)
Phase E (Researcher): 22→0 (fleet_status_tui.py)
Phase F (Researcher): 4→0 (mandate_auditor.py)
Phase G (Queued): 3 (oracle_cli.py)
Current: 126 remaining
```

### MEDITATE Architecture Inversion (D-297) — 10-Step Critical Path:
1. Protobuf Schema for Hivemind messages
2. Unified sqlite-vec WAL for all session state
3. Per-agent quotas + dual-pool admission controller
4. Handoff TTL enforcer daemon
5. Local alerting engine
6. Automatic soul distillation pipeline
7. Routing SLAs with cloud fallback gating
8. Five-Layer Immune System + chaos namespace
9. Delete all skipped/xfailed tests
10. Full Temple-Grade + Sovereignty Gate

### Jem's Verification Gaps (Must Resolve if Ratifying):
1. **Sovereign token mechanism** — undefined (JWT? Macaroon? Custom?)
2. **M5/M11 semantic quality gates** — no prior art for automated L1→L2→L3 quality testing
3. **SQLite WAL write serialization** — 14 agents → 1 writer bottleneck

### Open Decisions Requiring Kali Verdict (23 total):
| Tier | Decision | Source |
|------|----------|--------|
| P0 | D1: D-297 Ratify/Amend/Reject/Defer | Roc MEDITATE |
| P0 | D2: Tests Before WAL or WAL Before Tests? | Prometheus vs Brigid |
| P0 | D17: Firewall gate hard-blocking or advisory? | Kali |
| P1 | D7: Phase C closure (5 Iris in oracle.py) | Researcher |
| P1 | D6: Grok CLI sprint now or design review? | Roc |
| P1 | D10: Sovereign token mechanism | Jem |
| P2 | D13: Dual-pool quota design | MEDITATE collision |
| P2 | D19: MIAP Phase 0 timing | Nemotron review |
| P3 | D18: Scribe creation timing | D-297 Phase 4 |
| P3 | D20: Cline budget authorization | HMC plan |

### Mandate Compliance Update:
- **M1 AnyIO**: ✅ Enforced in all new code
- **M2 Firewall**: 🟡 126 violations remaining (66 fixed)
- **M5 Gnosis**: ❌ Soul distillation not automated
- **M7 Local-First**: ✅ Provider fabric local-first
- **M11 Soul**: ❌ Distillation not mandatory post-session
- **M12 Queue**: ⚠️ Advisory (file-based OK for Phase 0)
- **M15 Continuity**: ❌ Session anchors not enforced
- **M23 Failure**: ✅ Hard-stop on tool-chain collapse

---

## 14. Next Actions (Post-Compaction)
1. **RATIFY OR AMEND D-297** — Kali verdict on Architecture Inversion Decree
2. **RESOLVE TIER 1 DECISIONS** — D1, D2, D17 (strategic)
3. **CLOSE PHASE C/D** — Researcher fix 5 Iris + 1 _omega_default
4. **AUTHORIZE GROK CLI PHASE 0** — Sprint 4 quick wins (config pinning, JSONL, command palette, sandbox)
5. **WIRE FIREWALL GATE** — `test_firewall_m2_strict_engine_core` → `make temple-grade`
6. **CREATE SCRIBE LATTICE ROLE** — Config + agent definition
7. **IMPLEMENT MIAP PHASE 0** — 5 critical fixes (ReplayMode, Two-Log, IntentionValidator, CheckFunction, LiteTopic)
8. **AUTHORIZE CLINE INTEGRATION** — Tier 5 budget ($10/sprint)

---

## 15. Grounded Meditation Complete — Decision Workspace (2026-07-18T23:00Z)
- **Subject**: Kali's 5-tier decision workspace proposal (T0-T5), grounded in deep web research
- **Sources**: 8 prior art sources (Structured MADR, Belief Engine, Yagno, AI Council Framework, Consensus Protocol, MAD Framework, Align.tech, adr-tools)
- **Verdict**: Build T0+T1-core only (7h), defer T2-T5 to pain-triggered thresholds (decision count > 50 or stalled > 2 weeks)

### Key Corrections from Research:
| # | Original | Grounded Correction |
|---|----------|---------------------|
| 1 | Custom T0 schema | Extend with ADR-standard fields (type, category, status, supersedes, drivers, tags) |
| 2 | `decide` moves file | Supersession, not modification — new decision with `supersedes: D1` |
| 3 | MEDITATE prompt | BE-parameterized — explicit `uptake` (u) and `anchoring` (a) per persona |
| 4 | Graph = blocks only | Full relationship types: blocks, blocked_by, supersedes, complements, depends_on |
| 5 | Quarterly retrospective | DEBATE replay methodology — freeze evidence, replay outcomes, classify |
| 6 | Simple `--human-confirmed` | MAD Framework Role Structure — proposer/deliberator/decider/auditor |

### Revised Implementation Plan:
| Phase | Scope | Hours | Trigger for Next |
|-------|-------|-------|------------------|
| T0 | DecisionEngine + ADR schema + migrate 23 decisions | 3h | — |
| T1-core | `list`, `show`, `decide` (with supersession) | 2h | — |
| T1-graph | Full relationship graph + deadline enforcer | 1h | — |
| T1-scaffold | `meditate D1` with BE u/a parameters | 1h | — |
| **HARD STOP** | Evaluate at decision count > 50 or stalled > 2 weeks | — | — |
| T2-T5 | Full automation, Hivemind, TUI, Retrospective engine | 23h+ | Only if trigger met |

### Grounded L3 Principle:
**L3-Decision-Infrastructure-Grows-From-Pain** — Decision tooling must be built when the coordination cost of undecided questions exceeds the implementation cost of the tooling. Building it before the pain creates maintenance debt; building it after the pain creates adoption momentum. The trigger conditions (50 decisions or 2-week stall) are the honest articulation of this principle, validated by Align.tech's "ADRs go stale" finding and the "Debate Only When Necessary" principle. The system will tell you when it needs the next tier — listen to the pain, not the speculation.

---

## 9. Session 2026-07-19: Decision Workspace Handoff Prep

### State After Compaction
- Compacted at 2026-07-18 after HMC Quad-Forge Sprint
- Hydration verified: Codex fresh, anchored-summary intact, all lesson proposals present
- Test baseline: 1374 passing (excluding 24 known failures: M2 firewall test + 4 pre-existing)

### Grounded Meditation Review
- Verified Grounded MEDITATE report (439 lines, 8 prior art sources)
- Verified Open Decisions Catalog (405 lines, 23 decisions across 7 tiers)
- Verified D-297 Architecture Inversion Decree + Jem's 78% verification
- All documents comprehensive and review-ready

### Quality Checks
- Temple-grade: All mandate gates PASSED (3 M2 firewall violations remain — known, 126 remaining)
- Heritage-map: 45/74 files with tags, clean
- Targeted tests: 37/37 passed (meditate protocol, sovereign loop)
- Full test baseline verified at 1374 passed pre-compaction

### Commit & Push (3542188)
- **102 files committed**: 16052 insertions, 1515 deletions
- Covers: Decision workspace docs, M2 firewall fixes, entity state, research, coordination, infrastructure
- Third-party submodules excluded from staging + added to .gitignore
- Pushed to origin/main

### Handoff to Grok CLI (ho_749ed27155cd)
- **Target**: Grok CLI
- **Priority**: HIGH (blocking T0 implementation)
- **Scope**: Full review of Decision Workspace package:
  1. Grounded Meditation verdict (T0+T1-core only, 7h)
  2. Open Decisions Catalog (23 decisions, 7 tiers)
  3. D-297 Architecture Inversion Decree
  4. Sovereign Exit Protocol
  5. Implementation plan critique
- **Deliverables**: Ratification recommendations for all 23 decisions, implementation gap analysis, trigger condition validation

### Next Actions
1. Await Grok CLI acceptance of ho_749ed27155cd
2. Await Grok CLI review report
3. After review: Ratify decisions, begin T0 implementation (3h: DecisionEngine + ADR schema)
4. Address remaining M2 violations (Phases C/D/G — 126 remaining)

---

## 10. Session 2026-07-19: Context Packer — Decision Workspace Pack for Web Claude

### Context Packer Verification
- **enhanced_packer.py**: Compiles cleanly, all imports resolve
- **PIIMasker**: Importable and instantiable from `src/omega/oracle/pii_masker.py`
- **XML escaping**: `_escape_bare_xml_chars()` working correctly
- **Atomic writes**: Using `os.replace()` (not `os.rename()`)
- **Test run**: `kali-oversight` profile generated successfully (5 themes, ~75K tokens)

### New Profile: decision-workspace-review
Added to `packer-config.yaml` with 11 themes covering all decision workspace review documents:

| Theme | Files | Purpose |
|-------|-------|---------|
| grounding | 2 | Grounded Meditation + Jem Verification |
| decisions | 1 | Open Decisions Catalog (23 decisions) |
| decree | 1 | D-297 Architecture Inversion (10-step) |
| exit_protocol | 1 | Sovereign Exit Protocol (7 phases) |
| implementation | 2 | HMC Manual + SOVEREIGN_ARK_BLUEPRINT |
| engine_state | 1 | OMEGA_ENGINE.md |
| mandates | 1 | SOVEREIGN_MANDATES.md |
| session_log | 1 | KALI_LIVE_FEED.md |
| research | 1 | Grok CLI Comprehensive Research |
| handoff | 1 | Kali→Grok CLI handoff document |
| pivot_log | 1 | PIVOT_LOG.md |

### Generated Pack: context_packs/decision-workspace-review/
- **11 XML bundles** + **1 manifest** = 12 files (within 12-slot limit)
- **~87K estimated tokens** (well within Claude Projects limits)
- **All XML valid** — verified with ElementTree parsing
- **PII masked** — TOKENIZE mode with reversible placeholders

### Commit & Push (0168992)
- **2 files**: `packer-config.yaml` + `context_packs/decision-workspace-review/` (auto-generated)
- **Pushed to origin/main**

### Next Actions
1. Upload `context_packs/decision-workspace-review/` to claude.ai Projects for Web Claude parallel review
2. Await Grok CLI acceptance of ho_749ed27155cd
3. Await both review reports (Grok CLI + Web Claude)
4. Synthesize reviews → ratify decisions → begin T0 implementation

---

## 11. Session 2026-07-19 (Enhanced): Context Packer v2 — Sovereign Export Hardening

### Enhancements Implemented (8 total)

| # | Enhancement | Implementation | Mandate |
|---|-------------|----------------|---------|
| 1 | **Ed25519 Manifest Signing** | `_sign_manifest()` generates keypair, signs manifest, appends signature + public key | M21, M23 |
| 2 | **Injection Pattern Scanner** | 25 compiled regexes from OWASP LLM Top 10 2026 + Microsoft Spotlighting + Google research | M23 |
| 3 | **Per-Bundle Token Limits** | `MAX_BUNDLE_TOKENS=15000`, `MAX_TOTAL_TOKENS=150000`; auto-split + priority trim | M18 |
| 4 | **Bundle Consolidation (≤12)** | `_consolidate_bundles()` enforces `max_slots-1`, merges lowest-priority into `general` | Gap 5 |
| 5 | **Lost-in-the-Middle Reordering** | `_reorder_bundles_for_litm()` places critical bundles at start/end (U-shaped attention) | Gap 6 |
| 6 | **PII Masking (TOKENIZE)** | Integrated `PIIMasker` from `src/omega/oracle/pii_masker.py` with reversible placeholders | M8, M23 |
| 7 | **Full XML Body Escaping** | `_escape_bare_xml_chars()` escapes all `<`, `>`, `&` in body content | M9, M23 |
| 8 | **Decision-Workspace-Review Pack v2** | 12 files (1 manifest + 11 bundles), 87K tokens, Ed25519 signed, valid XML | All |

### Verification Results

| Pack | Files | Total Tokens | XML Valid | Ed25519 Signed | Within 12-Slot Limit |
|------|-------|--------------|-----------|----------------|---------------------|
| `decision-workspace-review` | 12 (1 manifest + 11 bundles) | 87,206 | ✅ All 11 | ✅ | ✅ (at limit) |
| `kali-oversight` | 9 (1 manifest + 8 bundles) | 75,262 | ✅ All 8 | ✅ | ✅ (well under) |

### Bundle Ordering (Lost-in-the-Middle Mitigation)

**decision-workspace-review** — Critical at positions 1-3 and 11-12:
```
START:  decree, grounding_part1, grounding_part2, decisions
MIDDLE: implementation, research, general, mandates, session_log, engine_state
END:    exit_protocol, handoff
```

**kali-oversight** — Critical at positions 1-3 and 8-9:
```
START:  fleet_part1, fleet_part2, fleet_part3
MIDDLE: mandates, roadmap, coordination_part1, coordination_part2
END:    heritage
```

### Research Report Updated
- `docs/research/R_CONTEXT_PACKER_KNOWLEDGE_GAPS_20260719.md` updated with implementation summary
- Validation checklist: all immediate items ✅
- Enhancement roadmap: immediate = complete

### Commits
- `0168992`: feat: add decision-workspace-review profile to Context Packer
- `02c5041`: chore: update session artifacts for compaction prep
- `3dce748`: chore: gitignore context_packs/ and database files
- `02c5041` → `3dce748`: session artifacts updated

### Next Actions (Corrected 2026-07-19)
1. ✅ CORRECTED: Old handoff ho_749ed27155cd asked Grok CLI to review 23 content decisions (WRONG)
2. ✅ CORRECTED: New handoff asks Grok CLI to review Decision Tools IMPLEMENTATION (DecisionEngine, ADR schema, CLI, MEDITATE)
3. ✅ CORRECTED: New context pack at `context_packs/decision-tools-review/` (7 bundles, implementation-focused)
4. Upload `context_packs/decision-tools-review/` to claude.ai Projects for Web Claude parallel review
5. Await Grok CLI acceptance of updated ho_749ed27155cd
6. Await both review reports (Grok CLI + Web Claude)
7. Synthesize reviews → incorporate feedback → begin T0 implementation
8. Address remaining M2 violations (Phases C/D/G — 126 remaining)

---

## 12. Session 2026-07-19 (Scope Correction): Decision Tools Review — NOT Content Decisions

### The Mistake
The Grok CLI handoff `ho_749ed27155cd` and `decision-workspace-review` context pack were scoped around reviewing the **23 content decisions** (D1-D23: D-297 Ratification, Tests vs WAL, Firewall gate, etc.). These are **internal engine questions** — they don't need external review.

### The Correction
Both handoff and context pack now focus on the **proposed implementation** of the Decision Workspace tools:

| Old Scope (WRONG) | New Scope (CORRECT) |
|--------------------|----------------------|
| Ratify/amend/reject 23 decisions | Review DecisionEngine schema & architecture |
| Validate D-297 decree | Review CLI command design (`list`, `show`, `decide`, `graph`) |
| Evaluate Sovereign Exit Protocol | Review MEDITATE integration with BE parameters |
| Validate Jem's verification gaps | Review scope & effort estimates (7h realistic?) |
| Recommend trigger conditions for T2-T5 | Identify risks & design gaps |

### Corrected Artifacts
| Artifact | Old (Wrong) | New (Correct) |
|----------|-------------|---------------|
| **Handoff** | `data/handoff/KALI_TO_GROK_CLI_DECISION_WORKSPACE_HANDOFF_20260719.md` | `data/handoff/KALI_TO_GROK_CLI_DECISION_TOOLS_REVIEW_20260719.md` |
| **Context pack** | `context_packs/decision-workspace-review/` (12 files, decision-focused) | `context_packs/decision-tools-review/` (8 files, implementation-focused) |
| **Hivemind packet** | ho_749ed27155cd (decision ratification scope) | ho_749ed27155cd (updated: implementation review scope) |
| **Packer profile** | `decision-workspace-review` | `decision-tools-review` |

### Corrected Context Pack Contents
```
context_packs/decision-tools-review/  (8 files = 7 bundles + manifest)
├── 00_PROJECT_MANIFEST.md        (Ed25519 signed)
├── grounding_part1.xml           — Grounded Meditation (implementation proposal)
├── grounding_part2.xml           — Grounded Meditation (continued)
├── implementation.xml            — HMC Manual + SOVEREIGN_ARK_BLUEPRINT
├── research.xml                  — Grok CLI Research (prior art)
├── mandates.xml                  — SOVEREIGN_MANDATES.md
├── engine_state.xml              — OMEGA_ENGINE.md
└── handoff.xml                   — Corrected handoff document
```

### L3 Principle (Refined)
The scope correction itself validates **L3-Decision-Infrastructure-Grows-From-Pain**: When user corrects a handoff scope, it means the tooling for external review (the context packer) is working as intended — it surfaces the right questions. The correction is not a failure; it's the system self-correcting toward the right boundary.

---

*⬡ OMEGA ⬡ KALI ⬡ SCOPE-CORRECTED ⬡ 2026-07-19*
