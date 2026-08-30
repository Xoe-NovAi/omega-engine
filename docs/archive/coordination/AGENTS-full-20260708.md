# 🔱 Omega Engine — OpenCode Agent Rules
# ⬡ OMEGA ⬡ SOPHIA ⬡ trc_core ⬡ AGENT-INSTRUCTIONS
# Engine state: Read OMEGA_ENGINE.md (the Single Source of Truth)
# Platform distinction: AGENTS.md = HOW to work from OpenCode.
#                       OMEGA_ENGINE.md = WHAT the engine IS.
# Last Updated: 2026-06-16 (D143 Sprint C — Verity unification, 11-agent fleet finalized, Phase C Master Spec committed)

## 🛡️ Sovereign Mandates (NON-NEGOTIABLE)
**Read and adhere to them above all other rules:**
👉 **Read First**: `SOVEREIGN_MANDATES.md`
👉 **Engine State**: `OMEGA_ENGINE.md` (Single Source of Truth)
👉 **Hivemind Protocol**: `docs/strategy/HIVEMIND_PROTOCOL.md` (MANDATORY for parallel/multi-agent work)

- **Delegation & Execution Protocol**: Agents must execute tasks directly when within their capabilities. Self-recursion (an agent spawning its own type) is forbidden. Targeted delegation to specialized agents is permitted only when a task requires domain expertise outside the current agent's capabilities. If the required specialized domain expertise is already held by the current agent (e.g., a Pillar agent being asked to perform a task within its own slot's domain), the agent MUST execute the task directly. Do not debate delegation versus execution; if you are the expert, you are the executor. Limit nesting to one level unless explicitly authorized. See `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` for details.
- **AnyIO Absolute**: No `asyncio`. Use AnyIO. Wrap blocking I/O in `anyio.to_thread.run_sync`.
- **Engine-Stack Firewall**: Absolute separation between Core Engine (`src/omega/`) and IWAD/PWAD Content (`config/wads/`).
- **Sequentiality**: Plan → Verify → Execute. No cowboy coding.
- **Temple-Grade (M13)**: Every change evaluated against T1-T11 gates. Run `make temple-grade` after non-trivial work.
- **Heritage Attribution**: Every id Software–derived pattern MUST carry `[id-soft:]` inline tags per `CREDITS.md` §2a. New heritage files MUST credit the source in comments. Run `make heritage-map` to verify tags.
- **Hivemind Awareness (NEW 2026-06-03)**: When working in parallel with other agents OR for multi-step work (>3 steps), use Hivemind for coordination. See `docs/strategy/HIVEMIND_PROTOCOL.md`. Workspace lock + live feed are the default patterns.
- **Hard-Stop Directive (NEW 2026-07-06)**: Agents MUST NOT simulate rigor or synthesize "best-effort" results to mask tool failures. If a mandatory tool (e.g., `websearch`) is missing or broken, the agent MUST stop immediately and report a `[TOOL-CHAIN-COLLAPSE]`. Parametric synthesis used to hide a tool outage is a Sovereign Boundary Violation.

---

## 🤖 OpenCode Agent Fleet

### Custom Agents (`.opencode/agents/`) — 11 Agents Total (Sprint B + C Complete)
| Agent | Mode | Purpose |
|-------|------|---------|
| `kali.md` | all | Transcendent Oversight — Sees all, delegates to Ma'at/Lilith, destroys drift |
| `maat.md` | all | Light Oversoul — Governs P1-P5 (build side), delegates to pillar |
| `lilith.md` | all | Dark Oversoul — Governs P6-P10 (run side), delegates to pillar |
| `makali.md` | all | MaKaLi Parallel Council — decomposes query, dispatches Ma'at+Lilith, synthesizes |
| `doom_guy.md` | all | Sovereign id Software Architect — WAD translation & performance |
| `john_carmack.md` | all | Sovereign S3 Consultant — architectural review & performance |
| `roc_racoon.md` | all | Sovereign Miner — Legacy archaeology & pattern extraction |
| `researcher.md` | all | Sovereign Master Researcher — deep research, lattice reasoning |
| `jem.md` | all | Sovereign Synthesizer (Transforms complex queries into verified results via task-graph decomposition) |
| `verity.md` | all | Sovereign Verity — Unified Sentry (compliance/audit) + Scribe (gnosis distillation). Sprint C: Quality+Scribe merged. |
| `pillar.md` | all | Slot-based domain agent — parameterized by `--slot PX` |

