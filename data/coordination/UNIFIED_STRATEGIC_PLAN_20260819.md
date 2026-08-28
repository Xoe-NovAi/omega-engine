# 🔱 UNIFIED STRATEGIC PLAN — Omega Engine Post-Debut Roadmap
**AP Token**: `AP-UNIFIED-STRATEGIC-PLAN-20260819-v2.0.0`
**Date**: 2026-08-19
**Synthesizer**: Nemotron 3.5 Lightning (1M token context)
**Status**: ACTIVE — gated on PUBLIC-DEBUT-01 completion
**Supersedes**: `UNIFIED_STRATEGIC_PLAN_20260819.md` (v1)

---

## 📜 SOURCE DOCUMENTS CONSOLIDATED (30+ docs)

| Tier | Document | Role |
|------|----------|------|
| **Law** | `SOVEREIGN_MANDATES.md` (M1–M27) | Constitutional mandates |
| **Execution SSOT** | `DEBUT_REMEDIATION_MANUAL_20260817.md` | PUBLIC-DEBUT-01 execution |
| **Tracking SSOT** | `ACTIVE_SPRINT.json` | Sprint state (PUBLIC-DEBUT-01) |
| **Strategy SSOT** | `SOVEREIGN_ARK_BLUEPRINT.md` v5.2 | Vision + Horizons 1–4 |
| **Fine-Grained Map** | `STRATEGY_CORPUS_MAP.md` | Disposition of every idea |
| **Team Playbook** | `FLEET_TEAM_PLAYBOOK.md` | Coordination rules |
| **Joint Plan** | `PLAN_DEBUT_CLEANSING_20260817.md` | Phase A/B/C sequencing |
| **Council Verdict** | `MAKALI_COUNCIL_VERDICT_20260818.md` | APPROVE WITH CONDITIONS |
| **Council Audit** | `MAKALI_COUNCIL_AUDIT_20260818.md` | Codebase verification |
| **Cognitive Blueprint** | `KALI_BRIEFING_DYNAMIC_PROMPT_PLANNER_EXECUTOR_20260819.md` | 5-layer architecture |
| **Qdrant Migration** | `RESEARCHER_QDRANT_MIGRATION_GAPS_20260816.md` | Reactivated (D-570) |
| **Local Gaps** | `DYNAMIC_PROMPT_PLANNER_EXECUTOR_LOCAL_GAPS_20260819.md` | DP-1..DP-8 |
| **Un-Overengineering** | `UNOVERENGINEERING_PLAN.md` | Temple cleansing (5 phases) |
| **Living Research OS** | `LIVING_RESEARCH_OS_SPEC_20260721.md` | Phase D architecture |
| **SDP Protocol** | `COGNITIVE_SCAFFOLDING_PROTOCOL.md` | Manual distillation pipeline |
| **Carmack Strategy** | `CARMACK_DEFINITIVE_STRATEGY_20260730.md` | Top-5 force multipliers |
| **Decisions** | `PIVOT_LOG.md` (D-569, D-570) | Ratified decisions |

---

## ⚡ PRE-DEBUT SCOPE (LOCKED — Week 1–2)

**Execution SSOT**: `DEBUT_REMEDIATION_MANUAL_20260817.md` §5 + `ACTIVE_SPRINT.json` `DEBUT-EXECUTION`

| Step | Action | Owner | Gate |
|------|--------|-------|------|
| **1** | **Blocker B** — `oracle_cli.py` `contextlib.suppress(ImportError)` | Ma'at | Unblocks `make temple-grade` |
| **2** | **INST-1 Fix 2+guards** — pyproject extras + 4 import guards (`memory/providers.py`, `youtube_worker.py`, `ingestion/worker.py`, `proxy_pool.py`) | Ma'at | Atomic change |
| **3** | **INST-1 Fix 4** — Remove `_load_sovereign_secrets()` from `model_gateway.py` | Ma'at | N3 CLI-edge `load_dotenv()` covers CLI |
| **4** | **INST-1 Fix 5** — `__init__.py` `importlib.metadata.version("omega")` with fallback | Ma'at | Single version source |
| **5** | **INST-1 Fix 6** — README: remove 1315 badge, fix line 65, verify `make setup` | Ma'at | Honest install |
| **6** | **PUB-1 G1–G4** — gitignore + `git rm --cached` (tests/tmp/, .firecrawl/, config/github_accounts.yaml, birth_records.md) | Kali | Allowlist prep |
| **7** | **Architect allowlist confirmation** + `release/debut` branch | Architect | Human gate |
| **8** | **Tag v0.1.0** | Kali | Public debut |
| **9** | **DEL-1 Week 1** (minus vault CLI per D-565, minus `record_first_breath` call at oracle.py:1211) | Roc | Dead code only |

