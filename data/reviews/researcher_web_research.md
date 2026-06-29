# Omega Engine - Sovereign Web Research Report
**RESEARCHER** | **2026-06-28** | **Status: COMPLETE**

**Method**: 14+ web searches, 5 deep URL fetches, 40+ authoritative sources analyzed

---

## Executive Summary

This sovereign web research pass investigated state-of-the-art across 7 domains. The Omega Engine is **ahead of the industry** in local-first provider fabric, BSP-style culling, and AnyIO-native async. But it has **specific blind spots** where production-proven patterns exist:

1. **Context compaction** has converged on 3-tier architecture (raw/reversible/lossy) at 70-80% trigger -- we have NO compaction lifecycle
2. **Agent observability** has stable OTel GenAI conventions (gen_ai.*) -- our trace_id gaps violate this standard
3. **Memory consolidation** research shows fact-level storage at write time is highest-leverage -- our distillation is turn-level batch
4. **Handoff protocols** converged on 6-field contract spec -- our Hivemind handoff is ad-hoc
5. **Provider health scoring** uses weighted composite scores -- our circuit breaker is binary open/closed

---

## SECTION 1: SESSION LIFECYCLE AND MEMORY MANAGEMENT

### Finding 1.1: 3-Tier Context Architecture Is Industry Standard

**Sources**:
- Redis Blog: "Context compaction for AI agents" (2026-05-27) https://redis.io/blog/context-compaction/
- Zylos Research: "AI Agent Context Compression Strategies" (2026-02-28) https://zylos.ai/research/2026-02-28-ai-agent-context-compression-strategies
- AI/TLDR: "Context Compaction for Long-Running AI Agents" (2026-06-12) https://ai-tldr.dev/learn/ai-agents/planning-and-memory/context-compaction-explained/

**Pattern**: Industry converged on 3-tier compaction:
```
Raw Context (keep first)
  -> Reversible Compaction (offload tool outputs, leave pointer)
    -> Lossy Summarization (LLM summarize old turns, last resort)
```

**Key Insight**: "Start with raw context. Move to reversible compaction when the window gets tight. Only fall back to lossy summarization when nothing cheaper works." (Redis, 2026)

**Trigger Thresholds**: Claude Code triggers at ~80% of context window. Anthropic API defaults to 150K trigger with 50K floor. Research recommends 70-80% as optimal.

**Application to Omega**: Our `context_builder.py` has sliding window but NO compaction lifecycle. Sessions grow unboundedly until context limit, then old messages silently dropped. We need:
1. `CompactionManager` triggering at 70% of context budget
2. Reversible compaction: offload large tool outputs to file store
3. Lossy summarization as last resort via fast local model (Qwen3-1.7B)

**Recommendation**: Add `CompactionManager` to `src/omega/oracle/context_builder.py` with strategies: `SlidingWindow`, `ToolOutputOffload`, `Summarization`.

---

### Finding 1.2: Session Retention Must Be TTL-Based with Namespace Scoping

**Sources**:
- TechAhead: "Agent Memory State Management" (2026-05-01) https://www.techaheadcorp.com/blog/agent-memory-state/
- youngju.dev: "Chatbot Multi-Turn Memory Management" (2026-03-11) https://www.youngju.dev/blog/chatbot/2026-03-11-chatbot-multi-turn-memory-langchain-langgraph.en

**Pattern**: Production TTLs per namespace:
```
Working (session)  -> Session TTL + 24h idle expiry
Episodic (events)  -> 90 days active, then archive
Semantic (knowledge) -> Indefinite until superseded
```

**Key Insight**: "One-size-fits-all TTL policies are a common source of both data loss and unnecessary storage cost." (TechAhead, 2026)

**Application to Omega**: Our `ARCHIVE_AFTER_DAYS = 7` is a single global constant. We need per-entity TTLs in entities.yaml. Wire `archive_old_sessions()` (currently dead code) into background reaper.

**Recommendation**: Add `retention_policy` block to entity config. Wire dead `archive_old_sessions()` into `background.py`.

---

### Finding 1.3: Memory Consolidation Is a Write-Time Decision

**Sources**:
- Hindsight: "The Consolidation Problem in Agent Memory" (2026-05-21) https://hindsight.vectorize.io/blog/2026/05/21/agent-memory-consolidation
- Automatos: "Memory Lifecycle and Consolidation" https://docs.automitos.app/automatos-ai-docs/design-docs/memory-system/memory-lifecycle-consolidation.md

