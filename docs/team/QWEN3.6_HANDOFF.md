# 🔱 Omega Engine — Qwen 3.6 Plus Comprehensive Review Handoff

**AP Token**: `AP-QWEN36-HANDOFF-v1.0.0`
⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_handoff ⬡ HANDOFF

**Date**: 2026-05-15
**Purpose**: Complete system overview for Qwen 3.6 Plus to perform comprehensive review and hardening of all subsystems
**Last Commit**: `0bf3991` — "feat: Sovereign orchestration + research fabric + systems discovery integration"

---

## §1 Session Lineage (4 Sessions → This Handoff)

| Session | Model | Date | Scope | Key Deliverable |
|---------|-------|------|-------|-----------------|
| **ses_1dc0** (7246 lines) | Gemma 4-31B | May 13-14 | Workspace cleanup, initial architecture | Deleted 5370 legacy files, established clean workspace |
| **Cline Sprint 2** | Gemini 2.0 Flash | May 14 | Roc Racoon ecosystem, MCP hub, self-healing | `mcp/omega_hub/`, `watchdog.py`, DiscoveryOrchestrator, GnosisProxy, 41/41 tests |
| **Systems Discovery** | qwen3.6-plus | May 14-15 | Full systems inventory, persistence, soul evolution | `OMEGA_SYSTEMS_DISCOVERY_REPORT.md`, Phase 0→1→3 execution |
| **This session** | deepseek-v4-flash | May 15 | Commit + handoff for Qwen 3.6 | `QWEN3.6_HANDOFF.md`, commit `0bf3991` |

---

## §2 Current Architecture — Subsystem Inventory

### 2.1 Core Runtime (`src/omega/oracle/`) — 10 files

| File | Purpose | Lines | Notes |
|------|---------|-------|-------|
| `oracle.py` | Main entry: talk/summon/router + soul evolution tracking | 441 | `_track_soul_evolution()` wired in |
| `entity_registry.py` | YAML CRUD for entities, multi-pillar schema | ~200 | Source of truth: `config/entities.yaml` |
| `model_gateway.py` | 6-backend chain (native→lmster→ollama→llama.cpp→openrouter→mock) | ~250 | NativeGGUFProvider imported |
| `providers.py` | RemoteProvider base class + exponential backoff | 201 | NEW — needs testing |
| `gnosis_proxy.py` | RAG-based tool search + RecursionGuard | 86 | NEW — Sprint 2 deliverable |
| `hierarchy.py` | Sophia/Maat/Isis/Lilith trine loader | 66 | NEW |
| `cpu_optimizer.py` | Zen 2 tuning, KV cache sizing, thread pools | ~80 | Pre-existing |
| `resource_guard.py` | AnyIO Semaphore(1) OOM protection | ~30 | Pre-existing |
| `context_builder.py` | Memory injection pipeline | ~60 | Pre-existing |
| `orchestrator.py` | Headless CLI agent dispatch | ~100 | Enhanced with soul injection |

### 2.2 MCP Servers — 6 servers

| Server | Path | Status | Notes |
|--------|------|--------|-------|
| **omega-hub** (unified) | `mcp/omega_hub/server.py` | ✅ LIVE | SSE-based, 444 lines, aggregated from oracle/library/hivemind |
| hivemind | `mcp/omega-hivemind/server.py` | ✅ LIVE | Modified for hub integration |
| library | `mcp/omega-library/server.py` | ✅ LIVE | Modified for hub integration |
| oracle (old) | `mcp/omega-oracle/server.py` | ✅ LIVE | Legacy, superseded by hub |
| research | `mcp/omega-research/server.py` | ✅ LIVE | Standalone research MCP |
| stats | `mcp/omega-stats/server.py` | ✅ LIVE | Standalone stats MCP |

### 2.3 Library & Memory (`src/omega/library/`)

