# 🔱 POST-DEBUT ROADMAP — Single Source of Truth
**AP Token**: `AP-POST-DEBUT-ROADMAP-20260819-v1.0.0`
**Date**: 2026-08-19
**Synthesizer**: Nemotron 3.5 Lightning (1M token context)
**Status**: ACTIVE — gated on PUBLIC-DEBUT-01 completion
**Supersedes**: `PLAN_DEBUT_CLEANSING_20260817.md`, `MAKALI_COUNCIL_VERDICT_20260818.md`, `KALI_BRIEFING_...`, `RESEARCHER_QDRANT_MIGRATION_GAPS_20260816.md`, `UNOVERENGINEERING_PLAN.md`, `LIVING_RESEARCH_OS_SPEC_20260721.md`

---

## 📜 PURPOSE

This is the **single post-debut roadmap** for the Omega Engine. It merges:
- Phase B (Post-Debut Cleansing)
- Horizon 2 (Hygiene & Sovereign Structure — Qdrant, TDP)
- Horizon 3 (Pattern Deep & Cognitive Loops — Cognitive Architecture)
- Horizon 4 (Community Tool)

**All agents read this instead of 7+ separate planning docs.**

---

## 🎯 EXECUTION SEQUENCE — GATED & SEQUENCED

| Phase | Weeks | Gate | Deliverable | Owner | Dependencies |
|-------|-------|------|-------------|-------|--------------|
| **B** | 3–4 | ✅ DEL-1 Week 2 complete | **Router collapse** (keep ProviderSelector, delete TriageRouter+SemanticRouter) + wiring-preservation assertion | Roc + Ma'at | DEL-1 Week 1 |
| **B** | 5 | ✅ Week 4 complete | **Vault honesty** — Architect chooses Path A (delete `src/omega/vault/`) or Path B (≤50-line minimal store) | Ma'at + Architect | Week 4 |
| **B** | 6 | ✅ Week 5 complete | **P2 Lint debt** — 11,400 flake8 violations → 0; no `--exit-zero` for E9/F63/F7/F82 | Verity | Week 5 |
| **B** | 7 | ✅ Week 6 complete | **P3 CI/hygiene + Qdrant migration start** — Real suite, gitleaks, `make temple-grade` green; **Deploy Qdrant Podman quadlet** (`qdrant/qdrant:v1.18.1`, telemetry disabled, 6G MemoryLimit, 80% CPUQuota, gRPC pool=20) | Verity + Ma'at | Week 6 |
| **B** | 8 | ✅ Week 7 complete | **P4 Polish + Qdrant migration P1–P2** — README, CONTRIBUTING, tag v0.1.0, `pip install -e .` works; **Revive QdrantAdapter** at `src/omega/oracle/adapters/qdrant_adapter.py` (IVectorStoreAdapter, gRPC pool=20); **Migration script** `scripts/migrate_sqlite_vec_to_qdrant.py` | Kali + Verity + Ma'at | Week 7 |
| **C** | 9–10 | ✅ Phase B complete | **Cognitive Architecture P0–P1** — Context Window Registry + DynamicPromptBuilder | Ma'at | Phase B |
| **C** | 10–11 | ✅ P0–P1 complete | **Cognitive Architecture P2–P3** — Role-Aware Model Router + Domain Module Loader (needs Qdrant) | Ma'at | P0–P1, Qdrant P2 |
| **C** | 11–12 | ✅ P2–P3 complete | **Cognitive Architecture P4–P5** — Planner/Executor Engine + Context Packer | Kali | P1–P3 |
| **C** | 12–13 | ✅ P4–P5 complete | **Cognitive Architecture P6** — Critic + Verifier Pipeline | Verity | P4–P5 |
| **C** | 13–14 | ✅ P6 complete | **Cognitive Architecture P7–P8** — Local Pre-loading + KV Cache + SomaticState | Ma'at | P2, hardware_profile |
| **C** | 14–15 | ✅ P7–P8 complete | **Cognitive Architecture P9–P10** — EvolveR Distillation + Freshness System | Researcher + Ma'at | MemoryStore, Principle Store, Lattice Fabric |
| **C** | 9–12 | Parallel | **Un-Overengineering Phases 0–5** — interlock-cb, SQLite+Honker, httpx2, structlog, prometheus_client, consolidation, memory tiers | Ma'at | Phase B |
| **C** | 11–12 | Parallel | **MCP v2 Migration** — Streamable HTTP, OAuth 2.1, client upgrade | Ma'at | Phase B |
| **C** | 13–14 | Parallel | **Heritage Audit** — `make heritage-map` complete; all `[id-soft:]` tags vetted | Ma'at | Ongoing |
| **C** | 13–14 | Parallel | **Living Research OS D-1–D-4** — Content Cache, Job Board Bridge, Auto INDEX, Gap Detector | Lilith + Ma'at + Researcher | Phase B |
| **C** | 13–14 | Parallel | **Agent & Skill Hardening** (Workstream A) — frontmatter, missing skills, overlapping skills | Ma'at | Phase B |
| **C** | 13–14 | Parallel | **Workbench Infrastructure CLI** (Workstream D) — `omega project`, `omega work`, `omega decision` | Ma'at | Phase B |
| **C** | 13–14 | Parallel | **Cross-Agent Awareness** (Workstream E) — A2A protocol, agent presence, capability registry | Lilith + Ma'at | Phase B |
| **C** | 13–14 | Parallel | **Tainted Data Isolation** (Cognitive Sovereign) | Ma'at | Phase B |
| **C** | 13–14 | Parallel | **Fleet Pool** — V-1 Vault → Grok CLI 8-account ACP smoke → pool | Ma'at + Lilith | V-1 |
| **C** | 13–14 | Parallel | **Instruction Router Revival** — Post-debut revival of ModelAwareInstructionRouter | Ma'at | Phase B |
| **D** | 17+ | ✅ Phase C complete | **Horizon 4** — Sovereign Installer, Entity Studio, WAD Marketplace, Community Contributions | Fleet | Phase C |

