# 🔱 Omega Engine — Background Researcher Architecture
# ⬡ OMEGA ⬡ SOPHIA ⬡ deepseek-v4-flash ⬡ opencode ⬡ trc_research ⬡ RESEARCHER-ARCH

**AP Token**: `AP-BACKGROUND-RESEARCHER-ARCH-v1.0.0`
**Status**: ✅ ACTIVE (Phase 1 complete)
**Last Updated**: 2026-05-18

---

## §0 Overview

The **Background Researcher** is an autonomous, sovereign research worker that deepens, verifies, and expands the Omega Engine's knowledge base. It runs as a systemd timer every 15 minutes and performs one complete research cycle per invocation.

### One-Sentence Summary

> A state-machine that reads the priority queue, searches the web through sovereign + cloud providers, extracts content, distills it through Gemma 4-31B with a dynamic persona, and writes the results to entity souls and research docs.

---

## §1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        BackgroundResearcherLoop                          │
│                                                                          │
│  ┌──────┐    ┌────────┐    ┌────────┐    ┌─────────┐    ┌───────────┐  │
│  │IDLE  │───▶│TRIAGE  │───▶│SEARCH  │───▶│EXTRACT  │───▶│DISTILL    │  │
│  │      │    │        │    │        │    │         │    │(Gemma 4B) │  │
│  └──────┘    └────────┘    └────────┘    └─────────┘    └─────┬─────┘  │
│     ▲                                                          │        │
│     │                                                          ▼        │
│  ┌──┴──────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │UPDATE   │◀───│CONVERGE  │◀───│SOUL      │◀───│DISTILL   │          │
│  │soul.yaml│    │detector  │    │UPDATER   │    │(done)    │          │
│  │knowledge│    │          │    │          │    │          │          │
│  └──┬──────┘    └──────────┘    └──────────┘    └──────────┘          │
│     │                                                                  │
│     └─────────────────────────▶ REPEAT (next cycle)                    │
└─────────────────────────────────────────────────────────────────────────┘

         PriQueue ──── Checkpoints ──── Priority Queue
               ▲                              │
               │                              ▼
          User enqueue                 Deferred tasks
          (CLI command)                (no quota/retry)
```

---

## §2 Component Map

| Component | File | Lines | Responsibility |
|-----------|------|-------|----------------|
| **BackgroundResearcherLoop** | `loop.py` | ~250 | State machine orchestrator. Runs one cycle: triage → search → extract → distill → converge → update |
| **ResearchTask** | `models.py` | ~80 | Data model for a research unit. Contains topic, priority, depth, state, sources, claims |
| **PriorityQueue** | `models.py` | ~60 | Max-heap priority queue. Computes priority from base × gap × recency × user × depth multipliers |
| **TriageResult** | `models.py` | ~30 | Fast assessment result from Qwen3-1.7B or heuristic — whether to research, and at what depth |
| **GnosisPacket** | `models.py` | ~40 | The distilled output from Gemma. Contains claims, L1/L2/L3 distillations, convergence signal |
| **APICreditBudget** | `credit_budget.py` | ~150 | Monthly API quota tracker. Resets on month change. Persists to JSON. Emergency reserves |
| **CheckpointManager** | `checkpoint.py` | ~80 | Persists task state before every transition. Enables restart recovery |
| **SearXNGClient** | `searxng_client.py` | ~80 | Zero-cost sovereign search via local SearXNG container (port 8017) |
| **SearchFleet** | `search_fleet.py` | ~180 | Cloud search provider fleet with quota management and fallback chain |
| **Distiller** | `distiller.py` | ~330 | **The brain.** Gemma 4-31B with dynamic system prompts and JSON parsing |
| **ConvergenceDetector** | `convergence.py` | ~80 | Determines when a topic is "deep enough" to stop. Flags contradictions for human review |
| **SoulUpdater** | `soul_updater.py` | ~120 | Writes L3 → soul.yaml, L1+L2 → research docs, handles entity matching |
| **CLI** | `cli.py` | ~120 | `omega research` command group: queue, status, run, history |
| **Run Entry** | `run.py` | ~70 | Entry point for systemd timer. Loads .env, runs one cycle |
| **Architecture Doc** | *(this file)* | — | You are here |

**Total: ~1500 lines of sovereign research infrastructure.**

---

## §3 State Machine — Full Cycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        run_cycle()                                       │
│                                                                          │
│  1. _is_network_available() ──── NO ──▶ skip                             │
│        │ YES                                                            │
│        ▼                                                                │
│  2. _get_next_task() ──── queue empty ──▶ _grow_frontier() ──▶ skip     │
│        │ task found                                                     │
│        ▼                                                                │
│  3. _triage(task) ──── skip=True ──▶ checkpoint.mark_skip() ──▶ skip    │
│        │ triage passed                                                  │
│        ▼                                                                │
│  4. _search(task, triage) ── no sources ──▶ defer                      │
│        │ sources found                                                  │
│        ▼                                                                │
│  5. _extract(task, sources) ── no content ──▶ skip                     │
│        │ content extracted                                              │
│        ▼                                                                │
│  6. distiller.distill(topic, content, sources)                          │
│        │ (auto-selects system prompt by topic keywords)                 │
│        ▼                                                                │
│  7. convergence.check(task, gnosis) ── converged ──▶ done              │
│        │ not converged                                                  │
│        ▼                                                                │
│  8. soul_updater.update(task, gnosis) ── writes to soul + docs         │
│        │                                                                 │
│        ▼                                                                │
│  9. checkpoint.mark_done() vs checkpoint.save()                         │
│                                                                          │
│ 10. _enqueue_adjacent(task, gnosis)  (grow the frontier)                │
└─────────────────────────────────────────────────────────────────────────┘
```