**Pattern**: 4-lever consolidation framework:
1. **Importance** -- What becomes a memory (fact extraction > turn storage)
2. **Merge** -- How related facts unify (entity resolution at write time)
3. **Decay** -- How confidence degrades (exponential decay with temporal validity)
4. **Eviction** -- When memories leave (compliance-only, not performance)

**Key Insight**: "Start with fact-level storage, not turn-level. Extracting facts at write time is the highest-leverage consolidation decision." (Hindsight, 2026)

**Application to Omega**: Our soul distillation extracts L1/L2/L3 at session END (fire-and-forget). Research shows this is backwards. We need fact extraction at each exchange, entity resolution at write time, temporal validity on soul.yaml lessons.

**Recommendation**: Add `FactExtractor` to oracle `add_exchange()` path. Add `valid_at` / `superseded_at` to soul.yaml entries.

---

## SECTION 2: OBSERVABILITY AND TELEMETRY

### Finding 2.1: OTel GenAI Semantic Conventions Are Now Stable

**Sources**:
- TrueFoundry: "OpenTelemetry for LLMs" (2026-05-28) https://www.truefoundry.io/blog/opentelemetry-llm-gateway-instrumentation
- Metacto: "LLM Tracing in Production" (2026-06-16) https://www.metacto.com/blogs/llm-tracing-production-guide

**Pattern**: The gen_ai.* namespace is the standard:
```
gen_ai.system, gen_ai.request.model, gen_ai.usage.input_tokens,
gen_ai.usage.output_tokens, gen_ai.response.finish_reason
```

**Key Insight**: "Adopting the standard is not religion -- it is portability." (Metacto, 2026)

**Application to Omega**: Our trace_id gaps directly violate this standard. "Every agent boundary must propagate trace context. If propagation breaks, your observability is broken." (Coverge, 2026)

**Recommendation**: Fix 2 trace_id propagation gaps (P0). Add provider_name to TokenLedger (P0). Future: adopt gen_ai.* naming.

---

### Finding 2.2: Agent Observability Requires 4 Span Types

**Sources**:
- Braintrust: "Agent observability: The complete guide for 2026" (2026-06-21) https://www.braintrust.dev/articles/agent-observability-complete-guide-2026
- Coverge: "AI agent observability" (2026-04-14) https://coverge.ai/blog/ai-agent-observability

**Pattern**: Minimum viable agent trace schema:
1. Tool-call spans -- name, args, output, duration, retries
2. Reasoning spans -- plan, action, observation, next-step
3. State transition spans -- before/after state, context edits
4. Memory operation spans -- query, results, relevance scores

**Application to Omega**: We have EventType enums but no typed spans or parent-child hierarchy. Phase 2 enhancement after trace_id fix.

---

### Finding 2.3: Event Log Retention Needs Priority-Based Sampling

**Sources**:
- Oracle OCI: "Observability for Agentic AI" (2026-05-05) https://blogs.oracle.com/ai-and-datascience/oci-observability-for-agentic-ai
- Claude Code Internals: "Observability Engineering" https://zhanghandong.github.io/harness-engineering-from-cc-to-ai-coding/en/part7/ch29.html

**Pattern**: Tiered sampling:
```
100% structural spans (attributes only)
100% error + slow traces with content
5-10% successful traces with content
0% content for PII/regulated traces
```

**Application to Omega**: Our event log has no retention policy. Events accumulate indefinitely. Need ERROR/WARN kept 100%, INFO sampled 10%, DEBUG sampled 1%. Max 30 days for INFO/DEBUG, 90 days for ERROR/WARN.

**Recommendation**: Add `EventSampler` with per-level rates. Add `EventRetentionPolicy` with TTL per level.

---

## SECTION 3: PROVIDER FABRIC AND FAILOVER

### Finding 3.1: Circuit Breakers Need Per-Provider-AND-Model Scoping

**Sources**:
- AI/TLDR: "Circuit Breakers for LLM Calls" (2026-06-13) https://ai-tldr.dev/learn/production-llmops/guardrails-reliability/llm-circuit-breaker/
- VeriSwarm: "Your LLM Provider Will Go Down" (2026-05-14) https://veriswarm.ai/blog/llm-provider-circuit-breakers

**Pattern**: Per-provider AND per-model breakers:
```
failure_threshold: 5 (cloud), 10 (local)
recovery_timeout: 30s (cloud), 10s (local)
half_open_max_calls: 2-3 probes
```

**Application to Omega**: Our AsyncCircuitBreaker is per-provider but NOT per-model. If gemma-4-31b fails but gemma-4-12b works, both blocked. Need model-granular breakers.

**Recommendation**: Extend breaker to accept provider+model key. Default per-provider with optional per-model override.

