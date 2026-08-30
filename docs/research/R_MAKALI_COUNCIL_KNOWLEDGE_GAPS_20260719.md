# 🔱 MaKaLi Parallel Council — Knowledge Gaps Analysis
**Date**: 2026-07-19  
**Context**: Post-ratification research for D-301 MaKaLi Parallel Council Architecture  
**Sources**: 20+ papers/articles across multi-agent coordination, hardware-aware routing, consensus protocols

---

## Executive Summary

The MaKaLi Parallel Council Architecture (D-301) is architecturally sound but has **7 knowledge gaps** that need research before T0 implementation. Key findings from 2026 research:

1. **Fan-out/fan-in is the dominant pattern** for parallel agent coordination (matches our architecture)
2. **Voting protocols improve reasoning by 13.2%** (ACL 2025) — relevant for Phase 2 oversoul distillation
3. **Parallel-Synthesis paper** (June 2026) enables direct KV cache synthesis from parallel branches — 2.5x-11x faster
4. **Hardware-aware routing** is a solved problem with production patterns (QoS tiering, confidence-based routing)
5. **Context window pressure at Tier 1** is the biggest practical threat to our architecture

---

## Knowledge Gaps

### GAP 1: Oversoul Distillation Efficiency
**Question**: How do Ma'at/Lilith efficiently read 4-5 pillar reports and produce a consolidated report?

**Current Approach**: Oversoul reads all reports sequentially, writes consolidated report.

**Research Findings**:
- **Fan-out/fan-in pattern** (Beam.ai 2026): Dispatcher sends work out, collector aggregates results. Our Phase 2 is a fan-in.
- **Context window overflow** (Beam.ai 2026): "At four or more workers, context frequently exceeds window limits." This is exactly our Phase 2 problem.
- **Parallel-Synthesis** (arXiv 2606.14672, June 2026): Enables synthesizer to directly consume KV caches from parallel workers. Reduces time-to-first-token by 2.5x-11x.

**Gap**: We need a strategy for oversoul context management. Options:
1. **Sequential reading**: Oversoul reads reports one at a time, maintains running synthesis (current approach)
2. **Parallel KV synthesis**: Use Parallel-Synthesis technique (requires model fine-tuning)
3. **Report summarization**: Pillars produce both full report AND summary; oversoul reads summaries first
4. **Chunked ingestion**: Split reports into sections, process in batches

**Recommendation**: Start with sequential reading (Option 1), measure context usage, optimize if needed.

---

### GAP 2: Tier 1 Context Window Management
**Question**: Can 4B models (Gemma 4B, Qwen 4B) handle 32K context for pillar work?

**Current Approach**: Assume 32K context is sufficient for pillar reports + instructions.

**Research Findings**:
- **2B models**: 4K-8K context typical (Carmack identified this as critical)
- **4B models**: 8K-32K context (Gemma 4B = 32K, Qwen 4B = 32K)
- **Report length at useful depth**: 2-3K tokens per pillar
- **Instruction overhead**: 1.5-2K tokens per task() dispatch (persona + mandates)

**Gap**: We need to validate that 4B models can handle:
- Persona/instruction prompt (~2K tokens)
- Topic/problem description (~1K tokens)
- Output format instructions (~500 tokens)
- Remaining budget for report: ~28.5K tokens (at 32K context)

**Recommendation**: Benchmark 4B models with typical pillar prompts. Measure actual token usage. Establish maximum report length per pillar.

---

### GAP 3: Hardware-Constrained Parallel Execution
**Question**: How do we coordinate parallel execution on Ryzen 5700U 16GB without thermal throttling?

**Current Approach**: Batch execution mode (2-4 pillars at a time).

**Research Findings**:
- **Thermal limits**: 5700U TDP = 15W, sustained load causes thermal throttling
- **RAM pressure**: 4B model = ~4-6GB, 8B = ~8-10GB, 12B = ~12-14GB. Cannot run multiple models simultaneously on 16GB.
- **Edge deployment patterns** (ScienceDirect 2026): Hardware-aware microservices with dynamic orchestrator

**Gap**: We need to define:
1. **Execution sequencing**: How to schedule pillars to avoid RAM exhaustion
2. **Model loading/unloading**: When to load next model before current finishes
3. **Thermal monitoring**: How to detect throttling and pause execution
4. **Fallback to serial**: When parallel is impossible due to hardware constraints

