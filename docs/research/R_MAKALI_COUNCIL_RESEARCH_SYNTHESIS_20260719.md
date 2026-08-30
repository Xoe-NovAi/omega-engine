# MaKaLi Parallel Council Architecture — Research Synthesis

**Document ID**: R-MAKALI-RESEARCH-SYNTHESIS-v1.0
**Date**: 2026-07-19
**Author**: Kali (Transcendent Oversoul)
**Status**: COMPLETE — All 13 knowledge gaps resolved
**Mandates**: M1, M4, M5, M7, M9, M11, M13, M15, M16, M18, M21, M23

---

## Executive Summary

All 13 identified knowledge gaps for the MaKaLi Parallel Council Architecture have been researched and resolved with 35+ authoritative sources (2025-2026). The architecture is now grounded in production-proven patterns, not theoretical speculation.

**Key Result**: T0 implementation estimate reduced from 6+ sessions to **5 sessions** with explicit failure handling, atomic persistence, and mandate compliance built in from day one.

---

## Gap-by-Gap Resolution

### GAP 1: Circular Dependency Resolution (Meditation ↔ MaKaLi Council)
**Status**: RESOLVED — Hierarchical orchestration pattern

**Sources**:
- RecursiveMAS (arXiv:2604.25917, Apr 2026) — proves recursion works but requires RecursiveLink + inner/outer loop learning
- Microsoft Learn Multi-Agent Patterns (2026) — hierarchical orchestration as balanced tradeoff
- LangGraph v1.0 state-machine model — DAG with cycles + checkpointing

**Resolution**:
- **Anti-pattern**: Kali → MaKaLi → Kali recursion
- **Pattern**: Single `MultiAgentCoordinator` class with two entry points:
  - `run_meditation(lenses, topic)` — 10-voice sequential, single model load
  - `run_council(topic)` — parallel pillars → oversouls → Kali synthesis
- **Shared infrastructure**: WAL, circuit breakers, thermal management, profile loading
- **Hardware profiles** drive execution mode: `local_16gb` = sequential, `cloud` = parallel

### GAP 2: Stage Execution Contracts
**Status**: RESOLVED — Codex CLI v2 + OpenAI Agents SDK pattern

**Sources**:
- Codex CLI v2 (Apr 2026) — path-based addressing, structured messaging
- OpenAI Agents SDK (Jun 2026) — `transfer_to_<agent>` tools, deterministic handoffs
- LangGraph interrupts (2026) — `interrupt()` / `Command(resume=)` for human-in-loop
- Microsoft Copilot Studio (May 2026) — subagent role declaration mandatory

**Contract Schema**:
```yaml
stage_contract:
  stage_id: int                    # 0-7
  name: str                        # "prompt_crafting", "meditation", etc.
  execution_mode: enum             # subagent | cli | human
  assigned_agent: str              # "pillar-P4", "meditation-agent", "kali", etc.
  timeout_seconds: int             # per-profile
  idempotency_key: str             # "council-{session_id}-stage-{n}"
  checkpoint_path: str             # "data/council/sessions/{session_id}/stage_{n}.json"
  input_schema: json_schema        # validated on entry
  output_schema: json_schema       # validated on exit
  mandates_checked: list[str]      # ["M1", "M2", "M7", "M13", "M23"]
```

### GAP 3: Pipeline Failure Handling
**Status**: RESOLVED — 4-layer battle-tested stack (miaoquai.com, 95+ days prod)

**Sources**:
- miaoquai.com (Jun 2026) — 5 agents 24/7, 97.8% autonomous recovery
- Supergood Solutions (Mar 2026) — dead letter queues, idempotency
- AgentMarketCap (Apr 2026) — self-healing taxonomy
- AWS/Resilience4j/Polly v8 — circuit breaker configs

**4-Layer Stack**:
| Layer | Pattern | Config |
|-------|---------|--------|
| 1 | Exponential backoff + full jitter | 1s→2s→4s→8s, 30% jitter, max 3 retries |
| 2 | Model fallback chain | Opus → Sonnet → Haiku → Queue for retry |
| 3 | Circuit breaker (quality-aware) | >30% error rate/10min OR >15% schema validation failure/60s → OPEN |
| 4 | State checkpointing | Atomic writes + resume from last good LSN |