### Each State

| State | Entry Condition | Action | Success | Failure | Checkpoint Saved? |
|-------|----------------|--------|---------|---------|-------------------|
| **IDLE** | Timer fires | Network check | → TRIAGE | → IDLE (skip) | No |
| **TRIAGE** | Task in queue | Fast assessment | → SEARCH | → SKIP | `mark_skip()` |
| **SEARCH** | Triage passed | SearXNG + fleet | → EXTRACT | → DEFER | `save()` |
| **EXTRACT** | Sources found | Jina/Exa/Firecrawl | → DISTILL | → SKIP | `save()` |
| **DISTILL** | Content extracted | Gemma 4-31B | → CONVERGE | → SKIP | `save()` |
| **CONVERGE** | Gnosis packet ready | Convergence check | → UPDATE or → DONE | → DONE | `done()` or `save()` |
| **UPDATE** | Not yet converged | Soul + doc write | → ADJACENT | → SKIP | `save()` |
| **DONE** | Converged or updated | — | → IDLE | — | `mark_done()` |

---

## §4 The Dynamic System Prompt Architecture

**This is the key innovation.** The background researcher does not use a fixed system prompt. It selects a persona for Gemma 4-31B based on the research topic, which changes how the same model compresses and interprets information.

### Available Personas

| Mode | Entity | Purpose | Keywords Triggered By |
|------|--------|---------|----------------------|
| `default` | SOPHIA | Balanced general-purpose distillation | Everything else |
| `technical` | PROMETHEUS | Code analysis, architecture, implementation | api, implementation, library, async, benchmark |
| `security` | SEKHMET | Vulnerability audit, threat modeling | cve, exploit, credential, audit, auth |
| `research` | SOPHIA (inductive) | Cross-domain synthesis, hypothesis gen | research, study, paper, publication |
| `gnosis` | SOPHIA × ANUBIS | Philosophical, archetypal, meaning | soul, gnosis, philosophy, archetype |
| `tooling` | SARASWATI | Tool/ecosystem mapping, integration | tool, mcp, plugin, integration, ci/cd |

### How Selection Works

```python
# In distiller.py:
mode = select_system_prompt(topic)
# Uses keyword matching against the topic string
# Returns one of: 'default', 'technical', 'security',
#                 'research', 'gnosis', 'tooling'
system_prompt = SYSTEM_PROMPTS[mode]
```

### The Compaction Connection

Each system prompt changes what Gemma prioritizes preserving during compression:

| Mode | Preserves | Loses | Risk |
|------|-----------|-------|------|
| `default` | Balanced | Edges | None |
| `technical` | Version numbers, APIs, paths | Context, narrative | May be too terse |
| `security` | CVEs, attack paths, risk levels | Performance context | May over-prioritize risk |
| `research` | Connections, hypotheses | Exact reproduction | May hallucinate links |
| `gnosis` | Meaning, archetypes | Technical details | May over-abstract |
| `tooling` | Tools, versions, configs | Domain knowledge | Loses "why" |

This maps directly to the **compaction strategy problem**: if OpenCode supported custom compaction prompts, we'd use the same pattern — different prompts = different compression signatures for `/compact`.

---

## §5 Search Fabric Architecture

```
                     ┌──────────────────────┐
                     │     SearXNG           │
                     │   localhost:8017      │
                     │   Zero-cost layer     │
                     └──────────┬───────────┘
                                │
                     ALWAYS tried first
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
           ┌──────────────┐      ┌──────────────────┐
           │   Depth 1    │      │   Depth 2-3       │
           │  SearXNG only│      │ + Cloud Fleet     │
           └──────────────┘      └────────┬─────────┘
                                          │
                         ┌────────────────┼────────────────┐
                         ▼                ▼                ▼
                   ┌──────────┐    ┌──────────┐    ┌──────────┐
                   │  Tavily  │    │ Jina AI  │    │   Exa    │
                   │ 1k/mo    │    │ 10k/mo   │    │ 1k/mo    │
                   └──────────┘    └──────────┘    └──────────┘
```