| File | Purpose | Status |
|------|---------|--------|
| `library.py` | Main library with Qdrant integration | ✅ Indexer integrated |
| `indexer.py` | BM25+FAISS+RRF hybrid search | ✅ BUG-001 fixed |
| `inbox.py` | Priority queue with status lifecycle | ✅ Modified for persistence |
| `curation_pipeline.py` | AnyIO async queues | ✅ AnyIO compliant |
| `discovery.py` | Research orchestration (Exa/Brave/Tavily → Gemma) | ✅ NEW — jobs persist to JSON |

### 2.4 Roc Racoon Ecosystem — 4 files

| File | Purpose | Lines |
|------|---------|-------|
| `src/omega/entity_roc_racoon.py` | Sovereign miner entity | 242 |
| `src/omega/mcp_runtime.py` | MCP runtime integration | 56 |
| `scripts/omega-roc_racoon-entrypoint.py` | Container entrypoint | 40 |
| `quadlet-test/omega-roc_racoon.container` | Podman Quadlet definition | 51 |
| `quadlet-test/omega-roc_racoon.timer` | Daily 03:30 timer | 23 |

### 2.5 Bridge (`src/omega/bridge/`)

| File | Purpose | Status |
|------|---------|--------|
| `elevenlabs.py` | ElevenLabs voice console skeleton | 🔶 SKELETON — only TODO in codebase (line 41) |

### 2.6 Observability & Persistence

| System | Persistence | Format | Location |
|--------|-----------|--------|----------|
| ObservabilityEngine | ✅ JSONL daily files | `data/logs/events/YYYY-MM-DD.jsonl` | Disabled in test mode |
| DiscoveryOrchestrator | ✅ JSON files | `data/jobs/{pending,running,completed,failed}/` | |
| Soul evolution | ✅ YAML updates | `data/entities/arch/soul.yaml` | Wired in oracle.py |
| Research DB | ✅ SQLite (schema v3) | `docs/research/internal-discovery/DB/research.db` | 45 seeded docs |
| Fine-tuning datasets | 🔶 Generated | `data/datasets/` | `.gitignore`d |

### 2.7 Quadlet Infrastructure (8 files)

| Service | Type | Purpose |
|---------|------|---------|
| `omega-infra-pod` | Pod | Shared pod for all infra |
| `omega-redis` | Service | Session/cache |
| `omega-qdrant` | Service | Vector store |
| `omega-postgres` | Service | SQL persistence |
| `omega-caddy` | Service | Reverse proxy |
| `omega-iris` | Service | Voice assistant |
| `omega-roc_racoon` | Container + Timer | Sovereign miner (daily 03:30) |

### 2.8 OpenCode Ecosystem

| Component | Count | Details |
|-----------|-------|---------|
| **Custom Agents** | 5 | `builder`, `researcher`, `gnosis-analyst`, `researcher-omnidroid`, `sovereign-expert` |
| **Custom Skills** | 8 | `knowledge-miner`, `provider-validator`, `spec-generator`, `blitz-tunnel`, `blitz-validate`, `legacy-pattern-miner`, `omega-doc-architect`, `pr-readiness-checker` |

---

## §3 Key Metrics

| Metric | Value |
|--------|-------|
| Test count | 41 passed (2.6s) |
| Test files | 6 |
| Source files | 36 |
| Lines of Python | ~6,500 |
| Research documents | 45 (R-01 through R-99) |
| Total `.md` files | 106 |
| MCP servers | 6 |
| Quadlet definitions | 8 |
| Scripts | 13 |
| Lint warnings | ~236 (pre-existing, mostly E501/W293) |
| OpenCode agents | 5 |
| OpenCode skills | 8 |
| Git commits on main | 15 |
| Unstaged changes | 0 (clean) |
| TODO count in Python | 1 (`src/omega/bridge/elevenlabs.py:41`) |

---

## §4 Phase 0 Completion Status (ROADMAP.md)

