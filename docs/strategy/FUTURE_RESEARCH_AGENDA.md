# 🔱 FUTURE RESEARCH AGENDA — Open Questions, Priorities, Assignments
**AP Token**: `AP-FUTURE-RESEARCH-AGENDA-20260829-v1.0.0`
⬡ OMEGA ⬡ RESEARCHER ⬡ jem-2.0 ⬡ opencode ⬡ trc_future_research_agenda ⬡ ACTIVE

**Date**: 2026-08-29
**Status**: CANONICAL — Consolidated from all open questions across the strategy corpus
**Method**: Open questions extracted from `R_*.md` research reports + `ACTIVE_SPRINT.json` blockers + `CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md` gaps + `GAP_REGISTRY.json` + `CLINE_FULL_REVIEW_ROLLUP_20260828.md` P0/P1/P2 + `STRATEGY_CORPUS_MAP.md` §2.1-2.5 (12 + 5 + 6 + 4 = 27 gaps) + `VISION_ANCHOR_PERPETUAL.md` §9-11 + `POST_DEBUT_ROADMAP.md` + D-XXX gaps

---

## 📋 EXECUTIVE SUMMARY

This document consolidates **all open research questions** into a single prioritized agenda. It is the input to the **Living Research OS** (D-1..D-4) and the **background researcher** (`data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md`).

**Priority Scale**:
- 🔴 **CRITICAL** — Blocks debut or safety gate
- 🟡 **HIGH** — Blocks post-debut planning or quality improvement
- 🟢 **STRATEGIC** — Long-arc value; assigned but not urgent
- ⚪ **MAINTENANCE** — Hygiene; opportunistic

**Specialist Assignment Key**:
- **RCH** = Researcher / Jem
- **MA'AT** = Ma'at / N3 (build)
- **ROC** = Roc / N1 (infrastructure + partitions)
- **CARM** = Carmack (architecture + reviews)
- **GROK** = Grokster (model fleet + platforms)
- **KALI** = Kali (orchestration + decisions)
- **VER** = Verity (mandate audit + distillation)
- **LIL** = Lilith / N7 (memory + soul)
- **ARCH** = Architect (ruling + human-in-loop)
- **DOOM** = Doom_Guy (heritage)

---