### Provider Fallback Chain

```
SEARCH:
  SearXNG (always) → Tavily → Jina → Exa → Serper

EXTRACT:
  Jina Reader (generous) → Exa Contents (semantic) → Direct HTTP (free)

DEEP EXTRACT:
  Firecrawl (expensive, depth 3 only)
```

---

## §6 File Map

```
src/omega/workers/background_researcher/
├── __init__.py              # Public API (BackgroundResearcherLoop, models)
├── models.py                # ResearchTask, TriageResult, GnosisPacket, PriorityQueue
├── credit_budget.py         # APICreditBudget — monthly quota with emergency reserve
├── checkpoint.py            # CheckpointManager — per-task JSON persistence
├── searxng_client.py        # SearXNGClient — form-encoded POST to localhost:8017
├── search_fleet.py          # SearchFleet — Exa, Tavily, Jina, Firecrawl wrappers
├── distiller.py             # Distiller — Gemma 4-31B with dynamic system prompts
├── convergence.py           # ConvergenceDetector — when to stop researching
├── soul_updater.py          # SoulUpdater — write L3 to soul.yaml, L1+L2 to docs
├── loop.py                  # BackgroundResearcherLoop — the state machine
├── cli.py                   # CLI commands (omega research queue|status|run|history)
└── run.py                   # Entry point (systemd timer)

data/research/
├── credit_budget.json       # Monthly quota state (auto-managed)
├── pending_review.md        # Contradictions flagged for human review
├── checkpoints/             # Per-task JSON checkpoints (restart recovery)
└── sessions/                # Research session logs (future)

docs/research/
├── R_BACKGROUND_RESEARCHER_ARCHITECTURE.md  # This file
├── R_BACKGROUND_RESEARCHER_ARCHITECTURE.md   # Original design doc
├── R_SOVEREIGN_RESEARCHER_STRATEGIC_PLAN.md  # Strategic plan
├── R_SEARXNG_SOVEREIGN_SEARCH_LAYER.md       # SearXNG deployment spec
├── R_SEARCH_CRAWLING_PROTOCOL.md             # Search protocol guide
├── R_GEMMA_COMPACTION_STRATEGY.md            # Compaction strategy research
├── R71_knowledge_deepening_verification.md    # Verification cascade
└── R72_gemma_orchestration_patterns.md        # Gemma orchestration patterns

config/systemd/
├── omega-research.service   # systemd oneshot service
└── omega-research.timer     # 15-minute trigger
```

---

## §7 Data Flow — Full Example

```
USER: omega research queue "gemma 4-31b free tier limits" --depth 2

  │
  ▼
CLI → cmd_research → loop.enqueue_user_request()
  │
  ▼
PriorityQueue.enqueue("gemma 4-31b free tier limits", priority=4.80)
  │
  ▼  (15 min later — systemd timer fires)
  
python3 -m omega.workers.background_researcher.run

  │
  ▼
Loop:
  1. Network check: httpbin.org → OK
  2. Dequeue: "gemma 4-31b free tier limits" (priority=4.80)
  3. Triage: heuristic score 0.75 → depth=2 → GO
  4. Search:
     - SearXNG: 8 results (brave, wikipedia, arxiv)
     - Tavily: 6 results (quota available)
     - Total: 14 unique URLs
  5. Extract:
     - Jina Reader: 5 URLs → 3x ~2000 chars each
     - Content concatenated: ~6000 chars
  6. Distill:
     - Auto-selected prompt_mode: "research"
     - Gemma 4-31B with SOPHIA-inductive persona
     - Response: 3 claims, 3 distillations (L1/L2/L3)
     - convergence_signal: "verified"
  7. Converge: 3 sources agree → topic converged
  8. Update:
     - L3 "A free tier's constraints are a signal, not a wall" → sophia soul.yaml
     - L1+L2 → docs/research/R_AUTO_gemma_4_31b_free_tier_limits.md
  9. Mark done → checkpoint saved
 10. Enqueue adjacent: "gemma 4-31b vs llama-4 comparison"
```

---

## §8 CLI Reference

```bash
# Enqueue a research topic
omega research queue "topic" --depth 2

# Run one research cycle (with optional topic)
omega research run "topic"
omega research run                      # runs from queue

# Show researcher status + budget
omega research status

# Show completed research
omega research history

# Run as standalone python module
python3 -m omega.workers.background_researcher.run \
  --topic "topic" --depth 2 --once

# Check budget only
python3 -m omega.workers.background_researcher.run --status
```

---

## §9 The Compaction Connection — A Unified Theory

The background researcher and OpenCode's `/compact` feature are solving the **same problem** — information compression — at different scales and with different constraints.