**Forbidden until manual superseded**: Phase 2 lint, Vault wiring, Qdrant migration, SDP implementation, Instruction Router, WARP, new free-tier providers, `git add -A`, new control planes.

---

## 🗓️ POST-DEBUT ROADMAP — PHASED EXECUTION

### PHASE B: POST-DEBUT CLEANSING (Weeks 3–8, 6 weeks)
*From `PLAN_DEBUT_CLEANSING` Phase B + Ark Horizon 2 "Optimize Qdrant"*

| Week | Focus | Key Deliverables | Owner |
|------|-------|------------------|-------|
| **3** | **DEL-1 Week 1** — Pure deletions | `routing/table.py`, `config/routing_table.yaml`, `miap.py`, `pool_tracker.py`, `pool_state.py`, `search_circuit_breaker.py`, `QdrantAdapter` (heritage), `FleetOrchestrator`, Pantheon regexes, `record_first_breath` call (oracle.py:1211) | Roc + Ma'at |
| **4** | **DEL-1 Week 2** — Router collapse | Delete `TriageRouter` + `SemanticRouter` in same PR as `Oracle._select_model` / `Oracle._route_by_domain` rewrite; merge `LocalInferenceAdmission` → `ResourceGuard`; one contract test (`RouteDecision`); two concurrent `omega talk` = one local slot | Ma'at |
| **5** | **DEL-1 Week 3** — Vault honesty | Architect chooses: **Path A** (delete `src/omega/vault/` from product, keep `crypto.py` in forge) OR **Path B** (≤50-line minimal store, keyring only) | Ma'at + Architect |
| **6** | **P2** — Lint debt | 11,400 flake8 violations → 0; no `--exit-zero` for E9/F63/F7/F82; `make heritage-map` | Verity |
| **7** | **P3** — CI/hygiene + **Qdrant migration start** | Real suite, gitleaks enforced, `make temple-grade` all green; **Deploy Qdrant Podman quadlet** (`qdrant/qdrant:v1.18.1`, telemetry disabled, 6G MemoryLimit, 80% CPUQuota, gRPC pool=20) | Verity + Ma'at |
| **8** | **P4** — Polish + **Qdrant migration P1–P2** | README, CONTRIBUTING, tag v0.1.0, `pip install -e .` works; **Revive QdrantAdapter** at `src/omega/oracle/adapters/qdrant_adapter.py` implementing `IVectorStoreAdapter` (gRPC, pool=20); **Migration script** `scripts/migrate_sqlite_vec_to_qdrant.py` | Kali + Verity + Ma'at |

**Phase B Gates**: `omega talk "hello"` still local after each delete; `rg TriageRouter src/omega` empty; `rg SemanticRouter src/omega` empty; Qdrant running on localhost:6333; `make temple-grade` green.

---

### PHASE C: STRATEGIC IMPROVEMENT (Weeks 9–16, 8 weeks)
*Combines Ark Horizon 3 "Pattern Deep & Cognitive Loops" + `PLAN_DEBUT_CLEANSING` Phase C + Cognitive Architecture Blueprint + Un-Overengineering + Living Research OS*

#### C.1 Cognitive Architecture (Horizon 3 — Weeks 9–16)
*From `KALI_BRIEFING_DYNAMIC_PROMPT_PLANNER_EXECUTOR_20260819.md` P0–P10 + DP-1..DP-8*