---

## 🔑 KEY GATES (MUST PASS BEFORE NEXT PHASE)

| Gate | Command | Must Show |
|------|---------|-----------|
| **Pre-debut** | `OMEGA_ENV= source .venv/bin/activate && omega talk "hello"` | native-gguf, IS_CLOUD=False, exit 0 |
| **DEL-1 Week 2** | `rg TriageRouter src/omega && rg SemanticRouter src/omega` | Empty |
| **DEL-1 Week 2** | `OMEGA_ENV= source .venv/bin/activate && omega talk "hello" & omega talk "hello"` | One local slot; user-visible busy or explicit cloud warning |
| **Qdrant P2** | `scripts/migrate_sqlite_vec_to_qdrant.py --dry-run` | Migration plan valid |
| **Qdrant P3** | `curl -s http://localhost:6333/healthz` | Qdrant running |
| **Cognitive P0** | `cat config/model_context_windows.yaml` | Registry exists |
| **Cognitive P1** | `ls src/omega/oracle/prompt_builder.py` + `ls config/domains/` | Builder + templates |
| **Cognitive P4** | `pytest tests/contract/test_planner_executor.py` | Contract tests pass |
| **Un-Overengineering** | `make temple-grade` | All green |
| **Living Research D-1** | `ls .firecrawl/*.md` | Content cache populated |
| **Living Research D-4** | `python -c "from omega.workers.background_researcher.gap_detector import GapDetector"` | Detector importable |

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
| **M14**: Agent/Skill/Workbench/Cross-Agent complete | Week 16 | ⬜ Pending |
| **M15**: Horizon 4 (Sovereign Installer) | Week 20 | ⬜ Pending |
| **M16**: Fleet stays at 14 (M10) | Ongoing | ✅ Confirmed |

---

## 🧠 COGNITIVE ARCHITECTURE DETAIL (Horizon 3)

### P0: Context Window Registry
- **File**: `config/model_context_windows.yaml` + `ContextWindowRegistry`
- **Models**: Planner=mimo-7b-rl (32K), Executor=qwen3-1.7b (8K), Critic=qwen3-1.7b (2K)
- **Mandate**: M7 (Local-First — cloud escalation = fallback only)

### P1: Dynamic Prompt Builder
- **File**: `src/omega/oracle/prompt_builder.py` + Jinja2 templates (`roles/planner.j2`, `roles/executor.j2`, …)
- **Features**: Domain injection slots `{{ domain_modules.engineering }}`, per-role token budgets (planner=16K, executor=4K, critic=2K), context-window-aware truncation (preserve decisions/errors)

