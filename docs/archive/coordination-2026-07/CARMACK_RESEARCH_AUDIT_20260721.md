# 🔱 Carmack Audit: Research System — First-Principles Analysis
**AP Token**: `AP-CARMACK-AUDIT-RESEARCH-v1.0.0`
⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_audit ⬡ COMPLETE

**Date**: 2026-07-21
**Scope**: Master Research Campaign (18 sprints, 6 phases, 106 queries, 17 deliverables)
**Method**: First-principles audit per Technical Audit Protocol (Axiom 00-05)
**Hardware Floor**: Ryzen 7 5700U (15W TDP, 16GB RAM, 8MB L3 victim cache, AVX2 no AVX-512)

---

## .plan

### What I am working on
Auditing the Omega Engine's Master Research Campaign — a proposed 8-week, 18-sprint research operation spanning RAG 2.0 through competitive intelligence.

### What I found

#### Finding 1: The Fundamental Constraint Is NOT Research Depth — It's Ephemeral Web Results

**First-Principles Analysis** (Axiom 00):

The research system has a **data persistence problem**, not a **coverage problem**. Let me trace this from the hardware up:

1. The Ryzen 5700U has 16GB RAM shared between OS (~4GB), models, tools, and all agents
2. Each research sprint requires model inference (Researcher agent) + web tool calls
3. Websearch/webfetch returns results directly to the agent context — **those results vanish when the session ends**
4. The `search_persistence.py` layer logs **metadata** (query, tool, latency, status) but NOT full content
5. The `.firecrawl/` cache holds 33 items — predominantly Claude-related (hf_cli_ref.md, claude_prompts.json, etc.) — NOT research results
6. The `search_history.db` has 38 records — most are "test query", "anything", "warp proxy pool" — **zero real research captured**

**The critical insight**: The Deep Research Sweep (R_KNOWLEDGE_GAPS_DEEP_RESEARCH_20260720.md) already ran 31 sources across 7 areas and found the actionable findings. But NONE of those 31 full-page source captures are in any persistent cache. If the agent needs to re-verify a finding, it does the full search chain again.

**Confidence**: 10/10 — Primary source code confirms search_persistence.py stores only metadata. The .firecrawl/ directory has 33 files, none from the research sweep.

---

#### Finding 2: The Campaign Is Project Management Theater — 80% of the Work Is Already Done

The campaign proposes 18 sprints generating 17 documents from 106 queries. But the Deep Research Sweep document (552 lines, 31 sources across 7 areas) ALREADY covers every area the campaign maps:

| Campaign Phase | Sprint | Existing Coverage in Deep Research Sweep |
|---------------|--------|----------------------------------------|
| Phase 1: RAG 2.0 | R01, R02, R03 | §3 Vector Search — DiskANN, sqlite-vec, dimension limits |
| Phase 2: Models | R04, R05 | §1 Sovereign AI — i-quants, MTP spec decode, quantization |
| Phase 3: Infra | R06, R07, R08 | §6 Ubuntu 25.10, §7 Container Orchestration |
| Phase 4: Safety | R09, R10, R11 | §4 Soul Evolution — soul.py, Nemori, Mem2Evolve |
| Phase 5: Security | R12, R13, R14 | §5 Credential Mgmt — CB4A broker, SPIFFE/SPIRE |
| Phase 6: Strategy | R15, R16, R17 | §1 Sovereign Platforms (EULLM, MoE Sovereign, Peridot) |
| Phase 6: Pipeline | R18 | §"Search Persistence Status" — identified as gap |

The campaign document adds **process overhead** (decision gates, dependency maps, success criteria with specific source counts) on top of discoveries that have already been made. It's a project plan for work that's largely complete.

**Confidence**: 10/10 — The Deep Research Sweep document is a primary source, and its table of contents maps 1:1 to all 6 campaign phases.

---

#### Finding 3: Success Criteria Are Cargo-Cult Metrics