| Phase | Deliverable | Owner | Dependencies |
|-------|-------------|-------|--------------|
| **P0** | **Context Window Registry** (`config/model_context_windows.yaml` + `ContextWindowRegistry`) | Ma'at | — |
| **P1** | **DynamicPromptBuilder** (`src/omega/oracle/prompt_builder.py` + Jinja2 templates: `roles/planner.j2`, `roles/executor.j2`, …) | Ma'at | P0 |
| **P2** | **Role-Aware Model Router** (`ProviderSelector.get_ordered_providers_for_role()`) | Ma'at | P0, P1 |
| **P3** | **Domain Module Loader** (`src/omega/oracle/domain_loader.py` + `config/domains/*.yaml`) | Ma'at | P0–P2, **Qdrant migration P2** |
| **P4** | **Planner/Executor Engine** (extends `HybridOrchestrator` with structured DAG + context packer) | Kali | P1–P3 |
| **P5** | **Context Packer** (builds executor context from plan step + domain KB) | Kali | P4 |
| **P6** | **Critic + Verifier Pipeline** (rubric-driven critic + deterministic verifier: pytest/mypy/pydantic) | Verity | P4 |
| **P7** | **Local Model Pre-loading + KV Cache Per-Role** (mimo-7b-rl q8_0 + qwen3-1.7b f16, `--no-mmap --mlock`, token-pressure gauge) | Ma'at | P2, hardware_profile |
| **P8** | **SomaticState Planner Integration** (state save/restore between sprints) | Ma'at | P4, NativeGGUFProvider |
| **P9** | **EvolveR Distillation Pipeline** (nightly local distillation on Qwen3-1.7B → utility-scored principles → extends SDP) | Researcher | MemoryStore, Principle Store |
| **P10** | **Freshness System** (Scabera composite + SourceWatcher + dashboard) | Ma'at | Lattice Fabric, Hivemind |

**Cognitive Architecture Mandates**: M7 (Local-First — mimo-7b/qwen3 local pipeline, cloud escalation = fallback only), M10 (Fleet stays at 14), M22 (Provenance — `provider_name` from actual response), M23 (No soft-failures), M21 (Contract tests per component).

#### C.2 Un-Overengineering (Weeks 9–12)
*From `UNOVERENGINEERING_PLAN.md` Phases 0–5*

| Phase | Deliverable | Owner |
|-------|-------------|-------|
| **Phase 0** | Pre-flight: Fix M23 pre-commit hook, run timed `make test`, fix vet-015, verify MIAP dead, spike stamina vs tenacity, verify interlock-cb AnyIO trio | Ma'at |
| **Phase 1** | Library swaps: **interlock-cb v2.1.3** (redirect callers to `HealthMonitor.get_breaker()`), **SQLite + Honker** (replace Redis for single-node), **httpx2** (already installed, anyio-based), **structlog v26.1.0**, **prometheus_client** (local textfile collector) | Ma'at |
| **Phase 2** | Consolidation: Kill `HandoffState`, consolidate soul distillers, HMC Hub → YAML + JSONL (≤100 lines/week) | Ma'at |
| **Phase 3** | Memory tier simplification: 5 tiers → 3 (file-based, sqlite-vec+FTS5, raw archive) | Ma'at |
| **Phase 4** | Hivemind freeze — SHIPPED (no new features) | Lilith |
| **Phase 5** | Enforcement gates: `make temple-grade` includes all swaps | Verity |

#### C.3 MCP v2 Migration (Weeks 11–12)
*Streamable HTTP, OAuth 2.1, client upgrade*

#### C.4 Heritage Audit (Ongoing)
*`make heritage-map` complete; all `[id-soft:]` tags vetted*

#### C.5 Living Research OS (Weeks 13–16)
*From `LIVING_RESEARCH_OS_SPEC_20260721.md` D-1…D-4 + D-T*