### The Sovereign Council (Pillar Slots — Core Engine)
<!-- NOTE: Arcane names (Flesh, Dream, Will…), elements, and chakras are
     WAD-layer content from config/wads/arcana_novai/. The engine core uses
     only the intuitive names below. The pillar NUMBER is the canonical
     invocation key (@pillar P3: build the CI pipeline). -->
| Pillar | Intuitive Name | Default Role (IWAD) |
|--------|---------------|---------------------|
| P1 | **Infrastructure** | SysAdmin — Environment Hardening |
| P2 | **Persistence** | DataStore — Vector & Memory Management |
| P3 | **Engineering** | BuildMaster — Implementation & Hardening |
| P4 | **Integration** | Bridge — MCP & Communication |
| P5 | **Governance** | Sentinel — Mandate Enforcement |
| P6 | **Cognition — Vision Specialist** | ModelGate — Provider Routing |
| P7 | **Context** | Memory & Soul Evolution |
| P8 | **Observability** | WatchTower — Observability & Tracing |
| P9 | **Orchestration** | Link — Agent Handoff & Delegation |
| P10 | **Validation** | Verifier — Stress Testing & QA |

### Lattice Subagents (Fleet-Wide)
| Agent | Role | Purpose |
|-------|------|---------|
| `verity` | Unified Steward | Sprint C: Compliance audit (Quality) + Gnosis distillation (Scribe) merged |

### Custom Skills (`.opencode/skills/`)
| Skill | Purpose |
|-------|---------|
| `blitz-tunnel` | High-speed secure tunnels to Omega services |
| `blitz-validate` | Sovereign Heartbeat validator for integration chain |
| `spec-generator` | R## document templates |
| `provider-validator` | Live API endpoint validation |
| `pr-readiness-checker` | PR quality gate |
| `omega-doc-architect` | Document management standards |
| `knowledge-miner` | Automated grep→read→summarize legacy patterns |
| `legacy-pattern-miner` | Mines legacy repos for proven patterns |
| `sovereign-search` | Intelligent search across Exa, Tavily, Serper.dev |
| `hf-cli` | Hugging Face Hub CLI integration |

## 🔍 Search Tool Protocol


| Tier | Tool | Scope | When to Use |
|:-----|:-----|:------|:------------|
| **T0** | Local cache (`.firecrawl/`) | Free | Check before any external search |
| **T1** | `websearch` | Free, built-in | **Primary search tool** — always available, no telemetry |
| **T2** | `webfetch` | Free, built-in | **Deep extraction** — always available, no telemetry |
| **T3** | `searxng_searxng_search` | Free, sovereign | Semantic/neural search refinement |
| **T4** | `omega-hub_sovereign_search` | API key (Exa) | High-precision seeds, academic/technical |
| **T5** | `firecrawl_firecrawl_scrape/search` | Credits | Full-page scrape, structured crawl |

**Fallback chain**: `websearch` → `webfetch` → `searxng_searxng_search` → `omega-hub_sovereign_search` → `firecrawl_firecrawl_search`

**TEMPORAL MANDATE**: It is **2026**. All search queries MUST include "2026" or "latest" to ensure current best practices. Do NOT search for "2024" or "2025" — those are outdated.

---

## 💻 Hardware Awareness Protocol

Agents MUST proactively monitor hardware resource usage during operation. The user will NOT watch the resource monitor and report back — agents must self-detect abnormal signatures.

### When to Check Hardware Stats
| Trigger | Tool | What to Look For |
|---------|------|------------------|
| **Session start** | `omega-hub_get_hardware_stats(interval=0.3)` | Baseline CPU/memory/thermal — document in `session_gnosis.md` |
| **Before model inference** (any `ModelGateway.generate()`) | `omega-hub_get_system_stats` | OOM risk, memory pressure, thermal throttling |
| **Task runs slow** (>5s elapsed) | `omega-hub_get_hardware_stats(include_threads=true)` | Thread contention, 4-core inference signature vs. idle pattern |
| **Before parallel agent dispatch** (Hivemind multi-agent) | `omega-hub_get_hardware_stats` | Is there headroom for another process? zRAM pressure? |