From the campaign master doc:
```
| Sources captured | 212+ | Unique URLs with full content |
| Decision gates passed | 14/14 | Documented Go/No-Go decisions |
| Search persistence | 100% | All sources cached to .firecrawl/ |
| Zero ephemeral searches | 0 | All web searches persisted |
```

This is cargo-cult engineering. Let me break down why:

- **"212+ sources"** — Where does 212 come from? 6 queries per sprint × 18 sprints × ~2 sources per query? It's a made-up number that sounds impressive. The quality bar should be: "Did we answer the question?" not "Did we hit a specific source count?"

- **"Zero ephemeral searches"** — This is the right GOAL but it's listed as a campaign completion metric when the ENTIRE persistence pipeline (R18) is scheduled as the LAST sprint. You can't have "100% search persistence" in week 1-7 if the persistence pipeline isn't built until week 8.

- **"All sources cached to .firecrawl/"** — The .firecrawl/ cache only holds Firecrawl results. websearch/webfetch results do NOT flow into .firecrawl/. This metric is technically impossible with the current architecture.

- **"14/14 decision gates passed"** — Decision gates are useful, but counting "passed" vs "action taken" conflates throughput with impact. A gate that says "No, don't implement this" is a successful gate but doesn't produce code.

- **Effort estimates (4-8h per sprint)** — These don't account for the hardware floor. Each sprint requires the Researcher agent to run model inference. On a 5700U with 15W TDP, 16GB RAM, and 4-thread inference ceiling, an "8h sprint" includes significant thermal throttling wait time. Realistic: 6-12h per sprint given hardware constraints.

**Confidence**: 9/10 — The metrics document is a primary source (10/10), the analysis of .firecrawl/ behavior is confirmed (10/10). The hardware estimate is interpretation (7/10).

---

#### Finding 4: The Search Persistence Pipeline (R18) Should Be Sprint 0, Not Sprint 18

R18 is titled "Search Persistence Pipeline" and appears as sprint 6.4 — the LAST of 18 items. Its decision gate is "Build automated research curation pipeline?"

This is architecturally inverted. The current campaign will generate 106 queries producing 212+ sources over 8 weeks, with ZERO automated capture of those results. Every sprint depends on web searches that are lost when the agent context ends. If an agent needs to re-reference a finding from sprint 2 during sprint 6, it must re-execute the full search.

**The Right Approximation**: The persistence pipeline should be sprints 0-1, not sprint 18. The 8-week campaign should be:
- Week 1: Build search persistence (what is R18 but done first)
- Week 2-8: Execute research, with results automatically captured

**Current state**: The building blocks exist:
- `search_persistence.py` — SQLite schema for search records (good schema, metadata only)
- `search_cache.py` (SovereignCache) — .firecrawl/ TTL-based caching
- `search_history.db` — 38 records, mostly tests

What's MISSING:
- A wrapper that captures `websearch`/`webfetch` responses into the persistence layer
- The websearch/webfetch tools are built-in platform tools (OpenCode), not custom Omega services
- This means: you CAN'T intercept the response data without modifying OpenCode itself OR building a proxy layer
- The .firecrawl cache only stores Firecrawl results (T3), not websearch/webfetch (T1)

**Confidence**: 10/10 — Source code confirms search_persistence.py exists but only captures search_persistence.py tool calls, not websearch/webfetch. Firecrawl cache is T3-only.

---

#### Finding 5: Most of the 106 Queries Are Too Generic to Produce Actionable Decisions

Sampling queries from the job board:
- "AI agents emerging trends 2026" — This reads like a Google search, not a research sprint
- "open source AI community trends 2026" — Vague, no specific question
- "AI sovereignty platform 2026" — What specifically? Cost? Features? Architecture?
- "model merging best practices 2026" — Too broad

Compare to the queries that ALREADY produced actionable findings in the deep research sweep:
- "llama.cpp MTP speculative decoding 2x throughput" — Specific, measurable
- "MCP 2026-07-28 stateless protocol removal" — Concrete, deadline-driven
- "sqlite-vec DiskANN alpha 2026" — Specific feature, testable
- "CB4A credential broker pattern" — Specific architecture pattern