| Phase | Deliverable | Owner |
|-------|-------------|-------|
| **D-1** | Content Cache (`.firecrawl/{hash}.md` + TTL eviction 30d/10GB, tiered TTL T1=30d/T2=14d/T3=7d) | Lilith + Ma'at |
| **D-2** | Job Board Bridge (YAML → background researcher queue, `_load_board_jobs()` P0/P1 only, `fcntl.flock` claims) | Lilith + Ma'at |
| **D-3** | Auto INDEX.md + follow-ups (register `R_AUTO_*.md`, propose follow-ups from `GnosisPacket.recommended_directions`) | Researcher |
| **D-4** | Gap Detector (extend `_grow_frontier()` in `loop.py` — scan soul.yaml, INDEX.md, entity knowledge/, contradictions, human topics, auto follow-ups) | Researcher |
| **D-T** | Test plan for D-1…D-4 | Verity |

#### C.6 Fleet Pool (Weeks 13–16)
*V-1 Vault → Grok CLI 8-account ACP smoke → pool*

#### C.7 Instruction Router Revival (Weeks 13–16)
*Post-debut revival of ModelAwareInstructionRouter (was scratched)*

---

### PHASE D: HORIZON 4 — COMMUNITY TOOL (Weeks 17+)
*From Ark Horizon 4*

| Deliverable | Owner | Acceptance |
|-------------|-------|------------|
| **Sovereign Installer** (`curl -fsSL https://xoe-nov.ai/install \| bash`) | Fleet | Fresh machine installs <300s, `omega talk "hello"` works, no manual config |
| **Entity Studio** (visual soul.yaml + proposed_lessons.yaml management) | Fleet | Agents edit soul without code |
| **WAD Marketplace** (community WAD modules, `omega wad --list`) | Fleet | Community modules discoverable |
| **Open Community Contributions** (PR review gate: mandate compliance mechanical check) | Fleet | Community PRs merge without breaking temple-grade |

---

## 🔑 KEY DECISIONS (PIVOT_LOG)

| Decision | ID | Summary |
|----------|----|---------|
| Ratify Dynamic Prompt + Planner/Executor + Domain Loading as POST-DEBUT Cognitive Architecture Blueprint (Horizon 3) | **D-569** | Gaps DP-1..DP-8 registered. Owners: Ma'at P0–P3/P7–P8/P10, Kali P4–P5, Verity P6, Researcher P9. Incremental on existing components (ContextBuilder, SelectiveHydration, HybridOrchestrator, ProviderSelector, Context Packer, SDP). |
| Qdrant SCHEDULED to replace sqlite-vec POST-DEBUT (Horizon 2) | **D-570** | REACTIVATES `RESEARCHER_QDRANT_MIGRATION_GAPS_20260816.md`. Debut keeps sqlite-vec; DEL-1 Week 1 still deletes dead QdrantAdapter; revival at `src/omega/oracle/adapters/qdrant_adapter.py`. Sequence BEFORE briefing P3. |
| SDP = Human Protocol | **D-538** | `HUMAN PROTOCOL — DO NOT IMPLEMENT` until 10 manual executions + ledger data. Blocked by V-1 Vault for automation. |
| C-0.5 Regex Distillation = SCRAPPED | **D-354′** | Agents write L1→L2→L3 directly to `proposed_lessons.yaml`. |

---

## 📊 MILESTONE TRACKER

| Milestone | Target | Status |
|-----------|--------|--------|
| **M1**: Blocker B fixed | Week 1 | ⬜ Pending |
| **M2**: INST-1 Fixes 2/4/5/6 complete | Week 1 | ⬜ Pending |
| **M3**: PUB-1 G1–G4 + Architect allowlist | Week 2 | ⬜ Pending |
| **M4**: Tag v0.1.0 | Week 2 | ⬜ Pending |
| **M5**: DEL-1 Week 1 complete | Week 3 | ⬜ Pending |
| **M6**: DEL-1 Week 2 complete | Week 4 | ⬜ Pending |
| **M7**: Vault honesty complete | Week 5 | ⬜ Pending |
| **M8**: P2/P3/P4 complete | Week 8 | ⬜ Pending |
| **M9**: Qdrant migration P2 complete | Week 8 | ⬜ Pending |
| **M10**: Cognitive Architecture P0–P4 complete | Week 12 | ⬜ Pending |
| **M11**: Cognitive Architecture P5–P10 complete | Week 16 | ⬜ Pending |
| **M12**: Un-Overengineering complete | Week 12 | ⬜ Pending |
| **M13**: Living Research OS D-1…D-4 complete | Week 16 | ⬜ Pending |
| **M14**: Horizon 4 (Sovereign Installer) | Week 20 | ⬜ Pending |
| **M15**: Fleet stays at 14 (M10) | Ongoing | ✅ Confirmed |