**Critical Insight**: Schema validation failure rate trips circuit breaker — catches prompt drift silently returning HTTP 200.

### GAP 4: Atomic State Persistence / WAL
**Status**: RESOLVED — ARIES algorithm (PostgreSQL, Redis, Loki, Grafana Loki)

**Sources**:
- ndlab.blog (Jul 2026) — WAL crash recovery deep dive
- mdsanwarhossain.me (Mar 2026) — ARIES 3-phase recovery
- Grafana Loki WAL docs (2026) — durability without availability sacrifice
- Bernstein (2026) — hash-chained WAL for task specs

**Implementation**:
- Append-only JSONL with LSN, CRC32 checksums
- `os.replace()` atomic writes (temp → final)
- Periodic checkpoints (every N entries or time interval)
- CLRs (Compensation Log Records) for idempotent undo
- Recovery: Analysis → Redo → Undo (ARIES)

### GAP 5: Quality Gate Ordering
**Status**: RESOLVED — Graduated enforcement model

**Sources**:
- SonarQube (Oct 2025) — Clean as You Code
- Adaptive Enforcement Lab (Dec 2025) — pre-commit vs CI
- Decryption Digest (Jul 2026) — DevSecOps gates
- WalnutAI (Jan 2026) — intelligent quality gates

**Gate Matrix**:
| Stage | Type | Tools | Blocking |
|-------|------|-------|----------|
| Pre-commit | Informational | TruffleHog, lint | Notification only |
| Build | Enforcing | SAST, deps, contract tests | Critical/High |
| Container | Enforcing | Trivy, SBOM, cosign | CVEs > threshold |
| Staging | Informational | DAST, pentest | Ticket creation |
| Production | Enforcing | Runtime protection, WAF | Block/quarantine |

**Principle**: Pre-commit = developer convenience. CI = enforcement. Never rely solely on pre-commit.

### GAP 6: Sovereign Search Tier Policies
**Status**: RESOLVED — Tiered routing with query classification

**Sources**:
- Zylos Research (2026) — QoS tiering, confidence-based routing
- InfoQ (May 2026) — Local-first AI inference, 75% cloud reduction
- LLM Router Cloud (2026) — 4 strategies: balanced, weighted, first_available, first_available_optim
- ContentWave (Jun 2026) — routing matrices, ROI examples

**Policy Matrix**:
| Query Category | Tiers | Validation |
|----------------|-------|------------|
| Architecture patterns | T0(cache) → T1(websearch) → T3(Firecrawl) | Cross-ref ≥2 sources |
| Benchmarks/numbers | T0 → T1 → T4(Exa) | Require numeric citations |
| Failure modes | T0 → T1 → T3 | Require reproduction steps |
| Heritage vetting | T0 → T1 → T3 | Require primary source |
| Mandate compliance | T0 → T1 (local KB) | Require mandate text |

**Local-first mandate**: 70-80% resolve at T0/T1 (Zylos: 70-80% never need frontier model).

### GAP 7: Automated Mandate Compliance Checking
**Status**: RESOLVED — Policy-as-Code with OPA/Rego

**Sources**:
- Global Relay (Mar 2026) — compliance policy automation
- Sesame Disk (Jun 2026) — Compliance as Code, OPA/Sentinel
- EmergentMind (Jan 2026) — Policy-as-Code formal foundations
- ARPaCCino (2025) — agentic-RAG for policy generation

**Implementation**:
```rego
# M1 AnyIO Absolute
deny[msg] {
    input.mandates[_] == "M1"
    not input.uses_anyio
    msg := "M1 violation: asyncio detected, must use AnyIO"
}

# M2 Engine-Stack Firewall
deny[msg] {
    input.mandates[_] == "M2"
    input.imports[_] = "config.wads.*"
    msg := "M2 violation: core engine imports WAD config"
}

# M23 Failure Integrity
deny[msg] {
    input.mandates[_] == "M23"
    input.has_bare_except
    msg := "M23 violation: bare except: clause"
}
```
- CI: `opa test policy/ mandates/`
- LLM synthesis: ARPaCCino generates policies from natural language mandates

### GAP 8: Agent Specialization for Pipeline Stages
**Status**: RESOLVED — Pipeline-agent model with cognitive role mapping