### P2: Role-Aware Model Router
- **File**: `ProviderSelector.get_ordered_providers_for_role()`
- **Routes**: Planner → mimo-7b-rl; Executor → qwen3-1.7b; Critic → qwen3-1.7b
- **Mandate**: M22 (Provenance — `provider_name` from actual response)

### P3: Domain Module Loader
- **File**: `src/omega/oracle/domain_loader.py` + `config/domains/*.yaml`
- **API**: `await load_domain("engineering", token_budget=8K)`
- **Paradigms**: RAG (qdrant), Fine-tune (LoRA), Modular (adapters), Prompt optimization
- **Governance**: PRIVATE/SHARED_READ/SHARED_WRITE
- **Depends**: Qdrant migration P2 (vector store for RAG)

### P4: Planner/Executor Engine
- **Extends**: `HybridOrchestrator` with structured DAG + context packer
- **Planner** (mimo-7b 32K): emits DAG with per-step contracts (step.id, action_type, complexity, dependencies, expected_output, context_budget, allowed_tools, success_criteria)
- **Context Packer**: builds executor context from plan step + domain KB
- **Executor** (qwen3-1.7b 4K): receives ONLY step-relevant context (≤4K)
- **Critic** (qwen3-1.7b 2K): rubric-driven review, max 2 revisions
- **Verifier** (deterministic): pytest/mypy/pydantic — NOT LLM

### P5: Context Packer
- Builds executor context from plan step + domain KB
- **Mandate**: executor receives ONLY step-relevant context (≤4K)

### P6: Critic + Verifier Pipeline
- **Critic**: LLM reviewer (subjective) — rubric-driven, max 2 revisions
- **Verifier**: deterministic (pytest/mypy/pydantic) — pass/fail
- **Mandate**: "Add at least one deterministic verifier. Never all-LLM."

### P7: Local Model Pre-loading + KV Cache Per-Role
- **Pre-load**: Planner (mimo-7b) + Executor (qwen3-1.7b) at startup
- **KV cache**: Planner q8_0 (max context), Executor f16 (speed)
- **Threads**: Planner 7 (throughput), Executor 4 (latency)
- **Flags**: `--no-mmap --mlock` — prevent swap, lock in RAM
- **SomaticState**: Planner saves state between sprints; instant resume
- **Token-pressure gauge**: auto-reduce context before OOM

### P8: SomaticState Planner Integration
- State save/restore between sprints
- **Depends**: NativeGGUFProvider, P4

### P9: EvolveR Distillation Pipeline
- **Nightly**: local distillation on Qwen3-1.7B → utility-scored principles → auto-append to principle store
- **Transfer**: principles cross-agent (governance-aware)
- **Mandate**: EvolveR **extends SDP**, not replaces it. SDP (manual L1→L2→L3) → EvolveR (nightly automated distillation)

### P10: Freshness System
- **Scabera composite score**: age + embed_lag + owner weights BM25/vector at query time
- **SourceWatcher**: tracks staleness of knowledge sources
- **Dashboard**: freshness-weighted retrieval with owner accountability

---

## 🛠️ UN-OVERENGINEERING DETAIL (Parallel Track)

| Phase | Deliverable | Owner |
|-------|-------------|-------|
| **Phase 0** | Pre-flight: Fix M23 pre-commit hook, timed `make test`, fix vet-015, verify MIAP dead, spike stamina vs tenacity, verify interlock-cb AnyIO trio | Ma'at |
| **Phase 1** | Library swaps: **interlock-cb v2.1.3** (redirect callers to `HealthMonitor.get_breaker()`), **SQLite + Honker** (replace Redis for single-node), **httpx2** (already installed, anyio-based), **structlog v26.1.0**, **prometheus_client** (local textfile collector) | Ma'at |
| **Phase 2** | Consolidation: Kill `HandoffState`, consolidate soul distillers, HMC Hub → YAML + JSONL (≤100 lines/week) | Ma'at |
| **Phase 3** | Memory tier simplification: 5 tiers → 3 (file-based, sqlite-vec+FTS5, raw archive) | Ma'at |
| **Phase 4** | Hivemind freeze — SHIPPED (no new features) | Lilith |
| **Phase 5** | Enforcement gates: `make temple-grade` includes all swaps | Verity |