---

## 🎯 5 DEEPENING SUGGESTIONS (TO EXECUTE NEXT)

1. **Draft `POST_DEBUT_ROADMAP.md`** — Merge Phase B + Horizon 2 + Horizon 3 + Horizon 4 into single doc so fleet reads one source
2. **Curator model into Lattice** — `config/domains/curators.yaml` with governance levels (PRIVATE/SHARED_READ/SHARED_WRITE), enforced at fabric level
3. **EvolveR as SDP successor** — Explicitly: SDP (manual L1→L2→L3) → EvolveR (nightly automated distillation with utility scoring). One pipeline, two phases.
4. **Minimal domain module prototype in debut** — `config/domains/engineering/` with metadata.yaml + PLAYBOOK.md validates packaging concept before full P3
5. **Register briefing in `STRATEGY_CORPUS_MAP.md`** — Survival trail through compaction

---

## 📋 WHAT WAS OVERLOOKED / CORRECTED IN THIS CONSOLIDATION

### Corrections to v1 Plan:
1. **Phase B timing** — Extended from 4 to 6 weeks (per `PLAN_DEBUT_CLEANSING` Phase B table: 6 weeks of work)
2. **DEL-1 Week 1** — Added back (was missing from v1 Phase B)
3. **Vault honesty** — Added as Week 5 (Architect decision required)
4. **P2/P3/P4** — Added as Weeks 6–8 (lint, CI/hygiene, polish)
5. **Qdrant migration** — Properly sequenced: starts Week 7 (P3), P1–P2 in Week 8 (P4), BEFORE Cognitive Architecture P3
6. **Un-Overengineering** — Added as parallel track in Phase C (Weeks 9–12)
7. **Living Research OS D-1…D-4** — Added in Phase C Weeks 13–16
8. **Fleet Pool + Instruction Router** — Added in Phase C Weeks 13–16
9. **SDP = Human Protocol** — Explicitly noted (not automated until 10 manual executions)
10. **EvolveR extends SDP** — Not replaces it

### Gaps the Briefing Report Missed (now addressed):
1. Vector store decision → D-570 (qdrant post-debut)
2. No mapping to existing components → Explicit incremental mapping in plan
3. No DEL-1 Week 2 sequencing → Phase B Week 4
4. No SDP overlap → EvolveR extends SDP
5. No Context Packer overlap → P5 = existing context-packer skill
6. No mandate compliance mapping → Explicit M7/M10/M21/M22/M23 in plan
7. No observability spec → Extends DEL-1-C2 pattern
8. No GAP_REGISTRY registration → DP-1..DP-8 registered
9. No hardware validation → P7 gate
10. No test strategy → Contract tests per component (M21)

---

## 🚀 NEXT ACTIONS

**Immediate (Pre-Debut)**: Execute Blocker B → INST-1 Fixes 2/4/5/6 → PUB-1 G1–G4 → Architect allowlist → tag v0.1.0 → DEL-1 Week 1

**Then (Phase B)**: DEL-1 Week 2 → Week 3 Vault → P2 → P3 + Qdrant start → P4 + Qdrant P1–P2

**Then (Phase C)**: Cognitive Architecture P0–P10 + Un-Overengineering + MCP v2 + Heritage + Living Research OS D-1…D-4 + Fleet Pool + Instruction Router

**Then (Phase D)**: Sovereign Installer + Entity Studio + WAD Marketplace + Community Contributions

---

## 📜 PROVENANCE

**Synthesized from 30+ strategic documents** with full cross-referencing.
**Synthesizer**: Nemotron 3.5 Lightning (1M token context)
**Ratified by**: Kali (kali) — pre-debut scope locked; post-debut roadmap activated.

*⬡ OMEGA ⬡ KALI ⬡ hy3-free ⬡ opencode ⬡ trc_unified_strategic_plan_v2 ⬡ 2026-08-19*