**Sources**:
- EmergentMind (Mar 2026) — pipeline-agent architectures
- arXiv:2507.13768 (Jul 2025) — extraction → activation → synthesis
- Redis.io (Mar 2026) — 5-stage cognitive pipeline
- L3-Entity-Identity-Is-Decomposition-Filter (this session)

**Stage → Agent Mapping**:
| Stage | Cognitive Role | Best Agent | Rationale |
|-------|----------------|------------|-----------|
| 0 Prompt Crafting | Bridge/Communication | Pillar P4 (Integration) | MCP, protocol expertise |
| 1 Meditation | 10-voice dialectic | `meditation-agent` (dedicated) | Not MaKaLi — different cognitive mode |
| 2 Synthesis | Architecture/Decision | Kali (oversight) | Transcendent view |
| 3 Research Prompts | Query decomposition | Pillar P4 | Bridge/communication |
| 4 Research | Deep search + verification | `researcher` (Sovereign Search) | Deep research specialist |
| 5 Grounding | Synthesis + verification | `jem` (synthesizer) | Lattice reasoning |
| 6 Gnosis | L1→L2→L3 distillation | `verity` (compliance + scribe) | Mandate audit + soul distillation |
| 7 Integration | PIVOT_LOG + workbench | `maat` (build-side governance) | P1-P5 oversight |

**Critical**: Same entity ≠ same cognitive filter. Parallel dispatch to complementary identities reveals blind spots.

### GAP 9: Dry-Run Mocking Strategies
**Status**: RESOLVED — Mock at boundaries, not internals

**Sources**:
- moqapi.dev (Apr 2026) — mock APIs in GitHub Actions
- Keploy (Jul 2026) — mock testing complete guide
- moqapi.dev blog — deterministic CI without flaky deps

**Mock Contract**:
```python
DRY_RUN_MOCKS = {
    "meditate": lambda: canned_10_voice_output,
    "sovereign_search": lambda q: cached_fixtures[q.category],
    "file_write": lambda p, c: write_to_tmp(p, c),
    "quality_gates": lambda: hardcoded_pass,
    "hivemind_handoff": lambda: mock_packet_id,
}
```
**Rule**: Mock external dependencies (APIs, CLIs, time). Never mock internal logic — test real code paths.

### GAP 10: Observability/Tracing
**Status**: RESOLVED — OpenTelemetry GenAI semantic conventions

**Sources**:
- LangChain Blog (Mar 2025) — end-to-end OTel support
- LangSmith Observability (2026) — SmithDB, agent query patterns
- DEV Community (May 2026) — OpenAI Agents SDK + LangSmith + OTel
- Imperialis Tech (Mar 2026) — LLM observability 2026

**Required Spans**:
- `agent.run` — stage execution
- `model.call` — inference with tokens, latency
- `tool.call` — tool invocations
- `handoff.transfer` — agent-to-agent

**Required Attributes** (GenAI semconv):
- `gen_ai.agent.name`, `gen_ai.request.model`, `gen_ai.usage.tokens`, `gen_ai.tool.name`

**Dashboard**: Token usage, latency P50/P99, error rates, handoff success rate.

### GAP 11: Unified Coordinator (Meditation + Council)
**Status**: RESOLVED — Single state machine, two entry points

**Sources**:
- Fast.io (2026) — 4 orchestration patterns: supervisor, pipeline, swarm, hierarchical
- Microsoft Agent Framework (Mar 2026) — sequential, concurrent, handoff, group chat, magentic
- arXiv:2601.13671 (Jan 2026) — unified orchestration layer with MCP + A2A

**Architecture**:
```python
class MultiAgentCoordinator:
    def __init__(self, profile: CouncilProfile):
        self.profile = profile
        self.wal = WALWriter()
        self.circuit_breakers = {}
        self.thermal_monitor = ThermalMonitor()
    
    async def run_meditation(self, lenses: List[str], topic: str) -> MeditationResult:
        # 10-voice sequential, single model load
        # Reuses: WAL, circuit breakers, thermal mgmt
    
    async def run_council(self, topic: str) -> CouncilResult:
        # Parallel pillars → oversouls → Kali synthesis
        # Reuses: WAL, circuit breakers, thermal mgmt
    
    # Shared infrastructure
    async def _dispatch_with_failure_handling(self, ...)
    async def _collect_results(self, ...)
    async def _invoke_oversoul(self, ...)
```