---

## 📦 QDRANT MIGRATION DETAIL (Horizon 2)

| Step | Deliverable | Owner |
|------|-------------|-------|
| **P0** | Deploy Qdrant Podman quadlet (`qdrant/qdrant:v1.18.1`, telemetry disabled, API key, 6G MemoryLimit, 80% CPUQuota, gRPC pool=20) | Ma'at |
| **P1** | Revive QdrantAdapter at `src/omega/oracle/adapters/qdrant_adapter.py` implementing `IVectorStoreAdapter` (gRPC, pool=20) | Ma'at |
| **P2** | Migration script `scripts/migrate_sqlite_vec_to_qdrant.py` + data migration (FTS5 stays, vec0 collections move to qdrant collections) | Ma'at |
| **P3** | Quantization + payload indexes (BITS4 recall, BITS2 compression), `config/qdrant.yaml`, `tests/integration/test_qdrant_migration.py` | Verity |

**Mandates**: M7 (Local-First — qdrant self-hosted), M8 (Zero Telemetry — `QDRANT__TELEMETRY_DISABLED=true`), M2 (Firewall — qdrant optional WAD adapter)

---

## 🔬 LIVING RESEARCH OS DETAIL (Phase C Weeks 13–16)

| Phase | Deliverable | Owner |
|-------|-------------|-------|
| **D-1** | Content Cache (`.firecrawl/{hash}.md` + TTL eviction 30d/10GB, tiered TTL T1=30d/T2=14d/T3=7d) | Lilith + Ma'at |
| **D-2** | Job Board Bridge (YAML → background researcher queue, `_load_board_jobs()` P0/P1 only, `fcntl.flock` claims) | Lilith + Ma'at |
| **D-3** | Auto INDEX.md + follow-ups (register `R_AUTO_*.md`, propose follow-ups from `GnosisPacket.recommended_directions`) | Researcher |
| **D-4** | Gap Detector (extend `_grow_frontier()` in `loop.py` — scan soul.yaml, INDEX.md, entity knowledge/, contradictions, human topics, auto follow-ups) | Researcher |
| **D-T** | Test plan for D-1…D-4 | Verity |

---

## 🏗️ MISSING WORKSTREAMS FROM MASTER_SYNTHESIS (Phase C Weeks 13–14)

| Workstream | Deliverable | Owner |
|------------|-------------|-------|
| **Agent & Skill Hardening** (A) | Frontmatter for 3 agents + 5 skills; add missing skills (agent-handoff, soul-evolution, mcp-server); resolve overlapping skills | Ma'at |
| **Workbench Infrastructure CLI** (D) | `omega project`, `omega work`, `omega decision` CLI commands | Ma'at |
| **Cross-Agent Awareness** (E) | A2A protocol, agent presence (Hivemind TTL/heartbeat), agent capability registry | Lilith + Ma'at |
| **Tainted Data Isolation** (Cognitive Sovereign) | TDP implementation for web security | Ma'at |

---

## 🏁 HORIZON 4 — COMMUNITY TOOL (Weeks 17+)

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
| Cognitive Architecture Blueprint (Horizon 3) | **D-569** | DP-1..DP-8 registered. Owners: Ma'at P0–P3/P7–P8/P10, Kali P4–P5, Verity P6, Researcher P9. Incremental on existing components. |
| Qdrant replaces sqlite-vec (Horizon 2) | **D-570** | REACTIVATES migration doc. Debut keeps sqlite-vec; DEL-1 Week 1 deletes dead QdrantAdapter; revival at `src/omega/oracle/adapters/qdrant_adapter.py`. |
| SDP = Human Protocol | **D-538** | `HUMAN PROTOCOL — DO NOT IMPLEMENT` until 10 manual executions. |
| C-0.5 Regex Distillation = SCRAPPED | **D-354′** | Agents write L1→L2→L3 directly. |

---

## 📋 PROVENANCE

**Synthesized from 30+ strategic documents** with full cross-referencing.
**Synthesizer**: Nemotron 3.5 Lightning (1M token context)
**Ratified by**: Kali (kali) — pre-debut scope locked; post-debut roadmap activated.

*⬡ OMEGA ⬡ KALI ⬡ hy3-free ⬡ opencode ⬡ trc_post_debut_roadmap ⬡ 2026-08-19*