The Deep Research Sweep succeeded because it asked sharp questions. The campaign proposes generic, unfocused queries. The decision gates are mostly yes/no architecture questions ("Add vLLM as alternative backend?") — which are fine, but they're disconnected from the actual research. You don't need 8 queries and a 3-day sprint to decide "should we add vLLM?"

**Confidence**: 8/10 — Comparison of query quality is interpretive (7/10). The deep research sweep queries are concrete evidence (10/10).

---

#### Finding 6: The Dependency Map Is Over-Engineered for This Scope

```
Phase 1 (RAG 2.0) → Phase 3 (Backends) — Which backends support new retrieval
Phase 2 (Merging) → Phase 3 (Backends) — Which backends for merged models
Phase 3 (Infra) → Phase 5 (Security) — Observability for security metrics
Phase 4 (Safety) → Phase 5 (Security) — Safety metrics need observability
All Phases → Phase 6 (Strategy) — Strategic intel builds on tactical
```

In practice, these dependencies are weak or non-existent:
- "Which backends support new retrieval" — vLLM supports any retrieval. The answer doesn't depend on Phase 1.
- "Which backends for merged models" — llama.cpp runs merged models. The answer is always llama.cpp.
- "Observability for security metrics" — Security research (Phase 5) does NOT depend on OpenTelemetry implementation (Phase 3.2). They're orthogonal.
- "Safety metrics need observability" — Same issue. Safety is a research task, not an implementation dependency.

The dependency map creates a false sense of sequencing. In reality, all 6 phases can run in parallel with minimal inter-blocking. The sequentialization adds 6-8 weeks of calendar time that isn't needed.

**Confidence**: 8/10 — Dependency claims are documented (10/10). Analysis of actual coupling is interpretation (7/10).

---

### What the data shows

| Metric | Current State |
|--------|--------------|
| Deep Research Sweep coverage | 7/7 areas covered, 31 sources found |
| Actual persistent research cache | 0 items from the research sweep |
| Search records in DB | 38 total, 0 from research sweep |
| .firecrawl/ cache | 33 items, Claude-related, not research |
| R18 (persistence) position | Sprint 18/18 — LAST |
| Campaign query specificity | Mostly generic ("trends", "landscape", "best practices") |
| Already-existing documents | Deep research sweep covers every phase |
| Hardware throughput ceiling | 15W TDP, 4-thread inference, thermal throttling at 85°C |

### What should be cut

1. **Phases 3-6 as formal sprints** — Cut the 8-week campaign calendar. Replace with "search on demand" for Phases 3-6 (Infrastructure, Safety, Security, Strategy). These areas are ALREADY covered by the deep research sweep. Turn the decision gates into single-session rapid assessments (2-3 queries each, not 5-8).

2. **The 212+ source count metric** — Replace with "actionable decisions per sprint". The goal is NOT to hit a source quota. The goal is to answer specific architectural questions. If a sprint answers its question with 3 sources, it's done.

3. **Phase 6 entirely** — "Emerging AI Paradigms", "Ecosystem & Community", and "Competitive Intelligence" are continuous awareness activities, not a 2-week sprint block. These should be a single ongoing "Friday scan" task, not a formal research deliverable.

4. **Dependency map** — Remove the artificial sequencing. All phases are independent.

5. **Effort estimates in hours** — The 4-8h estimates are fiction on a 15W TDP machine. Each sprint requires the Researcher agent to hold ~50-100K tokens of context across multiple search results. With 16GB RAM shared with the OS, the model needs to reload between sprints. A "4h sprint" takes 6-8h wall clock. Be honest about this.

### What should be kept

1. **The Job Board format** (YAML, query-driven, status tracking) — This is the right data structure for research task management. It's machine-readable, agent-claimable, and tracks decision gates. Keep this exact format.