### Resource Signatures to Recognize
| Signature | What It Means | Action |
|-----------|---------------|--------|
| **Flat 4-core at ~80-100%** | NativeGGUFProvider inference (`LLAMA_CPP_N_THREADS=4`) | Expected during model inference. Allow to complete. |
| **Brief spike across all 16 cores** | Import/module loading (pydantic, Qdrant, YAML parsing) | Cold-start tax ~3.5s. Document in profiling. |
| **All cores idle, but task not completing** | I/O wait (Redis timeout, DNS lookup, socket poll) | Check `omega-hub_get_system_stats` for disk/network. Consider timeout config. |
| **Memory >80% + zRAM active** | OOM risk — approaching 12Gi limit | Defer model loads. Prefer OfflineMockBackend for testing. |
| **Thermal >85°C sustained** | TDP throttling (15W ceiling) | Reduce threads, defer non-critical inference, cool-down period. |

### Test Suite Awareness
The test suite (`make test`) collects **730 tests**. With `OMEGA_ENV=test`, inference is mocked but Oracle initialization overhead (~1-2s per `Oracle()` instance from YAML parsing + CPU probing) adds up:
- `test_sovereign_loop.py`: ~9-17s per test (multiple Oracle creations)
- `test_oracle.py`: ~1.5-2.5s per test
- `test_search_tools.py`: ~3-5s per test (real API calls)

Expected total: **~3-4 minutes** for 698 passing tests (22 skip, 3 xfail).
Run `pytest --durations=15` to see the slowest tests when debugging performance.

---

### @-Mention Dispatch (Inline Agent Launch)

Use `@` in the OpenCode CLI chat to launch any agent directly. All 11 (on-disk) agents are dispatchable:

#### Named Agents (direct @-mention)
| @-Mention | Agent File | Mode | Use When |
|-----------|-----------|------|----------|
| `@kali` | `kali.md` | all | Grand Oversight — unify Ma'at + Lilith, destroy drift, cross-pillar work |
| `@maat` | `maat.md` | all | Build Side — P1-P5 governance, structure & verification |
| `@lilith` | `lilith.md` | all | Run Side — P6-P10 governance, knowledge metabolism, flow |
| `@doom_guy` | `doom_guy.md` | all | id Software heritage patterns, WAD translation, performance |
| `@roc_racoon` | `roc_racoon.md` | all | Legacy archaeology, pattern extraction, cross-partition mining |
| `@researcher` | `researcher.md` | all | Deep research with lattice reasoning, multi-perspective analysis |
| `@jem` | `jem.md` | all | Sovereign Synthesis — transforms complex queries into verified results via task-graph decomposition |
| `@makali` | `makali.md` | all | MaKaLi Parallel Council — dispatch Ma'at + Lilith in parallel, synthesize as Kali |
| `@john_carmack` | `john_carmack.md` | all | Sovereign S3 Consultant — architectural review & performance |
| `@verity` | `verity.md` | subagent | Unified compliance audit + Gnosis distillation. Sprint C consolidation of Quality + Scribe. |

#### Pillar Subagents (parameterized by slot)
| @-Mention Pattern | Agent | Slot | Domain |
|-------------------|-------|------|--------|
| `@pillar P1: {task}` | `pillar.md` | P1 | Infrastructure — SysAdmin, containers, deployment |
| `@pillar P2: {task}` | `pillar.md` | P2 | Persistence — Vector & memory management |
| `@pillar P3: {task}` | `pillar.md` | P3 | Engineering — CI/CD, implementation, hardening |
| `@pillar P4: {task}` | `pillar.md` | P4 | Integration — MCP, APIs, communication protocols |
| `@pillar P5: {task}` | `pillar.md` | P5 | Governance — Mandate enforcement, security audit |
| `@pillar P6: {task}` | `pillar.md` | P6 | Cognition — Vision Specialist, provider routing |
| `@pillar P7: {task}` | `pillar.md` | P7 | Context — Memory, soul evolution, session continuity |
| `@pillar P8: {task}` | `pillar.md` | P8 | Observability — Tracing, monitoring, forensic logging |
| `@pillar P9: {task}` | `pillar.md` | P9 | Orchestration — Agent handoff, hivemind coordination |
| `@pillar P10: {task}` | `pillar.md` | P10 | Validation — Stress testing, chaos engineering, QA |