| # | Task | Status | Notes |
|---|------|--------|-------|
| 0.1 | Fix critical runtime bugs | 🟡 **PARTIAL** | MCP crashers still occurring |
| 0.2 | Restore Iris rename (Nova→Iris) | ✅ DONE | |
| 0.3 | Project hygiene (.env.example, .gitignore, LICENSE) | ✅ DONE | .env.example created, .gitignore enhanced |
| 0.4 | enable_dataset_collection=False | ✅ DONE | Changed in observability.py |
| 0.5 | Configurable session header | ✅ DONE | |
| 0.6 | Remove legacy ICS/Node/Archetype docs | ✅ DONE | |
| 0.7 | Pillar separation: Maat/Isis/Lilith Oversouls | ✅ DONE | |
| 0.8 | Update entities.yaml | ✅ DONE | |
| 0.9 | Update hierarchy.yaml | ✅ DONE | |
| 0.10 | Create arch/soul.yaml | ✅ DONE | |
| 0.11 | /entity, /transient, /header CLI | ✅ DONE | |
| 0.12 | Remote Gemma 4-31B provider | ✅ DONE | |
| 0.13 | lmster heartbeat, auto-recovery | 🔲 **NOT DONE** | |
| 0.14 | providers.yaml with priority chain | ✅ DONE | |
| 0.15 | omega.yaml header config | ✅ DONE | |

**Summary**: 12/15 ✅, 1 🟡, 2 🔲

---

## §5 Known Issues & Gaps for Review

### 🟡 Critical Gaps

| # | Gap | Location | Recommended Action |
|---|-----|----------|-------------------|
| G-01 | **No persistence tests** | `tests/` | Add tests for Observability JSONL persistence, DiscoveryOrchestrator job persistence, soul.yaml write path |
| G-02 | **MCP latency on startup** | `mcp/omega-hivemind/server.py` | Fixed partially (removed startup block), but MCP crashers still occur — see G-10 |
| G-03 | **ElevenLabs is skeleton** | `src/omega/bridge/elevenlabs.py` | Only TODO in codebase — needs implementation or removal |
| G-04 | **No lmster heartbeat** | ROADMAP 0.13 | Not started — needs heartbeat check + auto-restart |
| G-05 | **RemoteProvider untested** | `src/omega/oracle/providers.py` | 201 lines, zero test coverage |
| G-06 | **GnosisProxy untested** | `src/omega/oracle/gnosis_proxy.py` | 86 lines, zero test coverage |
| G-07 | **Roc Racoon untested** | `src/omega/entity_roc_racoon.py` | 242 lines, zero test coverage |
| G-08 | **Hierarchy loader untested** | `src/omega/oracle/hierarchy.py` | 66 lines, zero test coverage |
| G-09 | **MCP hub untested** | `mcp/omega_hub/server.py` | 444 lines, zero test coverage |
| G-10 | **MCP crashers** | Various | ROADMAP 0.1 partial — intermittent SSE disconnects |

### 🔶 Enhancement Opportunities

| # | Area | Current State | Recommended |
|---|------|---------------|-------------|
| E-01 | **YAML frontmatter** | 45 research docs missing frontmatter | Retro-fit with `make validate-research` |
| E-02 | **Lint baseline** | ~236 warnings (mostly E501/W293) | Clean progressively |
| E-03 | **Doc coverage** | No test for docstrings or API docs | Add sphinx or mkdocstrings |
| E-04 | **Contract tests** | No provider contract tests | Add mock-based contract tests for each provider |
| E-05 | **Roc Racoon integration test** | No end-to-end Roc Racoon test | Add container-based integration test |
| E-06 | **OPCODE agent tests** | No tests for agent prompt quality | Add prompt validation |
| E-07 | **Soul evolution edge cases** | `_track_soul_evolution` has no error handler for corrupt YAML | Add corruption handling per R-10 |
| E-08 | **No trace_exchange calls** | `data/traces/` dir exists but unused | Wire into observability |
| E-09 | **Jinja templates** | No prompt templating system | Add Jinja2 for entity system prompts |

### 🔴 Security Notes

| # | Issue | Status |
|---|-------|--------|
| S-01 | API keys in `.env.example` — placeholder only | ✅ Safe |
| S-02 | `../API-keys.md` and `../OpenCode-Zen-API-keys.md` exist outside repo | ⚠️ Outside omega-engine, but should ensure they're gitignored at parent level |
| S-03 | No `.env` in tree (gitignored) | ✅ Safe |