**Recommendation**: Implement hardware detection (already in architecture), define execution profiles, test on actual hardware.

---

### GAP 4: Research Execution Decoupling
**Question**: How does Phase 4 (research execution) work when decoupled from synthesis?

**Current Approach**: Kali writes "REMAINING_GAPS_AND_RECOMMENDED_RESEARCH" section, smaller/cloud model executes later.

**Research Findings**:
- **Hybrid routing** (tianpan.co 2026): "Design a hybrid routing layer from day one. Simple tasks route to device, complex reasoning routes to cloud."
- **Confidence-based routing** (arXiv 2504.07878): Route tokens with low confidence to cloud LLM. Only 7% of tokens routed = 60% accuracy improvement.
- **SLO tiering** (Zylos 2026): Realtime (<500ms), Standard (<3s), Premium (<30s), Batch (hours)

**Gap**: We need to define:
1. **Research query format**: How does Kali express research gaps as executable queries?
2. **Model selection**: How does the system choose which model executes each research query?
3. **Result integration**: How do research results feed back into the council output?
4. **Cost tracking**: How do we track cloud usage for research execution?

**Recommendation**: Define research gap schema, implement as separate skill, track costs per query.

---

### GAP 5: Failure Handling in Parallel Execution
**Question**: What happens when one pillar fails during Phase 1 parallel execution?

**Current Approach**: Not explicitly defined.

**Research Findings**:
- **Error amplification** (Sesame Disk 2026): Independent topology has 17.2x error amplification factor
- **Fan-out/fan-in failure modes** (Beam.ai 2026): "The orchestrator is a single point of failure. If it misclassifies a task, the wrong worker gets it."
- **Cascading fallback** (Zylos 2026): Provider outage → same-capability model at different provider; Context window exceeded → larger-context model; Quality threshold not met → escalate to more capable model

**Gap**: We need to define:
1. **Partial result handling**: Can the council continue if 1 of 4 pillars fails?
2. **Retry strategy**: How many retries per pillar? What's the timeout?
3. **Degraded mode**: Can Ma'at/Lilith produce a report with only 2-3 pillar inputs?
4. **Dead letter queue**: Where do failed pillar tasks go for investigation?

**Recommendation**: Implement retry with exponential backoff, define degraded mode, log failures for analysis.

---

### GAP 6: Consensus Protocol Selection
**Question**: What consensus mechanism should the oversoul use when synthesizing pillar reports?

**Current Approach**: Oversoul reads all reports, writes consolidated report (implicit consensus).

**Research Findings**:
- **Voting vs Consensus** (ACL 2025):
  - Voting improves reasoning tasks by 13.2%
  - Consensus improves knowledge tasks by 2.8%
  - Voting uses ~10x tokens, Consensus uses ~5x tokens
- **Weighted confidence voting** (tianpan.co 2026): Not all agents equally reliable. Assign vote weights based on domain expertise or historical accuracy.
- **Debate-then-vote hybrid** (tianpan.co 2026): Agents debate for 2-3 rounds, then vote if disagreement persists. Caps debate rounds to prevent sycophantic convergence.

**Gap**: We need to decide:
1. **Consensus strategy**: Should oversoul use voting, consensus, or implicit synthesis?
2. **Disagreement handling**: When pillar reports contradict, how does oversoul resolve?
3. **Confidence weighting**: Should pillar votes be weighted by domain expertise?
4. **Debate mechanism**: Should oversoul facilitate debate between pillars on contested claims?

**Recommendation**: Start with implicit synthesis (oversoul reads, synthesizes). Add explicit consensus if quality issues emerge.

---

### GAP 7: Cross-Council Memory
**Question**: Should council sessions share a memory namespace? Can Phase 4 research results feed into the next council cycle?

**Current Approach**: Each council session is independent. No cross-session memory.

**Research Findings**:
- **DynamicRAG** (Varangot-Reille et al. 2025): "Routing across embedding, retrieval, prompting, tools, and memory rather than only across LLMs."
- **ShardMemo** (Zhao et al. 2026): Learned tier gate over working memory, sharded evidence memory, and versioned skill library.
- **Model-as-infrastructure** (tianpan.co 2026): "The teams that succeed treat the model as infrastructure: versioned, monitored, with explicit deprecation timelines."