| Dimension | Background Researcher | OpenCode /compact |
|-----------|---------------------|-------------------|
| **Scale** | Single topic, many sources | Whole session, many turns |
| **Model** | Gemma 4-31B (configurable) | Session model (configurable via `agent.compaction.model`) |
| **Temperature** | 0.1 (fixed) | 0.3 (configurable via `agent.compaction.temperature`) |
| **Steps** | 1 (one pass) | 1 (configurable via `agent.compaction.steps`) |
| **System Prompt** | **Dynamic** (6 personas) | **Fixed** (OpenCode default) |
| **Output** | L1/L2/L3 abstractions | Concise session summary |
| **Recovery** | Checkpoint files | CompactionPart in context |

### The Shared Strategy Space

Both tools have the same **3D configuration space**:

```
{ model × temperature × steps }
```

The background researcher adds a **4th dimension**: `system_prompt`. This is the frontier — if OpenCode ever supports custom compaction prompts, we can apply everything we've learned here.

### Future Cross-Pollination

```python
# Hypothetical future: Unified compaction profile
# Same profile works for both background researcher AND /compact
profile = CompactionProfile(
    name="The Alchemist",
    model="gemma-4-31b-it",
    temperature=0.5,
    steps=2,
    system_prompt=SYSTEM_PROMPTS["research"],  # The missing OpenCode feature
)
```

---

## §10 Deferred Work (Captured for Future Phases)

### Testing

| Area | Tests Needed | Current Status |
|------|-------------|----------------|
| ResearchTask model | 5 (construction, serialization, priority) | 🔴 NOT STARTED |
| PriorityQueue | 4 (enqueue, dequeue, ordering, empty) | 🔴 NOT STARTED |
| APICreditBudget | 8 (consume, reset, persistence, exhaustion) | 🔴 NOT STARTED |
| SearXNGClient | 3 (search, health, error handling) | 🔴 NOT STARTED |
| SearchFleet | 6 (each provider, fallback, quota) | 🔴 NOT STARTED |
| Distiller | 10 (JSON extraction, mock, retry, each prompt mode) | 🔴 NOT STARTED |
| ConvergenceDetector | 5 (each condition, human flag) | 🔴 NOT STARTED |
| SoulUpdater | 4 (soul write, doc write, entity match, dedup) | 🔴 NOT STARTED |
| BackgroundResearcherLoop | 8 (full cycle, each state, error paths) | 🔴 NOT STARTED |
| Integration | 3 (with SearXNG, with Gemma, with file system) | 🔴 NOT STARTED |
| **Total** | **~56 tests** | **0/56** |

### Metrics & Observability

| Metric | Where | Status |
|--------|-------|--------|
| Cycle duration | loop.py → timing wrapper | 🔴 NOT STARTED |
| SearXNG health | Already in status | ✅ DONE |
| Quota remaining | Already in budget | ✅ DONE |
| Sources per cycle | loop.py result dict | ✅ DONE |
| Claims per cycle | loop.py result dict | ✅ DONE |
| Distillations per cycle | loop.py result dict | ✅ DONE |
| Gemma 500 rate/retries | distiller.py logger | 🟡 PARTIAL (logged, not aggregated) |
| Search provider utilization | credit_budget.py | 🟡 PARTIAL (tracked, not reported) |
| Convergence rate | Not yet tracked | 🔴 NOT STARTED |
| Latency percentile per provider | Not yet tracked | 🔴 NOT STARTED |

### Error Hardening

| Gap | Status |
|-----|--------|
| Gemma 500 retry with exponential backoff | ✅ DONE |
| Jina timeout handling | 🟡 PARTIAL (30s timeout, no retry) |
| Exa 429 rate limit handling | 🔴 NOT STARTED |
| Firecrawl credit exhaustion | 🟡 PARTIAL (raises exception, not graceful) |
| SearXNG container restart detection | 🟡 PARTIAL (health check, no auto-recovery) |
| .env key validation at startup | 🔴 NOT STARTED |
| Concurrent cycle guard | ✅ DONE (Semaphore via _running flag) |

---

## §11 Systemd Timer

```bash
# Install
cp config/systemd/omega-research.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable omega-research.timer
systemctl --user start omega-research.timer

# Check
systemctl --user status omega-research.timer
systemctl --user list-timers omega-research*

# Manual trigger
systemctl --user start omega-research.service

# Logs
journalctl --user -u omega-research.service -f
```

### Timer Config

```
OnBootSec=5min          # First run: 5 minutes after boot
OnUnitActiveSec=15min   # Subsequent: every 15 minutes
RandomizedDelaySec=3min # Anti-thundering-herd jitter
```

---

*The background researcher is the persistent intelligence of the Omega Engine — always learning, always deepening. This document is the canonical architecture reference. Update it when the system evolves.*