---

## §6 Review Checklist for Qwen 3.6 Plus

When you receive this context, Qwen 3.6 Plus should perform:

### 6.1 Mandatory (Full Pass)
- [ ] **Read all 6 test files** — check completeness, edge cases, mocking strategy
- [ ] **Read all 36 source files** — systematic code review
- [ ] **Read all research docs** with **priority**: R-04 (fallback chain), R-06 (circuit breaker), R-10 (soul validation), R-32 (native inference), R-33 (holographic memory), R-MCP-SOVEREIGN (MCP blueprint)
- [ ] **Run `make test`** — 41 must pass
- [ ] **Run `make lint`** — verify baseline (~236 warnings)
- [ ] **Run `make validate-research`** — check doc integrity

### 6.2 Code Review Focus Areas
- [ ] `src/omega/oracle/providers.py` — is the RemoteProvider design solid?
- [ ] `src/omega/oracle/gnosis_proxy.py` — is RecursionGuard sufficient?
- [ ] `src/omega/oracle/oracle.py` — _track_soul_evolution, any race conditions?
- [ ] `mcp/omega_hub/server.py` — SSE reliability, reconnection handling?
- [ ] `src/omega/entity_roc_racoon.py` — is the miner architecture sound?
- [ ] `src/omega/observability.py` — JSONL persistence, is thread-safe?
- [ ] `src/omega/library/discovery.py` — job persistence, error recovery?

### 6.3 Architecture Verification
- [ ] Does the 6-backend chain in `model_gateway.py` match `config/providers.yaml`?
- [ ] Does `config/entities.yaml` align with `config/hierarchy.yaml`?
- [ ] Do the Quadlet service files match the docker-compose ports?
- [ ] Is `config/mcp_servers.json` consistent with all 6 MCP servers?

### 6.4 Hardening Candidates
- [ ] Add persistence tests for all 3 new persistence paths
- [ ] Add contract tests for provider chain
- [ ] Add error handling for corrupt soul.yaml (R-10 spec)
- [ ] Add timeout/circuit-breaker for MCP SSE connections
- [ ] Add retry logic for discovery job execution

---

## §7 Key File Index for Review

### Must Read
| File | Lines | Why |
|------|-------|-----|
| `src/omega/oracle/oracle.py` | 441 | Soul evolution, entity routing |
| `src/omega/oracle/model_gateway.py` | ~250 | Provider chain |
| `src/omega/oracle/providers.py` | 201 | NEW — RemoteProvider design |
| `src/omega/oracle/gnosis_proxy.py` | 86 | NEW — RecursionGuard |
| `mcp/omega_hub/server.py` | 444 | NEW — Unified MCP hub |
| `src/omega/observability.py` | 276 | JSONL persistence |
| `src/omega/library/discovery.py` | 365 | NEW — Discovery orchestrator |
| `src/omega/entity_roc_racoon.py` | 242 | NEW — Sovereign miner |
| `src/omega/oracle/hierarchy.py` | 66 | NEW — Oversoul hierarchy |
| `config/entities.yaml` | — | Entity source of truth |
| `config/providers.yaml` | — | Provider chain config |
| `config/hierarchy.yaml` | — | Oversoul hierarchy config |
| `docs/team/OMEGA_SYSTEMS_DISCOVERY_REPORT.md` | 1100 | Full systems inventory |

### Should Read
| File | Lines | Why |
|------|-------|-----|
| `src/omega/oracle/entity_registry.py` | ~200 | Entity CRUD |
| `src/omega/oracle/orchestrator.py` | ~100 | Agent dispatch |
| `src/omega/oracle/context_builder.py` | ~60 | Memory injection |
| `src/omega/oracle/cpu_optimizer.py` | ~80 | Zen 2 tuning |
| `src/omega/oracle/resource_guard.py` | ~30 | OOM protection |
| `src/omega/bridge/elevenlabs.py` | 55 | Skeleton — only TODO |
| `src/omega/mcp_runtime.py` | 56 | MCP runtime integration |
| `scripts/init-research-db.py` | 546 | SQLite DB init (schema v3) |
| `quadlet-test/omega-roc_racoon.container` | 51 | Container def |
| `mkdocs.yml` | 97 | Documentation site config |