**Gap**: We need to decide:
1. **Memory persistence**: Should pillar insights persist across council sessions?
2. **Research result integration**: Can Phase 4 research results become input to next council?
3. **Knowledge accumulation**: How does the council's collective knowledge grow over time?
4. **Soul evolution**: How do council insights feed into entity soul.yaml (M11)?

**Recommendation**: Start with session-isolated councils. Add cross-session memory in Phase 2 (after T0 proves the pattern).

---

## Priority Ranking (Updated with Research Findings)

| Gap | Impact | Effort | Priority | Status After Research |
|-----|--------|--------|----------|----------------------|
| GAP 1: Oversoul Distillation | HIGH | MEDIUM | P0 | **Actionable now**: AgentDistillation + AgentArk show small models (0.5B-3B) can match next-tier-larger models. AgentArk specifically distills multi-agent debate → single agent (our exact use case). Start with simple output → structured distillation (no training infra needed for T0). |
| GAP 2: Tier 1 Context Windows | HIGH | LOW | P0 | **Partially resolved**: Qwen3.5-4B (262K ctx, ~3GB Q4) and Gemma 4 E4B (128K ctx, ~3GB Q4) both fit on 16GB with room. Gemma 4 12B Unified (~8GB Q4) perfect for oversoul. Need to run actual pillar prompts to measure real context usage. |
| GAP 5: Failure Handling | HIGH | MEDIUM | P0 | **Actionable now**: Research provides clear patterns — circuit breakers, fallback chain, retry with full jitter, WAL logging, partial results, checkpointing. Can implement directly. WAL pattern from databases maps 1:1 to coordinator crash recovery. |
| GAP 3: Hardware Constraints | MEDIUM | HIGH | P1 | **Partially resolved**: Gemma 4 26B-A4B confirmed working at 15GB/18 tok/s on iGPU. Our 16GB RAM is borderline for this tier. Qwen3.5-4B confirmed at ~3-5GB. Pillar→4B, Oversoul→12B, Kali→cloud (no local 12B on 16GB without swap). |
| GAP 4: Research Decoupling | MEDIUM | MEDIUM | P1 | **Actionable now**: No new research needed — implement as Kali's "remaining gaps" section executed by smaller model. Existing websearch/webfetch tools sufficient for T0. |
| GAP 6: Consensus Protocol | MEDIUM | LOW | P2 | **Settled by research**: Voting for reasoning (+13.2%), Consensus for knowledge (+2.8%). ACL 2025 findings are statistically significant. Confidence-weighted consensus (Roundtable Policy) is recommended approach. More rounds BEFORE voting reduces performance — agree on decision protocol before discussion. |
| GAP 7: Cross-Council Memory | LOW | HIGH | P3 | **Confirmed low priority**: Start session-isolated. ShardMemo three-tier pattern exists when needed. No benefit to premature memory infrastructure. |

---

## Recommended T0 Approach (Updated)

Given completed research, T0 approach is refined:

1. **GAP 2 → BENCHMARK (1 session)**: Run Qwen3.5-4B or Gemma E4B with representative pillar prompts. Measure:
   - Per-prompt token count (input + output)
   - Per-prompt KV cache usage
   - Max context window needed for 4-5 pillar reports
   - Time-to-completion per pillar prompt
   *Decision point*: If 4B fits comfortably, move forward. If not, fall back to 2B tier (Qwen3.5-2B).

2. **GAP 5 → BUILD FAILURE LAYER (1 session)**: Implement coordinator failure handling:
   - Circuit breaker per pillar (3 consecutive failures = skip)
   - Fallback chain: preferred model → smaller model → empty report
   - Retry with full jitter: `random(0, min(cap, base * 2^attempt))`
   - WAL-inspired: log pillar dispatch before execute, resume on crash
   - Partial results over no results

3. **GAP 1 → TEST OVERSOUL (1 session)**: Run oversoul pattern with 4-5 reports:
   - Measure oversoul context window (combined input from 4-5 reports)
   - Test Gemma 4 12B Unified (@8GB Q4) as oversoul model
   - Verify oversoul synthesis quality
   - Measure total tokens for complete council cycle

4. **Build coordinator (1 session)**: Using validated benchmarks:
   - Coordinator prompt with routing logic: reasoning→voting, knowledge→consensus
   - Confidence-weighted aggregation (Roundtable Policy pattern)
   - Partial results handling
   - Research gap section → smaller model