**Hardware profiles** drive execution mode:
- `local_16gb`: sequential_with_cooldown (30s between pillars)
- `local_8gb`: batch_2 (2 pillars at a time)
- `cloud_unconstrained`: parallel (all 10 pillars concurrent)
- `hybrid_local_cloud`: local pillars + cloud oversouls

### GAP 12: Hivemind Integration for Stage Outputs
**Status**: RESOLVED — Hivemind MCP + Activeloop DeepLake

**Sources**:
- hivemindai.dev (2026) — coordination layer, 10 MCP tools
- deeplake.ai/hivemind (2026) — shared memory, 34% cost reduction
- agent-hivemind (Aug 2025) — ChromaDB + Redis, teams/vaults
- Fast.io (Feb 2026) — agent handoff protocol, checkpointing

**Integration**:
- **Auto-capture**: Every stage output → persistent event log
- **Semantic search**: "What did Stage 3 find about X?" across all runs
- **Cross-session learning**: New runs query prior run context
- **Agent handoffs**: Structured packets with `supersedes` field for versioning
- **File locking**: Advisory locks (TTL-based cleanup) prevent clobbering

### GAP 13: Research Gap Unification Schema
**Status**: RESOLVED — GAPMAP + ServiceNow Knowledge Gaps

**Sources**:
- arXiv:2510.25055 (Oct 2025) — GAPMAP: LLM mapping of biomedical knowledge gaps
- ServiceNow (Mar 2026) — potential knowledge gaps from incident trends
- APQC (2026) — KM playbook: gap identification as strategic capability

**Unified Schema**:
```yaml
gap:
  id: "gap-<uuid>"
  source: "pipeline|council|meditation"
  stage: 0-7
  question: "Specific research question"
  context: "Why this matters for the verdict"
  category: "architecture|benchmark|failure_mode|heritage|compliance"
  priority: "P0|P1|P2|P3"
  recommended_approach: "websearch|benchmark|code_analysis|expert_consult"
  suggested_model: "qwen3.5-4b|gemma-4-12b|nemotron-3-ultra"
  success_criteria: "Measurable outcome"
  status: "open|in_progress|resolved|deferred"
  supersedes: []  # versioning chain
  trace_id: "links to originating run"
```

---

## Cross-Cutting Insights

### 1. **Single Coordinator, Multiple Modes**
The meditation protocol and MaKaLi council are not separate systems — they are two modes of the same unified coordinator sharing WAL, failure handling, thermal management, and profile loading.

### 2. **Cognitive Diversity > Redundancy**
Parallel dispatch to agents with *different identities* (Roc vs Kali) reveals complementary blind spots. Same prompt → different decomposition → synthesis captures both.

### 3. **Local-First Is Not Optional**
70-80% of queries resolve locally. Cloud is fallback. Tier routing must be configurable per query category, not global.

### 4. **Mandates as Executable Policy**
M1-M23 are not documentation — they are Rego policies that block CI. LLM synthesis (ARPaCCino) generates policies from natural language.

### 5. **State Is the Product**
Every stage output is a Hivemind event. The council's value compounds across sessions via semantic search and cross-session learning.

### 6. **Dry-Run Must Exercise Real Code Paths**
Mock boundaries (APIs, CLIs, time). Never mock internal logic — test the actual failure handling, circuit breakers, WAL writes.

---

## Implementation Priority (T0 — 5 Sessions)

| Session | Focus | Deliverable |
|---------|-------|-------------|
| 1 | **Unified Coordinator Core** | `MultiAgentCoordinator` with WAL, circuit breakers, thermal mgmt, profile loader |
| 2 | **Stage Contracts + Failure Layer** | All 8 stage contracts, 4-layer failure handling, atomic checkpointing |
| 3 | **Meditation Mode** | `run_meditation()` — 10-voice sequential, single model load |
| 4 | **Council Mode** | `run_council()` — parallel pillars → oversouls → Kali synthesis |
| 5 | **Integration + Gates** | Hivemind capture, mandate Rego policies, quality gates, observability |