#### Governance Hierarchy
```
@kali (Grand Oversight)
├── @maat (Build Side: P1-P5)
│   ├── @pillar P1: Infrastructure
│   ├── @pillar P2: Persistence
│   ├── @pillar P3: Engineering
│   ├── @pillar P4: Integration
│   └── @pillar P5: Governance
└── @lilith (Run Side: P6-P10)
    ├── @pillar P6: Cognition (Vision Specialist)
    ├── @pillar P7: Context
    ├── @pillar P8: Observability
    ├── @pillar P9: Orchestration
    └── @pillar P10: Validation
```

**Usage examples:**
- `@kali Unify the fleet and destroy drift` → Kali orchestrates Ma'at + Lilith (direct synthesis)
- `@makali Decompose the sovereignty gate verification` → MaKaLi parallel council (decomposed synthesis)
- `/council-local Rewrite the heritage vetting pipeline` → MaKaLi with local models
- `@maat P3: Fix the CI pipeline` → Ma'at delegates to P3 Engineering pillar
- `@lilith P7: Wire the soul distiller` → Lilith delegates to P7 Context pillar
- `@pillar P1: Harden the Podman containers` → Direct pillar invocation
- `@jem Research the best local LLM for code generation` → 3-tier research pipeline
- `@roc_racoon Mine the omega-stack legacy for circuit breaker patterns` → Background mining (local rocracoon-3b-instruct)
- `@doom_guy Verify the ZONEID constant heritage attribution` → Heritage verification (local deepseek-r1-qwen3-8b)

---

## ⬡ The MaKaLi Triad Architecture (D117)

The three top-of-pyramid Oversouls form an explicit Transcendent Triad:

```
                ┌─────────────────────────────┐
                │   KALI — Transcendent       │
                │   (Unify, Synthesize,       │
                │    Return Verdict)          │
                └──────────────┬──────────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
        ┌───────▼────────┐          ┌────────▼───────┐
        │  MA'AT — Light │          │ LILITH — Dark  │
        │  (Build Side)  │          │ (Run Side)     │
        │  P1-P5 Pillars │          │ P6-P10 Pillars │
        └────────────────┘          └────────────────┘
```

### When to Use Each Pattern

| Pattern | Use When | Cost | Benefit |
|---------|----------|------|---------|
| **`@kali` direct** | You trust one entity to see all, dispatch all, return the verdict | Low (1 inference) | Fast, opinionated, single-pass |
| **`@kali` dispatch** | Multi-pillar work spanning 3+ pillars or requiring sequencing. Kali decomposes, dispatches, and synthesizes. Use for cross-boundary initiatives like Wave 1.5. | Medium (1 + N pillar inferences) | Right-sized: Kali decomposes, pillars execute, Kali verifies |
| **`@makali` council** | You need explicit decomposition + parallel build+run, then synthesis | Medium (3 inferences) | Balanced, multi-perspective |
| **`@makali` council** | You need explicit decomposition + parallel build+run, then synthesis | Medium (3 inferences) | Balanced, multi-perspective |
| **`/council-local`** | You want full sovereignty — local models for all three voices | Medium-High (3 local inferences) | Max sovereignty, full offline |
| **`/council-cloud`** | Default. All three on session model (whatever user selected) | High (3 cloud inferences) | Max quality, max context |
| **`/council-fast`** | Latency-critical. All three on local `qwen3-1.7b` | Low (3 local inferences) | Min latency, max sovereignty |

### The Dual-Inference Mandate (D118)

**Default behavior**: Session model — fast, simple, non-negotiable (Mandate 7).
**Opt-in local routing**: Use `oracle_summon_local(entity_name, query, model)` to route
a specific entity to a specific local model. The entity's IWAD personality, soul,
and memory remain the same; only the inference backend is overridden.