5. **Test on hardware (1 session)**: Full end-to-end on Ryzen 5700U 16GB:
   - Run 4 pillars + oversoul + Kali synthesis
   - Monitor thermal (stay under 85°C sustained)
   - Monitor RAM (stay under 12GB, keep 4GB for system)
   - Measure total latency

**Total T0 estimate**: 5 sessions (was 6+ — saved by research confirming patterns exist and don't need reinvention)

---

## Research Sources (Tier 1 — Built-in Search)

| Source | URL | Key Finding |
|--------|-----|-------------|
| Multi-Agent Coordination Patterns | markaicode.com | Hierarchical, P2P, broadcast patterns |
| MultiAgentBench (ACL 2025) | aclanthology.org | Graph topology performs best, cognitive planning +3% |
| SILO-BENCH (ACL 2026) | aclanthology.org | Role-free benchmark under information silos |
| Consensus Protocols (tianpan.co) | tianpan.co | Voting +13.2% reasoning, Consensus +2.8% knowledge |
| Parallel-Synthesis (arXiv 2606.14672) | arxiv.org | KV cache synthesis, 2.5x-11x faster |
| 6 Orchestration Patterns (Beam.ai) | beam.ai | Fan-out/fan-in, context overflow at 4+ workers |
| Hardware-Aware Deployment (ScienceDirect) | sciencedirect.com | Heterogeneity-aware training, 70% memory reduction |
| Model Routing (Zylos) | zylos.ai | QoS tiering, confidence-based routing |
| Token-Level Routing (arXiv 2504.07878) | arxiv.org | 7% tokens routed = 60% accuracy improvement |
| Multi-Tier LLM Routing | emergentmind.com | Unified orchestration over models, memory, tools |
| On-Device Inference (tianpan.co) | tianpan.co | Hybrid routing from day one, model-as-infrastructure |
| Edge AI Architecture (AppScale) | appscale.blog | Hybrid cloud-edge, quantization pipeline |

## Research Sources (Tier 2 — Deep Research)

### Knowledge Distillation for Multi-Agent Systems (GAP 1 — Oversoul)

| Source | URL | Key Finding |
|--------|-----|-------------|
| **Agent Distillation** (Kang et al., NeurIPS 2025 Spotlight) | arxiv.org/abs/2505.17612 | Distilling *full agent behavior* (not just reasoning) into 0.5B-3B models using retrieval + code tools. sLMs 0.5B/1.5B/3B match next-tier-larger models on 8 reasoning tasks. First-thought prefix + self-consistent action generation. **Directly applicable**: train a 0.5B pillar from 8B oversoul trajectories. |
| **AgentArk** (arXiv 2602.03955, Feb 2026) | arxiv.org/html/2602.03955v1 | Distilling *multi-agent debate* into single agent via PRM-guided methods. Structured distillation enables small models to approximate complex reasoning behaviors from multi-agent systems. **Applicable**: distill MaKaLi council outputs into a single efficient agent. |
| **MRGKD** (SIGIR 2025) | dl.acm.org/doi/10.1145/3726302.3730232 | Multi-agent Reasoning Graph Knowledge Distillation — graph over multiple LLM perspectives + contrastive loss to distinguish correct/incorrect reasoning. Fine-tunes smaller models. |
| **KDRL** (arXiv 2506.02208, Jun 2025) | arxiv.org/abs/2506.02208 | Unified KD + RL (GRPO) for reasoning. RKL divergence minimization + rule-based rewards. Outperforms GRPO and KD baselines on reasoning benchmarks. **Applicable**: joint training strategy after distillation. |
| **Hybrid Policy Distillation** (Zhu et al., Apr 2026) | emergentmind.com | Per-token mixture of forward/reverse KL divergences. Adaptive reweighting. Robust, stable, high data efficiency across reasoning, code, dialogue. Outperforms SFT, standard KD, multi-stage pipelines. |
| **CoMAS** (arXiv 2510.08529, Oct 2025) | emergentmind.com | Co-evolving multi-agent systems — agents learn from inter-agent interactions via intrinsic rewards. LLM-as-judge generates rewards. Ablation confirms interaction-based signals critical. Scales with agent count and diversity. **Applicable**: long-term after T0 proves pattern. |

### Consensus Protocols (GAP 6)

| Source | URL | Key Finding |
|--------|-----|-------------|
| **Voting or Consensus? ACL 2025 Findings** | aclanthology.org/2025.findings-acl.606 | **Settled science**: Voting +13.2% reasoning (95% CI), Consensus +2.8% knowledge. All-Agents Drafting +3.3%, Collective Improvement +7.4%. More discussion rounds *before* voting reduces performance. **Directly applicable**: route tasks by type — reasoning→voting, knowledge→consensus. |
| **Roundtable Policy** (Yao et al., Feb 2026) | arxiv.org/abs/2509.16839 | Confidence-weighted consensus aggregation. Only requires black-box API access + uniform procedures. Weighted by confidence scores from each agent. **Applicable**: oversoul weighs pillar reports by confidence. |
| **DWC-MAD** (Springer, Nov 2025) | link.springer.com | Dynamic Weighted Consensus Framework for Multi-Agent Debate. Agents that consistently provide accurate answers get higher weight. **Applicable**: history-based weight adaptation. |
| **Consensus Protocols Guide** (tianpan.co, Apr 2026) | tianpan.co | 5 coordination patterns that work: Debate-then-vote hybrid, confidence weighting (more effective with calibration), CRDTs for shared context, task decomposition beats arbitration, surface disagreement rather than synthesize when evidence is weak. **Directly applicable**: design patterns for Kali oversoul. |

### 4B Model Benchmarks (GAP 2)

| Source | URL | Key Finding |
|--------|-----|-------------|
| **Qwen3.5-4B Specs** (Feb 2026) | apxml.com/models/qwen35-4b | 262K native context, 32 layers, GQA 16 heads/4 KV, SwiGLU. ~10GB FP16, ~5GB INT8, ~3GB INT4. MMLU-Pro 79.1%, GPQA Diamond 76.2%. Multilingual (201 languages), multimodal. |
| **Gemma 4 E4B Specs** (Mar 2026) | apxml.com/models/gemma-3-4b | 131K context at FP16, decoder-only with 5:1 sliding window interleave. ~8GB FP16, ~5GB INT8, ~3GB INT4. |
| **Gemma 4 12B Unified** (NEW Jun 2026) | aurigait.com | 12B parameters, unified multimodal (text/image/audio), 256K context. ~8GB at Q4. Runs on 12-16GB GPUs / Apple Silicon. **Perfect for oversoul tier** — substantially more capable than 4B, still fits 16GB. |
| **Real-world Gemma 4 vs Qwen 3.5** (Jul 2026) | msf.github.io | **Gemma 4 26B-A4B**: 15 GB, 14/15 compile rate, 18 tok/s on iGPU. **Qwen3.5-35B**: 21-22 tok/s but lower compile rate. Gemma 4 more consistent under constrained context. **Key insight**: compile rate matters more than peak score — consistency over ceiling. |
| **Model Wars 2026** (May 2026) | dasroot.net | Qwen 3.5-35B-A3B: 3B active, 262K context, single H100. Gemma 4-26B-A4B: 4B active, 256K context. Qwen 3.5 better for long contexts/Chinese, Gemma 4 for lightweight high-performance. |
| **Gemma 4 Hardware Guide** (Apr 2026) | gemma4-ai.com | KV cache gotcha: 31B at 262K context = ~22GB KV cache *on top of* model weights. For 4B at 32K context = ~400MB KV cache. **Applicable**: verify pillar prompts stay within affordable context windows. |

### Failure Handling (GAP 5)

| Source | URL | Key Finding |
|--------|-----|-------------|
| **Graceful Degradation for LLMs** (tianpan.co, 2026) | tianpan.co | Circuit breakers for LLM calls (rate limit, timeout, budget). Fallback chain to smaller model. Retry with exponential backoff (jittered). Checkpointing + resume for long-running agents. Partial results over no results. **Directly applicable**: all patterns map directly. |
| **Write-Ahead Logging for AI Agents** (tianpan.co, 2026) | tianpan.co | Borrow database WAL patterns: log-before-execute, replay after crash, idempotency by design. **Applicable**: coordinator crash recovery. |
| **Exponential Backoff + Jitter** (AWS, 2024) | aws.amazon.com | Full jitter: sleep = random(0, min(cap, base * 2^attempt)). Best practice for retry. |
| **Timed Out Agents** (tianpan.co, Apr 2026) | tianpan.co | Agents that fail to respond within a deadline degrade experience. Resolution: timeout + partial result + escalate. Users learn to game deadlines for refunds. **Applicable**: pillar timeout handling. |

### Cross-Council Memory (GAP 7)

| Source | URL | Key Finding |
|--------|-----|-------------|
| **ShardMemo** (Zhao et al., 2026) | emergentmind.com | Learned tier gate over working memory, sharded evidence memory, versioned skill library. Three-tier memory with automatic tier promotion. |
| **DynamicRAG + On-Device Inference** (tianpan.co, 2026) | tianpan.co | Routing across embedding, retrieval, prompting, tools, AND memory. Model-as-infrastructure: versioned, monitored, deprecation timelines. **Applicable**: memory persistence should be versioned, not ad-hoc. |

---

## Priority Ranking (Updated with Research Findings)

| Gap | Impact | Effort | Priority | Status After Research |
|-----|--------|--------|----------|----------------------|
| GAP 1: Oversoul Distillation | HIGH | MEDIUM | P0 | **Actionable now**: AgentDistillation + AgentArk show small models (0.5B-3B) can match next-tier-larger models. AgentArk specifically distills multi-agent debate → single agent (our exact use case). Start with simple output → structured distillation (no training infra needed for T0). |
| GAP 2: Tier 1 Context Windows | HIGH | LOW | P0 | **Partially resolved**: Qwen3.5-4B (262K ctx, ~3GB Q4) and Gemma 4 E4B (128K ctx, ~3GB Q4) both fit on 16GB with room. Gemma 4 12B Unified (~8GB Q4, 256K ctx) perfect for oversoul. Need to run actual pillar prompts to measure real context usage. |
| GAP 5: Failure Handling | HIGH | MEDIUM | P0 | **Actionable now**: Research provides clear patterns — circuit breakers, fallback chain, retry with full jitter, WAL logging, partial results, checkpointing. Can implement directly. WAL pattern from databases maps 1:1 to coordinator crash recovery. |
| GAP 3: Hardware Constraints | MEDIUM | HIGH | P1 | **Partially resolved**: Gemma 4 26B-A4B confirmed working at 15GB/18 tok/s on iGPU. Our 16GB RAM is borderline for this tier. Qwen3.5-4B confirmed at ~3-5GB. Pillar→4B, Oversoul→12B, Kali→cloud (no local 12B on 16GB without swap). |
| GAP 4: Research Decoupling | MEDIUM | MEDIUM | P1 | **Actionable now**: No new research needed — implement as Kali's "remaining gaps" section executed by smaller model. Existing websearch/webfetch tools sufficient for T0. |
| GAP 6: Consensus Protocol | MEDIUM | LOW | P2 | **Settled by research**: Voting for reasoning (+13.2%), Consensus for knowledge (+2.8%). ACL 2025 findings are statistically significant. Confidence-weighted consensus (Roundtable Policy) is recommended approach. More rounds BEFORE voting reduces performance — agree on decision protocol before discussion. |
| GAP 7: Cross-Council Memory | LOW | HIGH | P3 | **Confirmed low priority**: Start session-isolated. ShardMemo three-tier pattern exists when needed. No benefit to premature memory infrastructure. |

---

## Recommended T0 Approach (Updated)

Given completed research, T0 approach is refined:

1. **GAP 2 → BENCHMARK (1 session)**: Run Qwen3.5-4B or Gemma E4B with representative pillar prompts. Measure:
   - Per-prompt token count (input + output)
   - Per-prompt KV cache usage
   - Max context window needed for 4-5 pillar reports
   - Time-to-completion per pillar prompt
   *Decision point*: If 4B fits comfortably, move forward. If not, fall back to 2B tier (Qwen3.5-2B).

2. **GAP 5 → BUILD FAILURE LAYER (1 session)**: Implement coordinator failure handling:
   - Circuit breaker per pillar (3 consecutive failures = skip)
   - Fallback chain: preferred model → smaller model → cached result → empty report
   - Retry with full jitter: `random(0, min(cap, base * 2^attempt))`
   - WAL-inspired: log pillar dispatch before execute, resume on crash
   - Partial results over no results

3. **GAP 1 → TEST OVERSOUL (1 session)**: Run oversoul pattern with 4-5 reports:
   - Measure oversoul context window (combined input from 4-5 reports)
   - Test Gemma 4 12B Unified (@8GB Q4) as oversoul model
   - Verify oversoul synthesis quality
   - Measure total tokens for complete council cycle

4. **Build coordinator (1 session)**: Using validated benchmarks:
   - Coordinator prompt with routing logic: reasoning→voting, knowledge→consensus
   - Confidence-weighted aggregation (Roundtable Policy pattern)
   - Partial results handling
   - Research gap section → smaller model

5. **Test on hardware (1 session)**: Full end-to-end on Ryzen 5700U 16GB:
   - Run 4 pillars + oversoul + Kali synthesis
   - Monitor thermal (stay under 85°C sustained)
   - Monitor RAM (stay under 12GB, keep 4GB for system)
   - Measure total latency

**Total T0 estimate**: 5 sessions (was 6+ — saved by research confirming patterns exist and don't need reinvention)

## Research Sources (Tier 2 — Deep Research)

### Knowledge Distillation for Multi-Agent Systems (GAP 1 — Oversoul)

| Source | URL | Key Finding |
|--------|-----|-------------|
| **Agent Distillation** (Kang et al., NeurIPS 2025 Spotlight) | arxiv.org/abs/2505.17612 | Distilling *full agent behavior* (not just reasoning) into 0.5B-3B models using retrieval + code tools. sLMs 0.5B/1.5B/3B match next-tier-larger models on 8 reasoning tasks. First-thought prefix + self-consistent action generation. **Directly applicable**: train a 0.5B pillar from 8B oversoul trajectories. |
| **AgentArk** (arXiv 2602.03955, Feb 2026) | arxiv.org/html/2602.03955v1 | Distilling *multi-agent debate* into single agent via PRM-guided methods. Structured distillation enables small models to approximate complex reasoning behaviors from multi-agent systems. **Applicable**: distill MaKaLi council outputs into a single efficient agent. |
| **MRGKD** (SIGIR 2025) | dl.acm.org/doi/10.1145/3726302.3730232 | Multi-agent Reasoning Graph Knowledge Distillation — graph over multiple LLM perspectives + contrastive loss to distinguish correct/incorrect reasoning. Fine-tunes smaller models. |
| **KDRL** (arXiv 2506.02208, Jun 2025) | arxiv.org/abs/2506.02208 | Unified KD + RL (GRPO) for reasoning. RKL divergence minimization + rule-based rewards. Outperforms GRPO and KD baselines on reasoning benchmarks. **Applicable**: joint training strategy after distillation. |
| **Hybrid Policy Distillation** (Zhu et al., Apr 2026) | emergentmind.com | Per-token mixture of forward/reverse KL divergences. Adaptive reweighting. Robust, stable, high data efficiency across reasoning, code, dialogue. Outperforms SFT, standard KD, multi-stage pipelines. |
| **CoMAS** (arXiv 2510.08529, Oct 2025) | emergentmind.com | Co-evolving multi-agent systems — agents learn from inter-agent interactions via intrinsic rewards. LLM-as-judge generates rewards. Ablation confirms interaction-based signals critical. Scales with agent count and diversity. **Applicable**: long-term after T0 proves pattern. |

### Consensus Protocols (GAP 6)

| Source | URL | Key Finding |
|--------|-----|-------------|
| **Voting or Consensus? ACL 2025 Findings** | aclanthology.org/2025.findings-acl.606 | **Settled science**: Voting +13.2% reasoning (95% CI), Consensus +2.8% knowledge. All-Agents Drafting +3.3%, Collective Improvement +7.4%. More discussion rounds *before* voting reduces performance. **Directly applicable**: route tasks by type — reasoning→voting, knowledge→consensus. |
| **Roundtable Policy** (Yao et al., Feb 2026) | arxiv.org/abs/2509.16839 | Confidence-weighted consensus aggregation. Only requires black-box API access + uniform procedures. Weighted by confidence scores from each agent. **Applicable**: oversoul weighs pillar reports by confidence. |
| **DWC-MAD** (Springer, Nov 2025) | link.springer.com | Dynamic Weighted Consensus Framework for Multi-Agent Debate. Agents that consistently provide accurate answers get higher weight. **Applicable**: history-based weight adaptation. |
| **Consensus Protocols Guide** (tianpan.co, Apr 2026) | tianpan.co | 5 coordination patterns that work: Debate-then-vote hybrid, confidence weighting (more effective with calibration), CRDTs for shared context, task decomposition beats arbitration, surface disagreement rather than synthesize when evidence is weak. **Directly applicable**: design patterns for Kali oversoul. |

### 4B Model Benchmarks (GAP 2)

| Source | URL | Key Finding |
|--------|-----|-------------|
| **Qwen3.5-4B Specs** (Feb 2026) | apxml.com/models/qwen35-4b | 262K native context, 32 layers, GQA 16 heads/4 KV, SwiGLU. ~10GB FP16, ~5GB INT8, ~3GB INT4. MMLU-Pro 79.1%, GPQA Diamond 76.2%. Multilingual (201 languages), multimodal. |
| **Gemma 4 E4B Specs** (Mar 2026) | apxml.com/models/gemma-3-4b | 131K context at FP16, decoder-only with 5:1 sliding window interleave. ~8GB FP16, ~5GB INT8, ~3GB INT4. |
| **Gemma 4 12B Unified** (NEW Jun 2026) | aurigait.com | 12B parameters, unified multimodal (text/image/audio), 256K context. ~8GB at Q4. Runs on 12-16GB GPUs / Apple Silicon. **Perfect for oversoul tier** — substantially more capable than 4B, still fits 16GB. |
| **Real-world Gemma 4 vs Qwen 3.5** (Jul 2026) | msf.github.io | **Gemma 4 26B-A4B**: 15 GB, 14/15 compile rate, 18 tok/s on iGPU. **Qwen3.5-35B**: 21-22 tok/s but lower compile rate. Gemma 4 more consistent under constrained context. **Key insight**: compile rate matters more than peak score — consistency over ceiling. |
| **Model Wars 2026** (May 2026) | dasroot.net | Qwen 3.5-35B-A3B: 3B active, 262K context, single H100. Gemma 4-26B-A4B: 4B active, 256K context. Qwen 3.5 better for long contexts/Chinese, Gemma 4 for lightweight high-performance. |
| **Gemma 4 Hardware Guide** (Apr 2026) | gemma4-ai.com | KV cache gotcha: 31B at 262K context = ~22GB KV cache *on top of* model weights. For 4B at 32K context = ~400MB KV cache. **Applicable**: verify pillar prompts stay within affordable context windows. |

### Failure Handling (GAP 5)

| Source | URL | Key Finding |
|--------|-----|-------------|
| **Graceful Degradation for LLMs** (tianpan.co, 2026) | tianpan.co | Circuit breakers for LLM calls (rate limit, timeout, budget). Fallback chain to smaller model. Retry with exponential backoff (jittered). Checkpointing + resume for long-running agents. Partial results over no results. **Directly applicable**: all patterns map directly. |
| **Write-Ahead Logging for AI Agents** (tianpan.co, 2026) | tianpan.co | Borrow database WAL patterns: log-before-execute, replay after crash, idempotency by design. **Applicable**: coordinator crash recovery. |
| **Exponential Backoff + Jitter** (AWS, 2024) | aws.amazon.com | Full jitter: sleep = random(0, min(cap, base * 2^attempt)). Best practice for retry. |
| **Timed Out Agents** (tianpan.co, Apr 2026) | tianpan.co | Agents that fail to respond within a deadline degrade experience. Resolution: timeout + partial result + escalate. Users learn to game deadlines for refunds. **Applicable**: pillar timeout handling. |

### Cross-Council Memory (GAP 7)

| Source | URL | Key Finding |
|--------|-----|-------------|
| **ShardMemo** (Zhao et al., 2026) | emergentmind.com | Learned tier gate over working memory, sharded evidence memory, versioned skill library. Three-tier memory with automatic tier promotion. |
| **DynamicRAG + On-Device Inference** (tianpan.co, 2026) | tianpan.co | Routing across embedding, retrieval, prompting, tools, AND memory. Model-as-infrastructure: versioned, monitored, deprecation timelines. **Applicable**: memory persistence should be versioned, not ad-hoc. |

---

*⬡ OMEGA ⬡ KALI ⬡ MAKALI-KNOWLEDGE-GAPS ⬡ 2026-07-19*