---

### Finding 3.2: Provider Health Scoring Uses Weighted Composite Scores

**Sources**:
- grate-limiter (PyPI) https://pypi.org/project/grate-limiter/
- Bifrost: "Adaptive Load Balancing" https://docs.getbifrost.ai/enterprise/adaptive-load-balancing

**Pattern**: Weighted composite scoring:
```
score = quota*0.40 + health*0.35 + priority*0.20 + latency*0.05
```

4-state model: Healthy -> Degraded -> Failed -> Recovering
EWMA for smooth health tracking. Momentum bias for recovery acceleration.

**Application to Omega**: Our binary breaker needs upgrade to 4-state health model with weighted composite scoring and EWMA.

**Recommendation**: Create `ProviderHealthScore` class. Update on every inference response. Use in `_precheck_provider()`.

---

### Finding 3.3: Typed Fallbacks Distinguish Failure Classes

**Sources**:
- AI/TLDR: "LLM Provider Outages" (2026-06-12) https://ai-tldr.dev/learn/production-llmops/llmops-fundamentals/llm-provider-failover/

**Pattern**: Different failures need different fallbacks:
```
Provider down (5xx)  -> Retry 1-2x, then failover
Rate limit (429)     -> Skip retries, immediate failover
Context window       -> Fallback to larger-context model
Content policy       -> Fallback or structured error
```

"Never use a single catch-all fallback."

**Application to Omega**: Our provider chain is a single ordered list. Need typed fallback paths.

**Recommendation**: Add `fallback_types` dict: general, context_window, rate_limit.

---

## SECTION 4: AGENT ORCHESTRATION AND HANDOFF

### Finding 4.1: Handoff Protocols Converged on 6-Field Contract

**Sources**:
- Geodocs.dev: "Agent Handoff Protocol Spec" (2026-04-29) https://geodocs.dev/ai-agents/agent-handoff-protocol-spec
- Agent Patterns Catalog: "Handoff" (2026-05-21) https://www.agentpatternscatalog.org/patterns/handoff/
- Google DevBlog: "ADK and A2A" (2026-06-22) https://developers.googleblog.com/build-cross-language-multi-agent-team-with-google-agent-development-kit-and-a2a/

**Pattern**: 6 required fields:
```
id, source, target, trigger, payload, acceptance_criteria, recovery
```

**Key Insight**: "Multi-agent AI systems fail at handoffs more often than they fail at reasoning." (Geodocs, 2026)

**Critical Finding**: Spec mandates `loop_guard` -- visited agent set to prevent infinite cycles. Our Hivemind has NO loop guard.

**Recommendation**: Create `config/handoff_contracts/` with YAML contracts. Add loop guard (visited_agents set). Add on_reject/on_timeout/on_error recovery.

---

### Finding 4.2: A2A Protocol Is the Emerging Standard

**Sources**:
- Google DevBlog (2026-06-22)
- arxiv: "Orchestration of Multi-Agent Systems" (2026-01-20) https://arxiv.org/html/2601.13671v1

**Pattern**: A2A defines Discovery (Agent Cards), Communication (JSON-RPC 2.0), Task lifecycle (submitted/working/completed/failed).

"A2A is the HTTP of the agent world." (Google, 2026)

**Application to Omega**: Our Hivemind is A2A-like. Document as A2A-compatible subset. Future: publish Agent Cards.

---

## SECTION 5: AI SOUL AND CONSTITUTION EVOLUTION

### Finding 5.1: Constitutional Amendment Cycles Demonstrated in Production

**Sources**:
- shimo4228: "Constitution Amendment Report" https://github.com/shimo4228/contemplative-agent-data/blob/main/reports/analysis/constitution-amendment-report.md
- shimo4228: "How Ethics Emerge from Episode Logs" (2026-04-05) https://dev.to/shimo4228/how-ethics-emerged-from-episode-logs-17-days-of-contemplative-agent-design-1kk5

**Pattern**: AKC (Agent Knowledge Cycle) 6-phase pipeline:
```
Research -> Extract -> Curate -> Promote -> Measure -> Maintain
```

**Key Discovery**: "Knowledge saturates. Semantic dedup rejects similar patterns. Distillation yields diminish. Breaking through requires sublimation to insight/skills/rules, and sublimation requires human approval. Self-improvement is rate-limited by human approval." (shimo4228, 2026)

**Critical Insight**: Step 0 fast classification BEFORE distillation separates constitutional from behavioral episodes.