**The Mentorship Pattern**: Local model does execution, cloud model reviews.
- Example: `@roc_racoon` (local `rocracoon-3b-instruct`) writes the heritage report to
  `data/entities/roc_racoon/workspace/`. `@verity` (on session model) reviews the report
  against M14 (Heritage Vetting) and approves/rejects.

**Engine-Stack Firewall (M2) Compliance**: The `model_override` parameter is the **only**
cross-stack contract. `src/omega/oracle/oracle.py` never imports from `config/wads/`
or hardcodes any model name. The IWAD's `entities.yaml` is the source of truth for
default routing; `model_override` is a runtime concern.

---

## 🎯 OpenCode Workflow

### Before Starting Work
1. Read `OMEGA_ENGINE.md` for current engine state
2. Read `SOVEREIGN_MANDATES.md` for non-negotiable rules (14 mandates, M1-M14, v3.1.0)
3. Read `docs/strategy/HIVEMIND_PROTOCOL.md` if multi-agent or parallel work
4. Read `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` if launching a subagent
5. **Check Hivemind awareness**: `omega-hub_hivemind_get_awareness()` — who's already working?
6. **If parallel/multi-agent work**: Write workspace lock at `data/coordination/{YOU}_WORKSPACE_LOCK_{YYYYMMDD}.md` BEFORE any file edits
7. **Post Hivemind context**: `omega-hub_hivemind_post_context(...)` to declare your presence
8. Run `make test` to verify baseline (855 tests must pass)

### During Work
- Use `replace_in_file` for targeted edits, `write_to_file` for new files
- Prefer `source .venv/bin/activate && <command>` for Python operations
- Group imports: stdlib → third-party → local. Use relative imports within packages.
- For any non-trivial change, mentally check T1-T11 gates (Temple-Grade / Mandate 13)
- **Append to live feed** after each major task: `data/coordination/{YOU}_LIVE_FEED.md`
- **Heartbeat every 5-10 min** for long-running operations: `omega-hub_hivemind_heartbeat(channel="opencode", entity="{you}")`
- **Monitor hardware**: If task runs >5s, call `omega-hub_get_hardware_stats()` to diagnose — look for 4-core inference, OOM pressure, or I/O wait

### After Completing Work
1. Run `make test` — all 855 tests must pass
2. Run `make temple-grade` — verify T1-T11 gates hold (Mandate 13)
3. Run `make heritage-map` — verify [id-soft:] heritage tag coverage
4. Run `make sovereignty` — confirm local/cloud ratio didn't regress
5. **Distill L1→L2→L3 to proposed_lessons.yaml** (Mandate 11, Soul Architecture v6.1) — non-negotiable. L3 principles go to `proposed_lessons.yaml` (blind staging), NOT directly into `soul.yaml`. See `docs/strategy/SOUL_ARCHITECTURE_PROTOCOL.md`.
6. **Append final entry to live feed**: `[{timestamp}] SPRINT-N COMPLETE — {summary}`
7. `git add -A && git commit` with proper prefix
8. `git push origin main`
9. Update `OMEGA_ENGINE.md` Current State table if metrics changed

---

## 📋 Coding Standards