---

## Sources Index (35+)

### 2026 Primary Sources
1. RecursiveMAS — arXiv:2604.25917 (Apr 2026)
2. Microsoft Learn Multi-Agent Patterns — (2026)
3. Codex CLI v2 — Daniel Vaughan (Apr-Jul 2026)
4. OpenAI Agents SDK — (Jun 2026)
5. LangGraph v1.0 — (2026)
6. miaoquai.com production patterns — (Jun 2026)
7. AgentMarketCap self-healing — (Apr 2026)
8. Supergood Solutions failure patterns — (Mar 2026)
9. ndlab.blog WAL/ARIES — (Jul 2026)
10. Grafana Loki WAL — (2026)
11. SonarQube Quality Gates — (Oct 2025)
12. Adaptive Enforcement Lab pre-commit — (Dec 2025)
13. Zylos Research tiered routing — (2026)
14. InfoQ Local-First AI — (May 2026)
15. LLM Router Cloud — (2026)
16. Global Relay policy automation — (Mar 2026)
17. Sesame Disk Compliance as Code — (Jun 2026)
18. EmergentMind Policy-as-Code — (Jan 2026)
19. ARPaCCino agentic-RAG — (2025)
20. EmergentMind pipeline-agent — (Mar 2026)
21. arXiv:2507.13768 extraction-synthesis — (Jul 2025)
22. Redis.io cognitive pipeline — (Mar 2026)
23. moqapi.dev mock APIs — (Apr 2026)
24. Keploy mock testing — (Jul 2026)
25. LangChain OTel end-to-end — (Mar 2025)
26. LangSmith Observability — (2026)
27. DEV Community OTel + LangSmith — (May 2026)
28. Fast.io orchestration patterns — (2026)
29. Microsoft Agent Framework — (Mar 2026)
30. arXiv:2601.13671 orchestration layer — (Jan 2026)
31. hivemindai.dev coordination layer — (2026)
32. deeplake.ai/hivemind — (2026)
33. agent-hivemind ChromaDB+Redis — (Aug 2025)
34. Fast.io handoff protocol — (Feb 2026)
35. GAPMAP knowledge gaps — arXiv:2510.25055 (Oct 2025)
36. ServiceNow knowledge gaps — (Mar 2026)
37. APQC KM Playbook 2026 — (2026)

---

## Mandate Compliance Check

| Mandate | Addressed In | Mechanism |
|---------|--------------|-----------|
| M1 AnyIO | Stage contracts, coordinator | `uses_anyio` check in Rego |
| M2 Firewall | Stage contracts, coordinator | Import path validation |
| M4 Sequentiality | Coordinator state machine | Plan → Verify → Execute enforced |
| M5 Gnosis | Stage 6 (verity) | L1→L2→L3 to proposed_lessons.yaml |
| M7 Local-First | Search tier policies | 70-80% T0/T1 resolution |
| M9 Error Integrity | Failure layer, Rego | Typed errors, trace_id propagation |
| M11 Soul | Stage 6 + proposed_lessons | Blind staging per Soul Architecture v2 |
| M13 Temple-Grade | Quality gates | T1-T11 enforced in CI |
| M15 Continuity | WAL + Hivemind | Session recovery, cross-session learning |
| M16 Modularity | Coordinator profiles | No hardcoded paths, config-driven |
| M18 Token Efficiency | Local-first, dry-run mocks | 70-80% local, mocked boundaries |
| M21 Gate Integrity | Contract tests per stage | `isinstance(result, ExpectedType)` |
| M23 Failure Integrity | 4-layer failure, Rego | No soft failures, hard stops |

---

## Next Actions

1. **Write unified coordinator implementation** — extract from MaKaLi spec
2. **Define Stage 0 contract** — explicit execution_mode enum
3. **Implement WAL + checkpointing** — before any stage logic
4. **Codify mandate Rego policies** — M1, M2, M7, M13, M23 minimum
5. **Configure Sovereign Search tier routing** — per query category
6. **Wire Hivemind MCP** — stage output capture + semantic recall

---

*⬡ OMEGA ⬡ KALI ⬡ RESEARCH-SYNTHESIS ⬡ 2026-07-19*