## 🔴 CRITICAL: BLOCKS DEBUT OR SAFETY

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **CR-01** | **P0-1**: How to fix the compliance meter (`check_mandate_compliance.py` calls `python` not `python3`; meter not wired into any green gate)? | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P0-1 | MA'AT + VER | 1h |
| **CR-02** | **P0-3**: When to execute `git filter-repo` scrub to remove GOCSPX from 4 commits of `release/debut` history? (Requires Architect confirmation + dedicated session) | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P0-3 | ROC | 2h |
| **CR-03** | **P0-4**: How to close the 4-file allowlist drift (empty dirs `data/library`, `data/memory` + 2 malformed research filenames)? | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P0-4 | KALI | 30 min |
| **CR-04** | **P0-5**: Fix `make gate-secrets` PEM baseline path drift (excludes wrong files; GOCSPX count must be 0) | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P0-5 | MA'AT | 1h |
| **CR-05** | **P1-1**: Fix `oracle_cli.py:80,83,85,106` logger NameError landmine (logger defined L106, used L80/85 during L83 `_inject_vault_to_env` call) | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P1-1 | CLINE | 30 min |
| **CR-06** | **M11 Promotion Backlog**: 49 kali proposals dated 08-26, 20 approved. Who vets the remaining 29? | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P1-4 | KALI | 4h |
| **CR-07** | **P1-5**: Fix `secret-scan.yml` C3 job references `scripts/ci_secret_scan.py` (forge-only) — replace with `make gate-secrets` or delete the step | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P1-5 | MA'AT | 1h |
| **CR-08** | **P1-6**: Sweep 5 tracked soul backups + 1 `.backup` on `release/debut` (`*.bak` doesn't match `*.bak.<ts>` in .gitignore) | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P1-6 | ROC | 30 min |
| **CR-09** | **ZS Adjudication**: D-584 (zswap+NVMe) vs Carmack-H-1 (zRAM-only); live machine matches H-1. Who decides? | `ACTIVE_SPRINT.json` workstream ZS | ARCH | 1h |
| **CR-10** | **GN Auth**: `notebooklm-py` auth capture (`master_token.json`) needs Architect browser. When can Architect do this? | `ACTIVE_SPRINT.json` workstream GN | ARCH + RCH | 1h |

---

## 🟡 HIGH: BLOCKS POST-DEBUT OR QUALITY

### Provider & Model Fleet

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-01** | **Cline `openai-codex` OAuth provider Responses API routing**: Does Cline's `openai-codex` handler auto-route to `/v1/responses` for GPT-5.3-Codex, or does it fall back to `/v1/chat/completions`? (Empirical test needed) | `R_RESEARCHER_GPT53_CLINE_20260828.md` §6 | MA'AT + GROK | 2h |
| **HQ-02** | **OpenAI ORG rate-limit interpretation for 8 keys**: Are 8 Cline-invoked OpenAI keys in the same billing ORG treated as 1 org (500 RPM shared) or 8 orgs (8× rate)? | `R_RESEARCHER_GPT53_CLINE_20260828.md` §6 | GROK | 4h |
| **HQ-03** | **ChatGPT Plus Codex bucket sharing across 8 Cline OAuth instances**: Empirical test of whether 8 Cline CLI sessions on 1 ChatGPT Plus account share a 5h bucket | `R_RESEARCHER_GPT53_CLINE_20260828.md` §6 | GROK | 2h |
| **HQ-04** | **GPT-5.6 Sol independent benchmark verification**: Lab claim 64.6% SWE-Bench Pro vs AA Intelligence Index 58.9 — which is correct? | `R_CARMACK_MODEL_STRATEGY_20260828.md` §2 | GROK | 4h |
| **HQ-05** | **DeepSeek V4 Flash 0731 independent verification**: Vendor reports 79% SWE-bench; need AA re-run | `R_RESEARCHER_DEEPSEEK_V4_FLASH_20260828.md` | GROK | 4h |
| **HQ-06** | **Nemotron 3 Ultra true cost audit at message level**: 611 sessions / 35,111 messages; confirm $0.00 across all fleet | `MODEL_WINDOW_ECONOMICS_20260823.md` §6 | ROC | 2h |
| **HQ-07** | **Cline provider fabric (priority 7) decision**: After `CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md`, what's the long-term plan? B1 CLI-wrapper (4-6h) or keep client-gated? | `CLINE_PROVIDER_ACTIVATION_AUDIT_20260822.md` §3 | MA'AT + KALI | 4h |

### Architecture & Refactoring

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-08** | **D-551 Atomic Split of oracle.py (1459L) + model_gateway.py (1582L)**: What's the split order? ProviderSelector + ModelGateway + IntentDetection + EntityRouting in DEL-1 Week 2? | `DEBUT_REMEDIATION_MANUAL_20260817.md` + D-551 | MA'AT + CARM | 2-3 days |
| **HQ-09** | **11 god-modules >1000 lines** split plan: Which split first, what's the contract test pattern? | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-1 | MA'AT | 4h planning |
| **HQ-10** | **5 of 7 circuit breaker clones deprecated; 2 unmigrated**: Which 2, what's the migration path? | `CARMACK_FULL_REPO_REVIEW_CHECKLIST_VALIDATED_20260828.md` + C-6′ | MA'AT | 4h |
| **HQ-11** | **P2-2: 60 silent `except…: pass` sites** (m23_gate green at 291/292 but disagrees with pyflakes count) | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-2 | VER | 4h |
| **HQ-12** | **P2-3: `_normalize_model` strips `-local/-free/-thinking` → silent re-route**: Exact-match should win first. How to fix? | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-3 | MA'AT | 2h |
| **HQ-13** | **P2-4: M1 loophole unratified**: `tty_agent.py:32` + `governance/` exemption has no D-number in PIVOT_LOG | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-4 | KALI | 30 min |
| **HQ-14** | **P2-5: M20 gate env-dependent**: `llama_cpp` absent → FAIL in meter; should be SKIP/untested | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-5 | MA'AT | 1h |
| **HQ-15** | **P2-6: Full pytest suite (161 files, ~1,887 defs) never completed in-session** — must run in CI with adequate resources | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-6 | MA'AT | 4h |
| **HQ-16** | **P2-7: 24/56 entities have substantive `proposed_lessons.yaml`** (M11 baseline NEW-04) — why 32 are empty? | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-7 | VER | 2h |
| **HQ-17** | **P2-8: OMEGA_ENGINE.md stale** (claims 25 mandates, actual 27 v3.8.0; dates 07-30 vs sprint 08-28) | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-8 | KALI | 1h |
| **HQ-18** | **P2-9: Malformed filenames + internal docs on public branch** (same as P0-4) | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-9 | ROC | 1h |
| **HQ-19** | **P2-10: Duplicate `OmegaError` import pattern** in oracle_cli.py:98-101 + model_gateway.py:56-58 | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-10 | MA'AT | 30 min |
| **HQ-20** | **P2-11: 19 `ses_*` session IDs in WAKE_STATE.json + entity/workspace docs**: policy before any future ship | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-11 | KALI | 2h |
| **HQ-21** | **P2-12: Fleet at 14 cap (M10)**: policy for slot eviction before adding new agents | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-12 | KALI | 2h |

### Living Research OS (D-1..D-4)

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-22** | **D-1 Content Cache** implementation: `.firecrawl/{hash}.md` + TTL eviction 30d/10GB, tiered TTL T1=30d/T2=14d/T3=7d | `POST_DEBUT_ROADMAP.md` §D-1 | LIL + MA'AT | 1 week |
| **HQ-23** | **D-2 Job Board Bridge**: YAML → background researcher queue, `_load_board_jobs()` P0/P1 only, `fcntl.flock` claims | `POST_DEBUT_ROADMAP.md` §D-2 | LIL + MA'AT | 1 week |
| **HQ-24** | **D-3 Auto INDEX.md + follow-ups**: register `R_AUTO_*.md`, propose follow-ups from `GnosisPacket.recommended_directions` | `POST_DEBUT_ROADMAP.md` §D-3 | RCH | 1 week |
| **HQ-25** | **D-4 Gap Detector**: extend `_grow_frontier()` in `loop.py` — scan soul.yaml, INDEX.md, entity knowledge/, contradictions, human topics, auto follow-ups | `POST_DEBUT_ROADMAP.md` §D-4 | RCH | 1 week |
| **HQ-26** | **NotebookLM 5-notebook ingestion** (NL-1): implement `prepare_notebooklm.py` per R52c spec | `STRATEGY_CORPUS_MAP.md` §3.1 | RCH + ROC | 4h |

### Cognitive Architecture (D-569)

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-27** | **P0 Context Window Registry** (`config/model_context_windows.yaml`) — model context windows, max output, vision support | `POST_DEBUT_ROADMAP.md` §P0 | MA'AT | 1 week |
| **HQ-28** | **P1 Dynamic Prompt Builder** — Jinja2 templates, per-role token budgets, context-window-aware truncation | `POST_DEBUT_ROADMAP.md` §P1 | MA'AT | 2 weeks |
| **HQ-29** | **P2 Role-Aware Model Router** — `ProviderSelector.get_ordered_providers_for_role()` | `POST_DEBUT_ROADMAP.md` §P2 | MA'AT | 1 week |
| **HQ-30** | **P3 Domain Module Loader** — `load_domain("engineering", 8K)`, governance levels | `POST_DEBUT_ROADMAP.md` §P3 | MA'AT | 2 weeks (needs Qdrant) |
| **HQ-31** | **P4 Planner/Executor Engine** — structured DAG + context packer | `POST_DEBUT_ROADMAP.md` §P4 | MA'AT | 1 week |
| **HQ-32** | **P5 Context Packer** — executor context ≤4K | `POST_DEBUT_ROADMAP.md` §P5 | MA'AT | 1 week |
| **HQ-33** | **P6 Critic + Verifier** — rubric-driven LLM (max 2 rev) + deterministic (pytest/mypy/pydantic) | `POST_DEBUT_ROADMAP.md` §P6 | VER | 1 week |
| **HQ-34** | **P7 Local Pre-load + KV Cache** — Planner q8_0, Executor f16, `--no-mmap --mlock` | `POST_DEBUT_ROADMAP.md` §P7 | MA'AT | 1 week |
| **HQ-35** | **P8 SomaticState Planner Integration** — state save/restore | `POST_DEBUT_ROADMAP.md` §P8 | MA'AT | 1 week |
| **HQ-36** | **P9 EvolveR Distillation** — nightly on Qwen3-1.7B → principle store, crosses agents (governance-aware) | `POST_DEBUT_ROADMAP.md` §P9 | RCH + MA'AT | 2 weeks |
| **HQ-37** | **P10 Freshness System** — Scabera composite (age + embed_lag + owner weights) | `POST_DEBUT_ROADMAP.md` §P10 | RCH + MA'AT | 2 weeks |

### Un-Overengineering (5 Phases)

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-38** | **UO Phase 0**: Pre-flight — fix M23 pre-commit hook, timed `make test`, fix vet-015, verify MIAP dead, spike stamina vs tenacity, verify interlock-cb AnyIO trio | `POST_DEBUT_ROADMAP.md` §UO | MA'AT | 1 week |
| **HQ-39** | **UO Phase 1**: 5 library swaps — interlock-cb→HealthMonitor, SQLite+Honker, httpx2, structlog, prometheus_client | `POST_DEBUT_ROADMAP.md` §UO | MA'AT | 2 weeks |
| **HQ-40** | **UO Phase 2**: Kill `HandoffState`, consolidate soul distillers, HMC→YAML+JSONL (≤100 lines/week) | `POST_DEBUT_ROADMAP.md` §UO | MA'AT | 2 weeks |
| **HQ-41** | **UO Phase 3**: Memory tier simplification (5→3: file-based, sqlite-vec+FTS5, raw archive) | `POST_DEBUT_ROADMAP.md` §UO | MA'AT | 1 week |
| **HQ-42** | **UO Phase 5**: Enforcement gates — `make temple-grade` includes all swaps | `POST_DEBUT_ROADMAP.md` §UO | VER | 1 week |

### Qdrant Migration (Horizon 2)

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-43** | **Qdrant P0**: Deploy Podman quadlet (`qdrant/qdrant:v1.18.1`, telemetry disabled, API key, 6G MemoryLimit, 80% CPUQuota, gRPC pool=20) | `POST_DEBUT_ROADMAP.md` §Qdrant | MA'AT | 1 week |
| **HQ-44** | **Qdrant P1**: Revive QdrantAdapter at `src/omega/oracle/adapters/qdrant_adapter.py` (IVectorStoreAdapter, gRPC pool=20) | `POST_DEBUT_ROADMAP.md` §Qdrant | MA'AT | 1 week |
| **HQ-45** | **Qdrant P2**: Migration script `scripts/migrate_sqlite_vec_to_qdrant.py` + data migration (FTS5 stays, vec0→qdrant) | `POST_DEBUT_ROADMAP.md` §Qdrant | MA'AT | 1 week |
| **HQ-46** | **Qdrant P3**: Quantization + payload indexes (BITS4 recall, BITS2 compression), `config/qdrant.yaml`, `tests/integration/test_qdrant_migration.py` | `POST_DEBUT_ROADMAP.md` §Qdrant | VER | 1 week |

### Domain Documentation System (D-578..D-584)

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-47** | **DS-1**: Meta-doc (DOMAIN_DOCUMENTATION_SYSTEM.md) | `ACTIVE_SPRINT.json` DS | KALI | 4h |
| **HQ-48** | **DS-2**: `docs/strategy/domains/gemini-notebook/` workspace structure | `ACTIVE_SPRINT.json` DS | KALI | 4h |
| **HQ-49** | **DS-3**: `config/domains/gemini-notebook/` runtime module | `ACTIVE_SPRINT.json` DS | MA'AT | 1 week |
| **HQ-50** | **DS-4**: `scripts/sync_domain_docs.py` (validated copy, not symlink) | `ACTIVE_SPRINT.json` DS | MA'AT | 1 week |
| **HQ-51** | **DS-5**: Update STRATEGY_INDEX.md + STRATEGY_CORPUS_MAP.md with Domain layer | `ACTIVE_SPRINT.json` DS | KALI | 2h |

### Knowledge Domains (D-578..D-584)

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-52** | **KD-1**: Domain module schema — `config/domains/<domain>/` structure, runtime YAML, workspace authoring | `ACTIVE_SPRINT.json` KD | KALI | 1 week |
| **HQ-53** | **KD-2**: Curator model — `config/domains/curators.yaml` with domain→curator_model mappings | `ACTIVE_SPRINT.json` KD | KALI | 1 week |
| **HQ-54** | **KD-3**: Affinity presets per domain (research→qwen3-4b-thinking; coding→mimo-7b-rl-q4_k_m; fast→qwen3-1.7b) | `ACTIVE_SPRINT.json` KD | KALI | 1 week |

### Headroom Integration (D-578..D-584)

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-55** | **HR-1**: HeadroomMiddleware (RESOLVED 811f813f) — tokens_saved metric debt remaining | `ACTIVE_SPRINT.json` HR | MA'AT | 1 week |
| **HQ-56** | **HR-2**: Adaptive context buffer integration (phantom path) | `ACTIVE_SPRINT.json` HR | MA'AT | 1 week |
| **HQ-57** | **HR-3**: MCP headroom tools (RESOLVED — wired oracle.py:163/189/897) | `ACTIVE_SPRINT.json` HR | MA'AT | DONE |

### zswap Subsystem (D-578..D-584)

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-58** | **ZS-1**: zswap sysctl + kernel cmdline deployment (BLOCKED on D-584 vs H-1) | `ACTIVE_SPRINT.json` ZS | MA'AT | 4h |
| **HQ-59** | **ZS-2**: 16GB NVMe swap file creation + systemd unit | `ACTIVE_SPRINT.json` ZS | MA'AT | 4h |
| **HQ-60** | **ZS-3**: WAD packaging (zswap-config.wad for community stacks) | `ACTIVE_SPRINT.json` ZS | MA'AT | 1 week |

### Gemini Notebook v2.0

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-61** | **GN-1**: Deploy `notebooklm-py[mcp]` in `.venv` with isolated auth profile per account (BLOCKED on auth) | `ACTIVE_SPRINT.json` GN | MA'AT | 4h |
| **HQ-62** | **GN-2**: Create 2 strategic notebooks — Ω-ACTIVE-RESEARCH + Ω-KNOWLEDGE-BASE | `ACTIVE_SPRINT.json` GN | RCH | 4h |
| **HQ-63** | **GN-3**: Free-tier fetch pipeline + systemd timer (weekly sync, 10 DR/mo corrected budget) | `ACTIVE_SPRINT.json` GN | MA'AT | 1 week |
| **HQ-64** | **GN-4**: NLG-SMOKE — Single-account free-tier Deep Research smoke test | `ACTIVE_SPRINT.json` GN | RCH | 1h |
| **HQ-65** | **GN-5**: SDP distillation pipeline + Scribe handoff integration (manual mode per GAP-8) | `ACTIVE_SPRINT.json` GN | RCH | 1 week |

### Truth-Alignment Dataset

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-66** | **TA-001..014**: Wire `truth_events.jsonl` to `omega_memory_search` hybrid retrieval | `ACTIVE_SPRINT.json` TRUTH | KALI | 1 week |
| **HQ-67** | **TA Dual-arm**: Dual-arm incident review protocol codification | `ACTIVE_SPRINT.json` TRUTH | KALI | 1 week |

### Orchestrator Cutover

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **HQ-68** | **OC Model choice**: Architect selects model for MaKaLi orchestrator | `ACTIVE_SPRINT.json` ORCHESTRATOR | ARCH | 1h |
| **HQ-69** | **OC Cutover timing**: When to flip from shadow to primary | `ACTIVE_SPRINT.json` ORCHESTRATOR | ARCH | 1h |
| **HQ-70** | **P13 Logging GO**: Approve steering wrapper syntax | `ACTIVE_SPRINT.json` ORCHESTRATOR | ARCH | 30 min |
| **HQ-71** | **Shapley fleet analysis**: Before locking orchestrator structure | `ACTIVE_SPRINT.json` ORCHESTRATOR | KALI | 1 week |
| **HQ-72** | **N5 router collapse Week 2**: After Week 1 | `ACTIVE_SPRINT.json` ORCHESTRATOR | KALI | 2 weeks |

---

## 🟢 STRATEGIC: LONG-ARC VALUE

### Vision & Heritage

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **ST-01** | **R-24 Soul-to-Visual Mapping** (VR Foundation) — UNASSIGNED critical path. VR Omegaverse Phase 4, 2028 horizon | `STRATEGY_CORPUS_MAP.md` §3.1 + `VISION_ANCHOR_PERPETUAL.md` §7 | UNASSIGNED | — |
| **ST-02** | **Legacy GitHub repo mining** — download before public (Correction 5) | `VISION_ANCHOR_PERPETUAL.md` §9 | ARCH + ROC | 2 days |
| **ST-03** | **Sovereign Ark linguistic era mapping** — map influence in current Engine | `VISION_ANCHOR_PERPETUAL.md` §11 | UNASSIGNED | 1 week |
| **ST-04** | **Temple-Grade Instruction Frequency Metric** — instrument ADTG vs EETG over time | `VISION_ANCHOR_PERPETUAL.md` §10 | ROC | 2 weeks |
| **ST-05** | **Godot Bridge** as engine component #5 — VR Omegaverse infrastructure | `VISION_ANCHOR_PERPETUAL.md` §7 | UNASSIGNED | — |
| **ST-06** | **P2P soul-print exchange** — user universes traversal | `VISION_ANCHOR_PERPETUAL.md` §7 | UNASSIGNED | — |
| **ST-07** | **Virtual research centers** — full staff, slash R&D times exponentially | `VISION_ANCHOR_PERPETUAL.md` §7 | UNASSIGNED | — |

### Heritage & Community

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **ST-08** | **Heritage Audit** — `make heritage-map` complete; all `[id-soft:]` tags vetted ≥7/10 with scope | `POST_DEBUT_ROADMAP.md` §Heritage | DOOM | 1 month |
| **ST-09** | **WAD Marketplace governance** — community module discovery | `POST_DEBUT_ROADMAP.md` §Horizon 4 | FLEET | — |
| **ST-10** | **Entity Studio** — visual soul.yaml + proposed_lessons.yaml management | `POST_DEBUT_ROADMAP.md` §Horizon 4 | FLEET | — |
| **ST-11** | **Sovereign Installer** — `curl -fsSL https://xoe-nov.ai/install \| bash` | `POST_DEBUT_ROADMAP.md` §Horizon 4 | FLEET | — |
| **ST-12** | **Open Community Contributions** — PR review gate | `POST_DEBUT_ROADMAP.md` §Horizon 4 | FLEET | — |

### Architecture & Process

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **ST-13** | **Agent & Skill Hardening** (Workstream A) — frontmatter, missing skills, overlapping skills | `POST_DEBUT_ROADMAP.md` §Workstreams | MA'AT | 1 month |
| **ST-14** | **Workbench Infrastructure CLI** (Workstream D) — `omega project`, `omega work`, `omega decision` | `POST_DEBUT_ROADMAP.md` §Workstreams | MA'AT | 1 month |
| **ST-15** | **Cross-Agent Awareness** (Workstream E) — A2A protocol, agent presence, capability registry | `POST_DEBUT_ROADMAP.md` §Workstreams | LIL + MA'AT | 1 month |
| **ST-16** | **Tainted Data Isolation** (Cognitive Sovereign) | `POST_DEBUT_ROADMAP.md` §Workstreams | MA'AT | 1 month |
| **ST-17** | **Fleet Pool** — V-1 Vault → Grok CLI 8-account ACP smoke → pool | `POST_DEBUT_ROADMAP.md` §Workstreams | MA'AT + LIL | 1 month |
| **ST-18** | **Instruction Router Revival** — Post-debut revival of ModelAwareInstructionRouter | `POST_DEBUT_ROADMAP.md` §Workstreams | MA'AT | 1 month |
| **ST-19** | **MCP v2 Migration** — Streamable HTTP, OAuth 2.1, client upgrade | `POST_DEBUT_ROADMAP.md` §MCP | MA'AT | 2 weeks |

### Hardening & Security

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **ST-20** | **AppArmor container hardening** — V-10 GAP (containers unconfined) | `STRATEGY_CORPUS_MAP.md` §6 + `SOVEREIGN_ARK_BLUEPRINT.md` §5 | MA'AT | 1 month |
| **ST-21** | **IA2 envelope freshness/signature** — V-9 GAP (no freshness check) | `STRATEGY_CORPUS_MAP.md` §6 | MA'AT | 2 weeks |
| **ST-22** | **V-1 Omega-Vault MVP** — credential / session automation (DEFERRED per D-535/D-565/D-566) | `SOVEREIGN_ARK_BLUEPRINT.md` §5 | RCH + GROK → MA'AT | 1 month |
| **ST-23** | **Hardening Deep Dive** — IDE supply chain (May 19 GitHub breach), FIDO2 SSH, CIS v2.0.0, systemd-analyze security as CI gate | `YOUTUBE_RESEARCH_SESSIONS/2026-07-30/04_evidence/HARDENING_DEEP_DIVE.md` | MA'AT | 1 month |
| **ST-24** | **Restic 3-2-1 Backup** — Amended: local repo acceptable; timer not enabled (only remaining required Phase D gate failure) | `SOVEREIGN_ARK_BLUEPRINT.md` §4 | MA'AT | 2 weeks |
| **ST-25** | **Workstation hardening** — `scripts/omega-harden-workstation.sh` created, run now | `YOUTUBE_RESEARCH_SESSIONS/2026-07-30/04_evidence/HARDENING_DEEP_DIVE.md` | ROC | 1 week |
| **ST-26** | **Workstation hardening CIS v2.0.0 + USG baseline**: Apply to all fleet machines | HARDENING_DEEP_DIVE | ROC | 1 month |

### Model Fleet & Performance

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **ST-27** | **Ornith-9B** — Qwen3.5 fine-tune (MIT, 69.4 SWE-Bench) — hardware-gated (16GB+ VRAM) | `YOUTUBE_RESEARCH_SESSIONS/2026-07-30/04_evidence/ORNITH_9B_TECHNICAL_DEEP_DIVE.md` | UNASSIGNED | When GPU available |
| **ST-28** | **Vulkan llama.cpp backend** — `GGML_VULKAN=ON` rebuild, GPU-agnostic binary | `YOUTUBE_RESEARCH_SESSIONS/2026-07-30/04_evidence/VULKAN_BACKEND_DEEP_DIVE.md` | MA'AT | 1 week |
| **ST-29** | **llama-optimus** — auto-tuning (15-35% CPU speedup) as pre-calibration pipeline | `YOUTUBE_RESEARCH_SESSIONS/2026-07-30/04_evidence/LLAMA_OPTIMUS_DEEP_DIVE.md` | MA'AT | 1 week |
| **ST-30** | **Instruction Router** — ModelAwareInstructionRouter (4-tier capability taxonomy T0-T3) | `YOUTUBE_RESEARCH_SESSIONS/2026-07-30/04_evidence/INSTRUCTION_ROUTER_DEEP_DIVE.md` | MA'AT | 2 weeks |
| **ST-31** | **Local Inference Opt** (LI-1..LI-5) — Sequential loading, q8_0 KV, Tier 0/1/2 matrix | `ACTIVE_SPRINT.json` LI | MA'AT | 1 month |
| **ST-32** | **Adaptive Context Buffer** (LI-1) — token-pressure gauge auto-reduces before OOM | `ACTIVE_SPRINT.json` LI | MA'AT | 1 week |
| **ST-33** | **Sequential Model Loader** (LI-2) — no mmap, keep context alive, one model at a time | `ACTIVE_SPRINT.json` LI | MA'AT | 1 week |
| **ST-34** | **llama-fit-params** (LI-3) — hardware probe at startup | `ACTIVE_SPRINT.json` LI | MA'AT | 1 week |

### Open Research Items (docs/research/INDEX.md)

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **ST-35** | **R-21 Agent Handoff Protocol** — UNRESEARCHED | `docs/research/INDEX.md` | UNASSIGNED | — |
| **ST-36** | **R-22 MCP Community Audit** — UNRESEARCHED | `docs/research/INDEX.md` | UNASSIGNED | — |
| **ST-37** | **R-23 Cold-Start Mitigation** — UNRESEARCHED | `docs/research/INDEX.md` | UNASSIGNED | — |
| **ST-38** | **R-24 Soul-to-Visual Mapping** (VR Foundation) — UNRESEARCHED; critical path | `docs/research/INDEX.md` | UNASSIGNED | — |
| **ST-39** | **R-35 Agent Handoff & State Transfer Protocol** — UNRESEARCHED | `docs/research/INDEX.md` | UNASSIGNED | — |
| **ST-40** | **R-36 Soul-to-Visual Mapping** (VR Foundation) — UNRESEARCHED | `docs/research/INDEX.md` | UNASSIGNED | — |
| **ST-41** | **R-37 Axiom & Ideal Generation Framework** — UNRESEARCHED | `docs/research/INDEX.md` | UNASSIGNED | — |

### Long-Arc Themes (PARKED from Ark v4.4)

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **ST-42** | **Strike 11 Sovereign WAD Protocol** (Lumps, Bus, Ethics WADs) | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-43** | **Strike 11.5 Council Dispatcher** deep | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-44** | **Dimension Framework / cartridges** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-45** | **Free-Will datasets / 42 Ideals training** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-46** | **Advanced ingestion & background workers** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-47** | **Jem S1–S5 sovereignty gaps** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-48** | **Gap Resolution S1–S6** (proxy, whisper, budget, quality, scheduler, YT sieve) | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-49** | **Tier 0 Ship-It** (F821, bare except, logging, Pydantic config) — fold into C-0 | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-50** | **D-290 Session Namespace Isolation** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-51** | **D-291 MIAP Phase 0** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-52** | **D-292 MACP alignment** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-53** | **D-293 Context Engineering knowledge layer** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-54** | **D-294 Experience Repository / Scribe** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-55** | **D-295 Trace-to-Eval** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-56** | **D-303 Headless Subagent Pool 24 accounts** (after V-1 + ACP smoke) | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-57** | **D-305 Hive Evolution** | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |
| **ST-58** | **D-306 Arch Soul / Nameless One** (Torment track) | `STRATEGY_CORPUS_MAP.md` §6 | UNASSIGNED | — |

---

## ⚪ MAINTENANCE: HYGIENE

| ID | Question | Source | Assign | Time Budget |
|----|----------|--------|--------|-------------|
| **MN-01** | **OMEGA_ENGINE.md update** (P2-8): claims 25 mandates → actual 27 v3.8.0; sprint date 08-28 | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P2-8 | KALI | 1h |
| **MN-02** | **P1-7: `make firewall-check` doesn't exist** — remove from docs or implement | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P1-7 | CLINE | 1h |
| **MN-03** | **P1-8: Temple-grade gate is decorative** — implement or delete placeholder | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P1-8 | CARM + KALI | 4h |
| **MN-04** | **P1-9: `check_mandate_compliance.py` not called in CI** — add to `make check-mandates` | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P1-9 | KALI | 2h |
| **MN-05** | **P1-10: pyflakes 174 findings (42 redefinitions, 62 unused imports)** | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P1-10 | MA'AT | 1 month |
| **MN-06** | **P1-2: Provider contract test STALE vs providers.yaml** — `deepseek-v4-flash` no longer on openrouter | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P1-2 | MA'AT | 1h |
| **MN-07** | **P1-3: Soul contract test couples to LIVE data** — assert staging==[] fails with 49 kali proposals | `CLINE_FULL_REVIEW_ROLLUP_20260828.md` §P1-3 | MA'AT + CLINE | 2h |
| **MN-08** | **Hivemind N13 closeout** — N13 retired; reassign N13 calls | `HIVEMIND_N13_CLOSEOUT_20260822.md` | LIL | 1h |
| **MN-09** | **Session end hook** — verify M5/M11 preservation working | D-VOS-002 | VER | 30 min |
| **MN-10** | **Soul validator VALID_SOUL_VERSIONS** — verify v7.x entities receiving strict validation | D-VOS-003 | VER | 30 min |

---

## 📊 RESEARCH BACKLOG STATISTICS

| Priority | Count | Description |
|----------|-------|-------------|
| 🔴 CRITICAL | 10 | Blocks debut or safety |
| 🟡 HIGH | 65 | Blocks post-debut or quality |
| 🟢 STRATEGIC | 58 | Long-arc value; assigned but not urgent |
| ⚪ MAINTENANCE | 10 | Hygiene; opportunistic |
| **TOTAL** | **143** | All open questions |

---

## 🎯 ASSIGNMENT SUMMARY

| Agent | CR | HQ | ST | MN | Total |
|-------|----|----|----|----|-------|
| **ARCH (Architect)** | 2 | 0 | 0 | 0 | 2 |
| **KALI (Orchestration)** | 3 | 7 | 1 | 4 | 15 |
| **MA'AT (Build)** | 4 | 22 | 11 | 2 | 39 |
| **LIL (Memory/Soul)** | 0 | 3 | 1 | 1 | 5 |
| **ROC (Infrastructure)** | 1 | 3 | 4 | 1 | 9 |
| **RCH (Research)** | 1 | 4 | 2 | 0 | 7 |
| **GROK (Model Fleet)** | 0 | 5 | 0 | 0 | 5 |
| **CARM (Architecture)** | 0 | 2 | 0 | 1 | 3 |
| **VER (Compliance)** | 1 | 3 | 0 | 2 | 6 |
| **CLINE (Cline Entity)** | 2 | 0 | 0 | 1 | 3 |
| **DOOM (Heritage)** | 0 | 0 | 1 | 0 | 1 |
| **FLEET (Collective)** | 0 | 0 | 4 | 0 | 4 |
| **UNASSIGNED** | 0 | 0 | 30 | 0 | 30 |
| **TOTAL** | **10** | **65** | **58** | **10** | **143** |

---

## 🔍 DECISIONS NEEDED

| Gap | Description | Blocked On |
|-----|-------------|------------|
| **D-XXX** | Architect ruling on ZS adjudication (D-584 zswap+NVMe vs Carmack-H-1 zRAM-only) | Architect |
| **D-XXX** | Fleet pool size beyond 14 (M10 cap) — slot eviction policy | Architect + Kali |
| **D-XXX** | Qdrant migration trigger threshold (>500k vectors vs. earlier) | Ma'at + Verity |
| **D-XXX** | Heritage vet record threshold for new `[id-soft:]` tags (≥7/10 scope) | Doom_Guy |
| **D-XXX** | Community installer scope (Sovereign Installer) — curl\|bash vs. guided | Fleet |
| **D-XXX** | WAD Marketplace governance model (community modules) | Fleet |
| **D-XXX** | R-24 Soul-to-Visual Mapping assignment (unassigned critical path) | Architect |
| **D-XXX** | Legacy GitHub repo mining (Correction 5) — download before public | Architect |
| **D-XXX** | Sovereign Ark linguistic era mapping (VISION_ANCHOR §11) | Recursive specialist |
| **D-XXX** | R-21, R-22, R-23, R-35, R-36, R-37 — 6 UNRESEARCHED items need ownership | Architect |

---

## 📋 LIVING RESEARCH OS INTEGRATION

This agenda integrates with the **Living Research OS** (D-1..D-4):

- **D-1 Content Cache**: `.firecrawl/{hash}.md` + TTL eviction 30d/10GB → stores research inputs
- **D-2 Job Board Bridge**: YAML → background researcher queue → `P0/P1 only` (per D-540)
- **D-3 Auto INDEX.md + follow-ups**: Registers `R_AUTO_*.md` research outputs
- **D-4 Gap Detector**: Extends `_grow_frontier()` in `loop.py` → **FEEDS this agenda automatically**

Each research item should:
1. Be added to `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` job board
2. Have `_load_board_jobs()` claim via `fcntl.flock`
3. Produce output: `R-{n}_{topic}.md` in `docs/research/` (or `data/coordination/`)
4. Distill to `proposed_lessons.yaml` per M11

---

## 🔗 CROSS-REFERENCES

- `CANONICAL_ROADMAP.md` — Current roadmap
- `CANONICAL_ARCHITECTURE.md` — System architecture
- `CANONICAL_DECISIONS.md` — D-521..D-612
- `CANONICAL_CONSTRAINTS.md` — Mandates + hardware + budget
- `CANONICAL_MODEL_FLEET.md` — Model assignments
- `STRATEGY_CORPUS_INDEX.md` — Classification of 141+623+609 docs
- `STRATEGY_CORPUS_MAP.md` §2.1-2.5 — 27 original gaps
- `data/coordination/GAP_REGISTRY.json` — Live gap registry
- `data/coordination/RESEARCH_PLAN_PHASE1_4_20260813.md` — Phase 1-4 research plan
- `docs/research/INDEX.md` — 173 R-items research index
- `POST_DEBUT_ROADMAP.md` — Post-debut phases
- `ACTIVE_SPRINT.json` — Sprint state

---

*⬡ OMEGA ⬡ RESEARCHER ⬡ FUTURE-RESEARCH-AGENDA ⬡ 2026-08-29*
<!-- PROVENANCE-CORRECTED 2026-08-30T03:06:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: jem-2.0 | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->