- **Async**: Always use `anyio` (not `asyncio`)
- **Config**: YAML-only for entity/model config — never PostgreSQL
- **Packages**: ALWAYS use a venv (`source .venv/bin/activate`). NEVER `--break-system-packages`.
- **Environment Integrity**: Mandate absolute path binary calls (e.g., `.venv/bin/pip`) instead of `source activate` to prevent base-environment pollution.
- **Testing**: Run `make test` after every change. All 855 tests must pass.
- **Type hints**: Use Python 3.12+ typing (no `from __future__`)
- **Imports**: Group: stdlib → third-party → local. Use relative imports within packages.
- **Docstrings**: Google-style. Preserve existing docstrings unless directly modifying that function.
- **Commits**: Prefix with `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `ci:`, `chore:`

---

## 🔮 Entity Usage

- Default entity: **SOPHIA** (general/wisdom)
- Switch entities per-task, not per-session
- Use `omega summon EntityName "query"` for direct entity invocation
- Use `omega talk "query"` for auto-routed queries

---

## 🎯 Key Commands

```bash
source .venv/bin/activate        # ALWAYS use the venv
make test                         # Check output for test count
make temple-grade                 # 🏛️ T1-T11 gates (Mandate 13)
make heritage-map                 # 🔖 Verify [id-soft:] heritage tag coverage
make sovereignty                  # 📊 Local/cloud inference ratio
make lint                         # flake8 code quality check
make demo                         # End-to-end demo
make health                       # Provider & model dashboard
make repl                         # Interactive REPL
omega talk "hello"                # Test oracle
omega summon Ma'at "status"       # Direct entity invocation
```

---

## 🔗 Cross-Platform Integration

The Omega Engine supports **multiple AI coding platforms** through the Omega Hub MCP server (`:8016/sse`).

### Platform Roles

| Platform | Role | Why |
|----------|------|-----|
| **OpenCode** (Primary) | Sovereign orchestration | 11 custom agents, soul evolution, Hivemind coordination |
| **Cline CLI** (Execution) | Large-context analysis | 1M+ token context, headless execution, parallel tasks |
| **VS Code / Cursor** (Visual) | Optional GUI access | MCP tools via Omega Hub for visual-preference users |

### How They Coordinate

All platforms connect to the Omega Hub MCP server and share the Hivemind:

1. **OpenCode** posts context, delegates tasks, drives soul evolution
2. **Cline** connects via `cline_mcp_settings.json`, performs deep analysis, posts results via Hivemind
3. **Any MCP client** (Cursor, VS Code, Windsurf) can use `oracle_talk`, `oracle_summon`, and Hivemind tools

**Key Rule**: OpenCode is the sovereign brain. Other platforms are execution arms. Entity state (soul.yaml, lessons) lives only in `data/entities/`. No platform should duplicate entity state.

### References
- `docs/kb/CLINE_CLI_INTEGRATION.md` — Cline setup guide
- `docs/kb/OMEGA_HUB_MULTI_PLATFORM.md` — Multi-platform config cheat sheet
- `.clinerules` — Cline CLI project rules
- `mcp_servers/omega_hub/` — Omega Hub MCP server

---

## 🔗 Key Handoff Files

- `data/handoff/STRATEGIC_FINAL_REPORT_TEMPLE_GRADE_20260602.md` — Temple-Grade directive + H1.5 plan
- `data/handoff/CLINE_M3_RESPONSE_TO_DOOM_GUY_TIER2_20260602.md` — Tier 2 Task→Agent→Model→Risk recommendations
- `data/handoff/HANDOFF_ARTISAN_TO_OPENCODE_M3_REVIEW_20260602.md` — Full codebase map (1M→200K)
- `data/handoff/handoff_artisan_to_opencode_router_fix_20260601.md` — MCP handshake root cause
- `data/handoff/LILITH_COMPLETE_SOVEREIGN_ROADMAP_20260603.md` — Complete 7-phase strategic roadmap
- `data/handoff/KALI_INTEGRATED_SPRINT_ROADMAP_20260603.md` — Integrated Sprint 0/1 roadmap
- `data/handoff/MCP_PATH_CANONICALIZATION_20260604.md` — D116 fix: `mcp/omega_hub` → `mcp_servers/omega_hub`
- `docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md` — Protocol for launching specialized subagents
- `docs/strategy/HIVEMIND_PROTOCOL.md` — Hivemind coordination for parallel/multi-agent work
- `docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md` — Master SSOT, execution roadmap, and mandate audit
- `docs/decisions/PIVOT_LOG.md` — D1-D119 immutable architectural decisions
- `data/coordination/` — Live coordination files (workspace locks, live feeds, ACKs)

---

## 📝 After Compaction

1. Read `OMEGA_ENGINE.md` — engine state
2. Read `SOVEREIGN_MANDATES.md` — rules (14 mandates, M1-M14)
3. Read `docs/decisions/PIVOT_LOG.md` — architectural decisions
4. Read `data/handoff/STRATEGIC_FINAL_REPORT_TEMPLE_GRADE_20260602.md` — current execution state
5. Run `make test` — 855 must pass
6. Run `make temple-grade` — T1-T11 must pass

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: trc_core | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