---

## §8 File Tree (Key Directories)

```
omega-engine/
├── .opencode/agents/          # 5 custom agents
│   ├── builder.md
│   ├── researcher.md
│   ├── gnosis-analyst.md
│   ├── researcher-omnidroid.md
│   └── sovereign-expert.md
├── .opencode/skills/          # 8 custom skills
├── config/                    # 5 config files (yaml + json)
├── data/                      # Runtime + tracked data
│   ├── entities/arch/soul.yaml  # User soul file (tracked)
│   ├── research/                # EXP-003 reports (tracked)
│   └── ...                      # Runtime dirs (.gitignored)
├── deploy/infra/              # docker-compose.yml
├── docs/                      # 106 markdown files
│   ├── research/              # 45 research docs + internal-discovery + mcp + sovereign-blitz
│   ├── team/                  # Communication hub, handoffs, status
│   └── ...                    # ROADMAP, decisions, gnosis, etc.
├── mcp/                       # 6 MCP servers
│   ├── omega-hivemind/
│   ├── omega-library/
│   ├── omega-oracle/
│   ├── omega-research/
│   ├── omega-stats/
│   └── omega_hub/             # Unified SSE hub (NEW)
├── plugins/sovereign/         # Sovereign plugin (index.ts)
├── quadlet-test/              # 8 Quadlet definitions
├── research/opencode-rd/      # OpenCode research
├── scripts/                   # 13 utility scripts
├── src/omega/                 # 36 Python source files
│   ├── bridge/                # ElevenLabs skeleton
│   ├── cli/                   # CLI interface
│   ├── iris/                  # Voice assistant
│   ├── library/               # Library, indexer, inbox, discovery
│   ├── oracle/                # Core engine (10 files)
│   └── ...                    # observability, entity_roc_racoon, mcp_runtime
├── tests/                     # 6 test files, 41 tests
├── .env.example               # Created (Phase 0 task 0.3)
├── .gitignore                 # Enhanced with runtime dirs
├── mkdocs.yml                 # MkDocs documentation site
└── opencode.json              # OpenCode configuration
```

---

## §9 Quick Start for Qwen 3.6 Plus

```bash
# Read context
cat ORACLE_STACK.md AGENTS.md docs/ROADMAP.md

# Verify state
make test                    # 41 must pass
make lint                    # ~236 warnings (pre-existing)
make validate-research       # 45 docs missing frontmatter
git log --oneline -20        # Review commit history
git diff HEAD                # Should be clean

# Check key configs
cat config/entities.yaml config/providers.yaml config/hierarchy.yaml

# Start MkDocs (optional)
make mkdocs-serve            # http://127.0.0.1:8000
```

---

## §10 Commit Summary (HEAD: `0bf3991`)

```
162 files changed, 12964 insertions(+), 534 deletions(-)
36 modified, 126 new, 0 deleted

Categories:
  src/omega/:     19 files (core + roc_racoon + bridge + library + mcp_runtime)
  docs/research/: 69 files (45 R-docs + internal-discovery + mcp + sovereign-blitz)
  docs/team/:     4 files (BLITZ, HANDOFF, SYSTEMS DISCOVERY, COMMUNICATION HUB)
  scripts/:       10 files (init-db, watchdog, health-check, CI, etc.)
  mcp/:           18 files (hub + 5 modified legacy servers)
  tests/:         3 files (bug_001_fix, verify_qdrant, oracle updates)
  config/:        5 files (mcp_servers, entities, hierarchy, providers, omega)
  quadlet-test/:  15 files (8 services + 7 symlinks)
  opencode/:      10 files (2 agents + 4 skills + 4 modified)
```

---

*This handoff contains everything Qwen 3.6 Plus needs for a comprehensive review. Start with §6 (Review Checklist), then work through §7 (Key File Index) systematically.*