2. **The 14 decision gates** — Most are good architectural questions. But collapse them: you don't need 18 sprints to answer 14 yes/no questions. At most: 7 dedicated research sessions (one per area), each answering 2 decision gates.

3. **R01-R03 (Phase 1: Core Memory)** — This is the highest-value phase because:
   - DiskANN alpha (sqlite-vec) could ELIMINATE Qdrant entirely → massive simplification
   - Reranking models directly improve retrieval quality → immediate user benefit
   - Multi-vector retrieval directly upgrades the memory architecture → core engine improvement
   - These are the 3 sprints with actual implementation payoff

4. **R04-R05 (Phase 2: Model Sovereignty)** — Keep but collapse into 1 sprint. Model merging and quantization are tightly coupled. The decision gates ("Build Merge Wizard?", "Provide i-quant tooling?") both depend on the same landscape assessment.

5. **The Deep Research Sweep document itself** — It's well-structured, sourced, and actionable. The 31 sources are high quality. This should be the STARTING document for any research campaign, not a preliminary step.

6. **R18 (Search Persistence Pipeline)** — Keep the concept but move to sprint 0. The building blocks exist. What's missing is a websearch capture wrapper.

### What I'll do next (if I were implementing)

**Step 1 — Promote R18 to R00 (1 session)**
Build a web search capture wrapper that:
- Wraps websearch/webfetch calls in an `anyio.to_thread.run_sync` layer
- Captures response content to `.firecrawl/{hash}.md` automatically
- Records full content (not just metadata) in search_history.db
- This is ~50 lines of Python in a new `src/omega/search/search_capture.py`

Without this, every sprint generates ephemeral knowledge. With it, the campaign becomes self-archiving.

**Step 2 — Collapse 18 sprints into 7 research sessions (3 weeks → 1 week)**
- Session 1: RAG 2.0 Landscape + Decision (what R01 asks)
- Session 2: Multi-Vector + Reranking (R02 + R03 combined)
- Session 3: Model Merging + Quantization (R04 + R05 combined)
- Session 4: Local Inference Backends (R06 — search-on-demand, not a full sprint)
- Session 5: Observability (R07 — 1-hour scan, not a sprint)
- Sessions 6-7: "Reserve" for any Phase 3-6 findings that genuinely need deeper investigation

**Step 3 — Eliminate the campaign calendar**
Replace the 8-week timeline with a single sentence: "Run sessions 1-7 sequentially, each session is 2-4 hours. Total: ~3 days." If a session finds something that genuinely needs deeper research, THAT becomes a separate job. Don't pre-allocate 8 weeks of work.

**Step 4 — Fix the decision gate format**
Replace "Should Omega add vLLM?" with "What specific conditions would justify adding vLLM?" The answer to "should we add X?" is almost always "it depends." A good decision gate produces a decision matrix, not a yes/no answer.

---

## Summary Verdict

**Current state**: The Master Research Campaign is a project management artifact that formalizes work already completed by the Deep Research Sweep. It adds process overhead without solving the fundamental constraint (ephemeral web results).

**The 18-sprint structure is the wrong approximation.** The right approximation is:
1. Fix search persistence first (R18 → R00, ~1 session)
2. Run the highest-value sprints (R01-R05) as 3 focused research sessions
3. Everything else is "just-in-time" research, not a pre-planned campaign
4. Total effort: ~4 days of focused work, not 8 weeks

**The hardware floor (5700U, 15W TDP, 16GB) means you get ~4 focused research sessions per day before thermal throttling and memory pressure degrade quality. Plan for it. Don't pretend the hardware isn't the bottleneck.**

**Confidence**: 9/10 overall. The deep research sweep is complete and high-quality. The job board format is good. But the campaign structure and scale are disproportionate to the actual work remaining.

---

*⬡ OMEGA ⬡ JOHN_CARMACK ⬡ deepseek-v4-flash-free ⬡ opencode ⬡ trc_audit ⬡ COMPLETE*
