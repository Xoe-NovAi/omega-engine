# 🔱 CANONICAL ROADMAP — Omega Engine Single Source of Truth
**AP Token**: `AP-CANONICAL-ROADMAP-20260829-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ jem-2.0 ⬡ opencode ⬡ trc_canonical_roadmap ⬡ ACTIVE

**Date**: 2026-08-29
**Status**: CANONICAL — This document supersedes all prior roadmaps
**Authority**: Derived from `DEBUT_REMEDIATION_MANUAL_20260817.md` + `ACTIVE_SPRINT.json` + `POST_DEBUT_ROADMAP.md` + `SOVEREIGN_ARK_BLUEPRINT.md` + `STRATEGY_CORPUS_MAP.md` + `DECISION_LEDGER.md` + `CLINE_STRATEGIC_STATE_SYNTHESIS_20260828.md` + `CLINE_FULL_REVIEW_ROLLUP_20260828.md`

---

## 📋 EXECUTIVE SUMMARY

This roadmap consolidates **141 strategy docs + 623 coordination docs + 609 research reports** into a single executable plan. It has three phases:

| Phase | Name | Status | Gate |
|-------|------|--------|------|
| **PRE-DEBUT** | PUBLIC-DEBUT-01 | 🔴 **IN PROGRESS — 4 P0s RED** | P0-1→PUB-1→INST-1→DEL-1→DOC-1 |
| **POST-DEBUT** | Phase B + Horizons 2–4 | ⏳ GATED ON DEBUT | Phase B complete → Cognitive P0–P10 |
| **LONG-ARC** | VR Omegaverse / Community Tools | 📋 PLANNED | Phase C complete |

**Critical Reality (2026-08-28)**: Soft launch narrative pushed (`release/debut` branch exists) but **4 P0 gates remain RED** — compliance meter broken, OAuth secret in history, allowlist drift, `gate-secrets` FAILS. The PR must not be finalized until all P0s close.

---

## 🚨 PHASE 0: PRE-DEBUT CRITICAL PATH (PUBLIC-DEBUT-01)

**Execution SSOT**: `docs/strategy/DEBUT_REMEDIATION_MANUAL_20260817.md` §5 + `data/coordination/ACTIVE_SPRINT.json`
**Sprint**: PUBLIC-DEBUT-01 | **Phase**: EXECUTION_MINIMAL | **Freeze**: LIFTED

### Ticket Order (MUST execute in sequence)

| Ticket | Description | Owner | Status | Blockers |
|--------|-------------|-------|--------|----------|
| **P0-1** | **SECURITY INCIDENT**: Rotate ALL exposed keys → `git filter-repo` scrub from ALL history → gitleaks/trufflehog to pre-commit + CI → full secret sweep + prune cline checkpoints | Architect (rotate) → Roc (scrub) → Ma'at (gitleaks) → Roc (sweep) | 🔴 IN PROGRESS | GCP rotation click pending; filter-repo pass pending |
| **PUB-1** | Publication allowlist — close G1-G4 gaps, Architect confirms allowlist + `release/debut` branch | Kali | 🔴 IN PROGRESS | 4 files fail allowlist (empty dirs + malformed research filenames) |
| **INST-1** | Install honesty — remove warp-proxy-pool hard dep, move qdrant/redis/youtube to extras, `install.sh .[native,cli]`, MemoryStore no Redis default, stop `_load_sovereign_secrets`, version align, README badge removal | Ma'at | 🔴 IN PROGRESS | 6 critical fixes (INST-1-fix2, fix4, fix6 ready; fix1,3,5 done) |
| **DEL-1** | Deletion campaign — Week 1: delete dead modules; Week 2: one control plane (ProviderSelector only); Week 3: vault honesty | Roc | ⏳ BLOCKED | Depends on INST-1 complete; test suite baseline must be green first |
| **DOC-1** | Strategy stamps — **COMPLETE 2026-08-17** | Kali + Verity | ✅ COMPLETE | — |

### P0 Gate Status (2026-08-28 verification)

| P0 | Status | Evidence |
|----|--------|----------|
| **P0-1** Compliance meter broken | 🔴 RED | `check_mandate_compliance.py` calls `python` (not `python3`); meter not wired into any green gate (`make check-mandates` exits 0, `make temple-grade` passes with placeholder) |
| **P0-2** oracle_cli.py structurally broken | 🟢 REFUTED → P1 | CLI smoke exits 0; fresh-venv import OK; one latent defect: `logger` NameError at import when vault present (L80/85 vs L106) |
| **P0-3** Real OAuth secret in history | 🔴 RED | GOCSPX in 4 commits of `release/debut` history + 12 disk files; filter-repo required |
| **P0-4** Allowlist drift | 🔴 RED | 4 files fail: `data/library`, `data/memory` (empty dirs) + 2 malformed research filenames |
| **P0-5** `make gate-secrets` FAILS | 🔴 RED | GOCSPX 4 commits + PEM baseline path drift (excludes wrong files) |

**GO Condition**: Close P0-1/P0-3/P0-4/P0-5 → re-run 9-item GO checklist → GO. Estimate: ~2–3 engineer-hours + 1 GCP rotation + 1 `git filter-repo` + 2 commits.

### Completed Gates (Green)

| Gate | Command | Verified |
|------|---------|----------|
| M1 AnyIO | `rg 'import asyncio\|from asyncio' src/omega/` (exempted globs) | 0 hits |
| M8 Zero Telemetry | `make check-m8-zero-telemetry` | "No telemetry SDKs in core" |
| M9 Error Integrity | `make check-m9-error-integrity` | "No bare except in core" |
| M14 Heritage | `bash scripts/heritage_vet.sh` | "All heritage tags have vet records" |
| M26 Docs | `make doc-llm-validate` | "All validations passed" |
| D-539 Fresh-Venv | `pip install -e .` + `import omega` + submodules | EXIT 0 |

### Three-Item Critical Path (Demoable Now)

1. **Local Inference E2E**: `omega talk "hello"` → native-gguf → response (IS_CLOUD=False, exit 0, 16.8s cold / <5s warm)
2. **Soul Persistence**: Agent writes L1→L2→L3 to `proposed_lessons.yaml`; `session_end.py` preserves; next session hydrates from `approved_lessons.yaml`
3. **One-Click Install**: `install.sh` provisions venv, downloads Qwen3-1.7B-Q6_K.gguf, sets `OMEGA_MODELS_DIR`, `omega talk` exits cleanly

---

## 📦 PHASE B: POST-DEBUT CLEANSING (Weeks 1–8 post-debut)

**SSOT**: `docs/strategy/POST_DEBUT_ROADMAP.md` | **Gate**: DEL-1 Week 2 complete

| Week | Deliverable | Owner | Gate Command |
|------|-------------|-------|--------------|
| 1–2 | **Router Collapse** — Keep `ProviderSelector`, delete `TriageRouter` + `SemanticRouter` + `RoutingTable`; wiring-preservation assertion | Roc + Ma'at | `rg TriageRouter src/omega && rg SemanticRouter src/omega` → Empty |
| 3–4 | **Vault Honesty** — Architect chooses Path A (delete `src/omega/vault/`) or Path B (≤50-line minimal store, python-age only) | Ma'at + Architect | Architect ruling |
| 5 | **P2 Lint Debt** — 11,400 flake8 violations → 0; no `--exit-zero` for E9/F63/F7/F82 | Verity | `make lint` → 0 |
| 6 | **P3 CI/Hygiene + Qdrant Migration Start** — Real suite, gitleaks, `make temple-grade` green; Deploy Qdrant Podman quadlet | Verity + Ma'at | `make temple-grade` green; `curl localhost:6333/healthz` |
| 7 | **P4 Polish + Qdrant Migration P1–P2** — README, CONTRIBUTING, tag v0.1.0; Revive QdrantAdapter at `src/omega/oracle/adapters/qdrant_adapter.py` (IVectorStoreAdapter, gRPC pool=20); Migration script `scripts/migrate_sqlite_vec_to_qdrant.py` | Kali + Verity + Ma'at | `scripts/migrate_sqlite_vec_to_qdrant.py --dry-run` valid |
| 8 | **Tag v0.1.0** — `pip install -e .` works on fresh machine | Kali | Fresh clone install |

---

## 🧠 HORIZON 2: HYGIENE & SOVEREIGN STRUCTURE (Weeks 9–16)

**Gate**: Phase B complete

| Workstream | Deliverable | Owner | Key Gates |
|------------|-------------|-------|-----------|
| **Qdrant Migration** | P0: Deploy Podman quadlet; P1: Revive QdrantAdapter (IVectorStoreAdapter, gRPC pool=20); P2: Migration script + data migration (FTS5 stays, vec0→qdrant); P3: Quantization + payload indexes (BITS4/BITS2) | Ma'at + Verity | `curl localhost:6333/healthz`; migration dry-run valid |
| **Un-Overengineering** | Phase 0: Pre-flight; Phase 1: 5 library swaps (interlock-cb→HealthMonitor, SQLite+Honker→Redis, httpx2, structlog, prometheus_client); Phase 2: Consolidation (kill HandoffState, soul distillers, HMC→YAML+JSONL); Phase 3: Memory tier simplification (5→3); Phase 4: Hivemind freeze (SHIPPED); Phase 5: Enforcement gates | Ma'at | `make temple-grade` all green |
| **MCP v2 Migration** | Streamable HTTP, OAuth 2.1, client upgrade | Ma'at | SEP-2575 compliant |
| **Heritage Audit** | `make heritage-map` complete; all `[id-soft:]` tags vetted ≥7/10 | Ma'at | Ongoing |
| **Agent & Skill Hardening** | Frontmatter for 3 agents + 5 skills; add missing skills (agent-handoff, soul-evolution, mcp-server); resolve overlapping skills | Ma'at | — |
| **Workbench Infrastructure CLI** | `omega project`, `omega work`, `omega decision` CLI commands | Ma'at | — |
| **Cross-Agent Awareness** | A2A protocol, agent presence (Hivemind TTL/heartbeat), agent capability registry | Lilith + Ma'at | — |
| **Tainted Data Isolation** | TDP implementation for web security (Cognitive Sovereign) | Ma'at | — |
| **Fleet Pool** | V-1 Vault → Grok CLI 8-account ACP smoke → pool | Ma'at + Lilith | V-1 complete |
| **Instruction Router Revival** | Post-debut revival of ModelAwareInstructionRouter | Ma'at | — |

---

## 🧠 HORIZON 3: COGNITIVE ARCHITECTURE (Weeks 9–16 parallel)

**SSOT**: `docs/strategy/POST_DEBUT_ROADMAP.md` §🧠 + `docs/strategy/MODEL_WINDOW_ECONOMICS_20260823.md` (D-601) + `docs/strategy/COGNITIVE_ROUTING_PLAYBOOK.md` + `KALI_BRIEFING_DYNAMIC_PROMPT_PLANNER_EXECUTOR_20260819.md` (D-569)

**Cognitive Architecture Blueprint (D-569 ratified)**: DP-1..DP-8 registered. Owners: Ma'at P0–P3/P7–P8/P10, Kali P4–P5, Verity P6, Researcher P9. Incremental on existing components.

| Phase | Deliverable | File / Component | Owner | Gate |
|-------|-------------|------------------|-------|------|
| **P0** | Context Window Registry | `config/model_context_windows.yaml` + `ContextWindowRegistry` | Ma'at | `cat config/model_context_windows.yaml` exists |
| **P1** | Dynamic Prompt Builder | `src/omega/oracle/prompt_builder.py` + Jinja2 templates (`roles/planner.j2`, `roles/executor.j2`, …) | Ma'at | `ls src/omega/oracle/prompt_builder.py` + `ls config/domains/` |
| **P2** | Role-Aware Model Router | `ProviderSelector.get_ordered_providers_for_role()` | Ma'at | Routes: Planner→mimo-7b-rl, Executor→qwen3-1.7b, Critic→qwen3-1.7b |
| **P3** | Domain Module Loader | `src/omega/oracle/domain_loader.py` + `config/domains/*.yaml` | Ma'at | `await load_domain("engineering", token_budget=8K)`; needs Qdrant P2 |
| **P4** | Planner/Executor Engine | Extends `HybridOrchestrator` with structured DAG + context packer | Ma'at | `pytest tests/contract/test_planner_executor.py` |
| **P5** | Context Packer | Builds executor context from plan step + domain KB (≤4K) | Ma'at | Executor receives ONLY step-relevant context |
| **P6** | Critic + Verifier Pipeline | Critic: LLM rubric-driven (max 2 rev); Verifier: deterministic (pytest/mypy/pydantic) | Verity | "Add at least one deterministic verifier. Never all-LLM." |
| **P7** | Local Model Pre-loading + KV Cache | Pre-load Planner (mimo-7b) + Executor (qwen3-1.7b); KV: Planner q8_0, Executor f16; `--no-mmap --mlock` | Ma'at | SomaticState: Planner saves state between sprints |
| **P8** | SomaticState Planner Integration | State save/restore between sprints | Ma'at | Depends: NativeGGUFProvider, P4 |
| **P9** | EvolveR Distillation Pipeline | Nightly local distillation on Qwen3-1.7B → utility-scored principles → auto-append to principle store | Researcher + Ma'at | EvolveR **extends SDP**, not replaces it |
| **P10** | Freshness System | Scabera composite score (age + embed_lag + owner weights BM25/vector); SourceWatcher; Dashboard | Researcher + Ma'at | Freshness-weighted retrieval with owner accountability |

### Model Window Economics (D-601 — Binding Doctrine)

| Law | Directive |
|-----|-----------|
| **LAW 1** | Ascending Windows — Order multi-model reviews by ASCENDING window size |
| **LAW 2** | Priming Ceilings — Prime to ≤85% of target model's window (≤150K for 200K models) |
| **LAW 3** | Cheap Prime, Expensive Cognate — Tool calls on cheap models; reasoning on expensive |
| **LAW 4** | Digest Before Descent — Wide-window model writes dense digest before narrow-window review |
| **LAW 5** | Family Diversity Weights — Different family > same family/newer version > same weights |
| **LAW 6** | Distill Before Switch — Every reviewer persists gnosis to disk before handoff (M11 applied to chains) |

### Cognitive Routing Playbook (Standard Play)

```
1. PRIME    — cheap/local models gather corpus to ≤150K
2. REVIEW-1 — Sonnet 4.6 deep review (pure cognition, zero tool calls)
3. REVIEW-2 — switch → Gemini 3.1 Pro (no compaction; inherits Review-1)
              mandate: adversarial cross-examination of Review-1
4. RESOLVE  — agreement ⇒ verdict logged (T0 dual-provenance)
              disagreement ⇒ Tier-3 Opus break-glass or Architect escalation
```

---

## 🏗️ HORIZON 4: COMMUNITY TOOL (Weeks 17+)

**Gate**: Phase C complete

| Deliverable | Owner | Acceptance |
|-------------|-------|------------|
| **Sovereign Installer** (`curl -fsSL https://xoe-nov.ai/install \| bash`) | Fleet | Fresh machine installs <300s, `omega talk "hello"` works, no manual config |
| **Entity Studio** (visual soul.yaml + proposed_lessons.yaml management) | Fleet | Agents edit soul without code |
| **WAD Marketplace** (community WAD modules, `omega wad --list`) | Fleet | Community modules discoverable |
| **Open Community Contributions** (PR review gate: mandate compliance mechanical check) | Fleet | Community PRs merge without breaking temple-grade |

---

## 🔑 KEY DECISIONS LOCKED (from ACTIVE_SPRINT.json)

| Decision | ID | Summary |
|----------|----|---------|
| One router only | **D-536** | ProviderSelector + providers.yaml. Delete Triage + Semantic + RoutingTable |
| Vault not wired for debut | **D-535/D-565/D-566** | Hide = PUBLIC_ALLOWLIST.txt exclusion; VaultCore stays in forge/private repo |
| CP-3 not publicly true | **D-539** | Until INST-1 passes on machine without warp-proxy-pool |
| SDP = Human Protocol | **D-538** | `HUMAN PROTOCOL — DO NOT IMPLEMENT` until 10 manual executions |
| C-0.5 Regex Distillation | **D-354′** | SCRAPPED — agents write L1→L2→L3 directly |
| Qdrant replaces sqlite-vec | **D-570** | Horizon 2; debut keeps sqlite-vec; DEL-1 Week 1 deletes dead QdrantAdapter |
| Cognitive Architecture | **D-569** | DP-1..DP-8 registered; incremental on existing components |
| Phase 0 Tracker Lock-In | **D-578..D-584** | 6 post-debut workstreams: GN/DS/LI/KD/HR/ZS |
| zswap > zRAM | **D-526/D-527** | 16GB NVMe swap, zswap enabled (25% pool, lzo_rle, zsmalloc), zRAM DISABLED, swappiness=100, cgroup MemoryMax=6G |
| Nemotron true cost | **D-601 amendment** | $0.00 (zero cost-bearing messages); 611 sessions / 35,111 messages |

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

## ⚠️ ACTIVE BLOCKERS

| Blocker | Description | Owner | Resolution |
|---------|-------------|-------|------------|
| **P0-1-RESIDUAL** | SECURITY_AUDIT ancestor commit + gitleaks wiring | Roc | filter-repo + gitleaks CI |
| **INST-1-FIX2** | pyproject.toml extras split + import guards | Ma'at | Ready |
| **INST-1-FIX4** | Remove `_load_sovereign_secrets()` from model_gateway.py | Ma'at | Ready |
| **ZS ADJUDICATION** | D-584 (zswap+NVMe) vs Carmack-H-1 (zRAM-only); live machine matches H-1 | Architect | Ruling gates LI-5/ZS-2/ZS-3 |
| **GN AUTH** | notebooklm-py auth capture (master_token.json) needs Architect browser | Researcher | Blocked on Architect |

---

## 📚 DOCUMENT HIERARCHY (Conflict Resolution)

1. **Law** → `SOVEREIGN_MANDATES.md` (27 laws, v3.8.0)
2. **This Month's Execution** → `DEBUT_REMEDIATION_MANUAL_20260817.md` + `ACTIVE_SPRINT.json`
3. **Live Pointer** → `HMC_COLLABORATION_HUB.md` `NEXT_ACTION`
4. **Long-Horizon Vision** → `SOVEREIGN_ARK_BLUEPRINT.md` (read-only unless Architect reopens)
5. **Post-Debut Plan** → `POST_DEBUT_ROADMAP.md` (gated on debut)
6. **Fine-Grained Preservation** → `STRATEGY_CORPUS_MAP.md`
7. **Archive** → `docs/archive/` — historical only

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ CANONICAL-ROADMAP ⬡ 2026-08-29*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: jem-2.0 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