**Application to Omega**: Our 133 unprocessed proposed_lessons = saturation problem. Need:
1. Step 0: Fast classification (constitutional/behavioral/noise)
2. Semantic dedup before appending
3. Importance scoring with time decay: effective = base * 0.95^days
4. Verity approval gate for L3 principles

**Recommendation**: Add `LessonClassifier` to soul distiller. Deduplicate against soul.yaml. Apply time decay.

---

### Finding 5.2: MAC Uses Specialized Agents for Constitutional Learning

**Sources**:
- arxiv: "MAC: Multi-Agent Constitution Learning" (2026-03) https://www.arxiv.org/pdf/2603.15968
- arxiv: "Evolving Interpretable Constitutions" (2026-02) https://www.arxiv.org/pdf/2602.00755

**Pattern**: Proposer suggests changes, Critic evaluates, Refiner polishes. "Operational specificity outperforms abstract principles."

**Application to Omega**: Our mandates are already operational (M1-M22). Future: use MaKaLi triad for automated lesson refinement.

---

## SECTION 6: HERITAGE ATTRIBUTION AND PROVENANCE

### Finding 6.1: SWHID Is the ISO Standard for Code Provenance

**Sources**:
- Software Heritage: "How to archive and reference code" (2024) https://www.softwareheritage.org/how-to-archive-reference-code/
- PMC: "Archiving and Referencing Source Code" https://pmc.ncbi.nlm.nih.gov/articles/PMC7340894/

**Pattern**: SWHID (Software Hash IDentifier) is ISO/IEC 18670:
```
swh:1:dir:<hash>  -- directory (most robust)
swh:1:rev:<hash>  -- revision/commit
swh:1:cnt:<hash>  -- content/file
```

**Application to Omega**: Our [id-soft:] tags are excellent. Missing: machine-readable provenance layer. Should archive repo to SWH, reference id Software source via SWHID qualifiers, add codemeta.json.

**Recommendation**: Archive omega-engine to SWH. Update CREDITS.md with SWHID refs. Add codemeta.json.

---

## SECTION 7: TOKEN BUDGETING AND RATE LIMITING

### Finding 7.1: Token-Based Rate Limiting Is Production Standard

**Sources**:
- TrueFoundry: "Rate Limiting in AI Gateway" (2026-06-12) https://www.truefoundry.com/blog/rate-limiting-in-llm-gateway
- Zuplo: "Token-Based Rate Limiting" (2026-03-08) https://zuplo.com/learning-center/token-based-rate-limiting-ai-agents

**Pattern**: Token-aware limits track tokens, cost, and concurrency per user/team/model. Fixed + sliding window + token bucket. Per-tenant quotas with priority routing.

**Application to Omega**: Our BudgetGate tracks tokens but lacks per-entity quotas and cost-weighted routing. Need daily/monthly token budgets per entity, cost-weighted provider selection.

**Recommendation**: Add per-entity token budgets to entity config. Add cost-weighted provider scoring.

---

### Finding 7.2: Cost-Aware Multi-Provider Routing

**Sources**:
- Scutum: "Cost-Aware Multi-Provider Routing" https://www.scutum.dev/docs/whitepapers/cost-aware-routing/

**Pattern**: Scalarized utility:
```
U_p(r) = -alpha*c_p(r) - beta*E[L_p] + gamma*Q_p(r)
```
Operator provides trade-off weights. Single-pass argmax over providers.

**Application to Omega**: Our local-first priority is fixed. Could add cost-latency-quality trade-off for cloud providers.

---

## PRIORITY MATRIX

| Priority | Finding | Impact | Effort |
|----------|---------|--------|--------|
| P0 | Fix trace_id propagation (2 sites) | CRITICAL | 2 lines |
| P0 | Add provider_name to TokenLedger | CRITICAL | 10 lines |
| P1 | Wire archive_old_sessions() | HIGH | 30 min |
| P1 | Add CompactionManager | HIGH | 1-2 days |
| P1 | LessonClassifier for proposed_lessons | HIGH | 1 day |
| P1 | Typed fallbacks in providers.yaml | HIGH | 2 hours |
| P2 | ProviderHealthScore (4-state) | MEDIUM | 1 day |
| P2 | Per-entity retention TTLs | MEDIUM | 4 hours |
| P2 | EventSampler with priority rates | MEDIUM | 4 hours |
| P2 | Handoff contract YAML files | MEDIUM | 1 day |
| P2 | Per-model circuit breakers | MEDIUM | 4 hours |
| P3 | AgentSpan typed trace schema | LOW | 2 days |
| P3 | SWHID references in CREDITS.md | LOW | 2 hours |
| P3 | A2A-compatible Agent Cards | LOW | 1 day |

---
